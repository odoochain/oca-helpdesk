# -*- coding: utf-8 -*-
from datetime import datetime, time

from odoo import api, fields, models
import json

class purchase_requisition_line_extend(models.Model):
    _inherit = 'purchase.requisition.line'

    image_product = fields.Binary(string='Imagen', related='product_id.image_1920')
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', compute='_compute_product_qty')
    available_quantity_total = fields.Float(string='Stock', related='product_id.available_stock',
                                 help='Muestra la cantidad disponible que está sin reservar')
    qty_location = fields.Float(string='Disponible', store=True,
                                 help='Muestra la cantidad disponible en la ubicación selecionada del producto')
    location = fields.Many2one(comodel_name='location_warehouse', string='Locación',
                                               help='Muestra la ubicación de la ciudad/locación del producto',
                                               )
    location_id_domain = fields.Char(compute="_compute_location_stock_picking", readonly=True, store=False)
    picking_type_id = fields.Many2one(comodel_name='stock.picking.type', string='Tipo de operación',
                                      related="warehouse_id.int_type_id")
    property_stock_inventory = fields.Many2one(comodel_name='stock.location',
                                               string='Mover de',
                                               help='Muestra la ubicación del producto en el inventario',
                                               )
    location_dest_id_domain = fields.Char(compute="_compute_location_dest_id", readonly=True, store=False)
    default_location_dest_id = fields.Many2one(comodel_name='stock.location', string='A ubicación',
                                               help='Ubicación a mover, con filtro de almacane y ubicación interna, cliente')
    inventory_product_qty = fields.Float(string='Cantidad inventario', compute='_compute_inventory_product_qty',
                                         help='Cantidad de pruductos que deseas sacar o mover de inventario')
    product_qty2 = fields.Float(string='Cantidad', help='Cantidad de pruductos solicitado')
    show_picking = fields.Boolean(string='show', related='requisition_id.show_picking',
                                  help='Mostrar/ocultar el button y smart button de solicitud de compra')
    name_picking = fields.Char(comodel_name='stock.location', related='product_id.name')
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='A almacen',
                                   domain="[('usage', '!=', 'customer'), ('available_requisition', '=', 'True')]",
                                   help='Almacen a mover')
    observations = fields.Text(string='Observaciones')
    x_project = fields.Many2one(comodel_name='helpdesk_project', string='Proyecto',
                                help='El proyecto está relacionado con su respectivo centro de costo')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    transit_location_id = fields.Many2one(comodel_name='stock.location', string='Ubicación de transito', store=True,
                                          help='Solo se permite una ubicación de transito por almacen')

    # Seleciona la ubicación de transito
    @api.onchange('default_location_dest_id')
    def _compute_transit_location(self):
        # Determina la ubicación de transito por defecto en ordenes de compra
        if self.warehouse_id.usage == 'internal':
            a = self.warehouse_id.transit_location_id
        else:
            virtual_transit_location = self.env['stock.location'].search(
                [('usage', '=', 'transit'), ('id', '=', self.product_id.categ_id.location_id.ids),
                 ('location_id.location_id2', '=', self.default_location_dest_id.location_id2.ids),
                 ('warehouse_id', '=', self.warehouse_id.ids)], limit=1)
            if virtual_transit_location:
                a = virtual_transit_location
            else:
                location = self.env['stock.location'].search(
                    [('usage', '=', 'transit'), ('id', '=', self.product_id.categ_id.location_default.ids)],
                    limit=1)
                a = location
        self.write({'transit_location_id': a})

    #   Función resetea locación de destino al seleciona almacen y seleciona la ubicación de transito
    @api.onchange('warehouse_id')
    def _reset_location_dest(self):
        self.write({'default_location_dest_id': False})

    # Contabilidad analítica
    @api.onchange('default_location_dest_id')
    def _compute_account_analytic_id(self):
        self.account_analytic_id = self.default_location_dest_id.account_analytic_id

    # Función que aplica filtro dinamico de localización del producto en inventario
    @api.onchange('location')
    @api.depends('product_id')
    def _compute_location_stock_picking(self):
        for rec in self:
            rec.location_id_domain = json.dumps(
                [('usage', '=', 'internal'), ('id', "=", rec.product_id.stock_quant.location_id.ids),
                 ('location_id2', '=', rec.location.ids)])

    # Función que filtra la ubicación a mover por ubicación tipo cliente e interno, y que tenga un almacen relacionado
    @api.depends('warehouse_id')
    def _compute_location_dest_id(self):
        for rec in self:
            rec.location_dest_id_domain = json.dumps(
                [('available_requisition', '=', True), ('warehouse_id', '=', rec.warehouse_id.ids), ('usage', '=', ['internal', 'customer'])]
            )

    #   Función que calcula la cantidad de stock por ubicación
    @api.onchange('location', 'product_id', 'warehouse_id', 'default_location_dest_id', 'product_qty2', 'state', 'show_picking')
    def compute_qty_available_location(self):
        c = 0
        if self.location:
            for rec in self.product_id.stock_quant:
                if rec.location == self.location and rec.location_id.usage == 'internal' and rec.usage == 'internal' and rec.product_id == self.product_id:
                    c = c + rec.available_quantity
                self.qty_location = c
        else:
            self.qty_location = 0
        return

    # Función que calcula la cantidad de inventario a mover
    @api.onchange('product_qty2')
    @api.depends('qty_location')
    def _compute_inventory_product_qty(self):
        for rec in self:
            if rec.product_qty2 <= rec.qty_location:
                rec.inventory_product_qty = rec.product_qty2
            else:
                rec.inventory_product_qty = rec.qty_location

    # Función que calcula la cantidad a comprar
    @api.onchange('product_qty2')
    @api.depends('qty_location')
    def _compute_product_qty(self):
        for rec2 in self:
            if rec2.product_qty2 > rec2.qty_location:
                rec2.product_qty = rec2.product_qty2 - rec2.qty_location
            else:
                rec2.product_qty = 0

    # Función concatena la descripción del producto en la descripción
    @api.onchange('product_id')
    def _related_product_description_variants(self):
        for rec in self.product_id:
            if rec.description_purchase:
                a = rec.description_purchase
                b = ' - '
            else:
                a = ''
                b = ''
            result = '[' + str(rec.default_code) + '] ' + str(rec.name) + b + str(a)
            self.write({'product_description_variants': result})


    # Prepara las lineas de puchase order line
    def _prepare_purchase_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        # # Determina la ubicación de transito por defecto en ordenes de compra
        # if self.warehouse_id.usage == 'internal':
        #     a = self.warehouse_id.transit_location_id
        # else:
        #     virtual_transit_location = self.env['stock.location'].search(
        #         [('usage', '=', 'transit'), ('id', '=', self.product_id.categ_id.location_id.ids),
        #          ('location_id.location_id2', '=', self.default_location_dest_id.location_id2.ids),
        #          ('warehouse_id', '=', self.warehouse_id.ids)], limit=1)
        #     if virtual_transit_location:
        #         a = virtual_transit_location
        #     else:
        #         location = self.env['stock.location'].search(
        #             [('usage', '=', 'transit'), ('id', '=', self.product_id.categ_id.location_default.ids)],
        #             limit=1)
        #         a = location
        # Optiene lineas para ordenes de compra
        self.ensure_one()
        requisition = self.requisition_id
        if self.product_description_variants:
            if self.product_description_variants == self.product_id.display_name:
                name += '\n'
            else:
                name += '\n'
        if requisition.schedule_date:
            date_planned = datetime.combine(requisition.schedule_date, time.min)
        else:
            date_planned = datetime.now()
        return {
            'name': name,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id,
            'product_qty': product_qty,
            'price_unit': price_unit,
            'taxes_id': [(6, 0, taxes_ids)],
            'date_planned': date_planned,
            'account_analytic_id': self.account_analytic_id.id,
            'analytic_tag_ids': self.analytic_tag_ids.id,
            'warehouse_id': self.warehouse_id.id,
            'transit_location_id': self.transit_location_id.id,
            'location_dest_id': self.default_location_dest_id.id,
        }




























































