# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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

from openerp.osv import fields, osv


class wss_upload_configuration(osv.osv_memory):
    _name = 'wss.upload.config.settings'
    _inherit = 'res.config.settings'

    _columns = {
        'company_id': fields.many2one('res.company','company', "Submission extension end date",
                                         help='This field is to set the end date of extensions on submissions.'),
        'submission_start': fields.related('company_id','submission_start','Submission start date',
            help='This field is to set the start date of submissions',type='date'),
        'submission_end': fields.related('company_id','submission_end',"Submission start date",
            help='This field is to set the end date of submissions.',type='date'),
        'submission_ext': fields.related('company_id','submission_ext',"Submission extension end date",
                                      help='This field is to set the end date of extensions on submissions.',type='date'),
    }

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.id

    _defaults = {
        'company_id': _default_company,
    }

class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'submission_start': fields.date('Submission start date',
            help='This field is to set the start date of submissions'),
        'submission_end': fields.date("Submission start date",
            help='This field is to set the end date of submissions.'),
        'submission_ext': fields.date("Submission extension end date",
                                      help='This field is to set the end date of extensions on submissions.'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
