{
    'name': "estate",
    'version': '1.0.0',
    'depends': ['base'],
    'author': "Teo Vinazza",
    'category': 'Real Estate',
    'summary': "Module for real estate listings",
    'description': """
    Description text
    """,

    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_menus.xml',
        'views/res_users_views.xml',
    ],

    'demo': [],
    'installable': True,     #True by default
    'application': True,     #True - visible under the "Apps" filter
    'license': 'LGPL-3',
} # type: ignore