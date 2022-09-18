from odoo import fields, models, api


class stock_picking_extend(models.Model):
    _inherit = 'stock.picking.type'

    available_requisition = fields.Boolean(string='Puede usarse en ordenes de compra',
                                           help='Permite usar el tipo de operación en requisiciones en el apartado solicitudes de compra')


