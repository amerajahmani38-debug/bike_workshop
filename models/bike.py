from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BikeWorkshopBike(models.Model):
    _name = 'bike.workshop.bike'
    _inherit = ['bike.service.mixin']
    _description = 'Workshop Bike'

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

    # الحقل الجديد لحساب عدد الإيجارات
    rental_count = fields.Integer(string='Rental Count', compute='_compute_rental_count')

    @api.constrains('name')
    def _check_unique_name(self):
        for record in self:
            existing_bike = self.search([('name', '=', record.name), ('id', '!=', record.id)])
            if existing_bike:
               raise ValidationError("Sorry, this bike name already exists! You cannot register two bikes with the same name.")

    # دالة حساب عدد الإيجارات المرتبطة بالدراجة
    def _compute_rental_count(self):
        for bike in self:
            bike.rental_count = self.env['bike.rental'].search_count([('bike_id', '=', bike.id)])

    # دالة فتح سجل الإيجارات الخاصة بالدراجة عند النقر على الـ Smart Button
    def action_view_rentals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rentals',
            'res_model': 'bike.rental',
            'view_mode': 'list,form',
            'domain': [('bike_id', '=', self.id)],
            'context': {'default_bike_id': self.id}
        }