# -*- coding: utf-8 -*-
# © 2015 Eficent - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.tests import common


class TestStockOperatingUnit(common.TransactionCase):

    def setUp(self):
        super(TestStockOperatingUnit, self).setUp()
        cr, uid = self.cr, self.uid
        data_model = self.registry('ir.model.data')
        self.move_model = self.registry('stock.move')
        self.res_users_model = self.registry('res.users')
        self.picking_model = self.registry('stock.picking')
        self.warehouse_model = self.registry('stock.warehouse')
        self.location_model = self.registry('stock.location')
        # company
        self.company1 = data_model.get_object(cr, uid, 'base', 'main_company')
        # groups
        self.group_purchase_user = data_model.get_object(cr, uid, 'purchase',
                                                         'group_purchase_user')
        self.group_stock_manager = data_model.get_object(cr, uid, 'stock',
                                                         'group_stock_manager')
        # Main Operating Unit
        self.ou1 = data_model.get_object(cr, uid, 'operating_unit',
                                         'main_operating_unit')
        # B2C Operating Unit
        self.b2c = data_model.get_object(cr, uid, 'operating_unit',
                                         'b2c_operating_unit')
        # Products
        self.product1 = data_model.get_object(cr, uid, 'product',
                                              'product_product_7')
        self.stock_location = data_model.get_object(cr, uid, 'stock',
                                                    'stock_location_stock')
        self.supplier_location =\
            data_model.get_object(cr, uid, 'stock', 'stock_location_suppliers')
        self.location_b2c_id = data_model.get_object(cr, uid,
                                                     'stock_operating_unit',
                                                     'stock_location_b2c')
        # Products
        self.product1 = data_model.get_object(cr, uid, 'product',
                                              'product_product_7')
        self.product2 = data_model.get_object(cr, uid, 'product',
                                              'product_product_9')
        self.product3 = data_model.get_object(cr, uid, 'product',
                                              'product_product_11')
        # Create users
        self.user1_id = self._create_user(cr, uid, 'stock_user_1',
                                          [self.group_stock_manager],
                                          self.company1,
                                          [self.ou1, self.b2c])
        self.user2_id = self._create_user(cr, uid, 'stock_user_2',
                                          [self.group_stock_manager],
                                          self.company1,
                                          [self.b2c])
        # Create Incoming Shipments
        self.picking_in1_id = self._create_picking(cr, uid, self.user1_id,
                                                   self.ou1.id,
                                                   'in',
                                                   self.supplier_location.id,
                                                   self.stock_location.id)
        self.picking_in2_id = self._create_picking(cr, uid, self.user2_id,
                                                   self.b2c.id,
                                                   'in',
                                                   self.supplier_location.id,
                                                   self.location_b2c_id.id)
        # Create Internal Shipment
        self.picking_int_id = self._create_picking(cr, uid, self.user1_id,
                                                   self.b2c.id,
                                                   'internal',
                                                   self.stock_location.id,
                                                   self.location_b2c_id.id)

    def _create_user(self, cr, uid, login, groups, company, operating_units):
        """ Create a user."""
        group_ids = [group.id for group in groups]
        user_id = self.res_users_model.create(cr, uid, {
            'name': 'Stock User',
            'login': login,
            'password': 'demo',
            'email': 'chicago@yourcompany.com',
            'company_id': company.id,
            'company_ids': [(4, company.id)],
            'operating_unit_ids': [(4, ou.id) for ou in operating_units],
            'groups_id': [(6, 0, group_ids)]
        }, context={'no_reset_password': True})
        return user_id

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
            'product_id': self.product1.id,
            'product_qty': 3.0,
            'product_uom': self.product1.uom_id.id,
            'picking_id': picking_id,
            'location_id': src_loc_id,
            'location_dest_id': dest_loc_id,
        })
        return picking_id

    def test_pickings(self):
        """Test Pickings of Stock Operating Unit"""
        cr = self.cr
        picking_ids = self.picking_model.\
            search(cr, self.user1_id, [('id', '=', self.picking_in1_id)])
        self.assertNotEqual(picking_ids, [], '')
        picking_ids = self.picking_model.\
            search(cr, self.user2_id, [('id', '=', self.picking_in2_id)])
        self.assertNotEqual(picking_ids, [])
        picking_ids = self.picking_model.\
            search(cr, self.user1_id, [('id', '=', self.picking_int_id)])
        self.assertNotEqual(picking_ids, [])

    def test_stock_ou_security(self):
        """Test Security of Stock Operating Unit"""
        cr = self.cr
        # User 1 can list the warehouses assigned to
        # Main and B2C OU
        wh_ids = self.warehouse_model.\
            search(cr, self.user1_id,
                   [('operating_unit_id', 'in', [self.ou1.id, self.b2c.id])])
        self.assertNotEqual(wh_ids, [], 'User does not have access to\
                            Warehouses which belong to Main and B2C\
                            Operating Unit.')
        # User 1 can list the locations assigned to Main and b2c OU
        location_ids = self.location_model.\
            search(cr, self.user1_id,
                   [('operating_unit_id', 'in', [self.ou1.id, self.b2c.id])])
        self.assertNotEqual(location_ids, [], 'User does not have access to\
                            Locations which belong to Main and B2C\
                            Operating Unit.')
        # User 2 cannot list the warehouses assigned to Main OU
        wh_ids = self.warehouse_model.\
            search(cr, self.user2_id,
                   [('operating_unit_id', '=', self.ou1.id)])
        self.assertEqual(wh_ids, [], 'User 2 should not be able to list the '
                                     'warehouses assigned to Main Operating '
                                     'Unit.')
        # User 2 cannot list the locations assigned to Main OU
        location_ids = self.location_model.\
            search(cr, self.user2_id,
                   [('operating_unit_id', 'in', [self.ou1.id])])
        self.assertEqual(location_ids, [], 'User 2 should not be able to list\
                         the locations assigned to Main OU.')
        pickings = [self.picking_in1_id, self.picking_in2_id,
                    self.picking_int_id]
        # User 1 can list the pickings 1, 2, 3
        picking_ids =\
            self.picking_model.search(cr, self.user1_id,
                                      [('id', 'in', pickings)])
        self.assertNotEqual(picking_ids, [], 'User 1 cannot list '
                                             'the pickings assigned to '
                                             'pickings 1, 2, 3.')
        # User 1 can list the stock moves assigned to picking 1, 2, 3
        move_ids =\
            self.move_model.search(cr, self.user1_id,
                                   [('picking_id', 'in', pickings)])
        self.assertNotEqual(move_ids, [], 'User 1 cannot list the\
                            stock moves assigned to pickings 1, 2, 3.')
        # User 2 cannot list the the stock moves assigned to picking 1
        move_ids =\
            self.move_model.search(cr, self.user2_id,
                                   [('picking_id', '=', self.picking_in1_id)])
        self.assertEqual(move_ids, [], 'User 2 sould not be able to list '
                                       'the stock moves assigned to '
                                       'picking 1.')
        # User 2 cannot list the pickings 1
        picking_ids =\
            self.picking_model.search(cr, self.user2_id,
                                      [('id', '=', self.picking_in1_id)])
        self.assertEqual(picking_ids, [], 'User 2 cannot list the picking 1.')
