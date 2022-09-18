from odoo import fields, models, api


class users_extend(models.Model):
    _inherit = 'res.users'

    employee_id = fields.Many2one(comodel_name='hr.employee', string='Empleado relacionado')

