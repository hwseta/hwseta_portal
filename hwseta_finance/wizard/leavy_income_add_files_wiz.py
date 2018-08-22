from openerp import models, fields, api, _

class leavy_income_add_files_wiz(models.Model):
    _name = 'leavy.income.add.files.wiz'
    
    attachment_ids = fields.Many2many(comodel_name='ir.attachement', 'Documents')