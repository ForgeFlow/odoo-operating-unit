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
from openerp.osv import orm
from openerp.tools.translate import _
from openerp.tools import float_compare


class AccountVoucher(orm.Model):
    _inherit = "account.voucher"

    def _voucher_move_line_prepare(self, cr, uid, voucher_id, line_total,
                                   move_id, company_currency, current_currency,
                                   voucher_line_id, context=None):

        voucher = self.pool['account.voucher'].browse(cr, uid, voucher_id,
                                                      context=context)
        line = self.pool['account.voucher.line'].browse(cr, uid,
                                                        voucher_line_id,
                                                        context=context)
        return {
            'journal_id': voucher.journal_id.id,
            'period_id': voucher.period_id.id,
            'name': line.name or '/',
            'account_id': line.account_id.id,
            'move_id': move_id,
            'partner_id': voucher.partner_id.id,
            'currency_id': line.move_line_id and
            (company_currency != line.move_line_id.currency_id.id and
             line.move_line_id.currency_id.id) or False,
            'analytic_account_id': line.account_analytic_id and
            line.account_analytic_id.id or False,
            'quantity': 1,
            'credit': 0.0,
            'debit': 0.0,
            'date': voucher.date
        }

    def _voucher_move_line_foreign_currency_prepare(
            self, cr, uid, voucher_id, line_total, move_id,
            company_currency, current_currency, voucher_line_id,
            foreign_currency_diff, context=None):

        line = self.pool['account.voucher.line'].browse(cr, uid,
                                                        voucher_line_id,
                                                        context=context)
        return {
            'journal_id': line.voucher_id.journal_id.id,
            'period_id': line.voucher_id.period_id.id,
            'name': _('change')+': '+(line.name or '/'),
            'account_id': line.account_id.id,
            'move_id': move_id,
            'partner_id': line.voucher_id.partner_id.id,
            'currency_id': line.move_line_id.currency_id.id,
            'amount_currency': -1 * foreign_currency_diff,
            'quantity': 1,
            'credit': 0.0,
            'debit': 0.0,
            'date': line.voucher_id.date,
        }

    def voucher_move_line_create(self, cr, uid, voucher_id, line_total,
                                 move_id, company_currency, current_currency,
                                 context=None):
        """
        This method replaces the original one in the account voucher module
        because it did not provide any hooks for customization.
        """
        if context is None:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        tot_line = line_total
        rec_lst_ids = []

        date = self.read(cr, uid, voucher_id, ['date'], context=context)['date']
        ctx = context.copy()
        ctx.update({'date': date})
        voucher = self.pool.get('account.voucher').browse(
            cr, uid, voucher_id, context=ctx)
        voucher_currency = voucher.journal_id.currency or \
            voucher.company_id.currency_id
        ctx.update({
            'voucher_special_currency_rate': voucher_currency.rate *
            voucher.payment_rate,
            'voucher_special_currency': voucher.payment_rate_currency_id and
            voucher.payment_rate_currency_id.id or False})
        prec = self.pool.get('decimal.precision').precision_get(cr, uid,
                                                                'Account')
        for line in voucher.line_ids:
            # create one move line per voucher line where amount is not 0.0
            # AND (second part of the clause) only if the original move line
            # was not having debit = credit = 0 (which is a legal value)
            if (
                not line.amount and
                not (
                    line.move_line_id and
                    not float_compare(line.move_line_id.debit,
                                      line.move_line_id.credit,
                                      precision_digits=prec) and
                    not float_compare(line.move_line_id.debit, 0.0,
                                      precision_digits=prec)
                )
            ):
                continue
            # convert the amount set on the voucher line into the currency
            # of the voucher's company
            # this calls res_curreny.compute() with the right context,
            # so that it will take either the rate on the voucher if it is
            # relevant or will use the default behaviour
            amount = self._convert_amount(cr, uid, line.untax_amount or
                                          line.amount, voucher.id, context=ctx)
            # if the amount encoded in voucher is equal to the amount
            # unreconciled, we need to compute the
            # currency rate difference
            if line.amount == line.amount_unreconciled:
                if not line.move_line_id:
                    raise orm.except_orm(_('Wrong voucher line'),
                                         _("The invoice you are willing to "
                                           "pay is not valid anymore."))
                sign = line.type == 'dr' and -1 or 1
                currency_rate_difference = sign * (
                    line.move_line_id.amount_residual - amount)
            else:
                currency_rate_difference = 0.0
            move_line = self._voucher_move_line_prepare(
                cr, uid, voucher_id, line_total, move_id, company_currency,
                current_currency, line.id, context=context)

            if amount < 0:
                amount = -amount
                if line.type == 'dr':
                    line.type = 'cr'
                else:
                    line.type = 'dr'

            if (line.type == 'dr'):
                tot_line += amount
                move_line['debit'] = amount
            else:
                tot_line -= amount
                move_line['credit'] = amount

            if voucher.tax_id and voucher.type in ('sale', 'purchase'):
                move_line.update({
                    'account_tax_id': voucher.tax_id.id,
                })

            if move_line.get('account_tax_id', False):
                tax_data = tax_obj.browse(cr, uid,
                                          [move_line['account_tax_id']],
                                          context=context)[0]
                if not (tax_data.base_code_id and tax_data.tax_code_id):
                    raise orm.except_orm(_('No Account Base Code and Account '
                                         'Tax Code!'),
                                         _("You have to configure account "
                                           "base code and account tax code on "
                                           "the '%s' tax!") % (tax_data.name))

            # compute the amount in foreign currency
            foreign_currency_diff = 0.0
            amount_currency = False
            if line.move_line_id:
                # We want to set it on the account move line as soon as the
                # original line had a foreign currency
                if line.move_line_id.currency_id and \
                        line.move_line_id.currency_id.id != company_currency:
                    # we compute the amount in that foreign currency.
                    if line.move_line_id.currency_id.id == current_currency:
                        # if the voucher and the voucher line share the same
                        # currency, there is no computation to do
                        sign = (move_line['debit'] - move_line['credit']) < 0 \
                               and -1 or 1
                        amount_currency = sign * (line.amount)
                    else:
                        # if the rate is specified on the voucher, it will be
                        # used thanks to the special keys in the context
                        # otherwise we use the rates of the system
                        amount_currency = currency_obj.compute(
                            cr, uid, company_currency,
                            line.move_line_id.currency_id.id,
                            move_line['debit']-move_line['credit'],
                            context=ctx)
                if line.amount == line.amount_unreconciled:
                    foreign_currency_diff = \
                        line.move_line_id.amount_residual_currency - abs(
                            amount_currency)

            move_line['amount_currency'] = amount_currency
            voucher_line = move_line_obj.create(cr, uid, move_line)
            rec_ids = [voucher_line, line.move_line_id.id]

            if not currency_obj.is_zero(cr, uid,
                                        voucher.company_id.currency_id,
                                        currency_rate_difference):
                # Change difference entry in company currency
                exch_lines = self._get_exchange_lines(
                    cr, uid, line, move_id, currency_rate_difference,
                    company_currency, current_currency, context=context)
                new_id = move_line_obj.create(cr, uid, exch_lines[0], context)
                move_line_obj.create(cr, uid, exch_lines[1], context)
                rec_ids.append(new_id)

            if line.move_line_id and line.move_line_id.currency_id and \
                    not currency_obj.is_zero(cr, uid,
                                             line.move_line_id.currency_id,
                                             foreign_currency_diff):
                # Change difference entry in voucher currency
                move_line_foreign_currency = \
                    self._voucher_move_line_foreign_currency_prepare(
                        cr, uid, voucher_id, line_total, move_id,
                        company_currency, current_currency, line.id,
                        foreign_currency_diff, context=context)

                new_id = move_line_obj.create(cr, uid,
                                              move_line_foreign_currency,
                                              context=context)
                rec_ids.append(new_id)
            if line.move_line_id.id:
                rec_lst_ids.append(rec_ids)
        return tot_line, rec_lst_ids
