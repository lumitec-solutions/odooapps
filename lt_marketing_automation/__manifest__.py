##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
{
    'name': 'Slides and Surveys in Marketing Automation',
    'summary': 'Send survey ans slide links from marketing automation',
    'author': "lumitec GmbH",
    'website': "https://www.lumitec.solutions",
    'category': 'Website',
    'version': '15.0.1.0.0',
    'license': 'OPL-1',
    'depends': [
        'base',
        'contacts',
        'website_slides',
        'marketing_automation',
        'survey',
    ],
    'data': [
        'data/mail_template_data.xml',
        'data/website_data.xml',
        'views/slide_channel_views.xml',
        'views/marketing_activity_views.xml',
        'views/website_slide_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
