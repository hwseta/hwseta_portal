from openerp.exceptions import Warning
from openerp import models, fields, tools, api, _
from openerp.osv import fields as fields2


class hwseta_sic_master(models.Model):
    _name = 'hwseta.sic.master'
    _rec_name = 'name'
    
    seta_id = fields.Many2one('seta.branches', string='SETA ID')
    code = fields.Char(string="Code")
    name = fields.Char(string="Description", required=True)
    
    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        res = []
        for record in self:
            rec_str = ''
            if record.code:
                rec_str += '[' + record.code + '] '
            if record.name:
                rec_str += record.name
            res.append((record.id, rec_str))
        return res

    @api.model
    def name_search(self, name='', args=[], operator='ilike', limit=1000):
        args += ['|', ('name', operator, name), ('code', operator, name)]
        cuur_ids = self.search(args, limit=limit)
        return cuur_ids.name_get()    

hwseta_sic_master()

class hwseta_organisation_legal_status(models.Model):
    _name = 'hwseta.organisation.legal.status'
    
    name = fields.Char(string="Name", required=True)

hwseta_organisation_legal_status()


class hwseta_provider_focus_master(models.Model):
    _name = 'hwseta.provider.focus.master'
    
    name = fields.Char(string="Name", required=True)

hwseta_provider_focus_master()

class hwseta_chamber_master(models.Model):
    _name = 'hwseta.chamber.master'
    
    name = fields.Char(string="Name", required=True)

hwseta_chamber_master()

class hwseta_relation_to_provider_status(models.Model):
    _name = 'hwseta.relation.to.provider.status'
    
    name = fields.Char(string="Name", required=True)

hwseta_relation_to_provider_status()


class hwseta_master(models.Model):
    _name = 'hwseta.master'
    
    name = fields.Char(string="Name", required=True)

hwseta_master()