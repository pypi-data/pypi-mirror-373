import logging
from odoo import models, fields
from odoo.tools.translate import _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class DDAAAuthorshipCondition(models.Model):
    _name = "ddaa.authorship.condition"
    _description = "Condiciones de DDAA para una autoría específica"

    authorship = fields.Many2one(comodel_name="authorship.product", string="Authorship", required=True, ondelete="cascade")
    min_qty = fields.Integer(string=_("Min. Quantity"), required=False)
    ddaa_percentage = fields.Float(string=_("DDAA percentage"), required=True)

    def create(self, values):
        for value in values:
            min_qty = value.get("min_qty")
            count = self.search_count([("min_qty", "=", min_qty), ("authorship", "=", value.get("authorship"))])
            if count > 0:
                raise ValidationError(_("Registro duplicado (%s) \nNo puede haber más de un registro con el mismo valor de cantidad mínima.") % min_qty)

        return super(DDAAAuthorshipCondition, self).create(values)


    def write(self, values):
        min_qty = values.get("min_qty")
        if min_qty:
            if self.min_qty == 0 and min_qty != 0:
                raise ValidationError(_("No puedes modificar el valor por defecto."))

            count = self.search_count([("min_qty", "=", min_qty), ("authorship", "=", self.authorship.id)])
            if count > 0:
                raise ValidationError(_("Registro duplicado (%s) \nNo puede haber más de un registro con el mismo valor de cantidad mínima.") % min_qty)

        return super(DDAAAuthorshipCondition, self).write(values)

    def unlink(self):
        existing_records = self.search_count([("min_qty", "=", 0), ("authorship", "=", self.authorship.id)])
        deleted_records = sum(record.min_qty == 0 for record in self)
        if existing_records - deleted_records == 0:
            raise ValidationError(_("No puedes eliminar el valor por defecto."))

        return super(DDAAAuthorshipCondition, self).unlink()