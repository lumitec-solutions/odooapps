##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
from odoo import fields, models


class Tag(models.Model):
    _inherit = 'crm.tag'

    send_double_opt_in = fields.Boolean(string='Send Double Opt-In', copy=False)
