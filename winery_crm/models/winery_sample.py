from odoo import fields, models


class WinerySample(models.Model):
    _name = "winery.sample"
    _description = "Tasting Sample"
    _order = "tasting_id, sequence, id"

    tasting_id = fields.Many2one(
        "winery.tasting",
        string="Tasting",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(
        default=10,
        help="Order in which the wine was served.",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Wine",
        required=True,
    )
    vintage = fields.Char(
        string="Vintage",
        help="Year or vintage label, e.g. 2017 or NV.",
    )
    score = fields.Float(
        string="Score",
        help="Score given during this tasting (e.g. 1–5).",
    )
    notes = fields.Text(
        string="Tasting Notes",
    )