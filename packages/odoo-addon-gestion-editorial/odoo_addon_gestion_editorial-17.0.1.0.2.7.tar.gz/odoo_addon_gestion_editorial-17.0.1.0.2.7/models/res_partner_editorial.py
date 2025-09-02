from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class EditorialPartners(models.Model):
    """ Extend res.partner template for editorial management """

    _description = "Editorial Partners"
    _inherit = 'res.partner'
    # we inherited res.partner model which is Odoo built in model and edited several fields in that model.
    cliente_num = fields.Integer(string="Num. cliente",
                           help="Número interno de cliente")
    is_author = fields.Boolean(string="Es autor", default=False,
                           help="Indica que el contacto es autor")

    authorship_ids = fields.One2many(
        comodel_name='authorship.product',
        inverse_name='author_id',
        string='Authorships')

    purchase_liq_pricelist = fields.Many2one(
        comodel_name='product.pricelist',
        string="Tarifa liquidaciones de compras",
        company_dependent=False,
        domain=lambda self: [('company_id', 'in', (self.env.company.id, False))],
        help="Esta tarifa se usará por defecto para liquidaciones de compra en depósito de este contacto")
    default_purchase_type = fields.Many2one(
        comodel_name='stock.picking.type',
        string="Tipo de compra",
        help="Este tipo de compra se usará por defecto en los pedidos de compra de este contacto",
        domain="[('code', '=', 'incoming')]"
    )

    def export_sales_deposit(self):
        wizard = self.env['deposit.stock.xls.report'].create({
            'deposit': 'ventas',
            'owner': self.id,
        })
        return wizard.export_xls()

    def export_purchases_deposit(self):
        wizard = self.env['deposit.stock.xls.report'].create({
            'deposit': 'compras',
            'owner': self.id,
        })
        return wizard.export_xls()

    def get_sales_deposit_lines(self):
        deposit_sales_location = self.env.company.location_venta_deposito_id.id
        incoming_domain = [
            ('move_id.partner_id', '=', self.id),
            ('location_dest_id', '=', deposit_sales_location),
            ('state', '=', 'done'),
        ]
        incoming_lines = self.env['stock.move.line'].search(incoming_domain)

        outgoing_domain = [
            ('move_id.partner_id', '=', self.id),
            ('location_id', '=', deposit_sales_location),
            ('state', '=', 'done'),
        ]
        outgoing_lines = self.env['stock.move.line'].search(outgoing_domain)

        total_quantities = {}
        for line in incoming_lines:
            total_quantities.setdefault(line.product_id.id, 0)
            total_quantities[line.product_id.id] += line.quantity

        for line in outgoing_lines:
            total_quantities.setdefault(line.product_id.id, 0)
            total_quantities[line.product_id.id] -= line.quantity

        return total_quantities

    def get_purchases_deposit_lines(self, alphabetical_order=False):
        domain = [
            ('partner_id', '=', self.id),
            ('state', 'in', ['purchase', 'done']),
            ('is_liquidated', '=', False),
            ('order_id.picking_type_id', '=', self.env.company.stock_picking_type_compra_deposito_id.id)
        ]
        order_clause = 'name asc' if alphabetical_order else 'date_planned asc'
        deposito_lines = self.env['purchase.order.line'].search(domain, order=order_clause)
        return deposito_lines


class EditorialPartnerType(models.Model):
    """ Editorial partner types management """

    _description = "Editorial contact type"
    _name = "res.partner.type"
    _rec_name = "name"

    name = fields.Char(string="Contact type", required=True)
    default_ddaa_percentage_books = fields.Float(string="Porcentaje de regalías por defecto para libros físicos")
    default_ddaa_percentage_ebooks = fields.Float(string="Porcentaje de regalías por defecto para libros digitales")
