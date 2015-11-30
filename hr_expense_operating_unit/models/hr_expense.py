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


class HrExpenseExpense(orm.Model):

    _inherit = 'hr.expense.expense'

    _columns = {
        'operating_unit_id': fields.many2one('operating.unit',
                                             'Operating Unit', required=True),
    }

    _defaults = {
        'operating_unit_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').operating_unit_default_get(cr, uid, uid, context=c),
    }

    def account_move_get(self, cr, uid, expense_id, context=None):
        res = super(HrExpenseExpense, self).account_move_get(cr, uid,
                                                             expense_id,
                                                             context=context)
        expense = self.browse(cr, uid, expense_id, context=context)
        if expense.operating_unit_id:
            res['operating_unit_id'] = expense.operating_unit_id.id
        return res
