# -*- coding: utf-8 -*-
# © 2015 Eficent - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Accounting with Operating Units',
    'version': '7.0.1.0.0',
    'category': 'Generic Modules/Sales & Purchases',
    'description': '''
Accounting with Operating Units
===============================
This module introduces the following features:
- Adds the Operating Unit in the account move line.
- Defines if the operating units are self-balanced and Inter-operating unit
clearing account at company level.
- When users create a journal entry with lines in different operating units,
if operating units have been defined to be self-balanced,
at the time of posting the journal entry it automatically creates the
corresponding lines in the Inter-operating unit clearing account,
making each OU self-balanced.
- The account financial reports include the option to filter by OU.
- Adds the Operating Unit in the invoice
- Implements security rules in the invoice
''',
    'author': "Eficent, Odoo Community Association (OCA)",
    'website': 'http://www.eficent.com',
    'depends': ['account', 'operating_unit'],
    'data': [
        'security/account_security.xml',
        'views/account_move_view.xml',
        'views/account_account_view.xml',
        'views/company_view.xml',
        'views/invoice_view.xml',
        'wizard/account_report_common_view.xml',
        'wizard/account_financial_report_view.xml',
    ],
    'demo': [
        'demo/account_minimal.xml'
    ],
    'installable': True,
}
