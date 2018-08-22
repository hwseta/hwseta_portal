from openerp import models, fields, api, _

class leavy_income_wiz(models.Model):
    _name = 'leavy.income.wiz'
    
    sdl_numbers = fields.Html(string='Missing SDL Numbers')
    
    @api.model
    def default_get(self, fields_list):
        res = super(leavy_income_wiz, self).default_get(fields_list)
        if self._context.get('missing_sdl',False):
            msg = ''
            count = 0
            for sdl_no in self._context['missing_sdl']:
                count +=1
                msg += '<font size="3"> <b>'+sdl_no+'</b> </font>'+','
                if count == 8:
                    msg += '<br>'
                    count = 0
            res.update({'sdl_numbers':msg})
        return res
    
    @api.multi
    def action_download_missing_employers_file(self):
        return {
                 'type' : 'ir.actions.act_url',
                 'url': '/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=%s' % (self._context.get('incorrect_id')),
                 'target': 'self',                
                }
leavy_income_wiz()

class missing_sdl(models.Model):
    _name = 'missing.sdl'
    
    name = fields.Char(string='SDL No.')
    leavy_wiz_id = fields.Many2one('leavy.income.wiz', string='Leavy Wizard')
missing_sdl()