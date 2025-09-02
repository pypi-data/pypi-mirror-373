from odoo import models


class EditorialProducts(models.Model):
    """ Extend stock location for editorial management """

    _description = "Editorial Stock Location"
    _inherit = 'stock.location'

    def get_all_child_locations(self):
        child_locations = self.child_ids
        location_ids = [self.id] + [child.id for child in child_locations]
        for child_location in child_locations:
            location_ids += child_location.get_all_child_locations()

        return location_ids
