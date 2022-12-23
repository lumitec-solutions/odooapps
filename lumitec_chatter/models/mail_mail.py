##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo.http import request
from odoo import fields, models


class MailMail(models.Model):
    _inherit = "mail.mail"

    def send_mail_to_non_contact(self, email, content):
        mail_values = {
            'email_from': request.env.company.email_formatted,
            'reply_to': request.env.company.email_formatted,
            'email_to': email,
            'subject': 'subject',
            'body_html':
                '<p>' + content + 'p',
            'is_notification': True,
        }
        mail = request.env['mail.mail'].sudo().create(mail_values)
        mail.send()
