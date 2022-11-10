##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
import logging
import werkzeug
from odoo import models, fields, api, _
from odoo.exceptions import AccessError
from odoo.fields import Datetime

_logger = logging.getLogger(__name__)


class MarketingSlideLink(models.Model):
    _inherit = 'marketing.activity'

    activity_type = fields.Selection(
        selection_add=[('course', 'Course'), ('survey', 'Survey')],
        ondelete={'course': 'set default', 'survey': 'set default'})
    channel_id = fields.Many2one('slide.channel', string="Course")
    course_template_id = fields.Many2one(
        'mail.template', 'Course template', index=True,
        domain="[('model', '=', 'slide.channel.partner')]")
    channel_url = fields.Char(related="channel_id.website_url", readonly=True,
                              store=True)
    survey_id = fields.Many2one('survey.survey', string="Survey Type")
    survey_url = fields.Char(string='Survey', compute='_compute_survey_url',
                             store=True, readonly=False)
    survey_template_id = fields.Many2one(
        'mail.template', 'Survey template', index=True,
        domain="[('model', '=', 'survey.user_input')]")

    @api.depends('survey_id')
    def _compute_survey_url(self):
        for rec in self:
            rec.survey_url = werkzeug.urls.url_join(
                rec.survey_id.get_base_url(),
                rec.survey_id.get_start_url()) if rec.survey_id else False

    @api.depends('activity_type')
    def _compute_mass_mailing_id_mailing_type(self):
        res = super(MarketingSlideLink,
                    self)._compute_mass_mailing_id_mailing_type()
        if self.activity_type == 'course':
            self.mass_mailing_id_mailing_type = 'mail'
        if self.activity_type == 'survey':
            self.mass_mailing_id_mailing_type = 'mail'
        return res

    def _execute_course(self, traces):
        if not self.env.is_superuser() and not self.user_has_groups(
                'marketing_automation.group_marketing_automation_user'):
            raise AccessError(
                _('To use this feature you should be an administrator or belong '
                  'to the marketing automation group.'))
        try:
            self.course_invite(traces)
        except Exception as e:
            _logger.warning(
                _('Marketing Automation: activity <%s> encountered mailing issue %s'),
                self.id, str(e), exc_info=True)
            traces.write({
                'state': 'error',
                'schedule_date': Datetime.now(),
                'state_msg': _('Exception in mass mailing: %s') % str(e),
            })
        else:
            failed_stats = self.env['mailing.trace'].sudo().search([
                ('marketing_trace_id', 'in', traces.ids),
                ('trace_status', 'in', ['error', 'bounce', 'cancel'])
            ])
            error_doc_ids = [stat.res_id for stat in failed_stats if
                             stat.trace_status in ('error', 'bounce')]
            cancel_doc_ids = [stat.res_id for stat in failed_stats if
                              stat.trace_status == 'cancel']

            processed_traces = traces
            canceled_traces = traces.filtered(
                lambda trace: trace.res_id in cancel_doc_ids)
            error_traces = traces.filtered(
                lambda trace: trace.res_id in error_doc_ids)

            if canceled_traces:
                canceled_traces.write({
                    'state': 'canceled',
                    'schedule_date': Datetime.now(),
                    'state_msg': _('Email canceled')
                })
                processed_traces = processed_traces - canceled_traces
            if error_traces:
                error_traces.write({
                    'state': 'error',
                    'schedule_date': Datetime.now(),
                    'state_msg': _('Email failed')
                })
                processed_traces = processed_traces - error_traces
            if processed_traces:
                processed_traces.write({
                    'state': 'processed',
                    'schedule_date': Datetime.now(),
                })
        return True

    def course_invite(self, traces):
        res_ids = [r for r in set(traces.mapped('res_id'))]
        for trace in traces:
            valid_partners = self.env['res.partner']
            model = trace.participant_id.model_id.model
            if model == 'res.partner':
                valid_partners = self.env['res.partner'].search([]).filtered(
                    lambda x: x.id in res_ids)
            elif model == 'sale.order':
                sale_orders = self.env['sale.order'].search([]).filtered(
                    lambda x: x.id in res_ids)
                for order in sale_orders:
                    if order.partner_id:
                        valid_partners |= order.partner_id
            elif model == 'crm.lead':
                leads = self.env['crm.lead'].search([]).filtered(
                    lambda x: x.id in res_ids)
                for lead in leads:
                    if lead.partner_id:
                        valid_partners |= lead.partner_id
                    elif lead.contact_id:
                        valid_partners |= lead.contact_id
                    else:
                        create_partner = self.env['res.partner'].create({
                            'name': lead.contact_name,
                            'email': lead.email_from,
                            'lead_id': lead.id,
                        })
                        valid_partners |= create_partner

            course_invite = self.env['slide.channel.invite'].create({
                'channel_id': self.channel_id.id,
                'partner_ids': valid_partners.ids,
                'template_id': self.course_template_id.id,
                'attachment_ids': [
                    (6, 0, self.course_template_id.attachment_ids.ids)],
            })
            course_invite.action_invite()
    def _execute_survey(self, traces):
        if not self.env.is_superuser() and not self.user_has_groups(
                'marketing_automation.group_marketing_automation_user'):
            raise AccessError(
                _('To use this feature you should be an administrator or belong '
                  'to the marketing automation group.'))
        try:
            self.survey_invite(traces)
        except Exception as e:
            _logger.warning(
                _('Marketing Automation: activity <%s> encountered mailing issue %s'),
                self.id, str(e), exc_info=True)
            traces.write({
                'state': 'error',
                'schedule_date': Datetime.now(),
                'state_msg': _('Exception in mass mailing: %s') % str(e),
            })
        else:
            failed_stats = self.env['mailing.trace'].sudo().search([
                ('marketing_trace_id', 'in', traces.ids),
                ('trace_status', 'in', ['error', 'bounce', 'cancel'])
            ])
            error_doc_ids = [stat.res_id for stat in failed_stats if
                             stat.trace_status in ('error', 'bounce')]
            cancel_doc_ids = [stat.res_id for stat in failed_stats if
                              stat.trace_status == 'cancel']

            processed_traces = traces
            canceled_traces = traces.filtered(
                lambda trace: trace.res_id in cancel_doc_ids)
            error_traces = traces.filtered(
                lambda trace: trace.res_id in error_doc_ids)

            if canceled_traces:
                canceled_traces.write({
                    'state': 'canceled',
                    'schedule_date': Datetime.now(),
                    'state_msg': _('Email canceled')
                })
                processed_traces = processed_traces - canceled_traces
            if error_traces:
                error_traces.write({
                    'state': 'error',
                    'schedule_date': Datetime.now(),
                    'state_msg': _('Email failed')
                })
                processed_traces = processed_traces - error_traces
            if processed_traces:
                processed_traces.write({
                    'state': 'processed',
                    'schedule_date': Datetime.now(),
                })
        return True

    def survey_invite(self, traces):
        res_ids = [r for r in set(traces.mapped('res_id'))]
        for trace in traces:
            valid_partners = self.env['res.partner']
            model = trace.participant_id.model_id.model
            if model == 'res.partner':
                valid_partners = self.env['res.partner'].search([]).filtered(
                    lambda x: x.id in res_ids)
            elif model == 'sale.order':
                sale_orders = self.env['sale.order'].search([]).filtered(
                    lambda x: x.id in res_ids)
                for order in sale_orders:
                    if order.partner_id:
                        valid_partners |= order.partner_id
            elif model == 'crm.lead':
                leads = self.env['crm.lead'].search([]).filtered(
                    lambda x: x.id in res_ids)
                for lead in leads:
                    if lead.partner_id:
                        valid_partners |= lead.partner_id
                    elif lead.contact_id:
                        valid_partners |= lead.contact_id
                    else:
                        create_partner = self.env['res.partner'].create({
                            'name': lead.contact_name,
                            'email': lead.email_from,
                            'lead_id': lead.id,
                        })
                        valid_partners |= create_partner
            survey_invite = self.env['survey.invite'].create({
                'survey_id': self.survey_id.id,
                'survey_start_url': self.survey_url,
                'partner_ids': valid_partners.ids,
                'template_id': self.survey_template_id.id,
                'attachment_ids': [(6, 0, self.survey_template_id.attachment_ids.ids)]
            })
            answers = survey_invite._prepare_answers(valid_partners, [])
            for answer in answers:
                survey_invite._send_mail(answer)
