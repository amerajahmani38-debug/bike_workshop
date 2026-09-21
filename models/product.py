from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_spare_part = fields.Boolean(
        string='Is Spare Part', 
        default=False,
        tracking=True,
        help="Check this box if this product can be used as a spare part in bike repairs."
    )