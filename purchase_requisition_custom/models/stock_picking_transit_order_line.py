from odoo import fields, models, _

class stock_picking_transit_order_line(models.Model):
    _name = 'stock_picking_transit_order_line'
    _description = "Stock picking transit order line"

    stage = fields.Integer(string='Etapa')
    order_id = fields.Many2one(comodel_name='purchase.order', string='Order Reference', index=True, required=True,
                               ondelete='cascade')
    purchase_line_id = fields.Many2one('purchase.order.line',
                                       'Purchase Order Line', ondelete='set null', index=True, readonly=True)
    stock_picking_id = fields.Many2one(comodel_name='stock.picking', string='Stock picking')
    product_id = fields.Many2one(comodel_name='product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 required=True)
    picking_type_id = fields.Many2one(comodel_name='stock.picking.type', string='Tipo de operación')
    location_id = fields.Many2one(comodel_name='stock.location',
                                  string='De ubicación',
                                  help='Muestra la ubicación del producto en el inventario',
                                  )
    transit_location_id = fields.Many2one(comodel_name='stock.location', string='Ubicación de transito',
                                          help='Solo se permite una ubicación de transito por almacen')
    dest_warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='A almacen', help='Almacen origen')
    dest_location_id = fields.Many2one(comodel_name='stock.location',
                                         string='A ubicación',
                                         help='Muestra la ubicación del producto en el inventario',
                                         )
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    quantity = fields.Float(string='qty', help='Muestra la cantidad pedida por ubicación')
    product_uom = fields.Many2one(comodel_name='uom.uom', string='Product Unit of Measure')


