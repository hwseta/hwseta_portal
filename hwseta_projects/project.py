from openerp import models, fields, api, _
class project_project(models.Model):
    _inherit = 'project.project'

    @api.one
    @api.depends('target_employed_learner','target_unemployed_learner')    
    def _get_total_targeted_learner(self):
        '''Method for calculate total no of targeted learner for project'''
        self.total_targeted_learner =  self.target_employed_learner + self.target_unemployed_learner

    @api.one
    @api.depends('budget_applied')
    def _get_decommitted_fund(self):
        '''Method for calculate decommitted fund for project'''
        decommitted_fund = 0.0
        if self.budget_applied :
            account_move_lines = self.env['account.move.line'].search([('project_id','=',self.id)])
            credits = 0.0
            debits = 0.0
            for lines in account_move_lines:
                debits+= lines.debit
                credits+= lines.credit
            if debits == credits :
                decommitted_fund = ((self.budget_applied) - (debits))
        self.decommitted_fund = decommitted_fund
        
    @api.one
    def _get_budget_committed_amount(self):
        '''Method for calculate budget committed all employer for this project'''
        total_cost = 0.0
        if self.employer_request_ids :
            for employer_cost in self.employer_request_ids : 
                total_cost += employer_cost.cost_required
        self.budget_committed =  total_cost    
        
    @api.one
    @api.depends('budget_committed')
    def _get_balance_due(self):
        '''Method for calculate Balance due for this project'''
        balance_due = 0.0
        if self.budget_committed :
            account_move_lines = self.env['account.move.line'].search([('project_id','=',self.id)])
            credits = 0.0
            debits = 0.0
            for lines in account_move_lines:
                debits+= lines.debit
                credits+= lines.credit
            if debits == credits :
                balance_due = ((self.budget_committed) - (debits))        
        self.balance_due =  balance_due              
    
    @api.one
    def _get_invoice_to_date(self):
        '''Method for calculate Balance due for this project'''
        invoice_to_date = 0.0
        if self.id :
            account_move_lines = self.env['account.move.line'].search([('project_id','=',self.id)])
            credits = 0.0
            debits = 0.0
            for lines in account_move_lines:
                debits+= lines.debit
                credits+= lines.credit
            if debits == credits :
                invoice_to_date = debits      
        self.invoice_to_date =  invoice_to_date      
        
    @api.one
    @api.depends('budget_applied','budget_committed')
    def _get_project_balance(self):
        '''Method for calculate Project Balance for this project'''
        balance = 0.0
        if self.budget_applied:
            balance = (self.budget_applied) - (self.budget_committed)
        self.project_balance =  balance    

    number = fields.Char(string='Number')
    funding = fields.Float(string='Funding Value')
    milestones = fields.Float(string='Milestones')
    invoice_to_date = fields.Float(string='Invoice To Date',compute='_get_invoice_to_date')
    seta_funding_year = fields.Many2one('account.fiscalyear', string='Funding Year')
    project_balance = fields.Float(string='Budget Balance',compute='_get_project_balance')
    comment = fields.Text('Executive Summary')
    project_parent_id = fields.Many2one('project.project', 'Parent Project', ondelete='cascade')
    sub_project_ids = fields.One2many('project.project', 'project_parent_id', 'Sub Project')
    course_fee = fields.Float(string='Course Fee')
    allowance = fields.Float(string='Allowance')
    uniform = fields.Float(string='Uniform')
    start_date=fields.Datetime('Start Date')
    end_date=fields.Datetime('End Date')
    project_description=fields.Html("Description")  
    project_id=fields.Many2one('hwseta.project',string="Project Name")   
    budget = fields.Float(string='Budget Available')
    budget_applied = fields.Float(string='Budget Allocated')
    eoi_start_date=fields.Datetime('Start Date')
    eoi_end_date=fields.Datetime('End Date')
    load_learner_start_date=fields.Datetime('Start Date')
    load_learner_end_date=fields.Datetime('End Date')    
#     no_of_tranche=fields.Integer(string="Number of Tranche")
    no_of_tranche=fields.Integer(string="Number of Tranche(18.1)")
    no_of_tranche_18_2=fields.Integer(string="Number of Tranche(18.2)")

    target_employed_learner = fields.Integer("Target Learner(18.1)")
    target_unemployed_learner = fields.Integer("Target Learner(18.2)")
    total_targeted_learner = fields.Integer("Total Targeted Learner(18.1/18.2) ",compute='_get_total_targeted_learner')
    decommitted_fund = fields.Float(string="Decommitted Fund",compute='_get_decommitted_fund')
    project_terms_and_condition = fields.Many2one('ir.attachment',string="Guide Line to Application")
    budget_committed = fields.Float("Budget Committed",compute='_get_budget_committed_amount')
    training_provider_applicable = fields.Boolean(string="Training Provider Applicable")
    moa_template = fields.Many2one('ir.attachment',string="MOA Template")
    conditional_approval_details = fields.Many2one('ir.attachment',string="Conditional Approval Details",default = False)
    balance_due = fields.Float("Balance Due",compute ='_get_balance_due')
    category = fields.Many2one('hwseta.project.category', string='Project Category')
    category_type = fields.Selection([('18.1','Employed Learners (18.1)'),('18.2','Unemployed Learners (18.2)')], string="Category Type")
    # Provider Groups
    provider_hwseta_group= fields.Boolean(string='HWSETA')
    provider_dhet_group= fields.Boolean(string='DHET')
    provider_hpcsa_group= fields.Boolean(string='HPCSA')
    provider_otherseta_group= fields.Boolean(string='Other SETA')
    provider_che_group= fields.Boolean(string='CHE')
    provider_sanc_group= fields.Boolean(string='SANC')
    provider_sapc_group= fields.Boolean(string='SAPC')

    @api.multi
    @api.depends('project_types')
    def onchange_provider_group(self,provider_hwseta_group,provider_dhet_group,provider_hpcsa_group,provider_otherseta_group,provider_che_group,provider_sanc_group,provider_sapc_group):
        '''This method is called when click on any one of the provider groups defined in project form,and used to filter out select group records in provider tab '''
        res = {}
        domain_val = []
        if provider_hwseta_group :
            domain_val.append(('provider_hwseta_group','=',True))
        if provider_dhet_group :
            domain_val.append(('provider_dhet_group','=',True))
        if provider_hpcsa_group :
            domain_val.append(('provider_hpcsa_group','=',True))
        if provider_otherseta_group :
            domain_val.append(('provider_otherseta_group','=',True))
        if provider_che_group :
            domain_val.append(('provider_che_group','=',True))
        if provider_sanc_group :
            domain_val.append(('provider_sanc_group','=',True))
        if provider_sapc_group :
            domain_val.append(('provider_sapc_group','=',True))
        if not domain_val :
            return res
        else:
            provider_vals = [(0,0,{'provider_id':provider.id,
                                   'provider_accreditation_num': provider.provider_accreditation_num,
                                   'project_description':self.project_description,
                                   }) for provider in self.env['res.partner'].search(domain_val) ]
            res.update({'value':{ 'pro_ids' : provider_vals }})
        return res

    @api.onchange('category_type')
    def onchange_category_type(self):
        '''This method is used to filter project category'''
        if not self.category_type:
            self.category = None
        category_values = self.env['hwseta.project.category'].search([('category_type','=',self.category_type)])
        category_lst = [cate.id for cate in category_values]
        if self.category_type == '18.1' and category_values:
            return {'domain': {'category': [('id', 'in', category_lst)]}}
        elif self.category_type == '18.2' and category_values:
            return {'domain': {'category': [('id', 'in', category_lst)]}}
        return {'domain': {'category': [('id', 'in', [])]}}

project_project()