# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm, fields
from openerp.tools.translate import _


class SaleOrderLineMakeInvoice(orm.TransientModel):
    _inherit = "sale.order.line.make.invoice"

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        res = super(SaleOrderLineMakeInvoice, self)._prepare_invoice(
            cr, uid, order, lines, context=context)
        if order.operating_unit_id:
            res['operating_unit_id'] = order.operating_unit_id.id
        return res

    def make_invoices(self, cr, uid, ids, context=None):

        operating_unit_id = False
        line_obj = self.pool['sale.order.line']
        line_ids = context.get('active_ids', [])
        for line in line_obj.browse(cr, uid, line_ids, context=context):
            if (
                line.order_id and
                line.order_id.operating_unit_id and
                operating_unit_id and
                line.order_id.operating_unit_id.id != operating_unit_id
            ):
                raise orm.except_orm(_('Error!'),
                                     _('All the order lines must belong to '
                                       'the same Operating Unit.'))
            else:
                operating_unit_id = line.order_id.operating_unit_id.id
        return super(SaleOrderLineMakeInvoice, self).make_invoices(
            cr, uid, ids, context=context)
