# -*- coding: utf-8 -*-
# Part of Odoo. See ICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
import json

class ReturnPickingLine(models.TransientModel):
    _inherit = 'stock.return.picking.line'

    location = fields.Many2one(comodel_name='location_warehouse', string='Locación', related='wizard_id.location',
                               help='Muestra la ciudad/locación del almacén')
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='De almacen', help='Almacen de origen')
    location_origin_id = fields.Many2one(comodel_name='stock.location', string='Return Location',
                                         domain="location_domain")
    return_location_id = fields.Many2one(comodel_name='stock.location', compute='_compute_return_location_id')
    stock_quant_ids = fields.One2many(comodel_name='stock.quant', inverse_name='return_picking_line_id',
                                      string='Detail Operation')

    @api.onchange('product_id')
    def _compute_return_location_id(self):
        for rec in self.product_id.categ_id.return_location_id:
            if rec.location_id2 == self.location:
                self.return_location_id = rec.id

class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    location = fields.Many2one(comodel_name='location_warehouse', string='Locación',
                               help='Muestra la ciudad/locación del almacén')
    warehouse_domain = fields.Char(string="domain warehouse", compute='_domain_warehouse_domain_id')
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='De almacen', help='Almacen de origen',
                                   domain='warehouse_domain')
    type_return = fields.Selection([('picking', 'Por Transferencias'),
                                    ('product', 'Por producto')], store=True,
                                   string='Return Type', help='Indica el tipo de devolución', default="picking")
    location_domain = fields.Char(string="domain location", compute='_domain_location_origin_id')
    location_origin_id = fields.Many2one(comodel_name='stock.location', string='Return Location',
                                         domain="location_domain")
    picking_domain_ids = fields.Char(string="domain pickings", compute='_domain_pickings_id')
    stock_picking_ids = fields.Many2many(comodel_name='stock.picking', string='Envio para devolver 2',
                                         domain="picking_domain_ids")
    stock_quant_domain = fields.Char(string="domain stock quant", compute='_domain_stock_quant_ids')
    stock_quant_ids = fields.Many2many(comodel_name='stock.quant', string='Stock Quant', domain='stock_quant_domain')
    related_stock_picking = fields.Boolean(string="relation ticket")

    # realciona y crea registro product_return_moves con stock_quant_ids
    @api.onchange('stock_quant_ids')
    def _compute_stock_picking(self):
        product = []
        if self.product_return_moves and self.related_stock_picking == True:
            self.product_return_moves = False
        for rec in self.mapped('stock_quant_ids').product_id:
            qty = 0
            product = []
            for rec2 in self.mapped('stock_quant_ids'):
                if rec.id == rec2.product_id.id:
                    product.append(rec2.id)
                    qty = rec2.quantity + qty
            self.write({'product_return_moves': [(0, 0, {'product_id': rec,
                                                         'quantity': qty,
                                                         'stock_quant_ids': product,
                                                          })]})

    @api.onchange('type_return')
    def _reset_stock_picking_ids(self):
        for rec in self:
            if rec.type_return == 'product' and rec.related_stock_picking == True:
                rec.stock_picking_ids = False
                rec.product_return_moves = False
            elif rec.type_return == 'picking' and rec.related_stock_picking == True:
                rec.stock_quant_ids = False
                rec.product_return_moves = False

    @api.onchange('location_origin_id')
    def _reset_stock_picking(self):
        for rec in self:
            if rec.location_origin_id and rec.related_stock_picking == True:
                rec.stock_picking_ids = False
                rec.product_return_moves = False

    @api.onchange('warehouse_id')
    def _reset_location_origin_id(self):
        self.location_origin_id = False

    # warehouse domain
    @api.depends('location')
    def _domain_warehouse_domain_id(self):
        if self.location:
            for rec in self:
                rec.warehouse_domain = json.dumps(
                    [('location_id', "=", rec.location.ids), ('usage', '=', 'internal')])
        else:
            self.warehouse_domain = json.dumps([])

    # Stock quant domain
    @api.depends('location_origin_id')
    def _domain_stock_quant_ids(self):
        if self.location_origin_id:
            for rec in self:
                rec.stock_quant_domain = json.dumps(
                    [('location_id', "=", rec.location_origin_id.ids), ('usage', '=', 'internal'),
                     ('location_id.usage', '=', 'internal'), ('available_quantity', '>', 0.0)])
        else:
            self.stock_quant_domain = json.dumps([])

    # Origin location domain
    @api.depends('warehouse_id')
    def _domain_location_origin_id(self):
        if self.warehouse_id:
            for rec in self:
                rec.location_domain = json.dumps([('id', "=", rec.mapped('suitable_picking_ids').location_dest_id.ids),
                                                  ('warehouse_id', '=', rec.warehouse_id.ids), ('usage', 'in', ['supplier', 'internal', 'customer'])])
        else:
            self.location_domain = json.dumps([])

    # pickings domain
    @api.depends('location_origin_id')
    def _domain_pickings_id(self):
        if self.location_origin_id:
            for rec in self:
                rec.picking_domain_ids = json.dumps([('id', 'in', self.mapped('suitable_picking_ids').filtered(lambda m: m.location_dest_id == rec.location_origin_id).ids)])
        else:
            self.picking_domain_ids = json.dumps([])

    @api.onchange('stock_picking_ids')
    def _onchange_stocok_picking_ids(self):
        move_dest_exists = False
        product_return_moves = [(5,)]
        for rec in self.stock_picking_ids:
            if rec and rec.state == 'done':
                raise UserError(_("You may only return Done pickings."))
        # In case we want to set specific default values (e.g. 'to_refund'), we must fetch the
        # default values for creation.
        line_fields = [f for f in self.env['stock.return.picking.line']._fields.keys()]
        product_return_moves_data_tmpl = self.env['stock.return.picking.line'].default_get(line_fields)
        for move in self.stock_picking_ids:
            if move.move_lines.state == 'cancel':
                continue
            if move.move_lines.scrapped:
                continue
            if move.move_lines.move_dest_ids:
                move_dest_exists = True
            product_return_moves_data = dict(product_return_moves_data_tmpl)
            product_return_moves_data.update(self._prepare_stock_return_picking_line_vals_from_move_ids(move.move_lines))
            product_return_moves.append((0, 0, product_return_moves_data))  # Se añade registro en la variable flotante
        if self.stock_picking_ids and not product_return_moves:
            raise UserError(
                _("No products to return (only lines in Done state and not fully returned yet can be returned)."))
        if self.stock_picking_ids:
            self.product_return_moves = product_return_moves
            self.product_return_moves = product_return_moves
            self.move_dest_exists = move_dest_exists
            self.parent_location_id = self.stock_picking_ids.picking_type_id.warehouse_id and self.stock_picking_ids.picking_type_id.warehouse_id.view_location_id.id or self.stock_picking_ids.location_id.location_id.id
            self.original_location_id = self.stock_picking_ids.location_id.id
            location_id = self.stock_picking_ids.location_id.id
            if self.stock_picking_ids.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
                location_id = self.stock_picking_ids.picking_type_id.return_picking_type_id.default_location_dest_id.id
            self.location_id = location_id

    @api.model
    def _prepare_stock_return_picking_line_vals_from_move_ids(self, stock_move):
        quantity = stock_move.product_qty
        for move in stock_move.move_dest_ids:
            if move.origin_returned_move_id and move.origin_returned_move_id == stock_move:
                continue
            if move.state in ('partially_available', 'assigned'):
                quantity -= sum(move.move_line_ids.mapped('product_qty'))
            elif move.state in ('done'):
                quantity -= move.product_qty
        quantity = float_round(quantity, precision_rounding=stock_move.product_id.uom_id.rounding)
        a = self.env['stock.move'].search([('id', '=', stock_move.ids)])
        return {
            'product_id': stock_move.product_id.id,
            'quantity': quantity,
            'move_id': a,
            'uom_id': stock_move.product_id.uom_id.id,
        }

    def _prepare_picking_default_values(self):
        # Stock picking origin concatenate
        if self.picking_id:
            return {
                'move_lines': [],
                'picking_type_id': self.picking_id.picking_type_id.return_picking_type_id.id or self.picking_id.picking_type_id.id,
                'state': 'draft',
                'origin': _("Return of %s") % self.picking_id.name,
                'location_id': self.picking_id.location_dest_id.id,
                'location_dest_id': self.location_id.id
            }
        string = ''
        if self.stock_picking_ids:
            for rec in self.stock_picking_ids:
                string += ' [ ' + rec.name + ']'
                type_operation = rec.picking_type_id.return_picking_type_id.id or rec.picking_type_id.id
            return {
                'move_lines': [],
                'picking_type_id': type_operation,
                'state': 'draft',
                'origin': _("Return of %s") % string,
                'location_id': self.location_origin_id.id,
                'location_dest_id': self.location_id.id,
            }

    def _create_returns(self):
        # TODO sle: the unreserve of the next moves could be less brutal
        for return_move in self.product_return_moves.mapped('move_id'):
            return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()

        # create new picking for returned products
        if self.picking_id:
            new_picking = self.picking_id.copy(self._prepare_picking_default_values())
            picking_type_id = new_picking.picking_type_id.id
            new_picking.message_post_with_view('mail.message_origin_link',
                values={'self': new_picking, 'origin': self.picking_id},
                subtype_id=self.env.ref('mail.mt_note').id)
        else:
            for rec in self.stock_picking_ids:
                picking = rec
            new_picking = picking.copy(self._prepare_picking_default_values())
            picking_type_id = new_picking.picking_type_id.id
            new_picking.message_post_with_view('mail.message_origin_link',
                                               values={'self': new_picking, 'origin': self.stock_picking_ids},
                                               subtype_id=self.env.ref('mail.mt_note').id)
        returned_lines = 0
        for return_line in self.product_return_moves:
            if not return_line.move_id:
                raise UserError(_("You have manually created product lines, please delete them to proceed."))
            # TODO sle: float_is_zero?
            if return_line.quantity:
                returned_lines += 1
                vals = self._prepare_move_default_values(return_line, new_picking)
                r = return_line.move_id.copy(vals)
                vals = {}

                # +--------------------------------------------------------------------------------------------------------+
                # |       picking_pick     <--Move Orig--    picking_pack     --Move Dest-->   picking_ship
                # |              | returned_move_ids              ↑                                  | returned_move_ids
                # |              ↓                                | return_line.move_id              ↓
                # |       return pick(Add as dest)          return toLink                    return ship(Add as orig)
                # +--------------------------------------------------------------------------------------------------------+
                move_orig_to_link = return_line.move_id.move_dest_ids.mapped('returned_move_ids')
                # link to original move
                move_orig_to_link |= return_line.move_id
                # link to siblings of original move, if any
                move_orig_to_link |= return_line.move_id \
                    .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel')) \
                    .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel'))
                move_dest_to_link = return_line.move_id.move_orig_ids.mapped('returned_move_ids')
                # link to children of originally returned moves, if any. Note that the use of
                # 'return_line.move_id.move_orig_ids.returned_move_ids.move_orig_ids.move_dest_ids'
                # instead of 'return_line.move_id.move_orig_ids.move_dest_ids' prevents linking a
                # return directly to the destination moves of its parents. However, the return of
                # the return will be linked to the destination moves.
                move_dest_to_link |= return_line.move_id.move_orig_ids.mapped('returned_move_ids') \
                    .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel')) \
                    .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel'))
                vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link]
                vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
                r.write(vals)
        if not returned_lines:
            raise UserError(_("Please specify at least one non-zero quantity."))
        new_picking.action_confirm()
        new_picking.action_assign()
        return new_picking.id, picking_type_id

    def _create_return_2(self):
        # --------------------------------------   Stage 1 -------------------------------------------------------
        l = []
        a = []
        for rec1 in self.stock_quant_ids:
            # Condición para solo tipos de productos almacenable y consubles
            if rec1.product_id.detailed_type != 'service':
                if rec1.transit_location_id:
                    l.append(rec1.transit_location_id.id)
                    a = list(set(l))
                else:
                    raise UserError('No se ha establecido una ubicación de tránsito en la categoría de productos.')
        for rec2 in a:
            picking = self.env['purchase.order.line'].search(
                [('transit_location_id', '=', rec2), ('order_id', '=', self.ids),
                 ('product_qty', '!=', 0)], limit=1)
            create_vals = {'stage': 1,
                           'partner_id': self.partner_id.id,
                           'order_id2': self.id,
                           'origin': self.name,
                           'scheduled_date': self.date_planned,
                           'picking_type_id': picking.transit_location_id.warehouse_id.in_type_id.id,
                           'location_id': picking.location_id.id,
                           'location_dest_id': picking.transit_location_id.id,
                           'requisition_id': self.requisition_id.id,
                           'currency_id': self.currency_id.id,
                           'purchase_bol': True,
                           }
            stock_picking1 = self.env['stock.picking'].create(create_vals)
            # Código que crea una nueva actividad
            create_activity = {
                'activity_type_id': 4,
                'summary': 'Transferencia, Ingreso de invetario:',
                'automated': True,
                'note': 'Ha sido asignado para validar el ingreso de inventario',
                'date_deadline': fields.datetime.now(),
                'res_model_id': self.env['ir.model']._get_id('stock.picking'),
                'res_id': stock_picking1.id,
                'user_id': picking.warehouse_id.employee_id.user_id.id,
            }
            new_activity1 = self.env['mail.activity'].sudo().create(create_activity)
            # Escribe el id de la actividad en un campo
            stock_picking1.write({'activity_id': new_activity1.id})
        picking_ids = []
        for rec3 in self.order_line:
            if rec3.product_id.detailed_type != 'service':
                stock_picking2 = self.env['stock.picking'].search(
                    [('order_id2', '=', self.ids), ('requisition_id', '=', self.requisition_id.ids),
                     ('picking_type_id', '=', rec3.transit_location_id.warehouse_id.in_type_id.ids),
                     ('location_dest_id', '=', rec3.transit_location_id.ids), ('stage', '=', 1)], limit=1)
                # Creación de registros necearios para el stock picking move
                self.write({'x_stock_picking_transit_order_line': [(0, 0, {'stage': 1,
                                                                           'order_id': self.id,
                                                                           'purchase_line_id': rec3.id,
                                                                           'stock_picking_id': stock_picking2.id,
                                                                           'product_id': rec3.product_id.id,
                                                                           'picking_type_id': rec3.transit_location_id.warehouse_id.in_type_id.id,
                                                                           'location_id': rec3.location_id.id,
                                                                           'transit_location_id': rec3.transit_location_id.id,
                                                                           'dest_warehouse_id': rec3.warehouse_id.id,
                                                                           'dest_location_id': rec3.location_dest_id.id,
                                                                           'account_analytic_id': rec3.account_analytic_id.id,
                                                                           'quantity': rec3.product_qty,
                                                                           'product_uom': rec3.product_uom.id,
                                                                           })]})
        for rec4 in self.x_stock_picking_transit_order_line:
            if rec4.stage == 1:
                create_vals2 = {
                    'stage': 1,
                    'origin': self.name,
                    'purchase_line_id': rec4.purchase_line_id.id,
                    'name': rec4.stock_picking_id.name,
                    'picking_id': rec4.stock_picking_id.id,
                    'product_id': rec4.product_id.id,
                    'product_uom': rec4.product_uom.id,
                    'product_uom_qty': rec4.quantity,
                    'quantity_done': 0,
                    'location_id': rec4.location_id.id,
                    'location_dest_id': rec4.transit_location_id.id,
                    'date_deadline': fields.datetime.now(),
                }
                self.env['stock.move'].sudo().create(create_vals2)
        # Confirma stock picking en etapa 1
        for rect in self.picking_ids:
            if rect.stage == 1 and rect.state != 'cancel':
                rect.action_confirm()

        # -------------------------------------------   Stage 2 -------------------------------------------------------
        r = []
        b = []
        for rc1 in self.order_line:
            # Condición para solo tipos de productos almacenable y consubles
            if rc1.product_id.detailed_type != 'service':
                if rc1.location_dest_id:
                    r.append(rc1.location_dest_id.id)
                    b = list(set(r))
                else:
                    raise UserError('No se ha establecido una ubicación de destino.')
        for rec5 in b:
            picking2 = self.env['stock_picking_transit_order_line'].search(
                [('dest_location_id', '=', rec5), ('order_id', '=', self.ids)], limit=1)
            create_vals3 = {'stage': 2,
                            'partner_id': self.partner_id.id,
                            'order_id2': self.id,
                            'origin': picking2.stock_picking_id.name,
                            'parent_stock_picking': picking2.stock_picking_id.id,
                            'scheduled_date': self.date_planned,
                            'picking_type_id': picking2.dest_location_id.warehouse_id.int_type_id.id,
                            'location_id': picking2.transit_location_id.id,
                            'location_dest_id': picking2.dest_location_id.id,
                            'requisition_id': self.requisition_id.id,
                            'currency_id': self.currency_id.id,
                            'purchase_bol': True,
                            }
            self.env['stock.picking'].create(create_vals3)
        for rec6 in self.order_line:
            if rec6.product_id.detailed_type != 'service':
                stock_picking4 = self.env['stock.picking'].search(
                    [('order_id2', '=', self.ids), ('requisition_id', '=', self.requisition_id.ids),
                     ('picking_type_id', '=', rec6.location_dest_id.warehouse_id.int_type_id.ids),
                     ('location_dest_id', '=', rec6.location_dest_id.ids), ('stage', '=', 2)], limit=1)
                # Creación de registros necearios para el stock picking move
                self.write({'x_stock_picking_transit_order_line': [(0, 0, {'stage': 2,
                                                                           'order_id': self.id,
                                                                           'purchase_line_id': rec6.id,
                                                                           'stock_picking_id': stock_picking4.id,
                                                                           'product_id': rec6.product_id.id,
                                                                           'picking_type_id': rec6.location_dest_id.warehouse_id.in_type_id.id,
                                                                           'location_id': rec6.location_id.id,
                                                                           'transit_location_id': rec6.transit_location_id.id,
                                                                           'dest_warehouse_id': rec6.warehouse_id.id,
                                                                           'dest_location_id': rec6.location_dest_id.id,
                                                                           'account_analytic_id': rec6.account_analytic_id.id,
                                                                           'quantity': rec6.product_qty,
                                                                           'product_uom': rec6.product_uom.id,
                                                                           })]})
        for rec7 in self.x_stock_picking_transit_order_line:
            if rec7.stage == 2:
                create_vals4 = {
                    'stage': 2,
                    'origin': self.name,
                    'purchase_line_id': rec7.purchase_line_id.id,
                    'name': rec7.stock_picking_id.name,
                    'picking_id': rec7.stock_picking_id.id,
                    'product_id': rec7.product_id.id,
                    'product_uom': rec7.product_uom.id,
                    'product_uom_qty': rec7.quantity,
                    'quantity_done': 0,
                    'location_id': rec7.transit_location_id.id,
                    'location_dest_id': rec7.dest_location_id.id,
                    'date_deadline': fields.datetime.now(),
                }
                self.env['stock.move'].sudo().create(create_vals4)

