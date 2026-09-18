from odoo import models, fields, api

class BikeRentalReport(models.Model):
    _name = 'bike.rental.report'
    _description = 'Bike Rental Analysis'
    _auto = False  # نموذج تعريفي يعتمد على SQL View لتجميع البيانات بكفاءة عالية

    name = fields.Char(string='Reference', readonly=True)
    customer_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    bike_id = fields.Many2one('bike.workshop.bike', string='Bike', readonly=True)
    bike_type = fields.Selection([
        ('road', 'Road'),
        ('mountain', 'Mountain'),
        ('city', 'City'),
        ('electric', 'Electric')
    ], string='Bike Type', readonly=True)
    
    start_date = fields.Date(string='Start Date', readonly=True)
    expected_return_date = fields.Date(string='Expected Return Date', readonly=True)
    actual_return_date = fields.Date(string='Actual Return Date', readonly=True)
    rental_duration = fields.Float(string='Average Rental Duration', group_operator="avg", readonly=True)
    total_amount = fields.Float(string='Total Rental Amount', group_operator="sum", readonly=True)
    rental_count = fields.Integer(string='Rental Count', group_operator="sum", readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled')
    ], string='Status', readonly=True)
    return_performance = fields.Selection([
        ('on_time', 'On Time'),
        ('late', 'Late'),
        ('pending', 'Pending')
    ], string='Return Performance', readonly=True)
    
    rental_duration = fields.Float(string='Rental Duration', readonly=True)
    total_amount = fields.Float(string='Total Amount', readonly=True)
    rental_count = fields.Integer(string='Rental Count', readonly=True)

    def init(self):
        # إلغاء إنشاء الـ View القديم وإنشاؤه بالشروط الصحيحة والحساب البرمجي للأداء
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW bike_rental_report AS (
                SELECT
                    r.id AS id,
                    r.reference AS name,
                    r.customer_id AS customer_id,
                    r.bike_id AS bike_id,
                    b.bike_type AS bike_type,
                    r.start_date AS start_date,
                    r.expected_return_date AS expected_return_date,
                    r.actual_return_date AS actual_return_date,
                    r.state AS state,
                    CASE
                        WHEN r.state = 'returned' AND r.actual_return_date <= r.expected_return_date THEN 'on_time'
                        WHEN r.state = 'returned' AND r.actual_return_date > r.expected_return_date THEN 'late'
                        ELSE 'pending'
                    END AS return_performance,
                    r.rental_duration AS rental_duration,
                    r.total_amount AS total_amount,
                    1 AS rental_count
                FROM bike_rental r
                LEFT JOIN bike_workshop_bike b ON r.bike_id = b.id
                WHERE r.state != 'draft'
            )
        """)