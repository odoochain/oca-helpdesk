from odoo import fields, models, api

class Type_stock_picking(models.Model):
    _name = 'purchase_requisition_custom_stock_picking_type'
    _description = 'Type for stock picking'

    name = fields.Char(string='Tipo')
    code = fields.Char(string='Código corto')

    # Restricción a nivel de SQL
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'El tipo ya existe')
    ]
