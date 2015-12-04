# -*- coding: utf-8 -*-
# Authors: Jordi Ballester Alomar
# Copyright 2015 Eficent (http://www.eficent.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public Lice
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from openerp.osv import orm, fields
from openerp.tools.translate import _


class stock_warehouse(orm.Model):
    _inherit = "stock.warehouse"
    _columns = {
        'operating_unit_id': fields.many2one('operating.unit',
                                             'Operating Unit'),
    }

    _defaults = {
        'operating_unit_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').operating_unit_default_get(cr, uid, uid, context=c),
    }


class stock_location(orm.Model):
    _inherit = 'stock.location'

    _columns = {
        'operating_unit_id': fields.many2one('operating.unit',
                                             'Operating Unit'),
    }

    def _check_warehouse_operating_unit(self, cr, uid, ids, context=None):
        warehouse_obj = self.pool.get('stock.warehouse')
        for l in self.browse(cr, uid, ids, context=context):
            w_ids = warehouse_obj.search(cr, uid, [('lot_input_id', '=',
                                                   l.id)], context=context)
            for w in warehouse_obj.browse(cr, uid, w_ids, context=context):
                if l.operating_unit_id != w.operating_unit_id:
                    return False
            w_ids = warehouse_obj.search(cr, uid, [('lot_stock_id', '=',
                                                   l.id)], context=context)
            for w in warehouse_obj.browse(cr, uid, w_ids, context=context):
                if l.operating_unit_id != w.operating_unit_id:
                    return False
            w_ids = warehouse_obj.search(cr, uid, [('lot_output_id', '=',
                                                   l.id)], context=context)
            for w in warehouse_obj.browse(cr, uid, w_ids, context=context):
                if l.operating_unit_id != w.operating_unit_id:
                    return False
        return True

    def _check_required_operating_unit(self, cr, uid, ids, context=None):
        for l in self.browse(cr, uid, ids, context=context):
            if l.usage == 'internal' and not l.operating_unit_id:
                return False
            if l.usage != 'internal' and l.operating_unit_id:
                return False
        return True

    def _check_company_operating_unit(self, cr, uid, ids, context=None):
        for sl in self.browse(cr, uid, ids, context=context):
            if sl.company_id and sl.operating_unit_id and \
                    sl.company_id != sl.operating_unit_id.company_id:
                return False
        return True

    def _check_parent_operating_unit(self, cr, uid, ids, context=None):
        for sl in self.browse(cr, uid, ids, context=context):
            if (
                sl.location_id and
                sl.location_id.usage == 'internal' and
                sl.operating_unit_id and
                sl.operating_unit_id != sl.location_id.operating_unit_id
            ):
                return False
        return True

    _constraints = [
        (_check_warehouse_operating_unit,
         'This location is assigned to a warehouse that belongs to a '
         'different operating unit.', ['operating_unit_id']),
        (_check_required_operating_unit,
         'The operating unit should be assigned to internal locations, '
         'and to non other.', ['operating_unit_id']),
        (_check_company_operating_unit,
         'The Company in the Stock Location and in the Operating '
         'Unit must be the same.', ['operating_unit_id',
                                    'company_id']),
        (_check_parent_operating_unit,
         'The Parent Stock Location must belong to the same Operating Unit.',
         ['operating_unit_id', 'location_id'])]


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    _columns = {
        'operating_unit_id': fields.many2one(
            'operating.unit', string='Requesting Operating Unit'),
    }

    _defaults = {
        'operating_unit_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').operating_unit_default_get(cr, uid, uid, context=c),

    }

    def _check_company_operating_unit(self, cr, uid, ids, context=None):
        for sp in self.browse(cr, uid, ids, context=context):
            if sp.company_id and sp.operating_unit_id and \
                    sp.company_id != sp.operating_unit_id.company_id:
                return False
        return True

    def _check_stock_move_operating_unit(self, cr, uid, ids, context=None):
        for sp in self.browse(cr, uid, ids, context=context):
            if not sp.operating_unit_id:
                return True
            for sm in sp.move_lines:
                if (
                    sm.location_id and
                    sm.location_id.operating_unit_id and
                    sp.operating_unit_id != sm.location_id.operating_unit_id
                ) and (
                    sm.location_dest_id and
                    sm.location_dest_id.operating_unit_id and
                    sp.operating_unit_id != sm.location_dest_id.operating_unit_id
                ):
                    return False
        return True

    _constraints = [
        (_check_company_operating_unit,
         'The Company in the Stock Picking and in the Operating '
         'Unit must be the same.', ['operating_unit_id',
                                    'company_id']),
        (_check_stock_move_operating_unit,
         'The Stock moves must be related to a location (source or '
         'destination) that belongs to the requesting Operating Unit.',
         ['operating_unit_id', 'move_lines'])
    ]

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id,
                         context=None):
        invoice_vals = super(stock_picking, self)._prepare_invoice(
            cr, uid, picking, partner, inv_type, journal_id, context=context)
        if picking.operating_unit_id:
            invoice_vals['operating_unit_id'] = \
                picking.operating_unit_id.id
        return invoice_vals


class stock_picking_in(orm.Model):

    _inherit = "stock.picking.in"

    def __init__(self, pool, cr):
        super(stock_picking_in, self).__init__(pool, cr)
        self._columns['operating_unit_id'] = \
            self.pool['stock.picking']._columns['operating_unit_id']


class stock_picking_out(orm.Model):

    _inherit = "stock.picking.out"

    def __init__(self, pool, cr):
        super(stock_picking_out, self).__init__(pool, cr)
        self._columns['operating_unit_id'] = \
            self.pool['stock.picking']._columns['operating_unit_id']


class stock_move(orm.Model):
    _inherit = 'stock.move'

    _columns = {
        'operating_unit_id': fields.related(
            'location_id', 'operating_unit_id', type='many2one',
            relation='operating.unit', string='Source Location Operating Unit',
            readonly=True),
        'operating_unit_dest_id': fields.related(
            'location_dest_id', 'operating_unit_id', type='many2one',
            relation='operating.unit', string='Dest. Location Operating Unit',
            readonly=True),

    }
