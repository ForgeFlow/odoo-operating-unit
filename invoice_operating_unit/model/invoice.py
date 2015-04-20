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


class account_invoice(orm.Model):
    _inherit = "account.invoice"
    _columns = {
        'operating_unit_id': fields.many2one('operating.unit',
                                             'Operating Unit'),
    }

    def finalize_invoice_move_lines(self, cr, uid, invoice_browse, move_lines):
        move_lines = super(account_invoice, self).finalize_invoice_move_lines(
            cr, uid, invoice_browse, move_lines)
        new_move_lines = []
        for line_tuple in move_lines:
            if invoice_browse.operating_unit_id:
                line_tuple[2]['operating_unit_id'] = \
                    invoice_browse.operating_unit_id.id
            new_move_lines.append(line_tuple)
        return new_move_lines


class account_invoice_line(orm.Model):
    _inherit = 'account.invoice.line'

    _columns = {
        'operating_unit_id': fields.related(
            'order_id', 'operating_unit_id', type='many2one',
            relation='operating.unit', string='Operating Unit',
            readonly=True),
    }
