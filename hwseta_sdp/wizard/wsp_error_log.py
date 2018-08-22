from openerp import models, fields, api, _
import re

class wsp_error_log(models.TransientModel):
    _name = 'wsp.error.log'
    _description = 'Will show wsp log if something goes wrong.'
    
    show_wsp_error_log = fields.Html(string='WSP Error Log')
    wsp_error_log_download = fields.Text(string='WSP Error Log')
    
    @api.model
    def default_get(self, fields_list):
        res = super(wsp_error_log, self).default_get(fields_list)
        if self._context.get('error_log_msg',False):
            msg_list = self._context['error_log_msg'].split('=')
            new_msg = ''
            pdf_error =''
            for msg_data in msg_list :
                new_msg += msg_data+'<br>'
                pdf_error+=str(re.sub('<[^>]*>', '', msg_data).encode('utf-8'))+"\n\n"
            res.update({'show_wsp_error_log' : new_msg,'wsp_error_log_download':pdf_error})
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
        return self.pool['report'].get_action(self._cr, self._uid, self._ids, 'hwseta_sdp.wsp_error_log_report',context=self._context)
        
    @api.multi
    def action_delete_incorrect_records(self):
        if self._context.get('total_employement_list',False):
            id_list = self._context['total_employement_list']
            self._cr.execute("delete from total_employment_profile_fields where id in %s",[tuple(id_list)])
            self._cr.commit()
        if self._context.get('planned_training_data_list',False):
            id_list = self._context['planned_training_data_list']
            self._cr.execute("delete from planned_training_fields where id in %s",[tuple(id_list)])
            self._cr.commit()
        if self._context.get('adult_education_training_data_list',False):
            id_list = self._context['adult_education_training_data_list']
            self._cr.execute("delete from planned_adult_education_training_fields where id in %s",[tuple(id_list)])
            self._cr.commit()
        if self._context.get('scarce_and_critical_data_list',False):
            id_list = self._context['scarce_and_critical_data_list']
            self._cr.execute("delete from scarce_and_critical_skills_fields where id in %s",[tuple(id_list)])
            self._cr.commit()
        
        return True
            
wsp_error_log()