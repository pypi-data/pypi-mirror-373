import odoo
import logging

_logger = logging.getLogger(__name__)

odoo.tools.config.parse_config([])
db_names = odoo.service.db.list_dbs()

if not db_names:
    raise ValueError("No database found.")

for db_name in db_names:
    print("### STARTING XML ID SCRIPT IN DATABASE: ", db_name)
    with odoo.api.Environment.manage():
        registry = odoo.registry(db_name)
        with registry.cursor() as cr:
            env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
            # Set xml_id for book and digital book
            book = env['product.category'].search([('name', '=', 'Libros')], limit=1)
            digital_book = env['product.category'].search([('name', '=', 'Libro Digital')], limit=1)
            if book:
                _logger.info("###### BOOK FOUND")
                model_data = env['ir.model.data'].search([
                    ('model', '=', 'product.category'),
                    ('name', '=', 'product_category_books')
                ], limit=1)

                if not model_data:
                    env['ir.model.data'].create({
                        'module': 'gestion_editorial',
                        'name': 'product_category_books',
                        'model': 'product.category',
                        'res_id': book.id,
                    })
                    _logger.info("###### XML ID FOR BOOK CREATED")
                else:
                    _logger.info("[x]###### XML ID FOR BOOK NOT CREATED")

            if digital_book:
                _logger.info("###### DIGITAL BOOK FOUND")
                model_data = env['ir.model.data'].search([
                    ('model', '=', 'product.category'),
                    ('name', '=', 'product_category_digital_books')
                ], limit=1)

                if not model_data:
                    env['ir.model.data'].create({
                        'module': 'gestion_editorial',
                        'name': 'product_category_digital_books',
                        'model': 'product.category',
                        'res_id': digital_book.id,
                    })
                    _logger.info("###### XML ID FOR DIGITAL BOOK CREATED")
                else:
                    _logger.info("[x]###### XML ID FOR DIGITAL BOOK NOT CREATED")

            # Set xml_id for rliq if it doesn't have one
            picking_type_rliq = env['stock.picking.type'].search([('sequence_code', '=', 'RLIQ')], limit=1)

            if picking_type_rliq:
                _logger.info("###### RLIQ FOUND")
                model_data = env['ir.model.data'].search([
                    ('model', '=', 'stock.picking.type'),
                    ('name', '=', 'stock_picking_type_rectificacion_liq')
                ], limit=1)

                if not model_data:
                    env['ir.model.data'].create({
                        'module': 'gestion_editorial',
                        'name': 'stock_picking_type_rectificacion_liq',
                        'model': 'stock.picking.type',
                        'res_id': picking_type_rliq.id,
                    })
                    _logger.info("###### XML ID FOR RLIQ CREATED")
                else:
                    _logger.info("[x] ###### XML ID FOR RLIQ NOT CREATED, ALREADY EXISTS ONE")

            # Set xml_id for sales deposit and parent deposit
            sales_deposit = env['stock.location'].browse(env.company.location_venta_deposito_id.id)

            if sales_deposit.exists():
                # Verify if it has xml_id in ir.model.data
                _logger.info("###### SALES DEPOSIT FOUND")
                xml_id_deposito = env['ir.model.data'].search([
                    ('model', '=', 'stock.location'),
                    ('name', '=', 'stock_location_deposito_venta')
                ], limit=1)

                # Si no tiene xml_id, asignarlo
                if not xml_id_deposito:
                    env['ir.model.data'].create({
                        'module': 'gestion_editorial',
                        'name': 'stock_location_deposito_venta',
                        'model': 'stock.location',
                        'res_id': sales_deposit.id,
                    })
                    _logger.info("###### SALES DEPOSIT XML ID CREATED")
                else:
                    _logger.info("[x] ###### XML ID FOR SALES DEPOSIT NOT CREATED, ALREADY EXISTS ONE")

                # Search parent location
                parent_location = sales_deposit.location_id
                if parent_location.exists():
                    _logger.info("###### PARENT LOCATION FOUND")

                    parent_xml_id = env['ir.model.data'].search([
                        ('model', '=', 'stock.location'),
                        ('name', '=', 'stock_location_my_company')
                    ], limit=1)

                    if not parent_xml_id:
                        env['ir.model.data'].create({
                            'module': 'gestion_editorial',
                            'name': 'stock_location_my_company',
                            'model': 'stock.location',
                            'res_id': parent_location.id,
                        })
                        _logger.info("###### PARENT LOCATION CREATED")
                    else:
                        _logger.info("[x] ###### XML ID FOR PARENT DEPOSIT NOT CREATED, ALREADY EXISTS ONE")

            env.cr.commit()
