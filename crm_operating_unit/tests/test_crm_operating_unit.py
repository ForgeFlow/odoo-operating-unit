# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.tests import common
from openerp import netsvc


class TestPurchaseOperatingUnit(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseOperatingUnit, self).setUp()
        cr, uid, context = self.cr, self.uid, {}
        data_model = self.registry('ir.model.data')
        self.res_users_model = self.registry('res.users')
        self.crm_lead_model = self.registry('crm.lead')
        # Groups
        self.grp_sale_user = data_model.get_object(cr, uid, 'base',
                                                  'group_sale_manager')
        self.grp_user = data_model.get_object(cr, uid, 'base',
                                                  'group_user')
        # Company
        self.company = data_model.get_object(cr, uid, 'base', 'main_company')
        # Main Operating Unit
        self.ou1 = data_model.get_object(cr, uid, 'operating_unit',
                                         'main_operating_unit')
        # B2C Operating Unit
        self.b2c = data_model.get_object(cr, uid, 'operating_unit',
                                         'b2c_operating_unit')
        # Create User 1 with Main OU
        self.user1_id = self._create_user(cr, uid, 'user_1',
                                     [self.grp_sale_user, self.grp_user],
                                     self.company,
                                     [self.ou1], context=context)
        # Create User 2 with B2C OU
        self.user2_id = self._create_user(cr, uid, 'user_2',
                                     [self.grp_sale_user, self.grp_user],
                                     self.company,
                                     [self.b2c], context=context)
        # Create CRM Leads
        self.lead1_id = self._create_crm_lead(cr, self.user1_id, self.ou1,
                                              context=context)
        self.lead2_id = self._create_crm_lead(cr, self.user2_id, self.b2c,
                                              context=context)

    def _create_user(self, cr, uid, login, groups, company, operating_units,
                     context=None):
        """ Create a user. """
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

    def _create_crm_lead(self, cr, uid, operating_unit, context=None):
        """Create a sale order."""
        crm_id = self.crm_lead_model.create(cr, uid, {
            'name': 'CRM LEAD',
            'operating_unit_id': operating_unit.id
        })
        return crm_id

    def test_security(self):
        cr, uid, context = self.cr, self.uid, {}
        # User 2 is only assigned to B2C Operating Unit, and cannot
        # access CRM leads for Main Operating Unit.
        user2 = self.res_users_model.browse(cr, uid, self.user2_id,
                                            context=None)
        lead_ids = self.crm_lead_model.search(cr, user2.id,
                                            [('id', '=', self.lead1_id),
                                             ('operating_unit_id', '=',
                                              self.ou1.id)], context=context)
        self.assertEqual(lead_ids, [], 'User 2 should not have access to '
                                       'OU %s' % self.ou1.name)
