##############################################################################
# Copyright (c) 2021 brain-tec AG (https://bt-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
from odoo import api, models, fields
from collections import defaultdict


class Lead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, vals):
        email = vals.get('email_from')
        mailing_contact = self.env['mailing.contact'].sudo().search([('email', '=', email)])
        tags = []
        if 'tag_ids' in vals:
            crm_tag_ids = vals.get('tag_ids')[0][2]
            crm_tags = self.env['crm.tag'].browse(crm_tag_ids)
            for tag in crm_tags:
                if (self.env['mailing.tag'].sudo().search([('name', '=', tag.name)]).name == tag.name):
                    tag_value = self.env['mailing.tag'].search([('name', '=', tag.name)]).id
                    tags.append(tag_value)
        if (email not in mailing_contact.mapped(lambda self: self.email)) and (email != False):
            print('rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr')
            self.env['mailing.contact'].sudo().create({
                'email': email,
                'company_name': vals.get('partner_name'),
                'name': vals.get('partner_id'),
                'country_id': vals.get('country_id'),
                'category_ids': tags
            })
        if (email != False) and (email == mailing_contact.email):
            print('qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq')
            for tag in tags:
                mailing_contact.write({'category_ids': [(4, tag)]})

            # Merge new lead if it have set the merge flag and already a lead with this email exists
            # lead = self._merge_lead_with_existing_lead(vals)
            # if lead:
            #     return lead

        return super(Lead, self).create(vals)

    def write(self, vals):
        for rec in self:
            mailing_contact = self.env['mailing.contact'].sudo().search([('email', '=', rec.email_from)])
            tags = []
            if vals.get('tag_ids'):
                crm_tag_ids = vals.get('tag_ids')[0][2]
                crm_tags = self.env['crm.tag'].browse(crm_tag_ids)
                for tag in crm_tags:
                    tag_value_id = self.env['mailing.tag'].sudo().search([('name', '=', tag.name)])
                    if (tag_value_id.name == tag.name) and (tag_value_id.id not in mailing_contact.category_ids.ids):
                        tag_value = tag_value_id.id
                        tags.append(tag_value)
            for tag in tags:
                mailing_contact.write({'category_ids': [(4, tag)]})
        return super(Lead, self).write(vals)
