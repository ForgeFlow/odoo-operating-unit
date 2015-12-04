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


class PurchaseOrder(orm.Model):

    _inherit = 'purchase.order'

    _columns = {
        'operating_unit_id': fields.many2one('operating.unit',
                                             'Operating Unit'),
        'requesting_operating_unit_id': fields.many2one(
            'operating.unit', 'Requesting Operating Unit'),
    }

    _defaults = {
        'operating_unit_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').operating_unit_default_get(cr, uid, uid, context=c),
        'requesting_operating_unit_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').operating_unit_default_get(cr, uid, uid, context=c),
    }

    def _check_warehouse_operating_unit(self, cr, uid, ids, context=None):
        for po in self.browse(cr, uid, ids, context=context):
            if po.warehouse_id and \
                    po.warehouse_id.operating_unit_id != po.operating_unit_id:
                return False
        return True

    def _check_company_operating_unit(self, cr, uid, ids, context=None):
        for po in self.browse(cr, uid, ids, context=context):
            if po.company_id and \
                    po.operating_unit_id and \
                    po.company_id != po.operating_unit_id.company_id:
                return False
        return True

    _constraints = [
        (_check_warehouse_operating_unit,
         'The Quotation / Purchase Order and the Warehouse must belong to '
         'the same Operating Unit.', ['operating_unit_id', 'warehouse_id']),
        (_check_company_operating_unit,
         'The Company in the Purchase Order and in the Operating '
         'Unit must be the same.', ['operating_unit_id',
                                    'requesting_operating_unit_id',
                                    'company_id']),
        (_check_company_operating_unit,
         'The Company in the Purchase Order and in the Requesting Operating '
         'Unit must be the same.', ['requesting_operating_unit_id',
                                    'company_id'])]

    def onchange_warehouse_id(self, cr, uid, ids, warehouse_id,
                              requesting_operating_unit_id, operating_unit_id):
        res = super(PurchaseOrder, self).onchange_warehouse_id(
            cr, uid, ids, warehouse_id)
        if not res:
            return {}
        location_obj = self.pool['stock.location']
        if requesting_operating_unit_id and operating_unit_id:
            request_location_ids = location_obj.search(
                cr, uid, [('operating_unit_id', '=',
                           requesting_operating_unit_id)], context=None)
            location_ids = location_obj.search(
                cr, uid, [('operating_unit_id', '=', operating_unit_id),
                          ('chained_location_id', 'in',
                           tuple(request_location_ids))], limit=1,
                context=None)
            if location_ids:
                res['value']['location_id'] = location_ids[0]
        return res

    def onchange_operating_unit_id(self, cr, uid, ids,
                                   requesting_operating_unit_id,
                                   operating_unit_id, context=None):
        # Obtain the default warehouse for the new operating unit
        if context is None:
            context = {}
        res = {'value': {}}
        warehouse_obj = self.pool['stock.warehouse']

        if operating_unit_id:
            warehouse_ids = warehouse_obj.search(cr, uid,
                                                 [('operating_unit_id', '=',
                                                   operating_unit_id)],
                                                 limit=1, context=context)
            if warehouse_ids:
                res['value']['warehouse_id'] = warehouse_ids[0]
                res_wh = self.onchange_warehouse_id(
                    cr, uid, ids, warehouse_ids[0],
                    requesting_operating_unit_id, operating_unit_id)
                if 'value' in res_wh:
                    res['value'].update(res_wh['value'])
        return res

    def action_invoice_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        inv_id = super(PurchaseOrder, self).action_invoice_create(
            cr, uid, ids, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            for invoice in order.invoice_ids:
                if order.operating_unit_id:
                    invoice_obj.write(
                        cr, uid, [invoice.id],
                        {'operating_unit_id': order.operating_unit_id.id},
                        context=context)
        return inv_id

    def _prepare_order_picking(self, cr, uid, order, context=None):
        if context is None:
            context = {}
        res = super(PurchaseOrder, self)._prepare_order_picking(
            cr, uid, order, context=context)
        if order.operating_unit_id:
            res['operating_unit_id'] = order.operating_unit_id.id
        return res


class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'

    _columns = {
        'operating_unit_id': fields.related(
            'order_id', 'operating_unit_id', type='many2one',
            relation='operating.unit', string='Operating Unit',
            readonly=True),
    }
