# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jordi Ballester (Eficent)
#    Copyright 2015 Eficent
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
from openerp.osv import orm, fields
from openerp.tools.translate import _


class AccountVoucher(orm.Model):
    _inherit = "account.voucher"

    _columns = {
        'operating_unit_id': fields.many2one('operating.unit',
                                             'Operating Unit'),
    }

    _defaults = {
        'operating_unit_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').operating_unit_default_get(cr, uid, uid, context=c),
    }

    def _check_company_operating_unit(self, cr, uid, ids, context=None):
        for av in self.browse(cr, uid, ids, context=context):
            if (
                av.company_id and
                av.operating_unit_id and
                av.company_id != av.operating_unit_id.company_id
            ):
                return False
        return True

    _constraints = [
        (_check_company_operating_unit,
         'The Company in the Voucher and in the Operating '
         'Unit must be the same.', ['operating_unit_id',
                                    'company_id'])]

    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        if not context:
            context = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.operating_unit_id:
                context.add()
            res = super(AccountVoucher, self).recompute_voucher_lines(
                cr, uid, [voucher.id], partner_id, journal_id, price,
                currency_id, ttype,
                date, context=context)


class AccountVoucherLine(orm.Model):
    _inherit = 'account.voucher.line'

    _columns = {
        'operating_unit_id': fields.related(
            'voucher_id', 'operating_unit_id', type='many2one',
            relation='operating.unit', string='Operating Unit',
            readonly=True),
    }

    def _check_move_line_operating_unit(self, cr, uid, ids, context=None):
        for avl in self.browse(cr, uid, ids, context=context):
            if (
                avl.operating_unit_id and
                avl.move_line_id and
                avl.operating_unit_id != avl.move_line_id.operating_unit_id
            ):
                return False
        return True

    _constraints = [
        (_check_move_line_operating_unit,
         'The Company in the Voucher and in the Operating '
         'Unit must be the same.', ['operating_unit_id',
                                    'company_id'])]
