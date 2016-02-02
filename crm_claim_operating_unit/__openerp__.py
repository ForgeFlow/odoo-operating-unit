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
    "name": "Operating Unit in CRM Claims",
    "version": "1.0",
    "author": "Eficent",
    "website": "http://www.eficent.com",
    "category": "CRM",
    "depends": ["crm_claim", "operating_unit"],
    "description": """
Operating Unit in CRM Claims
============================
This module introduces the security rules of operating unit to CRM Claims.
A user can only view and manage the claims associated to the warehouse of
the operating units that he has access to.

    """,
    "data": [
        "security/crm_security.xml",
        "views/crm_claim_view.xml"
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'active': False,
    'certificate': '',
}
