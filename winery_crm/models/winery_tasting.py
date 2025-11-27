from odoo import api, fields, models
from odoo.exceptions import ValidationError


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
    duration_hours = fields.Float(
        string="Duration (hours)",
        compute="_compute_duration_hours",
        store=True,
        help="Length of the tasting based on start/end times.",
    )

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

    @api.depends("date_start", "date_end")
    def _compute_duration_hours(self):
        for tasting in self:
            if tasting.date_start and tasting.date_end:
                delta = tasting.date_end - tasting.date_start
                tasting.duration_hours = delta.total_seconds() / 3600.0
            else:
                tasting.duration_hours = 0.0

    @api.constrains("date_start", "date_end")
    def _check_dates_order(self):
        for tasting in self:
            if tasting.date_start and tasting.date_end and tasting.date_end <= tasting.date_start:
                raise ValidationError("The end date must be after the start date.")
