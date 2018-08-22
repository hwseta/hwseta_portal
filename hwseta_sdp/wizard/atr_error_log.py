from openerp import models, fields, api, _
import re

class atr_error_log(models.TransientModel):
    _name = 'atr.error.log'
    _description = 'Will show ATR log if something goes wrong.'
    
    show_atr_error_log = fields.Html(string='ATR Error Log')
    atr_error_log_download = fields.Text(string='ATR Error Log')
    
    @api.model
    def default_get(self, fields_list):
        res = super(atr_error_log, self).default_get(fields_list)
        if self._context.get('error_log_msg',False):
            msg_list = self._context['error_log_msg'].split('=')
            new_msg = ''
            pdf_error =''
            for msg_data in msg_list :
                new_msg += msg_data+'<br>'
                pdf_error+=str(re.sub('<[^>]*>', '', msg_data).encode('utf-8'))+"\n\n"
            res.update({'show_atr_error_log' : new_msg,'atr_error_log_download':pdf_error})
        return res
    
    @api.multi
    def action_download_incorrect_atr_file(self):
        return {
                'type' : 'ir.actions.act_url',
                'url': '/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=%s' % (self._context.get('incorrect_id')),
                'target': 'self',                
                }
    
    @api.multi
    def action_download_error_log(self):
        return self.pool['report'].get_action(self._cr, self._uid, self._ids, 'hwseta_sdp.atr_error_log_report',context=self._context)
        
    @api.multi
    def action_delete_incorrect_records(self):
        if self._context.get('actual_training_data_list',False):
            id_list = self._context['actual_training_data_list']
            self._cr.execute("delete from actual_training_fields where id in %s",[tuple(id_list)])
            self._cr.commit()
        if self._context.get('actual_adult_education_training_list',False):
            id_list = self._context['actual_adult_education_training_list']
            self._cr.execute("delete from actual_adult_education_fields where id in %s",[tuple(id_list)])
            self._cr.commit()
        
        return True
            
atr_error_log()