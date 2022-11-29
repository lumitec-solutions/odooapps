##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
from odoo import http
from odoo.http import request
from odoo.addons.link_tracker.controller.main import LinkTracker


class LinkTrackerVisitor(LinkTracker):

    @http.route('/r/<string:code>', type='http', auth='public', website=True)
    def full_url_redirect(self, code, **post):
        """Will add the campaigns that the visitors come from"""
        res = super(LinkTrackerVisitor, self).full_url_redirect(code, **post)
        visitor_sudo = request.env[
            'website.visitor']._get_visitor_from_request()
        if visitor_sudo:
            code_rec = request.env['link.tracker.code'].sudo().search(
                [('code', '=', code)])
            if code_rec and code_rec.link_id and code_rec.link_id.campaign_id:
                visitor_sudo.campaign_ids = [(4, code_rec.link_id.campaign_id.id)]
        return res
