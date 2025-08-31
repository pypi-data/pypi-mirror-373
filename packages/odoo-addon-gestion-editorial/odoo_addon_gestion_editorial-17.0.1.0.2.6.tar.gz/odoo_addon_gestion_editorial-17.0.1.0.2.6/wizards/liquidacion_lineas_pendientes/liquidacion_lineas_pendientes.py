from odoo import api, fields, models, exceptions
from lxml import etree

class LiquidationWizard(models.TransientModel):
    """ Wizard: Ayuda para seleccionar las stock.move.lines pendientes de liquidar """
    _name = 'liquidacion.wizard.editorial'
    _description = "Wizard Depósito"

    partner_id = fields.Many2one('res.partner', string='Cliente')
    liquidacion_id = fields.Many2one('account.move', string='Liquidación')
    liquidacion_type = fields.Selection(related='liquidacion_id.move_type')
    liquidacion_line_ids = fields.One2many('liquidacion.line.editorial', 'liquidacion_wizard_id', string="Lineas de Liquidacion", copy=True)

    @api.onchange('partner_id')
    def _update_invoice_lines(self):
        pendientes_liquidar_line_ids = self.liquidacion_id.get_deposit_data(alphabetical_order=True)
        self.liquidacion_line_ids = self.env['liquidacion.line.editorial'] # Empty liquidation lines
        if self.partner_id.property_account_position_id:
            self.fiscal_position_id = self.partner_id.property_account_position_id

        if self.liquidacion_id.move_type == 'out_invoice' or self.liquidacion_id.move_type == 'out_refund':
            for product_id, qty in pendientes_liquidar_line_ids.items():
                if qty > 0:
                    liq_line = self._update_liq_line(product_id=product_id, product_qty=qty)
                    self.liquidacion_line_ids |= liq_line
        else:   # purchase liq
            for move_line in pendientes_liquidar_line_ids:
                liq_line = self._update_liq_line(move_line=move_line)
                self.liquidacion_line_ids |= liq_line

        if self.liquidacion_id.move_type == 'in_invoice' or self.liquidacion_id.move_type == 'in_refund':
            for liquidacion_line in self.liquidacion_line_ids:
                products_sold = liquidacion_line.product_id.get_liquidated_sales_qty()
                products_purchased_and_liquidated = liquidacion_line.product_id.get_liquidated_purchases_qty()
                liquidacion_line.vendidos_sin_liquidar = max(0, products_sold - products_purchased_and_liquidated)
                liquidacion_line.vendidos_sin_liquidar = min(liquidacion_line.vendidos_sin_liquidar, liquidacion_line.total_qty_disponibles)

    def _update_liq_line(self, move_line=None, product_id=None, product_qty=None):
        product_id = move_line.product_id if move_line else product_id
        liq_line = self.liquidacion_line_ids.filtered(
            lambda line: line.product_id == product_id)
        if liq_line:
            liq_line = liq_line[0]
        else:
            liq_line = self.env['liquidacion.line.editorial'].create({})
            liq_line.product_id = self.env["product.product"].browse(product_id)

        if self.liquidacion_id.move_type == 'out_invoice' or self.liquidacion_id.move_type == 'out_refund':
            total_product_uom_qty = product_qty
            liq_line.total_qty_done = 0
            liq_line.update({'total_product_uom_qty': total_product_uom_qty})
        else:   # purchase liq
            total_product_uom_qty = liq_line.total_product_uom_qty + move_line.qty_received
            liq_line.total_qty_done += move_line.liquidated_qty
            liq_line.update({'total_product_uom_qty': total_product_uom_qty})
        return liq_line

    @api.onchange('liquidacion_line_ids')
    def _check_liquidacion_lines(self):
        for wizard in self:
            for liquidacion_line in wizard.liquidacion_line_ids:
                if liquidacion_line.total_qty_a_liquidar and liquidacion_line.total_qty_a_liquidar > 0.0:
                    if wizard.liquidacion_type in ['in_invoice', 'out_invoice', 'out_refund'] and liquidacion_line.total_qty_a_liquidar > liquidacion_line.total_qty_disponibles:
                        raise exceptions.ValidationError("La cantidad seleccionada no puede ser mayor que la cantidad disponible en depósito.")
                    elif wizard.liquidacion_type == 'in_refund' and liquidacion_line.total_qty_a_liquidar > liquidacion_line.total_qty_disponibles_devolver_dep_com:
                        raise exceptions.ValidationError("La cantidad a liquidar no puede ser mayor que la cantidad disponible para devolver.")

    @api.model
    def default_get(self, fields):
        res = super(LiquidationWizard, self).default_get(fields)
        res['partner_id'] = self.env.context.get('partner_id')
        res['liquidacion_id'] = self.env.context.get('liquidacion_id')
        return res

    def seleccionar_para_liquidar(self):
        for liquidacion_line in self.liquidacion_line_ids:
            if liquidacion_line.total_qty_a_liquidar > 0.0:
                if not self.liquidacion_id.pricelist_id:
                    # Utilizamos siempre el PVP independientemente de si es liquidacion de compra o venta
                    price_unit = liquidacion_line.product_id.list_price
                else:
                    pricelist = self.liquidacion_id.pricelist_id
                    price_unit = pricelist._get_product_price(
                        liquidacion_line.product_id,
                        1,
                        currency=pricelist.currency_id,
                        uom=liquidacion_line.product_id.uom_id,
                        date=self.liquidacion_id.invoice_date
                    )
                quantity = liquidacion_line.total_qty_a_liquidar
                product = liquidacion_line.product_id
                partner = self.partner_id.id

                if self.liquidacion_type == 'in_invoice' or self.liquidacion_type == 'in_refund':
                    taxes = product.supplier_taxes_id
                else:
                    taxes = product.taxes_id

                taxes = self.liquidacion_id.fiscal_position_id.map_tax(taxes)
                vals = {
                    'name': liquidacion_line.product_id.name,
                    'move_id': self.liquidacion_id.id,
                    'partner_id': partner,
                    'product_id': product.id,
                    'journal_id': self.liquidacion_id.journal_id,
                    'quantity': quantity,
                    'price_unit': price_unit,
                    'tax_ids': taxes,
                }
                self.liquidacion_id.write({'invoice_line_ids': [(0,0,vals)]})
        return {'type': 'ir.actions.act_window_close'}

    def select_all_liquidacion_lines(self):
        for liquidacion_line in self.liquidacion_line_ids:
            liquidacion_line.total_qty_a_liquidar = liquidacion_line.total_qty_disponibles
            if not self.liquidacion_id.pricelist_id:
                price_unit = liquidacion_line.product_id.list_price
            else:
                pricelist = self.liquidacion_id.pricelist_id
                price_unit = pricelist._get_product_price(
                    liquidacion_line.product_id,
                    1,
                    currency=pricelist.currency_id,
                    uom=liquidacion_line.product_id.uom_id,
                    date=self.liquidacion_id.invoice_date
                )
            quantity = liquidacion_line.total_qty_a_liquidar
            product = liquidacion_line.product_id
            partner = self.partner_id.id

            vals = {
                'name': liquidacion_line.product_id.name,
                'move_id': self.liquidacion_id.id,
                'partner_id': partner,
                'product_id': product.id,
                'journal_id': self.liquidacion_id.journal_id,
                'quantity': quantity,
                'price_unit': price_unit,
                'tax_ids': product.taxes_id,
            }
            self.liquidacion_id.write({'invoice_line_ids': [(0,0,vals)]}) # = self.env['account.move.line'].new(vals)
        return {'type': 'ir.actions.act_window_close'}


class EditorialLiquidationLine(models.TransientModel):
    """ Modelo de línea de liquidación"""
    _name = "liquidacion.line.editorial"
    _description = "Linea Liquidacion Editorial"

    # company_id = fields.Many2one(related='liquidacion_id.company_id', readonly=True)
    liquidacion_wizard_id = fields.Many2one('liquidacion.wizard.editorial', "Liquidacion Wizard", index=True, ondelete="cascade")
    product_id = fields.Many2one('product.product', 'Producto')
    product_barcode = fields.Char('Código de barras / ISBN', related='product_id.barcode', readonly=True)
    product_name = fields.Char('Nombre', related='product_id.name', readonly=True)
    total_product_uom_qty = fields.Float('Total en Depósito', default=0.0, digits='Product Unit of Measure', required=True, copy=False)
    total_qty_done = fields.Float('Total Hecho', default=0.0, digits='Product Unit of Measure', copy=False)
    total_qty_disponibles = fields.Float('Total en depósito', default=0.0, digits='Product Unit of Measure', copy=False, compute="_compute_available")
    total_qty_disponibles_devolver_dep_com = fields.Float('Total disponible', default=0.0, digits='Product Unit of Measure', copy=False, compute="_compute_available_dep_com")
    total_qty_a_liquidar = fields.Float('A liquidar', default=0.0, digits='Product Unit of Measure', copy=False)
    vendidos_sin_liquidar = fields.Float('Vendidos sin liquidar', default=0.0, digits='Product Unit of Measure', copy=False, readonly=True)

    @api.depends('total_qty_done', 'total_product_uom_qty')
    def _compute_available(self):
        for record in self:
            if self.env.context.get('liquidacion_type') in ['out_invoice', 'out_refund']:
                record.total_qty_disponibles = record.total_product_uom_qty
            else:
                record.total_qty_disponibles = record.total_product_uom_qty - record.total_qty_done

    @api.depends('total_qty_done', 'total_product_uom_qty')
    def _compute_available_dep_com(self):
        for record in self:
            record.product_id._compute_on_hand_qty()
            stock = record.product_id.on_hand_qty
            record.total_qty_disponibles_devolver_dep_com = min(record.total_qty_disponibles, stock)
