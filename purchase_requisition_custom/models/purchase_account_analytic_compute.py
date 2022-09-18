from odoo import api, fields, models


class purchase_account_analytic_compute(models.Model):
    _name = 'purchase_account_analytic_compute'
    _description = "Purchase account analytic"

    purchase_order = fields.Many2one(comodel_name='purchase.order', string='Purchase order')
    purchase_order_line = fields.Many2one(comodel_name='purchase.order.line', string='Purchase order line')
    account_analytic_id = fields.Many2one(comodel_name='account.analytic.account', string='Analytic Account')
    price_subtotal = fields.Float(string='Subtotal')



