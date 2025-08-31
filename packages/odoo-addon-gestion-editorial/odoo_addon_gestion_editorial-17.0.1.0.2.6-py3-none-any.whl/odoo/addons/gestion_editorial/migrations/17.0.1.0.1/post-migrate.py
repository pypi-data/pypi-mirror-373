from odoo import api, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    routes = env['stock.route'].search([])
    _logger.info(f"### UPDATING MODULE TO 17.0.1.0.1")
    _logger.info(f"### SETTING show_in_pricelist TO TRUE FOR DEPOSIT SALES, DIRECT SALES AND AUTHORS PAID ROUTES")
    for route in routes:
        if route.id in [
            env.ref('gestion_editorial.route_deposit_sales').id,
            env.ref('gestion_editorial.route_direct_sales').id,
            env.ref('gestion_editorial.stock_route_authors_paid').id
        ]:
            route.write({'show_in_pricelist': True})
            if route.id == env.ref('gestion_editorial.route_direct_sales').id:
                route.write({'product_selectable': True})
        else:
            route.write({'show_in_pricelist': False})
        _logger.info(f"show_in_pricelist set {route.show_in_pricelist} in {route.name}")
