# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import json

# heredamos del modelo de tickets de mesa ayuda


class helpdesk_ticket_extended(models.Model):
    _inherit = 'helpdesk.ticket'

    x_visibility_related = fields.Boolean(string='Campo oculto', related='team_id.x_visibility', store=True,
                                          readonly=True)
    x_classification = fields.Many2one(comodel_name='helpdesk_classification', string='Clasificación')
    x_project = fields.Many2one(comodel_name='helpdesk_project', string='X Project',
                                help='El proyecto está relacionado con su respectivo centro de costo')
    x_family = fields.Many2one(comodel_name='helpdesk_family', string='Familia',
                               help='Familia a la que pertenece el requerimiento del ticket')
    x_sub_group = fields.Many2one(comodel_name='helpdesk_sub_group', string='Sub grupo',
                                  help='Subgrupo relacionado a cada familia')
    current_location = fields.Many2one(comodel_name='project_location', string='Ubicación actual',
                                       related='project.current_location', store=True,
                                       help='Agregar la ciudad donde se encuentra la sede del cliente')
    location = fields.Selection([('Bogotá', 'Bogotá'),
                                 ('Medellín', 'Medellín'),
                                 ('Barranquilla', 'Barranquilla'),
                                 ],
                                string='Locación', help='Indica la ciudad donde se ejecuta el proyecto', store=True)
    ticket_type = fields.Selection([('1', 'Ticket Interno'),
                                    ('2', 'Ticket Externo')],
                                   string='Tipo de ticket',
                                   help='Permite definir si es un ticket interno o un ticket desde el sitio web',
                                   required="True", store=True, default='2')
    project_domain = fields.Char(string='project domain', compute='_domain_depends_partner')
    project = fields.Many2one(comodel_name='project.project', string='Proyecto',
                              help='El proyecto está relacionado con su respectivo centro de costo')

    # Función que aplica filtro dinamico de proyecto
    @api.depends('partner_id')
    def _domain_depends_partner(self):
        project = self.env['project.project'].sudo().search([('partner_project_id', "=", self.partner_id.ids)])
        for rec in self:
            if self.partner_id:
                rec.project_domain = json.dumps([('id', "=", project.ids)])
            else:
                rec.project_domain = json.dumps([])















