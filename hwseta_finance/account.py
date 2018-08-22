from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import datetime, timedelta
import csv
from StringIO import StringIO
import itertools
import calendar
import os
import subprocess
from openerp.addons.base.workflow.workflow import workflow

class account_account(models.Model):
    _inherit = 'account.account'
    
    business_unit = fields.Char('Business Unit')
    account = fields.Char('Account')
    subsidiary = fields.Char('Subsidiary')
    company = fields.Char('Company')
    l_d = fields.Integer('L D')
    p_e = fields.Char('P E')
    currency_code = fields.Char('Currency Code')
    
account_account()

class scheme_year(models.Model):
    _name = 'scheme.year'
    
    name = fields.Char('Name')
    code = fields.Char('Code')
    state = fields.Selection([('open','Open'),('closed','Closed')], string="Status", default='open')
    
    @api.multi
    def set_to_close(self):
        self.write({'state':'closed'})
        return True
    
scheme_year()

class grant_config(models.Model):
    _name = 'grant.config'
    
    scheme_yr = fields.Many2one('scheme.year','Scheme Year')
    mendatory = fields.Char('Mandatory Grant (%)')
    admin_grant = fields.Char('Admin Grant (%)')
    descritionary = fields.Char('Descritionary Grant (%)')
    hwseta_rec = fields.Char('HWSETA Received (%)')
    state = fields.Selection([('draft','Draft'),('executed','Executed')], string="Status", default='draft')
    
grant_config()

class grant_new(models.Model):
    _name = 'grant.new'
    
    name = fields.Char('Name')
    code = fields.Char('Code')
    
grant_new()

class grant_config_new(models.Model):
    _name = 'grant.config.new'
    
    scheme_yr = fields.Many2one('scheme.year','Scheme Year')
    grant_assign_id = fields.One2many('grant.config.assign','grant_ass',String ='Grant')
    hwseta_rec = fields.Char('HWSETA Received (%)')
    
grant_config_new()

class grant_config_assign(models.Model):
    _name = 'grant.config.assign'
    
    grant_ass = fields.Many2one('grant.config.new','Grant')
    grant_id = fields.Many2one('grant.new','Grant')
    value = fields.Char('Grant Percent')
    
    
grant_config_assign()

class grant_account(models.Model):
    _name = 'grant.account'
    
    grant1 = fields.Many2one('leavy.income.config','Grant')
    grant_id = fields.Many2one('grant.new','Grant')
    account_id = fields.Many2one('account.account','Accounts')
    
grant_account()

class account_voucher(models.Model):
    _inherit = 'account.voucher'
    
    @api.one
    def proforma_voucher(self):
        self.action_move_line_create()
        ir_model_data_obj = self.env['ir.model.data']
        mail_template_id = ir_model_data_obj.get_object_reference('hwseta_finance', 'email_template_mgrant_payment_notification')
        if mail_template_id:
            self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True,context=self.env.context)
        return True

account_voucher()

class account_fiscalyear(models.Model):
    _inherit = 'account.fiscalyear'
    
    scheme_year_id = fields.Many2one('scheme.year','Scheme Year')