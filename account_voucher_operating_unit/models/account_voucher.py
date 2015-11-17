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
                                             'Operating Unit', required=False),
        'writeoff_operating_unit_id': fields.many2one(
            'operating.unit', 'Write-off Operating Unit', required=False),
    }

    def first_move_line_get(self, cr, uid, voucher_id, move_id,
                            company_currency, current_currency, context=None):
        res = super(AccountVoucher, self).first_move_line_get(
            cr, uid, voucher_id, move_id, company_currency, current_currency,
            context=context)
        voucher = self.pool['account.voucher'].browse(cr, uid, voucher_id,
                                                      context)
        if voucher.operating_unit_id:
            res['operating_unit_id'] = voucher.operating_unit_id.id

        else:
            if not voucher.account_id:
                orm.except_orm(_('Error!',
                                 _('Account %s does not have a '
                                   'default operating unit.') %
                                 voucher.account_id.code))
            else:
                res['operating_unit_id'] = \
                    voucher.account_id.operating_unit_id.id
        return res

    def _voucher_move_line_prepare(self, cr, uid, voucher_id, line_total,
                                   move_id, company_currency, current_currency,
                                   voucher_line_id, context=None):
        res = super(AccountVoucher, self)._voucher_move_line_prepare(
            cr, uid, voucher_id, line_total, move_id, company_currency,
            current_currency, voucher_line_id, context=context)
        line = self.pool['account.voucher.line'].browse(cr, uid,
                                                        voucher_line_id,
                                                        context=context)
        if line.voucher_id.operating_unit_id:
            res['operating_unit_id'] = line.voucher_id.operating_unit_id.id
        elif line.move_line_id and line.move_line_id.operating_unit_id:
            res['operating_unit_id'] = line.move_line_id.operating_unit_id.id
        return res

    def _voucher_move_line_foreign_currency_prepare(
            self, cr, uid, voucher_id, line_total, move_id,
            company_currency, current_currency, voucher_line_id,
            foreign_currency_diff, context=None):

        res = super(AccountVoucher, self)._voucher_move_line_prepare(
            cr, uid, voucher_id, line_total, move_id, company_currency,
            current_currency, voucher_line_id, foreign_currency_diff,
            context=context)
        line = self.pool['account.voucher.line'].browse(cr, uid,
                                                        voucher_line_id,
                                                        context=context)
        if line.move_line_id and line.move_line_id.operating_unit_id:
            res['operating_unit_id'] = line.move_line_id.operating_unit_id.id
        return res

    def writeoff_move_line_get(self, cr, uid, voucher_id,
                               line_total, move_id, name,
                               company_currency, current_currency,
                               context=None):
        res = super(AccountVoucher, self).writeoff_move_line_get(
            cr, uid, voucher_id, line_total, move_id, name, company_currency,
            current_currency, context=context)
        if res:
            voucher = self.pool['account.voucher'].browse(cr, uid,
                                                          voucher_id, context)
            if (voucher.payment_option == 'with_writeoff' or
                    voucher.partner_id):
                if not voucher.writeoff_operating_unit_id:
                    orm.except_orm(_('Error!',
                                   _('Please indicate a write-off Operating '
                                     'Unit.')))
                else:
                    res['operating_unit_id'] = \
                        voucher.writeoff_operating_unit_id.id
            else:
                if not voucher.writeoff_operating_unit_id:
                    if not voucher.account_id.operating_unit_id:
                        orm.except_orm(_('Error!',
                                       _('Please indicate a write-off '
                                         'Operating Unit or a default '
                                         'Operating Unit for account %s') %
                                         voucher.account_id.code))
                    else:
                        res['operating_unit_id'] = \
                                voucher.account_id.operating_unit_id.id
                else:
                        res['operating_unit_id'] = \
                                voucher.writeoff_operating_unit_id.id

        return res
