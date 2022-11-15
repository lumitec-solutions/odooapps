##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
from odoo import fields, models, api


class WebsiteVisitor(models.Model):
    _inherit = 'website.visitor'

    duration = fields.Float('Duration', compute='compute_duration', store=True)
    set_duration = fields.Boolean('Set Duration')

    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Override the search"""
        for arg in args:
            if arg == ['set_duration', '=', True]:
                bot_duration = int(self.env['ir.config_parameter'].sudo().get_param('website.visitors.duration',0))
                if bot_duration:
                    arg[0] = 'duration'
                    arg[1] = '>'
                    arg[2] = bot_duration
        res = super(WebsiteVisitor, self).search(args, offset=offset, limit=limit, order=order, count=count)
        return res

    @api.model
    def fields_get(self, fields=None, attributes=None):
        hide = ['set_duration']
        res = super(WebsiteVisitor, self).fields_get(fields,
                                                        attributes=attributes)
        for field in res:
            if field in hide:
                res[field]['searchable'] = False
        return res

    @api.depends('last_connection_datetime')
    def compute_duration(self):
        for rec in self:
            rec.duration = 0.0
            if rec.active and rec.last_connection_datetime:
                if rec.last_connection_datetime >= rec.create_date:
                    difference = rec.last_connection_datetime - rec.create_date
                else:
                    difference = rec.create_date - rec.last_connection_datetime
                rec.duration = difference.seconds
                rec.set_duration = True

    def _cron_archive_bots(self):
        bot_duration = int(self.env['ir.config_parameter'].sudo().get_param('website.visitors.duration'))
        if bot_duration:
            visitors_to_archive = self.env['website.visitor'].sudo().search([('duration', '<', bot_duration)])
            visitors_to_archive.write({'active': False})
