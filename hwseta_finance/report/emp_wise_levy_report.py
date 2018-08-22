from openerp.osv import osv, fields
import mx.DateTime
from mx.DateTime import RelativeDateTime
import time
from openerp.report import report_sxw
from datetime import datetime,date, timedelta
from openerp.tools.translate import _
from openerp import api, _

class levy_report(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context=None):
        self.records = False
        super(levy_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_date':self.get_date,
            'get_partner' : self.get_partner,
            'get_ana_account' : self.get_ana_account,
            'get_account_type':self.get_account_type,
            'get_grand_total' :self.get_grand_total,
        })
        
    def get_date(self,data):
        date_lst = []
        date_dict = {'from_date':data['form']['from_date'],'to_date':data['form']['to_date']} 
        date_lst.append(date_dict)
        return date_lst
    
    def get_partner(self,data):
        partner_lst=[]

        partner_mv_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',data['form']['from_date']),('date','<=',data['form']['to_date'])])
        if partner_mv_ser:
            partner_mv_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,partner_mv_ser)
            if partner_mv_brw:
                for br in partner_mv_brw:
                    if br.partner_id:
                        if br.partner_id not in partner_lst:
                            partner_lst.append(br.partner_id)
        return  partner_lst           
    
    def get_ana_account(self,alst,data):
        ana_lst=[]
        acc_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('partner_id','=',alst),('date','>=',data['form']['from_date']),('date','<=',data['form']['to_date'])])
        if acc_ser:
            acc_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,acc_ser)
            if acc_brw:
                for ac_br in acc_brw: 
                    if ac_br.analytic_account_id not in ana_lst:
                        if ac_br.analytic_account_id:
                            ana_lst.append(ac_br.analytic_account_id)
        return  ana_lst 

    def get_account_type(self,alst,an_br,data):
        acc_type_list = []
        acc_type = {}
        mandatory_brw =[]
        disc_brw = []
        admins_brw = []
        penalty_brw = []
        interest_brw = []
        m_credit_total = 0 
        m_debit_total = 0
        m_tax_total = 0
        d_credit_total = 0 
        d_debit_total = 0
        d_tax_total = 0
        a_credit_total = 0 
        a_debit_total = 0
        a_tax_total = 0
        p_credit_total = 0 
        p_debit_total = 0
        p_tax_total = 0
        i_credit_total = 0 
        i_debit_total = 0
        i_tax_total = 0
        
        grand_credit_total = 0
        grand_debit_total = 0
        grand_tax_total = 0
        grand_list = 0
        mandatory_credit_acc,discretionary_credit_acc,admins_credit_acc,interest_acc,penalty_acc='','','','',''
        acc_ser = self.pool.get('grant.account').search(self.cr,self.uid,[])
        if acc_ser:
            acc_mv = self.pool.get('grant.account').browse(self.cr,self.uid,acc_ser)
            if acc_mv:
                for ac in acc_mv:
                    if ac.grant_id.name == 'Mandatory Grant':
                        mandatory_credit_acc = ac.account_id.id
                    if ac.grant_id.name == 'Discretionary Grant':
                        discretionary_credit_acc = ac.account_id.id
                    if ac.grant_id.name == 'Admin Grant':
                        admins_credit_acc = ac.account_id.id
                    if ac.grant_id.name == 'Interest':
                        interest_acc = ac.account_id.id                    
                    if ac.grant_id.name == 'Penalty':
                        penalty_acc = ac.account_id.id
                            
#         leavy_ser = self.pool.get('leavy.income.config').search(self.cr,self.uid,[])
#         if leavy_ser:
#             leavy_brw = self.pool.get('leavy.income.config').browse(self.cr,self.uid,leavy_ser)
        
        mandatory_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',data['form']['from_date']),('date','<=',data['form']['to_date']),('analytic_account_id','=',an_br),('partner_id','=',alst),('account_id','=',mandatory_credit_acc)])
        if mandatory_ser:
            mandatory_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,mandatory_ser)
        acc_type['mandatory'] = mandatory_brw
            
        disc_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',data['form']['from_date']),('date','<=',data['form']['to_date']),('analytic_account_id','=',an_br),('partner_id','=',alst),('account_id','=',discretionary_credit_acc)])
        if disc_ser:
            disc_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,disc_ser)
        acc_type['discretionary'] = disc_brw
            
        admins_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',data['form']['from_date']),('date','<=',data['form']['to_date']),('analytic_account_id','=',an_br),('partner_id','=',alst),('account_id','=',admins_credit_acc)])
        if admins_ser:
            admins_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,admins_ser)
        acc_type['admins'] = admins_brw
            
        penalty_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',data['form']['from_date']),('date','<=',data['form']['to_date']),('analytic_account_id','=',an_br),('partner_id','=',alst),('account_id','=',penalty_acc)])
        if penalty_ser:
            penalty_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,penalty_ser)
        acc_type['penalty'] = penalty_brw
            
        interest_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',data['form']['from_date']),('date','<=',data['form']['to_date']),('analytic_account_id','=',an_br),('partner_id','=',alst),('account_id','=',interest_acc)])
        if interest_ser:
            interest_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,interest_ser)
        acc_type['interest'] = interest_brw
    
        if mandatory_brw:
            for i in mandatory_brw:
                m_credit_total += i.credit
                m_debit_total += i.debit
                m_tax_total += i.account_tax_id.name
        
        acc_type['m_credit_total'] = m_credit_total
        acc_type['m_debit_total'] = m_debit_total
        acc_type['m_tax_total'] = m_tax_total
        
        if disc_brw:
            for i in disc_brw:
                d_credit_total += i.credit
                d_debit_total += i.debit
                d_tax_total += i.account_tax_id.name
            
        acc_type['d_credit_total'] = d_credit_total
        acc_type['d_debit_total'] = d_debit_total
        acc_type['d_tax_total'] = d_tax_total
        
        if admins_brw:
            for i in admins_brw:
                a_credit_total += i.credit
                a_debit_total += i.debit
                a_tax_total += i.account_tax_id.name
            
        acc_type['a_credit_total'] = a_credit_total
        acc_type['a_debit_total'] = a_debit_total
        acc_type['a_tax_total'] = a_tax_total
        
        if penalty_brw:
            for i in penalty_brw:
                p_credit_total += i.credit
                p_debit_total += i.debit
                p_tax_total += i.account_tax_id.name
            
        acc_type['p_credit_total'] = p_credit_total
        acc_type['p_debit_total'] = p_debit_total
        acc_type['p_tax_total'] = p_tax_total
        
        if interest_brw:
            for i in interest_brw:
                i_credit_total += i.credit
                i_debit_total += i.debit
                i_tax_total += i.account_tax_id.name
            
        acc_type['i_credit_total'] = i_credit_total
        acc_type['i_debit_total'] = i_debit_total
        acc_type['i_tax_total'] = i_tax_total
        
        grand_credit_total = m_credit_total + d_credit_total + a_credit_total + p_credit_total + i_credit_total
        grand_debit_total = m_debit_total + d_debit_total + a_debit_total + p_debit_total + i_debit_total
        grand_tax_total = m_tax_total + d_tax_total + a_tax_total + p_tax_total + i_tax_total
        
        acc_type['grand_credit_total'] = grand_credit_total
        acc_type['grand_debit_total'] = grand_debit_total
        acc_type['grand_tax_total'] = grand_tax_total
        acc_type_list.append(acc_type)
        return acc_type_list
        
    def get_grand_total(self,data):
        partner_lst=[]
        grand_lst=[]
        acc_type={}
        credit_total = 0
        debit_total = 0
        tax_total = 0
        all_acc_brw = []
        mandatory_credit_acc,discretionary_credit_acc,admins_credit_acc,interest_acc,penalty_acc='','','','',''
        partner_mv_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',data['form']['from_date']),('date','<=',data['form']['to_date'])])
        if partner_mv_ser:
            partner_mv_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,partner_mv_ser)
            if partner_mv_brw:
                for br in partner_mv_brw:
                    if br.partner_id.id:
                        if br.partner_id.id not in partner_lst:
                            partner_lst.append(br.partner_id.id)

        ana_lst=[]
        acc_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('partner_id','in',partner_lst),('date','>=',data['form']['from_date']),('date','<=',data['form']['to_date'])])
        if acc_ser:
            acc_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,acc_ser)
            if acc_brw:
                for ac_br in acc_brw: 
                    if ac_br.analytic_account_id.id not in ana_lst:
                        if ac_br.analytic_account_id.id:
                            ana_lst.append(ac_br.analytic_account_id.id)
        
        acc_ser = self.pool.get('grant.account').search(self.cr,self.uid,[])
        if acc_ser:
            acc_mv = self.pool.get('grant.account').browse(self.cr,self.uid,acc_ser)
            if acc_mv:
                for ac in acc_mv:
                    if ac.grant_id.name == 'Mandatory Grant':
                        mandatory_credit_acc = ac.account_id.id
                    if ac.grant_id.name == 'Discretionary Grant':
                        discretionary_credit_acc = ac.account_id.id
                    if ac.grant_id.name == 'Admin Grant':
                        admins_credit_acc = ac.account_id.id
                    if ac.grant_id.name == 'Interest':
                        interest_acc = ac.account_id.id                    
                    if ac.grant_id.name == 'Penalty':
                        penalty_acc = ac.account_id.id
        
        
#         leavy_ser = self.pool.get('leavy.income.config').search(self.cr,self.uid,[])
#         if leavy_ser:
#             leavy_brw = self.pool.get('leavy.income.config').browse(self.cr,self.uid,leavy_ser)
        
        all_acc_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',data['form']['from_date']),('date','<=',data['form']['to_date']),('analytic_account_id','in',ana_lst),('partner_id','in',partner_lst),('account_id','in',[mandatory_credit_acc,discretionary_credit_acc,admins_credit_acc,penalty_acc,interest_acc])])
        if all_acc_ser:
            all_acc_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,all_acc_ser)
        
        for i in all_acc_brw:
            credit_total += i.credit
            debit_total += i.debit
            tax_total += i.account_tax_id.name
        
        acc_type['final_credit_total'] = credit_total
        acc_type['final_debit_total'] = debit_total
        acc_type['final_tax_total'] = tax_total
 
        grand_lst.append(acc_type)
        return grand_lst
        

        
class report_levy_moveline_report(osv.AbstractModel):
    _name = 'report.hwseta_finance.report_levy_report'
    _inherit = 'report.abstract_report'
    _template = 'hwseta_finance.report_levy_report'
    _wrapped_report_class = levy_report