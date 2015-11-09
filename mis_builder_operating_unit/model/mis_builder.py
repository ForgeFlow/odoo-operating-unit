# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jordi Ballester (Eficent)
#    Copyright 2015 Eficent
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
from openerp.osv import orm, fields


class MisReportInstance(orm.Model):

    _inherit = 'mis.report.instance'

    _columns = {
        'operating_unit_ids': fields.many2many('operating.unit',
                                               string='Operating Units',
                                               required=False),
    }


class MisReportInstancePeriod(orm.Model):

    _inherit = 'mis.report.instance.period'

    def _get_additional_move_line_filter(self, cr, uid, _id, context=None):
        aml_domain = super(
            MisReportInstancePeriod, self)._get_additional_move_line_filter(
            cr, uid, _id, context=context)
        this = self.browse(cr, uid, _id, context=context)
        if this.report_instance_id.operating_unit_ids:
            operating_unit_ids = [op.id for op in
                                  this.report_instance_id.operating_unit_ids]
            aml_domain.append(('operating_unit_id', 'in',
                               tuple(operating_unit_ids)))
        return aml_domain
