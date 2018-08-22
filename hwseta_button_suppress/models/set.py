from openerp import api, fields, models, _
class ResUsers(models.Model):
    _inherit = "res.users"
    
    @api.model
    def check_user_group(self):
        if self._uid ==1 :
            return 0 
        if(self.has_group('hwseta_sdp.group_sdf_user') or self.has_group('hwseta_finance.group_employer_user')) :
            return 1
        return 0