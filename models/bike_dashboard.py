from odoo import models, fields, api

class BikeDashboard(models.TransientModel):
    _name = 'bike.dashboard'
    _description = 'Workshop Operations Dashboard'

    active_rentals_count = fields.Integer(string="Active Rentals Today", compute='_compute_dashboard_counts')
    returns_due_count = fields.Integer(string="Returns Due Today", compute='_compute_dashboard_counts')
    repairs_in_progress_count = fields.Integer(string="Repairs In Progress", compute='_compute_dashboard_counts')

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        # السماح بعمليات الإنشاء والقراءة للجميع لتجنب أي Access Error في لوحة التحكم
        if operation in ('create', 'read'):
            return True
        return super(BikeDashboard, self).check_access_rights(operation, raise_exception=raise_exception)

    def _compute_dashboard_counts(self):
        for record in self:
            record.active_rentals_count = self.env['bike.rental'].search_count([('state', '=', 'active')])
            record.returns_due_count = self.env['bike.rental'].search_count([('return_date', '=', fields.Date.today())])
            record.repairs_in_progress_count = self.env['bike.repair'].search_count([('state', '=', 'in_progress')])

    def action_open_active_rentals(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Active Rentals',
            'res_model': 'bike.rental',
            'view_mode': 'list,form',
            'domain': [('state', '=', 'active')],
        }

    def action_open_returns_due(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Returns Due Today',
            'res_model': 'bike.rental',
            'view_mode': 'list,form',
            'domain': [('return_date', '=', fields.Date.today())],
        }

    def action_open_repairs_in_progress(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Repairs In Progress',
            'res_model': 'bike.repair',
            'view_mode': 'list,form',
            'domain': [('state', '=', 'in_progress')],
        }
