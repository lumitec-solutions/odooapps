##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
import uuid
from odoo import fields, models, api


class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'

    token = fields.Char('Access token',
                        default=lambda self: str(uuid.uuid4()), readonly=True,
                        copy=False)

    @api.model
    def _generate_invite_token(self):
        return str(uuid.uuid4())

    def get_start_url(self):
        return '%s/%s' % (self.channel_id.website_url, self.token)
