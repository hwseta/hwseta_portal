from openerp.exceptions import Warning
from openerp import models, fields, tools, api, _
from openerp.osv import fields as fields2


class hwseta_sic_master(models.Model):
    _name = 'hwseta.sic.master'
    
    name = fields.Char(string="Name", required=True)

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