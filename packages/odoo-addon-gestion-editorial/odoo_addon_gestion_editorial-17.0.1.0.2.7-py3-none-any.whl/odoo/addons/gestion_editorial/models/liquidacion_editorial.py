from collections import defaultdict
from odoo import models, fields, api, exceptions
from odoo.tools.float_utils import float_compare
from markupsafe import Markup


class EditorialLiquidacion(models.Model):
    """ Modelo de liquidación que extiende de account.move """

    # https://github.com/OCA/OCB/blob/13.0/addons/account/models/account_move.py
    _description = "Liquidacion Editorial"
    _inherit = ['account.move']

    @api.model
    def default_get(self, fields):
        res = super(EditorialLiquidacion, self).default_get(fields)
        if 'journal_id' in fields and res['is_liquidacion']:
            if res['move_type'] == 'in_refund':
                journal = self.env.company.account_journal_deposito_compra_id
                res['journal_id'] = journal.id
            elif res['move_type'] == 'out_refund':
                journal = self.env.company.account_journal_deposito_venta_id
                res['journal_id'] = journal.id
        return res

    # Set is_liquidacion to false. It will be false always to rectificative invoices made from invoice
    def action_reverse(self):
        self_copy = self
        self_copy.is_liquidacion = False
        action = super(EditorialLiquidacion, self_copy).action_reverse()
        return action

    @api.model
    def _get_default_is_liquidacion(self):
        if self._context.get('invoice_type') and self._context['invoice_type'] == 'LIQ':
            return True
        else:
            return False

    is_liquidacion = fields.Boolean(
        "Es liquidacion", default=_get_default_is_liquidacion
    )
    is_sales_deposit_return = fields.Boolean(
        "Es devolución de depósito de ventas", default=False
    )
    has_ref_picking = fields.Boolean(compute='_compute_has_ref_picking')

    def _compute_has_ref_picking(self):
        ref_picking = self.env['stock.picking'].search_count([
            ('origin', '=', self.name),
        ])
        self.has_ref_picking = ref_picking > 0

    # TO CHANGE IN FUTURE
    # This field is used to identify returns of liquidated liquidations with negative total
    # If True it will be used to change symbol of total amount in liquidations (only in views)
    is_negative_liquidation_return = fields.Boolean(
        "Es devolución de liquidación negativa", default=False
    )

    # TO CHANGE IN FUTURE
    # These variables are use to invert symbol of negative liquidation return (only in views)
    amount_untaxed_inverted = fields.Monetary(string='Base imponible', compute='_compute_inverted_amount_liquidations')
    amount_total_inverted = fields.Monetary(string='Total ', compute='_compute_inverted_amount_liquidations')
    amount_residual_inverted = fields.Monetary(string='Importe adeudado', compute='_compute_inverted_amount_liquidations')

    def _compute_inverted_amount_liquidations(self):
        self.amount_untaxed_inverted = self.amount_untaxed * -1
        self.amount_total_inverted = self.amount_total * -1
        self.amount_residual_inverted = self.amount_residual * -1

    @api.onchange('partner_id')
    def _set_partner_purchase_liq_pricelist(self):
        if self.move_type == 'in_invoice' and self.is_liquidacion and self.partner_id.purchase_liq_pricelist.id:
            self.pricelist_id = self.partner_id.purchase_liq_pricelist

    def action_post(self):
        if self.is_liquidacion and self.move_type == 'in_invoice':
            if not self.pricelist_id:
                raise exceptions.ValidationError(
                    "Es obligatorio seleccionar una tarifa."
                )
        return super().action_post()
    
    # When using the button for create "Factura rectificativa" set is_liquidation = False
    def action_switch_invoice_into_refund_credit_note(self):
        self.is_liquidacion = False
        return super().action_switch_invoice_into_refund_credit_note()

    def checkLiquidacionIsValid(self, liquidacion, deposit_data):
        products_to_check = defaultdict(lambda: {'total_liquidacion': 0, 'total_deposito': 0})
        negative_lines_to_check = defaultdict(int)

        for invoice_line in liquidacion.invoice_line_ids:
            if invoice_line.quantity < 0:
                if self.is_sales_deposit_return:
                    raise exceptions.ValidationError(f"No se pueden introducir cantidades negativas para devoluciones de depósito.")
                negative_lines_to_check[invoice_line.product_id] += -invoice_line.quantity
                continue
            products_to_check[invoice_line.product_id]['total_liquidacion'] += invoice_line.quantity
            qty_total_deposito = 0
            if (self.move_type == 'out_invoice' or self.move_type == 'out_refund'):
                qty_total_deposito = deposit_data[invoice_line.product_id.id]
                products_to_check[invoice_line.product_id]['total_deposito'] = qty_total_deposito
            else:   # purchase liquidation
                deposito_lines_to_check = deposit_data.filtered(
                    lambda deposito_line: deposito_line.product_id
                    == invoice_line.product_id
                )
                if deposito_lines_to_check:
                    if self.move_type == 'in_invoice':
                        qty_total_deposito = sum(p.qty_received - p.liquidated_qty for p in deposito_lines_to_check)
                    elif self.move_type == 'in_refund':
                        invoice_line.product_id._compute_on_hand_qty()
                        stock = invoice_line.product_id.on_hand_qty
                        qty_total_deposito = min(sum(p.qty_received - p.liquidated_qty for p in deposito_lines_to_check), stock)

                    products_to_check[invoice_line.product_id]['total_deposito'] = qty_total_deposito

        products_not_available = {}
        for product, qty in products_to_check.items():
            if qty['total_liquidacion'] > qty['total_deposito']:
                products_not_available[product.name] = qty['total_deposito']

        if len(products_not_available) > 0:
            msg = "No hay stock suficiente disponible en depósito con estos valores. Estos son valores disponibles en depósito:"
            for product_name, product_qty in products_not_available.items():
                msg += "\n* " + str(product_name) + ": " + str(product_qty)
            raise exceptions.UserError(msg)

        negative_lines_error_messages = []

        for product, return_qty in negative_lines_to_check.items():
            product_liquidated_qty = product.get_liquidated_sales_qty_per_partner(self.partner_id.id)
            if return_qty > product_liquidated_qty:
                negative_lines_error_messages.append(f"La cantidad que intentas devolver es mayor a la cantidad que has liquidado para el producto: {product.name}. Cantidad disponible: {product_liquidated_qty}")

        if negative_lines_error_messages:
            error_message = "\n".join(negative_lines_error_messages)
            raise exceptions.ValidationError(error_message)

    def get_deposit_data(self, alphabetical_order=False):
        deposito_lines = []
        # Sales liquidation
        if self.move_type == 'out_invoice' or self.move_type == 'out_refund':
            deposito_lines = self.partner_id.get_sales_deposit_lines()

        # Purchase liquidation
        elif self.move_type == 'in_invoice' or self.move_type == 'in_refund':
            deposito_lines = self.partner_id.get_purchases_deposit_lines(alphabetical_order)

        return deposito_lines

    def get_invoice_lines_sum_quantity_by_product(self):
        # group invoice line by product and sum quantities
        totals = defaultdict(int)
        for invoice_line in self.invoice_line_ids:
            totals[invoice_line.product_id] += invoice_line.quantity
        return totals.items()

    def create_return_liquidation_moves(self, products_and_qty):
        origin_draft_document = f'DRAFT/{self.id}'
        location_id = self.env.ref("stock.stock_location_customers").id
        location_dest_id = self.env.company.location_venta_deposito_id.id

        return_picking = self.env['stock.picking'].create({
            'partner_id': self.partner_id.id,
            'picking_type_id': self.env.ref("gestion_editorial.stock_picking_type_rectificacion_liq").id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'origin': origin_draft_document,
            'move_type': 'direct',
        })

        # Add products to return picking
        for product, qty in products_and_qty.items():
            new_stock_move = self.env['stock.move'].create({
                'picking_id': return_picking.id,
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': qty,
                'product_uom': product.uom_id.id,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
            })

            self.env['stock.move.line'].create({
                'move_id': new_stock_move.id,
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'quantity': qty,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'picking_id': return_picking.id,
            })

        # Set qty_done for each stock move
        for stock_move in return_picking.move_ids_without_package:
            stock_move.quantity = stock_move.product_uom_qty
        # Set qty_done for each move line
        for move_line in return_picking.move_line_ids_without_package:
            move_line.quantity = move_line.move_id.product_uom_qty

        return_picking.button_validate()

    def return_products_from_negative_lines(self, invoice_product_qty_data,
                                            is_return=False):
        invoice_product_qty_data_without_negatives = {}
        products_to_return = {}

        for product, quantity in invoice_product_qty_data:
            if quantity >= 0:
                invoice_product_qty_data_without_negatives[product] = quantity
            else:
                products_to_return[product] = -quantity     # Negative to invert negative value

        if is_return and products_to_return:
            raise exceptions.ValidationError(
                "No puede haber líneas negativas en una devolución de depósito."
            )

        if products_to_return:
            self.create_return_liquidation_moves(products_to_return)
        # return array without negative lines    
        return invoice_product_qty_data_without_negatives.items()

    def process_sales_liquidation(self, deposit_data, is_return=False):
        invoice_product_qty_data = self.get_invoice_lines_sum_quantity_by_product()
        # Get array without negative products after returning them
        invoice_product_qty_data = self.return_products_from_negative_lines(
            invoice_product_qty_data, is_return)

        # Return if there are no invoice lines
        # It can be because liquidation with only negative lines
        if not invoice_product_qty_data:
            return

        # Preparate picking
        if is_return:
            picking_type_id = self.env.ref('stock.picking_type_in').id
            location_id = self.env.company.location_venta_deposito_id.id
            location_dest_id = self.env.ref("stock.stock_location_stock").id
        else:
            picking_type_id = self.env.ref('stock.picking_type_out').id
            location_id = self.env.company.location_venta_deposito_id.id
            location_dest_id = self.env.ref("stock.stock_location_customers").id

        # Create liquidation picking
        picking_vals = {
            'partner_id': self.partner_id.id,
            'picking_type_id': picking_type_id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'origin': f'DRAFT/{self.id}',
            'move_type': 'direct',
        }

        picking = self.env['stock.picking'].create(picking_vals)

        # Add products from liquidation to picking
        for product_id, quantity in invoice_product_qty_data:
            invoice_line_qty = quantity
            total_product_qty = deposit_data[product_id.id]

            if total_product_qty < invoice_line_qty:
                raise exceptions.ValidationError(
                    f"No hay stock suficiente disponible en depósito para el producto {product_id.name}. "
                    f"Disponible: {total_product_qty}, "
                    f"Requerido: {invoice_line_qty}"
                )

            # Create stock move of product and associate to picking
            new_stock_move = self.env['stock.move'].create({
                'name': product_id.name,
                'product_id': product_id.id,
                'product_uom': product_id.uom_id.id,
                'product_uom_qty': invoice_line_qty,
                'picking_id': picking.id,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'picking_type_id': picking_type_id,
                'partner_id': self.partner_id.id,
            })

            self.env['stock.move.line'].create({
                'move_id': new_stock_move.id,
                'product_id': product_id.id,
                'product_uom_id': product_id.uom_id.id,
                'quantity': invoice_line_qty,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'picking_id': picking.id,
            })

        # Set move lines qty_done to liquidation qty
        for stock_move in picking.move_ids_without_package:
            stock_move.quantity = stock_move.product_uom_qty
        for move_line in picking.move_line_ids_without_package:
            move_line.quantity = move_line.move_id.product_uom_qty

        picking.button_validate()

        return picking

    def liquidate_deposito_compras(self, deposito_lines):

        invoice_product_qty_data = self.get_invoice_lines_sum_quantity_by_product()

        for product_id, quantity in invoice_product_qty_data:
            invoice_line_qty = quantity
            pendientes_liquidar_purchase_lines = deposito_lines.filtered(
                lambda deposito_line: deposito_line.product_id
                == product_id
            )
            if (not pendientes_liquidar_purchase_lines or len(pendientes_liquidar_purchase_lines) <= 0):
                raise exceptions.ValidationError(
                    "No hay stock suficiente disponible en depósito con estos valores a liquidar. Intenta volver a comprobar el depósito"
                )
            for purchase_line in pendientes_liquidar_purchase_lines:
                if invoice_line_qty > 0:
                    qty_to_liquidate = purchase_line.qty_received - purchase_line.liquidated_qty
                    # If qty from liquidation is greater than qty available to liquidate in purchase line
                    if invoice_line_qty >= qty_to_liquidate:
                        new_liquidated_qty = purchase_line.qty_received
                        invoice_line_qty -= qty_to_liquidate
                        self.post_note_purchase_liq(purchase_line.order_id, qty_to_liquidate, product_id)
                    else:
                        new_liquidated_qty = purchase_line.liquidated_qty + invoice_line_qty
                        self.post_note_purchase_liq(purchase_line.order_id, invoice_line_qty, product_id)
                        invoice_line_qty = 0

                    purchase_line.write({'liquidated_qty': new_liquidated_qty})

    def devolver_deposito_compras(self, deposito_lines):
        odoo_env = self.env
        pickings_return = {}    # relation between done_picking (key) and the created_return (value)

        invoice_product_qty_data = self.get_invoice_lines_sum_quantity_by_product()

        for product_id, quantity in invoice_product_qty_data:
            liquidacion_line_qty = quantity
            if liquidacion_line_qty > 0.0:
                pendientes_cerrar_purchase_lines = deposito_lines.filtered(
                    lambda deposito_line: deposito_line.product_id == product_id)
                if not pendientes_cerrar_purchase_lines:
                    raise exceptions.ValidationError(
                        "No hay stock suficiente disponible en depósito para devolver. Intenta volver a comprobar el depósito"
                    )
                for pendiente_purchase_line in pendientes_cerrar_purchase_lines:
                    if liquidacion_line_qty <= 0:
                        break
                    qty_deposito = pendiente_purchase_line.qty_received - pendiente_purchase_line.liquidated_qty
                    qty_difference = liquidacion_line_qty - qty_deposito

                    associated_done_picking = (
                        pendiente_purchase_line.order_id.picking_ids.filtered(
                            lambda picking: (
                            picking.picking_type_id.id == self.env.company.stock_picking_type_compra_deposito_id.id
                            and picking.state == 'done'
                            and product_id.id in [li.product_id.id for li in picking.move_line_ids_without_package]
                            )
                        )
                    )
                    if len(associated_done_picking) > 1:
                        associated_done_picking = associated_done_picking[0]
                    elif len(associated_done_picking) <= 0:
                        continue

                    # Check if we have already created a return for this done_picking
                    if associated_done_picking not in pickings_return:
                        # New Wizard to make the return of one line
                        return_picking = odoo_env['stock.return.picking'].create(
                            {'picking_id': associated_done_picking.id}
                        )
                        pickings_return[associated_done_picking] = return_picking
                        for line in return_picking.product_return_moves:
                            line.write({'quantity': 0})
                    return_picking = pickings_return.get(associated_done_picking)

                    return_picking_line = return_picking.product_return_moves.filtered(
                        lambda line: line.product_id == product_id
                    )
                    return_qty = qty_deposito if qty_difference >= 0 else liquidacion_line_qty
                    return_picking_line.write(
                        {'quantity': return_picking_line.quantity + return_qty}
                    )
                    liquidacion_line_qty = qty_difference
                    self.post_note_purchase_liq(pendiente_purchase_line.order_id, 
                        return_qty, product_id, is_return=True)

        new_return_pickings = []

        for return_picking in pickings_return.values():
            new_stock_picking_data = return_picking.create_returns()
            new_stock_picking = odoo_env['stock.picking'].browse(
                new_stock_picking_data['res_id']
            )

            # Set quantity_done to move and move lines
            for stock_move in new_stock_picking.move_ids_without_package:
                stock_move.quantity = stock_move.product_uom_qty
            for move_line in new_stock_picking.move_line_ids_without_package:
                move_line.quantity = move_line.move_id.product_uom_qty

            new_stock_picking.button_validate()
            new_return_pickings.append(new_stock_picking)

        return new_return_pickings

    def post_note_with_picking_ref(self, picking):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        picking_url = f"{base_url}/web#id={picking.id}&model=stock.picking&view_type=form"
        message = Markup(
            "Se ha creado una transferencia al procesar esta operación.<br/>"
            "Referencia: <a href='{url}' target='_blank'>{name}</a>"
        ).format(url=picking_url, name=picking.name)

        self.message_post(
            body=message,
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )

    def post_note_purchase_liq(self, purchase_order, liquidated_qty, product_id, is_return=False):
        word_action = "Liquidando" if not is_return else "Devolviendo"
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        picking_url = f"{base_url}/web#id={purchase_order.id}&model=purchase.order&view_type=form"
        message = Markup(
            "Se ha modificado la orden de compra <a href='{url}' target='_blank'>{name}</a> "
            "al procesar esta operación. {word_action} {liquidated_qty} unidades de: {product_name}<br/>"
        ).format(url=picking_url, name=purchase_order.name, liquidated_qty=liquidated_qty,
                 product_name=product_id.name, word_action=word_action)

        self.message_post(
            body=message,
            message_type='comment',
            subtype_xmlid='mail.mt_note'
        )

    def post_y_liquidar(self):
        if not self.is_liquidacion:
            raise exceptions.ValidationError(
                "Sólo se puede liquidar desde una factura tipo liquidación"
            )

        if not self.pricelist_id and self.move_type == 'in_invoice':
            raise exceptions.ValidationError(
                "Es obligatorio seleccionar una tarifa."
            )

        deposit_data = self.get_deposit_data()
        self.checkLiquidacionIsValid(self, deposit_data)

        if self.move_type == 'out_invoice':
            associated_picking = self.process_sales_liquidation(deposit_data)
        elif self.move_type == 'in_invoice':
            self.liquidate_deposito_compras(deposit_data)
            associated_picking = False

        if self.amount_total < 0.0:
            negative_liquidation = True
            self.move_type = 'out_refund'  # Change to RINV / Rectificative invoice
            self.amount_total *= -1  # Price change to avoid price check alert in action_post
            self.is_negative_liquidation_return = True
        else:
            negative_liquidation = False

        self.action_post()
        # We set the origin document after post because before we dont have the invoice name
        if associated_picking:
            associated_picking.origin = self.name
            self.post_note_with_picking_ref(associated_picking)

        # Only for return of liquidated liquidationsç
        return_pickings = self.env['stock.picking'].search([
            ('origin', '=', f'DRAFT/{self.id}'),
        ])
        for picking in return_pickings:
            picking.origin = self.name
            self.post_note_with_picking_ref(picking)

        # We transform the prices from normal invoice to rectificative invoice
        if negative_liquidation:
            for invoice_line in self.invoice_line_ids:
                pricelist = self.pricelist_id
                invoice_line.price_unit = pricelist._get_product_price(
                    invoice_line.product_id,
                    1,
                    currency=pricelist.currency_id,
                    uom=invoice_line.product_id.uom_id,
                    date=self.invoice_date
                )
            self.amount_total *= -1
            self.amount_residual *= -1
            self.amount_residual_signed *= -1
            self.amount_total_signed *= -1
            self.amount_tax_signed *= -1
            self.amount_untaxed_signed *= -1
            self.amount_untaxed *= -1
            self.amount_tax *= -1

    def post_y_devolver(self):
        if not self.is_liquidacion:
            raise exceptions.ValidationError(
                "Sólo se puede devolver depósito desde una factura tipo devolución depósito"
            )
        if self.move_type == 'out_refund':
            self.is_sales_deposit_return = True        

        deposito_lines = self.get_deposit_data()
        self.checkLiquidacionIsValid(self, deposito_lines)

        if self.move_type == 'out_refund':
            associated_picking = self.process_sales_liquidation(
                deposito_lines, is_return=True)
            self.action_post()
            associated_picking.origin = self.name
            self.post_note_with_picking_ref(associated_picking)
        elif self.move_type == 'in_refund':
            return_pickings = self.devolver_deposito_compras(deposito_lines)
            self.action_post()
            for picking in return_pickings:
                self.post_note_with_picking_ref(picking)


class EditorialAccountMoveLine(models.Model):
    """ Extend account.move.line template for editorial management """

    _description = "Editorial Account Move Line"
    _inherit = 'account.move.line'  # odoo/addons/account/models/account_move.py

    product_barcode = fields.Char(
        string="Código de barras / ISBN", related='product_id.barcode', readonly=True
    )
