from openerp.osv import fields, osv
from openerp.report import report_sxw


class organisation_payment_report(report_sxw.rml_parse):
    

    def __init__(self, cr, uid, name, context=None):
        super(organisation_payment_report, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'compute_credit_amount_total': self.compute_credit_amount_total,
             'compute_credit_original_amount':self.compute_credit_original_amount,
             'compute_credit_open_balance':self.compute_credit_open_balance,
             'compute_debit_amount_total': self.compute_debit_amount_total,
             'compute_debit_original_amount':self.compute_debit_original_amount,
             'compute_debit_open_balance':self.compute_debit_open_balance,
        })

    def compute_credit_amount_total(self,o):
           amt_total = 0
           for line in o.line_cr_ids:
              amt_total += line.amount
           return amt_total   
       
    
    def compute_credit_original_amount(self,o):
           amt_total = 0
           for line in o.line_cr_ids:
              amt_total += line.amount_original
           return amt_total 
    
    def compute_credit_open_balance(self,o):
           amt_total = 0
           for line in o.line_cr_ids:
              amt_total += line.amount_unreconciled
           return amt_total 
    
    
    def compute_debit_amount_total(self,o):
           amt_total = 0
           for line in o.line_dr_ids:
              amt_total += line.amount
           return amt_total   
       
    
    def compute_debit_original_amount(self,o):
           amt_total = 0
           for line in o.line_dr_ids:
              amt_total += line.amount_original
           return amt_total 
    
    def compute_debit_open_balance(self,o):
           amt_total = 0
           for line in o.line_dr_ids:
              amt_total += line.amount_unreconciled
           return amt_total 
      

class organisation_payment_report_view(osv.AbstractModel):
    _name = 'report.hwseta_finance.organisation_payment_report'
    _inherit = 'report.abstract_report'
    _template = 'hwseta_finance.organisation_payment_report'
    _wrapped_report_class = organisation_payment_report
