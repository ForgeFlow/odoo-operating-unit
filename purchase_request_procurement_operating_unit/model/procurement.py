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
from openerp.osv import orm


class Procurement(orm.Model):
    _inherit = 'procurement.order'

    def _prepare_purchase_request(self, cr, uid, procurement, context=None):
        res = super(Procurement, self)._prepare_purchase_request(
                cr, uid, procurement, context=context)
        if procurement.location_id.operating_unit_id:
            res.update({
                'operating_unit_id':
                    procurement.location_id.operating_unit_id.id
            })
        return res

    def _check_purchase_request_operating_unit(self, cr, uid, ids,
                                               context=None):
        for pr in self.browse(cr, uid, ids, context=context):
            if pr.request_id and pr.location_id.operating_unit_id and \
                            pr.request_id.operating_unit_id != \
                            pr.location_id.operating_unit_id:
                return False
        return True

    _constraints = [
        (_check_purchase_request_operating_unit,
         'The Purchase Request and the Procurement Order must '
         'belong to the same Operating Unit.', ['operating_unit_id',
                                                'purchase_id'])]
