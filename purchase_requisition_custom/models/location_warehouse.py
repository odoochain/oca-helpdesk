from odoo import fields, models, api, exceptions


class location_warehouse(models.Model):
    _name = 'location_warehouse'

    name = fields.Char(string='Locación')
    code = fields.Char(string='Código')

    # Restricción a nivel de SQL
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'La locación ya existe')
    ]

