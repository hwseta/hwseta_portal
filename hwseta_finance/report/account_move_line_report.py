# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
import mx.DateTime
from mx.DateTime import RelativeDateTime
import time
from openerp.report import report_sxw
from datetime import datetime,date, timedelta
from openerp.tools.translate import _
from openerp import api, _

class moveline_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        self.records = False
        super(moveline_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_date':self.get_date,
            'get_account' : self.get_account,
            'get_ana_account' : self.get_ana_account,
            'get_lines' : self.get_lines,
            'get_total' : self.get_total,
            'get_grand_total' : self.get_grand_total,
        })
    
    def get_date(self,form):
        date_lst = []
        date_dict = {'from_date':form['form']['from_date'],'to_date':form['form']['to_date']} 
        date_lst.append(date_dict)
        return date_lst    
    
    def get_account(self,form):
        acc_lst=[]
        if form['form']['account']:
            acc_brw = self.pool.get('account.account').browse(self.cr,self.uid,form['form']['account'][0])
            acc_lst.append(acc_brw) 
        else:
            acc_mv_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',form['form']['from_date']),('date','<=',form['form']['to_date'])])
            if acc_mv_ser:
                acc_mv_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,acc_mv_ser)
                for br in acc_mv_brw:
                    if br.account_id not in acc_lst:
                        acc_lst.append(br.account_id)    
        return  acc_lst           
        
    
    def get_ana_account(self,alst,form):
        ana_lst=[]
        acc_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',form['form']['from_date']),('date','<=',form['form']['to_date']),('account_id','=',alst)])
        if acc_ser:
            acc_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,acc_ser)
            if acc_brw:
                for ac_br in acc_brw: 
                    if ac_br.analytic_account_id not in ana_lst:
                        if ac_br.analytic_account_id:
                            ana_lst.append(ac_br.analytic_account_id)
        return  ana_lst 
    
    
    def get_lines(self,alst,an_br,form):
        lst1=[]
        ant_brw=[]
        ant_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',form['form']['from_date']),('date','<=',form['form']['to_date']),('analytic_account_id','=',an_br),('account_id','=',alst)])
        if ant_ser:
            ant_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,ant_ser)
        return  ant_brw 
    
    def get_total(self,alst,an_br,form):
        lst1=[]
        dict = {}
        tot_dr=0
        tot_cr=0
        ant_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',form['form']['from_date']),('date','<=',form['form']['to_date']),('analytic_account_id','=',an_br),('account_id','=',alst)])
        if ant_ser:
            ant_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,ant_ser)
            for brw in ant_brw:
                tot_dr = tot_dr+brw.debit
                tot_cr = tot_cr+brw.credit
            tot_bal = tot_dr-tot_cr  
            dict['tot_dr'] = tot_dr
            dict['tot_cr'] = tot_cr
            dict['tot_bal'] = tot_bal
            lst1.append(dict)
        return  lst1
    
    def get_grand_total(self,alst,form):
        lst2=[]
        dict = {}
        tot_dr=0
        tot_cr=0
        ant_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('date','>=',form['form']['from_date']),('date','<=',form['form']['to_date']),('account_id','=',alst)])
        if ant_ser:
            ant_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,ant_ser)
            for brw in ant_brw:
                tot_dr = tot_dr+brw.debit
                tot_cr = tot_cr+brw.credit
            tot_bal = tot_dr-tot_cr  
            dict['tot_dr'] = tot_dr
            dict['tot_cr'] = tot_cr
            dict['tot_bal'] = tot_bal
            lst2.append(dict)
        return  lst2
        
class report_moveline_report(osv.AbstractModel):
    _name = 'report.hwseta_finance.report_move_line'
    _inherit = 'report.abstract_report'
    _template = 'hwseta_finance.report_move_line'
    _wrapped_report_class = moveline_report
#    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: