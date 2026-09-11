{
    'name': 'Bike Workshop',
    'version': '19.0.1.0.2',
    'category': 'Services',
    'summary': 'Manage bikes and daily rental operations for Ramis workshop',
    'depends': ['base', 'mail', 'product'],    
    'data': [
        'security/bike_workshop_security.xml',
        'security/ir.model.access.csv',
        'data/rental_sequence.xml',
        'data/repair_sequence.xml',
        'views/bike_views.xml',
        'views/rental_views.xml',
        'views/repair_views.xml',
        'views/res_partner_views.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}