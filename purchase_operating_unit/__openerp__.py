# -*- coding: utf-8 -*-
# © 2015 Eficent - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Operating Unit in Purchase Orders",
    "version": "7.0.1.0.0",
    "category": "Purchase Management",
    "description": """
Operating Unit in Purchase Orders
=================================
This module introduces the operating unit to the purchase order.
The operating unit is copied to the invoice.
The operating unit is copied to the stock picking.
It implements user's security rules.
    """,
    "author": "Eficent, Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "depends": ["purchase", "procurement_operating_unit"],
    "data": [
        "security/purchase_security.xml",
        "views/purchase_order_view.xml",
        "views/purchase_order_line_view.xml",
    ],
    "demo": [
        "demo/purchase_order_demo.xml",
    ],
    "installable": True,
}
