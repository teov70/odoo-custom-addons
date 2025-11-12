from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"
    _check_tag_name = models.Constraint(
        'UNIQUE(name)',
        'This property tag already exists.',
    )
    _order = "name"
    name = fields.Char(required=True)
    color = fields.Integer(default=0)