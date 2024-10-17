{
    'name': "Slack Data Import",
    'author': 'Rizwaan',
    'version': "17.0.0.0",
    'sequence': "0",
    'depends': ['base','web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/base_views.xml',
        'views/import_wizard.xml',

    ],

    'demo': [],
    'summary': "Slack Data Import",
    'description': "Slack Data Import",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': False
}