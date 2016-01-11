# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.osv import orm, fields
from openerp.tools.translate import _

class AccountFiscalyearClose(orm.TransientModel):

    _inherit = "account.fiscalyear.close"

    def process(self, cr, uid, ids, context=None):

        def _reconcile_fy_closing(cr, uid, ids, context=None):
            """
            This private function manually do the reconciliation on the account_move_line given as `ids´, and directly
            through psql. It's necessary to do it this way because the usual `reconcile()´ function on account.move.line
            object is really resource greedy (not supposed to work on reconciliation between thousands of records) and
            it does a lot of different computation that are useless in this particular case.
            """
            #check that the reconcilation concern journal entries from only one company
            cr.execute('select distinct(company_id) from account_move_line where id in %s',(tuple(ids),))
            if len(cr.fetchall()) > 1:
                raise orm.except_orm(_('Warning!'), _('The entries to reconcile should belong to the same company.'))
            r_id = self.pool.get('account.move.reconcile').create(cr, uid, {'type': 'auto', 'opening_reconciliation': True})
            cr.execute('update account_move_line set reconcile_id = %s where id in %s',(r_id, tuple(ids),))
            return r_id

        obj_acc_account = self.pool.get('account.account')
        currency_obj = self.pool.get('res.currency')
        obj_acc_period = self.pool.get('account.period')
        obj_acc_fiscalyear = self.pool.get('account.fiscalyear')
        obj_acc_journal = self.pool.get('account.journal')
        obj_acc_move = self.pool.get('account.move')
        obj_acc_move_line = self.pool.get('account.move.line')

        data = self.browse(cr, uid, ids, context=context)
        fy_id = data[0].fy_id.id

        cr.execute("SELECT id FROM account_period WHERE date_stop < (SELECT date_start FROM account_fiscalyear WHERE id = %s)", (str(data[0].fy2_id.id),))
        fy_period_set = ','.join(map(lambda id: str(id[0]), cr.fetchall()))
        cr.execute("SELECT id FROM account_period WHERE date_start > (SELECT date_stop FROM account_fiscalyear WHERE id = %s)", (str(fy_id),))
        fy2_period_set = ','.join(map(lambda id: str(id[0]), cr.fetchall()))

        if not fy_period_set or not fy2_period_set:
            raise orm.except_orm(_('User Error!'), _('The periods to generate opening entries cannot be found.'))

        period = obj_acc_period.browse(cr, uid, data[0].period_id.id, context=context)
        new_fyear = obj_acc_fiscalyear.browse(cr, uid, data[0].fy2_id.id, context=context)

        operating_unit_id = None
        if 'operating_unit_ids' in context:
            operating_unit_id = context['operating_unit_ids'][0]

        new_journal = data[0].journal_id.id
        new_journal = obj_acc_journal.browse(cr, uid, new_journal, context=context)
        company_id = new_journal.company_id.id

        cr.execute("SELECT id FROM account_fiscalyear WHERE date_stop < %s", (str(new_fyear.date_start),))
        result = cr.dictfetchall()
        fy_ids = [x['id'] for x in result]
        # Pass the whole context to _query_get.
        ctx = context.copy()
        ctx['fiscalyear'] = fy_ids
        query_line = obj_acc_move_line._query_get(cr, uid,
                obj='account_move_line', context=ctx)
        #create the opening move
        vals = {
            'name': '/',
            'ref': '',
            'period_id': period.id,
            'date': period.date_start,
            'journal_id': new_journal.id,
            'operating_unit_id': operating_unit_id,
        }
        move_id = obj_acc_move.create(cr, uid, vals, context=context)

        #1. report of the accounts with defferal method == 'unreconciled'
        cr.execute('''
            SELECT a.id
            FROM account_account a
            LEFT JOIN account_account_type t ON (a.user_type = t.id)
            WHERE a.active
              AND a.type not in ('view', 'consolidation')
              AND a.company_id = %s
              AND t.close_method = %s''', (company_id, 'unreconciled', ))
        account_ids = map(lambda x: x[0], cr.fetchall())
        if account_ids:
            cr.execute('''
                INSERT INTO account_move_line (
                     name, create_uid, create_date, write_uid, write_date,
                     statement_id, journal_id, currency_id, date_maturity,
                     partner_id, blocked, credit, state, debit,
                     ref, account_id, period_id, date, move_id, amount_currency,
                     quantity, product_id, company_id, operating_unit_id)
                  (SELECT name, create_uid, create_date, write_uid, write_date,
                     statement_id, %s,currency_id, date_maturity, partner_id,
                     blocked, credit, 'draft', debit, ref, account_id,
                     %s, (%s) AS date, %s, amount_currency, quantity,
                     product_id, company_id, operating_unit_id
                   FROM account_move_line
                   WHERE account_id IN %s
                     AND ''' + query_line + '''
                     AND reconcile_id IS NULL)''', (new_journal.id, period.id, period.date_start, move_id, tuple(account_ids),))

            #We have also to consider all move_lines that were reconciled
            #on another fiscal year, and report them too
            query_line_b = obj_acc_move_line._query_get(
                    cr, uid, obj='b', context=ctx)
            cr.execute('''
                INSERT INTO account_move_line (
                     name, create_uid, create_date, write_uid, write_date,
                     statement_id, journal_id, currency_id, date_maturity,
                     partner_id, blocked, credit, state, debit,
                     ref, account_id, period_id, date, move_id, amount_currency,
                     quantity, product_id, company_id, operating_unit_id)
                  (SELECT
                     b.name, b.create_uid, b.create_date, b.write_uid, b.write_date,
                     b.statement_id, %s, b.currency_id, b.date_maturity,
                     b.partner_id, b.blocked, b.credit, 'draft', b.debit,
                     b.ref, b.account_id, %s, (%s) AS date, %s, b.amount_currency,
                     b.quantity, b.product_id, b.company_id, b.operating_unit_id
                     FROM account_move_line b
                     WHERE b.account_id IN %s
                        AND ''' + query_line_b + '''
                       AND b.reconcile_id IS NOT NULL
                       AND b.period_id IN ('''+fy_period_set+''')
                       AND b.reconcile_id IN (SELECT DISTINCT(reconcile_id)
                                          FROM account_move_line a
                                          WHERE a.period_id IN ('''+fy2_period_set+''')))''', (new_journal.id, period.id, period.date_start, move_id, tuple(account_ids),))

        #2. report of the accounts with defferal method == 'detail'
        cr.execute('''
            SELECT a.id
            FROM account_account a
            LEFT JOIN account_account_type t ON (a.user_type = t.id)
            WHERE a.active
              AND a.type not in ('view', 'consolidation')
              AND a.company_id = %s
              AND t.close_method = %s''', (company_id, 'detail', ))
        account_ids = map(lambda x: x[0], cr.fetchall())

        if account_ids:
            cr.execute('''
                INSERT INTO account_move_line (
                     name, create_uid, create_date, write_uid, write_date,
                     statement_id, journal_id, currency_id, date_maturity,
                     partner_id, blocked, credit, state, debit,
                     ref, account_id, period_id, date, move_id, amount_currency,
                     quantity, product_id, company_id, operating_unit_id)
                  (SELECT name, create_uid, create_date, write_uid, write_date,
                     statement_id, %s,currency_id, date_maturity, partner_id,
                     blocked, credit, 'draft', debit, ref, account_id,
                     %s, (%s) AS date, %s, amount_currency, quantity,
                     product_id, company_id, operating_unit_id
                   FROM account_move_line
                   WHERE account_id IN %s
                     AND ''' + query_line + ''')
                     ''', (new_journal.id, period.id, period.date_start, move_id, tuple(account_ids),))


        #3. report of the accounts with defferal method == 'balance'
        cr.execute('''
            SELECT a.id
            FROM account_account a
            LEFT JOIN account_account_type t ON (a.user_type = t.id)
            WHERE a.active
              AND a.type not in ('view', 'consolidation')
              AND a.company_id = %s
              AND t.close_method = %s''', (company_id, 'balance', ))
        account_ids = map(lambda x: x[0], cr.fetchall())

        query_1st_part = """
                INSERT INTO account_move_line (
                     debit, credit, name, date, move_id, journal_id, period_id,
                     account_id, currency_id, amount_currency, company_id,
                     operating_unit_id, state) VALUES
        """
        query_2nd_part = ""
        query_2nd_part_args = []
        ctx = context.copy()
        ctx['fiscalyear'] = fy_id
        for account in obj_acc_account.browse(cr, uid, account_ids,
                                              context=ctx):
            company_currency_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id
            if not currency_obj.is_zero(cr, uid, company_currency_id, abs(account.balance)):
                if query_2nd_part:
                    query_2nd_part += ','
                query_2nd_part += "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                                  "%s, %s, %s)"
                query_2nd_part_args += (account.balance > 0 and account.balance or 0.0,
                       account.balance < 0 and -account.balance or 0.0,
                       data[0].report_name,
                       period.date_start,
                       move_id,
                       new_journal.id,
                       period.id,
                       account.id,
                       account.currency_id and account.currency_id.id or None,
                       account.foreign_balance if account.currency_id else 0.0,
                       account.company_id.id,
                       operating_unit_id,
                       'draft')
        if query_2nd_part:
            cr.execute(query_1st_part + query_2nd_part, tuple(query_2nd_part_args))

        #validate and centralize the opening move
        obj_acc_move.validate(cr, uid, [move_id], context=context)

        #reconcile all the move.line of the opening move
        ids = obj_acc_move_line.search(cr, uid, [('journal_id', '=', new_journal.id),
            ('period_id.fiscalyear_id','=',new_fyear.id)])
        if ids:
            reconcile_id = _reconcile_fy_closing(cr, uid, ids, context=context)
            #set the creation date of the reconcilation at the first day of the new fiscalyear, in order to have good figures in the aged trial balance
            self.pool.get('account.move.reconcile').write(cr, uid, [reconcile_id], {'create_date': new_fyear.date_start}, context=context)

    def data_save(self, cr, uid, ids, context=None):        
        """
        This function overrides the standard method from account module, 
        providing additional hooks for better extension.
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Account fiscalyear close state’s IDs

        """

        obj_acc_period = self.pool.get('account.period')
        obj_acc_fiscalyear = self.pool.get('account.fiscalyear')
        obj_acc_journal = self.pool.get('account.journal')
        obj_acc_move = self.pool.get('account.move')
        obj_acc_move_line = self.pool.get('account.move.line')
        obj_acc_journal_period = self.pool.get('account.journal.period')

        data = self.browse(cr, uid, ids, context=context)

        if context is None:
            context = {}
        fy_id = data[0].fy_id.id
        period = obj_acc_period.browse(cr, uid, data[0].period_id.id, context=context)

        new_journal = data[0].journal_id.id
        new_journal = obj_acc_journal.browse(cr, uid, new_journal, context=context)
        company = new_journal.company_id

        if not new_journal.default_credit_account_id or not new_journal.default_debit_account_id:
            raise orm.except_orm(_('User Error!'),
                    _('The journal must have default credit and debit account.'))
        if (not new_journal.centralisation) or new_journal.entry_posted:
            raise orm.except_orm(_('User Error!'),
                    _('The journal must have centralized counterpart without the Skipping draft state option checked.'))

        #delete existing move and move lines if any
        move_ids = obj_acc_move.search(cr, uid, [
            ('journal_id', '=', new_journal.id), ('period_id', '=', period.id)])
        if move_ids:
            move_line_ids = obj_acc_move_line.search(cr, uid, [('move_id', 'in', move_ids)])
            obj_acc_move_line._remove_move_reconcile(cr, uid, move_line_ids, opening_reconciliation=True, context=context)
            obj_acc_move_line.unlink(cr, uid, move_line_ids, context=context)
            obj_acc_move.unlink(cr, uid, move_ids, context=context)

        if company.ou_is_self_balanced:
            ou_ids = self.pool['operating.unit'].search(
                    cr, uid, [('company_id', '=', company.id)], context=context)
            for ou_id in ou_ids:
                ctx = context.copy()
                ctx['operating_unit_ids'] = [ou_id]
                self.process(cr, uid, ids, context=ctx)
        else:
            self.process(cr, uid, ids, context=context)

       #create the journal.period object and link it to the old fiscalyear
        new_period = data[0].period_id.id
        ids = obj_acc_journal_period.search(cr, uid, [('journal_id', '=', new_journal.id), ('period_id', '=', new_period)])
        if not ids:
            ids = [obj_acc_journal_period.create(cr, uid, {
                   'name': (new_journal.name or '') + ':' + (period.code or ''),
                   'journal_id': new_journal.id,
                   'period_id': period.id
               })]
        old_fyear = obj_acc_fiscalyear.browse(cr, uid, fy_id, context=context)
        cr.execute('UPDATE account_fiscalyear ' \
                    'SET end_journal_period_id = %s ' \
                    'WHERE id = %s', (ids[0], old_fyear.id))

        return {'type': 'ir.actions.act_window_close'}
