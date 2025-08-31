import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    _logger.info("=== INICIANDO PRE-MIGRATE SCRIPT ===")
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    try:
        cr.execute("""
            SELECT id, author_id, product_id, price
            FROM authorship_product
        """)
        authorship_records = cr.fetchall()
        
        if not authorship_records:
            _logger.info("## No hay registros en authorship.product, saltando pre-migrate")
            return
        
        backup_data = []
        books_count = 0
        ddaa_products_count = 0
        
        for rec in authorship_records:
            record_id, author_id, product_id, price = rec

            product = env['product.template'].browse(product_id)
            author = env['res.partner'].browse(author_id)

            is_book = (
                product.categ_id.id == env.ref("gestion_editorial.product_category_books").id 
                or product.categ_id.id == env.ref("gestion_editorial.product_category_digital_books").id
                or product.categ_id.parent_id.id == env.ref("gestion_editorial.product_category_books").id
                or product.categ_id.parent_id.id == env.ref("gestion_editorial.product_category_digital_books").id
            )

            backup_record = {
                'id': record_id,
                'author_id': author_id,
                'product_id': product_id,
                'price': price,
                'is_book': is_book,
                'product_name': product.name,
                'author_name': author.name,
                'category_name': product.categ_id.name if product.categ_id else 'Sin categoría'
            }
            backup_data.append(backup_record)
            
            if is_book:
                books_count += 1
            else:
                ddaa_products_count += 1
        
        # Create temp table for backup
        cr.execute("""
            CREATE TABLE IF NOT EXISTS temp_authorship_product_backup (
                id INTEGER,
                author_id INTEGER,
                product_id INTEGER,
                price FLOAT,
                is_book BOOLEAN,
                product_name VARCHAR,
                author_name VARCHAR
            )
        """)
        
        cr.execute("DELETE FROM temp_authorship_product_backup")
        
        # Insert data into temp table
        for backup_record in backup_data:
            cr.execute("""
                INSERT INTO temp_authorship_product_backup 
                (id, author_id, product_id, price, is_book, 
                product_name, author_name)
                VALUES (%(id)s, %(author_id)s, %(product_id)s, %(price)s, %(is_book)s, 
                        %(product_name)s, %(author_name)s)
            """, backup_record)
        
        total_records = len(authorship_records)
        
        _logger.info(f"Respaldo creado: {total_records} registros totales")
        _logger.info(f"Productos tipo libro: {books_count}")
        _logger.info(f"Productos tipo DDAA: {ddaa_products_count}")
 
    except Exception as e:
        _logger.error(f"Error en pre-migrate: {str(e)}")
        raise
    
    _logger.info("=== PRE-MIGRATE COMPLETADO ===")