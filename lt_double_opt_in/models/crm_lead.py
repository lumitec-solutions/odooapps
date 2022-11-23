##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
from odoo import api, fields, models


class Lead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, vals):
        """merge the created leads with mailing contacts"""
        record = super(Lead, self).create(vals)
        if record.email_from:
            mailing_contacts = self.env['mailing.contact'].sudo().search([('email', '=', record.email_from)])
            for mailing_contact in mailing_contacts:
                if record.country_id:
                    mailing_contact.country_id = record.country_id
                for tag in record.tag_ids:
                    tag_id = self.env['mailing.tag'].search([('name', '=', tag.name)], limit=1)
                    if tag_id:
                        mailing_contact.category_ids = [(4, tag_id.id)]
                    else:
                        add_tag = self.env['mailing.tag'].create({
                            'name': tag.name})
                        mailing_contact.category_ids = [(4, add_tag.id)]
        return record

    def write(self, vals):
        """merge the leads with mailing contacts based on changes"""
        res = super(Lead, self).write(vals)
        if 'country_id' in vals or 'tag_ids' in vals:
            for record in self:
                mailing_contacts = self.env['mailing.contact'].sudo().search(
                    [('email', '=', record.email_from)])
                for mailing_contact in mailing_contacts:
                    mailing_contact.country_id = record.country_id
                    for tag in record.tag_ids:
                        tag_id = self.env['mailing.tag'].search(
                            [('name', '=', tag.name)], limit=1)
                        if tag_id:
                            mailing_contact.category_ids = [(4, tag_id.id)]
                        else:
                            add_tag = self.env['mailing.tag'].create({
                                'name': tag.name})
                            mailing_contact.category_ids = [(4, add_tag.id)]
        return res
