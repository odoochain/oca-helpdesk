# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

# heredamos del modelo de tickets de mesa ayuda
class helpdesk_ticket_requisition(models.Model):
    _inherit = 'helpdesk.ticket'

    requisition_id = fields.Many2one(comodel_name='purchase.requisition', string='Acuerdo de compra',
                                     )

    requisition_many2many = fields.Many2many(comodel_name='purchase.requisition',
                                        relation='x_helpdesk_ticket_purchase_requisition_rel',
                                        column1='helpdesk_ticket_id', column2='purchase_requisition_id',
                                        string='Acuerdo de compra')

    # permite asociar al acuerdo de compra cuando se crea un ticker desde el smart button
    @api.onchange('requisition_id')
    @api.depends('requisition_id')
    def _compute_ticket(self):
        for rec in self:
            if rec.requisition_id != False:
                rec.requisition_many2many = self.requisition_id

    # validación limite para asociar acuerdo de compra
    @api.onchange('requisition_many2many')
    def _compute_ticket_limit(self):
        c = 0
        for rec in self.requisition_many2many:
            c = c + 1
            if c > 1:
                raise UserError('Solo puede asociar un acuerdo de compra')




















