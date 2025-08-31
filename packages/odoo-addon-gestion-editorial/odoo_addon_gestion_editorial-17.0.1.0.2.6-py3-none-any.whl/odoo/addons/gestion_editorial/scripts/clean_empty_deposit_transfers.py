import odoo
import logging

_logger = logging.getLogger(__name__)

# This script remove empty buggy transfers generated from old deposit sales operations
# Use this once in databases older than version 13.0.0.10.0

odoo.tools.config.parse_config([])
db_names = odoo.service.db.list_dbs()

if not db_names:
    raise ValueError("No database found.")

for db_name in db_names:
    _logger.info(f"### STARTING SCRIPT IN DATABASE: {db_name}")
    with odoo.api.Environment.manage():
        registry = odoo.registry(db_name)
        with registry.cursor() as cr:
            env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

            transfers = env['stock.picking'].search([
                ('state', '=', 'confirmed'),
                ('origin', 'ilike', 'S%'),
                ('location_id', '=', env.company.location_venta_deposito_id.id),
                ('location_dest_id', '=', env.ref("stock.stock_location_customers").id),
                ('picking_type_id', '=', env.ref('stock.picking_type_out').id),
                ('move_line_ids_without_package', '=', False)
                ])

            for transfer in transfers:
                print(f"Transfer ID: {transfer.id} - {transfer.name}")

            transfers.unlink()

            _logger.info(f"### FINISHED SCRIPT IN DATABASE: {db_name}")
            _logger.info(f"### TOTAL TRANSFERS: {len(transfers)} ")

            env.cr.commit()
