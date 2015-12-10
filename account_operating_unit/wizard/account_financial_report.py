# -*- coding: utf-8 -*-
# © 2015 Eficent - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.osv import fields, orm


class accounting_report(orm.TransientModel):

    _inherit = "accounting.report"

    _columns = {
        'operating_unit_ids': fields.many2many('operating.unit',
                                               string='Operating Units',
                                               required=False),
    }

    def _build_contexts(self, cr, uid, ids, data, context=None):
        result = super(accounting_report, self)._build_contexts(
            cr, uid, ids, data, context=context)
        data2 = {}
        data2['form'] = self.read(cr, uid, ids, ['operating_unit_ids'],
                                  context=context)[0]
        result['operating_unit_ids'] = 'operating_unit_ids' in data2['form']\
                                       and data2['form']['operating_unit_ids']\
                                       or False
        return result

    def _build_comparison_context(self, cr, uid, ids, data, context=None):
        result = super(accounting_report, self)._build_comparison_context(
            cr, uid, ids, data, context=context)
        data['form'] = self.read(cr, uid, ids, ['operating_unit_ids'],
                                 context=context)[0]
        result['operating_unit_ids'] = 'operating_unit_ids' in data['form'] \
                                       and data['form']['operating_unit_ids'] \
                                       or False
        return result
