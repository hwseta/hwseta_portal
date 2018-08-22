from openerp.osv import osv
from openerp.report import report_sxw

class report_unpaid_employer(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_unpaid_employer, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
                                   'get_objects': self._get_objects,
                                   })
        self.read_data = []
        
    def _get_objects(self):
        if self.read_data:
            return self.read_data
#         self.empty_acc = empty_acc
#         self.read_data = []
#         self.get_children(self.ids)
        return self.read_data

class report_unpaidemployer(osv.AbstractModel):
    _name = 'report.hwseta_finance.leavy_unpaid'
    _inherit = 'report.abstract_report'
    _template = 'hwseta_finance.leavy_unpaid'
    _wrapped_report_class = report_unpaid_employer