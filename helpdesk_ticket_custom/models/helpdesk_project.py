# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions

# Se crea modelo proyecto
class helpdesk_project(models.Model):
    _name = 'helpdesk_project'
    _description = 'Proyecto en mesa de ayuda'

    name = fields.Char(string='Nombre', required="True")
    x_code = fields.Char(string='Codigo', required="True", help='Agregar el código de centro de costo')
    current_location = fields.Char(string='Ubicación actual',
                                   help='Agregar la ciudad donde se encuentra la sede del cliente')
    partner_id = fields.Many2many(comodel_name='res.partner', relation='x_helpdesk_project_res_partner_rel',
                                  column1='helpdesk_project_id', column2='res_partner_id', string='Compañias')

    # Restricción a nivel de SQL
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'El proyecto ya existe'),
    ]

    # Permite concatenar el name y la cuenta an analitica
    def name_get(self):
        result = []
        for rec in self:
            name = rec.name + ' [ ' + rec.x_code + ' ]'
            result.append((rec.id, name))
        return result
