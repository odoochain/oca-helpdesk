from odoo import fields, models, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    stock_quant = fields.One2many(comodel_name='stock.quant', inverse_name='product_tmpl_id',
                                  string='Inventario disponible')
    available_stock = fields.Float(string='Disponible', compute='_compute_available_stock')


    # Indica el stock en bodegas internas
    def _compute_available_stock(self):
        for rec2 in self:
            data = rec2.env['stock.quant'].sudo().search(
                [('product_tmpl_id', '=', rec2.ids), ('usage', '=', 'internal'),
                 ('location_id.usage', '=', 'internal'),
                 ('available_quantity', '>', 0)])
            if data:
                for rec in data:
                    rec2.available_stock += rec.available_quantity
            else:
                rec2.available_stock = 0









