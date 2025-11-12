from odoo import fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'  # type: ignore[assignment]

    property_ids = fields.One2many(
        "estate.property",
        "salesman_id",
        string = "Real Estate Properties",
        domain = [('state', 'not in', ('sold', 'canceled'))]
    )