# -*- coding: utf-8 -*-
# Authors: Leonardo Pistone, Jordi Ballester Alomar
# Copyright 2014 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2015 Eficent (http://www.eficent.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public Lice
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from openerp.osv import orm, fields
from openerp.tools.translate import _


class stock_move(orm.Model):
    _inherit = 'stock.move'

    def _create_account_move_line(self, cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=None):
        if context is None:
            context = {}
        res = super(stock_move, self)._create_account_move_line(
            cr, uid, move, src_account_id, dest_account_id, reference_amount,
            reference_currency_id, context=context)

        debit_line_vals = res[0][2]
        credit_line_vals = res[1][2]

        debit_line_vals['operating_unit_id'] = move.operating_unit_dest_id.id
        credit_line_vals['operating_unit_id'] = move.operating_unit_id.id

        if (
            move.operating_unit_id != move.operating_unit_dest_id and
            debit_line_vals['account_id'] != credit_line_vals['account_id']
        ):
            raise orm.except_orm(_('Error!'),
                                 _('You cannot create stock moves involving '
                                   'separate source and destination accounts '
                                   'and different source and destination '
                                   'operating units.'))

        return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

    def _create_product_valuation_moves(self, cr, uid, move, context=None):
        """
        Generate an accounting moves if the product being moved is subject
        to real_time valuation tracking,
        and the source or destination location are
        a transit location or is outside of the company or the source or
        destination locations belong to different operating units.
        """
        res = super(stock_move, self)._create_product_valuation_moves(
            cr, uid, move, context=context)

        if move.product_id.valuation == 'real_time':
            # Inter-operating unit moves do not accept to
            # from/to non-internal location
            if (
                move.location_id.company_id == move.location_dest_id.company_id
                and move.operating_unit_id != move.operating_unit_dest_id
            ):
                err = False
                if move.location_id.usage != 'internal' \
                        and move.location_dest_id.usage == 'internal':
                    err = True
                if move.location_id.usage != 'internal' \
                        and move.location_dest_id.usage == 'internal':
                    err = True
                if move.location_id.usage != 'internal' \
                        and move.location_dest_id.usage != 'internal':
                    err = True
                if err:
                    raise orm.except_orm(
                        _('Error!'),
                        _('Transfers between locations of different operating '
                          'unit locations is only allowed when both source '
                          'and destination locations are internal.'))
                src_company_ctx = dict(
                    context, force_company=move.location_id.company_id.id)
                company_ctx = dict(context, company_id=move.company_id.id)
                journal_id, acc_src, acc_dest, acc_valuation = \
                    self._get_accounting_data_for_valuation(cr, uid, move,
                                                            src_company_ctx)
                reference_amount, reference_currency_id = \
                    self._get_reference_accounting_values_for_valuation(
                        cr, uid, move, src_company_ctx)
                account_moves = []
                account_moves += [(journal_id, self._create_account_move_line(
                    cr, uid, move, acc_valuation, acc_valuation, reference_amount,
                    reference_currency_id, context))]
                move_obj = self.pool.get('account.move')
                for j_id, move_lines in account_moves:
                    move_obj.create(cr, uid,
                                    {'journal_id': j_id,
                                     'line_id': move_lines,
                                     'company_id': move.company_id.id,
                                     'ref': move.picking_id
                                     and move.picking_id.name},
                                    context=company_ctx)