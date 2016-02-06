# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import netsvc
from openerp.tests import common


class TestSaleOperatingUnit(common.TransactionCase):

    def setUp(self):
        super(TestSaleOperatingUnit, self).setUp()
        cr, uid, context = self.cr, self.uid, {}
        data_model = self.registry('ir.model.data')
        self.res_groups = self.registry('res.groups')
        self.partner_model = self.registry('res.partner')
        self.res_users_model = self.registry('res.users')
        self.shop_model = self.registry('sale.shop')
        self.sale_model = self.registry('sale.order')
        self.sale_order_model = self.registry('sale.order.line')
        self.acc_move_model = self.registry('account.move')
        self.res_company_model = self.registry('res.company')
        self.product_model = self.registry('product.product')
        self.operating_unit_model = self.registry('operating.unit')
        self.company_model = self.registry('res.company')
        self.warehouse_model = self.registry('stock.warehouse')
        # company
        self.company = data_model.get_object(cr, uid, 'base', 'main_company')
        self.grp_sale_user = data_model.get_object(cr, uid, 'base',
                                                  'group_sale_manager')
        # Main Operating Unit
        self.ou1 = data_model.get_object(cr, uid, 'operating_unit',
                                         'main_operating_unit')
        # B2B Operating Unit
        self.b2b = data_model.get_object(cr, uid, 'operating_unit',
                                         'b2b_operating_unit')
        # B2C Operating Unit
        self.b2c = data_model.get_object(cr, uid, 'operating_unit',
                                         'b2c_operating_unit')
        # B2C Warehouse
        self.warehouse2 = data_model.get_object(cr, uid,
                                                'stock_operating_unit',
                                                'stock_warehouse_b2c')
        # Payment Term
        self.pay = data_model.get_object(cr, uid, 'account',
                                         'account_payment_term_immediate')
        # Customer
        self.customer = data_model.get_object(cr, uid, 'base',
                                         'res_partner_2')
        # Price list
        self.pricelist = data_model.get_object(cr, uid, 'product',
                                         'list0')
        # Partner
        self.partner1 = data_model.get_object(cr, uid, 'base',
                                              'res_partner_1')
        # Products
        self.product1 = data_model.get_object(cr, uid, 'product',
                                              'product_product_7')
        self.product2 = data_model.get_object(cr, uid, 'product',
                                              'product_product_9')
        self.product3 = data_model.get_object(cr, uid, 'product',
                                              'product_product_11')
        # Create user1
        self.user1_id = self._create_user(cr, uid, 'user_1',
                                          [self.grp_sale_user],
                                          self.company, [self.ou1, self.b2c],
                                          context=context)
        # Create user2
        self.user2_id = self._create_user(cr, uid, 'user_2',
                                          [self.grp_sale_user],
                                          self.company, [self.b2c],
                                          context=context)
        # Shop1
        self.shop1 = data_model.get_object(cr, uid, 'sale',
                                         'sale_shop_1')
        # Create Shop2
        self.shop2_id = self._create_shop(cr, self.user2_id, self.warehouse2,
                                          self.pay, self.company, self.b2c,
                                          context=context)
        # Create Sale Order1
        self.sale1_id = self._create_sale_order(cr, self.user1_id,
                                                self.customer, self.product1,
                                                self.pricelist, self.shop1.id,
                                                self.ou1, context=context)
        # Create Sale Order2
        self.sale2_id = self._create_sale_order(cr, self.user2_id,
                                                self.customer, self.product1,
                                                self.pricelist, self.shop2_id,
                                                self.b2c, context=context)

    def _create_user(self, cr, uid, login, groups, company, operating_units,
                     context=None):
        """Create a user."""
        group_ids = [group.id for group in groups]
        user_id = self.res_users_model.create(cr, uid, {
            'name': 'Test Sales User',
            'login': login,
            'password': 'demo',
            'email': 'example@yourcompany.com',
            'company_id': company.id,
            'company_ids': [(4, company.id)],
            'operating_unit_ids': [(4, ou.id) for ou in operating_units],
            'groups_id': [(6, 0, group_ids)]
        })
        return user_id

    def _create_shop(self, cr, uid, warehouse, pay, company, operating_unit,
                     context=None):
        """Create a shop."""
        shop_id = self.shop_model.create(cr, uid, {
            'name': 'Test Shop',
            'warehouse_id': warehouse.id,
            'payment_default_id': pay.id,
            'company_id': company.id,
            'operating_unit_id': operating_unit.id,
        })
        return shop_id

    def _create_sale_order(self, cr, uid, customer, product, pricelist, shop,
                           operating_unit, context=None):
        """Create a sale order."""
        sale_id = self.sale_model.create(cr, uid, {
            'partner_id': customer.id,
            'partner_invoice_id': customer.id,
            'partner_shipping_id': customer.id,
            'pricelist_id': pricelist.id,
            'shop_id': shop,
            'operating_unit_id': operating_unit.id
        })
        self.sale_order_model.create(cr, uid, {
            'order_id': sale_id,
            'product_id': product.id,
            'name': 'Sale Order Line'
        })
        return sale_id

    def test_security(self):
        """Test Sale Operating Unit"""
#        # User 2 is only assigned to Operating Unit B2C, and cannot
#        # Access Sales order from Main Operating Unit.
        sale_ids = self.sale_model.search(self.cr, self.user2_id,
                                         [('operating_unit_id', '=',
                                           self.ou1.id)])
        self.assertEqual(sale_ids, [], 'User 2 should not have access to '
                                       'OU %s' % self.ou1.name)
