# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jordi Ballester (Eficent)
#    Copyright 2015 Eficent
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Accounting with Operating Units',
    'version': '1.0.1',
    'category': 'Generic Modules/Sales & Purchases',
    'description': '''
Accounting with Operating Units
===============================
This module introduces the following features:
- Adds the Operating Unit in the account move line.
- Define an Inter-operating unit clearing account at
company level.
- When users create a journal entry with lines in different operating units,
at the time of posting the journal entry it automatically creates the
corresponding lines in the Inter-operating unit clearing account,
making each OU self-balancing.
- Introduces checks that prevent users from entering cross-operating unit
journal entries using different accounts.
- The account financial reports include the option to filter by OU.
- Adds the Operating Unit in the invoice
- Implements security rules in the invoice
''',
    'author': "Eficent,Odoo Community Association (OCA)",
    'website': 'http://www.eficent.com',
    'depends': ['account', 'operating_unit'],
    'data': [
        'views/account_move_view.xml',
        'views/account_move_view.xml',
        'views/company_view.xml',
        'views/invoice_view.xml',
        'wizard/account_report_common_view.xml',
        'wizard/account_financial_report_view.xml',
        'security/invoice_security.xml'
    ],
    'demo': [
        'demo/account_minimal.xml'
    ],
    'installable': True,
}
