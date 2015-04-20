# -*- coding: utf-8 -*-
# Authors: Jordi Ballester Alomar
# Copyright 2015 Eficent (http://www.eficent.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public Lice
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
{
    'name': 'Stock with Operating Units',
    'version': '1.0',
    'category': 'Generic Modules/Sales & Purchases',
    'author': "Eficent,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    'website': 'http://camptocamp.com',
    'description': """\
Stock with Operating Units
==========================
Adds the operating unit to the stock locations.
Adds the operating unit to stock moves.
Adds the requesting operating unit to stock pickings.
Implements user's security access rules.

""",
    'depends': ['stock', 'operating_unit'],
    'data': [
        'view/stock.xml',
        'security/stock_security.xml',
    ],
    'installable': True,
}