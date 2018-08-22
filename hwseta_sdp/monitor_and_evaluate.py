from openerp import models, fields, api, _
from datetime import datetime
from openerp.exceptions import Warning

class mae_document(models.Model):
    _name = 'mae.document'
    _inherit='mail.thread'
    
    name = fields.Many2one('project.document',string="Document Name")
    monitor_and_evalaute_id = fields.Many2one('monitor.and.evaluate', string='Name')
    attached = fields.Binary(string='attach')
    attach_doc = fields.Many2one('ir.attachment', string='Attach Document')
    
mae_document()

class monitor_and_evaluate(models.Model):
    _name = 'monitor.and.evaluate'
    _inherit='mail.thread'
    
    @api.multi
    def get_related_employee(self):
        user_id = self.env.user.id
        employee_obj = self.env['hr.employee']
        employee_data = employee_obj.search([('user_id','=',user_id)])
        if not employee_data:
            return False
        else:
            if len(employee_data) > 1:
                employee_data = employee_data[0]
                return employee_data.id
            
    @api.one
    @api.depends(
                 'project_id',
                 'employer_id'
                 )
    def _get_amount_approved(self):
        amount_approved = 0.0
        if self.project_id and self.employer_id:
            employer_projects = self.env['employer.requests'].search([('project_id','=',self.project_id.id),('employer_id','=',self.employer_id.id)])
            for employer_project in employer_projects:
                amount_approved = 0.0
                amount_approved = employer_project.cost_required
        self.amount_approved = amount_approved
        
    @api.one
    @api.depends(
                 'project_id',
                 'employer_id',
                 'amount_approved',
                 )
    def _get_amount_disbursed(self):
        amount_disbursed = 0.0
        if self.project_id and self.employer_id:
            account_move_lines = self.env['account.move.line'].search([('project_id','=',self.project_id.id),('partner_id','=',self.employer_id.id)])
            credits = 0.0
            debits = 0.0
            for lines in account_move_lines:
                debits+= lines.debit
                credits+= lines.credit
            if debits == credits :
                amount_disbursed = self.amount_approved - debits
        self.amount_disbursed = amount_disbursed        
        
    @api.one
    @api.depends(
                 'amount_approved',
                 'amount_disbursed',
                 )
    def _get_amount_outstanding(self):
        amount_outstanding = 0.0
        if self.amount_approved and self.amount_disbursed :
                amount_outstanding = self.amount_approved - self.amount_disbursed
        self.amount_outstanding = amount_outstanding     

    @api.one
    @api.depends(
                 'project_id',
                 'employer_id'
                 )
    def _get_employed(self):
        employed = 0
        if self.project_id and self.employer_id:
            employer_projects = self.env['employer.requests'].search([('project_id','=',self.project_id.id),('employer_id','=',self.employer_id.id)])
            for employer_project in employer_projects:
                employed = 0
                employed = employer_project.app_employed
        self.no_of_employed = employed
        
    @api.one
    @api.depends(
                 'project_id',
                 'employer_id'
                 )
    def _get_unemployed(self):
        unemployed = 0
        if self.project_id and self.employer_id:
            employer_projects = self.env['employer.requests'].search([('project_id','=',self.project_id.id),('employer_id','=',self.employer_id.id)])
            for employer_project in employer_projects:
                unemployed = 0
                unemployed = employer_project.app_unemployed
        self.no_of_unemployed = unemployed   
        
    @api.one
    @api.depends(
                 'no_of_employed',
                 'no_of_unemployed'
                 )
    def _get_total_employed_unemloyed(self):
        total = (self.no_of_employed) + (self.no_of_unemployed)
        self.total_employed_unemployed = total               
        
    name = fields.Char(string='Name')
    state = fields.Selection([
                              ('org_and_proj','Organisation and Project Info'),
                              ('quality','Quality Assurance'),
                              ('administer','Administration'),
                              ('finance','Finance Audit Programme'),
                              ('learner_report','Learner Report'),
                              ('project_evaluation','Project Evaluation'),
                              ('overall_assess','Overall Assessment'),
                              ('submitted','Submitted'),
                              ('recommended','Recommended'),
                              ('approved','Approved'),
                              ], string="state", default='org_and_proj',track_visibility='onchange')
    # Fields for SECTION A : Organisational Details
    employer_id = fields.Many2one('res.partner', string='Name of Organisation')
    sdl_number = fields.Char(string='SDL No.',track_visibility='onchange')
    date_visit = fields.Date(string='Date Of Visit.')
#     me_conducted_by = fields.Many2one('res.users', string='M&E Conducted By', default=lambda self: self.env.user)
    me_conducted_by = fields.Char('M&E Conducted By')
    amount_approved = fields.Float(string='Amount Approved',compute='_get_amount_approved',track_visibility='onchange')
    amount_disbursed = fields.Float(string='Amount Disbursed',compute='_get_amount_disbursed',track_visibility='onchange')
    amount_outstanding = fields.Float(string='Amount Outstanding',compute='_get_amount_outstanding',track_visibility='onchange')
    
    # Fields for SECTION B : DISCRETIONARY GRANT PROJECT INFORMATION.
    project_info_ids = fields.One2many('grant.project.info', 'monitor_evaluate_id', string='Project Info')
    
    commencement_date = fields.Date(string='Commencement Date',track_visibility='onchange')
    completion_date = fields.Date(string='Completion Date',track_visibility='onchange')
    dropouts_emplyed = fields.Integer(string='Employed 18.1')
    dropouts_unemplyed = fields.Integer(string='Unemployed 18.2')
    
    # Fields for SECTION C : Quality Assurance.
    report_prepared = fields.Boolean(string='Report Prepared')
    regular_meeting = fields.Boolean(string='Regular Meeting')
    learner_dispute = fields.Boolean(string='Learner Dispute')
    project_reviewed = fields.Boolean(string='Project Reviewed')
    outcome_reviewed = fields.Boolean(string='Outcome Reviewed')
    comment_report_prepared = fields.Text(string='Comment Report Prepared')
    comment_regular_meeting = fields.Text(string='Comment Regular Meeting')
    comment_learner_dispute = fields.Text(string='Comment Learner Dispute')
    comment_project_reviewed = fields.Text(string='Comment Project Reviewed')
    comment_outcome_reviewed = fields.Text(string='Comment Outcome Reviewed')
    
    # Fields for SECTION D : Administration.
    req_main_met = fields.Boolean(string='Req and Maintenance')
    req_main_not_met = fields.Boolean(string='Not Req and Maintenance')
    data_main_met = fields.Boolean(string='Database Maintenance')
    data_main_not_met = fields.Boolean(string='Not Database Maintenance')
    confi_rec_met = fields.Boolean(string='Confidentiality Rec')
    confi_rec_not_met = fields.Boolean(string='Not Confidentiality Rec')
    rep_adm_capmet = fields.Boolean(string='Reporting and Administrative Capacity MET')
    rep_adm_not_capmet = fields.Boolean(string='Reporting and Administrative Capacity not MET')
    assessor_avail_met = fields.Boolean(string='Assessor Availability MET')
    assessor_avail_not_met = fields.Boolean(string='Assessor Availability Not MET')
    moderator_avail_met = fields.Boolean(string='Moderator Availability MET')
    moderator_avail_not_met = fields.Boolean(string='Moderator Availability not MET')
    coach_met = fields.Boolean(string='Coaches MET')
    coach_not_met = fields.Boolean(string='Coaches not MET')
    role_player_met = fields.Boolean(string='Role Players MET')
    role_player_not_met = fields.Boolean(string='Role Players not MET')
    access_resource_met =  fields.Boolean(string='Access Resource MET')
    access_resource_not_met =  fields.Boolean(string='Access Resource not MET')
    train_met = fields.Boolean(string='Training MET')
    train_not_met = fields.Boolean(string='Training not MET')
    comment_learner = fields.Text(string='Comment Learner',track_visibility='onchange')
    comment_database = fields.Text(string='Comment Database',track_visibility='onchange')
    comment_access = fields.Text(string='Comment Access',track_visibility='onchange')
    comment_reporting = fields.Text(string='Comment Reporting',track_visibility='onchange')
    comment_assessor = fields.Text(string='Comment Assessor',track_visibility='onchange')
    comment_moderator = fields.Text(string='Comment Moderator',track_visibility='onchange')
    comment_coaches = fields.Text(string='Comment Coaches',track_visibility='onchange')
    comment_role = fields.Text(string='Comment Role',track_visibility='onchange')
    comment_resource = fields.Text(string='Comment Resource',track_visibility='onchange')
    comment_training = fields.Text(string='Comment Training',track_visibility='onchange')
    
    # Fields for SECTION E : Finance Audit Programme.
    insti_have_moa = fields.Boolean(string='Have a Copy of MOA')
    signature_appear = fields.Boolean(string='Signature Appear')
    signatory_authority = fields.Boolean(string='Signatory Authority')
    read_content_moa = fields.Boolean(string='Read the Contents in the MOA')
    bank_sole_purpose = fields.Boolean(string='Bank Sole Purpose')
    bank_secure_stmt = fields.Boolean(string='Secure Bank Statement')
    list_receipt_bank_stmt = fields.Boolean(string='List reseipt reflected on the bank statement')
    list_payment_bank_stmt = fields.Boolean(string='List payment reflected on the bank statement')
    comment_insti_have_moa = fields.Text(string='Have a Copy of MOA')    
    comment_signature_appear = fields.Text(string='Signature Appear')
    comment_signatory_authority = fields.Text(string='Signatory Authority')
    comment_read_content_moa = fields.Text(string='Read the Contents in the MOA')
    comment_bank_sole_purpose = fields.Text(string='Bank Sole Purpose')
    comment_bank_secure_stmt = fields.Text(string='Secure Bank Statement')
    comment_list_receipt_bank_stmt = fields.Text(string='List reseipt reflected on the bank statement')
    comment_list_payment_bank_stmt = fields.Text(string='List payment reflected on the bank statement')
    # Fields for SECTION F : Learner Report.
    comment_abt_hwseta_prog = fields.Text(string='About HWSETA Programmes')
    comment_abt_satisfy_info = fields.Text(string='About HWSETA Satisfy Info')
    comment_abt_sign_contract = fields.Text(string='About Signed Contract')
    comment_abt_contract_about = fields.Text(string='What the Contract About')
    comment_abt_improve_recruit = fields.Text(string='About Improvement in Recruitment and Selection')
    comment_abt_theoretical_comp = fields.Text(string='About where theoretical training takes place')
    comment_abt_training_lang = fields.Text(string='About where training language')
    comment_abt_week_month_allowance = fields.Text(string='About Weekly or Monthly Allowance')
    comment_abt_supervisor_advice = fields.Text(string='About Supervisor advice during Training')
    comment_abt_overtime = fields.Text(string='About Overtime')
    comment_abt_received_uniforms = fields.Text(string='About Received Uniforms')
    comment_abt_received_books = fields.Text(string='About Received Books')
    comment_abt_remark = fields.Text(string='About Remark')
    # Fields for SECTION G : OVERALL PROJECT EVALUATION.
    indicator_no_of_learner = fields.Text(string='Number of Learners')
    indicator_no_of_dropouts = fields.Text(string='Number of Dropouts')
    indicator_factors_success = fields.Text(string='Factors Success/Failure')
    indicator_financial_performance = fields.Text(string='Financial Performance')
    action_evaluate_success = fields.Text(string='Financial Performance')
    action_no_of_learner = fields.Text(string='Number of Learners')
    action_no_of_dropouts = fields.Text(string='Number of Dropouts')
    action_factors_success = fields.Text(string='Factors Success/Failure')
    action_financial_performance = fields.Text(string='Financial Performance')
    # Fields for SECTION H : Overall Assessment of Monitoring and Evaluation Site Visit.
    area_of_concern = fields.Text(string='Areas of Concerns')
    professional_opinion = fields.Text(string='Professional Opinion')
    next_payment_process = fields.Text(string='Next Payment Process')
    compiled_by = fields.Many2one('res.users', string='Compiled By:', default=lambda self: self.env.user)
#     signature = fields.Binary(string='Signature')
    compiled_date = fields.Date(string='Date', default=datetime.now().date())
    related_employee1 = fields.Many2one('hr.employee', string='Employee', default=lambda self: self.get_related_employee())
    
    provincial_manager_name = fields.Many2one('res.users', string='Name', default=lambda self: self.env.user,track_visibility='onchange')
    related_emplyee = fields.Many2one('hr.employee', string='Employee',track_visibility='onchange')
#     prov_man_sign = fields.Binary(string='Signature')
    prov_man_date = fields.Date(string='Date', default=datetime.now().date())
    related_employee2 = fields.Many2one('hr.employee', string='Employee2', default=lambda self: self.get_related_employee())
    approved_learn = fields.Integer(string='Approved',track_visibility='onchange')
    not_approved_learn = fields.Integer(string='Not Approved')
    project_man_sign = fields.Binary(string='Signature')
    project_man_date = fields.Date(string='Date', default=datetime.now().date())
    monitor_and_evaluate_ids = fields.One2many('tranche.generation','monitor_and_evaluate_id',string="Monitoring Transche",track_visibility='onchange')
    attach_transche = fields.Boolean("Attach Transche",default=False)
    attach_document = fields.Boolean("Document")
    monitor_and_evaluate_document_ids = fields.One2many('mae.document','monitor_and_evalaute_id',string="ME Document")
    funding_year = fields.Many2one('account.fiscalyear', string='Funding Year')
    project_type_id = fields.Many2one('hwseta.project.types',string="Project Type")
    project_id = fields.Many2one('project.project',string="Project")
    no_of_employed = fields.Integer("Employed 18.1 ",compute='_get_employed')
    no_of_unemployed = fields.Integer("Unemployed 18.2",compute='_get_unemployed')
    total_employed_unemployed = fields.Integer("Total",compute='_get_total_employed_unemloyed')
    submit = fields.Boolean("Submit",track_visibility='onchange')
    recommend = fields.Boolean("Recommend",track_visibility='onchange')
    approve = fields.Boolean("Approve",track_visibility='onchange')
    
    @api.multi
    def onchange_funding_year(self, funding_year) :
        res = {}
        if not funding_year :
            res.update({'domain':{'project_type_id':[('id','in',[])]}})
            return res
        project_types = [project_types.id for project_types in self.env['hwseta.project.types'].search([('seta_funding_year','=',funding_year)])]
        res.update({'domain':{'project_type_id':[('id','in',project_types)]}})
        return res
    
    @api.multi
    def onchange_project_type(self, project_type_id) :
        res = {}
        print "inside onchanges@@@@@@@@@"
        if not project_type_id :
            res.update({'domain':{'project_id':[('id','in',[])]}})
            return res
        project = [ project.id for project in self.env['project.project'].search([('project_types','=',project_type_id)])]
        print "project--", project
        res.update({'domain':{'project_id':[('id','in',project)]}})            
        return res
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('monitor.and.evaluate.ref')
        res = super(monitor_and_evaluate, self).create(vals)
        return res
    
    @api.model
    def write(self, vals):
        if not self._context.get('button',False):
            if self.submit == False and (vals.get('state',False) =='submitted' or vals.get('state',False) =='recommended' or vals.get('state',False) =='approved'):
                raise Warning(_('Sorry! First Submit the Monitering and Evaluation!!!! '))    
            if self.recommend == False and (vals.get('state',False) == 'recommended' or vals.get('state',False) =='approved'):
                raise Warning(_('Sorry! First Recommend the Monitering and Evaluation!!!! '))    
        return super(monitor_and_evaluate, self).write(vals)

    @api.multi
    def action_submit_mae(self):
        self = self.with_context(button=True)
        self.write({'submit':True,'state':'submitted'})
        return True
    
    @api.multi
    def action_recommend_mae(self):
        self = self.with_context(button=True)
        self.write({'recommend':True,'state':'recommended'})
        return True 

    @api.multi
    def action_approve_mae(self):
        self = self.with_context(button=True)
        self.write({'approve':True,'state':'approved'})
        return True 
            
    @api.multi
    def action_get_transche(self):
        if not (self.project_id) : 
            raise Warning(_('Please select project for Monitor and evaluate !'))        
        ## for generating tranche line associated with the project in MOnitoring and evaluation
#         for project_data in self.project_info_ids:   
#             if project_data : 
#                 project = project_data.project_id and project_data.project_id  
#                 tranche_ids = self.env['transche.payment'].search([('project_id','=',project.id),('trigger_jv','in',['monitor.and.evaluate'])])
#                 if self.monitor_and_evaluate_ids : 
#                     self.write({'monitor_and_evaluate_ids' : [(2,tranche.id) for tranche in self.monitor_and_evaluate_ids]})
#                 if tranche_ids:
#                     tranche_list = [(0,0,{'name' :tranche.name,'number':tranche.no_of_tranche,'monitor_and_evaluate_id' : self.id,'tranche_id':tranche.id}) for tranche in tranche_ids]
#                     self.write({'monitor_and_evaluate_ids':tranche_list})        
#                 if not (tranche_ids):
#                     raise Warning(_('Please configure transche for project %s !')%(project.name))
        if self.project_id : 
            project = self.project_id 
            tranche_ids = self.env['transche.payment'].search([('project_id','=',project.id),('trigger_jv','in',['monitor.and.evaluate']),('funding_year','=',project.seta_funding_year.id)])
            if self.monitor_and_evaluate_ids : 
                self.write({'monitor_and_evaluate_ids' : [(2,tranche.id) for tranche in self.monitor_and_evaluate_ids]})
            if tranche_ids:
                if self.project_id.category_type == '18.1':
                    tranche_list = [(0,0,{'name' :tranche.name,'number':tranche.no_of_tranche,'monitor_and_evaluate_id' : self.id,'tranche_id':tranche.id}) for tranche in tranche_ids]
                    self.write({'monitor_and_evaluate_ids':tranche_list})
                if self.project_id.category_type == '18.2':
                    tranche_list = [(0,0,{'name' :tranche.name,'number':tranche.no_of_tranche_18_2,'monitor_and_evaluate_id' : self.id,'tranche_id':tranche.id}) for tranche in tranche_ids]
                    self.write({'monitor_and_evaluate_ids':tranche_list})    
            if not (tranche_ids):
                raise Warning(_('Please configure transche for project %s !')%(project.name))
        self.write({'attach_transche':True})
        return True
    
    @api.multi
    def action_get_document(self):
        if not (self.project_id) : 
            raise Warning(_('Please select project for Monitor and evaluate !'))    
        ## Finding number of unique project types.
        document_ids =[]
#         for project_info in self.project_info_ids : 
#             tranche_ids = self.env['transche.payment'].search([('project_id','=',project_info.project_id.id),('trigger_jv','in',['monitor.and.evaluate'])])
#             for tranche_id in tranche_ids :
#                 document_ids = list(set([document.name.id for document in tranche_id.tranche_document_ids]))
        if self.project_id :
            project = self.project_id
            tranche_ids = self.env['transche.payment'].search([('project_id','=',project.id),('trigger_jv','in',['monitor.and.evaluate']),('funding_year','=',project.seta_funding_year.id)])
            for tranche_id in tranche_ids :
                document_ids = list(set([document.name.id for document in tranche_id.tranche_document_ids]))    
        ## Removing Document records if exists before.
        if self.monitor_and_evaluate_document_ids : 
            self.write({'monitor_and_evaluate_document_ids' : [(2,document_info.id) for document_info in self.monitor_and_evaluate_document_ids]})
        ## Generating Document records which is equal to no of unique project types.
        document_list = [(0,0,{'name' : document_info.id,'monitor_and_evaluate_id' : self.id}) for document_info in self.env['project.document'].browse(document_ids)]
        self.write({'monitor_and_evaluate_document_ids' : document_list})      
        self.write({'attach_document':True})
        return True    
    
    @api.multi
    def onchange_employer_id(self, employer_id):
        result = {}
        if not employer_id:
            return result
        employer_data = self.env['res.partner'].browse(employer_id)
        result.update({'value':{'sdl_number':employer_data.employer_sdl_no}})
        return result
    
    
monitor_and_evaluate()

class grant_project_info(models.Model):
    _name = 'grant.project.info'
    
    ## Functional field no_of_persons computations.
    @api.one
    @api.depends(
                'employed',
                'unemployed',
                )
    def _compute_total_persons(self):
        total = self.employed+self.unemployed
        self.total = total
    ##
    
    type_of_project = fields.Selection([
                                        ('learnership','Learnerships'),
                                        ('bursaries','Bursaries'),
                                        ('skills_programmes','Skills Programmes'),
                                        ('artisans','Artisans'),
                                        ('levy_exempt','Levy Exempt'),
                                        ], string='Project Type')
    type_of_projects = fields.Many2one('hwseta.project.types', string='Project Type')
    
    project_id = fields.Many2one('project.project', string='Discretionary Grant Name')
    mark_x = fields.Boolean(string='Mark X')
    funding_year = fields.Char(string='Funding Year')
    employed = fields.Integer(string='Employed 18.1')
    unemployed = fields.Integer(string='Unemployed 18.2')
    total = fields.Integer(string='Total', compute='_compute_total_persons')
    monitor_evaluate_id = fields.Many2one('monitor.and.evaluate', string='Monitor and Evaluate')
    
grant_project_info()