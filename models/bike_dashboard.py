
from odoo import models, fields, api


class BikeDashboard(models.TransientModel):
    _name = 'bike.dashboard'
    _description = 'Workshop Operations Dashboard'

    active_rentals_count = fields.Integer(compute='_compute_counts', string='Active Rentals Today')
    returns_due_count = fields.Integer(compute='_compute_counts', string='Returns Due Today')
    repairs_in_progress_count = fields.Integer(compute='_compute_counts', string='Repairs In Progress')

    def _compute_counts(self):
        today = fields.Date.today()
        for rec in self:
            rec.active_rentals_count = self.env['bike.rental'].search_count([
                ('state', '=', 'confirmed'),
                ('start_date', '<=', today),
                ('expected_return_date', '>=', today),
            ])
            rec.returns_due_count = self.env['bike.rental'].search_count([
                ('state', '=', 'confirmed'),
                ('expected_return_date', '=', today),
            ])
            rec.repairs_in_progress_count = self.env['bike.repair'].search_count([
                ('state', '=', 'in_progress'),
            ])

    def action_open_active_rentals(self):
        today = fields.Date.today()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Active Rentals Today',
            'res_model': 'bike.rental',
            'view_mode': 'list,form',
            'domain': [
                ('state', '=', 'confirmed'),
                ('start_date', '<=', today),
                ('expected_return_date', '>=', today),
            ],
        }

    def action_open_returns_due(self):
        today = fields.Date.today()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Returns Due Today',
            'res_model': 'bike.rental',
            'view_mode': 'list,form',
            'domain': [
                ('state', '=', 'confirmed'),
                ('expected_return_date', '=', today),
            ],
        }

    def action_open_repairs_in_progress(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Repairs In Progress',
            'res_model': 'bike.repair',
            'view_mode': 'list,form',
            'domain': [('state', '=', 'in_progress')],
        }
