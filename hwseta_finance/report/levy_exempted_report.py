from openerp.osv import osv, fields
import mx.DateTime
from openerp.report import report_sxw
from datetime import datetime,date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
from openerp import api, _
from openerp.exceptions import Warning

class levy_exempted_report(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context=None):
        self.records = False
        super(levy_exempted_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_date':self.get_date,
            'get_partner':self.get_partner,
            'cal_date':self.cal_date,
        })

    def get_date(self,data):
        date_lst = []
        date_dict = {'from_date':data['form']['from_date'],'to_date':data['form']['to_date']} 
        date_lst.append(date_dict)
        return date_lst
    
    def get_partner(self,data):
        partner_lst=[]
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
        ant_brw = []
        exempt_ser = self.pool.get('leavy.income.config').search(self.cr,self.uid,[])
        if exempt_ser:
            exempt_brw = self.pool.get('leavy.income.config').browse(self.cr,self.uid,exempt_ser)
        if exempt_brw:
            partner_mv_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',from_date),('date','<=',to_date),('account_id','in',[exempt_brw.mandatory_credit_acc.id,exempt_brw.discretionary_credit_acc.id,exempt_brw.admins_credit_acc.id])])
        if partner_mv_ser:
            partner_mv_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,partner_mv_ser)
            for br in partner_mv_brw:
                if br.partner_id not in partner_lst:
                    partner_lst.append(br.partner_id)
        return  partner_lst

    def cal_date(self,data,alst):
        partner_lst = []
        partner_mv_brw= []
        total_credit_amt = 0
        total_debit_amt = 0
        grand_amount = 0
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
        date_format = '%Y-%m-%d'
         
        d1 = datetime.strptime(from_date, date_format).date()
        d2 = datetime.strptime(to_date, date_format).date()
        r = relativedelta(d2,d1)
        if r.days > 0:
            month_diff = r.months + 1
 
        account_ser = self.pool.get('leavy.income.config').search(self.cr,self.uid,[])
        if account_ser:
            account_brw = self.pool.get('leavy.income.config').browse(self.cr,self.uid,account_ser)        
            
        if account_brw:
            partner_mv_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('partner_id','=',alst),('date','>=',d1),('date','<=',d2),('account_id','in',[account_brw.mandatory_credit_acc.id,account_brw.discretionary_credit_acc.id,account_brw.admins_credit_acc.id])])
        if partner_mv_ser:
            partner_mv_brw = partner_mv_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,partner_mv_ser)
        for i in partner_mv_brw:
            total_credit_amt += i.credit
            total_debit_amt += i.debit
        
        amount_diff = total_credit_amt - total_debit_amt
        grand_amount += amount_diff
        
        partner_ser = self.pool.get('res.partner').search(self.cr,self.uid,[('id','=',alst)])
        if partner_ser:
            partner_brw = self.pool.get('res.partner').browse(self.cr,self.uid,partner_ser)
        
        if month_diff <= 3:
            if amount_diff < account_brw.period_one:
                partner_lst.append(partner_brw)
        elif month_diff <= 6:
            if amount_diff < account_brw.period_two:
                partner_lst.append(partner_brw)
        elif month_diff <= 9:
            if amount_diff < account_brw.period_three:
                partner_lst.append(partner_brw)
        elif month_diff <= 12:
            if amount_diff < account_brw.period_four:
                partner_lst.append(partner_brw)
        return partner_lst
        
class report_levy_exempted_report(osv.AbstractModel):
    _name = 'report.hwseta_finance.report_levy_exempted'
    _inherit = 'report.abstract_report'
    _template = 'hwseta_finance.report_levy_exempted'
    _wrapped_report_class = levy_exempted_report