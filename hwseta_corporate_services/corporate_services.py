from openerp import models, fields, api, _
class corporate_services(models.Model):
    _name = 'corporate.services'
    
    name = fields.Char(string='services')
    
corporate_services()