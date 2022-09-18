# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions

# Se crea modelo sub grupo
class helpdesk_sub_group(models.Model):
    _name = 'helpdesk_sub_group'
    _description = 'Sub grupo en mesa de ayuda'

    name = fields.Char(string='Nombre', required="True")
    x_code = fields.Char(string='Código', required="True")
    x_family = fields.Many2one(comodel_name='helpdesk_family', string='Familia')

    # Restricción a nivel de SQL
    _sql_constraints = [
        ('x_code_unique', 'UNIQUE(x_code)', 'El codigo debe ser unico'),
    ]


