# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Operating Unit in Sales",
    "version": "7.0.1.0.0",
    "author": "Eficent, Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Purchase Management",
    "depends": ["sale",
                "operating_unit"],
    "description": """
Operating Unit in Sales
=======================
This module was written to extend the Sales capabilities of Odoo.

This module introduces the operating unit to the Sales Order.

Security rules are defined to ensure that users can only display the
Sales Orders in which they are allowed access to.
    """,
    "license": "AGPL-3",
    "data": [
        "data/sale_data.xml",
        "views/sale_view.xml",
        "security/sale_security.xml",

    ],
    'installable': True,
    'active': False,
}
