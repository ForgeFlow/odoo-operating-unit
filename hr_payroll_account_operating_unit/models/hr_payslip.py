# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#               <jordi.ballester@eficent.com>
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


class HrPayslip(orm.Model):

    _inherit = 'hr.payslip'

    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {}
        move_obj = self.pool['account.move']
        res = super(HrPayslip, self).write(cr, uid, ids, vals, context=context)
        if 'move_id' in vals and vals['move_id']:
            for slip in self.browse(cr, uid, ids, context=context):
                if slip.contract_id and slip.contract_id.operating_unit_id:
                    move_obj.write(
                        cr, uid, [slip.move_id.id], {
                            'operating_unit_id':
                            slip.contract_id.operating_unit_id.id},
                        context=context)
        return res
