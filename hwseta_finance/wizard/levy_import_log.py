from openerp import models, fields, api, _

class levy_import_log(models.TransientModel):
    _name = 'levy.import.log'
    
    message = fields.Html(string='Message')
    
    @api.model
    def default_get(self, fields_list):
        res = super(levy_import_log, self).default_get(fields_list)
        if self._context.get('message',False):
            res.update({'message' : self._context.get('message')})
        return res
    
levy_import_log()
