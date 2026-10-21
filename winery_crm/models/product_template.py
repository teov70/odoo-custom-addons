from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template" # type: ignore[assignment]

    is_winery_product = fields.Boolean(
        string="Winery Product",
        default=False,
        help="Mark this as a winery-related product (wine, fruit, jam, etc.).",
    )
    winery_estate_id = fields.Many2one(
        "winery.estate",
        string="Produced by",
        help="Estate that produces this product.",
    )
    product_type = fields.Selection([
            ("wine", "Wine"),
            ("sparkling", "Sparkling"),
            ("fruit", "Fruit"),
            ("jam", "Jam"),
            ("juice", "Juice"),
            ("other", "Other"),
        ], # type: ignore
        string="Winery product",
    )
    winery_variety_ids = fields.Many2many(
        "winery.variety",
        string="Grape Varieties",
        help="Grape varieties used in this product.",
    )

    year = fields.Char(
        string="Year",
        help="Year or vintage label, e.g. 2019 or NV.",
    )

    has_allergen_warning = fields.Boolean(
        string="Allergen warning?"
    )
    allergen_warning_text = fields.Char(
        string="Allergen warning text"
    )

    has_serving_note = fields.Boolean(
        string="Special serving note?"
    )
    serving_note_text = fields.Char(
        string="Serving note text"
    )

    has_organic_cert = fields.Boolean(
        string="Organic certification?"
    )
    organic_cert_text = fields.Char(
        string="Organic certification text"
    )