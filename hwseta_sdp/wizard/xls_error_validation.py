from openerp import models, fields, api, _
import re

class xls_error_validation(models.TransientModel):
    _name = 'xls.error.validation'
    _description = 'Will show import log if something goes wrong.'
    
    xls_import_log = fields.Html(string='XLS Import Log')
    xls_import_log_download = fields.Text(string='XLS Import Log')
    
    @api.model
    def default_get(self, fields_list):
        res = super(xls_error_validation, self).default_get(fields_list)
        if self._context.get('error_log_msg',False):
            msg_list = self._context['error_log_msg'].split('=')
            new_msg = ''
            pdf_error =''
            for msg_data in msg_list :
                new_msg += msg_data+'<br>'
                pdf_error+=str(re.sub('<[^>]*>', '', msg_data).encode('utf-8'))+"\n\n"
            res.update({'xls_import_log' : new_msg,'xls_import_log_download':pdf_error})
        return res
    
    @api.multi
    def action_download_incorrect_wsp_file(self):
        return {
                'type' : 'ir.actions.act_url',
                'url': '/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=%s' % (self._context.get('incorrect_id')),
                'target': 'self',                
                }
    
    @api.multi
    def action_download_error_log(self):
        return self.pool['report'].get_action(self._cr, self._uid, self._ids, 'hwseta_sdp.error_log_report',context=self._context)
        
    
xls_error_validation()