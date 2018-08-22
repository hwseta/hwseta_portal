from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import workflow
from datetime import datetime
from openerp.exceptions import Warning

class account_emp_wise_wiz(osv.osv_memory):
    _name = "account.emp.wise.wiz"
    _columns={
    'from_date' :fields.date(string='From Date' , required=True),
    'to_date':  fields.date(string='To Date' , required=True),
    }

 
    def print_report1(self, cr, uid, ids, context=None):
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
        return self.pool['report'].get_action(cr, uid, [], 'hwseta_finance.report_levy_report', data=datas, context=context)   
