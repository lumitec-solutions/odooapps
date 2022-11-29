##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
from odoo import fields, models, api


class WebsiteVisitor(models.Model):
    _inherit = 'website.visitor'

    campaign_ids = fields.Many2many('utm.campaign', string='Campaigns')
