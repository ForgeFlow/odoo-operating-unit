# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Close Fiscal Year with Operating Units',
    'version': '7.0.1.0.0',
    'category': 'Generic Modules/Sales & Purchases',
    'description': '''
Close Fiscal Year with Operating Units
======================================
This module overrides the Odoo standard closing wizard with a new one that will
create separate opening moves for each operating unit, if the operating unit
 has been defined as self-balancing.

''',
    'author': "Eficent, Odoo Community Association (OCA)",
    'website': 'http://www.eficent.com',
    'depends': ['account_operating_unit'],
    'installable': True,
}
