##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import fields, models


class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    send_double_opt_in = fields.Boolean(string='Send Double Opt-In', copy=False)
