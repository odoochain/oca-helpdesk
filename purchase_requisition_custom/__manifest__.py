# -*- coding: utf-8 -*-
#
# Autor: Julián Toscano
# Email: jotate70@gmail.com
# https://www.linkedin.com/in/jotate70/
# Desarrollador y funcional Odoo
# Github: jotate70
# Cel. +57 3147754740
#

{
    'name': "Purchase Agreements Custom",

    'summary': """
        15.0.1 module that adds approvals by levels according to the budget of each immediate boss in the purchase requisitions.
        15.1.0 the option to assign stock picking tasks to warehouse managers will be added.
        15.2.0 ticket relationship with requisitions is added.
        15.2.1 Restrictions are added in fields.
        15.3.0 This versions contains stock movement in two steps, origin location to transit location, transit location to destination location. 
        15.4.0 Purchase order report and delivery voucher is added.
        15.5.0 Added option to pay for analytical accounting in stock picking.
        15.6.0 Automatic stock picking are added in purchase orders by destination location.
        15.6.1 error corrections.
        """,

    'description': """
        module that adds approvals by levels according to the budget of each immediate boss in the purchase requisitions.
    """,

    'author': "Author: Julián Toscano, https://www.linkedin.com/in/jotate70/",
    'website': "https://www.andirent.co",

    'category': 'Purchase',
    'version': '6.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase_requisition',
                'hr_holidays',
                'stock',
                'purchase_stock',
                'sale_stock',
                'helpdesk_ticket_custom',
                'web_domain_field',
                'account',
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/employee_extend_view.xml',
        'views/purchase_extend_view.xml',
        'views/purchase_requisition_extend_view.xml',
        'views/purchase_requisition_line_extend_view.xml',
        'views/users_extend_view.xml',
        'views/stock_picking_extend_view.xml',
        'views/product_template_extend_view.xml',
        'views/helpdesk_ticket_extended_view.xml',
        'views/stock_warehouse_extend_view.xml',
        'views/stock_location_form_extend_view.xml',
        'views/location_warehouse_view.xml',
        'views/stock_picking_move_extend_view.xml',
        'views/stock_picking_type_extend_view.xml',
        'views/account_analytic_line_extend_view.xml',
        'views/stock_quant_custom_view.xml',
        'views/stock_picking_move_line_extend_view.xml',
        'views/stock_move_line_extend_view.xml',
        'views/type_stock_picking_view.xml',
        'views/stock_production_lot_extend_view.xml',
        'views/stock_plaque_view.xml',
        'views/purchase_requisition_type_extend_view.xml',
        'views/product_category_extend.xml',
        'views/product_product_extend_view.xml',
        'report/report_purchaseorder_document_extend.xml',
        'report/report_deliveryslip_extend.xml',
        'wizard/stock_assign_serial_views_extend.xml',
    ],

    'installable': True,
    'application': True,

    'license': 'LGPL-3',

}
