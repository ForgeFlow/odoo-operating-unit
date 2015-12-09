# -*- coding: utf-8 -*-
# © 2015 Eficent - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
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
