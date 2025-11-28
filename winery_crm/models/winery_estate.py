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

    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(string="ZIP")
    city = fields.Char()
    country_id = fields.Many2one("res.country", string="Country")
    latitude = fields.Float(string="Latitude")
    longitude = fields.Float(string="Longitude")
    visiting_hours = fields.Char(
        string="Visiting Hours",
        help="Short description of visiting hours, e.g. Mon–Fri 10:00–18:00.",
    )

    variety_ids = fields.Many2many("winery.variety", string="Grape varieties")
    vineyard_area_ha = fields.Float(string="Vineyard Area (ha)")
    orchard_area_ha = fields.Float(string="Orchard Area (ha)")

    tasting_capacity_indoor = fields.Integer(string="Indoor Capacity")
    tasting_capacity_outdoor = fields.Integer(string="Outdoor Capacity")
    tasting_capacity_total = fields.Integer(
        string="Total Capacity",
        compute="_compute_tasting_capacity_total",
        store=True,
    )

    tasting_ids = fields.One2many(
        "winery.tasting", "estate_id", string="Tastings/Visits"
    )
    upcoming_attendees = fields.Integer(
        string="Upcoming Attendees",
        compute="_compute_upcoming_attendees",
        help="Total number of attendees on future tastings.",
    )
    capacity_utilization = fields.Float(
        string="Capacity Utilization",
        compute="_compute_capacity_utilization",
        help="Upcoming attendees divided by total capacity (0–100%).",
    )

    def _compute_tasting_capacity_total(self):
        for estate in self:
            estate.tasting_capacity_total = (
                (estate.tasting_capacity_indoor or 0)
                + (estate.tasting_capacity_outdoor or 0)
            )

    def _compute_upcoming_attendees(self):
        for estate in self:
            upcoming = estate.tasting_ids.filtered(
                lambda t: t.date_start and t.date_start >= fields.Datetime.now() # type: ignore
            )
            estate.upcoming_attendees = sum(len(t.attendees_ids) for t in upcoming) # type: ignore

    def _compute_capacity_utilization(self):
        for estate in self:
            total_capacity = estate.tasting_capacity_total or 0
            if total_capacity > 0:
                estate.capacity_utilization = (
                    estate.upcoming_attendees / total_capacity
                ) * 100.0
            else:
                estate.capacity_utilization = 0.0
