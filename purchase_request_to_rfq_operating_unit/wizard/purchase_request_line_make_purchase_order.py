# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
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
from openerp.tools.translate import _
from openerp.osv import fields, orm


class PurchaseRequestLineMakePurchaseOrder(orm.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    _columns = {
        'operating_unit_id': fields.many2one('operating.unit',
                                             'Operating Unit',
                                             readonly=True,
                                             required=True),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(PurchaseRequestLineMakePurchaseOrder, self).default_get(
            cr, uid, fields, context=context)
        request_line_obj = self.pool['purchase.request.line']
        request_line_ids = context.get('active_ids', [])
        operating_unit_id = False
        for line in request_line_obj.browse(cr, uid, request_line_ids,
                                            context=context):
            line_operating_unit_id = line.request_id.operating_unit_id \
                and line.request_id.operating_unit_id.id or False
            if operating_unit_id is not False \
                    and line_operating_unit_id != operating_unit_id:
                raise orm.except_orm(
                    _('Could not process !'),
                    _('You have to select lines '
                      'from the same operating unit.'))
            else:
                operating_unit_id = line_operating_unit_id
        res['operating_unit_id'] = operating_unit_id

        return res

    def _prepare_purchase_order(self, cr, uid, make_purchase_order,
                                warehouse_id, company_id,
                                context=None):
        data = super(PurchaseRequestLineMakePurchaseOrder,
                     self)._prepare_purchase_order(
            cr, uid, make_purchase_order, warehouse_id, company_id,
            context=context)
        data['requesting_operating_unit_id'] = \
            make_purchase_order.operating_unit_id.id
        data['operating_unit_id'] = \
            make_purchase_order.operating_unit_id.id
        return data
