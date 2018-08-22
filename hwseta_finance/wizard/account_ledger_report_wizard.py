from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import workflow
from datetime import datetime

class account_move_line_wiz(osv.osv_memory):
    _name = "account.move.line.wiz"
    _columns={
    'from_date' :fields.date(string='From Date' , required=True),
    'to_date':  fields.date(string='To Date' , required=True),
    'account':  fields.many2one('account.account',string ='Account'),
    }
    
    
    def print_report(self, cr, uid, ids, context=None):
        data1 = self.read(cr, uid, ids,)
        data= data1[0]
        if context is None:
            context = {}
        from_date = datetime.strptime(data['from_date'], '%Y-%m-%d').date()
        to_date = datetime.strptime(data['to_date'], '%Y-%m-%d').date()
        if from_date > to_date:
            raise Warning(_('From Date could not be greater than To Date!'))
        datas = {
            'ids': context.get('active_ids', []),
            'model': 'account.move.line',
            'form': data
        }
        datas['form']['active_ids'] = context.get('active_ids', False)
        return self.pool['report'].get_action(cr, uid, [], 'hwseta_finance.report_move_line', data=datas, context=context)

