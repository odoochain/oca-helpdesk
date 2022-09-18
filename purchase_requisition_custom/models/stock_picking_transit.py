from odoo import fields, models


class stock_picking_transit(models.Model):
    _name = 'stock_picking_transit'
    _description = "Stock picking transit"

    stage = fields.Integer(string='Etapa')
    requisition_id = fields.Many2one(comodel_name='purchase.requisition', required=True, string='Purchase Agreement',
                                     ondelete='cascade')
    stock_picking_id = fields.Many2one('stock.picking', string='Stock picking')
    product_id = fields.Many2one(comodel_name='product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 required=True)
    name_picking = fields.Char(comodel_name='stock.location', related='product_id.name')
    product_description_variants = fields.Char('Custom Description')
    picking_type_id = fields.Many2one(comodel_name='stock.picking.type', string='Tipo de operación')
    origin_location = fields.Many2one(comodel_name='location_warehouse',
                               string='Locación',
                               help='Muestra la ubicación de la ciudad/locación del producto',
                               )
    origin_warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='De Almacen', help='Almacen origen')
    origin_location_id = fields.Many2one(comodel_name='stock.location',
                                               string='De ubicación',
                                               help='Muestra la ubicación del producto en el inventario',
                                               )
    parent_location_id = fields.Many2one(comodel_name='stock.location',
                                         string='Ubicación padre',
                                         help='Muestra la ubicación padre del producto en el inventario',
                                         )
    transit_location_id = fields.Many2one(comodel_name='stock.location', string='Ubicación de transito',
                                          help='Solo se permite una ubicación de transito por almacen')
    dest_warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='A almacen', help='Almacen origen')
    dest_location_id = fields.Many2one(comodel_name='stock.location',
                                         string='A ubicación',
                                         help='Muestra la ubicación del producto en el inventario',
                                         )
    concatenate_location = fields.Char(string='Concatenar locación')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    available_quantity_total = fields.Float(string='Stock', help='Muestra la cantidad disponible que está sin reservar')
    qty_location = fields.Float(string='Disponible',
                                help='Muestra la cantidad disponible en la ubicación selecionada del producto')
    quantity = fields.Float(string='qty', help='Muestra la cantidad pedida por ubicación')
    observations = fields.Text(string='Observaciones')
    product_uom = fields.Many2one(comodel_name='uom.uom', string='Product Unit of Measure')

