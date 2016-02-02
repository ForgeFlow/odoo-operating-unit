# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import netsvc
from openerp.tools.translate import _
import time


class ClaimMakePicking(orm.TransientModel):

    _inherit = 'claim_make_picking.wizard'

    def _prepare_picking_vals(
            self, cr, uid, claim, p_type, partner_id, wizard, context=None):
        res = super(ClaimMakePicking, self)._prepare_picking_vals(
            cr, uid, claim, p_type, partner_id, wizard, context=context)
        res['operating_unit_id'] = claim.operating_unit_id.id
        return res