# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
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
#

from openerp.tests import common
from openerp import netsvc


class TestPurchaseOperatingUnit(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseOperatingUnit, self).setUp()
        cr, uid, context = self.cr, self.uid, {}

        self.purchase_model = self.registry('purchase.order')
        self.purchase_line_model = self.registry('purchase.order.line')
        self.stock_picking_model = self.registry('stock.picking')
        self.account_invoice_model = self.registry('account.invoice')
        self.product_model = self.registry('product.product')
        self.partner_model = self.registry('res.partner')
        self.location_model = self.registry('stock.location')
        self.pricelist_model = self.registry('product.pricelist')
        self.operating_unit_model = self.registry('operating.unit')
        self.res_users_model = self.registry('res.users')
        self.res_company_model = self.registry('res.company')
        self.res_groups = self.registry('res.groups')

        data_model = self.registry('ir.model.data')

        _, company1_id = data_model.get_object_reference(
            cr, uid, 'base', 'main_company')
        self.company1 = self.res_company_model.browse(cr, uid, company1_id,
                                                      context=context)
        _, company1_id = data_model.get_object_reference(
            cr, uid, 'stock', 'res_company_2')
        self.company2 = self.res_company_model.browse(cr, uid, company1_id,
                                                      context=context)
        _, group_purchase_user_id = data_model.get_object_reference(
            cr, uid, 'purchase', 'group_purchase_user')
        self.group_purchase_user = self.res_groups.browse(
            cr, uid, group_purchase_user_id, context=context)
        _, group_stock_user_id = data_model.get_object_reference(
            cr, uid, 'stock', 'group_stock_user')
        self.group_stock_user = self.res_groups.browse(cr, uid,
                                                       group_stock_user_id,
                                                       context=context)
        _, ou1_id = data_model.get_object_reference(
            cr, uid, 'operating_unit', 'main_operating_unit')
        self.ou1 = self.operating_unit_model.browse(cr, uid, ou1_id,
                                                    context=context)
        _, ou2_id = data_model.get_object_reference(
            cr, uid, 'stock_operating_unit', 'operating_unit_shop1')
        self.ou2 = self.operating_unit_model.browse(cr, uid, ou1_id,
                                                    context=context)
        _, partner1_id = data_model.get_object_reference(cr, uid, 'base',
                                                         'res_partner_1')
        self.partner1 = self.partner_model.browse(cr, uid, partner1_id,
                                                  context=context)
        _, product1_id = data_model.get_object_reference(
            cr, uid, 'product', 'product_product_7')
        self.product1 = self.product_model.browse(
            cr, uid, product1_id, context=context)

        _, product2_id = data_model.get_object_reference(cr, uid, 'product',
                                                         'product_product_9')
        self.product2 = self.product_model.browse(
            cr, uid, product2_id, context=context)

        _, product3_id = data_model.get_object_reference(
            cr, uid, 'product', 'product_product_11')
        self.product3 = self.product_model.browse(
            cr, uid, product3_id, context=context)

        _, warehouse1_id = data_model.get_object_reference(
            cr, uid, 'stock', 'warehouse0')
        self.warehouse1 = self.product_model.browse(
            cr, uid, warehouse1_id, context=context)

        _, location_stock1_id = data_model.get_object_reference(
            cr, uid, 'stock', 'stock_location_stock')
        self.location_stock1 = self.location_model.browse(
            cr, uid, location_stock1_id, context=context)

        _, purchase_pricelist_id = data_model.get_object_reference(
            cr, uid, 'purchase', 'list0')
        self.purchase_pricelist = self.pricelist_model.browse(
            cr, uid, purchase_pricelist_id, context=context)

        user1_id = self._create_user(cr, uid, 'user_1',
                                     [self.group_purchase_user,
                                      self.group_stock_user],
                                     self.company1,
                                     [self.ou1], context=context)
        self.user1 = self.res_users_model.browse(
            cr, uid, user1_id, context=context)

        user2_id = self._create_user(cr, uid, 'user_2',
                                     [self.group_purchase_user,
                                      self.group_stock_user],
                                     self.company2,
                                     [self.ou2], context=context)
        self.user2 = self.res_users_model.browse(
            cr, uid, user2_id, context=context)

        purchase1_id = self._create_purchase(
            cr, user1_id, 'picking', [(self.product1, 1000),
                                      (self.product2, 500),
                                      (self.product3, 800)], context=context)
        self.purchase1 = self.purchase_model.browse(
            cr, user1_id, purchase1_id, context=context)

        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'purchase.order', purchase1_id,
                                'purchase_confirm', cr)

        purchase2_id = self._create_purchase(
            cr, user1_id, 'order', [(self.product1, 1000),
                                    (self.product2, 500),
                                    (self.product3, 800)], context=context)
        self.purchase2 = self.purchase_model.browse(
            cr, user1_id, purchase2_id, context=context)
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'purchase.order', purchase2_id,
                                'purchase_confirm', cr)

    def _create_user(self, cr, uid, login, groups, company, operating_units,
                     context=None):
        """ Create a user.
        """
        group_ids = [group.id for group in groups]
        user_id = self.res_users_model.create(cr, uid, {
            'name': 'Chicago Purchase User',
            'login': login,
            'password': 'demo',
            'email': 'chicago@yourcompany.com',
            'company_id': company.id,
            'company_ids': [(4, company.id)],
            'operating_unit_ids': [(4, ou.id) for ou in operating_units],
            'groups_id': [(6, 0, group_ids)]
        })

        return user_id

    def _create_purchase(self, cr, uid, invoice_method, line_products,
                         context=None):
        """ Create a purchase order.

        ``line_products`` is a list of tuple [(product, qty)]
        """
        lines = []
        for product, qty in line_products:
            line_values = {
                'product_id': product.id,
                'product_qty': qty,
                'product_uom': product.uom_id.id,
                'price_unit': 50,
            }
            onchange_res = self.purchase_line_model.onchange_product_id(
                cr, uid, [], self.purchase_pricelist.id, product.id, qty,
                product.uom_id.id, self.partner1.id, context=context)
            line_values.update(onchange_res['value'])
            lines.append(
                (0, 0, line_values)
            )
        po = self.purchase_model.create(cr, uid, {
            'operating_unit_id': self.ou1.id,
            'requesting_operating_unit_id': self.ou1.id,
            'partner_id': self.partner1.id,
            'warehouse_id': self.warehouse1.id,
            'location_id': self.location_stock1.id,
            'pricelist_id': self.purchase_pricelist.id,
            'order_line': lines,
            'invoice_method': invoice_method,
            'company_id': self.company1.id,
        }, context=context)
        return po

    def test_security(self):
        cr, uid, context = self.cr, self.uid, {}
        # User 2 is only assigned to Operating Unit 2, and cannot list
        # purchase orders from Operating Unit 1.
        po_ids = self.purchase_model.search(cr, self.user2.id,
                                            [('operating_unit_id', '=',
                                              self.ou1.id)], context=context)
        self.assertEqual(po_ids, [])

        # User 2 cannot list the picking that was created from PO 1
        picking_ids = self.stock_picking_model.search(
            cr, self.user2.id, [('purchase_id', '=', self.purchase1.id)],
            context=context)
        self.assertEqual(picking_ids, [])

        # User 2 cannot list the invoice that was created from PO 2
        invoices = [inv.id for inv in self.purchase2.invoice_ids]
        invoice_ids = self.account_invoice_model.search(
            cr, self.user2.id, [('id', '=', invoices[0])],
            context=context)
        self.assertEqual(invoice_ids, [])

        # User 1 is assigned to Operating Unit 1, and can list
        # the purchase order 1 from Operating Unit 1.
        po_ids = self.purchase_model.search(cr, self.user1.id,
                                            [('operating_unit_id', '=',
                                              self.ou1.id)], context=context)
        self.assertNotEqual(po_ids, [])

        # User 1 can list the picking that was created from PO 1
        picking_ids = self.stock_picking_model.search(
            cr, self.user1.id, [('purchase_id', '=', self.purchase1.id)],
            context=context)
        self.assertNotEqual(picking_ids, [])

        # User 1 can list the invoice that was created from PO 2
        invoices = [inv.id for inv in self.purchase2.invoice_ids]
        invoice_ids = self.account_invoice_model.search(
            cr, self.user1.id, [('id', '=', invoices[0])],
            context=context)
        self.assertNotEqual(invoice_ids, [])
