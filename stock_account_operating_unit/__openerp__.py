# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Operating Unit in Stock Management with Real-Time Valuation',
    'version': '1.0',
    'category': 'Generic Modules/Sales & Purchases',
    'author': "Eficent,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    'website': 'http://www.eficent.com',
    'description': """\
Stock account moves with Operating Unit
=======================================
- Creates account move lines when stock moves are posted between internal
locations within the same company, but different OU’s.

""",
    'depends': ['stock_operating_unit', 'account_operating_unit'],
    'data': [],
    'installable': True,
}
