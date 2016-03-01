# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.osv import fields, orm
from openerp.tools.translate import _


class SaleShop(orm.Model):
    _inherit = 'sale.shop'

    _columns = {
        'operating_unit_id': fields.many2one('operating.unit',
                                             'Operating Unit'),
    }

    _defaults = {
        'operating_unit_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').operating_unit_default_get(cr, uid, uid, context=c),
    }

    def _check_company_operating_unit(self, cr, uid, ids, context=None):
        for r in self.browse(cr, uid, ids, context=context):
            if r.company_id and r.operating_unit_id and \
                    r.company_id != r.operating_unit_id.company_id:
                return False
        return True

    _constraints = [
        (_check_company_operating_unit,
         'The Company in the Sales Shop and in the Operating '
         'Unit must be the same.', ['operating_unit_id',
                                    'company_id'])]


class SaleOrder(orm.Model):

    _inherit = 'sale.order'

    def _get_default_shop(self, cr, uid, context=None):
        shop_id = super(SaleOrder, self)._get_default_shop(cr, uid,
                                                           context=context)
        default_ou_id = self.pool['res.users'].operating_unit_default_get(
            cr, uid, uid, context=context)
        shop_ids = self.pool.get('sale.shop').search(
            cr, uid, [('operating_unit_id', '=', default_ou_id)],
            context=context)
        if not shop_ids:
            raise orm.except_orm(_('Error!'),
                                 _('There is no default shop '
                                   'for the current user\'s operating unit!'))
        shop_id = shop_ids[0]
        return shop_id

    _columns = {
        'operating_unit_id': fields.many2one('operating.unit',
                                             'Operating Unit'),
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True,
                                   readonly=True,
                                   states={'draft': [('readonly', False)],
                                           'sent': [('readonly', False)]}),
    }

    _defaults = {
        'operating_unit_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').operating_unit_default_get(cr, uid, uid, context=c),
        'shop_id': _get_default_shop
    }

    def _check_company_operating_unit(self, cr, uid, ids, context=None):
        for r in self.browse(cr, uid, ids, context=context):
            if r.company_id and r.operating_unit_id and\
                    r.company_id != r.operating_unit_id.company_id:
                return False
        return True

    def _check_shop_operating_unit(self, cr, uid, ids, context=None):
        for r in self.browse(cr, uid, ids, context=context):
            if r.operating_unit_id != r.shop_id.operating_unit_id:
                return False
        return True

    def _check_invoices_operating_unit(self, cr, uid, ids, context=None):
        for r in self.browse(cr, uid, ids, context=context):
            for invoice in r.invoice_ids:
                if invoice.operating_unit_id != r.operating_unit_id:
                    return False
        return True

    _constraints = [
        (_check_company_operating_unit,
         'The Company in the Sales Order and in the Operating '
         'Unit must be the same.', ['operating_unit_id',
                                    'company_id']),
        (_check_shop_operating_unit,
         'The Operating Unit in the Sales Order and in the Shop '
         '%s must be the same.', ['operating_unit_id', 'shop_id']),
        (_check_invoices_operating_unit,
         'The Operating Unit in the Sales Order and in the invoices must be '
         'the same.', ['operating_unit_id', 'invoice_ids']),
    ]

    def _make_invoice(self, cr, uid, order, lines, context=None):
        invoice_obj = self.pool.get('account.invoice')
        res = super(SaleOrder, self)._make_invoice(
                                                   cr, uid, order,
                                                   lines, context=context)
        invoice_obj.write(
            cr, uid, res,
            {'operating_unit_id': order.operating_unit_id.id},
            context=context)
        return res


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    _columns = {
        'operating_unit_id': fields.related('order_id', 'operating_unit_id',
                                            type='many2one',
                                            relation='operating.unit',
                                            string='Operating Unit',
                                            readonly=True),
    }
