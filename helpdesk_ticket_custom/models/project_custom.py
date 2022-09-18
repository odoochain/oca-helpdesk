# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Project(models.Model):
    _inherit = "project.project"
    _description = 'Help desk project'

    partner_project_id = fields.Many2many(comodel_name='res.partner', relation='x_project_project_res_partner_rel',
                                          column1='project_project_id', column2='res_partner_id', string='Company')
    current_location = fields.Many2one(comodel_name='project_location', string='Current Location',
                                       help="Add the city where the client's headquarters are located")
