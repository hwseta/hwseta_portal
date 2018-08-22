from datetime import datetime
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import models, fields, api, _

class employer_unpaid(models.Model):
    _name = 'employer.unpaid'
    

    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    
    @api.multi
    def action_leavy_unpaid(self):
        data = self.read()[0]
        employer_obj = self.env['res.partner']
        employer_data = employer_obj.search([('employer','=',True)])
        unpaid_employers = []
        for employer in employer_data:
            paid = 0
            for leavy_history in employer.leavy_history_ids:
                period = leavy_history.period
                year = period[:4]
                day = period[-2:]
                month_day = period[-4:]
                month = month_day[:2]
                period_date = datetime.strptime(year+'-'+month+'-'+day, '%Y-%m-%d').date()
                if not (self.from_date or self.to_date):
                    raise Warning(_('From Date or To Date could not be blank!'))
                from_date = datetime.strptime(data['from_date'], '%Y-%m-%d').date()
                to_date = datetime.strptime(data['to_date'], '%Y-%m-%d').date()
                if from_date > to_date:
                    raise Warning(_('From Date could not be greater than To Date!'))
                if (period_date >= from_date and period_date <= to_date):
                    paid += 1
            if paid == 0:
                unpaid_employers.append(employer)
        if unpaid_employers :
            employers = []
            for emp in unpaid_employers:
                employers.append({
                                  'name':emp.name,
                                  'sdl':emp.employer_sdl_no and emp.employer_sdl_no,
                                  })
            data.update({'employers':employers})
            datas = {
                'ids': self._context.get('active_ids', []),
                'model': 'res.partner',
                'form': data
            }
            
            return self.pool['report'].get_action(self._cr, self._uid, [],'hwseta_finance.leavy_unpaid', data=datas, context=self._context)
        else:
            raise Warning(_('There are no unpaid employer for period from %s to %s')%(data['from_date'],data['to_date']))
        
employer_unpaid()