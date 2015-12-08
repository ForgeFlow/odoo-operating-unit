# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
from openerp.osv import fields, orm


class operating_unit(orm.Model):

    _name = 'operating.unit'
    _description = 'Operating Unit'

    _columns = {
        'name': fields.char('Name', size=256, required=True),
        'code': fields.char('Code', size=32, required=True),
        'active': fields.boolean('Active'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
    }

    _defaults = {
        'active': True,
        'company_id': lambda s, cr, uid,
        c: s.pool.get('res.company')._company_default_get(
            cr, uid, 'account.account', context=c),
    }

    _sql_constraints = [
        ('code_company_uniq', 'unique (code,company_id)',
         'The code of the operating unit must '
         'be unique per company !'),
        ('name_company_uniq', 'unique (name,company_id)',
         'The name of the operating unit must '
         'be unique per company !')
    ]
