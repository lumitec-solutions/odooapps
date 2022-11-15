##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
{
    'name': 'Website Visitor',
    'summary': 'Scroll tracker and changes based on duration in website visitor',
    'author': "lumitec GmbH",
    'website': "https://www.lumitec.solutions",
    'category': 'Website',
    'version': '15.0.1.0.0',
    'license': 'OPL-1',
    'depends': [
        'base',
        'website_sale',
    ],
    'data': [
        'data/defaults.xml',
        'data/cron.xml',
        'views/website_visitor_views.xml'
    ],
    "assets": {
            "web.assets_frontend": [
                "/lt_website_visitor/static/src/js/scroll_event.js",
            ],
        },
    'installable': True,
    'application': False,
    'auto_install': False,
}
