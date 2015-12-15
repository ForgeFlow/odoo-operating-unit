# -*- coding: utf-8 -*-
# © 2015 Eficent - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.osv import fields, orm
from openerp.tools.translate import _


class CrmMakeSale(orm.TransientModel):

    _inherit = "crm.make.sale"

    def default_get(self, cr, uid, fields, context=None):
        res = super(CrmMakeSale, self).default_get(
            cr, uid, fields, context=context)
        opp_obj = self.pool['crm.lead']
        opp_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not opp_ids:
            return res
        assert active_model == 'crm.lead', \
            'Bad context propagation'

        op_unit_ids = []
        for opp in opp_obj.browse(cr, uid, opp_ids, context=context):
            op_unit_ids.append(opp.operating_unit_id and
                               opp.operating_unit_id.id or False)
        op_unit_ids = list(set(op_unit_ids))
        if len(op_unit_ids) > 1:
            raise orm.except_orm(_('Error!'),
                                 _('All opportunities must belong to the '
                                   'same Operating Unit.'))

        default_ou_id = op_unit_ids[0]
        if default_ou_id:
            shop_ids = self.pool['sale.shop'].search(
                    cr, uid, [('operating_unit_id', '=', default_ou_id)],
                    context=context)
            if shop_ids:
                res['shop_id'] = shop_ids[0]
        return res

    def _get_shop_id(self, cr, uid, ids, context=None):
        shop_id = super(CrmMakeSale, self)._get_shop_id(cr, uid, ids,
                                                        context=context)
        default_ou_id = self.pool['res.users'].operating_unit_default_get(
            cr, uid, uid, context=context)
        shop_ids = self.pool['sale.shop'].search(
            cr, uid, [('operating_unit_id', '=', default_ou_id)],
            context=context)
        if shop_ids:
            shop_id = shop_ids[0]
        return shop_id

    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True),
    }
    _defaults = {
        'shop_id': _get_shop_id,
    }
