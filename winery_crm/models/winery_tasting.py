from odoo import api, fields, models


class WineryTasting(models.Model):
    _name = "winery.tasting"
    _description = "Winery Tasting / Visit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(required=True, tracking=True)
    estate_id = fields.Many2one(
        "winery.estate",
        string="Estate",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Main Customer",
        tracking=True,
    )

    date_start = fields.Datetime(required=True)
    date_end = fields.Datetime(required=True)

    attendees_ids = fields.Many2many(
        "res.partner",
        string="Attendees",
    )

    notes = fields.Html()

    state = fields.Selection([
            ("draft", "Draft"),
            ("planned", "Planned"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ], default="draft", tracking=True # type: ignore
    )

    sample_ids = fields.One2many(
        "winery.sample",
        "tasting_id",
        string="Sample"
    )

    sample_count = fields.Integer(
        compute='_compute_sample_count',
        string="Samples",
        help="Number of samples tasted.",
    )

    @api.depends("sample_ids")
    def _compute_sample_count(self):
        for tasting in self:
            tasting.sample_count = len(tasting.sample_ids)