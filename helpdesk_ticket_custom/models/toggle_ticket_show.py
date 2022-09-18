# -*- coding: utf-8 -*-
from odoo import models, fields

class helpdesk_partner_extended(models.Model):
    _inherit = 'res.partner'

    x_ticket_show = fields.Boolean(string='Mostrar en tickets', help='Este boton permite mostrar el contacto en los tickets')
