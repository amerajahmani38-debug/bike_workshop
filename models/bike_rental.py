from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import date

class BikeRental(models.Model):
    _name = 'bike.rental'
    _description = 'Bike Rental Management'
    _inherit = ['mail.thread']  # لدعم التتبع وتجنب تحذيرات السيرفر
    _rec_name = 'reference'

     company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    reference = fields.Char(string='Rental Reference', required=True, copy=False, readonly=True, default=lambda self: 'New')
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    bike_id = fields.Many2one('bike.workshop.bike', string='Rented Bike', required=True)
    
    start_date = fields.Date(string='Rental Start Date', required=True, default=fields.Date.today)
    expected_return_date = fields.Date(string='Expected Return Date', required=True)
    actual_return_date = fields.Date(string='Actual Return Date', readonly=True)
    
    daily_rental_price = fields.Float(string='Daily Rental Price', required=True)
    rental_duration = fields.Integer(string='Rental Duration (Days)', compute='_compute_rental_duration', store=True, readonly=False)
    total_amount = fields.Float(string='Total Rental Amount', compute='_compute_total_amount', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True, required=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'New') == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code('bike.rental') or 'New'
        return super().create(vals_list)

    @api.depends('start_date', 'expected_return_date')
    def _compute_rental_duration(self):
        for record in self:
            if record.start_date and record.expected_return_date:
                delta = record.expected_return_date - record.start_date
                duration = delta.days
                record.rental_duration = duration if duration > 0 else 0
            else:
                record.rental_duration = 0

    @api.depends('rental_duration', 'daily_rental_price')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.rental_duration * record.daily_rental_price

    @api.constrains('start_date', 'expected_return_date')
    def _check_rental_dates(self):
        for record in self:
            if record.start_date and record.expected_return_date:
                if record.expected_return_date <= record.start_date:
                    raise ValidationError("Expected return date must be strictly after the rental start date.")
                delta = record.expected_return_date - record.start_date
                if delta.days <= 0:
                    raise ValidationError("Rental duration must be greater than zero.")

    @api.constrains('daily_rental_price')
    def _check_daily_rental_price(self):
        for record in self:
            if record.daily_rental_price < 0:
                raise ValidationError("Daily rental price must not be negative.")

    @api.onchange('start_date', 'expected_return_date')
    def _onchange_dates(self):
        if self.start_date and self.expected_return_date and self.expected_return_date <= self.start_date:
            return {
                'warning': {
                    'title': 'Invalid Dates',
                    'message': 'The expected return date must be strictly after the rental start date.'
                }
            }

    @api.onchange('bike_id')
    def _onchange_bike_id(self):
        if self.bike_id:
            self.daily_rental_price = self.bike_id.daily_rental_price

    @api.constrains('bike_id', 'start_date', 'expected_return_date', 'state')
    def _check_rental_conflicts(self):
        for record in self:
            if record.state == 'confirmed':
                # التأكد من استخدام الـ id الرقمي حصرياً لتجنب مشاكل NewId
                bike_id = record.bike_id.id
                if not bike_id:
                    continue

                # 1. منع التأكيد إذا كانت الدراجة تحت الصيانة
                ongoing_repair = self.env['bike.repair'].search([
                    ('bike_source', '=', 'workshop'),
                    ('workshop_bike_id', '=', bike_id),
                    ('state', '=', 'in_progress')
                ], limit=1)
                
                if ongoing_repair:
                    raise ValidationError(f"Cannot confirm rental! The bike '{record.bike_id.name}' is currently under repair.")

                # 2. منع تعارض الحجوزات المتداخلة
                domain = [
                    ('bike_id', '=', bike_id),
                    ('state', '=', 'confirmed'),
                    ('id', '!=', record.id),
                    ('start_date', '<=', record.expected_return_date),
                    ('expected_return_date', '>=', record.start_date),
                ]
                overlapping = self.search_count(domain)
                if overlapping > 0:
                    raise ValidationError("Conflict Error: This bike is already booked and confirmed during this period.")

    def action_confirm(self):
        for record in self:
            if record.state != 'draft':
                raise UserError("Only a Draft Rental can be confirmed.")
            record._check_rental_conflicts()
            record.state = 'confirmed'

    def action_return(self):
        for record in self:
            if record.state != 'confirmed':
                raise UserError("Only A Confirmed Rental can be returned.")
            record.write({
                'state': 'returned',
                'actual_return_date': fields.Date.today()
            })

    def action_cancel(self):
        for record in self:
            if record.state == 'returned':
                raise UserError("Returned rentals cannot be cancelled.")
            record.state = 'cancelled'

    def action_print_rental_agreement(self):
     return self.env.ref('bike_workshop_task.action_report_bike_rental').report_action(self)
