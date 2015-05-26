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


class account_move_line(orm.Model):
    _inherit = "account.move.line"

    def _query_get(self, cr, uid, obj='l', context=None):
        query = super(account_move_line, self)._query_get(cr, uid, obj=obj,
                                                          context=context)
        if context.get('operating_unit_ids', False):
            operating_unit_ids = context.get('operating_unit_ids')
            query += 'AND '+obj+'.operating_unit_id in (%s)' % (
                ','.join(map(str, operating_unit_ids)))
        return query

    _columns = {
        'operating_unit_id': fields.many2one('operating.unit',
                                             'Operating Unit',
                                             required=False),
        'ou_cleared_line_id': fields.many2one('account.move.line',
                                              'Inter-OU Cleared move line',
                                              required=False),

    }


class account_move(orm.Model):
    _inherit = "account.move"

    def post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ml_obj = self.pool.get('account.move.line')
        for move in self.browse(cr, uid, ids, context=context):
            # If all move lines point to the same operating unit, there's no
            #  need to create a balancing move line
            multiple_ou = False
            previous_ou = False
            for line in move.line_id:
                if line.operating_unit_id:
                    if previous_ou and previous_ou \
                            != line.operating_unit_id.id:
                        multiple_ou = True
                    previous_ou = line.operating_unit_id.id
            if not multiple_ou:
                continue
            for line in move.line_id:
                cleared = False
                if line.operating_unit_id:
                    cl_acc = line.company_id.inter_ou_clearing_account_id
                    if not line.company_id.inter_ou_clearing_account_id:
                        raise orm.except_orm(
                            _('Error!'),
                            _("You need to define an inter-operating unit "
                              "clearing account in the company settings."))
                    if line.account_id == cl_acc:
                        continue
                    # Check if this line has already been cleared
                    for l in move.line_id:
                        if line == l.ou_cleared_line_id:
                            cleared = True
                    if cleared:
                        continue

                    # Create a balancing move line in the operating unit
                    # clearing account
                    lid = ml_obj.create(cr, uid, {
                        'name': _('Balancing line'),
                        'centralisation': line.centralisation,
                        'partner_id': False,
                        'account_id':
                            line.company_id.inter_ou_clearing_account_id.id,
                        'move_id': line.move_id.id,
                        'journal_id': line.journal_id.id,
                        'period_id': line.period_id.id,
                        'date': line.date,
                        'debit': line.credit,
                        'credit': line.debit,
                        'currency_id': line.currency_id.id,
                        'amount_currency': line.amount_currency,
                        'operating_unit_id': line.operating_unit_id.id,
                        'analytic_account_id': line.analytic_account_id.id,
                        'ou_cleared_line_id': line.id,
                    }, context=context)
                    self.write(cr, uid, [move.id],
                               {'line_id': [(4, lid)]}, context=context)

        return super(account_move, self).post(cr, uid, ids,
                                              context=context)

    def _check_inter_ou_same_account(self, cr, uid, ids):
        for move in self.browse(cr, uid, ids):
            ou = {}
            acc = {}
            for line in move.line_id:
                is_cl_acc = False
                if line.operating_unit_id:
                    cl_acc = \
                        line.company_id.inter_ou_clearing_account_id
                    if not cl_acc:
                        raise orm.except_orm(
                            _('Error!'),
                            _("You need to define an inter-operating unit "
                              "clearing account in the company settings."))
                    if line.account_id == cl_acc:
                        is_cl_acc = True
                    ou[line.operating_unit_id.id] = True
                if not is_cl_acc:
                    acc[line.account_id.id] = True

            if len(ou.keys()) > 1 and len(acc.keys()) > 1:
                return False
            return True

    def _check_same_ou_dr_cr(self, cr, uid, ids):
        for move in self.browse(cr, uid, ids):
            dr = {}
            cr = {}
            ou_ids = []
            for line in move.line_id:
                if line.operating_unit_id.id:
                    cl_acc = \
                        line.company_id.inter_ou_clearing_account_id
                    if not cl_acc:
                        raise orm.except_orm(
                            _('Error!'),
                            _("You need to define an inter-operating unit "
                              "clearing account in the company settings."))
                    ou_ids.append(line.operating_unit_id.id)
                    if not cl_acc:
                        if line.operating_unit_id.id in dr:
                            dr[line.operating_unit_id.id] += line.debit
                        else:
                            dr[line.operating_unit_id.id] = line.debit

                        if line.operating_unit_id.id in cr:
                            cr[line.operating_unit_id.id] += line.credit
                        else:
                            cr[line.operating_unit_id.id] = line.credit
            for ou_id in ou_ids:
                if (
                    ou_id in dr and
                    ou_id in cr and
                    dr[ou_id] > 0 and
                    cr[ou_id] > 0
                ):
                    return False
        return True

    _constraints = [
        (_check_inter_ou_same_account,
         'Moves with lines containing different operating units are only '
         'allowed when all lines refer to the same account.',
         ['line_id']),
        (_check_same_ou_dr_cr,
         'The same operating unit cannot exist in the debit and credit '
         'for the same account',
         ['line_id']),
    ]
