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
        result['operating_unit_ids'] = 'operating_unit_ids' in data2['form'] \
                                       and data2['form']['operating_unit_ids'] \
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
