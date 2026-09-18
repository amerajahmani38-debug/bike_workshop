from odoo import models, fields

class BikeServiceMixin(models.AbstractModel):
    _name = 'bike.service.mixin'
    _description = 'Bike Service Mixin'

    mechanic_id = fields.Many2one('res.users', string='Assigned Mechanic')
    last_service_date = fields.Date(string='Last Service Date')
    service_notes = fields.Text(string='Service Notes')