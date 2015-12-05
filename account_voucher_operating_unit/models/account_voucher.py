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
        'writeoff_operating_unit_id': fields.many2one(
            'operating.unit', 'Write-off Operating Unit', required=False),
    }

    _defaults = {
        'operating_unit_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').operating_unit_default_get(cr, uid, uid, context=c),
    }

    def _check_company_operating_unit(self, cr, uid, ids, context=None):
        for r in self.browse(cr, uid, ids, context=context):
            if r.company_id and r.operating_unit_id and \
                            r.company_id != r.operating_unit_id.company_id:
                return False
        return True

    def _check_journal_account_operating_unit(self, cr, uid, ids,
                                              context=None):
        for r in self.browse(cr, uid, ids, context=context):
            if r.type not in ('payment', 'receipt'):
                return True
            if (
                r.journal_id and r.operating_unit_id and
                r.journal_id.default_debit_account_id and
                r.journal_id.default_debit_account_id.operating_unit_id and
                r.journal_id.default_debit_account_id.operating_unit_id.id !=
                    r.operating_unit_id.id
            ):
                return False

            if (
                r.journal_id and r.operating_unit_id and
                r.journal_id.default_credit_account_id and
                r.journal_id.default_credit_account_id.operating_unit_id and
                r.journal_id.default_credit_account_id.operating_unit_id.id !=
                    r.operating_unit_id.id
            ):
                return False

        return True

    _constraints = [
        (_check_company_operating_unit,
         'The Company in the Move Line and in the '
         'Operating Unit must be the same.', ['operating_unit_id',
                                              'company_id']),
        (_check_journal_account_operating_unit,
         'The Default Debit and Credit Accounts defined in the Journal '
         'must have the same Operating Unit as the one indicated in the '
         'payment or receipt.',
         ['operating_unit_id', 'journal_id', 'type'])
    ]

    def first_move_line_get(self, cr, uid, voucher_id, move_id,
                            company_currency, current_currency, context=None):
        res = super(AccountVoucher, self).first_move_line_get(
            cr, uid, voucher_id, move_id, company_currency, current_currency,
            context=context)
        voucher = self.pool['account.voucher'].browse(cr, uid, voucher_id,
                                                      context)
        if not voucher.operating_unit_id:
            return res
        if voucher.type in ('payment', 'receipt'):
            if voucher.account_id.operating_unit_id:
                res['operating_unit_id'] = \
                    voucher.account_id.operating_unit_id.id
            else:
                raise orm.except_orm(_('Error!'),
                                     _('Account %s - %s does not have a '
                                       'default operating unit. \n '
                                       'Payment Method %s default Debit and '
                                       'Credit accounts should have a '
                                       'default Operating Unit.') %
                                     (voucher.account_id.code,
                                      voucher.account_id.name,
                                      voucher.journal_id.name))
        else:
            if voucher.operating_unit_id:
                res['operating_unit_id'] = voucher.operating_unit_id.id
            else:
                raise orm.except_orm(_('Error!'),
                                     _('The Voucher must have an Operating '
                                       'Unit.'))
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

        if line.voucher_id.type in ('sale', 'purchase') \
                and line.voucher_id.operating_unit_id:
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


class AccountVoucherLine(orm.Model):
    _inherit = "account.voucher.line"

    _columns = {
        'operating_unit_id': fields.related(
            'voucher_id', 'operating_unit_id', type='many2one',
            relation='operating.unit', string='Operating Unit', readonly=True)
    }
