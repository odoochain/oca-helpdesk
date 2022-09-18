from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = 'account.analytic.line'

    stock_picking_line_id = fields.Many2one(comodel_name='stock.move', string='Movimietos de Almacén sin paquete')

