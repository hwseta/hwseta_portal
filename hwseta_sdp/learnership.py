from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import datetime
import base64
import calendar
import psycopg2
class project_fees(models.Model):
    _name = 'project.fees'
    
    name = fields.Char(string='Fees Name')
    project_emp_id = fields.Many2one('project.project', string='Related Project')
    project_unemp_id = fields.Many2one('project.project', string='Related Project')
    course_id = fields.Many2one('fees.structure', string='Fees Name')
    course_amount = fields.Float(string='Course Amount')
    
project_fees()

## Added for EOI Configuration ( Masters for  EOI Approval Criteria )
class eoi_approval_criteria(models.Model):
    _name = 'eoi.approval.criteria'
    _rec_name = 'project_id'
    
    project_type = fields.Many2one('hwseta.project.types', string='Project Type', track_visibility='onchange')
    project_id = fields.Many2one('project.project', string='Project')
    allocation_ids = fields.One2many('allocation.data', 'eoi_approval_id', string='Allocation')
    funding_year = fields.Many2one('account.fiscalyear', string='Funding Year')
    category = fields.Many2one('hwseta.project.category', string='Project Category')
    category_type = fields.Selection([('18.1','Employed Learners (18.1)'),('18.2','Unemployed Learners (18.2)')], string="Category Type")

    @api.multi
    def onchange_funding_year(self, funding_year):
        res = {}
        if not funding_year :
            res.update({'domain':{'project_type':[('id','in',[])]}})
            return res
        project_types = [project_types.id for project_types in self.env['hwseta.project.types'].search([('seta_funding_year','=',funding_year)])]
        res.update({'domain':{'project_type':[('id','in',project_types)]}})
        return res

    @api.multi
    def onchange_project_type(self, project_type) :
        res = {}
        if not project_type:
            res.update({'domain':{'project_id':[('id','in',[])]}})
            return res
        project = [project.id for project in self.env['project.project'].search([('project_types','=',project_type)])]
        res.update({'domain':{'project_id':[('id','in',project)]}})
        return res

    @api.onchange('project_id')
    def onchange_project(self):
        if self.project_id:
            project = self.env['project.project'].browse(self.project_id.id)
            if project.category_type == '18.1':
                self.category_type = '18.1'
            else:
                self.category_type = '18.2'
            if project.category:
                self.category = project.category.id
    
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
    
    @api.model
    def create(self, vals):
        res = super(eoi_approval_criteria, self).create(vals)
        eoi_criteria = [eoi.id for eoi in self.env['eoi.approval.criteria'].search([('project_id','=',res.project_id.id),('funding_year','=',res.funding_year.id)])]
        if len(eoi_criteria) > 1:
            raise Warning(_('You can not create multiple EOI criteria for the Financial year %s !')%(res.funding_year.name))
        for line in res.allocation_ids:
            if res.category_type == '18.1' and line.learner_status == 'unemployed':
                raise Warning('You can not add unemployed learner status!')
            if res.category_type == '18.2' and line.learner_status == 'employed':
                raise Warning('You can not add employed learner status')
        return res
    
    @api.multi
    def write(self, vals):
        res = super(eoi_approval_criteria, self).write(vals)
        eoi_criteria = [eoi.id for eoi in self.env['eoi.approval.criteria'].search([('project_id','=',self.project_id.id),('funding_year','=',self.funding_year.id)])]
        if len(eoi_criteria) > 1:
            raise Warning(_('You can not create multiple EOI criteria for the Financial year %s !')%(self.funding_year.name))
        for line in self.allocation_ids:
            if self.category_type == '18.1' and line.learner_status == 'unemployed':
                raise Warning('You can not add unemployed learner status!')
            if self.category_type == '18.2' and line.learner_status == 'employed':
                raise Warning('You can not add employed learner status')
        return res
    
eoi_approval_criteria()

class employer_type(models.Model):
    _inherit = 'employer.type'
    
    allocation_id = fields.Many2one('allocation.data', string='Related Allocations')
    
employer_type()

class allocation_data(models.Model):
    _name = 'allocation.data'
    
    learner_status = fields.Selection([('employed','Employed'),('unemployed','Un-employed')], string='Learner Status')
    emp_type_id = fields.Many2many('employer.type', 'allocation_id', 'emp_type_id', string='Type Of Employer')  
    min_learner = fields.Integer(string='Min no. Learner')
    max_learner = fields.Integer(string='Max no. Learner')
    percentage_allocate = fields.Integer(string='Percentage(%)')
    eoi_approval_id = fields.Many2one('eoi.approval.criteria', string='Related EOI Approval')

    @api.depends('eoi_approval_id')
    @api.onchange('learner_status')
    def onchange_learner_status(self):
        '''This method is used to restrict learner status on the basis category type'''
        if self.eoi_approval_id.category_type == '18.2' and self.learner_status == 'employed':
            return {'warning': {'title': 'Invalid Learner Status', 'message': 'Sorry! You can not add employed learner status'}}
        if self.eoi_approval_id.category_type == '18.1' and self.learner_status == 'unemployed':
            return {'warning': {'title': 'Invalid Learner Status', 'message': 'Sorry! You can not add unemployed learner status'}}

allocation_data()
###

class project_project(models.Model):
    _inherit = 'project.project'
    
    project_types = fields.Many2one('hwseta.project.types', string="Project Type")

#     fees_employed = fields.Many2many('fees.structure', 'project_empfees_rel', 'project_id', 'fees_id', string='Fees 18.1')
#     fees_unemployed = fields.Many2many('fees.structure','project_unempfees_rel', 'project_id', 'fees_id', string='Fees 18.2')
    ## Added to have a facility
    fees_employed = fields.One2many('project.fees', 'project_emp_id', string='Fees 18.1')
    fees_unemployed = fields.One2many('project.fees', 'project_unemp_id', string='Fees 18.2')
    employer_request_ids = fields.One2many('employer.requests', 'project_id', string='Employer Requests Employed/Unemployed')
    fees_defined = fields.Boolean("Fees define",default=False)
    update_toeoi = fields.Boolean("Update to EOI",default=False)
    eoi_id = fields.Many2one('eoi_id.configuration', string="EOI ID")
    eoi_id_reference_invisible = fields.Char(related='eoi_id.eoi_id', string="EOI ID", store=True, readonly=True)
    state = fields.Selection([('template', 'Template'),
                                   ('draft','New'),
                                   ('open','In Progress'),
                                   ('publish','Publish'),
                                   ('cancelled', 'Cancelled'),
                                   ('pending','Pending'),
                                   ('close','Closed')],
                                  'Status', required=True, copy=False)
    @api.one
    def set_publish(self):
        return self.write({'state': 'publish'})
    
    @api.multi
    def onchange_funding_year(self, funding_year) :
        res = {}
        if not funding_year :
            res.update({'domain':{'project_types':[('id','in',[])]}})
            return res
        project_types = [project_types.id for project_types in self.env['hwseta.project.types'].search([('seta_funding_year','=',funding_year)])]
        res.update({'domain':{'project_types':[('id','in',project_types)]}})
        return res   
        
    @api.multi
    def onchange_project_type(self, project_type_id) :
        res = {}
        if not project_type_id :
            res.update({'domain':{'project_id':[('id','in',[])]}})
            return res
        project_type_data = self.env['hwseta.project.types'].browse(project_type_id)
        project_type_budget = project_type_data.applied_budget or 0
        ## Calculating already allocated budgets
        if project_type_budget :
            allocated_budget = 0
            for project_data in self.search([('project_types','=',project_type_id)]) :
                allocated_budget += project_data.budget_applied 
            available_budget = project_type_budget - allocated_budget
            if available_budget <= 0 :
                available_budget = 0
#             project_type_data.write({'rem_budget' : available_budget})
#             res.update({'value':{'budget' : available_budget}}) ## which will based on project from now
        else :
            pass
#             res.update({'value':{'budget' : project_type_budget}})  ## which will based on project from now
        project = [project.id for project in self.env['hwseta.project.types'].search([('id','=',project_type_id)]).project_ids]
        res.update({'domain':{'project_id':[('id','in',project)]}})            
        return res
    
    @api.multi
    def onchange_project(self, project_id) :
        res = {}
        if not project_id :
            return res
        project = self.env['hwseta.project'].browse(project_id)
        if project.target_employed != 0 and project.target_unemployed == 0:
            res.update({'value':{'name':project.name.name,'target_employed_learner':project.target_employed,'target_unemployed_learner':project.target_unemployed,'budget':project.budget_applied,'category_type':'18.1'}})
        else:
            res.update({'value':{'name':project.name.name,'target_employed_learner':project.target_employed,'target_unemployed_learner':project.target_unemployed,'budget':project.budget_applied,'category_type':'18.2'}})
        return res
    
    @api.multi
    def action_fees_structure(self):
        project_type_data = self.project_types
        fees_employed = [fees_data.id for fees_data in project_type_data.fees_employed]
        fees_unemployed = [fees_data.id for fees_data in project_type_data.fees_unemployed]
        if self.fees_employed :
            self.with_context({'from_get_fees':True}).write({'fees_employed' : [(2,fees_data.id) for fees_data in self.fees_employed]})
        if self.fees_unemployed :
            self.with_context({'from_get_fees':True}).write({'fees_unemployed' : [(2,fees_data.id) for fees_data in self.fees_unemployed]})
        ## condition changes in AND to OR    
        if fees_employed or fees_unemployed :
            self.with_context({'from_get_fees':True}).write({'fees_employed' : [(0,0,{'course_id' : fees_id, 'project_emp_id':self.id}) for fees_id in fees_employed], 'fees_unemployed' : [(0,0,{'course_id' : fees_id, 'project_unemp_id':self.id}) for fees_id in fees_unemployed]})
        # self.with_context({'from_get_fees':True}).write({'fees_unemployed' : [(0,0,{'course_id' : fees_id, 'project_unemp_id':self.id}) for fees_id in fees_unemployed]})                     
        else :
            raise Warning(_('Fees structure not defined for %s')%(project_type_data.name))   
        self = self.with_context(button=True)
        self.write({'fees_defined':True})          
        return True
    
    @api.model
    def create(self, vals):
        res = super(project_project, self).create(vals)
        project_type_data = res.project_types
        ## Handlings
        if res.budget == 0 and res.budget_applied :
            raise Warning(_('You dont have more budget to allocate for %s!')%(project_type_data.name.name))
        if res.budget_applied > res.budget :
            raise Warning(_('You can not apply more budget than exists!'))
        ## Calculating total budget applied within pr66ojects.
        project_type_budget = project_type_data.applied_budget or 0
        if project_type_budget and vals.get('budget_applied',False):
            allocated_budget = 0
            for project_data in self.search([]) :
                allocated_budget += project_data.budget_applied
            available_budget = project_type_budget - allocated_budget
            if available_budget <= 0 :
                available_budget = 0
            project_type_data.write({'rem_budget' : available_budget})
        #DATE VALIDATIONS
        if res.start_date and res.end_date:
            if res.start_date > res.end_date:
                raise Warning(_("Sorry! Project End Date should be greater than Project Start Date "))
            if res.eoi_start_date and res.eoi_end_date:
                if res.eoi_start_date < res.start_date or res.eoi_start_date > res.end_date:
                    raise Warning(_("Sorry! EOI Start Date should be between the range of Project Start Date and Project End Date"))
                if res.eoi_end_date < res.start_date or res.eoi_end_date > res.end_date:
                    raise Warning(_("Sorry! EOI End Date should be between the range of Project Start Date and Project End Date"))
                if res.eoi_start_date > res.eoi_end_date:
                    raise Warning(_("Sorry! EOI End Date should be greater than EOI Start Date "))
                if res.load_learner_start_date and res.load_learner_end_date:
                    if res.load_learner_start_date < res.eoi_start_date or res.load_learner_start_date < res.eoi_end_date:
                        raise Warning(_("Sorry! Load Learner Start Date should be greater than EOI dates"))
#                     if res.load_learner_end_date < res.eoi_start_date or res.load_learner_end_date < res.eoi_end_date:
#                         raise Warning(_("Sorry! Load Learner End Date should be between the range of EOI Start Date and EOI End Date"))
                    if res.load_learner_start_date > res.load_learner_end_date:
                        raise Warning(_("Sorry! Load Learner End Date should be greater than Load Learner Start Date "))
#         if vals.get('fees_defined') == False:
#             raise Warning(_("Please define the Fees structure for the projects"))
        return res
    
    @api.multi
    def write(self, vals):
        res = super(project_project, self).write(vals)
        project_type_data = self.project_types
        ## Handlings
        if self.budget == 0 and vals.get('budget_applied',False) :
            raise Warning(_('You dont have more budget to allocate for %s!')%(project_type_data.name))
        if self.budget_applied > self.budget or vals.get('budget_applied', False) > self.budget :
            raise Warning(_('You can not apply more budget than exists!'))
        total_fees_employed = 0
        fees_employed = 0 
        if self.fees_employed:
            for course in self.fees_employed:
                fees_employed += course.course_amount
            total_fees_employed = fees_employed * self.target_employed_learner
        total_fees_unemployed = 0
        fees_unemployed = 0
        if self.fees_unemployed:
            for course in self.fees_unemployed:
                fees_unemployed += course.course_amount
            total_fees_unemployed = fees_unemployed * self.target_unemployed_learner
        total_fees = total_fees_employed + total_fees_unemployed 
        if self.budget_applied < total_fees : 
            raise Warning(_('Your fees according to targeted learner is more than Budget Applied!'))
        ## Calculating total budget applied within projects.
        project_type_budget = project_type_data.applied_budget or 0
        if project_type_budget and vals.get('budget_applied',False):
            allocated_budget = 0
            for project_data in self.search([]) :
                allocated_budget += project_data.budget_applied
            available_budget = project_type_budget - allocated_budget
            if available_budget <= 0 :
                available_budget = 0
            project_type_data.write({'rem_budget' : available_budget})
        
        
        #DATE VALIDATIONS
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise Warning(_("Sorry! Project End Date should be greater than Project Start Date "))
            if self.eoi_start_date and self.eoi_end_date:
                if self.eoi_start_date < self.start_date or self.eoi_start_date > self.end_date:
                    raise Warning(_("Sorry! EOI Start Date should be between the range of Project Start Date and Project End Date"))
                if self.eoi_end_date < self.start_date or self.eoi_end_date > self.end_date:
                    raise Warning(_("Sorry! EOI End Date should be between the range of Project Start Date and Project End Date"))
                if self.eoi_start_date > self.eoi_end_date:
                    raise Warning(_("Sorry! EOI End Date should be greater than EOI Start Date "))
                if self.load_learner_start_date and self.load_learner_end_date:
                    if self.load_learner_start_date < self.eoi_start_date or self.load_learner_start_date < self.eoi_end_date:
                        raise Warning(_("Sorry! Load Learner Start Date should be greater than EOI dates"))
#                     if self.load_learner_end_date < self.eoi_start_date or self.load_learner_end_date < self.eoi_end_date:
#                         raise Warning(_("Sorry! Load Learner End Date should be between the range of EOI Start Date and EOI End Date"))
                    if self.load_learner_start_date > self.load_learner_end_date:
                        raise Warning(_("Sorry! Load Learner End Date should be greater than Load Learner Start Date "))
        if not self._context.get('button',False):
            if (vals.get('fees_defined',False) == True and self.fees_defined == False):
                raise Warning(_("Please define the Fees structure for the projects"))                    
        return res
    
    @api.multi
    def update_to_eoi(self):
        for employer_approval in self.employer_request_ids:
            enrollment_projects = employer_approval.enroll_project_id 
            enrollment_projects.write({
                                       'employed' : employer_approval.app_employed,
                                       'non_employed' : employer_approval.app_unemployed,
                                       'state' : 'approved'
                                       })
        return True
    
    @api.multi
    def get_calculated_emp(self, req_learners, min_range, max_range, percentage_allocated):
        ''' Calculates the number of learners to be approved.'''
        no_of_learners = float(percentage_allocated)/100 * req_learners
        no_after_decimal = str(no_of_learners - int(no_of_learners))[2:]
        length_of_number = len(str(no_after_decimal))
        if length_of_number > 1:
            no_after_decimal = int(str(no_after_decimal)[0])
        if no_after_decimal and int(no_after_decimal) >= 5 :
            no_of_learners = int(no_of_learners) + 1
        else : 
            no_of_learners = int(no_of_learners)
        return no_of_learners
    
    @api.multi
    def compute_allocation(self):
        ''' Computes no of employed and no of unemployed learners to be allocated according to EOI Approval 
        Criteria Configurations project wise'''
        
        eoi_approval_data = self.env['eoi.approval.criteria'].search([('project_id','=',self.id),('funding_year','=',self.seta_funding_year.id)], limit=1)
        if not eoi_approval_data :
            raise Warning(_('Please define EOI Approval Criteria for project %s !')%(self.name))
        total_request_employed = 0
        total_request_unemployed = 0
        for employe_data in self.employer_request_ids:
            total_request_employed = total_request_employed + int(employe_data.req_employed)
            total_request_unemployed = total_request_unemployed + int(employe_data.req_unemployed)
        for employe_data in self.employer_request_ids:
            ratio_request_employed = 0
            ratio_request_unemployed = 0
            if total_request_employed > self.target_employed_learner:
                ratio_request_employed = (((employe_data.req_employed*100)/total_request_employed)*(self.target_employed_learner))/100
                
                employe_data.write({'ratio_req_employed':ratio_request_employed})
            else:
                employe_data.write({'ratio_req_employed':employe_data.req_employed})
            if total_request_unemployed > self.target_unemployed_learner:
                ratio_request_unemployed = (((employe_data.req_unemployed*100)/total_request_unemployed)*(self.target_unemployed_learner))/100
                employe_data.write({'ratio_req_unemployed':ratio_request_unemployed})
            else:
                employe_data.write({'ratio_req_unemployed':employe_data.req_unemployed})

        for emp_req_data in self.employer_request_ids:
            no_emp_learner = 0  
            no_unemp_learner = 0           
            ## Getting Type of an Employer.
            emp_type_name = emp_req_data.employer_id.type_of_employer.name
            req_emp = emp_req_data.ratio_req_employed
            req_unemp = emp_req_data.ratio_req_unemployed
            for allocation_data in eoi_approval_data.allocation_ids :
                if allocation_data.emp_type_id:
                    ## Getting all employer types defined in EOI Approval Criteria.
                    emp_types = [emp_type.name for emp_type in allocation_data.emp_type_id]
                    if allocation_data.learner_status == 'employed' and emp_type_name in emp_types:
                        if req_emp >= allocation_data.min_learner and req_emp <= allocation_data.max_learner :
                            no_emp_learner = self.get_calculated_emp(req_emp, allocation_data.min_learner, allocation_data.max_learner, allocation_data.percentage_allocate)
                    if allocation_data.learner_status == 'unemployed' and emp_type_name in emp_types: 
                        if req_unemp >= allocation_data.min_learner and req_unemp <= allocation_data.max_learner :
                            no_unemp_learner = self.get_calculated_emp(req_unemp, allocation_data.min_learner, allocation_data.max_learner, allocation_data.percentage_allocate)
                    else:
                        if allocation_data.learner_status == 'employed' :
                            if req_emp >= allocation_data.min_learner and req_emp <= allocation_data.max_learner :
                                no_emp_learner = self.get_calculated_emp(req_emp, allocation_data.min_learner, allocation_data.max_learner, allocation_data.percentage_allocate)
                        if allocation_data.learner_status == 'unemployed' :
                            if req_unemp >= allocation_data.min_learner and req_unemp <= allocation_data.max_learner :
                                no_unemp_learner = self.get_calculated_emp(req_unemp, allocation_data.min_learner, allocation_data.max_learner, allocation_data.percentage_allocate)
                emp_req_data.write({ 'app_employed' : no_emp_learner, 'app_unemployed' : no_unemp_learner })
                self.write({'update_toeoi':True})
        return True
        
project_project()

class employer_requests(models.Model):
    _name = 'employer.requests'
    
    @api.one
    @api.depends(
                 'app_employed',
                 'app_unemployed',
                 'project_id'
                 )
    def _get_total_cost(self):
        total = 0
        if (self.app_employed or self.app_unemployed) and self.project_id :
            project_data = self.env['project.project'].browse(self.project_id.id)
            total_employed = 0
            total_unemployed = 0
            for fees_employed in project_data.fees_employed :
                total_employed += fees_employed.course_amount
            total_employed *=  self.app_employed
            for fees_unemployed in project_data.fees_unemployed :
                total_unemployed += fees_unemployed.course_amount
            total_unemployed *= self.app_unemployed
            total = total_employed + total_unemployed
        self.cost_required = total
        
#     @api.one
#     @api.depends(
#                  'req_employed',
#                  'req_unemployed',
#                  'project_id'
#                  )
#     def _get_ratio_target_employed(self):
#         total = 0
#         if (self.req_employed or self.req_unemployed) and self.project_id :
#             
#             project_data = self.env['project.project'].browse(self.project_id.id)
#             total_employed = 0
#             total_unemployed = 0
#             for fees_employed in project_data.fees_employed :
#                 total_employed += fees_employed.course_amount
#             total_employed *=  self.app_employed
#             for fees_unemployed in project_data.fees_unemployed :
#                 total_unemployed += fees_unemployed.course_amount
#             total_unemployed *= self.app_unemployed
#             total = total_employed + total_unemployed
#         self.cost_required = total    
    
    employer_id = fields.Many2one('res.partner', string='Employer', domain=[('employer','=',True)])
    req_employed = fields.Integer(string='Requested Employed')
    req_unemployed = fields.Integer(string='Requested Unemployed')
    ratio_req_employed = fields.Integer(string='Ratio Requested Employed')
    ratio_req_unemployed = fields.Integer(string='Ratio Requested Unemployed')    
    app_employed = fields.Integer(string='Approved Employed')
    app_unemployed = fields.Integer(string='Approved Unemployed')
    cost_required = fields.Float(string='Cost Reqd', compute='_get_total_cost')
    enroll_project_id = fields.Many2one('enrollment.projects', string='Project Enrollment in EOI')
    project_id = fields.Many2one('project.project', string='Project')
    eoi_id = fields.Many2one('learning.programme', string='Related EOI')
    
employer_requests

class enrollment_projects(models.Model):
    _name = 'enrollment.projects'
    
#     @api.one
#     @api.depends(
#                 'req_employed'
#                 )
#     def _set_employed(self):
#         '''requested employed for learners. '''
#         self.employed = self.req_employed
        
#     @api.one
#     @api.depends(
#                 'req_unemployed'
#                 )
#     def _set_unemployed(self):
#         '''requested unemployed for learners. '''
#         self.non_employed = self.req_unemployed  
            
    ## Functional field no_of_persons computations.
    @api.one
    @api.depends(
                'employed',
                'non_employed',
                )
    def _compute_total_persons(self):
        '''Total of employed and non-employed learners. '''
        total = self.employed + self.non_employed
        self.no_of_persons = total
    
    @api.multi
    def _get_employer(self):
        ''' Getting employer from enroll project via context passed in xml.'''
        context = self._context
        employer_id = context.get('employer',0)
        return employer_id
    
    @api.onchange('provider_id')
    def onchange_provider_id(self):
        ''' Getting only those provider belongs to project for which the EOI is created.'''
        res = {}
        context =self._context.copy()
        if context and context.get('employer_id') and context.get('project_id'):
            providers = self.env['partner.project.rel'].search[('employer_id','=',context.get('employer_id')),('pro_project_id','=',context.get('project_id'))]
#         res.update({'domain':{'provider_id':[('id','in',[])]}})
        return res 
        
    employer_id = fields.Many2one('res.partner', string='Employer', domain=[('employer','=',True)], default=_get_employer)
    project_types = fields.Many2one('hwseta.project.types', string="Project")
    project_id = fields.Many2one('project.project', string='Project')
    black = fields.Integer(string="Black")
    coloured = fields.Integer(string="Coloured")
    indian = fields.Integer(string="Indian") 
    req_employed = fields.Integer(string="No of Employed (18.1)")
    req_unemployed = fields.Integer(string="No of Unemployed (18.2)")
#     employed = fields.Integer(string="Employed", compute='_set_employed',store=True)
#     non_employed = fields.Integer(string="Non Employed", compute='_set_unemployed',store=True)
    employed = fields.Integer(string="Employed")
    non_employed = fields.Integer(string="Non Employed")
    no_of_persons = fields.Integer(string='Total Number of Learners Approved', compute='_compute_total_persons')
    persons_approved = fields.Integer(string='Persons Granted')
    learnership_id = fields.Many2one('learning.programme', string='Learnership')
#     state = fields.Selection([('draft','Draft'),
#                               ('submit','Submit'),
#                               ('approve','Approved'),
#                               ('moa_sent','MOA Sent'),
#                               ('accept_moa','Accept MOA'),
#                               ('final_approve','Final Approval'),
#                               ], string="State", default='draft')
    status = fields.Selection([('pending','Pending'),
                              ('evaluation','Evaluation'),
                              ('approved','Approved'),
                              ('final_approval','Final Approval'),
                              ], string="State", default='pending')
    provider_id = fields.Many2one('res.partner', string="HWSETA Training Provider",track_visibility='onchange', domain=[('provider','=',True)])
    provider = fields.Char("Other Provider")
    provider_campus_id = fields.Many2one('res.partner', string='Training Provider Campus')
    state = fields.Selection([('draft','Draft'),('pending_approval','Pending Approval'),('approved','Approved')], string='Status', default='draft')
#     no_of_learners = fields.Integer(string='No of Posssible Learners', compute='_get_total_learner')
    qualifications = fields.Many2many('provider.qualification', 'learning_programme_qualification_rel', 'learning_programme_id', 'qualification_id', string='Qualifications')
    
    @api.multi
    @api.onchange('req_employed')
    def onchange_req_employed(self):
        if self.req_employed > 0:
            self.req_unemployed = 0

    @api.multi
    @api.onchange('req_unemployed')
    def onchange_req_unemployed(self):
        if self.req_unemployed > 0:
            self.req_employed = 0
            
    @api.multi
    def onchange_employer(self, employer_id, project_type):
        '''Applying domain on project. Will show only projects in which selected employer 
        is participated and selected project type matches.'''
        res = {}
        if not (employer_id and project_type):
            return res
        if employer_id and project_type:
            project_ids = []
            for partner_project in self.env['partner.project.rel'].search([('employer_id','=',employer_id),('eoi_apply','=',True)]) :
                if partner_project.emp_project_id and partner_project.select_emp == True:
                    project_ids.append(partner_project.emp_project_id.id)
#             self._cr.execute('select emp_project_id from empl_proj_rel where res_partner_id=%s'%(employer_id))
#             project_ids = map(lambda x: x[0], self._cr.fetchall())
            res.update({'domain':{'project_id':[('id','in',project_ids),('project_types','=',project_type)]}})
        return res
    
    @api.multi
    def onchange_project_id(self, project):
        '''Applying domain on provider. 
        Will show only providers who participated in the selected project.'''
        res = {}
        if not project :
            return res
        provider_ids = []
        for partner_project in self.env['partner.project.rel'].search([('pro_project_id','=',project)]):
            if partner_project.provider_id and partner_project.select_pro == True :
                provider_ids.append(partner_project.provider_id.id)
#         self._cr.execute('select res_partner_id from pro_proj_rel where pro_project_id=%s'%(project))
#         provider_ids = map(lambda x: x[0], self._cr.fetchall())
        res.update({'domain':{'provider_id':[('id','in',provider_ids)]}})
        return res
    
enrollment_projects()


class sdp_learner_attachment(models.Model):
    """
    Form for Attachment details
    """
    _name = "sdp.learner.attachment"
    
    name = fields.Char('Document Name',required=True)
    data = fields.Binary('File', required=True )
    learner_attach_id =  fields.Many2one('sdp.learner', 'Document Upload', ondelete='cascade')
    
sdp_learner_attachment()

class project_enrolled(models.Model):
    _name = 'project.enrolled'
    
    project_id = fields.Many2one('project.project', string="Project")
    project_type = fields.Many2one('hwseta.project.types', string="Project Types")
    provider_id = fields.Many2one('res.partner', string="Provider", domain=[('provider','=',True)])
    sdp_learner_id = fields.Many2one('sdp.learner',string="SDP Learner")
    
project_enrolled()

class sdp_learner(models.Model):
    _name = 'sdp.learner'
    _description = 'Sdp Learner'
    
    select_learner_info = fields.Boolean(string='Please select to include this learner while loading learners')
    seq_no = fields.Char(string='Agreement No')
    learner_id = fields.Many2one('learning.programme', 'Learning Programme', ondelete='cascade', select=True)
    learner_attachment_ids = fields.One2many('sdp.learner.attachment', 'learner_attach_id', 'Document Upload')

    surname = fields.Char(string='Surname')
    # add middle name   
    middle_name = fields.Char(string='Middle Name')
    work_email = fields.Char(string='Email', track_visibility='onchange')
    work_phone = fields.Char(string='Phone', track_visibility='onchange', size=10)
    financial_year = fields.Datetime(string='Enrollment Year',track_visibility='onchange')
    initials = fields.Char(string='Initials', track_visibility='onchange', size=50)
    passport_id = fields.Char(string='Passport No', track_visibility='onchange')
    id_document = fields.Many2one('ir.attachment', string='ID Document', help='Upload Document')
    equity = fields.Selection([('black_african', 'Black: African'), ('black_indian', 'Black: Indian / Asian'), ('black_coloured', 'Black: Coloured'), ('other', 'Other'), ('unknown', 'Unknown'), ('white', 'White')], string='Equity')
    marital = fields.Selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('widow', 'Widow'), ('divorced', 'Divorced')], 'Marital Status', track_visibility='onchange')
    identity_number = fields.Char(string='Identity Number')
    socio_economic_saqa_code = fields.Selection([('1', '01'), ('2', '02'), ('3', '03'), ('4', '04'), ('6', '06'), ('7', '07'), ('8', '08'), ('9', '09'), ('10', '10'), ('97', '97'), ('98', '98'), ('U', 'U')], string='Socio Economic Status SAQA Code')
    disability_status = fields.Selection([
                                            ('sight', 'Sight ( even with glasses )'),
                                            ('hearing', 'Hearing ( even with h.aid )'),
                                            ('communication', 'Communication ( talk/listen)'),
                                            ('physical', 'Physical ( move/stand, etc)'),
                                            ('intellectual', 'Intellectual ( learn,etc)'),
                                            ('emotional', 'Emotional ( behav/psych)'),
                                            ('multiple', 'Multiple'),
                                            ('disabled', 'Disabled but unspecified'),
                                            ('none', 'None'), ], string='Disability Status')
    alternate_identity_no = fields.Char(string='Alternate identity No')
    certificate_no = fields.Char(string='Certificate No')
    
    title = fields.Char(string='Title')
    person_title = fields.Selection([('adv', 'Adv.'), ('dr', 'Dr.'),('mr', 'Mr.'),('mrs', 'Mrs.'), ('ms', 'Ms.'), ('prof', 'Prof.')], string='Title', track_visibility='onchange')
    name = fields.Char(string='Name')
    detials_surname = fields.Char(string='Surname')
    maiden_name = fields.Char(string='Maiden Name')
    rsa_identity_no = fields.Char(string='RSA Identity No',size=13)
    citizen_residential_status = fields.Selection([('dual','D - Dual (SA plus other)'),('other','O - Other'),('sa','SA - South Africa'),('unknown','U - Unknown')],string='Citizen Status')
    learner_reg_no = fields.Char(string='Learner Reg No')
    gender = fields.Selection([('male', 'Male'),('female', 'Female')],'Gender')
    equity = fields.Char(string='Equity')
    dissability = fields.Selection([('yes','Yes'),('no','No')], string='Dissability')
    home_language = fields.Many2one('res.lang', string='Home Language Code',track_visibility='onchange', size=6)
    highest_education = fields.Selection([('abet_level_1','Abet Level 1'),('abet_level_2','Abet Level 2'),('abet_level_3','Abet Level 3'),('abet_level_4','Abet Level 4'),('nqf123','NQF 1,2,3'),('nqf45','NQF 4,5'),('nqf67','NQF 6,7'),('nqf8910','NQF 8,9,10')],string='Highest Education')
    business_tel_no = fields.Char(string='Business Tel No')
    fax_no = fields.Char(string='Fax No')
    email = fields.Char(string='Email')
    
    cell = fields.Char(string='Mobile Number')
    method_of_communication = fields.Selection([('cell_phone','Cell Phone'),('email','Email')],string='Method of Communication')
    date_of_birth = fields.Date(string='Date of Birth')
    nationality_id = fields.Many2one('res.country', string='Nationality')
    learner_status = fields.Selection([('achieved', 'Achieved')],'Learner Status')
    status_effective_date = fields.Date(string='Status Effective Date')
    status_reason = fields.Selection([('workplace_learning', '500 - Workplace learning')],'Learner Status Reason')
    sponsorship = fields.Selection([('funded', 'Funded'),('nonfunded', 'Non-Funded')],'Sponsorship')
    wsp_year = fields.Selection([('2015', '2015'),('2016', '2016')],'WSP Year')
    status_comments = fields.Text('Status Comments')
    record_last_updated = fields.Datetime('Record Last Updated')
    last_updated_operator = fields.Char(string='Last Updated Operator')
    attached_report = fields.Binary(string="Agreement")
    project_id = fields.Many2one('project.project', string='Projects')
    proj_enrolled_ids = fields.One2many('project.enrolled','sdp_learner_id', string="Projects for EOI")
    created = fields.Boolean(string='Created', default=True)
    ## Learner Address ##
    learner_home_address_1 = fields.Char(string='Home Address 1',track_visibility='onchange', size=50)
    learner_home_address_2 = fields.Char(string='Home Address 2',track_visibility='onchange', size=50)
    learner_home_address_3 = fields.Char(string='Home Address 3',track_visibility='onchange', size=50)
    learner_postal_address_1 = fields.Char(string='Postal Address 1',track_visibility='onchange', size=50)
    learner_postal_address_2 = fields.Char(string='Postal Address 2',track_visibility='onchange', size=50)
    learner_postal_address_3 = fields.Char(string='Postal Address 3',track_visibility='onchange', size=50)
    learner_home_suburb = fields.Many2one('res.suburb',string='Home Suburb')
    learner_home_municipality = fields.Many2one('res.municipality', string='Municipality')
    learner_postal_suburb = fields.Many2one('res.suburb',string='Postal Suburb')
    learner_postal_municipality = fields.Many2one('res.municipality', string='Municipality')
    learner_home_city = fields.Many2one('res.city', string='Home City',track_visibility='onchange')
    learner_postal_city = fields.Many2one('res.city', string='Postal City',track_visibility='onchange')
    learner_home_zip = fields.Char(string='Home Zip',track_visibility='onchange')
    learner_postal_zip = fields.Char(string='Postal Zip',track_visibility='onchange')
    learner_country_home = fields.Many2one('res.country', string='Home Country', track_visibility='onchange')
    learner_country_postal = fields.Many2one('res.country', string='Postal Country', track_visibility='onchange')
    learner_home_province_code = fields.Many2one('res.country.state', string='Home Province Code', track_visibility='onchange')
    learner_postal_province_code = fields.Many2one('res.country.state', string='Postal Province Code',track_visibility='onchange')
    same_as_home = fields.Boolean(string='Same As Home Address')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    african = fields.Boolean(string='African')
    loaded = fields.Boolean(string='Loaded')
    req_for_approve = fields.Boolean("Request for Approval",default= False)
    # Rating
    
    seeing_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')], string='Seeing Rating Id', track_visibility='onchange')
    hearing_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')], string='Hearing Rating Id', track_visibility='onchange')
    walking_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')], string='Walking Rating Id', track_visibility='onchange')
    remembering_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')], string='Remembering Rating Id', track_visibility='onchange')
    statssa_area_code = fields.Integer(string='STATSSA Area Code', track_visibility='onchange', size=20)
    popi_act_status_date = fields.Date(string='POPI Act Status Date', track_visibility='onchange')
    communicating_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')], string='Communicating Rating Id', track_visibility='onchange')
    self_care_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')], string='Self Care Rating Id', track_visibility='onchange')
    last_school_emis_no = fields.Char(string='Last School EMIS No', track_visibility='onchange', size=20)
    last_school_year = fields.Integer(string='Last School Year', track_visibility='onchange', size=4)
    popi_act_status_id = fields.Integer(string='POPI Act Status Id', track_visibility='onchange', size=2)
    date_stamp = fields.Date(string='Date Stamp', track_visibility='onchange')
    
    
    state = fields.Selection([
            ('pending','Pending'),
            ('active', 'Active'),
            ('dropout', 'Drop Out'),                  
            ('replacement', 'Replacement'),
            ('suspended', ' Suspended'),
            ('inactive', 'In Active'),
        ], string='Status', index=True, readonly=True, default='pending',
        track_visibility='onchange', copy=False)
    
    '''current status field is used to track current status on learner_id one2many field'''
    current_status = fields.Selection([('req_active', 'Request For Active'),
                               ('req_in_active','Request For In Active'),
                               ('req_drop_out', 'Request For Drop Out'),
                               ('req_replacement', 'Request For Replacement'),
                               ('req_suspend','Request For Suspended'),
                               ('wait_active', 'Waiting For Active'),
                               ('wait_in_active','Waiting For In Active'),
                               ('wait_drop_out', 'Waiting For Drop Out'),
                               ('wait_replacement', 'Waiting For Replacement'),
                               ('wait_suspend','Waiting For Suspended'),
                               ('pending','Pending'),
                               ('active', 'Active'),
                               ('in_active','In Active'),
                               ('drop_out', 'Drop Out'),
                               ('replacement', 'Replacement'),
                               ('suspend','Suspended'),],
                              string='Current Status', default='req_active')
    employee_type = fields.Selection([('employed','Employed'),('unemployed','Unemployed')])
    
    '''This method is used to do request for Active state by Employer'''
    @api.multi
    def action_active_button(self):
        self.write({'current_status':'req_active','req_for_approve':False})
    
    '''This method is used to do request for Drop Out state by Employer'''
    @api.multi
    def action_dropout_button(self):
        self.write({'current_status':'req_drop_out','req_for_approve':False})
        
    '''This method is used to do request for Replacement state by Employer''' 
    @api.multi
    def action_replacement_button(self):
        self.write({'current_status':'req_replacement','req_for_approve':False})
    
    '''This method is used to do request for Suspend state by Employer'''
    @api.multi
    def action_suspend_button(self):
        self.write({'current_status':'req_suspend','req_for_approve':False})
    
    '''This method is used to do request for In Active state by Employer'''
    @api.multi
    def action_inactive_button(self):
        self.write({'current_status':'req_in_active','req_for_approve':False})
        
    #  adding validation 
    @api.multi
    @api.onchange('work_phone','cell','fax_no','work_email','business_tel_no')
    def onchange_validate_number(self):
            
            if self.business_tel_no:
                if not self.business_tel_no.isdigit() or len(self.business_tel_no) != 10:
                    self.business_tel_no = ''
                    return {'warning':{'title':'Invalid input','message':'Please enter 10 digits telephone number'}}
            if self.work_email:
                if '@' not in self.work_email:
                    self.work_email = ''
                    return {'warning':{'title':'Invalid input','message':'Please enter valid email address'}}
            if self.work_phone:
                if not self.work_phone.isdigit() or len(self.work_phone) != 10:
                    self.work_phone = ''
                    return {'warning':{'title':'Invalid input','message':'Please enter 10 digits Phone number'}}
            if self.cell:
                if not self.cell.isdigit() or len(self.cell) != 10:
                    self.cell = ''
                    return {'warning':{'title':'Invalid input','message':'Please enter 10 digits Mobile number'}}
            if self.fax_no:
                if not self.fax_no.isdigit() or len(self.fax_no) != 10:
                    self.fax_no = ''
                    return {'warning':{'title':'Invalid input','message':'Please enter 10 digits Fax number'}}
    
            
    '''This method is used to approve waiting request of Employer by SDP Manager'''
    @api.multi
    def action_approve_button(self):
        if self.current_status == 'wait_active':
            total_persons_granted = self.learner_id.enroll_project_ids.employed + self.learner_id.enroll_project_ids.non_employed
            count_active = 0
            for line in self.learner_id.learner_ids:
                if line.current_status == 'active':
                    count_active += 1
            if count_active >= total_persons_granted:
                raise Warning(_("Sorry!! Total persons granted has been exceed!"))
            else:
                self.write({'current_status':'active','state':'active'})
        elif self.current_status == 'wait_in_active':
            self.write({'current_status':'in_active','state':'inactive'})
        elif self.current_status == 'wait_drop_out':
            self.write({'current_status':'drop_out','state':'dropout'})
        elif self.current_status == 'wait_replacement':
            self.write({'current_status':'replacement','state':'replacement'})
        elif self.current_status == 'wait_suspend':
            self.write({'current_status':'suspend','state':'suspended'})
        return True
    
    '''This method is used to reject waiting request of Employer by SDP Manager'''
    @api.multi
    def action_reject_button(self):
        if self.current_status == 'wait_active':
            self.write({'current_status':self.state})
        elif self.current_status == 'wait_in_active':
            self.write({'current_status':self.state})
        elif self.current_status == 'wait_drop_out':
            self.write({'current_status':self.state})
        elif self.current_status == 'wait_replacement':
            self.write({'current_status':self.state})
        elif self.current_status == 'wait_suspend':
            self.write({'current_status':self.state})
        return True
    
    '''This method is used to send approval request to SDP Manager by Employer'''
    @api.multi
    def action_request_for_approve(self):
        self.write({'req_for_approve':True})
        if self.current_status == 'req_active':
            self.write({'current_status':'wait_active'})
        elif self.current_status == 'req_in_active':
            self.write({'current_status':'wait_in_active'})
        elif self.current_status == 'req_drop_out':
            self.write({'current_status':'wait_drop_out'})
        elif self.current_status == 'req_replacement':
            self.write({'current_status':'wait_replacement'})
        elif self.current_status == 'req_suspend':
            self.write({'current_status':'wait_suspend'})
        return True
    
    @api.multi
    def onchange_crc(self, citizen_residential_status):
        res = {}
        if not citizen_residential_status:
            return res
        if citizen_residential_status == 'sa':
            country_data = self.env['res.country'].search(['|',('code','=','ZA'),('name','=','South Africa')],limit=1)
            res.update({'value':{'nationality_id':country_data and country_data.id}})
        return res
    
    @api.multi
    def onchange_id_no(self, identification_id):
        res, val = {}, {}
        if not identification_id:
            return res
        if len(identification_id) == 13 and str(identification_id).isdigit():
            year = identification_id[:2]
            identification_id = identification_id[2:]
            month = identification_id[:2]
            identification_id = identification_id[2:]
            day = identification_id[:2]
            if int(month) > 12 or int(month) < 1 or int(day) > 31 or int(day) < 1:
                return {'value':{'identity_number':''},'warning':{'title':'Invalid Identification Number','message':'Incorrect Identification Number!'}}
            else:
                # # Calculating last day of month.
                x_year = int(year)
                if x_year == 00:
                    x_year = 2000
                last_day = calendar.monthrange(int(x_year),int(month))[1]
                if int(day) > last_day :
                    return {'value':{'identity_number':''},'warning':{'title':'Invalid Identification Number','message':'Incorrect Identification Number!'}}
            if int(year) == 00 or int(year) >= 01 and int(year) <= 20:
                birth_date = datetime.strptime('20' + year + '-' + month + '-' + day, '%Y-%m-%d').date()
            else:
                birth_date = datetime.strptime('19' + year + '-' + month + '-' + day, '%Y-%m-%d').date()
            
            val.update({'date_of_birth':birth_date})
            res.update({'value':val})
            return res
        else:
            return {'value':{'identity_number':''},'warning':{'title':'Invalid Identification Number','message':'Identification Number should be numeric!'}}
    
    ##  Added  Sequence for Learner Agreement
    @api.model
    def create(self, vals):
        vals['seq_no'] = self.env['ir.sequence'].get('sdp.learner')
        return super(sdp_learner, self).create(vals)
    
    @api.multi
    def country_for_province(self, province):
        state = self.env['res.country.state'].browse(province)
        return state.country_id.id
    
    @api.multi
    def onchange_postal_province(self, province):
        if province:
            country_id = self.country_for_province(province)
            return {'value': {'learner_country_postal': country_id }}
        return {}
    
    @api.multi
    def onchange_home_province(self, province):
        if province:
            country_id = self.country_for_province(province)
            return {'value': {'learner_country_home': country_id }}
        return {}
    
    @api.multi
    def onchange_country_id(self, country_id):
        res = {}
        if not country_id:
            return res
        country_data = self.env['res.country'].browse(country_id)
        if country_data.code == 'ZA':
            res.update({'value':{'african':True}})
        else:
            res.update({'value':{'african':False}})
        return res
    
    @api.multi
    def onchange_learner_suburb(self, person_suburb):
        res = {}
        if not person_suburb:
            return res
        if person_suburb:
            sub_res = self.env['res.suburb'].browse(person_suburb)
            res.update({'value':{'learner_home_zip':sub_res.postal_code,'learner_home_city':sub_res.city_id,'learner_home_municipality':sub_res.municipality_id,'learner_home_province_code':sub_res.province_id}})
        return res  
      
    @api.multi
    def onchange_learner_postal_suburb(self, person_postal_suburb):
        res = {}
        if not person_postal_suburb:
            return res
        if person_postal_suburb:
            sub_res = self.env['res.suburb'].browse(person_postal_suburb)
            res.update({'value':{'learner_postal_zip':sub_res.postal_code,'learner_postal_city':sub_res.city_id,'learner_postal_municipality':sub_res.municipality_id,'learner_postal_province_code':sub_res.province_id}})
        return res    
    
sdp_learner()

class eoi_moa(models.Model):
    _name = 'eoi.moa'
    
    name = fields.Char(string='Name')
    learning_programme_id = fields.Many2one('learning.programme', string='Name')
#     attach_moa = fields.Binary(string='MOA')
    attach_moa = fields.Many2one('ir.attachment', string='MOA')
    status = fields.Selection([('pending','Pending For Acceptance'),
                              ('accepted','Accepted'),
                              ], string="State", default='pending')
    
    
eoi_moa()

class eoi_document(models.Model):
    _name = 'eoi.document'
    
    name = fields.Many2one('project.document',string="Document Name")
    learning_programme_id = fields.Many2one('learning.programme', string='Name')
    attached = fields.Binary(string='attach')
    attach_doc = fields.Many2one('ir.attachment', string='Attach Document')
    
eoi_document()

class ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def default_get(self, fields_list):
        context = self._context.copy()
        res = super(ir_attachment, self).default_get(fields_list)
        if context and context.get('moa',False) :
            res.update({'name' : 'MOA'})
        return res 
    
ir_attachment()

class tranche_generation(models.Model):
    _name = 'tranche.generation'
    
    name = fields.Char("Name")
    tranche_id = fields.Integer("Tranche id")
    number = fields.Integer("Tranche Number")
    employed_unemployed = fields.Char("18.1/18.2")
    approve_transche = fields.Boolean("Tranche generated", default=False)
    reject_transche = fields.Boolean("Reject Tranche",default=False)
    recommend_transche = fields.Boolean("Recommend Tranche", default=False)
    learning_program_id = fields.Many2one('learning.programme',string="Learning Program")
    monitor_and_evaluate_id = fields.Many2one('monitor.and.evaluate',string="Monitor and Evaluate")
    status = fields.Char("Status")

    @api.multi
    def action_recommend_transche(self):
        ''' method to SDP manager will recommend for tranche generation to finance department'''
        transche = self.env['transche.payment'].search([('id','=',self.tranche_id)])
        transche_document_ids = [document.name.id for document in transche.tranche_document_ids if document.required == True]
        if self.learning_program_id and not (self.monitor_and_evaluate_id) : 
            learning_program = self.env['learning.programme'].search([('id','=',self.learning_program_id.id)])        
            for document in learning_program.document_ids:
                if document.name.id in transche_document_ids and not (document.attach_doc):
                    raise Warning(_('Please upload the %s document!')%(document.name.name))
        if not (self.learning_program_id) and self.monitor_and_evaluate_id : 
            monitor_and_evaluate = self.env['monitor.and.evaluate'].search([('id','=',self.monitor_and_evaluate_id.id)])
            for documents in monitor_and_evaluate.monitor_and_evaluate_document_ids:
                if documents.name.id in transche_document_ids and not (documents.attach_doc):
                    raise Warning(_('Please upload the %s document!')%(documents.name.name))            
        self.write({'recommend_transche':True,'status':'Recommended'})
        return True
    
    @api.multi
    def action_approve_transche(self):
        ''' method to Finance department will generated tranche'''
        if self.learning_program_id and not (self.monitor_and_evaluate_id) : 
            learning_program = self.env['learning.programme'].search([('id','=',self.learning_program_id.id)])
            employer_data = learning_program.employer_id
    #         ## Getting Project Wise Tranche.
            for project_data in learning_program.enroll_project_ids :
                project_info = project_data.project_id
                model_data = self.env['ir.model'].search([('model','=','learning.programme')])
                ## Previously single tranche payment generated for both emp and unemp.
                transche_payment_data = self.env['transche.payment'].search([('project_id','=',project_info.id),('trigger_jv','=',model_data.id),('id','=',self.tranche_id)])
                if not transche_payment_data :
                    raise Warning(_('No Tranche Payment Configuration defined for project %s for EOI!')%(project_info.name))
                if transche_payment_data:
                    if self.learning_program_id.learning_project_id.category_type == '18.1':
                        self.env['transche.payment'].transche_payment_jv(project_data, employer_data, '- Tranche Payment for EOI '+learning_program.name+'', transche_payment_data, 'employed')
                    if self.learning_program_id.learning_project_id.category_type == '18.2':
                        self.env['transche.payment'].transche_payment_jv(project_data, employer_data, '- Tranche Payment for EOI '+learning_program.name+'', transche_payment_data, 'unemployed')
        if self.monitor_and_evaluate_id and not (self.learning_program_id): 
            monitor_and_evaluate = self.env['monitor.and.evaluate'].search([('id','=',self.monitor_and_evaluate_id.id)])
            employer_data = monitor_and_evaluate.employer_id
            ### Getting Project Wise Tranche.
            for project_data in monitor_and_evaluate.project_info_ids:
                project_info = project_data.project_id
                model_data = self.env['ir.model'].search([('model','=','monitor.and.evaluate')])
                ## Previously single tranche payment generated for both emp and unemp.
                transche_payment_data = self.env['transche.payment'].search([('project_id','=',project_info.id),('trigger_jv','=',model_data.id),('id','=',self.tranche_id)])
                if not transche_payment_data :
                    raise Warning(_('No Tranche Payment Configuration defined for project %s for Monitoring and Evaluation!')%(project_info.name))
                if transche_payment_data:
                    if monitor_and_evaluate.project_id.category_type == '18.1':
                        self.env['transche.payment'].transche_payment_jv(project_data, employer_data, '- Tranche Payment for Monitoring and Evalaution '+monitor_and_evaluate.name+'', transche_payment_data, 'employed')
                    if monitor_and_evaluate.project_id.category_type == '18.2':
                        self.env['transche.payment'].transche_payment_jv(project_data, employer_data, '- Tranche Payment for Monitoring and Evalaution '+monitor_and_evaluate.name+'', transche_payment_data, 'unemployed')
        self.write({'approve_transche':True,'status':'Approved'})
        return True
    
    @api.multi
    def action_reject_transche(self):
        ''' method to Finance department will reject for  transche'''
        
        self.write({'reject_transche':True,'status':'Rejected'})
        return True        

## Class depicting Learnership Project.
class learning_programme(models.Model):
    _name = 'learning.programme'
    _inherit = 'mail.thread'
    _description = 'Learning Programme'

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ Override read_group to show correct group count and default EOI ID group in SDF Portal"""
        ret_val = super(learning_programme, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if ret_val:
            for rec in ret_val:
                if rec.has_key('eoi_id_reference'):
                    ppr_obj = self.env['learning.programme'].search([('eoi_id_reference','=',rec['eoi_id_reference'])])
                    if ppr_obj:
                        ppr_ids = [ppr_id.id for ppr_id in ppr_obj] 
                        domain.append(['id','in',ppr_ids])
                        rec['eoi_id_reference_count'] = len(ppr_ids)
                    else:
                        rec['eoi_id_reference_count'] = 0L
        return ret_val

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        user_obj = self.env['res.users']
        user_data = user_obj.browse(self._uid)
        user_groups = user_data.groups_id
        employer = False
        sdf = False
        for group in user_groups:
            if group.name == "WSP Manager":
                return super(learning_programme, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            if group.name == "SDP Manager":
                return super(learning_programme, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            if group.name == "Provincial Manager":
                return super(learning_programme, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            if group.name == "WSP Officer":
                return super(learning_programme, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            if group.name == "Provincial Officer":
                return super(learning_programme, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            if group.name == "WSP Administrator":
                return super(learning_programme, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            if group.name == "General Access":
                return super(learning_programme, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            if group.name == "Auditor Access":
                return super(learning_programme, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            if group.name == "Employer":
                employer = True
            if group.name == "SDF":
                sdf = True                
        if not user_data.id == 1 :
            if sdf :
                employer_sdf = self.env['sdf.tracking'].search([('status','=','approved'),('sdf_id','=',user_data.sdf_id.id)])
                employer_id = [employer1.partner_id.id for employer1 in employer_sdf] 
                args.append(('employer_id','in',employer_id))
            if employer :
                args.append(('employer_id','=',user_data.partner_id.id))
        return super(learning_programme, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)    
    
    ## In order to have employer selected by default.
    @api.model
    def _default_employer(self):
        user = self._uid
        user_data = self.env['res.users'].browse(user)
        if user_data.partner_id.employer:
            partner_id = user_data.partner_id.id
        else:
            partner_id = None
        return partner_id

    
    name = fields.Char(string='Leanership name',track_visibility='onchange', default='/')
    ## Employer Details.
    employer_id = fields.Many2one('res.partner', string="Employer",track_visibility='onchange', domain=[('employer','=',True)], default=_default_employer)
    employer_sdl_no = fields.Char(string='SDL No.',track_visibility='onchange', size=10)
    employer_site_no = fields.Char(string='Site No.',track_visibility='onchange', size=10)
    employer_seta_id = fields.Many2one('seta.branches', string='SETA Id',track_visibility='onchange')
    employer_sic_code = fields.Char(string='SIC Code',track_visibility='onchange', size=10)
    empl_sic_code = fields.Many2one('hwseta.sic.master', string='SIC Code')
    employer_registration_number = fields.Char(string='Registration Number',track_visibility='onchange', size=20)
    employer_trading_name = fields.Char(string='Employer Trading Name',track_visibility='onchange', size=70)
    ## Projects Related Fields
    category = fields.Many2one('hwseta.project.category', string='Project Category')
    category_type = fields.Selection([('18.1','Employed Learners (18.1)'),('18.2','Unemployed Learners (18.2)')], string="Category Type")
    enroll_project_ids = fields.One2many('enrollment.projects', 'learnership_id', string='Project Enrollments')
    ## State field for Learnership process.
    state = fields.Selection([
                              ('pending','Pending'),
                              ('submitted','Submitted'),
                              ('evaluation','Evaluation'),
                              ('recommended','Recommended'),
                              ('conditional_approval','Conditional Approval'),
                              ('approved','Approved'),
                              ('rejected','Rejected'),
                              ('final_approval','Completed'),
                              ], string="State",index=True, default='pending',
        track_visibility='onchange', copy=False,
        help=" * The 'Pending' Pending to Submit Project Details.\n"
             " * The 'Evaluation' Evaluating Projects and Related Docs.\n"
             " * The 'Approved' Projects Requirements are approved.\n"
             " * The 'Rejected' Application Rejection.\n"
             " * The 'Done' Process Completion.\n")
    ## Fields for Buttons Hide and Seek
    submitted = fields.Boolean(string='Submitted')
    approved = fields.Boolean(string='Approved')
    evaluate = fields.Boolean(string='Evaluated')
    recommend = fields.Boolean(string='Recomended')
    cond_approved = fields.Boolean(string='Conditional Approved')
    is_moa_attached = fields.Boolean(string='MOA Attached')
    accept_moa = fields.Boolean(string='MOA Accepted')
#     final_approved = fields.Boolean(string='Final Approved')
    rejected1 = fields.Boolean(string='Rejected1')
    learner_loaded = fields.Boolean(string='Learner Loaded')
    rejected2 = fields.Boolean(string='Rejected2')
    ##
    name_of_moa = fields.Char(string='MOA',track_visibility='onchange')
    name = fields.Char(string='Filename',track_visibility='onchange')
    attach_moa = fields.Binary(string='Attach MOA',nodrop=True)
    attach_moa2 = fields.Binary(string='Attach MOA',nodrop=True)
    requested_empl = fields.Char(string="Requested 18.1")
    requested_non_empl = fields.Char(string="Requested 18.2")
    approved_empl = fields.Char(string="Approved 18.1")
    approved_non_empl = fields.Char(string="Approved 18.2")
    accepted_empl = fields.Char(string="Accepted 18.1")
    accepted_non_empl = fields.Char(string="Accepted 18.2")
    granted_total_req = fields.Integer(string="Granted Req")
    granted_total_app = fields.Char(string="Granted App")
    granted_total_acc = fields.Char(string="Granted Acc")
    ## for final approval
    final_empl = fields.Char(string="Final 18.1")
    final_non_empl = fields.Char(string="Final 18.2")
    granted_total_final = fields.Char(string="Granted Final")
    learner_ids = fields.One2many('sdp.learner', 'learner_id', string='Learner')
    enroll_status = fields.Char(string='Status', default='Pending')
    show_moa = fields.Boolean(string='Show MOA')
    date_of_enroll = fields.Date(string='Date', default=datetime.now())
    comment = fields.Text(string='Reason')
    ## One2many for MOA's , will keep MOA per Project Type.
    moa_ids = fields.One2many('eoi.moa', 'learning_programme_id', string='MOA')
    document_ids = fields.One2many('eoi.document', 'learning_programme_id', string='MOA')
    learning_program_tranche_ids = fields.One2many('tranche.generation','learning_program_id',string="Tranche Generation")
    eoi_status_ids = fields.One2many('eoi.status', 'eoi_id', string='EOI Status')
    conditional_approval = fields.Boolean("Conditional Approval", default=False)
    learning_project_type_id = fields.Many2one('hwseta.project.types',string="Project Type")
    learning_project_id = fields.Many2one('project.project',string="Project")
    eoi_id_reference = fields.Char(related='learning_project_id.eoi_id.eoi_id', store=True, readonly=True, copy=False)

    @api.multi
    def onchange_default_project_type(self,learning_project_type_id):
        res = {}
        if learning_project_type_id :
            project = [ project.id for project in self.env['project.project'].search([('project_types','=',learning_project_type_id)])]
            res.update({'domain':{'learnerning_project_id':[('id','in',project)]}})
        return res       
    
    @api.multi
    def onchnage_attach_moa(self, attach_moa) : 
        ''' Copying MOA attached by SDP Manager to Employer MOA'''
        res = {}
        if not attach_moa:
            return res
        res.update({'value':{'attach_moa2':attach_moa}})
        return res
        
    @api.multi
    def onchange_employer_id(self, employer_id):
        res = {}
        if not employer_id:
            return res 
        employer_data = self.env['res.partner'].browse(employer_id)
        values = {
                  'employer_sdl_no' : employer_data.employer_sdl_no,
                  'employer_site_no' : employer_data.employer_site_no,
                  'employer_seta_id' : employer_data.employer_seta_id and employer_data.employer_seta_id.id,
                  'empl_sic_code' : employer_data.empl_sic_code and employer_data.empl_sic_code.id,
                  'employer_registration_number' : employer_data.employer_registration_number,
                  'employer_trading_name' : employer_data.employer_registration_number,
        } 
        res['value'] = values
        return res
    
    @api.multi
    def action_calculate_moa(self):
#         ## Finding number of unique project types.
#         project_type_ids = [project_info.project_types and project_info.project_types.id for project_info in self.enroll_project_ids]
#         unique_project_type_ids = list(set(project_type_ids))
#         ## Removing MOA records if exists before.
#         if self.moa_ids : 
#             self.write({'moa_ids' : [(2,moa_info.id) for moa_info in self.moa_ids]})
#         ## Generating MOA records which is equal to no of unique project types.
#         moa_list = [(0,0,{'name' : 'MOA for '+str(project_type_info.name.name),'learning_programme_id' : self.id}) for project_type_info in self.env['hwseta.project.types'].browse(unique_project_type_ids)]
#         self.write({'moa_ids' : moa_list})
        
        self = self.with_context({'eoi_id':self.id})
        return {
                    'name' : 'Attach',
                    'type' : 'ir.actions.act_window',
                    'view_type' : 'form',
                    'view_mode' : 'form',
                    'res_model' : 'moa.attachment',
                    'target' : 'new',
                    'context' : self._context,
                }        
        return True
    
    @api.multi
    def compute_total_learners(self):
        learner_obj = self.env['sdp.learner']
        learner_data = learner_obj.search([('learner_id','=',self.id)])
        if learner_data:
            self.write({'learner_ids':[(2, learner.id) for learner in learner_data]})
        for project_data in self.enroll_project_ids:
            total = 0
            total_employed = 0
            total_unemployed = 0
            total += (project_data.employed+project_data.non_employed)
            total_employed += (project_data.employed)
            total_unemployed += (project_data.non_employed)
            project_dict = {
                            'project_id':project_data.project_id and project_data.project_id.id, 
                            'project_type':project_data.project_id and project_data.project_id.project_types and project_data.project_types.id,
                            'provider_id':project_data.provider_id and project_data.provider_id.id 
                            }
            while total_employed>0:
                self.write({'learner_ids': [(0,0,{'learner_id':self.id,'employee_type':'employed','proj_enrolled_ids':[(0,0,project_dict)]})]})
                total_employed -= 1
            while total_unemployed>0:
                self.write({'learner_ids': [(0,0,{'learner_id':self.id,'employee_type':'unemployed','proj_enrolled_ids':[(0,0,project_dict)]})]})
                total_unemployed -= 1                
        return True
            
    @api.multi
    def get_list(self,list_val):
        ret_list = []
        for req_em in list_val:
            if req_em:
                ret_list.append(req_em)
        return ret_list
    
    @api.multi
    def write(self, vals):
        res = super(learning_programme, self).write(vals)
        status = ''
        context = self._context
        ##
        if vals.get('state',False) == "evaluation":
            status = 'evaluation'
        if vals.get('state',False) == 'approved':
            status = 'approved'
        if vals.get('state',False) == 'final_approval':
            status = 'final_approval'
        count = 0
        for project_data in self.enroll_project_ids :
            req_empl = []
            req_non_empl = []
            app_empl = []
            app_non_empl = []
            fin_empl = []
            fin_non_empl = []
            
            if self.requested_empl and self.requested_non_empl and self.approved_empl and self.approved_non_empl and self.final_empl and self.final_non_empl:
                req_empl = self.get_list(self.requested_empl.split(','))
                req_non_empl = self.get_list(self.requested_non_empl.split(','))
                app_empl = self.get_list(self.approved_empl.split(','))
                app_non_empl = self.get_list(self.approved_non_empl.split(','))
                fin_empl = self.get_list(self.final_empl.split(','))
                fin_non_empl = self.get_list(self.final_non_empl.split(','))
                
                if status == 'evaluation' and int(req_empl[count]) != 0 and int(req_non_empl[count]) != 0:
                    project_data.write({'employed':int(req_empl[count]), 'non_employed':int(req_non_empl[count])})
                if status == 'approved' and int(app_empl[count]) != 0 and int(app_non_empl[count]) != 0:
                    project_data.write({'employed':int(app_empl[count]), 'non_employed':int(app_non_empl[count])})
                if status == 'final_approval' and int(fin_empl[count]) != 0 and int(fin_non_empl[count]) != 0:
                    project_data.write({'employed':int(fin_empl[count]), 'non_employed':int(fin_non_empl[count])})
            project_data.write({'status':status})
            count+=1
            if (not (project_data.project_id.fees_employed) and project_data.req_employed > 0):
                raise Warning(_('Sorry! Employed learner can not apply for this project!'))
            if (not (project_data.project_id.fees_unemployed) and project_data.req_unemployed > 0):
                raise Warning(_('Sorry! Unemployed learner can not apply for this project!'))          
        
        
        #code to write newly added learner_ids's proj_enrolled_ids field on click of save button
        for learners in self.learner_ids:
            if not (learners.proj_enrolled_ids):
                    for project_data in self.enroll_project_ids:
                        project_dict = {
                                        'project_id':project_data.project_id and project_data.project_id.id, 
                                        'project_type':project_data.project_id and project_data.project_id.project_types and project_data.project_types.id,
                                        'provider_id':project_data.provider_id and project_data.provider_id.id 
                                        }  
                    learners.write({'proj_enrolled_ids':[(0,0,project_dict)]})                  
         
        ## Handling to avoid random clicks on states before approval.
        if context.get('submit',False) == True:
            pass
        if self.state == "evaluation" and self.submitted == False:
            raise Warning(_('Sorry! You can not change the status to evaluation.'))
#         if self.state == "conditional_approval" and self.attach_moa == False:
#             eoi_obj = self.env['eoi.moa']
#             eoi_search = eoi_obj.search([('learning_programme_id','=',self.id)])
#             if not eoi_search.attach_moa:
#                 self.write({'attach_moa':False})
#             else:
#                 self.write({'attach_moa':True})            
        if self.state == "approved" and self.approved == False:
            raise Warning(_('Sorry! You can not change the status to approved.'))
        if self.state == "rejected" and (self.rejected1 == False and self.rejected2 == False):
            raise Warning(_('Sorry! You can not change the status to rejected.'))
        if self.state == "final_approval" and (self.rejected1 == True or self.rejected2 == True):
            raise Warning(_('Sorry! You can not change the status to done.'))
        if self.state == "final_approval" and self.learner_loaded == False:
            raise Warning(_('Sorry! You can not change the status to done.'))
        if self.state == "approved" and (self.rejected1 == True or self.rejected2 == True):
            raise Warning(_('Sorry! You can not change the status to approve.'))
        return res
    
    ## Added Sequence for Learnership.
    @api.model
    def create(self, vals):    
        vals['name'] = self.env['ir.sequence'].get('learning.programme') or '/'
        res = super(learning_programme, self).create(vals)
        return res
    
    @api.multi
    def action_submit_learnership(self):
        current_date = datetime.now()
        employer_req_obj = self.env['employer.requests']
        if self.submitted == True:
            raise Warning(_('Information Already Submitted!'))
        if not self.enroll_project_ids:
            raise Warning(_('Please enter project related information!.'))
        if self.enroll_project_ids:
            for enroll_data in self.enroll_project_ids:
                if enroll_data.req_employed < 1 and self.learning_project_id.category_type == '18.1':
                    raise Warning(_('Please Add Employed Learners!'))
                if enroll_data.req_unemployed < 1 and self.learning_project_id.category_type == '18.2':
                    raise Warning(_('Please Add Unemployed Learners!'))
                if enroll_data.project_id:
                    project_obj= self.env['project.project'].search([('id','=',enroll_data.project_id.id)])
                    eoi_extension = self.env['partner.project.rel'].search([('emp_project_id','=',project_obj.id),('eoi_ext_request','=',True),('employer_id','=',self.employer_id.id)])
                    if not (eoi_extension) :
                        if str(current_date) > project_obj.eoi_end_date : 
                            raise Warning(_('Please apply to EOI extension for project %s !')%(project_obj.name))
                    if eoi_extension and not (eoi_extension.eoi_ext_date):
                        raise Warning(_('Please contact HWSETA to EOI extension date for project %s !')%(project_obj.name))  
        self = self.with_context(submit=True)
        self.write({'submitted':True, 'state':'submitted','enroll_status':'Submitted'})
        eoi_status_obj = self.env['eoi.status'].create({'user_id': self._uid,
                                                        'state': 'submitted',
                                                        'eoi_id': self.id,
                                                        'comment': self.comment,
                                                        'status': 'Submitted',
                                                      })
        for project_data in self.enroll_project_ids:
            self.write({'requested_empl':self.requested_empl or ','+','+str(project_data.employed), 'requested_non_empl':self.requested_non_empl or ','+','+str(project_data.non_employed)})
            project_data.write({'status':'evaluation'})
            project = project_data.project_id and project_data.project_id
            employer_req_obj.create({
                                     'employer_id' : self.employer_id and self.employer_id.id,
                                     'req_employed' : project_data.req_employed,
                                     'req_unemployed' : project_data.req_unemployed,
                                     'project_id' : project.id,
                                     'enroll_project_id' : project_data.id,
                                     'eoi_id' : self.id,
                                     })
            project_data.write({'state':'pending_approval'})
            
            ## for generating tranche line associated with the project in EOI
            tranche_ids = self.env['transche.payment'].search([('project_id','=',project.id),('trigger_jv','in',['learning.programme']),('funding_year','=',project.seta_funding_year.id)])
            if tranche_ids:
                if self.learning_project_id.category_type == '18.1':
                    tranche_list = [(0,0,{'name' :tranche.name,'number':tranche.no_of_tranche,'learning_program_id' : self.id,'tranche_id':tranche.id}) for tranche in tranche_ids]
                    self.write({'learning_program_tranche_ids':tranche_list})
                elif self.learning_project_id.category_type == '18.2':
                    tranche_list = [(0,0,{'name' :tranche.name,'number':tranche.no_of_tranche_18_2,'learning_program_id' : self.id,'tranche_id':tranche.id}) for tranche in tranche_ids]
                    self.write({'learning_program_tranche_ids':tranche_list})
            if not (tranche_ids):
                raise Warning(_('Please configure transche for project %s !')%(project.name))
        ## Finding number of unique project types.
        project_type_ids = [project_info.project_types and project_info.project_types.id for project_info in self.enroll_project_ids]
        unique_project_type_ids = list(set(project_type_ids))
        ## Removing Document records if exists before.
        if self.document_ids : 
            self.write({'document_ids' : [(2,document_info.id) for document_info in self.document_ids]})
        ## Generating Document records which is equal to no of unique project types.
        document_list = [(0,0,{'name' : project_type_info.name.id,'learning_programme_id' : self.id}) for project_type_info in self.env['hwseta.project.types'].browse(unique_project_type_ids).project_document_ids]
        self.write({'document_ids' : document_list})    
        ## Email Notification to Employer
#         ir_model_data_obj = self.env['ir.model.data']
#         mail_template_id = ir_model_data_obj.get_object_reference('hwseta_sdp', 'email_template_eoi_submit')
#         if mail_template_id:
#             self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True,context=self.env.context)
        return True
    
    @api.multi
    def action_evaluate(self):
        employer_req_obj = self.env['employer.requests']
#         if self.submitted == True:
#             raise Warning(_('Information Already Submitted!'))
#         if not self.enroll_project_ids:
#             raise Warning(_('Please enter project related information!.'))
        self = self.with_context(evaluate=True)
        self.write({'evaluate':True, 'state':'evaluation','enroll_status':'Evaluated'})
        eoi_status_obj = self.env['eoi.status'].create({'user_id': self._uid,
                                                        'state': 'evaluated',
                                                        'eoi_id': self.id,
                                                        'comment': self.comment,
                                                        'status': 'Evaluated',
                                                      })
        return True
    
    @api.multi
    def action_recommend(self):
        employer_req_obj = self.env['employer.requests']
#         if self.submitted == True:
#             raise Warning(_('Information Already Submitted!'))
#         if not self.enroll_project_ids:
#             raise Warning(_('Please enter project related information!.'))
        self = self.with_context(evaluate=True)
        self.write({'recommend':True, 'state':'recommended','enroll_status':'Recommended'})
        eoi_status_obj = self.env['eoi.status'].create({'user_id': self._uid,
                                                        'state': 'recommended',
                                                        'eoi_id': self.id,
                                                        'comment': self.comment,
                                                        'status': 'Recommeded',
                                                      })
        return True
    
    @api.multi
    def action_cond_approve(self):
        ''' Checking whether all projects got the approval.'''
        approved = True
        for enroll_project_info in self.enroll_project_ids :
            if not enroll_project_info.state == 'approved' :
                approved = False
        if approved == True :
            for project_data in self.enroll_project_ids:
                self.write({'approved_empl':self.approved_empl or ','+','+str(project_data.employed), 'approved_non_empl':self.approved_non_empl or ','+','+str(project_data.non_employed), 'granted_total_app':self.granted_total_app or ','+','+str(project_data.persons_approved)})
                project_data.write({'status':'approved'})
        else :
            raise Warning(_('Please update EOI information from individual project to mark project approved! Once all projects get approved , the transaction will be approved.'))
        self = self.with_context(evaluate=True)
        self.write({'cond_approved':True, 'state':'conditional_approval','enroll_status':'Conditional Approved'})
        return True

    @api.multi
    def action_conditional_approval(self):
        ''' send conditional approval template and moa template to the enmployer for accepting terms and condition for EOI.'''
        if self.learning_project_id :
                attachment_ids = []
                attachment_ids.append(self.learning_project_id.moa_template.id)
                attachment_ids.append(self.learning_project_id.conditional_approval_details.id)
                ir_model_data_obj = self.env['ir.model.data']
                mail_template_id = ir_model_data_obj.get_object_reference('hwseta_sdp', 'email_template_conditional_approval')
                email_template_obj = self.env['email.template']
                temp_obj = email_template_obj.browse(mail_template_id[1])
                if mail_template_id:
                    temp_obj.write({'attachment_ids':[(6, 0, attachment_ids)]})
                    self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True,context=self.env.context)
                self.write({'conditional_approval':True})
                eoi_status_obj = self.env['eoi.status'].create({'user_id': self._uid,
                                                        'state': 'conditional_approval',
                                                        'eoi_id': self.id,
                                                        'comment': self.comment,
                                                        'status': 'Conditional Approval',
                                                      })
        return True    
    
    @api.multi
    def action_approve_learnership(self):
        if self.submitted == False:
            raise Warning(_('Information Not Submitted in order to Approve it!'))
        if self.approved == True:
            raise Warning(_('Information Already Approved!'))
        if not self.moa_ids :
            raise Warning(_('Please attach MOA before Approval!'))
        ## Checking whether all projects got the approval.
#         approved = True
#         for enroll_project_info in self.enroll_project_ids :
#             if not enroll_project_info.state == 'approved' :
#                 approved = False
#         if approved == True :
#             for moa in self.moa_ids :
#                 if not moa.attach_moa :
#                     raise Warning(_('Please attach MOA in "%s"!')%(moa.name))
#             self.write({'approved':True, 'state':'approved','enroll_status':'Approved'})
#             for project_data in self.enroll_project_ids:
#                 self.write({'approved_empl':self.approved_empl or ','+','+str(project_data.employed), 'approved_non_empl':self.approved_non_empl or ','+','+str(project_data.non_employed), 'granted_total_app':self.granted_total_app or ','+','+str(project_data.persons_approved)})
#                 project_data.write({'status':'approved'})
#         else :
#             raise Warning(_('Please update EOI information from individual project to mark project approved! Once all projects get approved , the transaction will be approved.'))
        self.write({'approved':True, 'state':'approved','enroll_status':'Approved'})
        eoi_status_obj = self.env['eoi.status'].create({'user_id': self._uid,
                                                        'state': 'approved',
                                                        'eoi_id': self.id,
                                                        'comment': self.comment,
                                                        'status': 'Approved',
                                                      })
        ## Email Notification to Employer
#         ir_model_data_obj = self.env['ir.model.data']
#         mail_template_id = ir_model_data_obj.get_object_reference('hwseta_sdp', 'email_template_eoi_approve')
#         if mail_template_id:
#             self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True,context=self.env.context)
        return True
    
    ## This method deny the learnership process.
    @api.multi
    def action_deny_learnership(self):
#         self.write({'state':'rejected', 'approved': True, 'final_approved':True, 'moa_sent':True, 'accept_moa':True,'enroll_status':'Rejected'})
        ## Email Notification to Employer
        ir_model_data_obj = self.env['ir.model.data']
        mail_template_id = ir_model_data_obj.get_object_reference('hwseta_sdp', 'email_template_eoi_rejection')
        if mail_template_id:
            self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True,context=self.env.context)
        self.write({'state':'rejected', 'enroll_status':'Rejected', 'rejected1':True})
        eoi_status_obj = self.env['eoi.status'].create({'user_id': self._uid,
                                                        'state': 'rejected',
                                                        'eoi_id': self.id,
                                                        'comment': self.comment,
                                                        'status': 'Rejected',
                                                      })
        return True
    
    @api.multi
    def action_deny_learnership2(self):
#         self.write({'state':'rejected', 'approved': True, 'final_approved':True, 'moa_sent':True, 'accept_moa':True,'enroll_status':'Rejected'})
        ## Email Notification to Employer
        ir_model_data_obj = self.env['ir.model.data']
        mail_template_id = ir_model_data_obj.get_object_reference('hwseta_sdp', 'email_template_eoi_rejection')
        if mail_template_id:
            self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True,context=self.env.context)
        self.write({'state':'rejected', 'enroll_status':'Rejected', 'rejected2':True})
        return True
    
    @api.multi
    def action_accept_moa(self):
        ## Email Notification to Employer
#         ir_model_data_obj = self.env['ir.model.data']
#         mail_template_id = ir_model_data_obj.get_object_reference('hwseta_sdp', 'email_template_eoi_moa_acceptance')
#         if mail_template_id:
#             self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True,context=self.env.context)
#         self.write({'state':'moa_accepted'})
        eoi_obj = self.env['eoi.moa']
        eoi_search = eoi_obj.search([('learning_programme_id','=',self.id)])
        if not eoi_search.attach_moa:
            raise Warning(_('Please attach MOA before Approval!'))
        eoi_search.write({'status':'accepted'})  
        
        self.write({'accept_moa':True})  
#         if not self.learner_ids :
#             raise Warning(_('Please enter Learners!'))
#         for learner_data in self.learner_ids: 
#             if not (learner_data.name or learner_data.surname or learner_data.identity_number or learner_data.citizen_residential_status) :
#                 raise Warning(_('Please enter mandatory informations for learners before loading!'))  
        return True
    
    @api.multi
    def action_load_learners(self):
        current_date = datetime.now()
        app_learner_count = 0
        for enroll_data in self.enroll_project_ids:
            app_learner_count += enroll_data.no_of_persons
            if enroll_data.project_id:
                project_obj= self.env['project.project'].search([('id','=',enroll_data.project_id.id)])
                learner_extension = self.env['partner.project.rel'].search([('emp_project_id','=',project_obj.id),('load_learner_ext_request','=',True),('employer_id','=',self.employer_id.id)])
                if not (learner_extension) :
                    if str(current_date) > project_obj.load_learner_end_date : 
                        raise Warning(_('Please apply to load learner extension for project %s !')%(project_obj.name))
                if learner_extension and not (learner_extension.load_learner_ext_date):
                    raise Warning(_('Please contact HWSETA to load learner extension date for project %s !')%(project_obj.name))                
        if not self.learner_ids :
            raise Warning(_('Please enter Learners!'))
        learner_count = 0
        for learner_data in self.learner_ids:
            learner_count += 1
            if not (learner_data.name or learner_data.surname or learner_data.identity_number or learner_data.citizen_residential_status) :
                raise Warning(_('Please enter mandatory informations for learners before loading!'))
        if learner_count > app_learner_count:
            raise Warning(_('Sorry! You cant load more learners than approved'))
        ##### Code for creating learners record.
        learner_obj = self.env['hr.employee']
        for learner_data in self.learner_ids:
            ## Checking whether to include this learner while loading.
            if learner_data.select_learner_info == True and learner_data.loaded == False and learner_data.current_status == 'active':
                ## Checking Whether learner belongs to multiple projects or not
                project_types_ids = [enrolled_proj.project_type.id for enrolled_proj in learner_data.proj_enrolled_ids]
                len_project_types = len(set(project_types_ids))
                if len_project_types > 1:
                    raise Warning(_('Learner %s %s can not enroll for more than one Project Type!')%(learner_data.name,learner_data.surname))
                ## Checking whether learner exist earlier or not
                learner_exist = learner_obj.search([('rsa_identity_no','=',learner_data.identity_number),('is_learner','=',True)])
                employer_list = [(0,0,{
                                       'employer_id' : self.employer_id.id, 
                                       'sdl_no': self.employer_id.employer_sdl_no, 
                                       'seta_id' : self.employer_id.employer_seta_id and self.employer_id.employer_seta_id.id, 
                                       'registration_number' : self.employer_id.employer_registration_number, 
                                       'state':'draft'
                                       })]
                employer_done = False
                agreement_done = False
                if learner_exist:
                    for employer in learner_exist.employer_ids:
                        if employer.state != 'draft':
                            employer_done = True
                    for agree in learner_exist.agreement_ids:
                        if agree.state != 'new':
                            agreement_done = True
                    if employer_done == True and agreement_done == True:
                        learner_exist.write({
                                             'latest_employer':self.employer_id.id,
                                             'employer_ids' : employer_list,
                                             })
                    else :
                        raise Warning(_('Please complete asessment for learner %s')%(learner_exist.name))
                else:
                    seq_no=self.env['ir.sequence'].get('learner.registration.sequence')
                    attachments = [(0,0,{'name':attachment.name,'data':attachment.data}) for attachment in learner_data.learner_attachment_ids]
                    project_list = [(0,0,{
                                          'project_id' : project_data.project_id and project_data.project_id.id,
                                          'project_type_id' : project_data.project_id and project_data.project_id.project_types and project_data.project_id.project_types.id,
                                          'project_budget' : project_data.project_id and project_data.project_id.budget_applied,
                                          'qualification_ids' : [(6,0,[qualification_id.id for qualification_id in project_data.project_id.qualification_ids])],
                                          }) for project_data in learner_data.proj_enrolled_ids]
                    learner_dict = {
                                    'name' : learner_data.name,
                                    'work_email' : learner_data.work_email,
                                    'work_phone' : learner_data.work_phone,
                                    'equity':learner_data.equity,
                                    'marital':learner_data.marital,
                                    'disability_status':learner_data.disability_status,
                                    'passport_id':learner_data.passport_id,
                                    'id_document':learner_data.id_document.id,
                                    'initials':learner_data.initials,
                                    'seeing_rating_id':learner_data.seeing_rating_id,
                                    'hearing_rating_id':learner_data.hearing_rating_id,
                                    'walking_rating_id':learner_data.walking_rating_id,
                                    'remembering_rating_id':learner_data.remembering_rating_id,
                                    'statssa_area_code':learner_data.statssa_area_code,
                                    'popi_act_status_date':learner_data.popi_act_status_date,
                                    'communicating_rating_id':learner_data.communicating_rating_id,
                                    'self_care_rating_id':learner_data.self_care_rating_id,
                                    'last_school_emis_no':learner_data.last_school_emis_no,
                                    'last_school_year':learner_data.last_school_year,
                                    'popi_act_status_id':learner_data.popi_act_status_id,
                                    'date_stamp':learner_data.date_stamp,
                                    'financial_year' : learner_data.financial_year,
                                    'business_tel_no' : learner_data.business_tel_no,
                                    'country_id' : learner_data.nationality_id and learner_data.nationality_id.id,
                                    'person_alternate_id' : learner_data.alternate_identity_no,
                                    'identification_id' : learner_data.identity_number,
                                    'maiden_name' : learner_data.maiden_name,
                                    'person_title' : learner_data.person_title,
                                    'person_last_name' : learner_data.surname,
                                    'certificate_no' : learner_data.certificate_no,
                                    'rsa_identity_no' : learner_data.rsa_identity_no,
                                    'learner_reg_no' : seq_no,
                                    'home_language_code' : learner_data.home_language and learner_data.home_language.id,
                                    'method_of_communication' : learner_data.method_of_communication,
                                    'learner_status' : learner_data.learner_status,
                                    'person_birth_date' : learner_data.date_of_birth,
                                    'record_last_updated' : learner_data.record_last_updated,
                                    'status_comments' : learner_data.status_comments,
                                    'citizen_resident_status_code' : learner_data.citizen_residential_status,
                                    'gender' : learner_data.gender,
                                    'dissability' : learner_data.dissability,
                                    'highest_education' : learner_data.highest_education,
                                    'person_fax_number' : learner_data.fax_no,
                                    'cell' : learner_data.cell,
                                    'status_reason' : learner_data.status_reason,
                                    'wsp_year' : learner_data.wsp_year,
                                    'status_effective_date' : learner_data.status_effective_date,
                                    'last_updated_operator' : learner_data.last_updated_operator,
                                    'learner_attachment_ids' : attachments,
                                    'is_learner' : True,
                                    'seta_elements' : True,
                                    'employer_ids' : employer_list,
                                    'latest_employer' : self.employer_id.id,
                                    'learning_programme_id' : self.id,
                                    'project_ids' : project_list,
                                    ## Updating Home Address
                                    'person_home_address_1' : learner_data.learner_home_address_1,
                                    'person_home_address_2' : learner_data.learner_home_address_2,
                                    'person_home_address_3' : learner_data.learner_home_address_3,
                                    'person_home_suburb' : learner_data.learner_home_suburb and learner_data.learner_home_suburb.id,
                                    'person_home_city' : learner_data.learner_home_city and learner_data.learner_home_city.id,
                                    'person_home_province_code' : learner_data.learner_home_province_code and learner_data.learner_home_province_code.id,
                                    'country_home' : learner_data.learner_country_home and learner_data.learner_country_home.id,
                                    'person_home_zip' : learner_data.learner_home_zip,
                                    ## Updating Postal Address
                                    'person_postal_address_1' : learner_data.learner_postal_address_1,
                                    'person_postal_address_2' : learner_data.learner_postal_address_2,
                                    'person_postal_address_3' : learner_data.learner_postal_address_3,
                                    'person_postal_suburb' : learner_data.learner_postal_suburb and learner_data.learner_postal_suburb.id,
                                    'person_postal_city' : learner_data.learner_postal_city and learner_data.learner_postal_city.id,
                                    'person_postal_province_code' : learner_data.learner_postal_province_code and learner_data.learner_postal_province_code.id,
                                    'country_postal' : learner_data.learner_country_postal and learner_data.learner_country_postal.id,
                                    'person_postal_zip' : learner_data.learner_postal_zip,  
                                    'same_as_home' : learner_data.same_as_home,
                                    'socio_economic_status':learner_data.employee_type
                                    }
                    learner_data.write({'learner_reg_no':seq_no})
                    hr_obj = learner_obj.create(learner_dict)
                    ## For Learner Track Count in Final Approved State
                    for project_data in self.enroll_project_ids:
                        fin_empl = self.final_empl or ','
                        fin_non_empl = self.final_non_empl or ','
                        self.write({'final_empl':fin_empl+','+str(project_data.employed), 'final_non_empl':fin_non_empl+','+str(project_data.non_employed)})
                    #merging code
                    count = 0
                    #for learner_info in self.learner_ids:
                    ## Checking whether to include this learner while loading.
                    if learner_data.select_learner_info == True and learner_data.loaded == False:
                        count += 1
                        ## Checking whether learner exist earlier or not
                        learner_exist = learner_obj.search([('rsa_identity_no', '=', learner_data.identity_number)])
                        provider_done = False
                        if learner_exist:
                            for provider in learner_exist.learner_pro_ids:
                                if provider.state != 'new':
                                    provider_done = True
                        if provider_done :
                            provider_list = [(0,0,{
                                                        'name' : project_data.provider_id and project_data.provider_id.name,
                                                        'provider_id' : project_data.provider_id and project_data.provider_id.id,
                                                        'provider_accreditation_num' : project_data.provider_id and project_data.provider_id.provider_accreditation_num,
                                                        'provider_etqe_id' : project_data.provider_id and project_data.provider_id.provider_etqe_id,
                                                        'state' : 'new'
                                                        })for project_data in learner_data.proj_enrolled_ids]
                            learner_exist.write({'learner_pro_ids':provider_list})
                            learner_data.write({'loaded':True})
                            report_obj = self.env['report'].get_pdf(learner_exist,'hwseta_sdp.report_learner_agreement')
                        else:
                            #learner_data = learner_obj.search([('learner_reg_no', '=',learner_data.learner_reg_no)])
                            # Providers to which learner belongs
                            provider_list = [(0,0,{
                                                    'name' : project_data.provider_id and project_data.provider_id.name,
                                                    'provider_id' : project_data.provider_id and project_data.provider_id.id,
                                                    'provider_accreditation_num' : project_data.provider_id and project_data.provider_id.provider_accreditation_num,
                                                    'provider_etqe_id' : project_data.provider_id and project_data.provider_id.provider_etqe_id,
                                                    'state' : 'new'
                                                    }) for project_data in learner_data.proj_enrolled_ids]
                            learner_data.write({'learner_pro_ids':provider_list})
                            report_obj = self.env['report'].get_pdf(hr_obj,'hwseta_sdp.report_learner_agreement')
                            learner_data.write({'attached_report':base64.encodestring(report_obj),'loaded':True})
                    ## Marking process as complete once all learners are loaded.
                    loaded_learners = 0
                    for learner_data in self.learner_ids:
                        if learner_data.loaded :
                            loaded_learners += 1
                    if loaded_learners == len(self.learner_ids) :
                        eoi_status_obj = self.env['eoi.status'].create({'user_id': self._uid,
                                                        'state': 'final_approval',
                                                        'eoi_id': self.id,
                                                        'comment': self.comment,
                                                        'status': 'Completed',
                                                      })
                        self.write({'learner_loaded':True,'state':'final_approval', 'enroll_status':'Completed'})
        return True

learning_programme()
    

class partner_project_rel(models.Model):
    _inherit = 'partner.project.rel'
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ Override read_group to filter record count based on logged SDF """
        if self.env.user.id != 1 and self.env.user.sdf_id:
            eoi_ids = []
            self._cr.execute("select id from partner_project_rel where create_uid='%s'" % (self.env.user.id,))
            eoi_ids = map(lambda x:x[0], self._cr.fetchall())
            domain.append(('id', 'in', eoi_ids))
        return super(partner_project_rel, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
#     emp_project_id = fields.Many2one('project.project', string="Emp Project",track_visibility='onchange')
#     eoi_id_reference = fields.Char(related='emp_project_id.name', store=True, readonly=True, copy=False)
    eoi_id_reference_new = fields.Char(related='emp_project_id.eoi_id_reference_invisible', store=True, readonly=True, copy=False)

partner_project_rel()

class eoi_status(models.Model):
    _name = 'eoi.status'
    
    user_id = fields.Many2one('res.users', string='Name')
    state = fields.Selection([
            ('pending', 'Pending'),
            ('submitted', 'Submitted'),
            ('evaluated', 'Evaluated'),
            ('recommended', 'Recommended'),
            ('conditional_approval', 'Conditional Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('final_approval', 'Completed'),
        ], string='State', index=True, readonly=True, default='pending',
        track_visibility='onchange', copy=False)
    status = fields.Char("Status")
    s_date = fields.Datetime(string='Date', default=datetime.now())
    update_date = fields.Datetime(string='Update Date', default=datetime.now())
    comment = fields.Char(string='Comment')
    eoi_id = fields.Many2one('learning.programme', string='Learnership')
    
eoi_status()