# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.osv import orm, fields


class res_company(orm.Model):
    _inherit = 'res.company'

    _columns = {
        'inter_ou_clearing_account_id': fields.many2one(
            'account.account', 'Inter-operating unit clearing account'),
        'ou_is_self_balanced': fields.boolean(
                'Operating Units are self-balanced',
                help="Activate if your company is required to generate a "
                     "balanced balance sheet for each operating unit.")
        }

    _defaults = {
        'ou_is_self_balanced': True
    }

    def _inter_ou_clearing_acc_required(self, cr, uid, ids):
        for company in self.browse(cr, uid, ids):
            if company.ou_is_self_balanced and not \
                    company.inter_ou_clearing_account_id:
                return False
        return True

    _constraints = [
        (_inter_ou_clearing_acc_required,
         'Please indicate an Inter-operating unit clearing account.',
         ['ou_is_self_balanced'])]
