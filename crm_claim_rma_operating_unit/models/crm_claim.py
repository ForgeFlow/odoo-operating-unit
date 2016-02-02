# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.osv import orm, fields
from openerp.tools.translate import _


class CrmClaim(orm.Model):
    _inherit = "crm.claim"

    def _get_default_warehouse(self, cr, uid, context=None):
        res = super(CrmClaim, self)._get_default_warehouse(cr, uid,
                                                           context=context)
        default_ou_id = self.pool['res.users'].operating_unit_default_get(
            cr, uid, uid, context=context)
        wh_ids = self.pool.get('stock.warehouse').search(
            cr, uid, [('operating_unit_id', '=', default_ou_id)],
            context=context)
        if not wh_ids:
            raise orm.except_orm(_('Error!'),
                                 _('There is no warehouse '
                                   'for the current user\'s operating unit!'))
        res = wh_ids[0]
        return res

    _defaults = {
        'warehouse_id': _get_default_warehouse,
    }

    def _check_warehouse_operating_unit(self, cr, uid, ids, context=None):
        for claim in self.browse(cr, uid, ids, context=context):
            if claim.warehouse_id and claim.operating_unit_id and\
                    claim.warehouse_id.operating_unit_id != \
                    claim.operating_unit_id:
                return False
        return True

    _constraints = [
        (_check_warehouse_operating_unit,
         'The Claim and the Warehouse must belong to '
         'the same Operating Unit.', ['operating_unit_id', 'warehouse_id']),
    ]
