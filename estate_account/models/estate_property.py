import logging
from odoo import models, Command # type: ignore
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class EstateProperty(models.Model):
    _inherit = 'estate.property' #type: ignore

    def set_state_sold(self):
        res = super().set_state_sold() #type: ignore
        Move = self.env['account.move']
        Journal = self.env['account.journal']

        for rec in self:
            commission = rec.selling_price * 0.06 # type: ignore
            sale_journal = Journal.search([
                ('type', '=', 'sale'),
                ('company_id', '=', self.env.company.id)
            ], limit=1)

            vals = {
                'partner_id': rec.buyer_id.id, #type: ignore
                'move_type': 'out_invoice',
                'journal_id': sale_journal.id,
                "invoice_line_ids": [
                    Command.create({
                        "name": f"Commission 6% — {rec.name}", # type: ignore
                        "quantity": 1.0,
                        "price_unit": commission,
                    }),
                    Command.create({
                        "name": "Administrative fees",
                        "quantity": 1.0,
                        "price_unit": 100.0,
                    })
                ],
            }
            Move.create(vals)
        return res