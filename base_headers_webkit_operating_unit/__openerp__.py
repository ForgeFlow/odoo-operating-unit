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
{'name': """Common Webkit headers and CSS for reports related to operating
units (sale, purchase, invoices, ...)""",
 'version': '1.0',
 'category': 'Reports/Webkit',
 'description': """
  Contains Common data headers and CSS to design standard reports, used by:
   - sale_order_wekbit,
   - purchase_order_webkit,
   - ...
""",
 'author': "Eficent,Odoo Community Association (OCA)",
 'website': 'http://www.eficent.com',
 'depends': ['operating_unit', 'report_webkit'],
 'init_xml': [],
 'update_xml': ['base_headers_data.xml'],
 'demo_xml': [],
 'test': [],
 'installable': True,
 'active': False,
 }
