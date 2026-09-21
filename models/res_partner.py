from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    preferred_bike_type = fields.Selection([
        ('city', 'City'),
        ('mountain', 'Mountain'),
        ('electric', 'Electric'),
        ('road', 'Road')
    ], string='Preferred Bike Type', default='city')