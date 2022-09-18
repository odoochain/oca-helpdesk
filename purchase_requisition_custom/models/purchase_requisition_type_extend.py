# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _

class PurchaseRequisitionType(models.Model):
    _inherit = "purchase.requisition.type"

    disable_approval = fields.Boolean(string='No pedir aprobación')


