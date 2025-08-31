from odoo import models, fields
from odoo.exceptions import UserError
from odoo import _


class EditorialProductPricelist(models.Model):
    """ Extend product pricelist model for editorial management """

    _description = "Editorial Product Pricelist"
    _inherit = 'product.pricelist'

    route_id = fields.Many2one('stock.route', string='Ruta')
    genera_ddaa = fields.Boolean(
        string="Genera derechos de autoría",
        default=lambda self: self.env.company.pricelists_generate_ddaa
    )
    price_from = fields.Selection(
        string="Obtener precio desde",
        help="Indica qué precio se elige para calcular los derechos de autoría.\n"
             "Producto: El importe de regalías se basa en aplicar un porcentaje al precio indicado en la ficha de prodcuto.\n"
             "Venta/Liquidación: El importe de regalías se base en aplicar un porcentaje al precio indicado en el presupuesto de venta o liquidación.",
        selection=[("product", "Producto"),
                   ("sale", "Venta/Liquidación")],
        default="product"
    )
    display_edit_warning = fields.Boolean(compute='_compute_display_edit_warning')

    # Displays a warning if the pricelist is not recomended to be updated
    def _compute_display_edit_warning(self):
        for pricelist in self:
            pricelist.display_edit_warning = pricelist.id in [self.env.company.sales_to_author_pricelist.id]

    def is_deposit_pricelist(self):
        return self in self.get_deposit_pricelists()

    def get_deposit_pricelists(self):
        # Search for the deposit routes
        # deposit -> customers
        deposit_rules = self.env['stock.rule'].search([
            ('location_src_id', '=', self.env.company.location_venta_deposito_id.id),
            ('location_dest_id', '=', self.env.ref("stock.stock_location_customers").id)
        ])

        if deposit_rules:
            routes = self.env['stock.route'].search([
                ('rule_ids', 'in', deposit_rules.ids)
            ])
            if routes:
                # Search for all the pricelist with deposit route
                pricelists = self.env['product.pricelist'].search([
                    ('route_id', 'in', routes.ids)
                ])
                return pricelists
        return []
