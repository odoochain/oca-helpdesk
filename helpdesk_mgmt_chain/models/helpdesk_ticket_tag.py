from odoo import fields, models


class HelpdeskTicketTag(models.Model):
    _name = "helpdesk.ticket.chain.tag"
    _description = "Helpdesk Ticket Chain Tag"

    name = fields.Char()
    color = fields.Integer(string="Color Index")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
