# -*- coding: utf-8 -*-
# © 2015 Eficent - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Operating Unit in Procurement Orders",
    "version": "7.0.1.0.0",
    "author": "Eficent, Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Stock Management",
    "depends": ["procurement", "operating_unit", "stock_operating_unit"],
    "description": """
Operating Unit in Procurement Orders
====================================
This module implements global security rules on procurement orders so that
a user can only read procurement orders where the location is linked to an
operating unit that the user has access to.
    """,
    "data": [
        "security/procurement_security.xml",
    ],
    'installable': True,
    'active': False,
    'certificate': '',
}
