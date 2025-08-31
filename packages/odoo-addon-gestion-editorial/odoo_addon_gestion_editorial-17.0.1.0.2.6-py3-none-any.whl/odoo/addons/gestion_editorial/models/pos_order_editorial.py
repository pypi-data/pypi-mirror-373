from odoo import models, api

class EditorialPosOrder(models.Model):
    """ Extend pos.order for editorial management """

    _description = "Editorial POS Order"
    _inherit = 'pos.order'

    @api.model
    def create(self, vals):
        order = super(EditorialPosOrder, self).create(vals)
        order.generate_pos_ddaa()
        return order
    
    # Extend refund POS function for generate negative DDAA
    def refund(self):
        result = super(EditorialPosOrder, self).refund()

        book_lines = self.lines.filtered(lambda line: self.env.company.is_category_genera_ddaa_or_child(line.product_id.categ_id))
        for line in book_lines:
            line.product_id.product_tmpl_id.generate_ddaa(-line.qty)

        return result


    def generate_pos_ddaa(self):
        if not self.env.company.module_editorial_ddaa:
            return

        book_lines = self.lines.filtered(lambda line: self.env.company.is_category_genera_ddaa_or_child(line.product_id.categ_id))
        for line in book_lines:
            line.product_id.product_tmpl_id.generate_ddaa(line.qty)
 