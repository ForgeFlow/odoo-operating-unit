# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#               <contact@eficent.com>
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
    "name": "Operating Unit in Purchase Orders",
    "version": "1.0",
    "author": "Eficent",
    "website": "http://www.eficent.com",
    "category": "Purchase Management",
    "depends": ["purchase", "stock_operating_unit",
                "procurement_operating_unit"],
    "description": """
Operating Unit in Purchase Orders
=================================
This module introduces the operating unit to the purchase order.
The operating unit is copied to the invoice.
The operating unit is copied to the stock picking.

It implements user's security rules.


    """,
    "data": [
        "views/purchase_order_view.xml",
        "views/purchase_order_line_view.xml",
        "security/purchase_security.xml",
    ],
    'demo': [
        'demo/purchase_order_demo.xml'
    ],
    'test': [
    ],
    'installable': True,
    'active': False,
    'certificate': '',
}
