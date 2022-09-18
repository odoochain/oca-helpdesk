from odoo import fields, models, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    requisition_state = fields.Selection(string='Estado acuerdo de compra', related='requisition_id.state')
    related_requisition = fields.Boolean(string='relacion requicision', related='requisition_id.available')
    state_aprove = fields.Integer(string='nivel de aprobación')
    manager_before = fields.Many2one(comodel_name='hr.employee', string='Responsable de anterior')
    aprove_manager = fields.Many2one(comodel_name='hr.employee', string='Responsable de aprobación',
                                     help='Jefe responsable de aprobar la solicitud de compra')
    aprove_manager2 = fields.Many2one(comodel_name='hr.employee',
                                  string='Aprobación alternativa',
                                  help='Cuando el jefe inmediato se encuentra ausente, debe aprobar el siguiente respondable')
    representative_user = fields.Many2one(comodel_name='res.users', string='Representante de requisición', store=True,
                                          related='requisition_id.user_id', help='Usuario que solicita el acuerdo de compra')
    activity_id = fields.Integer(string='id actividad')
    # Obtiene la fecha y hora actual
    current_date = fields.Datetime('Fecha actual', required=False, readonly=False, select=True,
                                   default=lambda self: fields.datetime.now())
    time_off = fields.Char(string='Disponibilidad', compute='_compute_number_of_days')
    time_off_related = fields.Boolean(string='Ausencia', related='aprove_manager.is_absent')
    x_account_analytic_cost = fields.One2many(comodel_name='purchase_account_analytic_compute',
                                              inverse_name='purchase_order', string='subtotal cuentas analíticas')
    warehouse_manager = fields.Many2many(comodel_name='hr.employee', relation='x_hr_employee_stock_warehouse_rel',
                                         column1='stock_warehouse_id', column2='hr_employee_id',
                                         string='Responsable de almacen',
                                         related='picking_type_id.default_location_dest_id.warehouse_id.employee_id')
    mobile_phone = fields.Char(string='Teléfono celular',
                               related='picking_type_id.default_location_dest_id.warehouse_id.employee_id.mobile_phone')
    x_stock_picking_transit_order_line = fields.One2many(comodel_name='stock_picking_transit_order_line', inverse_name='order_id',
                                                         string='Stock picking transitorio_order_line')
    stock_picking_ids = fields.One2many(comodel_name='stock.picking', inverse_name='purchase_id', string='Recepciones')

    # Create stock pickings
    def stock_picking_create_order_line(self):
        # --------------------------------------   Stage 1 -------------------------------------------------------
        l = []
        a = []
        for rec1 in self.order_line:
            # Condición para solo tipos de procutos almacenable y consubles
            if rec1.product_id.detailed_type != 'service':
                if rec1.transit_location_id:
                    l.append(rec1.location_dest_id.id)
                    a = list(set(l))
                else:
                    raise UserError('No se ha establecido una ubicación de tránsito en la categoría de productos.')
        for rec2 in a:
            picking = self.env['purchase.order.line'].search([('location_dest_id', '=', rec2), ('order_id', '=', self.ids)], limit=1)
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
                stock_picking2 = self.env['stock.picking'].search([('order_id2', '=', self.ids), ('requisition_id', '=', self.requisition_id.ids),
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
            if rect.stage == 1:
                rect.action_confirm()

        # -------------------------------------------   Stage 2 -------------------------------------------------------
        for rec5 in a:
            picking2 = self.env['stock_picking_transit_order_line'].search([('dest_location_id', '=', rec5), ('order_id', '=', self.ids)], limit=1)
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
                            }
            self.env['stock.picking'].create(create_vals3)
        for rec6 in self.order_line:
            if rec6.product_id.detailed_type != 'service':
                stock_picking4 = self.env['stock.picking'].search([('order_id2', '=', self.ids), ('requisition_id', '=', self.requisition_id.ids),
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

    def get_default_color(self):
        self._get_default_color()    # seleción de color por estado

    # Color en ordenes de compra
    def _get_default_color(self):
        self.update_relate_purchase_order()     # Relación de tag de ordenes de compra con requisiciones
        if self.state == 'draft':
            self.write({'color': 4})
        elif self.state == 'sent':
            self.write({'color': 2})
        elif self.state == 'to approve':
            self.write({'color': 3})
        elif self.state == 'purchase':
            self.write({'color': 9})
        elif self.state == 'done':
            self.write({'color': 10})
        elif self.state == 'cancel':
            self.write({'color': 0})

    color = fields.Integer(string='Color')

    # Actualizar estado requisición
    @api.onchange('partner_id')
    def update_state_requisition(self):
            if self.requisition_id and self.requisition_state == 'assigned' or self.requisition_state == 'open':
                requisition_state = self.env['purchase.requisition'].search([('id', '=', self.requisition_id.ids)], limit=1)
                requisition_state.update({
                    'state': 'open',
                    'purchase_order_process': True,
                })

    # relaciona la orden de compra con el campo may2many de requisiciones
    def update_relate_purchase_order(self):
        requisition_state = self.env['purchase.requisition'].search([('id', '=', self.requisition_id.ids)], limit=1)
        requisition_state.update({
            'purchase_order_many2many': [(4, self.id)],
        })

    # Función que actualiza el responsable de aprobar
    @api.onchange('partner_id')
    def aprove_manager_employee(self):
        self.aprove_manager = self.requisition_id.manager_id

    # Indica si el jefe inmediato está o no está ausente
    @api.depends('time_off_related')
    def _compute_number_of_days(self):
        if self.time_off_related == False:
            self.time_off = 'Disponible'
        else:
           self.time_off = 'Ausente'
           self.write({'aprove_manager2': self.aprove_manager.parent_id})
        return self.time_off

    # Función del boton confirmar
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
                order.write({'state': 'to approve', 'color': 3})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

    # Función del boton confirmar sin requisición
    def button_confirm2(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order.write({'state': 'to approve', 'color': 3})
        return True

    # Función del boton confirmar extend
    def button_confirm_extend(self):
        self._get_default_color()  # seleción de color por estado
        # Calcular costo en cuentas analiticas
        self.compute_account_analytic_cost()
        # código nuevo con condición
        if self.related_requisition == True:
            self.update_state_requisition()  # Actualizar esatdo a open en la requisición
            self.update_relate_purchase_order()
            if self.aprove_manager and self.time_off_related == False:
                for order in self:
                    if order.state not in ['draft', 'sent']:
                        continue
                    order._add_supplier_to_product()
                    order.write({'state': 'to approve', 'color': 3})
                    # Código que crea una nueva actividad
                    model_id = self.env['ir.model']._get(self._name).id
                    create_vals = {
                        'activity_type_id': 4,
                        'summary': 'Solicitud de compra:',
                        'automated': True,
                        'note': 'Ha sido asignado para aprobar la siguiente solicitud de compra',
                        'date_deadline': self.current_date.date(),
                        'res_model_id': model_id,
                        'res_id': self.id,
                        'user_id': self.requisition_id.manager_id.user_id.id
                    }
                    new_activity = self.env['mail.activity'].create(create_vals)
                    # Escribe el id de la actividad en un campo
                    self.write({'activity_id': new_activity})
                    # Contador de niveles de aprobación
                    c = self.state_aprove + 1
                    self.write({'state_aprove': c})
                    if order.partner_id not in order.message_partner_ids:
                        order.message_subscribe([order.partner_id.id])
                return True
            # Si esta ausente el jefe inmediato se asigna tarea al siguiente responsable
            else:
                for order in self:
                    if order.state not in ['draft', 'sent']:
                        continue
                    order._add_supplier_to_product()
                    order.write({'state': 'to approve', 'color': 3})
                    # Código que crea una nueva actividad
                    model_id = self.env['ir.model']._get(self._name).id
                    create_vals = {
                        'activity_type_id': 4,
                        'summary': 'Solicitud de compra:',
                        'automated': True,
                        'note': 'Ha sido asignado para aprobar la siguiente solicitud de compra, el jefe responsable se encuentra ausente',
                        'date_deadline': self.current_date.date(),
                        'res_model_id': model_id,
                        'res_id': self.id,
                        'user_id': self.aprove_manager2.user_id.id
                    }
                    new_activity = self.env['mail.activity'].create(create_vals)
                    # Escribe el id de la actividad en un campo
                    self.write({'activity_id': new_activity})
                    # Contador de niveles de aprobación
                    c = self.state_aprove + 1
                    self.write({'state_aprove': c})
                    # aprobador alternativo
                    self.write({'aprove_manager': self.aprove_manager2})
                    if order.partner_id not in order.message_partner_ids:
                        order.message_subscribe([order.partner_id.id])
                return True
        elif self.requisition_id.state == 'cancel':
            raise UserError('El acuerdo de compra asociado está en estado cancelado.')
        elif self.requisition_id.state == 'draft' or self.requisition_id.state == 'in_progress':
            raise UserError('EL acuerdo de compra primero debe ser aprobado.')
        else:
            # Función por defecto
            self.button_confirm()

    def button_approve(self, force=False):
        self = self.filtered(lambda order: order._approval_allowed())
        self.write({'state': 'purchase', 'date_approve': fields.Datetime.now()})
        self.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
        return {}

    # Función del boton aprobación extend
    def button_approve_extend(self, force=False):
        if self.related_requisition == True:
            if self.env.user.employee_id.general_manager == False and self.env.user.employee_id.active_budget == True:  # Si tiene un tope
                # aprobación para el manager
                if self.aprove_manager.user_id == self.env.user:
                    # niveles de aprobación dependiendo el monto asignado al jefe inmediato
                    # si cumple la condición aprueba la orden, si no pide un nivel más
                    if self.amount_untaxed <= self.aprove_manager.budget:
                        #  Marca actividad como hecha de forma automatica
                        new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
                        new_activity.action_feedback(feedback='Es aprobado')
                        # Aprueba la orden
                        self.button_approve()
                        self.write({'color': 9})
                        if self.requisition_id:
                            self.stock_picking_create_order_line()  # Crea modelo de transición solo cuando existe requisición
                    else:
                        # está condición evita que repita aprobación
                        if self.aprove_manager != self.env.user.employee_id.parent_id:
                            #  Marca actividad anterior como hecha de forma automatica
                            new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
                            new_activity.action_feedback(feedback='Requiere otra aprobación')
                            # Contador de niveles de aprovación
                            c = self.state_aprove + 1
                            self.write({'state_aprove': c})
                            # jefe inmediato del jefe actual
                            users = self.env.user.employee_id.parent_id
                            self.write({'aprove_manager': users})
                            # se usa para avisar al usuario que ya aprobo la solictud
                            users_before = self.env.user.employee_id
                            self.write({'manager_before': users_before})
                            # Código que crea una nueva actividad y valida que no sea un genre general
                            model_id = self.env['ir.model']._get(self._name).id
                            create_vals = {
                                'activity_type_id': 4,
                                'summary': 'aprobación adicional, solicitud de compra:',
                                'automated': True,
                                'note': 'Ha sido asignado para aprobar la siguiente solicitud de compra, debido a que el montón supera la base del jefe a cargo',
                                'date_deadline': self.current_date.date(),
                                'res_model_id': model_id,
                                'res_id': self.id,
                                'user_id': self.aprove_manager.user_id.id
                                }
                            new_activity = self.env['mail.activity'].create(create_vals)
                            # Escribe el id de la nueva actividad para el siguiente nivel de aprobación
                            self.write({'activity_id': new_activity})
                        else:
                            raise UserError('Ya aprobaste la solicitud de compra, debes esperar a que su jefe inmediato apruebe ya que supera su monto asigando.')
                elif self.requisition_id.manager_id == self.env.user.employee_id:
                    raise UserError('Ya aprobaste la solicitud, Su jefe inmediato debe aprobar ya que supera su presupuesto asignado.')
                elif self.manager_before == self.env.user.employee_id:
                    raise UserError('Ya aprobaste la solicitud, Su jefe inmediato debe aprobar ya que supera su presupuesto asignado.')
                else:
                    raise UserError('El gerente responsable debe aprobar la solicitud.')
            elif self.env.user.employee_id.general_manager == True and self.env.user.employee_id.active_budget == True:
                #  Marca actividad anterior como hecha de forma automatica
                new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
                new_activity.action_feedback(feedback='Es aprobado')
                # aprobación gerente general
                self.button_approve()
                if self.requisition_id:
                    self.stock_picking_create_order_line()  # Crea modelo de transición solo cuando existe requisición
                self.write({'color': 9})
            elif self.env.user.employee_id.active_budget == False:
                raise UserError('No tiene asignado un monto de presupuesto o activa la opcíón sin tope, por favor comunicarse con el administrador para realizar asignación.')
        # Función de aprobación por defecto
        else:
            self.button_approve()
            self.write({'color': 9})
            if self.requisition_id:
                self.stock_picking_create_order_line()  # Crea modelo de transición solo cuando existe requisición

    # Botón reestableercer a borrador
    def button_draft(self):
        self.write({'x_stock_picking_transit_order_line': [(5)]})  # Limpiar/deslinkear registros del modelo
        self.write({'state': 'draft', 'color': 4})
        return {}

    # Botón reestableercer a borrador extend
    def button_draft_extend(self):
        self.button_draft()     # Función reestablecer
        # se reestablece el jefe actual
        self.write({'aprove_manager': self.requisition_id.manager_id})
        # se reestablece el jefe actual
        self.write({'manager_before': False})
        # se reestablece el nivel de aprobación
        self.write({'state_aprove': 0})
        # se reestablece la suma de cuentas x cuentas analiticas
        self.compute_account_analytic_cost_delete()
        return {}

    # Boton cancelar
    def button_cancel(self):
        for order in self:
            for inv in order.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(_("Unable to cancel this purchase order. You must first cancel the related vendor bills."))
        self.write({'state': 'cancel', 'mail_reminder_confirmed': False, 'color': 0})
        # Update state to cancel stock picking incoming
        for rec in self.stock_picking_ids:
            rec.action_cancel()

    # Boton cancelar extend
    def button_cancel_extend(self):
        self.button_cancel()  # Función cancelar
        #  Marca actividad como hecha de forma automatica
        new_activity = self.env['mail.activity'].search([('id', '=', self.activity_id)], limit=1)
        new_activity.action_feedback(feedback='Es Rechazado')

    # Accón contabilidad analítica
    def button_account_analytic_cost(self):
        if self.x_account_analytic_cost:
            return True
        else:
            self.compute_account_analytic_cost_delete()
            self.compute_account_analytic_cost()

    # Función borrar linea
    def compute_account_analytic_cost_delete(self):
        self.write({'x_account_analytic_cost': [(5)]})

    # subtotal los centros de costo x centro de costo
    def compute_account_analytic_cost(self):
        a = []
        b = []
        analytic_cost = 0
        for rec1 in self.order_line:
            if rec1.account_analytic_id:
                a.append(rec1.account_analytic_id.id)
                b = list(set(a))
        for rec2 in b:
            analytic_cost = 0
            for rec3 in self.order_line:
                if rec2 == rec3.account_analytic_id.id:
                    analytic_cost += rec3.price_subtotal
            self.write({'x_account_analytic_cost': [(0, 0, {'purchase_order_line': rec3.id,
                                                            'account_analytic_id': rec2,
                                                            'price_subtotal': analytic_cost,
                                                            })]})






















