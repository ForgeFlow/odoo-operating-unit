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
        self.account_obj = self.registry('account.account')
        self.invoice_obj = self.registry('account.invoice')
        self.inv_line_obj = self.registry('account.invoice.line')
        self.product_model = self.registry('product.product')
        self.partner_model = self.registry('res.partner')
        self.operating_unit_model = self.registry('operating.unit')
        self.res_users_model = self.registry('res.users')
        self.res_company_model = self.registry('res.company')
        self.acc_move_obj = self.registry('account.move')
        self.aml_obj = self.registry('account.move.line')
        self.res_groups = self.registry('res.groups')
        data_model = self.registry('ir.model.data')
        _, company_id = data_model.get_object_reference(
            cr, uid, 'base', 'main_company')
        self.company = self.res_company_model.browse(cr, uid, company_id,
                                                      context=context)
        _, group_account_user_id = data_model.get_object_reference(
            cr, uid, 'account', 'group_account_invoice')
        self.group_account_user = self.res_groups.browse(
            cr, uid, group_account_user_id, context=context)
        _, ou1_id = data_model.get_object_reference(
            cr, uid, 'operating_unit', 'main_operating_unit')
        self.ou1 = self.operating_unit_model.browse(cr, uid, ou1_id,
                                                    context=context)
        _, b2b_id = data_model.get_object_reference(
            cr, uid, 'operating_unit', 'b2b_operating_unit')
        self.b2b_id = self.operating_unit_model.browse(cr, uid, b2b_id,
                                                    context=context)
        _, b2c_id = data_model.get_object_reference(
            cr, uid, 'operating_unit', 'b2c_operating_unit')
        self.b2c_id = self.operating_unit_model.browse(cr, uid, b2c_id,
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
        user1_id = self._create_user(cr, uid, 'user_1',
                                     [self.group_account_user],
                                     self.company,
                                     [self.b2b_id, self.b2c_id],
                                     context=context)
        self.user1 = self.res_users_model.browse(
            cr, uid, user1_id, context=context)
        account_id = self._create_account(cr, uid, self.company,
                                     context=context)
        invoice_id = self._create_validate_invoice(
            cr, user1_id, [(self.product1, 1000),
                                    (self.product2, 500),
                                    (self.product3, 800)], context=context)
        self.invoice = self.invoice_obj.browse(
            cr, user1_id, invoice_id, context=context)
        self.move_id = self._create_account_move(cr, user1_id, account_id,
                                                 context=context)
        self._check_balance(cr, user1_id, account_id, context=context)
        self._check_balance(cr, user1_id,
                            self.company.inter_ou_clearing_account_id.id,
                            context=context)

    def _create_account_move(self, cr, uid, account_id, context=None):
        journal_ids = self.registry('account.journal').search(cr, uid,
                                                 [('code', '=', 'MISC')])
        default_move_vals = self.acc_move_obj.default_get(cr, uid, [],
                                                          context=context)
        move_vals = {}
        move_vals.update(default_move_vals)
        lines = [(0, 0, {
                'name': 'Test',
                'account_id': account_id,
                'debit':0,
                'credit': 100,
                'operating_unit_id': self.b2b_id.id,
            }),
                 (0, 0, {
                'name': 'Test',
                'account_id': account_id,
                'debit': 100,
                'credit': 0,
                'operating_unit_id': self.b2c_id.id,
            })]
        move_vals.update({
            'journal_id': journal_ids and journal_ids[0],
            'line_id': lines,
        })
        move_id = self.acc_move_obj.create(cr, uid, move_vals)
        return move_id

    def _get_balance(self, cr, uid, domain):
        aml_rec = self.aml_obj.read_group(cr, uid, domain,
                                ['debit', 'credit', 'account_id'],
                                ['account_id'])[0]
        return aml_rec.get('debit', 0) - aml_rec.get('credit', 0)

    def _check_balance(self, cr, uid, account_id, context=None):
        #check balance for all operating units
        domain = [('account_id', '=', account_id)]
        balance = self._get_balance(cr, uid, domain)
        self.assertEqual(balance, 0.0, 'Balance is 0 for all Operating Units.')
        #check balance for operating B2B units
        domain = [('account_id', '=', account_id),
                  ('operating_unit_id', '=', self.b2b_id.id)]
        balance = self._get_balance(cr, uid, domain)
        self.assertEqual(balance, -100,
                         'Balance is -100 for Operating Unit B2B.')
        #check balance for operating B2C units
        domain = [('account_id', '=', account_id),
                  ('operating_unit_id', '=', self.b2c_id.id)]
        balance = self._get_balance(cr, uid, domain)
        self.assertEqual(balance, 100.0,
                         'Balance is 100 for Operating Unit B2C.')

    def _create_account(self, cr, uid, company, context=None):
        """ Create an account.
        """
        type_ids = self.registry('account.account.type').search(cr, uid,
                                                [('code', '=', 'cash')])
        account_id = self.account_obj.create(cr, uid, {
            'name': 'Cash - Test',
            'code': 'test123',
            'type': 'liquidity',
            'user_type': type_ids and type_ids[0],
            'company_id': company.id,
            'operating_unit_id': self.ou1.id,
        })
        return account_id

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

    def _create_validate_invoice(self, cr, uid, line_products, context=None):
        """Create invoice.
        ``line_products`` is a list of tuple [(product, qty)]
        """
        part_id = self.partner1.id
        inv_vals = self.invoice_obj.onchange_partner_id(cr, uid, [],
                                                        'in_invoice',
                                                        part_id)['value']
        default_inv_vals = self.invoice_obj.default_get(cr, uid, [],
                                                        context=context)
        inv_vals.update(default_inv_vals)
        lines = []
        for product, qty in line_products:
            uom_id = product.uom_id.id
            line_values = {
                'product_id': product.id,
                'quantity': qty,
                'price_unit': 50,
            }
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
            'operating_unit_id': self.b2b_id.id,
        })
        invoice_id = self.invoice_obj.create(cr, uid, inv_vals)
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'account.invoice', invoice_id,
                                'invoice_open', cr)
        return invoice_id

    def test_account_operating_unit(self):
        """Test Account Operating Unit"""
        self.assertNotEqual(self.invoice.id, [])
        return True
