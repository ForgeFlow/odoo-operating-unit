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
        self.stock_location_stock = data_model.get_object(cr, uid, 'stock',
                                                    'stock_location_stock')
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

#        # Create cash - test account
        self.account_id = self._create_account(cr, uid, self.company,
                                                        context=context)
        self.account_id1 = self._create_account1(cr, uid, self.company,
                                                        context=context)
        self.account_id2 = self._create_account2(cr, uid, self.company,
                                                        context=context)
        self.account_id3 = self._create_inter_ou_account(cr, uid, self.company,
                                                         context=context)
#    Create Product
        self.product_id = self._create_product(cr, uid, context=context)

        # Create Incoming Shipments
        self.picking_in1_id =\
            self._create_picking(cr, uid, self.user1_id, self.ou1.id, 'in',
                                 self.supplier_location.id,
                                 self.stock_location_stock.id)
        self._confirm_receive(cr, self.user1_id, self.picking_in1_id,
                              context=context)
        self._check_balance_inv(cr, uid, self.account_id2,
                            acc_type='cash',
                            context=context)
        self._check_balance_grni(cr, uid, self.account_id,
                            acc_type='cash',
                            context=context)
        self.picking_in2_id = self._create_picking(cr, uid, self.user2_id,
                                                   self.b2c.id,
                                                   'in',
                                                   self.supplier_location.id,
                                                   self.location_b2c_id.id)
        self._confirm_receive(cr, self.user2_id, self.picking_in2_id,
                              context=context)
        self._check_balance_2_inv(cr, uid, self.account_id2,
                            acc_type='cash',
                            context=context)
        self._check_balance_2_grni(cr, uid, self.account_id,
                            acc_type='cash',
                            context=context)

#        # Create Internal Shipment
        self.picking_int_id =\
            self._create_picking(cr, uid, self.user1_id, self.b2c.id,
                                 'internal', self.stock_location_stock.id,
                                 self.location_b2c_id.id)
        self._confirm_receive(cr, self.user1_id, self.picking_int_id,
                              context=context)
        self._check_balance_int(cr, uid, self.account_id2,
                            acc_type='cash',
                            context=context)
#        self._check_balance_int_grni(cr, uid, self.account_id3,
#                            acc_type='cash',
#                            context=context)

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

    def _create_account(self, cr, uid, company, context=None):
        """Create an account."""
        type_ids = self.acc_type_model.search(cr, uid,
                                              [('code', '=', 'equity')])
        account_id = self.account_model.create(cr, uid, {
            'name': 'Goods Received Not Invoiced',
            'code': 'grni',
            'type': 'liquidity',
            'user_type': type_ids and type_ids[0],
            'company_id': company.id
        })
        return account_id

    def _create_account1(self, cr, uid, company, context=None):
        """Create an account."""
        type_ids = self.acc_type_model.search(cr, uid,
                                              [('code', '=', 'expense')])
        account_id = self.account_model.create(cr, uid, {
            'name': 'COGS',
            'code': 'cogs',
            'type': 'liquidity',
            'user_type': type_ids and type_ids[0],
            'company_id': company.id
        })
        return account_id

    def _create_account2(self, cr, uid, company, context=None):
        """Create an account."""
        type_ids = self.acc_type_model.search(cr, uid,
                                              [('code', '=', 'asset')])
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
        return account_id

    def _create_product(self, cr, uid, context=None):
        """Create a Product."""
#        group_ids = [group.id for group in groups]
        product_ctg_id = self.product_ctg_model.create(cr, uid, {
            'name': 'test_product_ctg',
            'property_stock_valuation_account_id': self.account_id2
        })
        product_id = self.product_model.create(cr, uid, {
            'name': 'test_product',
            'categ_id': product_ctg_id,
            'type': 'product',
            'standard_price': 1.0,
            'list_price': 1.0,
            'valuation': 'real_time',
            'property_stock_account_input': self.account_id,
            'property_stock_account_output': self.account_id1,
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

    def _check_balance_inv(self, cr, uid, account_id, acc_type='clearing',
                       context=None):
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

    def _check_balance_grni(self, cr, uid, account_id, acc_type='clearing',
                       context=None):
        """
        Check the balance of the account based on different operating units.
        """
        # Check balance for all operating units
        domain = [('account_id', '=', account_id)]
        balance = self._get_balance(cr, uid, domain)
        self.assertEqual(balance, -1, 'Balance is -1 for all Operating Units.')

    def _check_balance_2_inv(self, cr, uid, account_id, acc_type='clearing',
                       context=None):
        """
        Check the balance of the account based on different operating units.
        """
        # Check balance for all operating units
        domain = [('account_id', '=', account_id)]
        balance = self._get_balance(cr, uid, domain)
        self.assertEqual(balance, 2, 'Balance is 2 for all Operating Units.')
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

    def _check_balance_2_grni(self, cr, uid, account_id, acc_type='clearing',
                       context=None):
        """
        Check the balance of the account based on different operating units.
        """
        # Check balance for all operating units
        domain = [('account_id', '=', account_id)]
        balance = self._get_balance(cr, uid, domain)
        self.assertEqual(balance, -2, 'Balance is -2 for all Operating Units.')

    def _check_balance_int(self, cr, uid, account_id, acc_type='clearing',
                       context=None):
        """
        Check the balance of the account based on different operating units.
        """
        # Check balance for all operating units
        domain = [('account_id', '=', account_id)]
        balance = self._get_balance(cr, uid, domain)
        self.assertEqual(balance, 2, 'Balance is 2 for all Operating Units.')
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
        domain = [('account_id', '=', account_id),
                  ('operating_unit_id', '=', self.b2c.id)]
        balance = self._get_balance(cr, uid, domain)
        if acc_type == 'cash':
            self.assertEqual(balance, 2,
                             'Balance is 2 for Operating Unit B2C.')
        else:
            self.assertEqual(balance, 2,
                             'Balance is 2 for Operating Unit B2C.')

    def _check_balance_int_grni(self, cr, uid, account_id, acc_type='clearing',
                       context=None):
        """
        Check the balance of the account based on different operating units.
        """
        # Check balance for all operating units
        domain = [('account_id', '=', account_id)]
        balance = self._get_balance(cr, uid, domain)
        self.assertEqual(balance, 0, 'Balance is 0 for all Operating Units.')
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
            self.assertEqual(balance, -1,
                             'Balance is -1 for Operating Unit B2C.')
        else:
            self.assertEqual(balance, -1,
                             'Balance is -1 for Operating Unit B2C.')

    def _get_balance(self, cr, uid, domain):
        """
        Call read_group method and return the balance of particular account.
        """
        if self.aml_model.read_group(cr, uid, domain,
                                            ['debit', 'credit', 'account_id'],
                                            ['account_id']) and\
                                            self.aml_model.read_group(cr, uid,
                                                                      domain,
                                            ['debit', 'credit', 'account_id'],
                                            ['account_id'])[0]:
            aml_rec = self.aml_model.read_group(cr, uid, domain,
                                                ['debit', 'credit',
                                                 'account_id'],
                                                ['account_id'])[0]
            return aml_rec.get('debit', 0) - aml_rec.get('credit', 0)

    def test_stock_account_ou(self):
        """Test of Stock Account Operating Unit"""
        return True
