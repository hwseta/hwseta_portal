from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import datetime
from openerp.tools.translate import _

class mandatory_wiz(models.TransientModel):
    _name = 'mandatory.wiz'

    
    from_date  = fields.Date('From Date')
    to_date = fields.Date('To Date')

    @api.multi
    def generate_mandatory_report(self):
        data1 = self.read()
        data = data1[0]
        if self._context is None:
            self._context = {}
        
        from_date = datetime.strptime(data['from_date'], '%Y-%m-%d').date()
        to_date = datetime.strptime(data['to_date'], '%Y-%m-%d').date()
        if from_date > to_date:
            raise Warning(_('From Date could not be greater than To Date!'))
        datas = {
            'ids': self._context.get('active_ids', []),
            'model': 'account.analytic.account',
             'form': data,
        }
        return self.pool['report'].get_action(self._cr, self._uid, [],'hwseta_finance.report_mandgrant', data=datas, context=self._context)
mandatory_wiz()

# class report_mandgrant(models.AbstractModel):
#     _name = 'report.hwseta_finance.report_mandgrant'
#     _inherit = 'report.abstract_report'
#     _template = 'hwseta_finance.report_mandgrant'
#     _wrapped_report_class = account_analytic_balance