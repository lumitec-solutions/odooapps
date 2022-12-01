##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
from odoo import fields, models, api, _
from odoo.tools.misc import format_date


class UtmCampaign(models.Model):
    _inherit = 'utm.campaign'

    project_count = fields.Integer('Project Count',
                                   compute='_compute_project_count')
    meeting_count = fields.Integer('Meeting Count',
                                   compute='_compute_meeting_count')
    event_count = fields.Integer('Event Count',
                                 compute='_compute_event_count')
    deadline_date = fields.Datetime('Deadline',
                                    help='Deadline for the Campaign when its over')
    deadline_date_formatted = fields.Char(
        compute='_compute_deadline_date_formatted', store=True)
    budget = fields.Float('Budget',
                          help='How much we want to spend on to fullfill the purpose of the event')
    link_ids = fields.One2many('link.tracker', 'campaign_id', string='Links')
    link_count = fields.Integer('Number of Links',
                                compute='_compute_link_count', store=True)
   

    def _compute_project_count(self):
        for rec in self:
            count = self.env['project.project'].search_count(
                [('campaign_id', '=', rec.id)])
            rec.project_count = count

    def _compute_meeting_count(self):
        for rec in self:
            count = self.env['calendar.event'].search_count(
                [('campaign_id', '=', rec.id)])
            rec.meeting_count = count

    def _compute_event_count(self):
        for rec in self:
            count = self.env['event.event'].search_count(
                [('campaign_id', '=', rec.id)])
            rec.event_count = count

    @api.depends('link_ids')
    def _compute_link_count(self):
        for campaign in self:
            campaign.link_count = len(campaign.link_ids)

    @api.depends('deadline_date')
    def _compute_deadline_date_formatted(self):
        for rec in self:
            rec.deadline_date_formatted = format_date(self.env,
                                                      rec.deadline_date) if rec.deadline_date else None

    def action_view_projects(self):
        """View the projects related to this campaign"""
        return {
            'name': _('Projects'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'view_mode': 'kanban,form',
            'target': 'current',
            'domain': [('campaign_id', '=', self.id)],
            'context': {'default_campaign_id': self.id}
        }

    def action_view_meetings(self):
        """View the meetings related to this campaign"""
        return {
            'name': _('Meetings'),
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'view_mode': 'calendar,tree,form',
            'target': 'current',
            'domain': [('campaign_id', '=', self.id)],
            'context': {'default_campaign_id': self.id}
        }

    def action_view_events(self):
        """View the events related to this campaign"""
        return {
            'name': _('Events'),
            'type': 'ir.actions.act_window',
            'res_model': 'event.event',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('campaign_id', '=', self.id)],
            'context': {'default_campaign_id': self.id}
        }

    def create_link_tracker(self):
        """Create link tracker using this campaign when clicking the button"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'link.tracker',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_campaign_id': self.id}
        }
