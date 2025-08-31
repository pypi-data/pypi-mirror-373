from odoo import fields, models


class EditorialCompany(models.Model):
    """Extend res.company for editorial management"""

    _inherit = "res.company"
    _check_company_auto = True

    module_editorial_ddaa = fields.Boolean("Gestión de DDAA", default=True)

    def is_category_genera_ddaa_or_child(self, cat_id):
        if cat_id.parent_path:
            parents_and_self_ids = [int(x) for x in cat_id.parent_path.split("/")[:-1]]
            for cat_ddaa_id in self.product_categories_genera_ddaa_ids:
                if cat_ddaa_id.id in parents_and_self_ids:
                    return True
        return False

    product_category_ddaa_id = fields.Many2one(
        "product.category",
        string="Categoría de producto para DDAA",
        help="Categoría de producto que representa los derechos de autoría.",
    )

    product_categories_genera_ddaa_ids = fields.Many2many(
        "product.category",
        string="Categorías que generan DDAA",
        help="Categorías de producto madre que generan derechos de autoría.",
    )

    sales_to_author_pricelist = fields.Many2one(
        "product.pricelist",
        string="Pricelist used for sales to authors",
    )

    pricelists_generate_ddaa = fields.Boolean(
        string="Pricelists generate DDAA by default",
        default=True
    )

    stock_picking_type_compra_deposito_id = fields.Many2one(
        "stock.picking.type",
        string="Tipo de operación de depósito compra",
        help="Tipo de operación usada para las compras a depósito.",
    )

    account_journal_deposito_compra_id = fields.Many2one(
        "account.journal",
        string="Diario para liquidaciones de compra a depósito",
    )

    account_journal_deposito_venta_id = fields.Many2one(
        "account.journal",
        string="Diario para liquidaciones de venta a depósito",
    )

    location_venta_deposito_id = fields.Many2one(
        "stock.location",
        string="Ubicación de depósito venta",
        help="Ubicación usada para las ventas a depósito.",
    )

    visibility_limited_by_supplier = fields.Boolean("Limited visibility for supplier", default=True)

    location_authors_courtesy_id = fields.Many2one(
        'stock.location',
        string='Libros entregados de cortesía a autores',
    )

    location_authors_royalties_id = fields.Many2one(
        'stock.location',
        string='Libros entregados a cuenta de regalías de autores',
    )

    location_promotion_id = fields.Many2one(
        'stock.location',
        string='Ubicación para promoción',
        help="Ubicación utilizada para productos entregados en promociones"
    )

    module_dilve = fields.Boolean(string="Dilve", readonly=False)
