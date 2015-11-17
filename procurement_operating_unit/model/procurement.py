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

    _columns = {
        'operating_unit_id': fields.many2one('operating.unit',
                                             'Operating Unit', required=True),
    }

    _defaults = {
        'operating_unit_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').operating_unit_default_get(cr, uid, uid, context=c),
    }

    def _check_stock_move_operating_unit(self, cr, uid, ids, context=None):
        for pr in self.browse(cr, uid, ids, context=context):
            if pr.move_id and \
                    pr.move_id.operating_unit_id != pr.operating_unit_id:
                return False
        return True

    def _check_location_operating_unit(self, cr, uid, ids, context=None):
        for pr in self.browse(cr, uid, ids, context=context):
            if pr.move_id and \
                    pr.move_id.operating_unit_id != pr.operating_unit_id:
                return False
        return True

    def _check_company_operating_unit(self, cr, uid, ids, context=None):
        for pr in self.browse(cr, uid, ids, context=context):
            if pr.company_id and \
                    pr.company_id != pr.operating_unit_id.company_id:
                return False
        return True

    _constraints = [
        (_check_stock_move_operating_unit,
         'The Stock Move and the Procurement Order must '
         'belong to the same Operating Unit.', ['operating_unit_id',
                                                'move_id']),
        (_check_location_operating_unit,
         'The Location and the Procurement Order must '
         'belong to the same Operating Unit.', ['operating_unit_id',
                                                'location_id']),
        (_check_company_operating_unit,
         'The Company in the Procurement Order in the '
         'Operating Unit must be the same.', ['operating_unit_id',
                                              'company_id'])
    ]
