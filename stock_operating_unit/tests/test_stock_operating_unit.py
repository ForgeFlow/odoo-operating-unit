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
        # Locations
#        b2c_wh = data_model.get_object(cr, uid, 'stock_operating_unit',
#                                              'stock_warehouse_b2c')
#        b2c_wh.lot_stock_id.write({'operating_unit_id': self.b2c.id})
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
        self.picking_in1 = self._create_picking(cr, uid, self.user1_id,
                                                self.b2c.id,
                                                'in',
                                                self.supplier_location.id,
                                                self.stock_location.id)
        self.picking_in2 = self._create_picking(cr, uid, self.user2_id,
                                                self.b2c.id,
                                                'in',
                                                self.supplier_location.id,
                                                self.location_b2c_id.id)
        # Create Internal Shipment
        self.picking_int = self._create_picking(cr, uid, self.user1_id,
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
        picking_ids = self.PickingObj.sudo(self.user1_id).\
            search([('id', '=', self.picking_in1.id)]).ids
        self.assertNotEqual(picking_ids, [], '')
        picking_ids = self.PickingObj.sudo(self.user2_id).\
            search([('id', '=', self.picking_in2.id)]).ids
        self.assertNotEqual(picking_ids, [])
        picking_ids = self.PickingObj.sudo(self.user1_id).\
            search([('id', '=', self.picking_int.id)]).ids
        self.assertNotEqual(picking_ids, [])
