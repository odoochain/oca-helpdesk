from odoo import fields, models, api, _
from odoo.tools.float_utils import float_compare, float_is_zero

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    return_picking_line_id = fields.Many2one(Comodel='stock.return.picking.line', string='Return Picking Line')
