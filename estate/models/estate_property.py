from odoo import _, models, fields, api # type: ignore[attr-defined]
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _check_expected_price = models.Constraint(
    'CHECK(expected_price > 0)',
    'Expected price must be greater than zero.',
    )
    _check_selling_price = models.Constraint(
    'CHECK(selling_price >= 0)',
    'Selling price must be zero or more.',
    )
    _order = "id desc"

    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(default=lambda self: fields.Date.add(fields.Date.context_today(self), months=3), copy=False)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string='Living Area (sqm)')
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string='Garden Area (sqm)')
    garden_orientation = fields.Selection([
        ('north','North'),('east','East'),
        ('south','South'),('west','West')]) # type: ignore
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('new','New'),('received','Offer Received'),
        ('accepted','Offer Accepted'),('sold','Sold'),('cancelled','Cancelled')], default='new', required=True, copy=False) # type: ignore
    property_type_id = fields.Many2one("estate.property.type", string="Property Type",)
    salesman_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    tag_ids = fields.Many2many("estate.property.tag", string="Property Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offer")
    total_area = fields.Integer(compute='_compute_total_area', store=True)
    best_offer = fields.Float(compute='_compute_best_offer', store=True)

    @api.constrains("expected_price", "selling_price")
    def _check_selling_vs_expected(self):
        for rec in self:
            if float_is_zero(rec.selling_price, precision_digits=2):
                continue
            min_allowed = rec.expected_price * 0.90
            if float_compare(rec.selling_price, min_allowed, precision_digits=2) < 0:
                raise ValidationError(
                    "Selling price must be at least 90% of the expected price. "
                    "Reduce the expected price if you want to accept this offer."
                )
            
    @api.constrains('state', 'buyer_id')
    def _check_buyer_on_sold(self):
        for rec in self:
            if rec.state == 'sold' and not rec.buyer_id:
                raise ValidationError(_("A sold property must have a buyer."))

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = (rec.living_area or 0) + (rec.garden_area or 0)
    
    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for rec in self:
            prices = rec.offer_ids.mapped('price')
            rec.best_offer = max(prices) if prices else 0.0

    @api.depends('offer_ids.status')
    def _set_state_received(self):
        for rec in self:
            if rec.offer_ids and not any(rec.offer_ids.status == 'accepted'): # type: ignore[attr-defined]
                rec.write({'state': 'received'})

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 100
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def set_state_sold(self):
        for rec in self:
            if rec.state == 'cancelled':
                raise UserError(_("Cancelled properties cannot be sold."))
            if not rec.buyer_id:
                raise UserError(_("Accept an offer first (buyer is not set)."))
        self.write({'state': 'sold'})
        return True
        
    def set_state_cancelled(self):
        if any(rec.state == 'sold' for rec in self):
            raise UserError(_("Sold properties cannot be cancelled."))
        self.write({'state': 'cancelled'})
        return True
    
    @api.ondelete(at_uninstall=False)
    def _prevent_delete(self):
        blocked_states = self.filtered_domain([('state', 'in', ('received', 'accepted', 'sold'))])
        if blocked_states:
            raise UserError(_("You can only delete new and cancelled properties!"))
    
        