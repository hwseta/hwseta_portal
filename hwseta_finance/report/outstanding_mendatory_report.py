from openerp.osv import osv, fields
import mx.DateTime
from mx.DateTime import RelativeDateTime
import time
from openerp.report import report_sxw
from datetime import datetime,date, timedelta
from openerp.tools.translate import _
from openerp import api, _
from openerp.exceptions import Warning

class outstanding_mandatory_grant_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        self.records = False
        super(outstanding_mandatory_grant_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_partner' : self.get_partner,
            'get_lines' : self.get_lines,
            'get_amount' : self.get_amount,
        })

    def get_partner(self):
        partner_lst=[]
        ant_brw = []
        mandatory_ser = self.pool.get('leavy.income.config').search(self.cr,self.uid,[])
        if mandatory_ser:
            mandatory_brw = self.pool.get('leavy.income.config').browse(self.cr,self.uid,mandatory_ser)
        if mandatory_brw:
            partner_mv_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('account_id','=',mandatory_brw.provision_acc.id)])
            if partner_mv_ser:
                partner_mv_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,partner_mv_ser)
                for br in partner_mv_brw:
                    if br.partner_id not in partner_lst:
                        partner_lst.append(br.partner_id)
        return  partner_lst   


    
    def get_lines(self,part):
        mandatory_move_brw = []
        mandatory_move_res = []
        mandatory_ser = self.pool.get('leavy.income.config').search(self.cr,self.uid,[])
        if mandatory_ser:
            mandatory_brw = self.pool.get('leavy.income.config').browse(self.cr,self.uid,mandatory_ser)
        if mandatory_brw:
            mandatory_move_ser = self.pool.get('account.move.line').search(self.cr,self.uid,[('partner_id','=',part.id),('account_id','=',mandatory_brw.provision_acc.id),('reconcile_id','=',False),('name','like','Mandatory')])
        if mandatory_move_ser:
            mandatory_move_brw = self.pool.get('account.move.line').browse(self.cr,self.uid,mandatory_move_ser)
            for manda in mandatory_move_brw:
                if not manda.reconcile_id:
                    mandatory_move_res.append(manda)
        return mandatory_move_brw
    
    def get_amount(self,line):
        if line.reconcile_partial_id:
            account_voucher_ser = self.pool.get('account.voucher.line').search(self.cr,self.uid,[('move_line_id','=',line.id)])
            if account_voucher_ser:
                account_voucher_brw = self.pool.get('account.voucher.line').browse(self.cr,self.uid,account_voucher_ser[0])
                res=account_voucher_brw.amount_original-account_voucher_brw.amount
        else:
            res=line.credit   
        return res
        
class report_mandatory_grant_moveline_report(osv.AbstractModel):
    _name = 'report.hwseta_finance.report_outstanding_mandatory_grant'
    _inherit = 'report.abstract_report'
    _template = 'hwseta_finance.report_outstanding_mandatory_grant'
    _wrapped_report_class = outstanding_mandatory_grant_report
    