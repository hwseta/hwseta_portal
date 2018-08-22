from openerp.osv import osv, fields
import mx.DateTime
from openerp.report import report_sxw
from datetime import datetime,date, timedelta
from openerp.tools.translate import _
from openerp import api, _
from openerp.exceptions import Warning

class mandatory_income_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        self.records = False
        super(mandatory_income_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_date':self.get_date,
            'get_partner' : self.get_partner,
            'get_total' : self.get_total
        })

    def get_date(self,data):
        date_lst = []
        date_dict = {'from_date':data['form']['from_date'],'to_date':data['form']['to_date']} 
        date_lst.append(date_dict)
        return date_lst
    
    def get_partner(self,data):
        partner_lst=[]
        wsp_brw = []
        partner_mv_brw = []
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
        total_credit = 0
        total_debit = 0
        total_tax = 0
        
        mandatory_ser = self.pool.get('leavy.income.config').search(self.cr,self.uid,[])
        if mandatory_ser:
            mandatory_brw = self.pool.get('leavy.income.config').browse(self.cr,self.uid,mandatory_ser)
        if mandatory_brw:
            partner_mv_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',from_date),('date','<=',to_date),('account_id','=',mandatory_brw.mandatory_credit_acc.id)])
        if partner_mv_ser:
            partner_mv_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,partner_mv_ser)

        for br in partner_mv_brw:
            if br not in partner_lst:
                if br.analytic_account_id.name:
                    wsp_ser = self.pool.get('wsp.submission.track').search(self.cr,self.uid,[('employer_id','=',br.partner_id.id),('scheme_year','=',br.analytic_account_id.name),('status','not in',['accepted'])])
                    if wsp_ser:
                        wsp_brw = self.pool.get('wsp.submission.track').browse(self.cr,self.uid,wsp_ser)
                    if wsp_brw :    
                        for i in wsp_brw:
                            partner_lst.append(br)    
        return  partner_lst
    
    def get_total(self,data):
        dict ={}
        total_tax = 0
        total_credit = 0
        total_debit = 0
        move_obj = []
        total = []
        move_obj = self.get_partner(data);
        for i in move_obj:
            total_tax += i.account_tax_id.name
            total_credit += i.credit
            total_debit += i.debit
        
        dict['total_tax'] = total_tax
        dict['total_debit'] = total_debit
        dict['total_credit'] = total_credit
        total.append(dict)
        return total
    
class report_mandatory_income_moveline_report(osv.AbstractModel):
    _name = 'report.hwseta_finance.report_mandatory_income'
    _inherit = 'report.abstract_report'
    _template = 'hwseta_finance.report_mandatory_income'
    _wrapped_report_class = mandatory_income_report