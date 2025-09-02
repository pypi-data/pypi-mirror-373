import odoo
import logging

_logger = logging.getLogger(__name__)

odoo.tools.config.parse_config([])
db_names = odoo.service.db.list_dbs()

if not db_names:
    raise ValueError("No database found.")

for db_name in db_names:
    print("### CLEANING CACHE IN DATABASE: ", db_name)
    registry = odoo.registry(db_name)
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
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