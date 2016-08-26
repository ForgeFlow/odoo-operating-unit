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
    'name': 'Account Vouchers Move Line Create Hooks',
    'version': '1.0',
    'category': 'Generic Modules/Sales & Purchases',
    'description': '''
Account Vouchers Move Line Create Hooks
=======================================
This module reimplements the method that creates the account moves from the
voucher, with the same basic result as in the standard case.

Hooks are provided for extra modules can influence the data that is passed
to the account moves.

''',
    'author': "Eficent",
    'website': 'http://www.eficent.com',
    'depends': ['account_voucher'],
    'data': [],
    'installable': True,
}
