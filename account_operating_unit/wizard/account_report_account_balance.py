# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.osv import fields, orm
from openerp.addons.account.report.account_balance import account_balance
from openerp.report import report_sxw


class AccountBalanceReport(orm.TransientModel):
    _inherit = "account.balance.report"

    _columns = {
        'operating_unit_ids': fields.many2many('operating.unit',
                                               string='Operating Units',
                                               required=False),
    }

    def _build_contexts(self, cr, uid, ids, data, context=None):
        result = super(AccountBalanceReport, self)._build_contexts(
            cr, uid, ids, data, context=context)
        data2 = {}
        data2['form'] = self.read(cr, uid, ids, ['operating_unit_ids'],
                                  context=context)[0]
        result['operating_unit_ids'] = 'operating_unit_ids' in data2['form']\
                                       and data2['form']['operating_unit_ids']\
                                       or False
        return result

    def _build_comparison_context(self, cr, uid, ids, data, context=None):
        result = super(AccountBalanceReport, self)._build_comparison_context(
            cr, uid, ids, data, context=context)
        data['form'] = self.read(cr, uid, ids, ['operating_unit_ids'],
                                 context=context)[0]
        result['operating_unit_ids'] = 'operating_unit_ids' in data['form'] \
                                       and data['form']['operating_unit_ids'] \
                                       or False
        return result
