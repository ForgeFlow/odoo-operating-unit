# -*- coding: utf-8 -*-
# © 2015 Eficent - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.osv import orm, fields
from openerp.tools.translate import _


class AccountMoveLine(orm.Model):
    _inherit = "account.move.line"

    def _query_get(self, cr, uid, obj='l', context=None):
        query = super(AccountMoveLine, self)._query_get(cr, uid, obj=obj,
                                                        context=context)
        if context.get('operating_unit_ids', False):
            operating_unit_ids = context.get('operating_unit_ids')
            query += 'AND ' + obj + '.operating_unit_id in (%s)' % (
                ','.join(map(str, operating_unit_ids)))
        return query

    _columns = {
        'operating_unit_id': fields.many2one('operating.unit',
                                             'Operating Unit'),
    }

    _defaults = {
        'operating_unit_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').operating_unit_default_get(cr, uid, uid, context=c),
    }

    def _check_company_operating_unit(self, cr, uid, ids, context=None):
        for ml in self.browse(cr, uid, ids, context=context):
            if ml.company_id and ml.operating_unit_id and\
                            ml.company_id != ml.operating_unit_id.company_id:
                return False
        return True

    _constraints = [
        (_check_company_operating_unit,
         'The Company in the Move Line and in the '
         'Operating Unit must be the same.', ['operating_unit_id',
                                              'company_id'])
    ]


class AccountMove(orm.Model):
    _inherit = "account.move"

    def _prepare_inter_ou_balancing_move_line(self, cr, uid, move, ou_id,
                                              ou_balances, context=None):

        if not move.company_id.inter_ou_clearing_account_id:
            raise orm.except_orm(
                _('Error!'),
                _("You need to define an inter-operating unit "
                  "clearing account in the company "
                  "settings."))

        res = {
            'name': 'OU-Balancing',
            'move_id': move.id,
            'journal_id': move.journal_id.id,
            'period_id': move.period_id.id,
            'date': move.date,
            'operating_unit_id': ou_id,
            'account_id': move.company_id.inter_ou_clearing_account_id.id
        }

        if ou_balances[ou_id] < 0.0:
            res['debit'] = abs(ou_balances[ou_id])

        else:
            res['credit'] = ou_balances[ou_id]
        return res

    def _check_ou_balance(self, cr, uid, move, context=None):
        # Look for the balance of each OU
        ou_balance = {}
        for line in move.line_id:
            if line.operating_unit_id.id not in ou_balance:
                ou_balance[line.operating_unit_id.id] = 0.0
            ou_balance[line.operating_unit_id.id] += (line.debit - line.credit)
        return ou_balance

    def post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ml_obj = self.pool.get('account.move.line')
        for move in self.browse(cr, uid, ids, context=context):
            if not move.company_id.ou_is_self_balanced:
                continue

            # If all move lines point to the same operating unit, there's no
            #  need to create a balancing move line
            ou_list_ids = [line.operating_unit_id and
                           line.operating_unit_id.id for line in
                           move.line_id if line.operating_unit_id]
            ou_ids = list(set(ou_list_ids))
            if len(ou_ids) <= 1:
                continue
            # Create balancing entries for un-balanced OU's.
            curr_obj = self.pool['res.currency']
            ou_balances = self._check_ou_balance(cr, uid, move,
                                                 context=context)
            for ou_id in ou_balances.keys():
                # If the OU is already balanced, then do not continue
                if curr_obj.is_zero(cr, uid, move.company_id.currency_id,
                                    ou_balances[ou_id]):
                    continue
                # Create a balancing move line in the operating unit
                # clearing account
                line_data = self._prepare_inter_ou_balancing_move_line(
                            cr, uid, move, ou_id, ou_balances, context=context)
                if line_data:
                    lid = ml_obj.create(cr, uid, line_data,
                                        context=context)
                    self.write(cr, uid, [move.id],
                               {'line_id': [(4, lid)]}, context=context)

        return super(AccountMove, self).post(cr, uid, ids, context=context)

    def _check_ou(self, cr, uid, ids):
        for move in self.browse(cr, uid, ids):
            if not move.company_id.ou_is_self_balanced:
                continue
            for line in move.line_id:
                if not line.operating_unit_id:
                    return False
        return True

    _constraints = [
        (_check_ou,
         'The operating unit must be completed for each line if the '
         'operating unit has been defined as self-balanced at company level.',
         ['line_id'])]
