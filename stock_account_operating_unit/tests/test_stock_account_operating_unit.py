# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import netsvc
from openerp.tests import common


class TestStockAccountOperatingUnit(common.TransactionCase):

    def setUp(self):
        super(TestStockAccountOperatingUnit, self).setUp()
        cr, uid, context = self.cr, self.uid, {}
        data_model = self.registry('ir.model.data')
        self.res_groups = self.registry('res.groups')
        self.partner_model = self.registry('res.partner')
        self.res_users_model = self.registry('res.users')
        self.acc_move_model = self.registry('account.move')
        self.aml_model = self.registry('account.move.line')
        self.account_model = self.registry('account.account')
        self.product_model = self.registry('product.product')
        self.product_ctg_model = self.registry('product.category')
        self.acc_type_model = self.registry('account.account.type')
        self.operating_unit_model = self.registry('operating.unit')
        self.company_model = self.registry('res.company')
        self.move_model = self.registry('stock.move')
        self.picking_model = self.registry('stock.picking')
        self.picking_partial_model = self.registry('stock.partial.picking')
        # company
        self.company = data_model.get_object(cr, uid, 'base', 'main_company')
        # groups
        self.group_stock_manager = data_model.get_object(cr, uid, 'stock',
                                                         'group_stock_manager')
        self.grp_acc_user = data_model.get_object(cr, uid, 'account',
                                                  'group_account_invoice')
        self.grp_stock_user = data_model.get_object(cr, uid, 'stock',
                                                    'group_stock_user')
        # Main Operating Unit
        self.ou1 = data_model.get_object(cr, uid, 'operating_unit',
                                         'main_operating_unit')
        # B2B Operating Unit
        self.b2b = data_model.get_object(cr, uid, 'operating_unit',
                                         'b2b_operating_unit')
        # B2C Operating Unit
        self.b2c = data_model.get_object(cr, uid, 'operating_unit',
                                         'b2c_operating_unit')
        # Partner
        self.partner1 = data_model.get_object(cr, uid, 'base',
                                              'res_partner_1')
        self.stock_location_stock = data_model.get_object(
                cr, uid, 'stock', 'stock_location_stock')
        self.supplier_location =\
            data_model.get_object(cr, uid, 'stock', 'stock_location_suppliers')
        self.location_b2c_id = data_model.get_object(cr, uid,
                                                     'stock_operating_unit',
                                                     'stock_location_b2c')
        # Create user1
        self.user1_id =\
            self._create_user(cr, uid, 'stock_account_user_1',
                              [self.grp_stock_user, self.grp_acc_user,
                               self.group_stock_manager],
                              self.company, [self.ou1, self.b2c],
                              context=context)
        # Create user2
        self.user2_id =\
            self._create_user(cr, uid, 'stock_account_user_2',
                              [self.grp_stock_user, self.grp_acc_user,
                               self.group_stock_manager],
                              self.company, [self.b2c], context=context)
        # Create account for Goods Received Not Invoiced
        acc_type = 'equity'
        name = 'Goods Received Not Invoiced'
        code = 'grni'
        self.account_grni_id = self._create_account(cr, uid, acc_type, name,
                                                    code, self.company,
                                                    context=None)

        # Create account for Cost of Goods Sold
        acc_type = 'expense'
        name = 'Cost of Goods Sold'
        code = 'cogs'
        self.account_cogs_id = self._create_account(cr, uid, acc_type, name,
                                                    code, self.company,
                                                    context=None)
        # Create account for Inventory
        acc_type = 'asset'
        name = 'Inventory'
        code = 'inventory'
        self.account_inventory_id = self._create_account(cr, uid, acc_type,
                                                         name, code,
                                                         self.company,
                                                         context=None)
        # Create account for Inter-OU Clearing
        acc_type = 'equity'
        name = 'Inter-OU Clearing'
        code = 'inter_ou'
        self.account_inter_ou_clearing_id = self._create_account(
                cr, uid, acc_type, name, code, self.company, context=None)

        # Update company data
        self.company_model.write(cr, uid, [self.company.id],
                                 {'inter_ou_clearing_account_id':
                                  self.account_inter_ou_clearing_id,
                                  'ou_is_self_balanced': True})

        # Create Product
        self.product_id = self._create_product(cr, uid, context=context)

    def _create_user(self, cr, uid, login, groups, company, operating_units,
                     context=None):
        """Create a user."""
        group_ids = [group.id for group in groups]
        user_id = self.res_users_model.create(cr, uid, {
            'name': 'Test Stock Account User',
            'login': login,
            'password': 'demo',
            'email': 'example@yourcompany.com',
            'company_id': company.id,
            'company_ids': [(4, company.id)],
            'operating_unit_ids': [(4, ou.id) for ou in operating_units],
            'groups_id': [(6, 0, group_ids)]
        })
        return user_id

    def _create_account(self, cr, uid, acc_type, name, code, company,
                        context=None):
        """Create an account."""
        type_ids = self.acc_type_model.search(cr, uid,
                                              [('code', '=', acc_type)])
        account_grni_id = self.account_model.create(cr, uid, {
            'name': name,
            'code': code,
            'type': 'other',
            'user_type': type_ids and type_ids[0],
            'company_id': company.id
        })
        return account_grni_id

    def _create_product(self, cr, uid, context=None):
        """Create a Product."""
#        group_ids = [group.id for group in groups]
        product_ctg_id = self.product_ctg_model.create(cr, uid, {
            'name': 'test_product_ctg',
            'property_stock_valuation_account_id': self.account_inventory_id
        })
        product_id = self.product_model.create(cr, uid, {
            'name': 'test_product',
            'categ_id': product_ctg_id,
            'type': 'product',
            'standard_price': 1.0,
            'list_price': 1.0,
            'valuation': 'real_time',
            'property_stock_account_input': self.account_grni_id,
            'property_stock_account_output': self.account_cogs_id,
        })
        return product_id

    def _create_picking(self, cr, uid, user_id, ou_id, picking_type,
                        src_loc_id, dest_loc_id):
        """Create a Picking."""
        picking_id = self.picking_model.create(cr, user_id, {
            'type': picking_type,
            'location_id': src_loc_id,
            'location_dest_id': dest_loc_id,
            'operating_unit_id': ou_id,
        })
        self.move_model.create(cr, user_id, {
            'name': 'a move',
            'product_id': self.product_id,
            'product_qty': 1.0,
            'product_uom': 1,
            'picking_id': picking_id,
            'location_id': src_loc_id,
            'location_dest_id': dest_loc_id,
        })
        return picking_id

    def _confirm_receive(self, cr, uid, pick_id, context=None):
        self.picking_model.draft_validate(cr, uid, [pick_id], context=context)
        partial_vals =\
            self.picking_partial_model.default_get(cr, uid,
                                                   ['move_ids', 'date',
                                                    'picking_id'],
                                                   context=context)
        moves = []
        for move in partial_vals.pop('move_ids', []):
            moves.append((0, 0, move))
        partial_vals.update({'move_ids': moves})
        partial_id = self.picking_partial_model.create(cr, uid, partial_vals,
                                                       context=context)
        self.picking_partial_model.do_partial(cr, uid, [partial_id],
                                              context=context)

    def _check_account_balance(self, cr, uid, account_id, operating_unit=None,
                               expected_balance=0.0, context=None):
        """
        Check the balance of the account based on different operating units.
        """
        domain = [('account_id', '=', account_id)]
        if operating_unit:
            domain.extend([('operating_unit_id', '=', operating_unit.id)])

        balance = self._get_balance(cr, uid, domain)
        if operating_unit:
            self.assertEqual(
                    balance, expected_balance,
                    'Balance is not %s for Operating Unit %s.'
                    % (str(expected_balance), operating_unit.name))
        else:
            self.assertEqual(
                    balance, expected_balance,
                    'Balance is not %s for all Operating Units.'
                    % str(expected_balance)) \


    def _get_balance(self, cr, uid, domain):
        """
        Call read_group method and return the balance of particular account.
        """
        aml_rec = self.aml_model.read_group(cr, uid, domain,
                                            ['debit', 'credit', 'account_id'],
                                            ['account_id'])
        if aml_rec:
            return aml_rec[0].get('debit', 0) - aml_rec[0].get('credit', 0)
        else:
            return 0.0

    def test_pickings(self):
        """Test account balances during receiving stock into the main
        operating unit, then into b2c operating unit, and then transfer stock
        from main ou to b2c."""
        cr, uid, context = self.cr, self.uid, {}
        # Create Incoming Shipment 1
        picking_id =\
            self._create_picking(cr, uid, self.user1_id, self.ou1.id, 'in',
                                 self.supplier_location.id,
                                 self.stock_location_stock.id)
        # Receive it
        self._confirm_receive(cr, self.user1_id, picking_id, context=context)
        # GL account ‘Inventory’ has balance 1 irrespective of the OU
        expected_balance = 1.0
        self._check_account_balance(cr, uid, self.account_inventory_id,
                                    operating_unit=None,
                                    expected_balance=expected_balance,
                                    context=context)
        # GL account ‘Inventory’ has balance 1 on OU main_operating_unit
        expected_balance = 1.0
        self._check_account_balance(cr, uid, self.account_inventory_id,
                                    operating_unit=self.ou1,
                                    expected_balance=expected_balance,
                                    context=context)
        # GL account ‘Inventory’ has balance 0 on OU main_operating_unit
        expected_balance = 0.0
        self._check_account_balance(cr, uid, self.account_inventory_id,
                                    operating_unit=self.b2c,
                                    expected_balance=expected_balance,
                                    context=context)
        # GL account ‘Goods Received Not Invoiced’ has balance - 1
        # irrespective of the OU
        expected_balance = -1.0
        self._check_account_balance(cr, uid, self.account_grni_id,
                                    operating_unit=None,
                                    expected_balance=expected_balance,
                                    context=context)
        # GL account ‘Goods Received Not Invoiced’ has balance -1 on Main OU
        expected_balance = -1.0
        self._check_account_balance(cr, uid, self.account_grni_id,
                                    operating_unit=self.ou1,
                                    expected_balance=expected_balance,
                                    context=context)
        # GL account ‘Goods Received Not Invoiced’ has balance 0 on OU b2c
        expected_balance = 0.0
        self._check_account_balance(cr, uid, self.account_grni_id,
                                    operating_unit=self.b2c,
                                    expected_balance=expected_balance,
                                    context=context)

        # Create Incoming Shipment 2
        picking_id = self._create_picking(cr, uid, self.user2_id, self.b2c.id,
                                          'in', self.supplier_location.id,
                                          self.location_b2c_id.id)
        # Receive it
        self._confirm_receive(cr, self.user2_id, picking_id, context=context)

        # GL account ‘Inventory’ has balance 2 irrespective of the OU
        expected_balance = 2.0
        self._check_account_balance(cr, uid, self.account_inventory_id,
                                    operating_unit=None,
                                    expected_balance=expected_balance,
                                    context=context)
        # GL account ‘Inventory’ has balance 1 on OU main_operating_unit
        expected_balance = 1.0
        self._check_account_balance(cr, uid, self.account_inventory_id,
                                    operating_unit=self.ou1,
                                    expected_balance=expected_balance,
                                    context=context)
        # GL account ‘Inventory’ has balance 1 on OU b2c
        expected_balance = 1.0
        self._check_account_balance(cr, uid, self.account_inventory_id,
                                    operating_unit=self.b2c,
                                    expected_balance=expected_balance,
                                    context=context)
        # GL account ‘Goods Received Not Invoiced’ has balance - 2
        # irrespective of the OU
        expected_balance = -2.0
        self._check_account_balance(cr, uid, self.account_grni_id,
                                    operating_unit=None,
                                    expected_balance=expected_balance,
                                    context=context)
        # GL account ‘Goods Received Not Invoiced’ has balance -1 on Main OU
        expected_balance = -1.0
        self._check_account_balance(cr, uid, self.account_grni_id,
                                    operating_unit=self.ou1,
                                    expected_balance=expected_balance,
                                    context=context)
        # GL account ‘Goods Received Not Invoiced’ has balance 0 on OU b2c
        expected_balance = -1.0
        self._check_account_balance(cr, uid, self.account_grni_id,
                                    operating_unit=self.b2c,
                                    expected_balance=expected_balance,
                                    context=context)

        # Create Internal Transfer
        picking_id =\
            self._create_picking(cr, uid, self.user1_id, self.b2c.id,
                                 'internal', self.stock_location_stock.id,
                                 self.location_b2c_id.id)
        # Receive it
        self._confirm_receive(cr, self.user1_id, picking_id,
                              context=context)
        # GL account ‘Inventory’ has balance 2 irrespective of the OU
        expected_balance = 2.0
        self._check_account_balance(cr, uid, self.account_inventory_id,
                                    operating_unit=None,
                                    expected_balance=expected_balance,
                                    context=context)
        # GL account ‘Inventory’ has balance 0 on OU main_operating_unit
        expected_balance = 0.0
        self._check_account_balance(cr, uid, self.account_inventory_id,
                                    operating_unit=self.ou1,
                                    expected_balance=expected_balance,
                                    context=context)
        # GL account ‘Inventory’ has balance 2 on OU b2c
        expected_balance = 2.0
        self._check_account_balance(cr, uid, self.account_inventory_id,
                                    operating_unit=self.b2c,
                                    expected_balance=expected_balance,
                                    context=context)
        # GL account ‘Inter-OU clearing’ has balance 0 irrespective of the OU
        expected_balance = 0.0
        self._check_account_balance(cr, uid, self.account_inter_ou_clearing_id,
                                    operating_unit=None,
                                    expected_balance=expected_balance,
                                    context=context)
