# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions

# Se crea modelo clasificación
class helpdesk_classification(models.Model):
    _name = 'helpdesk_classification'
    _description = 'Clasificación en mesa de ayuda'

    name = fields.Char(string='Nombre', required="True")
    x_code = fields.Char(string='Código', required="True")

    # Restricción a nivel de SQL
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Classification already exists'),
    ]

