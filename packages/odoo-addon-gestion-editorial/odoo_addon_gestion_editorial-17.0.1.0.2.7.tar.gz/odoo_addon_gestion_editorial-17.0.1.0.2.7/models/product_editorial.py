from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError
from markupsafe import Markup
from odoo.tools.translate import _

import logging

_logger = logging.getLogger(__name__)


class EditorialProducts(models.Model):
    """ Extend product product for editorial management """

    _description = "Editorial Core Products"
    _inherit = 'product.product'

    on_hand_qty = fields.Float(compute='_compute_on_hand_qty', string='En almacén')
    liquidated_qty = fields.Float(compute='_compute_liquidated_sales_qty', string='Ventas liquidadas')
    liquidated_purchases_qty = fields.Float(compute='_compute_liquidated_purchases_qty', string='Compras liquidadas')
    owned_qty = fields.Float(compute='_compute_owned_qty', string='Existencias totales')
    in_distribution_qty = fields.Float(compute='_compute_in_distribution_qty', string='En distribución')
    purchase_deposit_qty = fields.Float(compute='_compute_purchase_deposit_qty', string='Depósito de compra')
    received_qty = fields.Float(compute='_compute_received_qty', string='Recibidos')

    def get_liquidated_sales_qty(self):
        return (
            self.get_product_quantity_in_location(
                self.env.ref("stock.stock_location_customers")
            ) - self.get_sales_to_author_qty()
        )

    def get_product_quantity_in_location(self, location):
        location_ids = location.get_all_child_locations()

        quants = self.env['stock.quant'].search([
            ('product_id', '=', self.id),
            ('location_id', 'in', location_ids)
        ])

        quantity = sum(quant.quantity for quant in quants)
        return quantity

    def get_received_qty(self):
        domain = [
            ('state', 'in', ['purchase', 'done']),
            ('product_id', '=', self.id)
        ]
        purchase_order_lines = self.env['purchase.order.line'].search(domain)
        return sum(purchase_order_lines.mapped('qty_received'))

    def get_liquidated_purchases_qty(self):
        domain = [
            ('state', 'in', ['purchase', 'done']),
            ('product_id', '=', self.id)
        ]
        purchase_order_lines = self.env['purchase.order.line'].search(domain)
        return sum(purchase_order_lines.mapped('liquidated_qty'))

    def get_liquidated_sales_qty_per_partner(self, partner_id):
        liquidated_sale_lines = self.env['stock.move.line'].search([
            ('move_id.partner_id', '=', partner_id),
            ('state', '=', 'done'),
            ('location_dest_id', '=', self.env.ref("stock.stock_location_customers").id),
            ('product_id', '=', self.id)
        ])
        liquidated_sales_qty = sum(line.quantity for line in liquidated_sale_lines)

        returned_sale_lines = self.env['stock.move.line'].search([
            ('move_id.partner_id', '=', partner_id),
            ('state', '=', 'done'),
            ('location_id', '=', self.env.ref("stock.stock_location_customers").id),
            ('product_id', '=', self.id)
        ])
        returned_sales_qty = sum(line.quantity for line in returned_sale_lines)
        return liquidated_sales_qty - returned_sales_qty

    def get_sales_to_author_qty(self):
        # Get sale orders with author pricelist
        sale_order_lines = self.env['sale.order.line'].search([
            ('product_id', '=', self.id),
            ('order_id.pricelist_id', '=',
             self.env.company.sales_to_author_pricelist.id)
        ])
        sale_orders = sale_order_lines.mapped('order_id')

        # Get stock moves related to these orders
        stock_moves = self.env['stock.move'].search([
            ('picking_id.sale_id', 'in', sale_orders.ids),
            ('state', '=', 'done'),
            ('product_id', '=', self.id)
        ])

        stock_moves_sales = stock_moves.filtered(
            lambda m: m.picking_code == 'outgoing'
        )
        stock_moves_refunds = stock_moves.filtered(
            lambda m:
            m.picking_code == 'incoming'
            and m.origin_returned_move_id
        )

        total_quantity = (
            sum(move.product_uom_qty for move in stock_moves_sales) - 
            sum(move.product_uom_qty for move in stock_moves_refunds)
        )
        return total_quantity

    def button_generate_ddaa_purchase_order(self):
        self.product_tmpl_id.button_generate_ddaa_purchase_order()

    def _compute_liquidated_purchases_qty(self):
        for product in self:
            product.liquidated_purchases_qty = product.get_liquidated_purchases_qty()

    def _compute_received_qty(self):
        for product in self:
            product.received_qty = product.get_received_qty()

    def _compute_purchase_deposit_qty(self):
        #Purchased on deposit but not settled
        for product in self:
            product.purchase_deposit_qty = product.received_qty - product.liquidated_purchases_qty

    def _compute_on_hand_qty(self):
        for product in self:
            product.on_hand_qty = product.get_product_quantity_in_location(self.env.ref("stock.stock_location_stock"))

    def _compute_liquidated_sales_qty(self):
        for product in self:
            product.liquidated_qty = product.get_liquidated_sales_qty()

    def _compute_owned_qty(self):
        for product in self:
            product.owned_qty = product.on_hand_qty + product.in_distribution_qty

    def _compute_in_distribution_qty(self):
        for product in self:
            product.in_distribution_qty = product.get_product_quantity_in_location(self.env.company.location_venta_deposito_id)


class EditorialTemplateProducts(models.Model):
    """ Extend product template for editorial management """

    _description = "Editorial Template Products"
    _inherit = 'product.template'
    # we inherited product.template model which is Odoo/OpenERP built in model and edited several fields in that model.
    isbn_number = fields.Char(string="ISBN", copy=False, required=False,
                              help="International Standard Book Number \
                              (ISBN)")
    legal_deposit_number = fields.Char(string="Legal deposit", help="Legal deposit number")
    product_tags = fields.Many2many(
        'product.template.tag', string='Product tag')
    purchase_ok = fields.Boolean('Can be Purchased', default=False)
    on_hand_qty = fields.Float(
        compute='_compute_on_hand_qty', string='En almacén')
    liquidated_qty = fields.Float(
        compute='_compute_liquidated_sales_qty', string='Ventas liquidadas')
    liquidated_purchases_qty = fields.Float(
        compute='_compute_liquidated_purchases_qty', string='Compras liquidadas')
    owned_qty = fields.Float(compute='_compute_owned_qty',
                             string='Existencias totales')
    in_distribution_qty = fields.Float(
        compute='_compute_in_distribution_qty', string='En distribución')
    purchase_deposit_qty = fields.Float(
        compute='_compute_purchase_deposit_qty', string='Depósito de compra')
    received_qty = fields.Float(
        compute='_compute_received_qty', string='Recibidos')
    authorship_ids = fields.One2many(
        'authorship.product', 'product_id', string='Authorships')
    # This field is used to filter the main authorship of the book for the view
    main_authorship_ids = fields.One2many(
        comodel_name='authorship.product',
        inverse_name='product_id',
        string='Relaciones principales para el precio de venta',
        domain=[('is_main_entry', '=', True)]
    )
    show_ddaa_data = fields.Boolean(compute='_compute_show_ddaa_data')
    is_book = fields.Boolean(compute='_compute_is_book')
    categ_name = fields.Text(compute='_compute_categ_name')

    @api.constrains('main_authorship_ids')
    def update_prices_book_delivered_to_authorship_lines(self):
        if not self.env.company.module_editorial_ddaa or \
            not (self.genera_ddaa or self.categ_id == self.env.company.product_category_ddaa_id):
            return

        for authorship in self.authorship_ids.filtered(lambda a: a.is_main_entry):
            domain = [
                    ('partner_id', '=', authorship.author_id.id),
                    ('state', '=', 'draft'),
                    ('is_ddaa_order', '=', True)
                ]
            ddaa_purchase_order = self.env['purchase.order'].search(domain, order='date_order desc', limit=1)
            if not ddaa_purchase_order:
                ddaa_purchase_order = self.button_generate_ddaa_purchase_order()

            _logger.info(f"### Updating DDAA order line book deliver for author: \
                          {authorship.author_id.name}, order: {ddaa_purchase_order.name}")
            # Update the DDAA order book lines with modified price
            ddaa_purchase_order.update_books_delivered_to_authorship_line(
                self, 'update_price', authorship.sales_price
            )

    @api.model
    def check_save_conditions(self, records_data):
        company = self.env.company
        conditions = []

        # Check legal deposit number duplicates
        try:
            legal_deposit = records_data.get('legal_deposit_number')
            if legal_deposit:
                duplicate = self.search([
                    ('legal_deposit_number', '=', legal_deposit),
                    ('id', '!=', records_data.get('id', False))
                ])
                if duplicate:
                    conditions.append({
                        'message': _(
                            "There is already a product with the legal deposit number %s:\n"
                            "%s\n"
                            "Do you want to continue?"
                        ) % (legal_deposit, duplicate[0].name)
                    })
        except Exception:
            _logger.exception("Error processing legal_deposit_number in check_save_conditions")

        # If the product is being created don't check for more conditions
        if not records_data.get('id', False):
            return conditions

        # If company does not have editorial DDAA module enabled return conditions
        if (not company.module_editorial_ddaa or not
                company.product_category_ddaa_id):
            return conditions

        prod = self.browse(records_data.get('id'))
        # 1) Check authorship changes
        try:
            authorships = records_data.get('authorship_ids') or []
            if authorships:
                conditions.append({
                    'message':
                        "Las ventas de este producto realizadas "
                        "tras este cambio utilizarán este nuevo porcentaje. "
                        "¿Deseas continuar?"
                })
        except Exception:
            _logger.exception("Error processing authorship_ids in check_save_conditions")

        # 2) Check product list_price changes
        try:
            new_price = records_data.get('list_price') or None
            if new_price and prod.list_price != new_price:
                conditions.append({
                    'message':
                        "Tras este cambio, los derechos de autoría "
                        "generados por ventas de este producto aplicarán "
                        "el porcentaje correspondiente sobre este nuevo precio. "
                        "¿Deseas continuar?"
                })
        except Exception:
            _logger.exception("Error processing list_price in check_save_conditions")

        # 3) Check related contacts price changes
        try:
            authorship_ids = records_data.get('main_authorship_ids') or []
            if authorship_ids:
                conditions.append({
                        'message':
                            "Vas a proceder a guardar el producto con modificaciones "
                            "en los importes a los que las autorías/receptoras de "
                            "regalías pueden adquirir los libros. Se procederá a "
                            "actualizar el precio del producto en los albaranes "
                            "de autoría que todavía no hayan sido confirmados. "
                            "¿Deseas continuar?"
                    })
        except Exception:
            _logger.exception("Error processing main_authorship_ids in check_save_conditions")

        return conditions

    # Show ddaa data in product view
    # if product generate ddaa or is ddda product
    def _compute_show_ddaa_data(self):
        self.show_ddaa_data = (
            self.env.company.module_editorial_ddaa and
            (self.env.company.product_category_ddaa_id == self.categ_id or
             self.env.company.is_category_genera_ddaa_or_child(self.categ_id))
        )

    # Product categ is book or child (All/Libros) or (All/Libro Digital)
    def _compute_is_book(self):
        self.is_book = (
         self.categ_id.id == self.env.ref("gestion_editorial.product_category_books").id 
         or self.categ_id.id == self.env.ref("gestion_editorial.product_category_digital_books").id
         or self.categ_id.parent_id.id == self.env.ref("gestion_editorial.product_category_books").id
         or self.categ_id.parent_id.id == self.env.ref("gestion_editorial.product_category_digital_books").id
        )

    def is_physical_book(self):
        return (self.categ_id.id == self.env.ref("gestion_editorial.product_category_books").id
                or self.categ_id.parent_id.id == self.env.ref("gestion_editorial.product_category_books").id)

    def is_ebook(self):
        return (self.categ_id.id == self.env.ref("gestion_editorial.product_category_digital_books").id
                or self.categ_id.parent_id.id == self.env.ref("gestion_editorial.product_category_digital_books").id)

    def _compute_on_hand_qty(self):
        for template in self:
            on_hand_qty = 0.0
            for product in template.product_variant_ids:
                on_hand_qty += product.get_product_quantity_in_location(self.env.ref("stock.stock_location_stock"))
            template.on_hand_qty = on_hand_qty

    def _compute_liquidated_sales_qty(self):
        for template in self:
            liquidated_sales_qty = 0.0
            for product in template.product_variant_ids:
                liquidated_sales_qty += product.get_liquidated_sales_qty()
            template.liquidated_qty = liquidated_sales_qty

            for authorship in template.authorship_ids:
                authorship.update_ddaa_percentage_based_on_conditions()

    def _compute_liquidated_purchases_qty(self):
        for template in self:
            liquidated_purchases_qty = 0.0
            for product in template.product_variant_ids:
                liquidated_purchases_qty += product.get_liquidated_purchases_qty()
            template.liquidated_purchases_qty = liquidated_purchases_qty

    def _compute_purchase_deposit_qty(self):
        for template in self:
            template.purchase_deposit_qty = template.received_qty - template.liquidated_purchases_qty

    def _compute_received_qty(self):
        for template in self:
            received_qty = 0.0
            for product in template.product_variant_ids:
                received_qty += product.get_received_qty()
            template.received_qty = received_qty

    def _compute_owned_qty(self):
        for template in self:
            template.owned_qty = template.on_hand_qty + template.in_distribution_qty

    def _compute_in_distribution_qty(self):
        for template in self:
            in_distribution_qty = 0.0
            for product in template.product_variant_ids:
                in_distribution_qty += product.get_product_quantity_in_location(self.env.company.location_venta_deposito_id)
            template.in_distribution_qty = in_distribution_qty

    @api.depends("categ_id")
    def _compute_categ_name(self):
        for product in self:
            if product.categ_id:
                product.categ_name = product.categ_id.name
            else:
                product.categ_name = ""

    @api.depends("categ_id")
    def _compute_display_name(self):
        super()._compute_display_name()

        for product in self:
            if product.is_ebook():
                product.display_name = f"[{product.categ_name}] {product.name}"


    @api.constrains("isbn_number")
    def check_is_isbn13(self):
        for record in self:
            if record.isbn_number:
                n = record.isbn_number.replace("-", "").replace(" ", "")
                if len(n) != 13:
                    raise exceptions.ValidationError("El ISBN debe tener 13 dígitos")
                product = sum(int(ch) for ch in n[::2]) + sum(
                    int(ch) * 3 for ch in n[1::2]
                )
                if product % 10 != 0:
                    raise exceptions.ValidationError(
                        "El ISBN %s no es válido." % record.isbn_number
                    )
        # all records passed the test, don't return anything

    @api.constrains("legal_deposit_number")
    def check_legal_deposit_number_format(self):
        for record in self:
            if record.legal_deposit_number:
                n = record.legal_deposit_number
                # Check if the string only contains allowed characters
                allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -')
                if not all(c in allowed_chars for c in n):
                    raise exceptions.ValidationError(_(
                        "The legal deposit number can only contain letters, numbers, spaces and dashes."
                    ))

    def update_or_create_ddaa_purchase_orders(self, ddaa_qty, sale_unit_price=None):
        authorships = self.authorship_ids.filtered(lambda a: a.generates_ddaa())
        _logger.info(f"## Updating or creating DDAA purchase orders for product: {self.name}, authorships: {authorships}")

        for authorship in authorships:
            _logger.info(f"Processing author: {authorship.author_id.name}, ddaa_qty: {ddaa_qty}")
            author = authorship.author_id
            domain = [
                ('partner_id', '=', author.id),
                ('state', '=', 'draft'),
                ('is_ddaa_order', '=', True)
            ]
            authorship_ddaa_order = self.env['purchase.order'].search(domain, order='date_order desc')

            if not authorship_ddaa_order:
                # Create purchase.order to ddaa receiver
                authorship_ddaa_order = self.env['purchase.order'].create({
                    'partner_id': author.id,
                    'is_ddaa_order': True,
                    'picking_type_id': self.env.ref("stock.picking_type_in").id
                })

            if sale_unit_price: # The selected pricelist gets the unit_price from the sale record
                ddaa_price = sale_unit_price * authorship.ddaa_percentage / 100
            else: # The selected pricelist gets the price from the authorship
                ddaa_price = authorship.price

            self.update_or_create_ddaa_purchase_order_lines(authorship_ddaa_order, authorship, ddaa_qty, ddaa_price)
        
        return authorship_ddaa_order

    def update_or_create_ddaa_purchase_order_lines(self, purchase_order, authorship, ddaa_qty, ddaa_price=None):
        section_count = len(purchase_order.order_line.filtered(lambda line: line.display_type == 'line_section'))
        sequence = section_count * 100

        # If there are section for the product use that sequence
        for line in purchase_order.order_line:
            if line.display_type == 'line_section' and line.section_id == self.id:
                sequence = line.sequence

        section_id = self.id # The section_id is the Odoo product's ID to which this line is related
        section_line = self.create_section_line(purchase_order, sequence)
        book_ddaa_lines = self.update_or_create_book_ddaa_lines(purchase_order, section_id, authorship, ddaa_qty, ddaa_price, sequence)
        books_delivered_to_authorship_line = self.create_books_delivered_to_authorship_line(purchase_order, section_id, authorship, sequence)
        royalty_advance_line = self.create_royalty_advance_line(purchase_order, section_id, sequence)

        _logger.debug(f"section_line: {section_line}")
        _logger.debug(f"book_ddaa_lines: {book_ddaa_lines}")
        _logger.debug(f"books_delivered_to_authorship_line: {books_delivered_to_authorship_line}")
        _logger.debug(f"royalty_advance_line: {royalty_advance_line}")


        purchase_order.write({'order_line': section_line + \
                                            book_ddaa_lines + \
                                            books_delivered_to_authorship_line + \
                                            royalty_advance_line
                              })

    def create_section_line(self, purchase_order, sequence):
        section_name = self.name
        section_line = purchase_order.order_line.filtered(
            lambda line: line.display_type == 'line_section' and line.name == section_name)

        values = {
            'name': section_name,
            'display_type': 'line_section',
            'section_id': self.id,
            'product_id': False,
            'product_qty': 0,
            'product_uom_qty': 0,
            'price_unit': 0,
            'sequence': sequence + 10
        }

        return [(0, 0, values)] if not section_line else []

    def update_or_create_book_ddaa_lines(self, purchase_order, section_id, authorship, ddaa_qty, ddaa_price, sequence):
        sequence_number = sequence + 10
        book_ddaa_lines = []
        ddaa_product_id = self.derecho_autoria.product_variant_ids[0].id

        # Get sequence of other ddaa lines with different contact type
        other_contact_types_ddaa_lines = purchase_order.order_line.filtered(
            lambda line: line.product_id.id == ddaa_product_id and line.contact_type != authorship.contact_type)
        if other_contact_types_ddaa_lines:
            line_with_highest_sequence = max(
                other_contact_types_ddaa_lines,
                key=lambda line: line.sequence,
                default=False
            )
            sequence_number = line_with_highest_sequence.sequence + 10

        book_ddaa_line = purchase_order.order_line.filtered(
            lambda line: line.product_id.id == ddaa_product_id and line.contact_type == authorship.contact_type and not line.end_date)

        values = {
            'name': self.name,
            'section_id': section_id,
            'product_id': ddaa_product_id,   # This field needs product.product id, ddaa is template.product, so we get the first product variant
            'product_qty': ddaa_qty,
            'contact_type': authorship.contact_type.id,
            'price_unit': ddaa_price,
            'product_uom': 1,
            'date_planned': purchase_order.date_order,
            'display_type': False,
        }

        _logger.debug(f"book_ddaa_line.price_unit: {book_ddaa_line.price_unit}")
        _logger.debug(f"ddaa_price: {ddaa_price}")

        if book_ddaa_line and book_ddaa_line.price_unit == ddaa_price:
            values["product_qty"] = book_ddaa_line.product_qty + ddaa_qty
            book_ddaa_lines.append((1, book_ddaa_line.id, values))
            _logger.info("Updating DDAA order line:")
            _logger.debug(f"\tPrice: {ddaa_price}")
            _logger.debug(f"\tQuantity: {book_ddaa_line.product_qty} + ({ddaa_qty}) = {values.get('product_qty')}")
        else:
            values["sequence"] = book_ddaa_line.sequence + 1 if book_ddaa_line else sequence_number + 1
            values["start_date"] = fields.Datetime.now()
            if book_ddaa_line:
                _logger.info("Closing existing DDAA order line.")
                book_ddaa_line.write({"end_date": fields.Datetime.now()})
                currency = self.env.user.company_id.currency_id
                body = Markup(
                    "El importe de regalías para <b>'{product_name}'</b> ha cambiado de <b>{previous_qty}{currency}</b> a <b>{new_qty}{currency}</b>.<br/>"
                    "Se ha creado una nueva línea en el albarán para contemplar el cambio de importe"
                ).format(product_name=self.name, currency=currency.symbol, previous_qty=book_ddaa_line.price_unit, new_qty=ddaa_price)
                purchase_order.message_post(
                    body=body,
                    message_type='comment',
                    subtype_xmlid='mail.mt_note'
                )
            _logger.info("Creating DDAA order line:")
            _logger.debug(f"\tPrice: {ddaa_price}")
            book_ddaa_lines.append((0, 0, values))

        return book_ddaa_lines

    def create_books_delivered_to_authorship_line(self, purchase_order, section_id, authorships, sequence):
        authorship = authorships[0]
        books_delivered_to_authorship_line = purchase_order.order_line.filtered(
            lambda line: line.product_id.id == self.env.ref("gestion_editorial.product_books_delivered_to_authorship").id and
                        line.section_id == section_id)

        values = {
            'name': self.env.ref("gestion_editorial.product_books_delivered_to_authorship").name,
            'section_id': section_id,
            'product_id': self.env.ref("gestion_editorial.product_books_delivered_to_authorship").id,
            'product_qty': 0,
            'price_unit': -authorship.sales_price,
            'date_planned': purchase_order.date_order,
            'product_uom': 1,
            'display_type': False,
            'sequence': sequence + 80,
        }

        return [(0, 0, values)] if not books_delivered_to_authorship_line else []

    def create_royalty_advance_line(self, purchase_order, section_id, sequence):
        royalty_advance_line = purchase_order.order_line.filtered(
            lambda line: line.product_id.id == self.env.ref("gestion_editorial.product_royalties_advance").id and
                         line.section_id == section_id)

        values = {
            "name": self.env.ref("gestion_editorial.product_royalties_advance").name,
            'section_id': section_id,
            "product_id": self.env.ref("gestion_editorial.product_royalties_advance").id,
            "date_planned": purchase_order.date_order,
            "product_uom": 1,
            "display_type": False,
            "product_qty": 0,
            "price_unit": 0.0,
            "sequence": sequence + 90
        }

        return [(0, 0, values)] if not royalty_advance_line else []

    def button_generate_ddaa_purchase_order(self):
        if not self.env.company.module_editorial_ddaa or \
            not (self.genera_ddaa or self.categ_id == self.env.company.product_category_ddaa_id):
            raise exceptions.ValidationError(
                'Este producto no genera DDAA o el modulo de DDAA no esta habilitado.'
            )
        # Is DDAA product
        if self.categ_id == self.env.company.product_category_ddaa_id and self.authorship_ddaa:
            ddaa_order = self.producto_referencia[0].update_or_create_ddaa_purchase_orders(0)
        else:   # Product is book
            ddaa_order = self.generate_ddaa(0)
        
        self.message_post(
            body=f"Se han creado los albaranes de autoría para este producto utilizando el botón de 'Generar albaranes de autoría'.",
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )
        return ddaa_order

    def generate_ddaa(self, ddaa_qty, sale_unit_price=None):
        if not self.env.company.module_editorial_ddaa or not self.genera_ddaa:
            return
        # Check if the book already has ddaa product created
        ddaa = self.derecho_autoria
        if not ddaa:
            authors = self.authorship_ids
            if not authors:
                return
            else:
                ddaa = self.env['product.template'].create({
                    'name': 'DDAA de ' + self.name,
                    'categ_id': self.env.company.product_category_ddaa_id.id,
                    'detailed_type': 'service',
                    'sale_ok': False,
                    'purchase_ok': True,
                    'producto_referencia': [self.id],
                    'derecho_autoria': False,
                    "supplier_taxes_id": False
                })
        
        # Generate purchase order for each authorship receptor
        return self.update_or_create_ddaa_purchase_orders(ddaa_qty, sale_unit_price)

    # DDAA: Derechos de autoría
    # When the category "All / Books" is selected the default values ​​are set:
    # Product that can be sold and bought and is storable.
    @api.onchange("categ_id")
    def _onchange_categ(self):
        book_categ_id = self.env.ref("gestion_editorial.product_category_books").id
        digital_book_categ_id = self.env.ref("gestion_editorial.product_category_digital_books").id

        for record in self:
            record._compute_is_book()
            if (
                record.categ_id.id == book_categ_id
                or record.categ_id.parent_id.id == book_categ_id
            ):
                record.sale_ok = True
                record.purchase_ok = True
                record.detailed_type = 'product'
            elif (
                record.categ_id.id == digital_book_categ_id
                or record.categ_id.parent_id.id == digital_book_categ_id
            ):
                record.sale_ok = True
                record.purchase_ok = True
                record.detailed_type = 'consu'
            elif (
                record.categ_id == self.env.company.product_category_ddaa_id
            ):
                record.detailed_type = 'service'
                record.sale_ok = False
                record.purchase_ok = True
                record.derecho_autoria = False
                record.supplier_taxes_id = False
            if (
                record.env.company.module_editorial_ddaa
                and record.env.company.is_category_genera_ddaa_or_child(record.categ_id)
            ):
                record.genera_ddaa = True
            else:
                record.genera_ddaa = False

    @api.onchange("categ_id")
    def _compute_view_show_fields(self):
        if self.env.company.module_editorial_ddaa:
            self.view_show_genera_ddaa_fields = (
                self.env.company.is_category_genera_ddaa_or_child(self.categ_id)
            )
            self.view_show_ddaa_fields = (
                self.categ_id == self.env.company.product_category_ddaa_id
            )
        else:
            self.view_show_genera_ddaa_fields = False
            self.view_show_ddaa_fields = False

    # DDAA: Copyright
    # Check one2one relation. Here between "producto_referencia" y "derecho_autoria"
    #
    # Note: we are creating the relationship between the templates.
    # Therefore, when we add the product to a stock.picking or a sale or purchase, we are actually adding the product  and not the template.
    # Please use product_tmpl_id to access the template of a product.
    producto_referencia = fields.One2many(
        "product.template",
        "derecho_autoria",
        string="Libro de referencia",
        help="Este campo se utiliza para relacionar el derecho de autoría con el libro",
    )

    # prod_ref = fields.Many2one("product.template", compute='compute_autoria', inverse='autoria_inverse', string="prod ref",
    #                             required=False)

    @api.model
    def _derecho_autoria_domain(self):
        return [("categ_id", "=", self.env.company.product_category_ddaa_id.id)]

    derecho_autoria = fields.Many2one(
        "product.template",
        domain=_derecho_autoria_domain,
        string="Producto ddaa",
        help="Este campo se utiliza para relacionar el derecho de autoría con el libro",
    )

    genera_ddaa = fields.Boolean("Genera derechos de autoría", default=False)

    authorship_ddaa = fields.One2many('authorship.product', related='producto_referencia.authorship_ids', string='DDAA', readonly=False)

    # @api.depends('producto_referencia')
    # def compute_autoria(self):
    #     if len(self.derecho_autorias) > 0:
    #         self.derecho_autoria = self.derecho_autorias[0]

    # def autoria_inverse(self):
    #     if len(self.derecho_autorias) > 0:
    #         # delete previous reference
    #         ddaa = self.env['product.template'].browse(self.derecho_autorias[0].id)
    #         ddaa.producto_referencia = False
    #     # set new reference
    #     self.derecho_autoria.producto_referencia = self

    view_show_genera_ddaa_fields = fields.Boolean(
        "Muestra los campos asociados a categorías que generan ddaa",
        compute="_compute_view_show_fields",
        default=False,
    )
    view_show_ddaa_fields = fields.Boolean(
        "Muestra los campos asociados a la categoría ddaa",
        compute="_compute_view_show_fields",
        default=False,
    )

    limited_visibility_by_provider = fields.Boolean(
        "Visibilidad limitada por proveedor", 
        help="El producto solo será visible en compras para los proveedores configurados",
        default=lambda self: self.env.company.visibility_limited_by_supplier
    )

    # DDAA: Copyright
    # A product associated with the category representing the DDAA is created
    @api.model_create_multi
    def create(self, vals_list):
        product_tmpl = super(EditorialTemplateProducts, self).create(vals_list)
        company = self.env.company
        if company.module_editorial_ddaa and vals_list:
            vals = vals_list[0]
            category_id = self.env["product.category"].browse(vals.get("categ_id"))
            if (
                company.is_category_genera_ddaa_or_child(category_id)
                and vals.get("genera_ddaa") == True
            ):
                ddaa = self.env["product.template"].create(
                    {
                        "name": "DDAA de " + vals.get("name"),
                        "categ_id": company.product_category_ddaa_id.id,
                        "detailed_type": "service",
                        "sale_ok": False,
                        "purchase_ok": True,
                        "producto_referencia": [product_tmpl.id],
                        "derecho_autoria": False,
                        "supplier_taxes_id": False
                    }
                )
                ddaa.button_generate_ddaa_purchase_order()
            else:
                product_tmpl.genera_ddaa = False
        return product_tmpl

    def get_sales_to_author_qty(self):
        sales_to_author_qty = 0.0
        for product in self.product_variant_ids:
            sales_to_author_qty += product.get_sales_to_author_qty()

        return sales_to_author_qty
    
    def button_total_existences(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Existencias totales',
            'res_model': 'stock.quant',
            'view_mode': 'tree',
            'views': [(False, 'tree')],
            'target': 'current',
            'domain': [('product_id', '=', self.id),
                       ('warehouse_id', '=', 1)],
            'context': {
                'group_by': 'location_id',
            },
        }
    
    def button_in_stock(self):
        self.ensure_one()
        stock_location = self.env.ref("stock.stock_location_stock")
        stock_location_and_childs = stock_location.get_all_child_locations()
        return {
            'type': 'ir.actions.act_window',
            'name': 'En stock',
            'res_model': 'stock.quant',
            'view_mode': 'tree',
            'views': [(False, 'tree')],
            'target': 'current',
            'domain': [('product_id', '=', self.id),
                       ('location_id', 'in', stock_location_and_childs)],
            'context': {
                'group_by': 'location_id',
            },
        }

    def button_in_distribution(self):
        self.ensure_one()
        deposit_location = self.env.company.location_venta_deposito_id.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'En distribución',
            'res_model': 'stock.quant',
            'view_mode': 'tree',
            'views': [(False, 'tree')],
            'target': 'current',
            'domain': [('product_id', '=', self.id),
                       ('location_id', '=', deposit_location)],
            'context': {
                'group_by': 'owner_id',
            },
        }        
    
    def button_purchases(self, view_name):
        picking_deposit_purchase = self.env.ref("gestion_editorial.stock_picking_type_compra_deposito").id
        return {
            'type': 'ir.actions.act_window',
            'name': view_name,
            'res_model': 'purchase.order.line',
            'view_mode': 'tree',
            'views': [(self.env.ref('gestion_editorial.editorial_purchase_order_line_tree').id, 'tree')],            
            'target': 'current',
            'domain': [('product_id', '=', self.id),
                       ('order_id.picking_type_id', '=', picking_deposit_purchase),
                    ],
        }
        
    def button_purchases_deposit(self):
        self.ensure_one()
        return self.button_purchases("Depósito de compra")
    
    def button_liquidated_purchases(self):
        self.ensure_one()
        return self.button_purchases("Compras liquidadas")

    def button_received(self):
        self.ensure_one()
        vendors_location = self.env.ref("stock.stock_location_suppliers").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Recibidos',
            'res_model': 'stock.move.line',
            'view_mode': 'tree',
            'views': [(False, 'tree')],
            'target': 'current',
            'domain': [('product_id', '=', self.id),
                        '|',
                        ('location_id', '=', vendors_location),
                        ('location_dest_id', '=', vendors_location)
                    ],
        }
    
    def button_liquidated_sales(self):
        self.ensure_one()
        customers_location = self.env.ref("stock.stock_location_customers").id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move.line',
            'name': 'Ventas liquidadas',
            'view_mode': 'tree',
            'views': [(False, 'tree')],
            'target': 'current',
            'domain': [('product_id', '=', self.id),
                        '|',
                        ('location_id', '=', customers_location),
                        ('location_dest_id', '=', customers_location)
                    ],
        }


class EditorialProductTags(models.Model):
    """ Editorial product tags management """

    _description = 'Editorial product tags'
    _name = 'product.template.tag'
    _rec_name = 'name'

    name = fields.Char(string='Product tag', required=True)

