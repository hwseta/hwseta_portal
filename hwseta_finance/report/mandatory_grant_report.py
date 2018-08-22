from openerp.osv import osv, fields
import mx.DateTime
from mx.DateTime import RelativeDateTime
import time
from openerp.report import report_sxw
from datetime import datetime,date, timedelta
from openerp.tools.translate import _
from openerp import api, _
from openerp.exceptions import Warning

class mandatory_grant_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        self.records = False
        super(mandatory_grant_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_date':self.get_date,
            'get_partner' : self.get_partner,
            'get_ana_account' : self.get_ana_account,
            'get_lines' : self.get_lines,
            'get_income_amount' : self.get_income_amount,
            'get_grand_total' : self.get_grand_total,
            'get_expense_amount':self.get_expense_amount
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
        grant_ser = self.pool.get('leavy.income.config').search(self.cr,self.uid,[])
        if grant_ser:
            grant_brw = self.pool.get('leavy.income.config').browse(self.cr,self.uid,grant_ser)
        if grant_brw:
            partner_mv_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',from_date),('date','<=',to_date),('account_id','=',grant_brw.expense_acc.id)])
        if partner_mv_ser:
            partner_mv_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,partner_mv_ser)
            for br in partner_mv_brw:
                if br.partner_id not in partner_lst:
                    partner_lst.append(br.partner_id)
        return  partner_lst   

    def get_ana_account(self,alst,data):
        ana_lst=[]
        ant_brw = []
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
        grant_ser = self.pool.get('leavy.income.config').search(self.cr,self.uid,[])
        if grant_ser:
            grant_brw = self.pool.get('leavy.income.config').browse(self.cr,self.uid,grant_ser)
        if grant_brw:
            acc_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',from_date),('date','<=',to_date),('partner_id','=',alst),('account_id','=',grant_brw.expense_acc.id)])
        if acc_ser:
            acc_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,acc_ser)
            if acc_brw:
                for ac_br in acc_brw: 
                    if ac_br.analytic_account_id not in ana_lst:
                        if ac_br.analytic_account_id:
                            ana_lst.append(ac_br.analytic_account_id)
        return  ana_lst 

    def get_lines(self,alst,an_br,data):
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
        ant_brw = []
        grant_ser = self.pool.get('leavy.income.config').search(self.cr,self.uid,[])
        if grant_ser:
            grant_brw = self.pool.get('leavy.income.config').browse(self.cr,self.uid,grant_ser)
        if grant_brw:
            ant_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',from_date),('date','<=',to_date),('partner_id','=',alst),('analytic_account_id','=',an_br),('account_id','=',grant_brw.expense_acc.id)])
        if ant_ser:
            ant_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,ant_ser)
        return ant_brw
    
    def get_income_amount(self,alst,an_br,data):
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
        res =0
        mandatory_move_brw = []
        mandatory_ser = self.pool.get('leavy.income.config').search(self.cr,self.uid,[])
        if mandatory_ser:
            mandatory_brw = self.pool.get('leavy.income.config').browse(self.cr,self.uid,mandatory_ser)
        if mandatory_brw:
            mandatory_move_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',from_date),('date','<=',to_date),('partner_id','=',alst),('analytic_account_id','=',an_br),('account_id','=',mandatory_brw.mandatory_credit_acc.id)])
        
        if mandatory_move_ser:
            mandatory_move_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,mandatory_move_ser)
            if mandatory_move_brw:
                if mandatory_move_brw[0].credit:
                    res = mandatory_move_brw[0].credit
                else:
                    res = -1*mandatory_move_brw[0].debit
            return res
        
    def get_expense_amount(self,debit,credit):
            res =debit-credit
            return res
        
    def get_grand_total(self,data):
        partner = []
        ana_account = []
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
        brw_list = []
        total_tax = 0
        tatal_debit = 0
        total_credit = 0
        total_list = []
        dict = {}       
        partner = self.get_partner(data)
        for i in partner:
            ana_account = self.get_ana_account(i.id,data)
            for an in ana_account:
                grant_ser = self.pool.get('leavy.income.config').search(self.cr,self.uid,[])
                if grant_ser:
                    grant_brw = self.pool.get('leavy.income.config').browse(self.cr,self.uid,grant_ser)
                if grant_brw:
                    mv_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',from_date),('date','<=',to_date),('partner_id','=',i.id),('analytic_account_id','=',an.id),('account_id','=',grant_brw.expense_acc.id)])
                if mv_ser:
                    mv_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,mv_ser)
                    brw_list.append(mv_brw)
           
        for brw in brw_list:
            for brw1 in brw:
                total_tax += brw1.account_tax_id.name
                tatal_debit += brw1.debit
                total_credit += brw1.credit
        dict['total_tax'] = total_tax
        dict['total_debit'] = tatal_debit
        dict['total_credit'] = total_credit
        total_list.append(dict)
        return total_list
        
class report_mandatory_grant_moveline_report(osv.AbstractModel):
    _name = 'report.hwseta_finance.report_mandgrant'
    _inherit = 'report.abstract_report'
    _template = 'hwseta_finance.report_mandgrant'
    _wrapped_report_class = mandatory_grant_report