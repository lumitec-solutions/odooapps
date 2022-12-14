##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
{
    'name': 'Double Opt-In',
    'summary': 'Double Opt-In Logic in Mailing Contacts',
    'author': "lumitec GmbH",
    'website': "https://www.lumitec.solutions",
    'category': 'Website',
    'version': '15.0.1.0.0',
    'license': 'OPL-1',
    'depends': [
        'base',
        'mail',
        'mass_mailing',
        'crm',
        'website',
    ],
    'data': [
        'data/cron.xml',
        'data/mailing_contact_token_mail_data.xml',
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'views/res_config_settings_views.xml',
        'views/mailing_contact_token_templates.xml',
        'views/mailing_tag_views.xml',
        'views/mailing_contact_views.xml',
        # 'views/res_partner_category.xml',
        # 'views/crm_lead_views.xml',
        # 'views/res_partner_salutation_views.xml',
    ],
    "assets": {
        "web.assets_backend": [
            # "lt_double_opt_in/static/src/js/update_list.js",
            # "mypatent_cb_profile_score/static/src/js/progress_bar_color.js",
            # "mypatent_cb_profile_score/static/src/js/profile_update.js",
        ],
        "web.assets_qweb": [
            # "lt_double_opt_in/static/src/xml/update_list.xml",
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
