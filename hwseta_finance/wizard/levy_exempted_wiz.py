from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import datetime
from openerp.tools.translate import _

class levy_exempted_wiz(models.TransientModel):
    _name = 'levy.exempted.wiz'
    
    from_date  = fields.Date('From Date')
    to_date = fields.Date('To Date',default= datetime.now())

    @api.multi
    def generate_levy_exempted_report(self):
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
            'model': 'account.move.line',
             'form': data,
        }
        return self.pool['report'].get_action(self._cr, self._uid, [],'hwseta_finance.report_levy_exempted', data=datas, context=self._context)

levy_exempted_wiz()