from openerp import models, fields, api, _
from datetime import date
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp

class account_bank_statement(models.Model):
    _inherit = 'account.bank.statement'

    branch_id = fields.Many2one('hr.department', string='Branch', domain=[('is_branch','=',True)], track_visibility='onchange')
    province_id = fields.Many2one('res.country.state', string='Province', track_visibility='onchange')
    state = fields.Selection([('draft', 'New'),
                                   ('open','Open'), # used by cash statements
                                   ('approve1','Approve by Accountant'),
                                   ('approve2','Approve by Financial Manager'),
                                   ('approve3','Approve by CFO'),
                                   ('confirm', 'Closed')],
                                   'Status', required=True, readonly="1",
                                   copy=False,
                                   help='When new statement is created the status will be \'Draft\'.\n'
                                        'And after getting confirmation from the bank it will be in \'Confirmed\' status.')
          
   
    @api.multi
    def approve_by_accountant(self):
        self.write({'state':'approve1'})
        return True
    
    @api.multi
    def approve_by_manager(self):
        self.write({'state':'approve2'})
        return True
    
    @api.multi
    def approve_by_cfo(self):
        self.write({'state':'approve3'})
        return True
    
account_bank_statement()

class account_bank_statement_line(models.Model):
    _inherit = 'account.bank.statement.line'

    docs = fields.Many2one('ir.attachment',string='Documents')
    
account_bank_statement_line()

class crossovered_budget_lines(models.Model):
    
    _inherit = "crossovered.budget.lines"
    
    approved_amount=fields.Float( string='Planned Amount', required=True, digits_compute=dp.get_precision('Account'))
    commited_amount=fields.Float( string='Commited Amount', required=True, digits_compute=dp.get_precision('Account'))
    recomited_amount=fields.Float( string='Recompiled Amount', required=True, digits_compute=dp.get_precision('Account'))

crossovered_budget_lines()

class petty_cash(models.Model):
    _name = 'petty.cash'
    _inherit = ['mail.thread']
    _description = 'Petty Cash'
    
    ## Fields for Petty cash Requisition.
    name = fields.Char(string='Request No.', default= lambda self: self.env['ir.sequence'].get('petty.cash'))
    branch_id = fields.Many2one('hr.department', string='Branch Name', domain=[('is_branch','=',True)], track_visibility='onchange')
    province_id = fields.Many2one('res.country.state', string='Province', track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string='Department', track_visibility='onchange')
    date = fields.Date(string='Date', default=date.today(), track_visibility='onchange')
    amount_requested = fields.Float(string='Requested Amount', track_visibility='onchange')  
    account_number = fields.Integer(string='Account Number', track_visibility='onchange')
    acc_number = fields.Char(string='Account Number', track_visibility='onchange')
    requested_by = fields.Many2one('hr.employee', string='Requested By', track_visibility='onchange')
    description_need = fields.Text(string='Description', track_visibility='onchange')
    approved_by = fields.Many2one('res.users', string='Approved By')
    received_by = fields.Many2one('res.users', string='Received By')
    approve_by = fields.Many2one('hr.employee', string='Approved By')
    receive_by = fields.Many2one('hr.employee', string='Received By')
    signature_approved_by = fields.Binary(string='Signature')
    signature_received_by = fields.Binary(string='Signature')
    state = fields.Selection([
                              ('draft','Draft'),
                              ('requested','Requested'),
                              ('recommend','Recommended'),
                              ('approved','Approved'),
                              ('received','Received'),
                              ('deny','Denied'),
                              ], 
                             string='State', default='draft', track_visibility='onchange')
    user_id = fields.Many2one('res.users', string='Related User')
    branch_chk = fields.Boolean(string="Branch")
    province_chk = fields.Boolean(string="Province")
#     analytic_id = fields.Many2one('account.analytic.account', string='Province')
    
    
    @api.multi
    def onchange_requested_by(self, requestor):
        if not requestor:
            return {}
        else:
            user_data = self.env['hr.employee'].browse(requestor).user_id
            return {'value':{'received_by':user_data and user_data.id}}
    
    @api.multi
    def onchange_branch_id(self, province_id):
        if province_id:
            return {'value':{'province_id':'' }}
    
    @api.multi
    def onchange_province_id(self, branch_id):
        if branch_id:
            return {'value':{'branch_id':'' }}
    
    
    @api.multi
    def action_request_petty_cash(self):
        ## Previously petty cash limit is considered fix as 500 R. But now it is configurable under
        ## Admin Configuration -> Petty Cash. Where you can set maximum petty cash request limit amount.
        admin_config_data = self.env['leavy.income.config'].search([])
        if isinstance(admin_config_data, list) :
            admin_config_data = admin_config_data[0]
        if self.amount_requested > admin_config_data.petty_limit :
#         if self.amount_requested > 500 :
            raise Warning(_('You can request maximum of 500R per transaction!'))
        self.write({'state':'requested'})
        return True
    
    @api.multi
    def action_recommend_petty_cash(self):
        self.write({'state':'recommend'})
        return True
    
        
    @api.multi
    def action_approve_petty_cash(self):    
        ''' This method will create a line entry in cash register master if it is open.'''
        ## Checking for whether cash register is open or not.
        cash_reg_data=[]
        if self.branch_id.id:
            cash_journal = self.env['account.journal'].search([('name','=','Cash')])
            cash_reg_data = self.env['account.bank.statement'].search([('journal_id','=',cash_journal.id),('state','=','open'),('branch_id','=',self.branch_id.id)])        
        if self.province_id.id:
            cash_journal = self.env['account.journal'].search([('name','=','Cash')])
            cash_reg_data = self.env['account.bank.statement'].search([('state','=','open'),('province_id','=',self.province_id.id)])        
            ##removed journal checking condition
#             cash_reg_data = self.env['account.bank.statement'].search([('journal_id','=',cash_journal.id),('state','=','open'),('province_id','=',self.province_id.id)])
        
        if cash_reg_data :
            ## Getting partner based on requested employee.
            related_user = self.requested_by.user_id
            if not related_user :
                raise Warning(_('Please select related user under Requested By (Employee)!'))
            partner = related_user.partner_id.id
            cash_line_data = {
                                'name':'Personal',
                                'ref':self.name,
                                'partner_id':partner,
                                'amount':int(-self.amount_requested),
                              }
            cash_reg_data.write({'line_ids':[(0,0,cash_line_data)]})
        else:
            if self.branch_id.id:
                raise Warning(_('Cash Box for branch %s should be open in order to approve this order!')%(self.branch_id.name))
            if self.province_id.id:
                raise Warning(_('Cash Box for Province %s should be open in order to approve this order!')%(self.province_id.name))
        
        ## Code for getting signature from Employee master.
        employee_data = self.env['hr.employee'].search([('user_id','=',self._uid)])
        if employee_data.signature:
            signature = employee_data.signature
        else:
            signature = False
        self.write({'state':'approved','approve_by':employee_data.id, 'signature_approved_by':signature})
        return True
    
    @api.multi
    def action_deny_petty_cash(self):
        self.write({'state':'deny'})
        return True
    
    @api.multi
    def action_receive_petty_cash(self):
        ## Code for getting signature from Employee master.
        employee_data = self.env['hr.employee'].search([('user_id','=',self._uid)])
        if employee_data.signature:
            signature = employee_data.signature
        else:
            signature = False
        self.write({'state':'received','receive_by':employee_data.id,'signature_received_by':signature})
        return True
    
petty_cash()