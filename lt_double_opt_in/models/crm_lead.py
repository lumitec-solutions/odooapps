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

    # salutation_id = fields.Many2one('res.partner.salutation',
    #                                 string='Salutation', ondelete="restrict")

    # FIELDS_TO_MERGE = ['tag_ids', 'double_opt_in']

    @api.model
    def create(self, vals):
        email = vals.get('email_from', False)
        mailing_contact = self.env['mailing.contact'].sudo().search([('email', '=', self.email_from)])
        if 'tag_ids' in vals:
            crm_tag_ids = vals.get('tag_ids')[0][2]
            crm_tags = self.env['crm.tag'].browse(crm_tag_ids)
            tags = []
            for tag in crm_tags:
                if (self.env['mailing.tag'].sudo().search([('name', '=', tag.name)]).name == tag.name):
                    tag_value = self.env['mailing.tag'].search([('name', '=', tag.name)]).id
                    print(tags, 'ssssssssssss', tag_value)
                    tags.append(tag_value)
            # for tag in crm_tags:
            #     elif (self.env['res.partner.category'].search([('name', '=', tag.name)]).name != tag.name):
            #         new_tags = self.env['res.partner.category'].create({
            #             'name': tag.name
            #         })
            #         tags.append(new_tags.id)
            if email not in mailing_contact.mapped(lambda self: self.email):
                self.env['mailing.contact'].sudo().create({
                    'email': email,
                    'company_name': vals.get('partner_name'),
                    'name': vals.get('partner_id'),
                    'country_id': vals.get('country_id'),
                    'category_ids': tags
                })
            if self.email_from == mailing_contact.email:
                for tag in tags:
                    mailing_contact.write({'category_ids': [(4, tag)]})

        # Merge new lead if it have set the merge flag and already a lead with this email exists
        # lead = self._merge_lead_with_existing_lead(vals)
        # if lead:
        #     return lead

        return super(Lead, self).create(vals)

    def write(self, vals):
        mailing_contact = self.env['mailing.contact'].sudo().search([]).filtered(lambda x: self.email_from == x.email)
        if vals.get('tag_ids'):
            crm_tag_ids = vals.get('tag_ids')[0][2]
            crm_tags = self.env['crm.tag'].browse(crm_tag_ids)
            tags = []
            for tag in crm_tags:
                tag_value_id = self.env['mailing.tag'].sudo().search([('name', '=', tag.name)])
                if (tag_value_id.name == tag.name) and (tag_value_id.id not in mailing_contact.category_ids.ids):
                    tag_value = tag_value_id.id
                    tags.append(tag_value)
                # for tag in crm_tags:
                # elif (self.env['res.partner.category'].search([('name', '=', tag.name)]).name != tag.name):
                #     new_tags = self.env['res.partner.category'].create({
                #         'name': tag.name
                #     })
                #     tags.append(new_tags.id)

                    for tag in tags:
                        mailing_contact.write({'category_ids': [(4, tag)]})
        return super(Lead, self).write(vals)

    # def _resolve_2many_commands(self, field_name, commands, fields=None):
    #     """ Serializes one2many and many2many commands into record dictionaries
    #         (as if all the records came from the database via a read()).  This
    #         method is aimed at onchange methods on one2many and many2many fields.
    #
    #         Because commands might be creation commands, not all record dicts
    #         will contain an ``id`` field.  Commands matching an existing record
    #         will have an ``id``.
    #
    #         :param field_name: name of the one2many or many2many field matching the commands
    #         :type field_name: str
    #         :param commands: one2many or many2many commands to execute on ``field_name``
    #         :type commands: list((int|False, int|False, dict|False))
    #         :param fields: list of fields to read from the database, when applicable
    #         :type fields: list(str)
    #         :returns: records in a shape similar to that returned by ``read()``
    #             (except records may be missing the ``id`` field if they don't exist in db)
    #         :rtype: list(dict)
    #     """
    #     result = []                     # result (list of dict)
    #     record_ids = []                 # ids of records to read
    #     updates = defaultdict(dict)     # {id: vals} of updates on records
    #
    #     for command in commands or []:
    #         if not isinstance(command, (list, tuple)):
    #             record_ids.append(command)
    #         elif command[0] == 0:
    #             result.append(command[2])
    #         elif command[0] == 1:
    #             record_ids.append(command[1])
    #             updates[command[1]].update(command[2])
    #         elif command[0] in (2, 3):
    #             record_ids = [id for id in record_ids if id != command[1]]
    #         elif command[0] == 4:
    #             record_ids.append(command[1])
    #         elif command[0] == 5:
    #             result, record_ids = [], []
    #         elif command[0] == 6:
    #             result, record_ids = [], list(command[2])
    #
    #     # read the records and apply the updates
    #     field = self._fields[field_name]
    #     records = self.env[field.comodel_name].browse(record_ids)
    #     for data in records.read(fields):
    #         data.update(updates.get(data['id'], {}))
    #         result.append(data)
    #
    #     return result

    # def _merge_lead_with_existing_lead(self, vals):
    #
    #     email = vals.get('email_from', False)
    #     print(email,'email')
    #     lead = False
    #     if email:
    #         lead = self.with_context(active_test=False).search([('email_from', '=', email),
    #                                                             ('type', '=', 'lead')],
    #                                                            limit=1, order='id desc')
    #         print('lead',lead)
    #
    #     # Get categories
    #     tags = self._resolve_2many_commands('tag_ids', vals.get('tag_ids', []), fields=['id'])
    #     tag_ids = set(tag['id'] for tag in tags)
    #     tags = self.env['crm.tag'].browse(tag_ids)
    #     print('tttt',tag_ids,'t',tags)
    #
    #     # If tag merge flag is set update already existing lead instead of creating a new one
    #     if not (lead or any(tags.mapped('merge_lead_automatically'))):
    #         print('autoooo')
    #         return False
    #
    #     new_values = dict()
    #     print(new_values,'new_values',self.FIELDS_TO_MERGE)
    #     for column in vals:
    #         if column in self.FIELDS_TO_MERGE:
    #             print(column,'field_to_merge')
    #             # Same logic as in mypatent_parter to merge contacts.
    #             # Reused here as it is in separated module and modules should be independent one from the other.
    #             field = lead._fields[column]
    #             print(field,'fieldddddddddddd')
    #             if field.type not in ('many2many', 'one2many') and field.compute is None:
    #                 # Only update fields which are not already set
    #                 if not lead[column] and vals[column]:
    #                     print('11111111111111111111111111111111')
    #                     new_values[column] = vals[column]
    #
    #             elif field.type in ('many2many', 'one2many'):
    #                 print('22222222222222222222222222222')
    #                 many2many_values = []
    #                 records = self._resolve_2many_commands(column, vals.get(column, []), fields=['id'])
    #                 print(records,'records')
    #                 # Get records which not exists at the moment and must be created
    #                 values_to_create = [value for value in records if not value.get('id', False)]
    #                 print('values_to_create',values_to_create)
    #                 for value_to_create in values_to_create:
    #                     records.remove(value_to_create)
    #                     many2many_values.append((0, 0, value_to_create))
    #
    #                 # Get new IDs which are not already set on field
    #                 new_record_ids = [rec['id'] for rec in records if rec['id'] not in lead[column].ids]
    #                 print(new_record_ids,'new_record_ids')
    #                 if new_record_ids:
    #                     print('33333333333333333')
    #                     many2many_values.extend([(4, record_id) for record_id in new_record_ids])
    #
    #                 if many2many_values:
    #                     print('444444444444444444444444')
    #                     new_values[column] = many2many_values
    #                     print(many2many_values,'many2many_values')
    #                 print(many2many_values,'many2many_values_out')
    #
    #     old_values = {}
    #     for field in new_values.keys():
    #         print('aaaaaaaaaaaaaaaa')
    #         old_values[field] = lead[field]
    #         print(old_values[field],'old_values[field]')
    #
    #     # remove id that can not be updated
    #     new_values.pop('id', None)
    #     lead.write(new_values.copy())
    #
    #     tracking_value_ids = []
    #
    #     if new_values:
    #         lead_obj = self.env['crm.lead'].with_context(lang='en_US')
    #         # Field names should always be in english
    #         ref_tracked_fields = lead_obj.fields_get(list(new_values.keys()))
    #         lead = lead.with_context(lang='en_US')
    #         dummy, tracking_value_ids = lead._mail_track(ref_tracked_fields, old_values)
    #     # Message should always be in english
    #     body = 'Another lead was merged with this one. '
    #     if tracking_value_ids:
    #         body += 'The following fields are updated:'
    #     else:
    #         body += 'No fields are updated.'
    #     lead.message_post(body=body, tracking_value_ids=tracking_value_ids)
    #
    #     return lead
