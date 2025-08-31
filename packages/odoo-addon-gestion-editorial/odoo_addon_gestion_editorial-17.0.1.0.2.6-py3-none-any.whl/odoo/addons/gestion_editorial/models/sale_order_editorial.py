from odoo.exceptions import UserError
from odoo import models, fields, api


class EditorialSaleOrder(models.Model):
    """ Extend sale.order template for editorial management """

    _description = "Editorial Sale Order"
    _inherit = 'sale.order'  # odoo/addons/sale/models/sale.py

    is_deposit_sale_order = fields.Boolean(
        compute='_compute_is_deposit_sale_order',
        string="Is deposit sale order"
    )

    is_client_default_pricelist = fields.Boolean(
        compute='_compute_is_client_default_pricelist',
    )

    @api.onchange("pricelist_id")
    def _compute_is_client_default_pricelist(self):
        for record in self:
            record.is_client_default_pricelist = (
                self.pricelist_id == self.partner_id.property_product_pricelist
            )

    def _compute_is_deposit_sale_order(self):
        for record in self:
            record.is_deposit_sale_order = record.pricelist_id.is_deposit_pricelist()

    @api.onchange('order_line')
    def default_pricelist_when_order_line(self):
        if self.order_line:
            if self.pricelist_id.route_id:
                for line in self.order_line:
                    line.route_id = self.pricelist_id.route_id.id

    @api.onchange('pricelist_id')
    def default_pricelist_when_pricelist_id(self):
        if self.order_line:
            if self.pricelist_id.route_id:
                for line in self.order_line:
                    line.route_id = self.pricelist_id.route_id.id
                    line.price_unit = line._get_display_price()

    def action_confirm(self):
        # If pricelist is sales to author
        # check if the client is ddaa receiver of all books of the order
        if (self.pricelist_id == self.env.company.sales_to_author_pricelist):
            for line in self.order_line:
                ddaa_receivers = line.product_id.product_tmpl_id.main_authorship_ids.mapped('author_id')
                if self.partner_id not in ddaa_receivers:
                    raise UserError(
                        "Esta tarifa solo se puede aplicar si el cliente esta "
                        "relacionado con el libro y tiene fijado un precio de venta.")

        result = super(EditorialSaleOrder, self).action_confirm()

        # If pricelist is deposit delete DS/Depositos to Customers transfer
        if self.pricelist_id.is_deposit_pricelist():
            pickings = self.picking_ids.filtered(lambda p: p.state == 'waiting')
            if pickings:
                pickings[0].action_cancel()
                pickings[0].unlink()

        return result
    
    # Check if is author pricelist to set special price for that contact
    @api.onchange('order_line', 'partner_id', 'pricelist_id')
    def onchange_order_line(self):
        if all(l.product_id for l in self.order_line if not l.display_type and not l.is_delivery):
            super().onchange_order_line()

        authors_pricelist = self.env.ref("gestion_editorial.authors_pricelist", raise_if_not_found=False)   
        if not authors_pricelist or self.pricelist_id != authors_pricelist:
            return
        
        for line in self.order_line.filtered(lambda l: l.product_id and not l.display_type and not l.is_delivery):
            authorship = line.product_id.product_tmpl_id.main_authorship_ids.filtered(
                lambda a: a.author_id == self.partner_id)
            
            if authorship:
                currency = self.pricelist_id.currency_id
                line.price_unit = currency.round(authorship.sales_price)
            else:
                raise UserError(
                    "%s no es un contacto relacionado con el libro %s, "
                    "o no tiene fijado un precio de venta. "
                    "Por lo que no se puede aplicar la tarifa de venta a autoras." %
                    (self.partner_id.name, line.product_id.name)
                )


class EditorialSaleOrderLine(models.Model):
    """ Extend sale.order.line template for editorial management """
    _description = "Editorial Sale Order Line"
    _inherit = 'sale.order.line' # odoo/addons/sale/models/sale.py

    product_barcode = fields.Char(
        string='Código de barras / ISBN',
        related='product_id.barcode', readonly=True
    )
    product_list_price = fields.Float(
        string='PVP',
        related='product_id.list_price',
        readonly=True
    )
    in_stock_qty = fields.Float(
        string='In stock', 
        compute='_compute_in_stock_qty'
    )
    in_distribution_qty = fields.Float(
        string='In distribution',
        compute='_compute_in_distribution_qty'
    )

    @api.depends('product_id')
    def _compute_in_stock_qty(self):
        for record in self:
            if record.product_id:
                record.in_stock_qty = record.product_id.on_hand_qty
            else:
                record.in_stock_qty = 0

    @api.depends('product_id')
    def _compute_in_distribution_qty(self):
        for record in self:
            if record.product_id:
                record.in_distribution_qty = record.product_id.in_distribution_qty
            else:
                record.in_distribution_qty = 0