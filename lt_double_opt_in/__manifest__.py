##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
{
    'name': 'Double Opt-In',
    'summary': 'Double Opt-In Logic in leads',
    'author': "lumitec GmbH",
    'website': "https://www.lumitec.solutions",
    'category': 'Website',
    'version': '15.0.1.0.0',
    'license': 'OPL-1',
    'depends': [
        'base',
        'mail',
        'crm',
        'website',
    ],
    'data': [
        'data/mypatent_crm_lead_token_cron.xml',
        'data/mypatent_crm_lead_token_mail_data.xml',
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'views/mypatent_crm_lead_token_templates.xml',
        'views/crm_lead_tag_views.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
