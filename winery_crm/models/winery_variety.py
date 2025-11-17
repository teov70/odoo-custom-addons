from odoo import fields, models


class WineryVariety(models.Model):
    _name = "winery.variety"
    _description = "Grape Variety"
    _order = "name"

    name = fields.Char(required=True)
    tag_color = fields.Integer(default=0)
    color = fields.Selection([
            ("white", "White"),
            ("red", "Red"),
            ("rose", "Rosé"),
            ("sparkling", "Sparkling"),
            ("other", "Other"),
        ], required=True, default="white",  # type: ignore
    )
    notes = fields.Text()
    active = fields.Boolean(default=True)