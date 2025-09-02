from odoo import models, fields, api
from odoo.exceptions import ValidationError
from markupsafe import Markup
from odoo.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class EditorialAuthorshipProduct(models.Model):
    """ Editorial book contacts management """

    _description = 'Editorial book contacts information'
    _name = 'authorship.product'
    _rec_name = 'author_id'
    _sql_constraints = [('unique_authorship', 'unique(author_id, product_id, contact_type)',
                         '¡Autoría duplicada!\nEn un mismo libro no puede haber un contacto duplicado con el mismo rol.')]

    author_id = fields.Many2one(comodel_name="res.partner", required=True, ondelete="cascade")
    product_id = fields.Many2one(comodel_name="product.template", required=True, ondelete="cascade", index=True)
    contact_type = fields.Many2one(comodel_name='res.partner.type', required=True, string='Contact Type')
    ddaa_percentage = fields.Float(string='Porcentaje de regalías')
    sales_price = fields.Float(string='Precio de venta', default=0.0, help="Precio al que el contacto puede comprar el libro")
    is_main_entry = fields.Boolean(string="Relación principal para el precio de venta")
    # Special price for author if product is book
    # Amount received from DDAA if product is DDAA
    price = fields.Float(compute='_compute_ddaa_price', string='Importe de regalías')

    is_condition_active = fields.Boolean(string='Is Condition Active?', required=False)
    ddaa_conditions = fields.One2many(
        comodel_name='ddaa.authorship.condition',
        inverse_name='authorship',
        string='DDAA conditions',
        required=False)
    
    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res_type = self.env.ref("gestion_editorial.contact_type_author", raise_if_not_found=False)
        if res_type:
            res['contact_type'] = res_type.id

        return res
    
    def create(self, values):
        # Support both single record and multiple records creation
        if isinstance(values, dict):
            values = [values]

        group_author_product = {}
        for record in values:
            author_id = record.get('author_id')

            contact_type_id = record.get("contact_type")
            contact_type = self.env["res.partner.type"].browse(contact_type_id)

            product_id = record.get("product_id")
            product = self.env["product.template"].browse(product_id)

            if not record.get("ddaa_percentage"):
                record["ddaa_percentage"] = self._get_default_ddaa_precentage(product, contact_type)

            key = (author_id, product_id)
            # If we receive more than one record for the same author and product,
            # we set is_main_entry to False for all but the first one
            if key not in group_author_product:
                existing = self.search([
                    ('author_id', '=', key[0]),
                    ('product_id', '=', key[1]),
                    ('is_main_entry', '=', True)
                ], limit=1)

                if existing:
                    group_author_product[key] = True
                    record['is_main_entry'] = False
                else:
                    group_author_product[key] = True
                    record['is_main_entry'] = True
            else:
                record['is_main_entry'] = False

        res = super(EditorialAuthorshipProduct, self).create(values)
        res.create_default_ddaa_condition()
        return res
    
    def write(self, values):
        for record in self:
            ddaa_percentage_changed = values.get("ddaa_percentage") is not None and round(values.get("ddaa_percentage")) != round(self._origin.ddaa_percentage)
            contact_type_changed = values.get("contact_type") and values.get("contact_type") != self._origin.contact_type.id
            if ddaa_percentage_changed or contact_type_changed:
                contact_type = self.env["res.partner.type"].browse(values.get("contact_type")) or self._origin.contact_type
                self._origin.product_id.message_post(
                    body=Markup(f"""Se han modificado los datos de regalías para <b>{self._origin.author_id.name}</b>:<br>
                         <b>{self._origin.contact_type.name}</b> --> <b>{contact_type.name}</b><br>
                         <b>{round(self._origin.ddaa_percentage)}%</b> --> <b>{values.get('ddaa_percentage')}%</b>"""),
                    message_type="comment",
                    subtype_xmlid="mail.mt_note"
                )

            record.create_default_ddaa_condition()
        res = super(EditorialAuthorshipProduct, self).write(values)
        self.update_default_condition()
        return res

    @api.constrains('product_id', 'is_main_entry')
    def _check_unique_main_entry(self):
        for record in self:
            if record.is_main_entry:
                existing = self.search([
                    ('product_id', '=', record.product_id.id),
                    ('author_id', '=', record.author_id.id),
                    ('is_main_entry', '=', True),
                    ('id', '!=', record.id)
                ], limit=1)
                if existing:
                    raise ValidationError("Solo puede haber una relación principal por libro.")

    @api.onchange('contact_type')
    def _onchange_contact_type(self):
        self.ddaa_percentage = self._get_default_ddaa_precentage(self.product_id, self.contact_type)

    def _get_default_ddaa_precentage(self, product, contact_type):
        _logger.debug("_get_default_ddaa_percentage")
        default_ddaa_percentage = 0

        if product.is_physical_book():
            _logger.debug("Product is a pyshical book.")
            default_ddaa_percentage = contact_type.default_ddaa_percentage_books
        elif product.is_ebook():
            _logger.debug("Product is a digital book.")
            default_ddaa_percentage = contact_type.default_ddaa_percentage_ebooks

        _logger.debug(f"default_dda_percentage={default_ddaa_percentage}")
        return default_ddaa_percentage

    @api.depends('ddaa_percentage')
    def _compute_ddaa_price(self):
        for record in self:
            record.price = round(round(record.product_id.list_price, 2) * (record.ddaa_percentage / 100), 2)

    def create_default_ddaa_condition(self):
        for record in self:
            if not record.ddaa_conditions or 0 not in [condition.min_qty for condition in record.ddaa_conditions]:
                _logger.debug("Creating default DDAA % condition")
                self.env["ddaa.authorship.condition"].create([{
                    "authorship": record.id,
                    "min_qty": 0,
                    "ddaa_percentage": record.ddaa_percentage
                }])

    def action_open_product(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'product.template',
            'res_id': self.product_id.id,
        }

    def action_open_contact(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'res.partner',
            'res_id': self.author_id.id,
        }

    def update_ddaa_percentage_based_on_conditions(self):
        _logger.info(f"Checking if ddaa % should change for {self.author_id.name}")
        _logger.debug(f"liquidated_qty: {self.product_id.liquidated_qty}")
        matching_condition = max([condition for condition in self.ddaa_conditions if (self.product_id.liquidated_qty - condition.min_qty) >= 0], key=lambda x:x.min_qty, default=None)
        if matching_condition:
            _logger.debug(f"matching_condition.min_qty: {matching_condition.min_qty}")
            if matching_condition.ddaa_percentage != self.ddaa_percentage:
                _logger.info(f"Changing DDAA % because liquidated_qty ({self.product_id.liquidated_qty}) >= {matching_condition.min_qty}")
                _logger.info(f"{self.ddaa_percentage}% --> {matching_condition.ddaa_percentage}%")
                if matching_condition.ddaa_percentage >= self.ddaa_percentage:
                    self._origin.product_id.message_post(
                        body=Markup(_("Se ha superado el umbral de {0} ventas para <b>{1}</b>".format(matching_condition.min_qty, self.author_id.name))),
                        message_type="comment",
                        subtype_xmlid="mail.mt_note"
                    )
                else:
                    self._origin.product_id.message_post(
                        body=Markup(_("Se ha reducido el umbral de ventas para <b>{0}</b>".format(self.author_id.name))),
                        message_type="comment",
                        subtype_xmlid="mail.mt_note"
                    )

                self.is_condition_active = True
                self.ddaa_percentage = matching_condition.ddaa_percentage

    def update_default_condition(self):
        _logger.info("DDAA Percentage changed")
        for record in self:
            if not record.is_condition_active:
                base_condition = record.ddaa_conditions.filtered(lambda cond: cond.min_qty == 0)
                if base_condition:
                    base_condition.ddaa_percentage = record.ddaa_percentage

    def open_ddaa_conditions(self):
        return {
            "type": "ir.actions.act_window",
            "name": f"Condiciones de DDAA para {self.author_id.name}",
            "res_model": "authorship.product",
            "res_id": self.id,
            "view_mode": "form",
            "view_id": self.env.ref("gestion_editorial.view_ddaa_authorship_conditions_tree").id,
            "target": "new",
        }

    def generates_ddaa(self):
        return self.contact_type and self.ddaa_percentage > 0
