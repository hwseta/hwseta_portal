from openerp import models, fields, api, _
import re

class moa_attachment(models.TransientModel):
    _name = 'moa.attachment'
    _description = 'Will show import log if something goes wrong.'
    
    moa_attachment_id = fields.Many2one('ir.attachment',"MOA Attach")
    
    
    @api.multi
    def action_attach_moa(self):
        ## Removing MOA records if exists before.
        learning_programme = self.env['learning.programme'].search([('id','=',self._context['active_id'])])
        if learning_programme.moa_ids : 
            learning_programme.write({'moa_ids' : [(2,moa_info.id) for moa_info in learning_programme.moa_ids]})
        ## Generating MOA records which is equal to no of unique project types.
        moa_list = [(0,0,{'name' : 'MOA for ','learning_programme_id' : learning_programme.id,'attach_moa':self.moa_attachment_id.id}) for project_type_info in self.env['hwseta.project.types'].browse(learning_programme.learning_project_type_id.id)]
        learning_programme.write({'moa_ids' : moa_list, 'is_moa_attached': True})        
        return True
    
    @api.multi
    def action_cancel(self):
        pass
        return True    
    
        
    
moa_attachment()