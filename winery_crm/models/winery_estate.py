from odoo import fields, models


class WineryEstate(models.Model):
    _name = "winery.estate"
    _description = "Winery Estate"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one(
        "res.partner",
        string="Main Contact",
        domain=[("is_company", "=", True)],
        ondelete="restrict",
        tracking=True,
    )
    region = fields.Char()
    description = fields.Html()

    variety_ids = fields.Many2many("winery.variety", string="Grape varieties")
    vineyard_area_ha = fields.Float(string="Vineyard Area (ha)")
    orchard_area_ha = fields.Float(string="Orchard Area (ha)")

    tasting_capacity_indoor = fields.Integer(string="Indoor Capacity")
    tasting_capacity_outdoor = fields.Integer(string="Outdoor Capacity")

    tasting_ids = fields.One2many(
        "winery.tasting", "estate_id", string="Tastings/Visits"
    )
