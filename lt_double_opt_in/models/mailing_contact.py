##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
from odoo import api, fields, models


class MailingContact(models.Model):
    _inherit = 'mailing.contact'

    category_ids = fields.Many2many('mailing.tag', string='Mailing Tags')
    double_opt_in = fields.Boolean(string='Double Opt-In', readonly=True,
                                   copy=False)
    mail_opt_in = fields.Boolean(string='Mail Opt-In', readonly=True,
                                 copy=False)
    can_manually_set_double_opt_in = fields.Boolean(
        "Can Manually Set Double Opt In",
        compute="_compute_can_set_double_opt_in")

    def _compute_can_set_double_opt_in(self):
        for record in self:
            if record.user_has_groups(
                    'lt_double_opt_in.can_manually_set_double_opt_in_mailing'):
                record.can_manually_set_double_opt_in = True
            else:
                record.can_manually_set_double_opt_in = False

    @api.model
    def create(self, vals):
        """Send double opt-in mail when creates a record"""
        record = super(MailingContact, self).create(vals)
        if record.category_ids and record.email:
            record.send_double_opt_in_email()
            record.mail_opt_in = True
        return record

    def write(self, vals):
        """send double opt-in mail when updates a record"""
        res = super(MailingContact, self).write(vals)
        if 'email' in vals:
            for record in self:
                record.double_opt_in = False
        if 'category_ids' in vals or 'email' in vals:
            for record in self:
                if not record.mail_opt_in:
                    record.send_double_opt_in_email()
                record.mail_opt_in = False
        return res

    def unlink(self):
        """Deletes token when deleting the record"""
        for record in self:
            mailing_token = self.env['mailing.contact.token'].sudo().search(
                [('mailing_contact_id', '=', record.id)])
            if mailing_token:
                mailing_token.unlink()
        return super(MailingContact, self).unlink()

    def send_double_opt_in_email(self):
        """Send double opt-in mail"""
        if self.double_opt_in or not self.email:
            return
        conf_send_double_opt_in = self.env['ir.config_parameter'].sudo().get_param(
            'lt_double_opt_in.send_double_opt_in')
        for tag in self.category_ids:
            if tag.send_double_opt_in and conf_send_double_opt_in:
                template = self.env.ref(
                    'lt_double_opt_in.lt_double_opt_in_email_template')
                template.send_mail(self.id, force_send=True)
                return

    def generate_access_token(self, action):
        """creates access token"""
        mailing_contact_token = self.env['mailing.contact.token'].create({
            'mailing_contact_id': self.id,
            'action': action,
        })
        return mailing_contact_token.get_url()
