# -*- coding: utf-8 -*-
# © 2015 Eficent - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.osv import fields, orm


class ProcurementOrder(orm.Model):

    _inherit = 'procurement.order'

    def _check_purchase_order_operating_unit(self, cr, uid, ids, context=None):
        for pr in self.browse(cr, uid, ids, context=context):
            if pr.purchase_id and \
                    pr.purchase_id.operating_unit_id != \
                    pr.location_id.operating_unit_id:
                return False
        return True

    _constraints = [
        (_check_purchase_order_operating_unit,
         'The Quotation / Purchase Order and the Procurement Order must '
         'belong to the same Operating Unit.', ['operating_unit_id',
                                                'purchase_id'])]

    def create_procurement_purchase_order(self, cr, uid, procurement, po_vals, line_vals, context=None):
        """Create the purchase order from the procurement, using
           the provided field values, after adding the given purchase
           order line in the purchase order.

           :params procurement: the procurement object generating the purchase order
           :params dict po_vals: field values for the new purchase order (the
                                 ``order_line`` field will be overwritten with one
                                 single line, as passed in ``line_vals``).
           :params dict line_vals: field values of the single purchase order line that
                                   the purchase order will contain.
           :return: id of the newly created purchase order
           :rtype: int
        """
        if procurement.location_id.operating_unit_id:
            line_vals.update({
                'operating_unit_id':
                    procurement.location_id.operating_unit_id.id,
                'requesting_operating_unit_id':
                    procurement.location_id.operating_unit_id.id
            })
        return super(ProcurementOrder, self).\
            create_procurement_purchase_order(cr, uid, procurement, po_vals,
                                              line_vals, context=context)
