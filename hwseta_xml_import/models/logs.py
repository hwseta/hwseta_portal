from openerp import api, fields, models



class Logs(models.Model):
    _name = 'xml.import.logs'
    
    import_datetime = fields.Datetime('Import DateTime')
    import_qualification_ids = fields.Char("Imported Qualifications Ids")
    import_qualification_lines = fields.Char('Imported Qualification Lines')
    import_exec_by = fields.Char('Imported By')
