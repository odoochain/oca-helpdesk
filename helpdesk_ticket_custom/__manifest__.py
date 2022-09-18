# -*- coding: utf-8 -*-
#
# Autor: Julián Toscano
# Email: jotate70@gmail.com
# Desarrollador y funcional Odoo
# Github: jotate70
# Cel. +57 3147754740
#
#
{
    'name': "helpdesk ticket custom",

    'summary': """
        This module creates new models and fields to extend the functionality of the helpdesk tickets,
        and website tickets form
        """,

    'description': """
        Module that extends functionality in the helpdesk module and add website tickets form

        15.0.1
        15.0.2
        15.1.0
        15.2.0 industry fsm suport
        15.3.0 Added filter on website for internal and external tickets
        15.3.1 fix filter create by on website
        15.4.0 the department field is added to be used in the filter and grouping in the view
        15.5.0 Team grouping is added to the web portal
        15.1.1 bug fix filter all on website
        15.2.0 The family and subgroup field is hidden and the type field is included in the website.
        15.3.0 The helpdesk module is related to projects.
    """,

    'author': "Author: Julián Toscano, https://www.linkedin.com/in/jotate70/",
    'website': "https://www.andirent.co",

    'category': 'helpdesk',
    'version': '3.0',

    # any module necessary for this one to work correctly
    'depends': [
                'helpdesk',
                'helpdesk_fsm',
                'website_helpdesk_form',
                'contacts',
                'project',
                'hr',
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views_helpdesk_classification.xml',
        'views/views_helpdesk_family.xml',
        'views/views_helpdesk_project.xml',
        'views/views_helpdesk_sub_group.xml',
        'views/views_helpdesk_task_extended.xml',
        'views/views_helpdesk_team_extended.xml',
        'views/views_helpdesk_ticket_extended.xml',
        'views/views_helpdesk_partner_extended.xml',
        'views/views_helpdesk_users_extended.xml',
        'views/helpdesk_templates_o.xml',
        'views/helpdesk_portal_templates.xml',
        'views/project_inherit_view.xml',
        'views/views_project_location.xml',
        'views/helpdesk_custom_views.xml',
    ],
    'installable': True,
    'application': True,

    'assets': {
        'web.assets_frontend': [
            'helpdesk_ticket_custom/static/src/js/script.js',
        ],
        'website.assets_editor': [
            'helpdesk_ticket_custom/static/src/js/website_helpdesk_form_editor.js',
        ],
    },

    'license': 'LGPL-3',
}
