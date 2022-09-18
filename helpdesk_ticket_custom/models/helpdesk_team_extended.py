# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from lxml import etree

# heredamos del modelo helpdesk team
class helpdesk_team_extended(models.Model):
    _inherit = 'helpdesk.team'

    x_visibility = fields.Boolean(string='Visibilidad de clasificación', help='Permite mostrar el campo clasificación en los ticket')

