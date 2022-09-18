# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class helpdesk_users_extended(models.Model):
    _inherit = 'res.users'

    x_project = fields.Many2many(comodel_name='helpdesk_project',
                                 relation='x_helpdesk_project_res_partner_rel',
                                 column1='res_partner_id',
                                 column2='helpdesk_project_id',
                                 string='Proyecto')

    project = fields.Many2many(comodel_name='project.project',
                               relation='x_project_project_res_partner_rel',
                               column1='res_partner_id',
                               column2='project_project_id',
                               string='Proyecto',
                               )

    department_id = fields.Many2one(comodel_name='hr.department', string='Department',
                                    related='employee_id.department_id', store=True, )
