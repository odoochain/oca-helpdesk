from odoo import fields, models, api, exceptions


class project_location(models.Model):
    _name = 'project_location'

    name = fields.Char(string='Locación')
    code = fields.Char(string='Código')

    # Restricción a nivel de SQL
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'La locación ya existe')
    ]

