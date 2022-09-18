# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions

# Se crea modelo family
class helpdesk_family(models.Model):
    _name = 'helpdesk_family'
    _description = 'Familia en mesa de ayuda'

    name = fields.Char(string='Nombre', required="True")
    x_code = fields.Char(string='Código', required="True")
    x_sub_group = fields.Many2many(comodel_name='helpdesk_sub_group',
                                   relation='helpdesk_relation_f_a_s',
                                   column1='id',
                                   column2='name',
                                   string='Sub grupo',
                                   readonly='False')

    # Restricción a nivel de SQL
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'La familia ya existe'),
    ]

