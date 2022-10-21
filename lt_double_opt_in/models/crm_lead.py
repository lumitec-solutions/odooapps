##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
from odoo import api, fields, models


class Lead(models.Model):
    _inherit = 'crm.lead'

    double_opt_in = fields.Boolean(string='Double Opt-In', readonly=True, copy=False)
    mail_opt_in = fields.Boolean(string='Mail Opt-In', readonly=True, copy=False)
    can_manually_set_double_opt_in = fields.Boolean("Can Manually Set Double Opt In",
                                                    compute="_compute_can_set_double_opt_in")

    def _compute_can_set_double_opt_in(self):
        for record in self:
            if record.user_has_groups('lt_double_opt_in.can_manually_set_double_opt_in_lead'):
                record.can_manually_set_double_opt_in = True
            else:
                record.can_manually_set_double_opt_in = False

    @api.model
    def create(self, vals):
        record = super(Lead, self).create(vals)
        if record.tag_ids and record.email_from:
            record.send_double_opt_in_email()
            record.mail_opt_in = True
        return record

    def write(self, vals):
        res = super(Lead, self).write(vals)
        if 'email_from' in vals:
            for record in self:
                record.double_opt_in = False
        if 'tag_ids' in vals or 'email' in vals:
            for record in self:
                if not record.mail_opt_in:
                    record.send_double_opt_in_email()
                record.mail_opt_in = False
        return res

    def unlink(self):
        for record in self:
            lead_token = self.env['crm.lead.token'].sudo().search([('lead_id', '=', record.id)])
            if lead_token:
                lead_token.unlink()
        return super(Lead, self).unlink()

    def send_double_opt_in_email(self):
        if self.double_opt_in or not self.email_from:
            return
        for tag in self.tag_ids:
            if tag.send_double_opt_in:
                template = self.env.ref('lt_double_opt_in.mypatent_double_opt_in_email_template')
                template.send_mail(self.id, force_send=True)
                return

    def generate_access_token(self, action):
        crm_lead_token = self.env['crm.lead.token'].create({
            'lead_id': self.id,
            'action': action,
        })
        return crm_lead_token.get_url()
