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
        print('hhhhhhhhhhhhhhhhhhhhhhh',email,'sssss', content)
        # post = request.env['onyx.social.post'].search([('client_name', '=', kw.get('client_name'))], limit=1)
        # print(post.read(), 'llllllllllllllllllllllllllll', kw)
        # link = 'https://applixodoo-onyx-main-staging-5077041.dev.odoo.com/' + 'web/login'
        mail_values = {
            'email_from': request.env.company.email_formatted,
            'reply_to': request.env.company.email_formatted,
            'recipient_ids': email,
            'subject': 'subject',
            'body_html':
                '<p>' + content + 'p',
            'is_notification': True,
        }
        mail = request.env['mail.mail'].sudo().create(mail_values)
        mail.send()