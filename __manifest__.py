# -*- coding: utf-8 -*-
{
    'name': "sd_visualize_petronad",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "Arash Homayounfar",
    'website': "https://gilaneh.com/",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Service Desk/Service Desk',
    'application': True,
    'installable': True,
    'version': '1.1.3',


    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'sd_visualize', ],

    # always loaded
    'data': [
        ],
    'assets': {
        'web._assets_common_scripts': [
        ],
        'web._assets_common_styles': [
        ],
        'web.assets_backend': [
        ],
        'web.assets_frontend': [
],
        'web.report_assets_common': [
        ],
        },
    'license': 'LGPL-3',
}
