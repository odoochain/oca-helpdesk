from odoo import http
from odoo.http import request
from odoo.tools import is_html_empty
from odoo.addons.website_helpdesk.controllers import main
from lxml import etree
import json

class WebsiteHelpdesk(main.WebsiteHelpdesk):

    def _get_partner_data(self):
        partner = request.env.user.partner_id
        #partner = False
        if partner != request.website.user_id.sudo().partner_id:
            #partner_values['name'] = partner.name or ''
            #partner_values['email'] = partner.email or ''
            return partner
        return partner

    @http.route(['/helpdesk', '/helpdesk/<model("helpdesk.team"):team>'], type='http', auth="public", website=True, sitemap=True)
    def website_helpdesk_teams(self, team=None, **kwargs):
        search = kwargs.get('search')
        # For breadcrumb index: get all team
        teams = request.env['helpdesk.team'].search(['|', '|', ('use_website_helpdesk_form', '=', True), ('use_website_helpdesk_forum', '=', True), ('use_website_helpdesk_slides', '=', True)], order="id asc")
        if not request.env.user.has_group('helpdesk.group_helpdesk_manager'):
            teams = teams.filtered(lambda team: team.website_published)
        if not teams:
            return request.render("website_helpdesk.not_published_any_team")
        result = self.get_helpdesk_team_data(team or teams[0], search=search)
        # For breadcrumb index: get all team
        result['teams'] = teams
        if teams:
            #default_form = etree.fromstring(request.env.ref('helpdesk_ticket_custom.website_helpdesk_form_ticket_submit_form_inherit').arch)
            default_form = etree.fromstring(request.env.ref('website_helpdesk_form.ticket_submit_form').arch)
            for t in teams:
                xmlid = 'website_helpdesk_form.team_form_' + str(t.id)
                ir = request.env['ir.ui.view'].sudo().search([('name', '=', xmlid)])
                if ir:
                    ir.sudo().write({'arch': etree.tostring(default_form)})
        result['is_html_empty'] = is_html_empty
        partner_id = request.env.user.partner_id
        #new
        helpdesk_family = request.env['helpdesk_family'].sudo().search([])
        ticket_type_id = request.env['helpdesk.ticket.type'].sudo().search([])
        #result['partner_name'] = partner_values.get('name')
        result['partner_id'] = partner_id
        result['helpdesk_family'] = helpdesk_family
        result['ticket_type_id'] = ticket_type_id
        if partner_id.project:
            result['projects'] = partner_id.project
        else:
            result['projects'] = []
        return request.render("website_helpdesk.team", result)

    @http.route(['/familty/sub_grupo/<int:family_id>'], type='http', auth="public", methods=['GET'], website=True, csrf=False)
    def get_county_all(self, family_id=0):
        ar = []
        if family_id:
            sub_groups = request.env['helpdesk_sub_group'].sudo().search([('x_family', '=', int(family_id))])
            for s in sub_groups:
                ar.append({
                    'id': s.id,
                    'name': s.name
                })
        return json.dumps(ar)