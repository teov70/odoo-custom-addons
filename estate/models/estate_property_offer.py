from odoo import _, models, fields, api
from odoo.exceptions import UserError, ValidationError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"

    price = fields.Float(string="Price", required=True)
    status = fields.Selection([
        ('accepted','Accepted'),
        ('refused','Refused'),
    ], string="Status", copy=False) # type: ignore
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True, ondelete="cascade")
    validity = fields.Integer(default=7, string="Validity (days)")
    date_deadline = fields.Date(compute="_compute_deadline", inverse="_inverse_deadline", string="Deadline", store=True)
    property_type_id = fields.Many2one(related="property_id.property_type_id", string="Property Type", store=True, readonly=True)

    _check_price = models.Constraint(
        'CHECK(price > 0)',
        "Offer price must be greater than zero.",
    )

    @api.depends('validity', 'create_date')
    def _compute_deadline(self):
        for offer in self:
            base = fields.Date.to_date(offer.create_date) if offer.create_date else fields.Date.context_today(offer) # type: ignore[attr-defined]
            offer.date_deadline = fields.Date.add(base, days=int(offer.validity or 0)) # type: ignore[assignment]
    
    def _inverse_deadline(self):
        for offer in self:
            if not offer.date_deadline:
                offer.validity = 0
                continue
            base = fields.Date.to_date(offer.create_date) if offer.create_date else fields.Date.context_today(offer) # type: ignore[attr-defined]
            offer.validity = (offer.date_deadline - base).days # type: ignore[assignment]

    @api.model
    def _get_best_offer_amount(self, property_id):
        property = self.env['estate.property'].browse(property_id)
        return property.best_offer or 0.0 # type: ignore[attr-defined]
    
    @api.constrains('status', 'property_id')
    def _check_single_accepted_offer(self):
        for rec in self:
            if rec.status == 'accepted':
                count = self.search_count([
                    ('property_id', '=', rec.property_id.id),
                    ('status', '=', 'accepted'),
                    ('id', '!=', rec.id),
                ])
                if count:
                    raise ValidationError("This property already has an accepted offer.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            pid = vals.get('property_id')
            price = vals.get('price')

            best_offer = self._get_best_offer_amount(pid)
            if price < best_offer: # type: ignore[assignment]
                raise ValidationError("Can't create an offer with a lower amount than an existing offer")
            
        offers = super().create(vals_list)
        offers.mapped('property_id').write({'state': 'received'}) # type: ignore[attr-defined]
        return offers

    def action_accept_offer(self):
        for offer in self:
            other_accepted = offer.property_id.offer_ids.filtered_domain([ # type: ignore[attr-defined]
                ('status', '=', 'accepted'),
                ('id', '!=', offer.id),
            ])
            if other_accepted:
                raise UserError("This property already has an accepted offer.")
            offer.status = 'accepted'
            offer.property_id.write({
                'selling_price': offer.price,
                'buyer_id': offer.partner_id.id,
                'state': 'accepted'
            })
        return True

    def action_refuse_offer(self):
        self.write({'status': 'refused'})
        return True