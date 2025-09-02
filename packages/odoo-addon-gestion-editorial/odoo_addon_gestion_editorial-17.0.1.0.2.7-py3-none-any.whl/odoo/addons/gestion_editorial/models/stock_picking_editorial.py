import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class EditorialPicking(models.Model):
    """ Extend stock.picking template for editorial management """

    _description = "Editorial Stock Picking"
    _inherit = 'stock.picking'  # odoo/addons/stock/models/stock_picking.py

    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Tarifa',
        related='sale_id.pricelist_id',
        readonly=True
    )

    # Assign the owner_id equal to the partner on creation if not set
    @api.model
    def create(self, vals):
        picking = super().create(vals)
        if picking.partner_id and not picking.owner_id:
            picking.owner_id = picking.partner_id.id

        return picking

    @api.depends(
            'state',
            'move_lines',
            'move_lines.state',
            'move_lines.package_level_id',
            'move_lines.move_line_ids.package_level_id'
        )
    def _compute_move_without_package(self):
        for picking in self:
            for move in self.move_lines:
                for ml in move.move_line_ids:
                    # If owner_id is equal we don't need to change anything so we don't call write method
                    if ml.owner_id != self.partner_id:
                        ml.owner_id = self.partner_id
            picking.move_ids_without_package = picking._get_move_ids_without_package()

    # DDAA: Derechos de autoría
    # Cuando se valida un stock.picking, se comprueba que la localización de
    # destino o origen (devoluciones) sea Partner Locations Customers para actualizar 
    # el albarán de autoría. Se revisa también que la tarifa de la venta genere DDAA
    def generate_picking_ddaa(self):
        tarifa = self.sale_id.pricelist_id
        if self.env.company.module_editorial_ddaa and \
            (not self.sale_id or tarifa.genera_ddaa) and \
            self.env.ref("stock.stock_location_customers").id in \
                (self.location_dest_id.id, self.location_id.id):
            # Para las líneas que contengan un libro que tenga derechos de
            # autoría. Busca una purchase order a ese autor con la línea con
            # el derecho de autoría, si no, créala
            book_lines = self.move_line_ids_without_package.filtered(
                lambda line: self.env.company.is_category_genera_ddaa_or_child(
                    line.product_id.categ_id
                )
            )
            if book_lines:
                for book_line in book_lines:
                    if book_line.move_id and tarifa.price_from == "sale":
                        sale_unit_price = book_line.move_id.sale_line_id.price_unit
                    else:
                        sale_unit_price = None

                    if self.location_dest_id.id == self.env.ref("stock.stock_location_customers").id:
                        ddaa_qty = book_line.quantity
                    else:
                        ddaa_qty = 0 - book_line.quantity  # For refunds the quantity is negative

                    book_line.product_id.product_tmpl_id.generate_ddaa(ddaa_qty, sale_unit_price)

    def check_ddaa_and_books_authors(self):
        for product in self.move_ids_without_package:
            if not product.product_tmpl_id.genera_ddaa:
                raise UserError(_(f"El libro {product.name} no genera DDAA y por lo tanto no puede ser transferido de esta forma."))
            product_authors = product.product_tmpl_id.authorship_ids.mapped('author_id')
            if self.partner_id not in product_authors:
                raise UserError(_(f"El libro {product.name} no corresponde con el autor de esta transferencia."))

    def update_ddaa_order_authorship_lines(self):
        domain = [
                ('partner_id', '=', self.partner_id.id),
                ('state', '=', 'draft'),
                ('is_ddaa_order', '=', True)
            ]
        authorship_purchase_order = self.env['purchase.order'].search(domain, order='date_order desc', limit=1)
        if not authorship_purchase_order:
            raise UserError(_(f"No se encuentra el albarán de DDAA para el autor {self.partner_id.name}."))

        # Update the DDAA order book lines with the quantities from the picking
        for line in self.move_ids_without_package:
            if line.product_id.product_tmpl_id.genera_ddaa:
                authorship_purchase_order.update_books_delivered_to_authorship_line(
                    line.product_id.product_tmpl_id, 'update_qty', line.product_uom_qty, self.name
                )

    def button_validate(self):
        if self.picking_type_id.id == self.env.ref("gestion_editorial.stock_picking_type_entrega_autoria").id:
            self.check_ddaa_and_books_authors()
            self.update_ddaa_order_authorship_lines()
        self.generate_picking_ddaa()
        return super(EditorialPicking, self).button_validate()

    def action_assign(self):
        if self.picking_type_id.id == self.env.ref("gestion_editorial.stock_picking_type_entrega_autoria").id:
            self.check_ddaa_and_books_authors()
        return super(EditorialPicking, self).action_assign()

    def action_confirm(self):
        for picking_type in self.picking_type_id:
            if picking_type.id == self.env.ref("gestion_editorial.stock_picking_type_entrega_autoria").id:
                self.check_ddaa_and_books_authors()
        return super(EditorialPicking, self).action_confirm()


