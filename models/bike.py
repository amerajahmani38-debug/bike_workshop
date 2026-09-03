from odoo import models, fields

class BikeWorkshopBike(models.Model):
    _name = 'bike.workshop.bike'
    _description = 'Bike'

    name = fields.Char(string='Bike Name / Code', required=True)
    brand = fields.Char(string='Brand')
    bike_type = fields.Selection([
        ('road', 'Road'),
        ('mountain', 'Mountain'),
        ('city', 'City'),
        ('electric', 'Electric')
    ], string='Bike Type', default='city')
    purchase_date = fields.Date(string='Purchase Date')
    last_maintenance_date = fields.Date(string='Last Maintenance Date')
    daily_rental_price = fields.Float(string='Daily Rental Price', required=True)
    wheel_size = fields.Float(string='Wheel Size (inches)')
    availability_date = fields.Date(string="Availability Date", copy=False)
    active = fields.Boolean(string='Active', default=True)
    state = fields.Selection([
        ('new', 'New'),
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Maintenance'),
        ('cancelled', 'Cancelled')
    ], string='Status', required=True, copy=False, default='new')
    
    bike_code = fields.Char(string='Bike Code', copy=False,  default='New')

    _sql_constraints = [
        ('check_daily_rental_price_positive', 'CHECK(daily_rental_price >= 0)', 'The daily rental price must be strictly positive.'),
        ('check_selling_price_positive', 'CHECK(selling_price >= 0)', 'The selling price must be positive.'),
        ('unique_name', 'UNIQUE(name)', 'The bike name must be unique!')
    ]

    def action_make_available(self):
        for record in self:
            record.state = 'available'

    def action_make_rented(self):
        for record in self:
            record.state = 'rented'