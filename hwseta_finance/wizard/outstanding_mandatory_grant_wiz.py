# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.tools.translate import _

class outstanding_mandatory_grant_wiz(osv.osv_memory):
    _name = 'outstanding.mandatory.grant.wiz'
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        acc_move_line = self.pool.get('account.move.line')
        leavy_income_config = self.pool.get('leavy.income.config')
        acc_acc = self.pool.get('account.account')
        
        leavy_config_id = leavy_income_config.search(cr, uid, [], context=context)[0] #Always take latest configuration
        for leavy in leavy_income_config.browse(cr, uid, [leavy_config_id], context=context):
            proj_budget_acc_id = leavy.project_budget_acc.id
        acc_move_line_ids = acc_move_line.search(cr, uid, [('account_id','=',proj_budget_acc_id),('reconcile_id','=',False),('reconcile_partial_id','=',False),], context=context)
        mandatory_grant = acc_move_line.read(cr, uid, acc_move_line_ids, context=context)
        outstanding = {'outstanding': mandatory_grant}
        data = {
                'ids': context.get('active_ids', []),
                'model': 'account.move.line',
                'form': outstanding 
                }
        
        return self.pool['report'].get_action(cr, uid, [], 'hwseta_finance.report_outstanding_mandatory_grant', data=data, context=context)
outstanding_mandatory_grant_wiz()