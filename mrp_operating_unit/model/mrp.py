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


class MrpProduction(orm.Model):

    _inherit = 'mrp.production'

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
         'The Company in the Manufacturing Order and in the Operating '
         'Unit must be the same.', ['operating_unit_id',
                                    'company_id'])]



class PurchaseRequisitionLine(orm.Model):
    _inherit = 'purchase.requisition.line'

    _columns = {
        'operating_unit_id': fields.related(
            'requisition_id', 'operating_unit_id', type='many2one',
            relation='operating.unit', string='Operating Unit',
            readonly=True),
    }
