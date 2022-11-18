##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
from odoo.tests import common
import logging
_logger = logging.getLogger(__name__)


class TestWebsiteVisitor(common.TransactionCase):
    def test_archive_bots(self):
        _logger.info(
            "----------TEST _cron_archive_bots--------------------------")
        self.env['ir.config_parameter'].sudo().set_param(
            'website.visitors.live.duration', 7)

        visitor = self.env['website.visitor'].create({
            'lang_id': self.env.ref('base.lang_en').id,
            'country_id': self.env.ref('base.be').id,
            'website_id': 1,
        })
        self.assertTrue(visitor.active)
        # archive bot visitor
        visitor.duration = 6
        self.env['website.visitor']._cron_archive_bots()
        self.assertEqual(visitor.active, False,
                         "Visitor should be archived after inactivity")
        _logger.info(
            "----------TEST PASS _cron_archive_bots--------------------------")
