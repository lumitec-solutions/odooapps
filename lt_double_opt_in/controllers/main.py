##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
import logging
import werkzeug
from dateutil.relativedelta import relativedelta

from odoo import http, fields, _
from odoo.http import request
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class LeadTokenController(http.Controller):

    @http.route(['/lead/manage'], type='http', auth="public", website=True, sitemap=False)
    def manage_lead(self, access_token=None, **post):

        def redirect_to_double_opt_in_fail_page():
            fail_page = request.env.ref('lt_double_opt_in.double_opt_in_fail').sudo()
            if not fail_page or not fail_page.is_published:
                raise ValidationError(_('Your Link is wrong or expired! Please contact us or start a '
                                        'new subscription to get a new link.'))
            return werkzeug.utils.redirect(fail_page.url or '/')

        if not access_token:
            return redirect_to_double_opt_in_fail_page()

        lead_token_obj = request.env['crm.lead.token']
        config_param = request.env['ir.config_parameter']
        token_valid_days = config_param.sudo().get_param('lt_double_opt_in.token_valid_days', default='7')
        valid_date = fields.Date.today() - relativedelta(days=int(token_valid_days))
        lead_token = lead_token_obj.sudo().search([('access_token', '=', access_token),
                                                   ('token_generation_date', '>=', valid_date)], limit=1)

        if lead_token and lead_token.action == 'double_opt_in':
            if not lead_token.lead_id.double_opt_in:
                lead_token.lead_id.double_opt_in = True

            success_page = request.env.ref('lt_double_opt_in.double_opt_in_success').sudo()
            if not success_page or not success_page.is_published:
                return werkzeug.utils.redirect('/')
            return werkzeug.utils.redirect(success_page.url or '/')
        else:
            return redirect_to_double_opt_in_fail_page()
