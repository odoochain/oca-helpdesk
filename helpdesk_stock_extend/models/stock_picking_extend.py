# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    _description = 'Quants'

    stock_return_line = fields.Many2one(comodel_name='stock.return.picking.line', string="Related return line")
