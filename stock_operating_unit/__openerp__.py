# -*- coding: utf-8 -*-
# © 2015 Eficent - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock with Operating Units',
    'version': '7.0.1.0.0',
    'category': 'Generic Modules/Sales & Purchases',
    'description': """\
Stock with Operating Units
==========================
This module introduces the following features:
- Adds the operating unit to the Warehouse.
- Adds the operating unit to the Stock Location.
- Adds the requesting operating unit to stock pickings.
- Implements user's security access rules.
""",
    'author': "Eficent Business and IT Consulting Services S.L., "
              "Serpent Consulting Services Pvt. Ltd.,"
              "Odoo Community Association (OCA)",
    'website': 'http://camptocamp.com',
    'depends': ['stock', 'account_operating_unit'],
    'data': [
        'security/stock_security.xml',
        'data/stock_data.xml',
        'view/stock.xml',
    ],
    'demo': [
        'demo/stock_demo.xml',
    ],
    'installable': True,
}
