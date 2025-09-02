from odoo import models, fields


class EditorialStockRoute(models.Model):
    """ Extend product stock route model for editorial management """

    _description = "Editorial Stock Route"
    _inherit = ['stock.route']

    show_in_pricelist = fields.Boolean(
        "Show in pricelist", default=False,
    )
