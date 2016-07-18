# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#               <jordi.ballester@eficent.com>
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
from openerp.tools.translate import _
from openerp import models, fields, api
from openerp.exceptions import Warning


class HrPayslip(models.Model):

    _inherit = 'hr.payslip'

    @api.multi
    def write(self, vals):
        super(HrPayslip, self).write(vals)
        if 'move_id' in vals and vals['move_id']:
            for slip in self:
                if slip.contract_id and slip.contract_id.operating_unit_id:
                    slip.move_id.write({
                            'operating_unit_id':
                            slip.contract_id.operating_unit_id.id})

    @api.cr_uid_ids_context
    def process_sheet(self, cr, uid, ids, context=None):
        OU = None
        for slip in self.browse(cr, uid, ids, context=context):
            # Check that all slips are related to contracts that belong to the same OU.
            if OU:
                if slip.contract_id.operating_unit_id.id != OU:
                    raise Warning(_('Configuration error!\nThe Contracts must\
                    refer the same Operating Unit.'))
            OU = slip.contract_id.operating_unit_id.id

        # Add to context the OU of the employee contract
        new_context = context.copy()
        new_context.update(force_operating_unit=OU)

        return super(HrPayslip, self).process_sheet(cr,uid,[slip.id],
                                                    new_context)
