##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
from odoo import api, fields, models
from collections import defaultdict


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
    FIELDS_TO_MERGE = ['category_ids', 'double_opt_in', 'country_id']

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
        mailing_contact = self._merge_mailing_contact_with_existing_mailing_contact(vals)
        if mailing_contact:
            return mailing_contact
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
        result = []                     # result (list of dict)
        record_ids = []                 # ids of records to read
        updates = defaultdict(dict)     # {id: vals} of updates on records

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

    def _merge_mailing_contact_with_existing_mailing_contact(self, vals):

        email = vals.get('email', False)

        mailing_contact = False
        if email:
            mailing_contact = self.with_context(active_test=False).search(
                [('email', '=', email)], limit=1, order='id desc')

        if not mailing_contact:
            return False

        new_values = dict()
        for column in vals:
            if column in self.FIELDS_TO_MERGE:
                field = mailing_contact._fields[column]
                if field.type not in (
                'many2many', 'one2many') and field.compute is None:
                    # Only update fields which are not already set
                    if not mailing_contact[column] and vals[column]:
                        new_values[column] = vals[column]

                elif field.type in ('many2many', 'one2many'):
                    many2many_values = []
                    records = self._resolve_2many_commands(column,
                                                           vals.get(column, []),
                                                           fields=['id'])

                    # Get records which not exists at the moment and must be created
                    values_to_create = [value for value in records if
                                        not value.get('id', False)]
                    for value_to_create in values_to_create:
                        records.remove(value_to_create)
                        many2many_values.append((0, 0, value_to_create))

                    # Get new IDs which are not already set on field
                    new_record_ids = [rec['id'] for rec in records if
                                      rec['id'] not in mailing_contact[column].ids]
                    if new_record_ids:
                        many2many_values.extend(
                            [(4, record_id) for record_id in new_record_ids])

                    if many2many_values:
                        new_values[column] = many2many_values

        old_values = {}
        for field in new_values.keys():
            old_values[field] = mailing_contact[field]

        # remove id that can not be updated
        new_values.pop('id', None)
        mailing_contact.write(new_values.copy())

        tracking_value_ids = []

        if new_values:
            mailing_contact_obj = self.env['mailing.contact'].with_context(lang='en_US')
            # Field names should always be in english
            ref_tracked_fields = mailing_contact_obj.fields_get(list(new_values.keys()))
            mailing_contact = mailing_contact.with_context(lang='en_US')
            dummy, tracking_value_ids = mailing_contact._mail_track(ref_tracked_fields,
                                                         old_values)
        # Message should always be in english
        body = 'Another mailing contact was merged with this one. '
        if tracking_value_ids:
            body += 'The following fields are updated:'
        else:
            body += 'No fields are updated.'
        mailing_contact.message_post(body=body, tracking_value_ids=tracking_value_ids)

        return mailing_contact

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
