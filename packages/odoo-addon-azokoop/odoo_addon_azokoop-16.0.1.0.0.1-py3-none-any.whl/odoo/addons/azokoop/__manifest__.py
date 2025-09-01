{
    'name': 'Azokoop Custom Addon',
    'version': '16.0.1.0.0',
    'summary': 'Custom Addons for Azokoop',
    'description': """
        Customize checkout page to show pricelist
    """,
    'author': 'Coopdevs Treball SCCL',
    'website': 'https://coopdevs.coop',
    'category': 'Cooperative Management',
    'depends': ['website_sale', 'website_recaptcha_v2', 'auth_signup'],
    'data': [
        'views/templates.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
