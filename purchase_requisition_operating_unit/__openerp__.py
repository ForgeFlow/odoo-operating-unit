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
    "name": "Operating Unit in Purchase Requisitions",
    "version": "1.0",
    "author": "Eficent",
    "website": "http://www.eficent.com",
    "category": "Purchase Management",
    "depends": ["purchase_requisition",
                "purchase_operating_unit"],
    "description": """
Operating Unit in Purchase Requisitions
=======================================
This module was written to extend the Purchase Requsition capabilities of Odoo.

This module introduces the operating unit to the purchase requisition.

Security rules are defined to ensure that users can only display the
Purchase Requisitions in which they are allowed access to.

Installation
============

No additional installation instructions are required.


Configuration
=============

This module does not require any additional configuration.

Usage
=====

At the time when a user creates a new purchase requisition the system
proposes the user's default operating unit.

The operating unit is a required field.

When the user creates a purchase order (PO) from the purchase requisition the
operating unit is copied to the PO.


Known issues / Roadmap
======================

No issue has been identified.

Credits
=======

Contributors
------------

* Jordi Ballester <jordi.ballester@eficent.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.


    """,
    "init_xml": [],
    "update_xml": [
        "view/purchase_requisition.xml",
        "security/purchase_security.xml",
    ],
    'demo_xml': [

    ],
    'test':[
    ],
    'installable': True,
    'active': False,
    'certificate': '',
}
