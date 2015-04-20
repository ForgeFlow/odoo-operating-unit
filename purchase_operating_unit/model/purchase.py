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

from openerp.tools.translate import _
from openerp.osv import fields, orm
from openerp import SUPERUSER_ID, tools


class purchase_order(orm.Model):

    _inherit = 'purchase.order'

    _columns = {
        'operating_unit_id': fields.many2one('operating.unit',
                                             'Operating Unit', required=True),
    }

    _defaults = {
        'operating_unit_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').operating_unit_default_get(cr, uid, uid, context=c),
    }

    def _check_warehouse_operating_unit(self, cr, uid, ids, context=None):
        for po in self.browse(cr, uid, ids, context=context):
            if po.warehouse_id and \
                    po.warehouse_id.operating_unit_id != po.operating_unit_id:
                return False
        return True

    _constraints = [
        (_check_warehouse_operating_unit,
         'The Quotation / Purchase Order and the Warehouse must belong to '
         'the same Operating Unit.', ['operating_unit_id', 'warehouse_id'])]

    def action_invoice_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        inv_id = super(purchase_order, self).action_invoice_create(
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
        res = super(purchase_order, self)._prepare_order_picking(
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