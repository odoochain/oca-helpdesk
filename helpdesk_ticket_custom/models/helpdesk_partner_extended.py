# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json

# heredamos del modelo usuarios
class helpdesk_partner_extended(models.Model):
    _inherit = 'res.partner'

    x_ticket_show = fields.Boolean(string='Mostrar en tickets',
                                   help='Este boton permite mostrar el contacto en los tickets')

    x_project = fields.Many2many(comodel_name='helpdesk_project',
                                 relation='x_helpdesk_project_res_partner_rel',
                                 column1='res_partner_id',
                                 column2='helpdesk_project_id',
                                 string='Proyecto',
                                 )
    project_domain = fields.Char(string='project domain', compute='_compute_project_domain2')
    project = fields.Many2many(comodel_name='project.project',
                                 relation='x_project_project_res_partner_rel',
                                 column1='res_partner_id',
                                 column2='project_project_id',
                                 string='Proyecto',
                                 )

    # Función que aplica filtro dinamico de almacen
    @api.depends('parent_id')
    def _compute_project_domain2(self):
        project = self.env['project.project'].sudo().search([('id', "=", self.parent_id.project.ids)])
        if self.parent_id:
            for rec in self:
                rec.project_domain = json.dumps([('id', "=", project.ids)])
        else:
            for rec in self:
                rec.project_domain = json.dumps([])






















