from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _check_price = models.Constraint(
        'CHECK(price > 0)',
        'Offer\'s price must be greater than zero.',
    )
    _order = "price desc"


    price = fields.Float()
    status = fields.Selection(
        [('accepted','Accepted'),
         ('refused','Refused')], copy=False) # type: ignore
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", required=True, ondelete="cascade")
    validity = fields.Integer(default=7, string="Validity (days)")
    date_deadline = fields.Date(compute="_compute_deadline", inverse="_inverse_deadline", string="Deadline", store=True)
    property_type_id = fields.Many2one(related = "property_id.property_type_id", store=True, readonly=True)


    @api.model
    def _max_price_offer(self, property_id: int) -> float:
        property = self.env['estate.property'].browse(property_id)
        return property.best_offer # type: ignore[attr-defined]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            pid = vals.get('property_id')
            price = vals.get('price')
            if not pid or price is None:
                raise UserError("Both property and price are requiredd.")
            best_offer = self._max_price_offer(pid)
            if price < best_offer:
                raise UserError("Can't create an offer with a lower amount than an existing offer")
            
        offers = super().create(vals_list)
        offers.mapped('property_id').write({'state': 'received'}) # type: ignore[attr-defined]
        return offers

    @api.depends('validity', 'create_date')
    def _compute_deadline(self):
        for record in self:
            base = fields.Date.to_date(record.create_date) if record.create_date else fields.Date.context_today(record) # type: ignore[attr-defined]
            assert base is not None
            record.date_deadline = fields.Date.add(base, days=int(record.validity or 0))

    def _inverse_deadline(self):
        for record in self:
            if not record.date_deadline:
                record.validity = 0
                continue
            base = fields.Date.to_date(record.create_date) if record.create_date else fields.Date.context_today(record) # type: ignore[attr-defined]
            assert base is not None
            record.validity = (record.date_deadline - base).days

    def accept_offer(self):
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

    def refuse_offer(self):
        self.write({'status': 'refused'})
        return True
    
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
                    raise ValidationError("Only one accepted offer is allowed per property.")
