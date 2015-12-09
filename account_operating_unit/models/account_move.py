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
        'ou_cleared_line_id': fields.many2one('account.move.line',
                                              'Inter-OU Cleared move line',
                                              required=False),
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

    def post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ml_obj = self.pool.get('account.move.line')
        for move in self.browse(cr, uid, ids, context=context):
            # If all move lines point to the same operating unit, there's no
            #  need to create a balancing move line
            ou_list_ids = [line.operating_unit_id and
                           line.operating_unit_id.id for line in
                           move.line_id]
            ou_ids = list(set(ou_list_ids))
            if len(ou_ids) <= 1:
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
                        'name': line.name,
                        'centralisation': line.centralisation,
                        'partner_id': line.partner_id and
                        line.partner_id.id or False,
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

        return super(AccountMove, self).post(cr, uid, ids, context=context)

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
        (_check_same_ou_dr_cr,
         'The same operating unit cannot exist in the debit and credit '
         'for the same account',
         ['line_id'])]
