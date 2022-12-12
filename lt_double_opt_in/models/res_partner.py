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

    # user_id = fields.Many2one(default=lambda self: self.env.user)
    # competitive_system_used_ids = \
    #     fields.Many2many('competitive.system.used', string='Competitive Systems Used', copy=False,
    #                      ondelete='restrict')
    # units_consumed_id = fields.Many2one('units.consumed', string='Units Consumed per Year', ondelete="restrict")
    # special_clinical_technique_ids = \
    #     fields.Many2many('special.clinical.technique', string='Special Clinical Techniques', copy=False,
    #                      ondelete='restrict')
    # salutation_id = fields.Many2one('res.partner.salutation', string='Salutation', ondelete="restrict")
    # [t118757] Rename "Categorized job position" to "Role"
    # job_position_id = fields.Many2one(string='Role')
    # # Override email field
    # email = fields.Char(copy=False)
    # parent_id = fields.Many2one(domain="[('is_company','=',True)]")
    # lang_char = fields.Char(compute='_compute_lang_char', string='Language Char')
    # sale_order_count_marketing = fields.Integer(compute='_compute_sale_order_count_marketing',
    #                                             store=True, string='Sale Order Count Marketing',
    #                                             help='Sale order count for only this partner, '
    #                                                  'without counting the child partners sales.')

    # Selection type field without the contact option
    # type_address = fields.Selection(selection=[('invoice', 'Invoice Address'), ('delivery', 'Delivery Address'),
    #                                            ('other', 'Other Address'), ("private", "Private Address")],
    #                                 compute='_compute_type_address', inverse='_inverse_type_address')
    # top_filter = fields.Boolean("Is Invoice greater than zero",
    #                             compute='_compute_sale_amount', store=True)
    # sale_amount = fields.Float('Invoice Total',
    #                            compute='_compute_sale_amount', store=True)

    # status = fields.Selection([
    #     ('a_interested', 'Interested'),
    #     ('b_committed', 'Committed'),
    #     ('c_starting', 'Starting'),
    #     ('d_developing', 'Developing'),
    #     ('e_loyal', 'Loyal')], string='Customer Status')

    # @api.depends('invoice_ids')
    # def _compute_sale_amount(self):
    #     if not self.ids:
    #         return True
    #
    #     user_currency_id = self.env.company.currency_id.id
    #     all_partners_and_children = {}
    #     all_partner_ids = []
    #     for partner in self:
    #         # price_total is in the company currency
    #         all_partners_and_children[partner] = self.with_context(
    #             active_test=False).search([('id', 'child_of', partner.id)]).ids
    #         all_partner_ids += all_partners_and_children[partner]
    #
    #     price_totals = self.env['account.invoice.report'].search(
    #         [('partner_id', 'in', all_partner_ids),
    #          ('state', 'not in', ['draft', 'cancel']),
    #          ('move_type', 'in', ('out_invoice', 'out_refund'))])
    #     for partner, child_ids in all_partners_and_children.items():
    #         partner.sale_amount = sum(
    #             price.price_subtotal for price in price_totals if
    #             price.partner_id.id in child_ids)
    #         if partner.sale_amount > 0:
    #             partner.top_filter = True
    #         else:
    #             partner.top_filter = False

    # def search(self, args, offset=0, limit=None, order=None, count=False):
    #     """Override the search"""
    #     flag = 0
    #     for arg in args:
    #         if arg == ['top_filter', '!=', False]:
    #             flag = 1
    #
    #     if flag == 1:
    #         order = 'sale_amount desc'
    #         limit = 10
    #     res = super(ResPartner, self).search(args, offset=offset, limit=limit, order=order, count=count)
    #     return res

    # @api.depends('type')
    # def _compute_type_address(self):
    #     for partner in self:
    #         if partner.type != 'contact':
    #             partner.type_address = partner.type
    #         else:
    #             partner.type_address = False

    # @api.onchange('type_address')
    # def _inverse_type_address(self):
    #     """This method should update the type field to be in sync.
    #     Decorating it with onchange as suggested in
    #     #23891: https://github.com/odoo/odoo/issues/23891 to have the field type
    #     updated on the fly and so, possible view changes"""
    #     for partner in self:
    #         partner.type = partner.type_address

    # @api.depends('lang')
    # def _compute_lang_char(self):
    #     for partner in self:
    #         partner.lang_char = partner.lang

    # @api.depends('sale_order_ids')
    # def _compute_sale_order_count_marketing(self):
    #     for partner in self:
    #         partner.sale_order_count_marketing = len(partner.sale_order_ids)

    # @api.model
    # def _fields_view_get_address(self, arch):
    #     arch = super(ResPartner, self)._fields_view_get_address(arch)
    #     doc = etree.fromstring(arch)
    #     for node in doc.xpath("//field[@name='parent_id']"):
    #         node.attrib['context'] = "{'default_is_company': True, 'show_vat': True, 'default_lang': lang_char," \
    #                                  " 'default_phone': phone, 'default_website': website}"
    #
    #     arch = etree.tostring(doc, encoding='unicode')
    #     return arch

    # @api.onchange('is_company', 'email')
    # def onchange_email(self):
    #     res = {}
    #     if self.email:
    #         partners = self.with_context(active_test=False).search([('id', 'not in', self.ids),
    #                                                                 ('email', '=', self.email),
    #                                                                 ('is_company', '=', not self.is_company)])
    #         if partners:
    #             message = _('The following %s already exist with this e-mail address:') % (_('individuals') if
    #                                                                                        self.is_company else
    #                                                                                        _('companies'))
    #             for partner in partners:
    #                 message += '\n- %s (ID %s)' % (partner.name, str(partner.id))
    #             res['warning'] = {
    #                 'title': _('Warning'),
    #                 'message': message
    #             }
    #     return res

    # def _validate_email(self):
    #     if not self.email:
    #         return
    #     partner = self.with_context(active_test=False).search([('id', 'not in', self.ids),
    #                                                            ('email', '=', self.email),
    #                                                            ('is_company', '=', self.is_company)])
    #     if partner:
    #         raise UserError(_('This contact can not be saved. Another contact with the same E-Mail and type is '
    #                           'already existing. Please change the E-Mail Adress.'))

    @api.model
    def create(self, vals):
        # Merge new partner if it have set the merge flag and already a partner with this email exists
        if 'category_id' in vals:
            email = vals.get('email', False)
            mailing_contact = self.env['mailing.contact'].sudo().search([])
            partner_tag_ids = vals.get('category_id')[0][2]
            partner_tags = self.env['res.partner.category'].browse(partner_tag_ids)
            tags = []
            for tag in partner_tags:
                if (self.env['mailing.tag'].search([('name', '=', tag.name)]).name == tag.name):
                    tag_value = self.env['mailing.tag'].sudo().search([('name', '=', tag.name)]).id
                    tags.append(tag_value)
            company_name = self.browse(vals.get('partent_id')).name
            if email not in mailing_contact.mapped(lambda self: self.email):
                self.env['mailing.contact'].create({
                    'email': vals.get('email', False),
                    'company_name': company_name if vals.get('parent_id') else vals.get('name'),
                    'name': vals.get('name'),
                    'country_id': vals.get('country_id'),
                    'title_id': vals.get('title') if vals.get('title') else False,
                    'category_ids': tags,
                })
        partner = self._merge_partner_with_existing_partner(vals)
        if partner:
            return partner
        new_partner = super(ResPartner, self).create(vals)
        # new_partner._validate_email()
        return new_partner

    # def write(self, vals):
    #     res = super(ResPartner, self).write(vals)
    #     if 'is_company' in vals or 'email' in vals:
    #         for record in self:
    #             record._validate_email()
    #     return res

    def write(self, vals):
        # mailing_contact = self.env['mailing.contact'].sudo().search([('email', '=', self.email)], limit=1)
        # if vals.get('category_id'):
        #     partner_tag_ids = vals.get('category_id')[0][2]
        #     partner_tags = self.env['res.partner.category'].browse(partner_tag_ids)
        #     tags = []
        #     for tag in partner_tags:
        #         tag_value_id = self.env['mailing.tag'].search([('name', '=', tag.name)])
        #         if (tag_value_id.name == tag.name) and (tag_value_id.id not in mailing_contact.tag_ids.ids):
        #             tag_value = tag_value_id.id
        #             print(tags, 'ssssssssssss', tag_value)
        #             tags.append(tag_value)
        #     if self.email == mailing_contact.email:
        #         for tag in tags:
        #             mailing_contact.write({'category_ids': [(4, tag)]})
        mailing_contact = self.env['mailing.contact'].sudo().search([('email', '=', self.email)])
        if self.email == mailing_contact.email:
            if vals:
                tags = []
                print('yyyyyyyyyyyyyyyyyeeeeeeeedddddddddddd')
                if vals.get('category_id'):
                    print('llllllllllll',vals.get('category_id')[0][0],type(vals.get('category_id')[0][0]))
                    # contact_tag_ids = vals.get('category_id')
                    if vals.get('category_id')[0][0] == 6:
                        contact_tag_ids = vals.get('category_id')[0][2]
                        partner_tags = self.env['res.partner.category'].browse(contact_tag_ids)
                    # else:
                    #     contact_tag_ids = vals.get('category_id')[0]
                        print(contact_tag_ids,'contact_tag_ids')

                        for tag in partner_tags:
                            tag_value_id = self.env['mailing.tag'].search([('name', '=', tag.name)])
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
            # elif vals.get('category_id')[0][2]:
            #     contact_tag_ids = vals.get('category_id')[0][2]
            #     tags = []
            #     for tag in contact_tag_ids:
            #         tag_value = self.env['res.partner.category'].search([('id', '=', tag)]).id
            #         if (tag_value not in mailing_contact.tag_ids.ids):
            #             tags.append(tag_value)
                    # else:
                    #     new_tags = self.env['res.partner.category'].create({
                    #         'name': tag.name
                    #     })
                    #     tags.append(new_tags.id)

                    for value in tags:
                        mailing_contact.write({'category_ids': [(4, value)]})
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
