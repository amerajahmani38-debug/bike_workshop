from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date

class BikeRepair(models.Model):
    _name = 'bike.repair'
    _description = 'Bike Repair Job'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Repair Reference', required=True, copy=False, readonly=True, default=lambda self: 'New')
    
    # Customer and Bike Source Info
    customer_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    bike_source = fields.Selection([
        ('workshop', 'Workshop Bike'),
        ('external', 'External Bike')
    ], string='Bike Source', required=True, default='workshop', tracking=True)
    
    # Workshop Bike vs External Bike Fields
    workshop_bike_id = fields.Many2one('bike.workshop.bike', string='Workshop Bike', tracking=True)
    external_bike_name = fields.Char(string='Bike Reference / Description')
    external_bike_brand = fields.Char(string='Brand')
    external_bike_type = fields.Selection([
        ('mountain', 'Mountain Bike'),
        ('road', 'Road Bike'),
        ('hybrid', 'Hybrid Bike'),
        ('electric', 'Electric Bike')
    ], string='Bike Type')

    # Shared / Service Details
    reported_issue = fields.Text(string='Reported Issue', required=True, tracking=True)
    mechanic_id = fields.Many2one('res.users', string='Assigned Mechanic', required=True, tracking=True)
    service_date = fields.Date(string='Service Date', default=fields.Date.today, tracking=True)
    service_notes = fields.Text(string='Service Notes', tracking=True)

    # Spare Parts Lines & Costs
    repair_line_ids = fields.One2many('bike.repair.line', 'repair_id', string='Spare Parts Lines')
    total_parts_cost = fields.Monetary(string='Total Spare Parts Cost', compute='_compute_total_parts_cost', store=True, currency_field='company_currency_id')
    company_currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    # Lifecycle State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('bike.repair.sequence') or 'New'
        return super().create(vals_list)

    @api.depends('repair_line_ids.subtotal')
    def _compute_total_parts_cost(self):
        for repair in self:
            repair.total_parts_cost = sum(line.subtotal for line in repair.repair_line_ids)

    # Lifecycle Action Methods & Validations
    def action_start(self):
        for repair in self:
            if not repair.customer_id or not repair.reported_issue or not repair.mechanic_id:
                raise UserError("Cannot start repair without a Customer, Reported Issue, and Assigned Mechanic.")
            if repair.bike_source == 'workshop' and not repair.workshop_bike_id:
                raise UserError("Please select a workshop bike.")
            if repair.bike_source == 'external' and (not repair.external_bike_brand or not repair.external_bike_type):
                raise UserError("Please provide brand and type for the external bike.")
            repair.state = 'in_progress'

    def action_complete(self):
        for repair in self:
            if not repair.service_notes or not repair.service_date:
                raise UserError("Cannot complete the repair without Service Notes and Service Date.")
            repair.state = 'completed'

    def action_cancel(self):
        for repair in self:
            if repair.state == 'completed':
                raise UserError("Completed repairs cannot be cancelled.")
            repair.state = 'cancelled'

    def action_draft(self):
        for repair in self:
            if repair.state in ['completed', 'cancelled']:
                raise UserError("Processed repairs cannot be moved back to draft.")
            repair.state = 'draft'


class BikeRepairLine(models.Model):
    _name = 'bike.repair.line'
    _description = 'Bike Repair Spare Part Line'

    repair_id = fields.Many2one('bike.repair', string='Repair Reference', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Spare Part Product', required=True)
    name = fields.Char(string='Description', related='product_id.name', readonly=True)
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    
    unit_price = fields.Monetary(string='Unit Price', required=True, currency_field='currency_id')
    subtotal = fields.Monetary(string='Subtotal', compute='_compute_subtotal', store=True, currency_field='currency_id')
    
    currency_id = fields.Many2one('res.currency', related='repair_id.company_currency_id', readonly=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.unit_price = self.product_id.lst_price

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            if line.quantity < 0 or line.unit_price < 0:
                raise ValidationError("Quantity and unit price cannot be negative.")
            line.subtotal = line.quantity * line.unit_price