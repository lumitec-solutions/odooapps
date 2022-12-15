##############################################################################
# Copyright (c) 2020 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from lxml import etree
from collections import defaultdict


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        # Merge new partner if it have set the merge flag and already a partner with this email exists
        if 'category_id' in vals:
            email = vals.get('email', False)
            mailing_contact = self.env['mailing.contact'].sudo().search([('email', '=', self.email)])
            partner_tag_ids = vals.get('category_id')[0][2]
            partner_tags = self.env['res.partner.category'].browse(partner_tag_ids)
            tags = []
            for tag in partner_tags:
                if (self.env['mailing.tag'].search([('name', '=', tag.name)]).name == tag.name):
                    tag_value = self.env['mailing.tag'].sudo().search([('name', '=', tag.name)]).id
                    tags.append(tag_value)
            company_name = self.browse(vals.get('parent_id')).name
            if email not in mailing_contact.mapped(lambda self: self.email):
                self.env['mailing.contact'].sudo().create({
                    'email': vals.get('email', False),
                    'company_name': company_name if vals.get('parent_id') else vals.get('name'),
                    'name': vals.get('name'),
                    'country_id': self.browse(vals.get('parent_id')).country_id.id if ((vals.get('type') == 'contact') and (vals.get('company_type') == 'person')) else vals.get('country_id'),
                    'title_id': vals.get('title') if vals.get('title') else False,
                    'category_ids': tags,
                })
        partner = self._merge_partner_with_existing_partner(vals)
        if partner:
            return partner
        new_partner = super(ResPartner, self).create(vals)
        # new_partner._validate_email()
        return new_partner

    def write(self, vals):
        mailing_contact = self.env['mailing.contact'].sudo().search([('email', '=', self.email)],limit=1)
        if self.email == mailing_contact.email:
            if vals:
                tags = []
                if vals.get('category_id'):
                    if vals.get('category_id')[0][0] == 6:
                        contact_tag_ids = vals.get('category_id')[0][2]
                        partner_tags = self.env['res.partner.category'].browse(contact_tag_ids)
                    # else:
                    #     contact_tag_ids = vals.get('category_id')[0]
                        print(contact_tag_ids,'contact_tag_ids')

                        for tag in partner_tags:
                            tag_value_id = self.env['mailing.tag'].sudo().search([('name', '=', tag.name)])
                            if (tag_value_id.name == tag.name) and (tag_value_id.id not in mailing_contact.category_ids.ids):
                                tag_value = tag_value_id.id
                                print(tags, 'ssssssssssss', tag_value)
                                tags.append(tag_value)
                    else:
                        for tag in vals.get('category_id'):
                            print(tag[0],'ppppp',type(tag[1]))
                            mail_tag = self.env['res.partner.category'].browse(tag[1])
                            tag_value_id = self.env['mailing.tag'].search([('name', '=', mail_tag.name)])
                            if (mail_tag.name == tag_value_id.name) and (tag[1] not in mailing_contact.tag_ids.ids):
                                tag_value = tag_value_id.id
                                tags.append(tag_value)
                    for value in tags:
                        mailing_contact.update({'category_ids': [(4, value)]})
        return super(ResPartner, self).write(vals)

    def _resolve_2many_commands(self, field_name, commands, fields=None):
        """ Serializes one2many and many2many commands into record dictionaries
            (as if all the records came from the database via a read()).  This
            method is aimed at onchange methods on one2many and many2many fields.

            Because commands might be creation commands, not all record dicts
            will contain an ``id`` field.  Commands matching an existing record
            will have an ``id``.

            :param field_name: name of the one2many or many2many field matching the commands
            :type field_name: str
            :param commands: one2many or many2many commands to execute on ``field_name``
            :type commands: list((int|False, int|False, dict|False))
            :param fields: list of fields to read from the database, when applicable
            :type fields: list(str)
            :returns: records in a shape similar to that returned by ``read()``
                (except records may be missing the ``id`` field if they don't exist in db)
            :rtype: list(dict)
        """
        result = []  # result (list of dict)
        record_ids = []  # ids of records to read
        updates = defaultdict(dict)  # {id: vals} of updates on records

        for command in commands or []:
            if not isinstance(command, (list, tuple)):
                record_ids.append(command)
            elif command[0] == 0:
                result.append(command[2])
            elif command[0] == 1:
                record_ids.append(command[1])
                updates[command[1]].update(command[2])
            elif command[0] in (2, 3):
                record_ids = [id for id in record_ids if id != command[1]]
            elif command[0] == 4:
                record_ids.append(command[1])
            elif command[0] == 5:
                result, record_ids = [], []
            elif command[0] == 6:
                result, record_ids = [], list(command[2])

        # read the records and apply the updates
        field = self._fields[field_name]
        records = self.env[field.comodel_name].browse(record_ids)
        for data in records.read(fields):
            data.update(updates.get(data['id'], {}))
            result.append(data)

        return result

    def _merge_partner_with_existing_partner(self, vals):
        email = vals.get('email', False)
        is_company = vals.get('is_company', False)

        # Search for already existing partner
        partner = False
        if email:
            partner = self.with_context(active_test=False).search([('email', '=', email),
                                                                   ('is_company', '=', is_company)], limit=1,
                                                                  order='id desc')

        # If partner doesn't exist create a new one
        if not partner:
            return False

        # Update partner values
        new_values = dict()
        for column in vals:
            field = partner._fields[column]
            if field.type not in ('many2many', 'one2many') and field.compute is None:
                # Only update fields which are not already set
                if not partner[column] and vals[column]:
                    new_values[column] = vals[column]

            elif field.type in ('many2many', 'one2many'):
                many2many_values = []
                records = self._resolve_2many_commands(column, vals.get(column, []), fields=['id'])

                # Get records which not exists at the moment and must be created
                values_to_create = [value for value in records if not value.get('id', False)]
                for value_to_create in values_to_create:
                    records.remove(value_to_create)
                    many2many_values.append((0, 0, value_to_create))

                # Get new IDs which are not already set on field
                new_record_ids = [rec['id'] for rec in records if rec['id'] not in partner[column].ids]
                if new_record_ids:
                    many2many_values.extend([(4, record_id) for record_id in new_record_ids])

                if many2many_values:
                    new_values[column] = many2many_values

        old_values = {}
        for field in new_values.keys():
            old_values[field] = partner[field]

        # remove fields that can not be updated (id and parent_id)
        new_values.pop('id', None)
        parent_id = new_values.pop('parent_id', None)
        partner.with_context(send_no_double_opt_in=True).write(new_values.copy())
        if parent_id and parent_id != partner.id:
            try:
                partner.write({'parent_id': parent_id})
                new_values['parent_id'] = parent_id
            except ValidationError:
                pass

        tracking_value_ids = []
        if new_values:
            partner_obj = self.env['res.partner'].with_context(lang='en_US')
            # Field names should always be in english
            ref_tracked_fields = partner_obj.fields_get(list(new_values.keys()))
            partner = partner.with_context(lang='en_US')
            dummy, tracking_value_ids = partner.message_track(ref_tracked_fields, {partner.id: old_values})[partner.id]
        # Message should always be in english
        body = 'Another contact was merged with this contact. '
        if tracking_value_ids:
            body += 'The following fields are updated:'
        else:
            body += 'No fields are updated.'
        partner.message_post(body=body, tracking_value_ids=tracking_value_ids)

        # Send information mail to the contact
        send_merged_contact_email = self.env['ir.config_parameter'].sudo() \
            .get_param('mypatent_partner.send_merged_contact_email')
        if send_merged_contact_email:
            template = self.env.ref('mypatent_partner.mypatent_merge_email_template')
            template.send_mail(partner.id, force_send=True)

        return partner
