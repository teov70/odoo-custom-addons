from odoo import fields, models, api
from odoo.exceptions import ValidationError


class WinerySample(models.Model):
    _name = "winery.sample"
    _description = "Tasting Sample"
    _order = "tasting_id, sequence, id"

    estate_id = fields.Many2one(
        "winery.estate",
        related="tasting_id.estate_id",
        store=True,
        readonly=True,
    )

    product_id = fields.Many2one(
        "product.product",
        string="Wine",
        required=True,
    )

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

    product_variety_ids = fields.Many2many(
        "winery.variety",
        string="Grape varieties",
    )
    year = fields.Char(
        string="Year",
        help="Year or vintage label, e.g. 2017 or NV.",
    )
    score = fields.Float(
        string="Score",
        help="Score given during this tasting (e.g. 1–5).",
    )
    notes = fields.Text(
        string="Tasting Notes",
    )

    @api.constrains("product_id")
    def _check_product_is_winery(self):
        for rec in self:
            if rec.product_id and not rec.product_id.is_winery_product: # type: ignore
                raise ValidationError("Sample product must be a winery product.")

    @api.constrains("product_id", "estate_id")
    def _check_product_matches_estate(self):
        for rec in self:
            if (
                rec.product_id
                and rec.estate_id
                and rec.product_id.winery_estate_id # type: ignore
                and rec.product_id.winery_estate_id != rec.estate_id # type: ignore
            ):
                raise ValidationError("Sample product must belong to the tasting estate.")
            

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for rec in self:
            product = rec.product_id
            if not product:
                continue

            if not rec.year and product.year: # type: ignore
                rec.year = product.year # type: ignore

            if not rec.product_variety_ids and product.winery_variety_ids: # type: ignore
                rec.product_variety_ids = product.winery_variety_ids # type: ignore
