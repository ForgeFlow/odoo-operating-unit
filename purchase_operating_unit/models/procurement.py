# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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

    def create_procurement_purchase_order(self, cr, uid, procurement, po_vals,
                                          line_vals, context=None):
        if procurement.location_id.operating_unit_id:
            po_vals.update({
                'operating_unit_id':
                    procurement.location_id.operating_unit_id.id,
                'requesting_operating_unit_id':
                    procurement.location_id.operating_unit_id.id
            })
        return super(ProcurementOrder, self).\
            create_procurement_purchase_order(cr, uid, procurement, po_vals,
                                              line_vals, context=context)
