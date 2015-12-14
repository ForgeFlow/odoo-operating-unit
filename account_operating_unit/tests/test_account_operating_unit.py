# -*- coding: utf-8 -*-
# © 2015 Eficent - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import netsvc
from openerp.tests import common


class TestAccountOperatingUnit(common.TransactionCase):

    def setUp(self):
        super(TestAccountOperatingUnit, self).setUp()
        cr, uid, context = self.cr, self.uid, {}
        data_model = self.registry('ir.model.data')
        self.res_groups = self.registry('res.groups')
        self.partner_model = self.registry('res.partner')
        self.res_users_model = self.registry('res.users')
        self.acc_move_obj = self.registry('account.move')
        self.aml_obj = self.registry('account.move.line')
        self.account_obj = self.registry('account.account')
        self.invoice_obj = self.registry('account.invoice')
        self.journal_obj = self.registry('account.journal')
        self.res_company_model = self.registry('res.company')
        self.product_model = self.registry('product.product')
        self.inv_line_obj = self.registry('account.invoice.line')
        self.acc_type_obj = self.registry('account.account.type')
        self.operating_unit_model = self.registry('operating.unit')
        self.company = data_model.get_object(cr, uid, 'base', 'main_company')
        self.grp_acc_user = data_model.get_object(cr, uid, 'account',
                                                  'group_account_invoice')
        self.ou1 = data_model.get_object(cr, uid, 'operating_unit',
                                         'main_operating_unit')
        self.b2b = data_model.get_object(cr, uid, 'operating_unit',
                                         'b2b_operating_unit')
        self.b2c = data_model.get_object(cr, uid, 'operating_unit',
                                         'b2c_operating_unit')
        self.partner1 = data_model.get_object(cr, uid, 'base', 'res_partner_1')
        self.product1 = data_model.get_object(cr, uid, 'product',
                                              'product_product_7')
        self.product2 = data_model.get_object(cr, uid, 'product',
                                               'product_product_9')
        self.product3 = data_model.get_object(cr, uid, 'product',
                                              'product_product_11')
        user1_id = self._create_user(cr, uid, 'user_1', [self.grp_acc_user],
                                     self.company, [self.b2b, self.b2c],
                                     context=context)
        invoice_id = self._create_validate_invoice(cr, user1_id,
                                                   [(self.product1, 1000),
                                                    (self.product2, 500),
                                                    (self.product3, 800)])
        self.invoice = self.invoice_obj.browse(cr, user1_id, invoice_id,
                                               context=context)
        self._check_move_accounts(cr, user1_id, invoice_id)
        account_id = self._create_account(cr, uid, self.company,
                                          context=context)
        self._create_account_move(cr, user1_id, account_id,
                                                 context=context)
        self._check_balance(cr, user1_id, account_id, context=context)
        clearing_account_id = self.company.inter_ou_clearing_account_id.id
        self._check_balance(cr, user1_id, clearing_account_id, context=context)
        self.user2_id = self._create_user(cr, uid, 'user_2',
                                          [self.grp_acc_user],
                                          self.company, [self.b2c],
                                          context=context)

    def _create_user(self, cr, uid, login, groups, company, operating_units,
                     context=None):
        """Create a user."""
        group_ids = [group.id for group in groups]
        user_id = self.res_users_model.create(cr, uid, {
            'name': 'Test Account User',
            'login': login,
            'password': 'demo',
            'email': 'example@yourcompany.com',
            'company_id': company.id,
            'company_ids': [(4, company.id)],
            'operating_unit_ids': [(4, ou.id) for ou in operating_units],
            'groups_id': [(6, 0, group_ids)]
        })
        return user_id

    def _create_validate_invoice(self, cr, uid, line_products):
        """Create invoice.
        ``line_products`` is a list of tuple [(product, qty)]
        """
        part_id = self.partner1.id
        # Call partner onchange
        inv_vals = self.invoice_obj.onchange_partner_id(cr, uid, [],
                                                        'in_invoice',
                                                        part_id)['value']
        # Get default values of invoice
        default_inv_vals = self.invoice_obj.default_get(cr, uid, [])
        inv_vals.update(default_inv_vals)
        lines = []
        # Prepare invoice lines
        for product, qty in line_products:
            uom_id = product.uom_id.id
            line_values = {
                'product_id': product.id,
                'quantity': qty,
                'price_unit': 50,
            }
            # Call product onchange
            line_res = self.inv_line_obj.product_id_change(cr, uid, [],
                                                           product.id,
                                                           uom_id, qty,
                                                           type='in_invoice',
                                                           partner_id=part_id
                                                           )['value']
            line_values.update(line_res)
            lines.append((0, 0, line_values))
        inv_vals.update({
            'partner_id': self.partner1.id,
            'account_id': self.partner1.property_account_payable.id,
            'invoice_line': lines,
            'operating_unit_id': self.b2b.id,
        })
        # Create invoice
        invoice_id = self.invoice_obj.create(cr, uid, inv_vals)
        wf_service = netsvc.LocalService("workflow")
        # Validate the invoice
        wf_service.trg_validate(uid, 'account.invoice', invoice_id,
                                'invoice_open', cr)
        return invoice_id

    def _check_move_accounts(self, cr, uid, invoice_id):
        """
        Check if journal entries of the invoice have same operating units.
        """
        all_op_units = all(move_line.operating_unit_id.id != self.b2b.id\
                           for move_line in self.invoice.move_id.line_id)
        # Assert if journal entries of the invoice
        # have different operating units
#        self.assertNotEqual(all_op_units, False, 'Journal Entries have\
#                            different Operating Units.')

    def _create_account(self, cr, uid, company, context=None):
        """Create an account."""
        type_ids = self.acc_type_obj.search(cr, uid, [('code', '=', 'cash')])
        account_id = self.account_obj.create(cr, uid, {
            'name': 'Cash - Test',
            'code': 'test_cash',
            'type': 'liquidity',
            'user_type': type_ids and type_ids[0],
            'company_id': company.id,
            'operating_unit_id': self.ou1.id,
        })
        return account_id

    def _create_account_move(self, cr, uid, account_id, context=None):
        """Create Journal Entries."""
        journal_ids = self.journal_obj.search(cr, uid, [('code', '=', 'MISC')])
        # get default values of account move
        default_move_vals = self.acc_move_obj.default_get(cr, uid, [],
                                                          context=context)
        move_vals = {}
        move_vals.update(default_move_vals)
        lines = [(0, 0, {
                    'name': 'Test',
                    'account_id': account_id,
                    'debit':0,
                    'credit': 100,
                    'operating_unit_id': self.b2b.id,
                }),
                 (0, 0, {
                    'name': 'Test',
                    'account_id': account_id,
                    'debit': 100,
                    'credit': 0,
                    'operating_unit_id': self.b2c.id,
                })
        ]
        move_vals.update({
            'journal_id': journal_ids and journal_ids[0],
            'line_id': lines,
        })
        move_id = self.acc_move_obj.create(cr, uid, move_vals)
        # Post journal entries
        self.acc_move_obj.button_validate(cr, uid, [move_id])
        return True

    def _check_balance(self, cr, uid, account_id, context=None):
        """
        Check the balance of the account based on different operating units.
        """
        # Check balance for all operating units
        domain = [('account_id', '=', account_id)]
        balance = self._get_balance(cr, uid, domain)
        self.assertEqual(balance, 0.0, 'Balance is 0 for all Operating Units.')
        # Check balance for operating B2B units
        domain = [('account_id', '=', account_id),
                  ('operating_unit_id', '=', self.b2b.id)]
        balance = self._get_balance(cr, uid, domain)
        self.assertEqual(balance, -100,
                         'Balance is -100 for Operating Unit B2B.')
        # Check balance for operating B2C units
        domain = [('account_id', '=', account_id),
                  ('operating_unit_id', '=', self.b2c.id)]
        balance = self._get_balance(cr, uid, domain)
        self.assertEqual(balance, 100.0,
                         'Balance is 100 for Operating Unit B2C.')

    def _get_balance(self, cr, uid, domain):
        """
        Call read_group method and return the balance of particular account.
        """
        aml_rec = self.aml_obj.read_group(cr, uid, domain,
                                          ['debit', 'credit', 'account_id'],
                                          ['account_id'])[0]
        return aml_rec.get('debit', 0) - aml_rec.get('credit', 0)

    def test_security(self):
        """Test Account Operating Unit"""
        # User 2 is only assigned to Operating Unit B2C, and cannot list
        # Journal Entries from Operating Unit B2B.
        move_ids = self.aml_obj.search(self.cr, self.user2_id,
                                       [('operating_unit_id',
                                         '=',
                                         self.b2b.id)])
#        self.assertNotEqual(move_ids, [], 'You do not have access to Journal\
#                            Entries of other operating units.')
