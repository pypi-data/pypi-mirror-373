import logging
from odoo import api, SUPERUSER_ID
from odoo.tools import sql

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.registry.clear_cache()
    env.invalidate_all()
    _logger.info("=== INICIANDO POST-MIGRATE SCRIPT ===")

    try:
        ## Migrate DDAA Orders
        ddaa_orders = env['purchase.order'].search([
            ('is_ddaa_order', '=', True),
            ('state', '=', 'draft')
        ])

        for order in ddaa_orders:
            lines = order.order_line.filtered(lambda l: not l.display_type).sorted(key=lambda l: l.sequence)
            lines = list(lines)
            for i, line in enumerate(lines):
                # Get the book product
                if line.product_id.producto_referencia:
                    product = line.product_id.producto_referencia[0]
                if product and product.is_book:
                    line.section_id = product.id
                    line.contact_type = env.ref('gestion_editorial.contact_type_author').id
                    line.start_date = order.date_order
                    next_lines = lines[i + 1:i + 3] 
                    for next_line in next_lines:
                        next_line.section_id = product.id                    

        _logger.info(f"### TOTAL DDAA ORDERS: {len(ddaa_orders)} ")

        if not sql.table_exists(cr, 'temp_authorship_product_backup'):
            _logger.info("## No se encontró tabla de backup, saltando post-migrate")
            return
        
        # Get backup data
        cr.execute("SELECT * FROM temp_authorship_product_backup ORDER BY id")
        backup_records = cr.dictfetchall()
        
        if not backup_records:
            _logger.info("## No hay datos de backup, saltando post-migrate")
            return
        
        # Create contact type for authors (default contact type) if not exists
        ext_id = "contact_type_author"
        existing = env.ref(f"gestion_editorial.{ext_id}", raise_if_not_found=False)
        if not existing:
            record = env['res.partner.type'].create({
                'name': 'Autora',
                'default_ddaa_percentage_books': 10,
                'default_ddaa_percentage_ebooks': 10,
            })
            env['ir.model.data'].create({
                'module': 'gestion_editorial',
                'name': ext_id,
                'model': 'res.partner.type',
                'res_id': record.id,
                'noupdate': True,
            })
            _logger.info("=== CREATED CONTACT TYPE AUTHOR ===")
        _logger.info("=== CONTACT TYPE AUTHOR WAS ALREADY CREATED ===")
        
        # Get contact type for authors
        author_type = env.ref('gestion_editorial.contact_type_author')
        author_type_id = author_type.id if author_type else None

        if author_type_id is None:
            raise ValueError("### No se pudo obtener el ID del contact_type 'Autora'")

        _logger.info(f"=== AUTHOR ID = {author_type_id} ===")
        
        books_migrated = 0
        errors = []

        # Clear existing records
        env['authorship.product'].search([]).unlink()

        books = [record for record in backup_records if record['is_book']]

        _logger.info(f"=== MIGRATING AUTHORSHIPS ===")

        # First books then DDAA products
        for backup_record in books:
            try:
                product_id = backup_record['product_id']
                books_migrated += 1
                
                author = env['res.partner'].browse(backup_record['author_id'])
                product = env['product.template'].browse(product_id)
                
                if not author.exists():
                    errors.append(f"Autor ID {backup_record['author_id']} no existe")
                    continue
                if not product.exists():
                    errors.append(f"Producto ID {backup_record['product_id']} no existe")
                    continue
                
                existing_authorship = env['authorship.product'].search([
                    ('author_id', '=', backup_record['author_id']),
                    ('product_id', '=', product_id),
                    ('contact_type', '=', author_type_id),
                ])
                
                if not existing_authorship:
                    authorship_vals = {
                        'author_id': backup_record['author_id'],
                        'product_id': product_id,
                        'contact_type': author_type_id,
                        'sales_price': backup_record['price']
                    }

                    if product.derecho_autoria:
                        if product.derecho_autoria.list_price <= 0:
                            authorship_vals['ddaa_percentage'] = 0
                        else:
                            ddaa_percentage = product.derecho_autoria.list_price / product.list_price * 100
                            authorship_vals['ddaa_percentage'] = ddaa_percentage

                    env['authorship.product'].create(authorship_vals)
                    
            except Exception as e:
                error_msg = f"Error procesando registro: {authorship_vals}: {str(e)}"
                errors.append(error_msg)
                continue
        
        original_count = len(backup_records)
        
        _logger.info(f"=== RESUMEN DE MIGRACIÓN ===")
        _logger.info(f"Registros originales: {original_count}")
        _logger.info(f"Registros (libros): {books_migrated}")
        _logger.info(f"Errores: {len(errors)}")
        
        if errors:
            _logger.warning("=== ERRORES ENCONTRADOS ===")
            for error in errors[:10]:  # Show up to 10 errors
                _logger.warning(error)
        
        # # Opcional: Limpiar tabla temporal 
        # # cr.execute("DROP TABLE IF EXISTS temp_authorship_product_backup")

    except Exception as e:
        _logger.error(f"Error en post-migrate: {str(e)}")
        raise
    
    _logger.info("=== POST-MIGRATE COMPLETADO ===")