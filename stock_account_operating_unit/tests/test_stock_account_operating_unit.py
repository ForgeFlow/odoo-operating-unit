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
        self.invoice_model = self.registry('account.invoice')
        self.journal_model = self.registry('account.journal')
        self.res_company_model = self.registry('res.company')
        self.product_model = self.registry('product.product')
        self.product_ctg_model = self.registry('product.category')
        self.inv_line_model = self.registry('account.invoice.line')
        self.acc_type_model = self.registry('account.account.type')
        self.operating_unit_model = self.registry('operating.unit')
        self.company_model = self.registry('res.company')
        self.move_model = self.registry('stock.move')
        self.res_users_model = self.registry('res.users')
        self.picking_model = self.registry('stock.picking')
        self.picking_partial_model = self.registry('stock.partial.picking')
        self.warehouse_model = self.registry('stock.warehouse')
        self.location_model = self.registry('stock.location')
        # company
        self.company = data_model.get_object(cr, uid, 'base', 'main_company')
        # groups
#        self.group_purchase_user = data_model.get_object(cr, uid, 'purchase',
#                                                         'group_purchase_user')
        self.group_stock_manager = data_model.get_object(cr, uid, 'stock',
                                                         'group_stock_manager')
        self.grp_acc_user = data_model.get_object(cr, uid, 'account',
                                                  'group_account_invoice')
        self.grp_stock_user = data_model.get_object(cr, uid, 'stock',
                                                  'group_stock_user')
#        self.grp_inv_val = data_model.get_object(cr, uid, 'res_groups',
#                                                  'group_inventory_valuation')
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
        self.stock_location_stock = data_model.get_object(cr, uid, 'stock',
                                                    'stock_location_stock')
        self.supplier_location =\
            data_model.get_object(cr, uid, 'stock', 'stock_location_suppliers')
        self.location_b2c_id = data_model.get_object(cr, uid,
                                                     'stock_operating_unit',
                                                     'stock_location_b2c')
#        self.data_account_type_equity = data_model.get_object(cr, uid,
#                                                     'account',
#                                                     'account.data_account_type_equity')
#        self.data_acc_expense = data_model.get_object(cr, uid,
#                                                     'account',
#                                                     'data_account_type_expense')
#        self.data_acc_asset = data_model.get_object(cr, uid,
#                                                     'account',
#                                                     'data_account_type_asset')
        # Create user1
        self.user1_id = self._create_user(cr, uid, 'stock_account_user_1',
                                          [self.grp_stock_user, self.grp_acc_user, self.group_stock_manager],
                                          self.company, [self.ou1, self.b2c],
                                          context=context)

        # Create user2
        self.user2_id = self._create_user(cr, uid, 'stock_account_user_2',
                                          [self.grp_stock_user, self.grp_acc_user, self.group_stock_manager],
                                          self.company, [self.b2c],
                                          context=context)

#        # Create cash - test account
        self.account_id = self._create_account(cr, uid, self.company,
                                               context=context)
        self.account_id1 = self._create_account1(cr, uid, self.company,
                                               context=context)
        self.account_id2 = self._create_account2(cr, uid, self.company,
                                               context=context)

#    Create Product
        self.product_id = self._create_product(cr, uid, self.user1_id, context=context)

        # Create Incoming Shipments
        self.picking_in1_id = self._create_picking(cr, uid, self.user1_id,
                                                   self.ou1.id,
                                                   'in',
                                                   self.supplier_location.id,
                                                   self.stock_location_stock.id)
        self.picking_model.draft_validate(cr, self.user1_id, [self.picking_in1_id], context=context)
        picking_browse_id = self.picking_model.browse(cr, self.user1_id, self.picking_in1_id, context=context)
        print "picking_browse_id.state ###########################", picking_browse_id.state
        partial_vals =\
            self.picking_partial_model.default_get(cr, self.user1_id,
                                                   ['move_ids', 'date',
                                                    'picking_id'],
                                                   context=context)
        print "\n\n#######    ", partial_vals
        moves = []
        for move in partial_vals.pop('move_ids', []):
            moves.append((0, 0, move))
        partial_vals.update({'move_ids': moves})
        print "\n\n&&&&&&&&&&&    ", partial_vals
        partial_id = self.picking_partial_model.create(cr, self.user1_id, partial_vals, context=context)
#        picking_partial_id = picking_partial_fields['picking_id']
        self.picking_partial_model.do_partial(cr, uid, [partial_id], context=context)
        picking_browse_id = self.picking_model.browse(cr, self.user1_id, self.picking_in1_id, context=context)
        print "picking_browse_id.state 2222222222222222222222222222", picking_browse_id.state
#        self.picking_in2_id = self._create_picking(cr, uid, self.user2_id,
#                                                   self.b2c.id,
#                                                   'in',
#                                                   self.supplier_location.id,
#                                                   self.location_b2c_id.id)
#        # Create Internal Shipment
#        self.picking_int_id = self._create_picking(cr, uid, self.user1_id,
#                                                   self.b2c.id,
#                                                   'internal',
#                                                   self.stock_location_stock.id,
#                                                   self.location_b2c_id.id)

    def _create_user(self, cr, uid, login, groups, company, operating_units,
                     context=None):
        print "Create a user %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
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

    def _create_picking(self, cr, uid, user_id, ou_id, picking_type,
                        src_loc_id, dest_loc_id):
        print "Create a Picking &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
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

#    def test_pickings(self):
#        """Test Pickings of Stock Account Operating Unit"""
#        cr = self.cr
#        picking_ids = self.picking_model.\
#            search(cr, self.user1_id, [('id', '=', self.picking_in1_id)])
#        self.assertNotEqual(picking_ids, [], '')
#        picking_ids = self.picking_model.\
#            search(cr, self.user2_id, [('id', '=', self.picking_in2_id)])
#        self.assertNotEqual(picking_ids, [], '')
#        picking_ids = self.picking_model.\
#            search(cr, self.user1_id, [('id', '=', self.picking_int_id)])
#        self.assertNotEqual(picking_ids, [], '')

#    def _check_move_accounts(self, cr, uid, invoice_id):
#        """
#        Check if journal entries of the invoice have same operating units.
#        """
#        all_op_units = all(move_line.operating_unit_id.id == self.b2b.id for
#                           move_line in self.invoice.move_id.line_id)
#        # Assert if journal entries of the invoice
#        # have different operating units
#        self.assertNotEqual(all_op_units, False, 'Journal Entries have\
#                            different Operating Units.')

    def _create_account(self, cr, uid, company, context=None):
        print "Create an account 0000000000000000000000000000000000000000000"
        """Create an account."""
        type_ids = self.acc_type_model.search(cr, uid, [('code', '=', 'equity')])
        account_id = self.account_model.create(cr, uid, {
            'name': 'Goods Received Not Invoiced',
            'code': 'grni',
            'type': 'liquidity',
            'user_type': type_ids and type_ids[0],
            'company_id': company.id
        })
        return account_id

    def _create_account1(self, cr, uid, company, context=None):
        print "Create an account 1111111111111111111111111111111111111111111"
        """Create an account."""
        type_ids = self.acc_type_model.search(cr, uid, [('code', '=', 'expense')])
        account_id = self.account_model.create(cr, uid, {
            'name': 'COGS',
            'code': 'cogs',
            'type': 'liquidity',
            'user_type': type_ids and type_ids[0],
            'company_id': company.id
        })
        return account_id

    def _create_account2(self, cr, uid, company, context=None):
        print "Create an account  22222222222222222222222222222222222222222222222"
        """Create an account."""
        type_ids = self.acc_type_model.search(cr, uid, [('code', '=', 'asset')])
        account_id = self.account_model.create(cr, uid, {
            'name': 'Inventory',
            'code': 'inventory',
            'type': 'liquidity',
            'user_type': type_ids and type_ids[0],
            'company_id': company.id
        })
        return account_id

    def _create_inter_ou_account(self, cr, uid, company, context=None):
        """Create an account."""
        print "Create an INTER - account $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        type_ids = self.acc_type_model.search(cr, uid,
                                              [('code', '=', 'equity')])
        account_id = self.account_model.create(cr, uid, {
            'name': 'Inter-OU Clearing',
            'code': 'test_inter_ou',
            'type': 'other',
            'user_type': type_ids and type_ids[0],
            'company_id': company.id
        })
        self.company_model.write(cr, uid, [company.id],
                                 {'inter_ou_clearing_account_id': account_id,
                                  'ou_is_self_balanced': True})
        return True

    def _create_product(self, cr, uid, user_id, context=None):
        print "Create a product %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
        """Create a Product."""
#        group_ids = [group.id for group in groups]
        product_ctg_id = self.product_ctg_model.create(cr, user_id, {
            'name': 'test_product_ctg',
            'property_stock_valuation_account_id': self.account_id2
        })
        product_id = self.product_model.create(cr, user_id, {
            'name': 'test_product',
            'categ_id': product_ctg_id,
            'type': 'product',
            'standard_price': 1.0,
            'list_price': 1.0,
            'valuation': 'real_time',
            'property_stock_account_input': self.account_id,
            'property_stock_account_output': self.account_id1,
        })
        print "product_id ============================================", product_id
        return product_id

    def _check_balance(self, cr, uid, account_id, acc_type='clearing',
                       context=None):
        print "_check_balance ###############################################"
        """
        Check the balance of the account based on different operating units.
        """
        # Check balance for all operating units
        domain = [('account_id', '=', account_id)]
        balance = self._get_balance(cr, uid, domain)
        self.assertEqual(balance, 1, 'Balance is 1 for all Operating Units.')
        # Check balance for operating Main units
        domain = [('account_id', '=', account_id),
                  ('operating_unit_id', '=', self.ou1.id)]
        balance = self._get_balance(cr, uid, domain)
        if acc_type == 'cash':
            self.assertEqual(balance, 1,
                             'Balance is 1 for Operating Unit Main.')
        else:
            self.assertEqual(balance, 1,
                             'Balance is 1 for Operating Unit Main.')
#        # Check balance for operating B2C units
        domain = [('account_id', '=', account_id),
                  ('operating_unit_id', '=', self.b2c.id)]
        balance = self._get_balance(cr, uid, domain)
        if acc_type == 'cash':
            self.assertEqual(balance, 0,
                             'Balance is 0 for Operating Unit B2C.')
        else:
            self.assertEqual(balance, 0,
                             'Balance is 0 for Operating Unit B2C.')

    def _check_balance1(self, cr, uid, account_id, acc_type='clearing',
                       context=None):
        print "_check_balance 111111111111111111111111111111111111111111111"
        """
        Check the balance of the account based on different operating units.
        """
        # Check balance for all operating units
        domain = [('account_id', '=', account_id)]
        balance = self._get_balance(cr, uid, domain)
        self.assertEqual(balance, -1, 'Balance is 1 for all Operating Units.')
        # Check balance for operating Main units
        domain = [('account_id', '=', account_id),
                  ('operating_unit_id', '=', self.ou1.id)]
        balance = self._get_balance(cr, uid, domain)
        if acc_type == 'cash':
            self.assertEqual(balance, 0,
                             'Balance is 0 for Operating Unit Main.')
        else:
            self.assertEqual(balance, 0,
                             'Balance is 0 for Operating Unit Main.')
#        # Check balance for operating B2C units
#        domain = [('account_id', '=', account_id),
#                  ('operating_unit_id', '=', self.b2c.id)]
#        balance = self._get_balance(cr, uid, domain)
#        if acc_type == 'cash':
#            self.assertEqual(balance, -1,
#                             'Balance is -1 for Operating Unit B2C.')
#        else:
#            self.assertEqual(balance, -1,
#                             'Balance is -1 for Operating Unit B2C.')

    def _get_balance(self, cr, uid, domain):
        """
        Call read_group method and return the balance of particular account.
        """
        print "get_balance *********************************************"
        aml_rec = self.aml_model.read_group(cr, uid, domain,
                                            ['debit', 'credit', 'account_id'],
                                            ['account_id'])[0]
        return aml_rec.get('debit', 0) - aml_rec.get('credit', 0)

#    def test_invoice(self):
#        """Test that when an invoice is created the operating unit is
#        passed to the accounting journal items"""
#        cr, uid, context = self.cr, self.uid, {}
#        # Check Operating Units in journal entries
#        self._check_move_accounts(cr,  self.user1_id, self.invoice_id)
#
    def test_cross_ou_journal_entry(self):
        """Test that when I create a manual journal entry with multiple
        operating units, new cross-operating unit entries are created
        automatically when the journal entry is posted, ensuring that each
        OU is self-balanced."""
        print "voila $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        cr, uid, context = self.cr, self.uid, {}
        # Create inter-ou - test account
        self._create_inter_ou_account(cr, uid, self.company, context=context)
#        # Create & post journal entries
#        self._create_account_move(cr, self.user1_id, self.account_id,
#                                  context=context)
        # Check the balance of the account - inventory
        self._check_balance(cr, self.user1_id, self.account_id2,
                            acc_type='cash',
                            context=context)
        # Check the balance of the account - grni
#        self._check_balance1(cr, self.user1_id, self.account_id,
#                            acc_type='cash',
#                            context=context)

#        clearing_account_id = self.company.inter_ou_clearing_account_id.id
#        self._check_balance(cr, self.user1_id, clearing_account_id,
#                            acc_type='clearing', context=context)

#    def test_security(self):
#        """Test Account Operating Unit"""
#        # User 2 is only assigned to Operating Unit B2C, and cannot list
#        # Journal Entries from Operating Unit B2B.
#        move_ids = self.aml_model.search(self.cr, self.user2_id,
#                                         [('operating_unit_id', '=',
#                                           self.b2b.id)])
#        self.assertEqual(move_ids, [], 'user_2 should not have access to '
#                                       'OU %s' % self.b2b.name)
