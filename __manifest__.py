{
    'name': 'Bike Workshop',
    'version': '19.0.1.0.0',
    'category': 'Services',
    'summary': 'Manage bikes and daily rental operations for Ramis workshop',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/bike_views.xml',  
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
