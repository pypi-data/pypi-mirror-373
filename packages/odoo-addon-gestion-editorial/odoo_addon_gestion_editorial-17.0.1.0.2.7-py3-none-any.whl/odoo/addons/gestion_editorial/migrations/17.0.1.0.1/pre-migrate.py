from odoo import api, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info(f"### PRE UPDATING MODULE TO 17.0.1.0.1")

    # Fix LIQ journal error
    liq_journal = env['account.journal'].search([
        ('code', '=', 'LIQ'),
        ('type', '=', 'sale'),
    ], limit=1)

    if liq_journal and not env['ir.model.data'].search([
        ('module', '=', 'gestion_editorial'),
        ('name', '=', 'account_journal_venta_deposito'),
        ('model', '=', 'account.journal')
    ]):
        env['ir.model.data'].create({
            'name': 'account_journal_venta_deposito',
            'model': 'account.journal',
            'module': 'gestion_editorial',
            'res_id': liq_journal.id,
            'noupdate': True
        })

    # Fix stock location fkey error
    stock_location_view = env['ir.model.data'].search([
        ('module', '=', 'gestion_editorial'),
        ('name', '=', 'stock_location_my_company')
    ])
    if stock_location_view:
        stock_location_view.write({'noupdate': True})

    # We make it also in the hook but we need it to run it here for old installations
    # Change Name "Deliver in 1 step route and rule" to "Direct sales"
    customers_location = env.ref('stock.stock_location_customers')
    stock_location = env.ref('stock.stock_location_stock')
    direct_sales_rule = env['stock.rule'].search([
        ('location_src_id', '=', stock_location.id),
        ('location_dest_id', '=', customers_location.id),
        ('procure_method', '=', 'make_to_stock'),
    ], limit=1)

    # Create xml_id for the route
    direct_sales_rule.name = "Regla venta en firme"
    direct_sales_rule.route_id.name = "Ruta venta en firme"
    if not env['ir.model.data'].search([
        ('module', '=', 'gestion_editorial'),
        ('name', '=', 'route_direct_sales'),
        ('model', '=', 'stock.route')
    ]):
        env['ir.model.data'].create({
            'name': 'route_direct_sales',
            'model': 'stock.route',
            'module': 'gestion_editorial',
            'res_id': direct_sales_rule.route_id.id,
            'noupdate': True  # Evita que se actualice en futuras actualizaciones
        })

    ## Clear caches of the module
    env['ir.ui.view'].clear_caches()
    env['ir.actions.act_window'].clear_caches()
    env['ir.actions.report'].clear_caches()
    env['ir.model.data'].clear_caches()
    env['ir.model'].clear_caches()
    env['ir.model.fields'].clear_caches()
    env['ir.model.access'].clear_caches()
    env['ir.config_parameter'].clear_caches()
    env['ir.ui.menu'].clear_caches()
    env['ir.ui.view'].clear_caches()
    env['ir.rule'].clear_caches()
    env.invalidate_all() 

    # Remove all views related to the module from database
    data = env['ir.model.data'].search([
        ('module', '=', 'gestion_editorial'),
        ('model', '=', 'ir.ui.view'),
    ])
    views = env['ir.ui.view'].browse(data.mapped('res_id'))
    views.unlink()
    data.unlink()

