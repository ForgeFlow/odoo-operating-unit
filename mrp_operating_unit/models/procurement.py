# -*- coding: utf-8 -*-
# © 2015 Eficent - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.osv import fields, orm


class ProcurementOrder(orm.Model):

    _inherit = 'procurement.order'

    def _check_mrp_production_operating_unit(self, cr, uid, ids,
                                             context=None):
        for pr in self.browse(cr, uid, ids, context=context):
            if (
                pr.production_id and
                pr.location_id.operating_unit_id and
                pr.production_id.operating_unit_id !=
                    pr.location_id.operating_unit_id
            ):
                return False
        return True

    _constraints = [
        (_check_mrp_production_operating_unit,
         'The Production Order and the Procurement Order must '
         'belong to the same Operating Unit.', ['operating_unit_id',
                                                'production_id'])]

    def _prepare_mo_vals(self, cr, uid, procurement, context=None):
        res = super(ProcurementOrder, self)._prepare_mo_vals(cr, uid,
                                                             procurement,
                                                             context=context)
        if procurement.location_id.operating_unit_id:
            res['operating_unit_id'] = \
                procurement.location_id.operating_unit_id.id
        return res
