##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
{
    'name': 'Multi Language Sitemap',
    'summary': 'Sitemap for multi language urls',
    'author': "lumitec GmbH",
    'website': "https://www.lumitec.solutions",
    'category': 'Website',
    'version': '15.0.1.0.0',
    'license': 'OPL-1',
    'images': ['static/description/thumbnail.gif'],
    'depends': [
        'base',
        'http_routing',
        'website',
    ],
    'data': [
        'data/cron.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
