from odoo import fields, models, api, _
from odoo.tools.float_utils import float_compare, float_is_zero

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    default_code = fields.Char(string='referencia', related='product_id.default_code')
    location = fields.Many2one(comodel_name='location_warehouse',
                               string='Locación', related='warehouse_id.location_id',
                               help='Muestra la ubicación de la ciudad/locación del producto',
                               )
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='Almacen', store=True,
                                          related='location_id.warehouse_id', help='Almacen origen')
    transit_location_id = fields.Many2one(comodel_name='stock.location', string='Ubicación de transito',
                                          related='location_id.transit_location_id',
                                          help='Solo se permite una ubicación de transito por almacen')
    fee_unit = fields.Float(string='Tarifa unitaria')
    plaque_id = fields.Many2one(comodel_name='stock_production_plaque', string='Placa', index=True)
    contract_date = fields.Date(string='Inicio de contrato',
                                help='Indica la fecha que se realiza el contrato asociada a dicha transferencia')
    contract_date_end = fields.Date(string='Finalización de contrato',
                                help='Indica la fecha que se realiza el contrato asociada a dicha transferencia')
    product_category_id = fields.Many2one(comodel_name='product.category', name='Categoria de producto', related='product_id.categ_id', store=True)
    usage = fields.Selection([
        ('supplier', 'Almacen Cliente'),
        ('internal', 'Almacen Interno'),
        ('customer', 'Almacen Proveedor')], string='Tipo de almacén',
        index=True, required=True, related='warehouse_id.usage',
        help="* Vendor Location: Virtual location representing the source location for products coming from your vendors"
             "\n* Internal Location: Physical locations inside your own warehouses,"
             "\n* Customer Location: Virtual location representing the destination location for products sent to your customers")

    @api.model
    def _update_available_quantity(self, product_id, location_id, quantity, lot_id=None, plaque_id=None, package_id=None, owner_id=None,
                                   in_date=None, fee_unit=fee_unit, contract_date=contract_date, contract_date_end=contract_date_end):
        """ Increase or decrease `reserved_quantity` of a set of quants for a given set of
        product_id/location_id/lot_id/package_id/owner_id.

        :param product_id:
        :param location_id:
        :param quantity:
        :param lot_id:
        :param plaque_id:
        :param package_id:
        :param owner_id:
        :param fee_unit:
        :param contract_date:
        :param contract_date_end:
        :param datetime in_date: Should only be passed when calls to this method are done in
                                 order to move a quant. When creating a tracked quant, the
                                 current datetime will be used.
        :return: tuple (available_quantity, in_date as a datetime)
        """
        self = self.sudo()
        quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id,
                              strict=True)

        if location_id.should_bypass_reservation():
            incoming_dates = []
        else:
            incoming_dates = [quant.in_date for quant in quants if quant.in_date and
                              float_compare(quant.quantity, 0, precision_rounding=quant.product_uom_id.rounding) > 0]
        if in_date:
            incoming_dates += [in_date]
        # If multiple incoming dates are available for a given lot_id/package_id/owner_id, we
        # consider only the oldest one as being relevant.
        if incoming_dates:
            in_date = min(incoming_dates)
        else:
            in_date = fields.Datetime.now()

        quant = None
        if quants:
            # see _acquire_one_job for explanations
            self._cr.execute("SELECT id FROM stock_quant WHERE id IN %s LIMIT 1 FOR NO KEY UPDATE SKIP LOCKED",
                             [tuple(quants.ids)])
            stock_quant_result = self._cr.fetchone()
            if stock_quant_result:
                quant = self.browse(stock_quant_result[0])

        if quant:
            quant.write({
                'quantity': quant.quantity + quantity,
                'in_date': in_date,
            })
        else:
            self.create({
                'product_id': product_id.id,
                'location_id': location_id.id,
                'quantity': quantity,
                'lot_id': lot_id and lot_id.id,
                'plaque_id': plaque_id and plaque_id.id,
                'package_id': package_id and package_id.id,
                'owner_id': owner_id and owner_id.id,
                'in_date': in_date,
                'fee_unit': fee_unit,
                'contract_date': contract_date,
                'contract_date_end': contract_date_end,
            })
        return self._get_available_quantity(product_id, location_id, lot_id=lot_id, package_id=package_id,
                                            owner_id=owner_id, strict=False, allow_negative=True), in_date










