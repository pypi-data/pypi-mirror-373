from odoo import api, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)

def pre_init_hook(env):
    # Change Name "Deliver in 1 step route and rule" to "Direct sales"
    customers_location = env.ref('stock.stock_location_customers')
    stock_location = env.ref('stock.stock_location_stock')
    direct_sales_rule = env['stock.rule'].search([
        ('location_src_id', '=', stock_location.id),
        ('location_dest_id', '=', customers_location.id),
        ('procure_method', '=', 'make_to_stock'),
    ], limit=1)

    direct_sales_rule.name = "Regla venta en firme"
    direct_sales_rule.route_id.name = "Ruta venta en firme"
    # Create xml_id for the route
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

    # ES Billing -> Set fiscal location
    # Verify is company country is Spain
    if env.company.country_id.code == 'ES':
        template_code = 'es_assec'
        env['account.chart.template'].with_context(preserve_journals=True).try_loading(template_code, env.company.id)

        # Set default taxes to 4% (book taxes in spain)
        tax_sale_4g = env['account.tax'].search([
            ('name', '=', '4% G'),
            ('type_tax_use', '=', 'sale')], limit=1)
        tax_purchase_4g = env['account.tax'].search([
            ('name', '=', '4% G'),
            ('type_tax_use', '=', 'purchase')], limit=1)
        env.company.account_sale_tax_id = tax_sale_4g
        env.company.account_purchase_tax_id = tax_purchase_4g

def post_init_hook(env):
    # Set necessary settings for the module to work properly

    # Sales -> Client account -> On invitation
    env['ir.config_parameter'].set_param('auth_signup.invitation_scope', 'b2b')

    # Accounting -> Add internal users to group "Show Full Accounting Features"    
    group_account_user = env.ref('account.group_account_user')
    # Sales advanced pricelist
    group_advanced_pricelist = env.ref('product.group_sale_pricelist')
    users = env['res.users'].search([('share', '=', False)])    # All internal users
    for user in users:
        user.groups_id += group_advanced_pricelist
        user.groups_id += group_account_user
    # Sales -> Disable online signature
    env.company.portal_confirmation_sign = False

    # Sales -> Shipping methods
    module = env['ir.module.module'].search(
        [('name', '=', 'delivery')], limit=1)
    if module and module.state != 'installed':
        module.button_install()

    # General -> Uninstall module web image library unplash
    module = env['ir.module.module'].search(
        [('name', '=', 'web_unsplash')], limit=1)
    if module and module.state == 'installed':
        module.button_uninstall()

    # General -> Uninstall module partner autocomplete
    module = env['ir.module.module'].search(
        [('name', '=', 'partner_autocomplete')], limit=1)
    if module and module.state == 'installed':
        module.button_uninstall()

    # Inventory -> Uninstall module confirmation by sms
    module = env['ir.module.module'].search(
        [('name', '=', 'stock_sms')], limit=1)
    if module and module.state == 'installed':
        module.button_uninstall()

    # Inventory
    # Enable locations + routes multi-step
    # Disable partner autocomplete
    # Sales -> Pricelists
    # Stock -> Consignment
    env['res.config.settings'].create({
        'group_stock_multi_locations': True,
        'group_stock_adv_location': True,
        'module_partner_autocomplete': False,
        'group_product_pricelist': True,
        'product_pricelist_setting': 'advanced',
        'group_stock_tracking_owner': True,
    }).execute()

    # Billing
    # Set rounding method global instead of per line
    env.company.tax_calculation_rounding_method = 'round_globally'

    # Select price include in taxes
    other_taxes = env['account.tax'].search([])
    for tax in other_taxes:
        tax.price_include = True

    # Set company default values for gestion_editorial
    if not env.company.location_venta_deposito_id:
        env.company.location_venta_deposito_id = env.ref(
            "gestion_editorial.stock_location_deposito_venta"
        ).id

    if not env.company.product_category_ddaa_id:
        env.company.product_category_ddaa_id = env.ref(
            "gestion_editorial.product_category_ddaa"
        ).id

    if not env.company.product_categories_genera_ddaa_ids:
        env.company.product_categories_genera_ddaa_ids = [
            env.ref(
                "gestion_editorial.product_category_books"
            ).id,
            env.ref(
                "gestion_editorial.product_category_digital_books"
            ).id
            ]

    if not env.company.stock_picking_type_compra_deposito_id:
        env.company.stock_picking_type_compra_deposito_id = env.ref(
            "gestion_editorial.stock_picking_type_compra_deposito"
        ).id

    if not env.company.account_journal_deposito_compra_id:
        env.company.account_journal_deposito_compra_id = env.ref(
            "gestion_editorial.account_journal_compra_deposito"
        ).id
    
    if not env.company.account_journal_deposito_venta_id:
        env.company.account_journal_deposito_venta_id = env.ref(
            "gestion_editorial.account_journal_venta_deposito"
        ).id 

    if not env.company.location_authors_royalties_id:
        env.company.location_authors_royalties_id = env.ref(
            "gestion_editorial.stock_location_authors_royalties"
        ).id

    if not env.company.location_authors_courtesy_id:
        env.company.location_authors_courtesy_id = env.ref(
            "gestion_editorial.stock_location_authors_courtesy"
        ).id

    if not env.company.location_promotion_id:
        env.company.location_promotion_id = env.ref(
            "gestion_editorial.stock_location_promocion"
        ).id

    if not env.company.sales_to_author_pricelist:
        env.company.sales_to_author_pricelist = env.ref(
            "gestion_editorial.authors_pricelist"
        ).id

    # Update parent of deposit location
    deposit_location = env.ref(
        'gestion_editorial.stock_location_deposito_venta')
    storage_location_parent = env.ref(
        'stock.stock_location_stock').location_id
    deposit_location.location_id = storage_location_parent.id

    # Set warehouse name
    warehouse = env['stock.warehouse'].search(
        [('company_id', '=', env.company.id)], limit=1)
    warehouse.name = "Almacén"
    warehouse.code = "AL"

    # Set route settings for direct sales route
    direct_route = env.ref('gestion_editorial.route_direct_sales')
    direct_route.show_in_pricelist = True
    direct_route.product_selectable = True
