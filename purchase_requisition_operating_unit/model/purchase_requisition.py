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
from openerp.tools.translate import _


class PurchaseRequisition(orm.Model):

    _inherit = 'purchase.requisition'

    _columns = {
        'operating_unit_id': fields.many2one('operating.unit',
                                             'Operating Unit', required=True),
    }

    _defaults = {
        'operating_unit_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').operating_unit_default_get(cr, uid, uid, context=c),
    }

    def _check_company_operating_unit(self, cr, uid, ids, context=None):
        for pr in self.browse(cr, uid, ids, context=context):
            if pr.company_id and \
                    pr.company_id != pr.operating_unit_id.company_id:
                return False
        return True

    _constraints = [
        (_check_company_operating_unit,
         'The Company in the Purchase Requisition and in the Operating '
         'Unit must be the same.', ['operating_unit_id',
                                    'company_id'])]

    def make_purchase_order(self, cr, uid, ids, partner_id,
                            context=None):
        if context is None:
            context = {}
        res = super(PurchaseRequisition, self).make_purchase_order(
            cr, uid, ids, partner_id, context=context)

        po_obj = self.pool['purchase.order']
        warehouse_obj = self.pool['stock.warehouse']

        for requisition in self.browse(cr, uid, ids, context=context):
            po_req = po_obj.search(cr, uid,
                                   [('requisition_id', '=', requisition.id)],
                                   context=context)
            for po in po_obj.browse(cr, uid, po_req):
                whs_ids = warehouse_obj.search(
                    cr, uid, [('operating_unit_id', '=',
                               requisition.operating_unit_id.id)])
                if not whs_ids:
                    raise orm.except_orm(
                        _('Error!'),
                        _("No warehouse exists for this Operating Unit."))
                whs = warehouse_obj.browse(cr, uid, whs_ids[0],
                                           context=context)
                po_obj.write(
                    cr, uid, [po.id],
                    {'operating_unit_id': requisition.operating_unit_id.id,
                     'warehouse_id': whs.id,
                     'location_id': whs.lot_input_id.id,
                     'dest_address_id': False
                     },
                    context=context)
        return res


class PurchaseRequisitionLine(orm.Model):
    _inherit = 'purchase.requisition.line'

    _columns = {
        'operating_unit_id': fields.related(
            'requisition_id', 'operating_unit_id', type='many2one',
            relation='operating.unit', string='Operating Unit',
            readonly=True),
    }
