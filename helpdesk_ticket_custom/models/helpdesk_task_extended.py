# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions

# Se hereda el campo de ticket en el modelo de tareas
class helpdesk_task_extended(models.Model):
    _inherit = 'project.task'

    helpdesk_ticket_id = fields.Many2one(comodel_name='helpdesk.ticket',
                                         string='Ticket',
                                         help='Ticket this task was generated from')

    department = fields.Many2many(comodel_name='hr.department', relation='x_hr_department_project_task_rel',
                                  column1='project_task_id', column2='hr_department_id',
                                  string='Departamento', compute='_get_department', store=True)

    # Relaciona el departamento con el empleado asignado
    @api.depends('user_ids')
    def _get_department(self):
        if self.user_ids:
            self.department = self.user_ids.department_id.ids
        else:
            self.department = False












