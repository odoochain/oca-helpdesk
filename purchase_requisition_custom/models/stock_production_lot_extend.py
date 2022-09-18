from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    plaque_id = fields.Many2one(comodel_name='stock_production_plaque', string='Placa')

    # Realaciona la placa/tarifa/fecha de contrato con numero de serie desde el modelo stock move line
    def compute_plaque_id(self):
        data = self.env['stock.move.line'].search([('lot_id', '=', self.ids),
                                                   ('product_id', '=', self.product_id.ids),
                                                   ('qty_done', '=', self.product_qty)], limit=1, order='id DESC')
        self.plaque_id = data.plaque_id.id

    # Restricción de placas aociadas a un serial/lote
    @api.constrains('plaque_id')
    def _compute_constrains_plaque(self):
        for rec in self:
            exist_lines = []
            for line in rec.plaque_id.lot_ids:
                if line:
                    exist_lines.append(line.ids)
                    a = len(exist_lines)
                    if a > 1:
                        raise UserError('La placa ya se encuentra asociada al serial %s.' % line.name)


    # @api.constrains('name', 'plaque_id', 'product_id', 'company_id')
    # def _check_unique_lot(self):
    #     domain = [('product_id', 'in', self.product_id.ids),
    #               ('company_id', 'in', self.company_id.ids),
    #               ('plaque_id', 'in', self.plaque_id.ids),
    #               ('name', 'in', self.mapped('name'))]
    #     fields = ['company_id', 'plaque_id', 'product_id', 'name']
    #     groupby = ['company_id', 'plaque_id', 'product_id', 'name']
    #     records = self.read_group(domain, fields, groupby, lazy=False)
    #     error_message_lines = []
    #     for rec in records:
    #         if rec['__count'] != 1:
    #             product_name = self.env['product.product'].browse(rec['product_id'][0]).display_name
    #             plaque_name = self.env['stock_production_plaque'].browse(rec['plaque_id'][0]).display_name
    #             error_message_lines.append(_(" - Product: %s, %s Serial Number: %s %s", product_name, plaque_name, rec['name']))
    #     if error_message_lines:
    #         raise ValidationError(
    #             _('The combination of serial number and product must be unique across a company.\nFollowing combination contains duplicates:\n') + '\n'.join(
    #                 error_message_lines))






