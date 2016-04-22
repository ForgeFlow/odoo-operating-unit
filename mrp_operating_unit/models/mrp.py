# -*- coding: utf-8 -*-
# © 2015 Eficent - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, orm


class MrpProduction(orm.Model):

    _inherit = 'mrp.production'

    _columns = {
        'operating_unit_id': fields.many2one('operating.unit',
                                             'Operating Unit'),
    }

    _defaults = {
        'operating_unit_id': lambda self, cr, uid, c: self.pool.get(
            'res.users').operating_unit_default_get(cr, uid, uid, context=c),
    }

    def _check_location_operating_unit(self, cr, uid, ids, context=None):
        for mo in self.browse(cr, uid, ids, context=context):
            if (
                not mo.operating_unit_id and
                (mo.location_src_id.operating_unit_id or
                 mo.location_dest_id.operating_unit_id)
            ):
                return False
            if (
                mo.operating_unit_id and
                mo.operating_unit_id != mo.location_src_id.operating_unit_id
            ):
                return False
            if (
                mo.operating_unit_id and
                mo.operating_unit_id != mo.location_dest_id.operating_unit_id
            ):
                return False
        return True

    _constraints = [
        (_check_location_operating_unit,
         'The Operating Unit of the Manufacturing Order must match '
         'with that of the Raw Materials and Finished Product '
         'Locations.', ['location_src_id', 'location_dest_id'])
    ]

    def _make_production_internal_shipment(self, cr, uid, production,
                                           context=None):
        picking_id = super(
            MrpProduction, self)._make_production_internal_shipment(
            cr, uid, production, context=context)
        if production.operating_unit_id:
            self.pool['stock.picking'].write(
                cr, uid, [picking_id],
                {'operating_unit_id': production.operating_unit_id.id},
                context=context)
        return picking_id
