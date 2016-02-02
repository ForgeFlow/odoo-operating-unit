# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.osv import orm, fields


class CrmClaim(orm.Model):
    _inherit = "crm.claim"

    _columns = {
        'operating_unit_id': fields.many2one('operating.unit',
                                             'Default Operating Unit'),
    }

    _defaults = {
        'operating_unit_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').operating_unit_default_get(cr, uid, uid, context=c)
    }

    def _check_company_operating_unit(self, cr, uid, ids, context=None):
        for claim in self.browse(cr, uid, ids, context=context):
            if claim.company_id and \
                    claim.operating_unit_id and \
                    claim.company_id != claim.operating_unit_id.company_id:
                return False
        return True

    _constraints = [
        (_check_company_operating_unit,
         'The Company in the Claim and in the Operating '
         'Unit must be the same.', ['operating_unit_id',
                                    'company_id']),
    ]
