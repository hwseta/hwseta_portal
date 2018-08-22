from openerp import models, fields, api, _
# from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.exceptions import Warning
# from openerp import tools
from datetime import datetime
import os
import base64
# import string
# import random
import calendar
import random

class skill_plan(models.Model):
    _name = 'skill.plan'
    
    name = fields.Char(string='Skills')
    
skill_plan()

def validate_phone_mobile(phone_no):
    
    return True

class project_indicator(models.Model):
    _name = 'project.indicator'
    
    name = fields.Char(string="Name")

    _sql_constraints = [('project_indicator_uniq', 'unique(name)',
            'Project Indicator must be unique!'),]      
    
project_indicator()

class hwseta_project_category(models.Model):
    _name = 'hwseta.project.category'
    _rec_name = 'category_name'
    
    category_type = fields.Selection([('18.1','Employed Learners (18.1)'),('18.2','Unemployed Learners (18.2)')], string="Category Type")
    category_name = fields.Char(string="Category Name")
    
    @api.model
    def create(self, vals):
        res = super(hwseta_project_category, self).create(vals)
        project_category_lst = self.env['hwseta.project.category'].search([('category_name','=',res.category_name),('category_type','=',res.category_type)])
        if len(project_category_lst) > 1:
            raise Warning(_('You can not create duplicate category name for same category type!'))
        return res
hwseta_project_category()

class account_account(models.Model):
    _inherit = 'account.account'
    
    is_project_type = fields.Boolean("Project Type")
    
account_account()

class hwseta_project_types(models.Model):
    _name = 'hwseta.project.types'
    _inherit = 'mail.thread'
    
    @api.multi
    def onchange_default_project_type(self,name):
        res = {}
        project_type = [ project_type.id for project_type in self.env['account.account'].search([('is_project_type','=',True)])]
        if name :
            project_code = self.env['account.account'].search([('id','=',name)])
            res.update({'value':{'code':project_code.code}})
        res.update({'domain':{'name':[('id','in',project_type)]}})
        return res    
    
    @api.model
    def _default_budget(self):
        ## Getting correct admin configuration accourding to fiscal year.
        current_date = datetime.now().date()
        fiscal_year = False
        for fiscalyear_data in self.env['account.fiscalyear'].search([]) :
            if current_date >= datetime.strptime(fiscalyear_data.date_start,'%Y-%m-%d').date() and current_date <= datetime.strptime(fiscalyear_data.date_stop,'%Y-%m-%d').date() :
                fiscal_year = fiscalyear_data.id
#         if not fiscal_year :
#             raise Warning(_('No Fiscal Year defined for the current year!'))
        leavy_income_config_data = self.env['leavy.income.config'].search([('wsp_financial_year','=',fiscal_year)], limit=1)
        if leavy_income_config_data :
            total_balance = leavy_income_config_data.project_budget_acc and leavy_income_config_data.project_budget_acc.balance or 0
            if total_balance < 0 :
                total_balance = total_balance * (-1)
            if total_balance :
                ## Calculating already allotted balance in other project types.
                total_applied_budget = 0
                for project_type in self.search([]) :
                    total_applied_budget += project_type.applied_budget
                available_budget = total_balance - total_applied_budget
                if available_budget <= 0 :
                    available_budget = 0
                return available_budget
            else :
                return total_balance
            
    @api.one
    @api.depends(
                 'app_target_employed',
                 'app_target_unemployed',
                 )
    def _get_total_app_target(self):
        self.app_target_employed_unemployed = (self.app_target_employed + self.app_target_unemployed)
        
    @api.one
    @api.depends(
                 'app_target_achieved_employed',
                 'app_target_achieved_unemployed',
                 )
    def _get_total_app_target_achieved(self):
        self.app_target_achieved_employed_unemployed = (self.app_target_achieved_employed + self.app_target_achieved_unemployed)   

    @api.one
    def _get_app_target_achieved_employed(self):
#         project_type_id = self.env['hwseta.project.types'].search([('name','=',self.name.id)])
        enroll_project = self.env['enrollment.projects'].search([('project_types','=',self.id),('state','=','approved')])
        total_employed = 0
        for employed in enroll_project :
            total_employed += employed.employed    
        self.app_target_achieved_employed = total_employed 
        
    @api.one
    def _get_app_target_achieved_unemployed(self):
#         project_type_id = self.env['hwseta.project.types'].search([('name','=',self.name.id)])
        enroll_project = self.env['enrollment.projects'].search([('project_types','=',self.id),('state','=','approved')])
        total_unemployed = 0
        for unemployed in enroll_project :
            total_unemployed += unemployed.non_employed
        self.app_target_achieved_unemployed = total_unemployed       
        
    @api.one
    @api.depends(
                 'app_target_employed_unemployed',
                 'app_target_achieved_employed_unemployed',
                 )
    def _compute_variance(self):
        if self.app_target_employed_unemployed !=0:
            app_variance = ((float(self.app_target_achieved_employed_unemployed)/float(self.app_target_employed_unemployed))*100)
            if app_variance != 0:
                self.variance = (100- app_variance)                          
    
    code = fields.Char(string="Code")
    name = fields.Many2one('account.account',string="Name")
    budget = fields.Float(string='Available Discretionary budget', default=_default_budget)
    rem_budget = fields.Float(string='Rem Budget')
    applied_budget = fields.Float(string='Project Type Budget')
    fees_employed = fields.Many2many('fees.structure', 'project_type_fees_emp_rel', 'project_type_id', 'fees_id', string='Funding Structure 18.1')
    fees_unemployed = fields.Many2many('fees.structure', 'project_type_fees_unemp_rel', 'project_type_id', 'fees_id', string='Funding Structure 18.2')
    project_ids = fields.One2many('hwseta.project','project_type_id',string="Projects")
    project_document_ids = fields.One2many('hwseta.project.document','project_type_id',string="Project Documents") 
    seta_funding_year = fields.Many2one('account.fiscalyear', string='Funding Year')
    app_target_employed = fields.Integer(string="App Target 18.1")
    app_target_unemployed = fields.Integer(string="App Target 18.2")
    app_target_employed_unemployed = fields.Integer(compute='_get_total_app_target',string="Total App Target")
    app_target_achieved_employed = fields.Integer(compute='_get_app_target_achieved_employed',string="App Target Achieved 18.1")
    app_target_achieved_unemployed = fields.Integer(compute='_get_app_target_achieved_unemployed',string="App Target Achieved 18.2")
    app_target_achieved_employed_unemployed = fields.Integer(compute='_get_total_app_target_achieved',string="Total App Target Achieved ")
    variance = fields.Float(string="Variance",compute='_compute_variance')
    project_indicator_id = fields.Many2one('project.indicator',string="Indicator")
    project_type_description=fields.Html("Description")  
    project_type_terms_condition = fields.Many2one('ir.attachment',string="Terms and Conditions")
    
    @api.model
    def create(self, vals):
        res = super(hwseta_project_types, self).create(vals)
        project_types = [types.id for types in self.env['hwseta.project.types'].search([('name','=',res.name.id),('seta_funding_year','=',res.seta_funding_year.id)])]
        if len(project_types) > 1:
            raise Warning(_('You can not create multiple Project type for the Financial year %s !')%(res.seta_funding_year.name))
        if res.budget == 0 and res.applied_budget :
            raise Warning(_('You dont have more budget to allocate!'))
        if res.applied_budget > res.budget :
            raise Warning(_('You can not apply more budget than exists!'))
        if res.project_ids :
            total_budget = 0.0
            total_employed = 0
            total_unemployed = 0            
            for project in res.project_ids :
                if project.target_employed == 0 and project.target_unemployed == 0:
                    raise Warning(_('Please add Target 18.1 or Target 18.2 for %s')%project.name.name)
                total_budget += project.budget_applied
                total_employed += project.target_employed
                total_unemployed += project.target_unemployed      
            if total_budget > res.applied_budget :
                raise Warning(_('You can not apply more budget than Project type budget exists!'))
            if total_employed > res.app_target_employed :
                raise Warning(_('You can not apply more Employed than App target Employed exists!'))
            if total_unemployed > res.app_target_unemployed :
                raise Warning(_('You can not apply more Unemployed than App Target Unemployed exists!'))            
        
        return res
    
    @api.multi
    def write(self, vals):
        res = super(hwseta_project_types, self).write(vals)
        if self.budget == 0 and vals.get('applied_budget',False) :
            raise Warning(_('You dont have more budget to allocate!'))
        if self.applied_budget > self.budget or vals.get('applied_budget',False) > self.budget :
            raise Warning(_('You can not apply more budget than exists!'))
        if self.project_ids :
            total_budget = 0.0
            total_employed = 0
            total_unemployed = 0
            for project in self.project_ids :
                if project.target_employed == 0 and project.target_unemployed == 0:
                    raise Warning(_('Please add Target 18.1 or Target 18.2 for %s')%project.name.name)
                total_budget += project.budget_applied
                total_employed += project.target_employed
                total_unemployed += project.target_unemployed
            if total_budget > self.applied_budget :
                raise Warning(_('You can not apply more budget than Project type budget exists!'))
            if total_employed > self.app_target_employed :
                raise Warning(_('You can not apply more Employed than App target Employed exists!'))
            if total_unemployed > self.app_target_unemployed :
                raise Warning(_('You can not apply more Unemployed than App Target Unemployed exists!'))
            
        return res
    
hwseta_project_types()

class hwseta_project(models.Model):
    _name = 'hwseta.project'
    
    @api.multi
    @api.onchange('name')
    def onchange_project(self):
        res = {}
        
        project_type_id = self.project_type_id.name
        if not project_type_id:
            raise Warning(_('Please Select Project Type!'))
        project_type = [ project_type.id for project_type in self.env['account.account'].search([('parent_id','=',project_type_id.id)])]
        res.update({'domain':{'name':[('id','in',project_type)]}})
        return res
        
#     name = fields.Char('Name')
    name = fields.Many2one("account.account",string="Projects",track_visibility='onchange')
    project_type_id = fields.Many2one('hwseta.project.types',string="Project Type")
    budget_applied = fields.Float("Budget Allocated")
    target_employed = fields.Integer("Target 18.1")
    target_unemployed = fields.Integer("Target 18.2")
    project_approval = fields.Many2one('ir.attachment',string="Project Approval")

    @api.multi
    @api.onchange('target_employed')
    def onchange_taget_employed(self):
        if self.target_employed > 0:
            self.target_unemployed = 0

    @api.multi
    @api.onchange('target_unemployed')
    def onchange_taget_unemployed(self):
        if self.target_unemployed > 0:
            self.target_employed = 0

class hwseta_project_document(models.Model):
    _name =  'hwseta.project.document'
    
    name = fields.Many2one('project.document',string="Document Name")
    required = fields.Boolean("Document Required")
    project_type_id=fields.Many2one('hwseta.project.types',string="Project Type")

hwseta_project_document()


class document_library(models.Model):
    _name = 'document.library'
    
#     @api.multi
#     def get_attach_id(self, msg, file_path):
#         ''' This Method get the file from given location in odoo and creates
#             attachment and finally returns attachment id.
#         '''
#         attach_obj = self.env['ir.attachment']
#         try :   
#             file_doc = open(file_path,"r")
#             file_get = base64.encodestring(file_doc.read())
#         except IOError as e :
#             raise Warning(_('I/O Error %s : %s')%(e.errno, e.strerror))
#         return file_get
    
    
    @api.model
    def default_get(self, fields_list):
        ''' This method will set the documents by default within document library. '''
        res = super(document_library, self).default_get(fields_list)
        ## OFO Codes
#         attach_ofo = self.get_attach_id('OFO Codes', os.path.abspath('openerp/addons/hwseta_sdp/static/src/doc/ofo.pdf'))
#         attach_ofo = self.get_attach_id('OFO Codes', '/opt/odoo/odoo-server/openerp/addons/hwseta_sdp/static/src/doc/ofo.pdf')
        ## Authorisation Page for less than 50 Employees.
#         attach_auth1 = self.get_attach_id('Auth. Page (less than 50)', os.path.abspath('openerp/addons/hwseta_sdp/static/src/doc/auth_page_less_fifty.pdf'))
#         attach_auth1 = self.get_attach_id('Auth. Page (less than 50)', '/opt/odoo/odoo-server/openerp/addons/hwseta_sdp/static/src/doc/auth_page_less_fifty.pdf')
        ## Authorisation Page for more than 50 Employees.
#         attach_auth2 = self.get_attach_id('Auth. Page (more than 50)', os.path.abspath('openerp/addons/hwseta_sdp/static/src/doc/auth_page_more_fifty.pdf'))
#         attach_auth2 = self.get_attach_id('Auth. Page (more than 50)', '/opt/odoo/odoo-server/openerp/addons/hwseta_sdp/static/src/doc/auth_page_more_fifty.pdf')
        ## Training Guide.
#         attach_manual = self.get_attach_id('Training Manual', os.path.abspath('openerp/addons/hwseta_sdp/static/src/doc/train_guide.pdf'))
#         attach_manual = self.get_attach_id('Training Manual', '/opt/odoo/odoo-server/openerp/addons/hwseta_sdp/static/src/doc/train_guide.pdf')
        ## WSP Template.
#         wsp_template = self.get_attach_id('WSP Template', '/opt/odoo/odoo-server/openerp/addons/hwseta_sdp/static/src/doc/Planned.xlsx')
#         wsp_template = self.get_attach_id('WSP Template', os.path.abspath('openerp/addons/hwseta_sdp/static/src/doc/Planned.xlsx'))
        ## ATR Template.
#         atr_template = self.get_attach_id('WSP Template', os.path.abspath('openerp/addons/hwseta_sdp/static/src/doc/Actual.xlsx'))
#         atr_template = self.get_attach_id('WSP Template', '/opt/odoo/odoo-server/openerp/addons/hwseta_sdp/static/src/doc/Actual.xlsx')
        res.update({
                    'name' : 'Documents',
#                     'ofo_file' : attach_ofo,
                    'ofo_file_name' : 'ofo.pdf',
#                     'auth_page_less_fifty' : attach_auth1, 
                    'auth_page_name1' : 'auth_page_less_fifty.pdf',
#                     'auth_page_more_fifty' : attach_auth2, 
                    'auth_page_name2' : 'auth_page_more_fifty.pdf',
#                     'training_guide' : attach_manual,
                    'training_guide_name' : 'train_guide.pdf',
#                     'wsp_template' : wsp_template,
                    'wsp_template_name' : 'Planned.xlsx',
#                     'atr_template' : atr_template,
                    'atr_template_name' : 'Actual.xlsx'
                    })
        return res
    
    name = fields.Char(string='Document')
    ofo_file = fields.Binary(string='OFO Codes')
    ofo_file_name = fields.Char(string='OFO File Name')
    auth_page_less_fifty = fields.Binary(string='Authorisation Page (less than 50 Employees)')
    auth_page_name1 = fields.Char(string='Auth Page Name1')
    auth_page_more_fifty = fields.Binary(string='Authorisation Page (more than 50 Employees)')
    auth_page_name2 = fields.Char(string='Auth Page Name2')
    training_guide = fields.Binary(string='Training Guide')
    training_guide_name = fields.Char(string='Training Guide Name')
    wsp_template = fields.Binary(string='WSP Template')
    wsp_template_name = fields.Char(string='WSP Template Name')
    atr_template = fields.Binary(string='ATR Template')
    atr_template_name = fields.Char(string='ATR Template Name')
    
    @api.model
    def create(self, vals):
        res = super(document_library, self).create(vals)
        return res
    
document_library()

class learner_agree(models.Model):
    _name = 'learner.agree'
    
    seq_no = fields.Char(string='Agreement No')
    learner_reg_no = fields.Char(string='Learner Reg No')
    attached_report = fields.Binary(string="Agreement No")
    identity_number = fields.Char(string='Identity Number')
    learner_id = fields.Many2one('hr.employee', string='Learner')
    state = fields.Selection([('new','New'),('done','Done')], string="status")
    
learner_agree()

class learner_project_rel(models.Model):
    _name = 'learner.project.rel'
    
    project_id = fields.Many2one('project.project',string='Project Details')
    learner_id = fields.Many2one('hr.employee', string='Learner', domain=[('is_learner','=',True)])
    project_type_id = fields.Many2one('hwseta.project.types', string="Project")
    project_budget = fields.Float(string='Budget')
#     qualification_id = fields.Many2one('provider.qualification', string='Qualification')
    #Multiple qualification per projects
    qualification_ids = fields.Many2many('provider.qualification', 'learner_qualification_rel', 'learner_id', 'qualification_id', string='Qualifications')
    
learner_project_rel()

## SDF Related fields will be accessible here from hwseta_person module.
class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    @api.model
    def default_get(self, fields_list):
        res = super(hr_employee, self).default_get(fields_list)
        context =self._context.copy()
        if context and context.get('is_learner_from_assessment',False):
            res.update({'is_learner_from_assessment' : True, 'seta_elements':True, 'is_learner':True})
        return res
    
    
    employer_ids = fields.One2many('sdf.employer.rel', 'sdf_prof_id', string='Employers')
    sdf_reg_id = fields.Many2one('sdf.register', string='SDF Register ID')
    latest_employer = fields.Many2one('res.partner', string="Latest Employer")
    agreement_ids = fields.One2many('learner.agree','learner_id', string='Agreement')
    learning_programme_id = fields.Many2one('learning.programme', string='Learning Programme')
    project_ids = fields.One2many('learner.project.rel','learner_id', string='Projects')
    
    @api.multi
    def country_for_province(self, province):
        state = self.env['res.country.state'].browse(province)
        return state.country_id.id
    
    @api.multi
    def onchange_work_province(self, province):
        if province:
            country_id = self.country_for_province(province)
            return {'value': {'work_country': country_id }}
        return {}
    
    @api.multi
    def onchange_home_province(self, province):
        if province:
            country_id = self.country_for_province(province)
            return {'value': {'country_home': country_id }}
        return {}
    
    @api.multi
    def onchange_postal_province(self, province):
        if province:
            country_id = self.country_for_province(province)
            return {'value': {'country_postal': country_id }}
        return {}
    
    @api.model
    def create(self, vals):
        user = self.env['res.users'].browse(self._uid)
        res = super(hr_employee, self).create(vals)
        related_user_data = False
        if res.is_learner:
            seq_no=self.env['ir.sequence'].get('learner.registration.sequence')
            res.write({'learner_reg_no':seq_no,'seta_elements':True})
        if not res.is_learner and not vals.get('already_registered') and not res.is_sdf:
            group_obj = self.env['res.groups']
            ## Code for Random Numbers for Password Generation.
#             chars = string.letters + string.digits
#             pwdSize = 15
#             passwd = ''.join((random.choice(chars)) for x in range(pwdSize))
            ##
            if res.work_email:
                duplicate_match = self.env['res.users'].search([('login','=',res.work_email)])
            elif res.name:
                duplicate_match = self.env['res.users'].search([('login','=',res.name+'@gmail.com')])
            if duplicate_match:
                if duplicate_match.assessor_moderator_id:
                    raise Warning(_('Sorry!! Assessessor/Moderator is already registered with  %s email Id !')%(res.work_email))

                mainlist = []
                group_data = group_obj.search(['|', ('name', '=', 'Portal'), ('name', '=', 'Assessors')])
                for data in group_data:
                    tup1 = (4, data.id)
                    mainlist.append(tup1)

                res.write({'user_id' : duplicate_match.id})
                duplicate_match.write({'assessor_moderator_id':res.id,'groups_id':mainlist,})
                return res
            else:    
                related_user_data = self.env['res.users'].create({
                                                                  'name' : res.name,
                                                                  'image': res.image_medium,
                                                                  'login' : res.work_email, 
                                                                  'password':res.password, 
                                                                  'assessor_moderator_id':res.id,
                                                                  'internal_external_users':'Assessors',
                                                                  })
                mainlist = []
                group_data = group_obj.search(['|', ('name', '=', 'Portal'), ('name', '=', 'Assessors')])
                for data in group_data:
                    tup1 = (4, data.id)
                    mainlist.append(tup1)                
                res.write({'user_id' : related_user_data.id})
                related_user_data.partner_id.write({'email':res.work_email})
                related_user_data.write({'groups_id':mainlist, })
                
        if res.is_sdf == True:
            ## SDF User Creation after creating SDF.
            group_list = [] 
            group_obj = self.env['res.groups']
            ## Applying Portal and SDF groups to SDF related user.
            group_data = group_obj.search(['|',('name','=','Portal'),('name','=','SDF')])
            for data in group_data:
                tup = (4,data.id)
                group_list.append(tup)
            ## Removing Contact Creation and Employee group from SDF related user.   
            rem_group_data = group_obj.search(['|',('name', '=', 'Contact Creation'),('name','=','Employee')])
            for data in rem_group_data:
                tup = (3,data.id)
                group_list.append(tup)  
            
            related_user_data = self.env['res.users'].create({
                                                                  'name' : res.name,
                                                                  'image': res.image_medium,
                                                                  'login' : res.work_email, 
                                                                  'password':res.password, 
                                                                  'internal_external_users':'SDF',
                                                                  })
            related_user_data.write({'groups_id':group_list,'sdf_id':res.id})
            res.write({'user_id' : related_user_data.id})
            ## Employer having the rights to create SDF and needs no approval.
            partner = user.partner_id
            if partner.employer :
                tracking_obj = self.env['sdf.tracking']
                ## Checking if already entry occurs
                register_data = res.sdf_reg_id
                track_data = tracking_obj.search([('sdf_register_id','=',register_data.id)])
                if not track_data :
                    track_dict = {
                       'sdf_id':res.id,
                       'status':'approved',
                       'partner_id':partner.id,
                       'sdf_approved_denied':True,
                       }
                    tracking_obj.create(track_dict)
                self.env['sdf.employer.rel'].create({'employer_id':partner.id,'sdf_prof_id':res.id})
        return res
    
    @api.multi
    def write(self, vals):
        res = super(hr_employee, self).write(vals)
        sdl_number = []
        for employer in self.employer_ids :
            if employer.sdl_no in sdl_number :
                raise Warning(_('You can not add same employer multiple time!!.'))
            else :
                sdl_number.append(employer.sdl_no)
        return res
    
    
hr_employee()

class res_users(models.Model):
    _inherit = 'res.users'
    
    sdf_id = fields.Many2one('hr.employee', string='SDF')
    assessor_moderator_id = fields.Many2one('hr.employee', string='Assessor Moderator')
#     sdf_ids = fields.Many2many('res.users','res_sdf_users_rel','id','sdf_id','Previous SDF')
    internal_external_users = fields.Selection([('SDF','SDF'),('Providers','Providers'),('Assessors','Assessors'),\
                                 ('Moderators','Moderators'),('Employer','Employer'),('Administrator','Administrator'),\
                                 ('Internal','Internal'),('Unknown','Unknown')], string = 'Users', default = "Internal")
res_users()

class fees_structure(models.Model):
    _name = 'fees.structure'
    
    name = fields.Char(string='Name')
    related_product = fields.Many2one('product.product', string='Related Product')
    project_emp_id = fields.Many2one('project.project', string='Related Project')
    project_unemp_id = fields.Many2one('project.project', string='Related Project')
    
fees_structure()

class ir_attachment(models.Model):
    _inherit = 'ir.attachment'
    
    @api.model
    def default_get(self, fields_list):
        res = super(ir_attachment, self).default_get(fields_list)
        context =self._context.copy()
        if context and context.get('model',False) == 'sdf.register' :
            res.update({'name' : 'ID Document/Passport Upload'})
        return res 
    
    @api.model
    def create(self, vals):
        context = self._context.copy()
        if context and context.get('model',False) == 'sdf.register' :
            vals.update({'name' : vals.get('datas_fname',False)})
        return super(ir_attachment, self).create(vals)
    
    @api.v7
    def check(self, cr, uid, ids, mode, context=None, values=None):
        """Restricts the access to an ir.attachment, according to referred model
        In the 'document' module, it is overriden to relax this hard rule, since
        more complex ones apply there.
        """
        res_ids = {}
        require_employee = False
        if ids:
            if isinstance(ids, (int, long)):
                ids = [ids]
            cr.execute('SELECT DISTINCT res_model, res_id, create_uid FROM ir_attachment WHERE id = ANY (%s)', (ids,))
            for rmod, rid, create_uid in cr.fetchall():
                if not (rmod and rid):
                    if create_uid != uid:
                        require_employee = True
                    continue
                res_ids.setdefault(rmod,set()).add(rid)
        if values:
            if values.get('res_model') and values.get('res_id'):
                res_ids.setdefault(values['res_model'],set()).add(values['res_id'])

        ima = self.pool.get('ir.model.access')
        for model, mids in res_ids.items():
            # ignore attachments that are not attached to a resource anymore when checking access rights
            # (resource was deleted but attachment was not)
            if not self.pool.get(model):
                require_employee = True
                continue
            existing_ids = self.pool[model].exists(cr, uid, mids)
            if len(existing_ids) != len(mids):
                require_employee = True
            ima.check(cr, uid, model, mode)
            self.pool[model].check_access_rule(cr, uid, existing_ids, mode, context=context)
            
ir_attachment()

class sdf_register(models.Model):
    _inherit = 'sdf.register'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        user = self._uid
        ##
        user_obj = self.env['res.users']
        user_groups = user_obj.browse(user).groups_id
        for group in user_groups:    
            if group.name == "SDP Manager":
                return super(sdf_register, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            if group.name == "Provincial Manager" or group.name == "Provincial Officer" :
                user_province_ids = [province_data.id for province_data in self.env['res.users'].browse(self._uid).province_ids]
                if user_province_ids :
                    args.append(('work_province','in',user_province_ids))
#                 return super(sdf_register, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
#             if group.name in ['Financial Manager','Accountant','Invoicing & Payments']:
#                 return super(sdf_register, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
        ##
        employee_data = self.env['hr.employee'].search([('user_id','=',user)])
        if employee_data.is_sdf == True:
            user_data = self.env['res.users'].browse(user)
            args.append(('related_sdf','=',user_data.sdf_id.id))
        return super(sdf_register, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
    
    @api.multi
    def get_default_province(self):
        user_obj = self.env['res.users']
        user_groups = user_obj.browse(self._uid).groups_id
        province_id = None
        group_names = [group.name for group in user_groups]
        if "Provincial Manager" in group_names or "Provincial Officer" in group_names :
            user_province_ids = [province_data.id for province_data in self.env['res.users'].browse(self._uid).province_ids]
            if user_province_ids : 
                province_id = user_province_ids[0]
        return province_id 
    
    ## fields for image.
    image_medium = fields.Binary(string='Medium Photo')
    # fields from SDF General Information
    name = fields.Char(string="Name", track_visibility='onchange', required=True)
#     category_ids = fields.Many2many('hr.employee.category', 'employee_category_rel', 'emp_id', 'category_id', string='Tags')
    work_email = fields.Char(string='Work Place Email', track_visibility='onchange')
    work_phone = fields.Char(string='Work Place Phone', track_visibility='onchange', size=10)
    work_address2 = fields.Char(string='Work Place Address 2', track_visibility='onchange')
    work_address3 = fields.Char(string='Work Place Address 3', track_visibility='onchange')
    work_city = fields.Many2one('res.city', string='Work City', track_visibility='onchange')
    work_province = fields.Many2one('res.country.state', string='Work Place Province', default=get_default_province, track_visibility='onchange')
    work_zip = fields.Char(string='Work Place Zip', track_visibility='onchange')
    work_country= fields.Many2one('res.country', string='Work Place Country', track_visibility='onchange') 
    # fields from SDF Public Information
    work_address = fields.Char(string='Work Place Address', track_visibility='onchange')
#     mobile_phone = fields.Char(string='Mobile / Phone',track_visibility='onchange', size=20)
    work_location = fields.Char(string='Work Place Location',track_visibility='onchange')
    department = fields.Char(string='Department', track_visibility='onchange')
    job_title = fields.Char(string='Job Title', track_visibility='onchange')
    manager = fields.Char(string='Manager', track_visibility='onchange')
    coach_id = fields.Many2one('hr.employee', string='Coach', track_visibility='onchange')
    user_id = fields.Many2one('res.users', string='Related User', track_visibility='onchange')
    notes = fields.Text(string='Notes', track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', track_visibility='onchange')
    person_home_city = fields.Many2one('res.city', string='Home City',track_visibility='onchange')
    person_postal_city = fields.Many2one('res.city', string='Postal City',track_visibility='onchange')
    person_home_zip = fields.Char(string='Home Zip', track_visibility='onchange')
    person_postal_zip = fields.Char(string='Postal Zip', track_visibility='onchange')
    person_home_province_code = fields.Many2one('res.country.state', string='Home Province Code', track_visibility='onchange')
    person_postal_province_code = fields.Many2one('res.country.state', string='Postal Province Code', track_visibility='onchange')
    country_home = fields.Many2one('res.country', string='Home Country', track_visibility='onchange')
    country_postal = fields.Many2one('res.country', string='Postal Country', track_visibility='onchange')
    # fields from SDF Personal Information
    country_id = fields.Many2one('res.country', string='Nationality',track_visibility='onchange')
    identification_id = fields.Char(string='Identification No',track_visibility='onchange', size=13)
    passport_id = fields.Char(string='Passport No',track_visibility='onchange')
    bank_account_id = fields.Many2one('res.partner.bank', string='Bank Account Number',track_visibility='onchange', domain="[('partner_id','=',address_home_id)]", help='Employee bank salary account')
#     otherid = fields.Char(string='Other Id',track_visibility='onchange')
    national_id = fields.Char(string='National Id',track_visibility='onchange')
    home_language_code = fields.Many2one('res.lang', string='Home Language Code',track_visibility='onchange', size=6)
    citizen_resident_status_code = fields.Selection([('dual','D - Dual (SA plus other)'),('other','O - Other'),('sa','SA - South Africa'),('unknown','U - Unknown')],string='Citizen Status')
#     filler01 = fields.Char(string='Filler01',track_visibility='onchange', size=2)
#     filler02 = fields.Char(string='Filler02',track_visibility='onchange', size=10)
    address_home = fields.Char(string='Home Address',track_visibility='onchange',)
    bank_account_number = fields.Char(string='Bank Account Number',track_visibility='onchange')
#     person_alternate_id = fields.Char(string='Person Alternate Id',track_visibility='onchange', size=20)
#     alternate_id_type_id = fields.Char(string='Alternate Type Id',track_visibility='onchange', size=3)
#     equity_code = fields.Char(string='Equity Code',track_visibility='onchange', size=10)
    person_last_name = fields.Char(string='Last Name',track_visibility='onchange', size=45)
#     person_middle_name = fields.Char(string='Middle Name',track_visibility='onchange', size=50)
    person_title = fields.Selection([('adv', 'Adv.'), ('dr', 'Dr.'),('mr', 'Mr.'),('mrs', 'Mrs.'), ('ms', 'Ms.'), ('prof', 'Prof.')], string='Job Title', track_visibility='onchange')
    person_birth_date = fields.Date(string='Birth Date',track_visibility='onchange')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Gender',track_visibility='onchange')
    marital = fields.Selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('widow','Widow'), ('divorced', 'Divorced')], 'Marital Status',track_visibility='onchange')
    # fields from SDF Address Tab
    person_home_address_1 = fields.Char(string='Home Address 1',track_visibility='onchange', size=50)
    person_home_address_2 = fields.Char(string='Home Address 2',track_visibility='onchange', size=50)
    person_home_address_3 = fields.Char(string='Home Address 3',track_visibility='onchange', size=50)
    person_postal_address_1 = fields.Char(string='Postal Address 1',track_visibility='onchange', size=50)
    person_postal_address_2 = fields.Char(string='Postal Address 2',track_visibility='onchange', size=50)
    person_postal_address_3 = fields.Char(string='Postal Address 3',track_visibility='onchange', size=50)
    person_home_addr_postal_code = fields.Char(string='Home Address Postal Code',track_visibility='onchange', size=4)
    person_home_addr_post_code = fields.Char(string='Home Address Post Code',track_visibility='onchange', size=4)
#     person_cell_phone_number = fields.Char(string='Cell Phone Number',track_visibility='onchange', size=20)
#     person_fax_number = fields.Char(string='Fax Number',track_visibility='onchange', size=20)
#     province_code = fields.Char(string='Province Code',track_visibility='onchange', size=2)
#     provider_code = fields.Char(string='Provider Code',track_visibility='onchange', size=20)
    employer_ids = fields.One2many('sdf.employer.rel', 'sdf_id', string='Employers',track_visibility='onchange', copy=True)
    state = fields.Selection([
            ('general_info','General Information'),
            ('public_info','Public Information'),
            ('personal_info','Personal Information'),
            ('address_info','Address Information'),
            ('employer_info','Employer'),
            ('pending','Pending'),
            ('approved','Approved'),
            ('denied','Rejected'),
        ], string='State',track_visibility='onchange', index=True, default='general_info',
        copy=False,
        help=" * The 'Public Information' status is used when user fills Public Information.\n"
             " * The 'Personal Information' status is used when user fills Personal Information.\n"
             " * The 'Address Information' status is used when user fills Address Information.\n"
             " * The 'Pending' is used when user submit Registration Information.\n"
             " * The 'Approved' status is used when user has been approved by Department.\n"
             " * The 'Denied' status is used when user has been denied by Department.")
    submitted = fields.Boolean(string='Submitted')
    approved = fields.Boolean(string='Approved')
    denied = fields.Boolean(string='Denied')
    related_sdf = fields.Many2one('hr.employee', string='Related SDF')
    initials = fields.Char(string='Initials',track_visibility='onchange', size=50)
    population_group = fields.Selection([('African', 'African'), ('Coloured', 'Coloured'),('Indian', 'Indian'), ('White', 'White')], 'Population Group',track_visibility='onchange')
    disabled = fields.Boolean('Disabled')
    highest_level_of_education = fields.Char(string='Highest Level Of Education',track_visibility='onchange', size=50)
    current_occupation = fields.Char(string='Current Occupation',track_visibility='onchange', size=50)
    citizen_status = fields.Selection([('African', 'African'), ('Coloured', 'Coloured'),('Indian', 'Indian'), ('White', 'White')], 'Citizen Status',track_visibility='onchange')
#     experiance = fields.Char(string='Experiance',track_visibility='onchange', size=100)
#     experiance_dur = fields.Char(string='Duration of total experience in years',track_visibility='onchange', size=50)
    cell_phone_number = fields.Char(string='Cell Phone Number',track_visibility='onchange', size=10)
#     telephone_number = fields.Char(string='Telephone Number',track_visibility='onchange', size=50)
#     fax_number = fields.Char(string='Fax Number',track_visibility='onchange', size=50)
    person_suburb = fields.Many2one('res.suburb',string='Suburb')
    person_home_suburb = fields.Many2one('res.suburb',string='Home Suburb')
    person_postal_suburb = fields.Many2one('res.suburb',string='Postal Suburb')
#     username = fields.Char(string='Username',track_visibility='onchange', size=50)
#     password = fields.Char(string='Password',track_visibility='onchange', size=50)
#     confirm_password = fields.Char(string='Confirm Password',track_visibility='onchange', size=50)
    person_name = fields.Char(string='Name',track_visibility='onchange', size=50)
    cont_number_home = fields.Char(string='Contact Number Home', track_visibility='onchange', size=20)
    cont_number_office = fields.Char(string='Contact Number Office', track_visibility='onchange', size=20)
    id_document = fields.Many2one('ir.attachment', string='ID Document', help='Upload Document')
#     id_document = fields.Binary(string='ID Document')
    final_state = fields.Char(string='Status')
    sdf_reference_no = fields.Char(string='Reference No',track_visibility='onchange', size=50)
    dissability = fields.Selection([('yes','Yes'),('no','No')], string="Dissability")
    ## Banking Details
    bank_name = fields.Char(string='Bank Name')
    branch_code = fields.Char(string='Branch Code')
    ##
    same_as_home = fields.Boolean(string='Same As Home Address')
#     sdf_reference_no = fields.Char(string='Reference_No',track_visibility='onchange', size=50)
    ## Field for Identifying african or not.
    african = fields.Boolean(string='African')
    sdf_type = fields.Selection([('internal','Internal'),('consultant','Consultant')], string='SDF Type')
    sdf_approval_date = fields.Date(string='SDF Approval Date')
    sdf_register_date = fields.Date(string='SDF Registation Date')
    waiting_approval = fields.Boolean(string='Waiting Approval')
    sdf_letter_from_employer=fields.Many2one("ir.attachment",string="Letter of SDF appointment from employer")
    sdf_password = fields.Char("Password")
    primary_secondary = fields.Selection([('primary','Primary'),('secondary','Secondary')], string='Internal Type')
    check_sdf_type = fields.Boolean(string="Check SDF Type",default=False)
    
    _sql_constraints = [('identityno_uniq', 'unique(identification_id)',
            'R.S.A.Identification No must be unique per SDF!'),]
    
    @api.model
    def create(self, vals):
        context = self._context
        if not context.get('from_website', False) :
            vals['sdf_reference_no'] = self.env['ir.sequence'].get('sdf.register.reference')
            vals['final_state'] = 'Draft'
        res = super(sdf_register, self).create(vals)
        if context.get('from_website',False) :
#              Sending Email Notification.
            ir_model_data_obj = self.env['ir.model.data']
            mail_template_id = ir_model_data_obj.get_object_reference('hwseta_sdp', 'email_template_sdf_register_submit')
            if mail_template_id:
                self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], res.id, force_send=True,context=self.env.context)
       
            mail_template_bronwen_id = ir_model_data_obj.get_object_reference('hwseta_sdp', 'email_template_sdf_register_brian_submit')
            if mail_template_bronwen_id:
                self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_bronwen_id[1], res.id, force_send=True,context=self.env.context)
        # Validations for Phone and Mobile Number
        if vals.get('work_phone') :
            validate_phone_mobile(vals['work_phone'])
        return res
    
    @api.multi
    def onchange_sdf_type(self, sdf_type):
        res = {}
        if not sdf_type:
            res.update({'value':{'check_sdf_type':False}})
            return res
        if sdf_type == 'internal':
            res.update({'value':{'check_sdf_type':True}})
        if sdf_type == 'consultant':
            res.update({'value':{'check_sdf_type':False,'primary_secondary':''}})
        return res
        
    @api.multi
    def onchange_person_suburb(self, person_suburb):
        res = {}
        if not person_suburb:
            return res
        if person_suburb:
            sub_res = self.env['res.suburb'].browse(person_suburb)
            res.update({'value':{'work_zip':sub_res.postal_code,'work_city':sub_res.city_id,'work_province':sub_res.province_id}})
        return res

    @api.multi
    def onchange_person_home_suburb(self, person_home_suburb):
        res = {}
        if not person_home_suburb:
            return res
        if person_home_suburb:
            sub_res = self.env['res.suburb'].browse(person_home_suburb)
            res.update({'value':{'person_home_zip':sub_res.postal_code,'person_home_city':sub_res.city_id,'person_home_province_code':sub_res.province_id}})
        return res
        
    @api.multi
    def onchange_person_postal_suburb(self, person_postal_suburb):
        res = {}
        if not person_postal_suburb:
            return res
        if person_postal_suburb:
            sub_res = self.env['res.suburb'].browse(person_postal_suburb)
            res.update({'value':{'person_postal_zip':sub_res.postal_code,'person_postal_city':sub_res.city_id,'person_postal_province_code':sub_res.province_id}})
        return res

    @api.multi
    def onchange_crc(self, citizen_resident_status_code):
        res = {}
        if not citizen_resident_status_code:
            return res
        if citizen_resident_status_code == 'sa':
            country_data = self.env['res.country'].search(['|',('code','=','ZA'),('name','=','South Africa')],limit=1)
            res.update({'value':{'country_id':country_data and country_data.id},'domain':{'country_id':[('id','in',[country_data.id])]}})
        else:res.update({'domain':{'country_id':[('id','in',[country_data.id for country_data in self.env['res.country'].search([])])]}})
        return res
    
    @api.multi
    def onchange_country_id(self, country_id):
        res = {}
        if not country_id:
            return res
        country_data = self.env['res.country'].browse(country_id)
        if country_data.code == 'ZA':
            res.update({'value':{'african':True, 'citizen_resident_status_code':'sa'}})
        else:
            res.update({'value':{'african':False}})
        return res
    
    @api.multi
    def country_for_province(self, province):
        state = self.env['res.country.state'].browse(province)
        return state.country_id.id
    
    @api.multi
    def onchange_work_province(self, province):
        if province:
            country_id = self.country_for_province(province)
            return {'value': {'work_country': country_id }}
        return {}
    
    @api.multi
    def onchange_home_province(self, province):
        if province:
            country_id = self.country_for_province(province)
            return {'value': {'country_home': country_id }}
        return {}
    
    @api.multi
    def onchange_postal_province(self, province):
        if province:
            country_id = self.country_for_province(province)
            return {'value': {'country_postal': country_id }}
        return {}
    
    @api.multi
    def action_submit_button(self):
        if not self.work_address:
            raise Warning(_('Please fill Work Address in Public Information.'))
        if not self.person_home_address_1:
            raise Warning(_('Please fill Home Address in Address Information.'))
        if not self.person_postal_address_1:
            raise Warning(_('Please fill Postal Address in Address Information.'))
        if not self.citizen_resident_status_code:
            raise Warning(_('Please Select Citizen Status in Personal Information.'))
        if not self.id_document:
            raise Warning(_('Please upload ID Document in Personal Information.'))
        if not self.employer_ids:
            raise Warning(_('Please Select Employers Information.'))
        self = self.with_context(submit=True)
        self.write({'state':'pending','submitted':True,'final_state':'Submitted'})
        sdf_type = ''
        if self.sdf_type == 'internal':
            sdf_type = self.primary_secondary
        elif self.sdf_type == 'consultant':
            sdf_type = self.sdf_type
            
#         ir_model_data_obj = self.env['ir.model.data']
#         sdf_mail_template_id = ir_model_data_obj.get_object_reference('hwseta_sdp', 'email_template_sdf_register_submit')
#         if sdf_mail_template_id:
#             self.pool['email.template'].send_mail(self.env.cr, self.env.uid, sdf_mail_template_id[1], self.id, force_send=True,context=self.env.context) 
                   
        for employer_data in self.employer_ids:
            employer_id = employer_data.employer_id.id
            email_template_obj = self.env['email.template']
            ir_model_data_obj = self.env['ir.model.data']
            mail_template_id = ir_model_data_obj.get_object_reference('hwseta_sdp', 'email_template_sdf_individual_register_submit')
            employers_sdfs = self.env['sdf.tracking'].search([('partner_id','=',employer_id),('status','=','approved'),('sdf_register_id','!=',self.id)])
                        
            employer_data.write({'status':'waiting_approval','employer_status':'Pending'})
            ##Added for One step approval
#             employer_data.write({'status':'approved','employer_status':'Pending'})
            if mail_template_id:
                temp_obj = email_template_obj.browse(mail_template_id[1])
                body="""
                <table>
                <tbody><tr><td>SDF Name :&nbsp;</td><td><b>%s</b></td></tr>
                </tbody></table>
                <br>
                
                <table>
                <tbody><tr><td><div>Name of Organisation :<b>%s</b>
                </div></td></tr>
                </tbody></table>
                <br>
                
                <table>
                <tbody><tr><td><div>SDL Number of Organisation :<b>%s</b>
                </div></td></tr>
                </tbody></table>
                <br>
                <table>
                <tbody><tr><td>Application Unique Number :&nbsp;</td><td><b>%s</b></td> </tr>
                </tbody></table>
                <br>
                
                <table>
                <tbody><tr><td>Dear </td><td><b>&nbsp;%s</b>,</td> 
                </tr>
                </tbody></table>
                
                <p><u>Application for Skills Development Facilitator Registration</u></p>
                
                <p>This email is to confirm that you have made an application to be the Skills Development Facilitator for <b>%s<span>-</span>%s
                </b>In order to finalise your application please send through a letter confirming your status as the SDF to <a href="">Tiyanin@hwseta.org.za</a><br><br>
                
                If you should have any queries please contact Ms Motshidisi Marera on <a href="">motshidisim@hwseta.org </a> or 011 607 7026.</p>
                
                
                <table>
                <tbody><tr><td>Regards</td></tr>
                <tr><td>Bronwen du Plessis</td> </tr>
                <tr><td>WSP Manager</td></tr>
                </tbody></table>
                """%(self.name,employer_data.employer_id.name,employer_data.employer_id.employer_sdl_no,self.sdf_reference_no,self.name,employer_data.employer_id.name,employer_data.employer_id.employer_sdl_no,)
                if employer_data.employer_id:
                    temp_obj.write({'email_to' : employer_data.employer_id.email,'body_html':body})
                    self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id,force_send=True,context=self.env.context)           
            res = {
                   'sdf_register_id':self.id,
                    'status':'requested_approval',
                   'partner_id':employer_id,
                   ## new added for one step SDF approval
#                    'status':'approved',
                   'sdf_approved_denied':True,
                   'sdf_type':sdf_type
                   
            }
            partner_data = self.env['res.partner'].browse(employer_id)
            partner_data.write({'sdf_tracking_ids':[(0, 0, res)]})
            ##Added for one step approval
            self.write({'waiting_approval':True})
               
            
        return True
    
    @api.multi
    def action_deny_button(self):
        self = self.with_context(deny=True)
        for employer in self.employer_ids:
            employer_id = employer.employer_id and employer.employer_id.id
            employers_sdfs_id = self.env['sdf.tracking'].search([('partner_id','=',employer_id),('sdf_register_id','=',self.id)])
            employers_sdfs_id.write({'status':'denied'})
            employer.write({'status':'rejected','employer_status':'Rejected'})
        self.write({'state':'denied','denied':True,'final_state':'Denied'})
        return True
    
    
    @api.multi
    def action_approve_button(self):
        self = self.with_context(submit=True)
        sdf_obj = self.env['hr.employee']
#         self.write({'state':'approved','approved':True})
        sdf_type = ''
        if self.sdf_type == 'internal':
            sdf_type = self.primary_secondary
        elif self.sdf_type == 'consultant':
            sdf_type = self.sdf_type
        if not self.approved :
            ## Writing Employers in SDF Profile (Employers who approved SDF only).
            employer_values = []
            for employer in self.employer_ids:
                employer_id = employer.employer_id and employer.employer_id.id
                ## Avoiding SDF Registration for Employer if employer already having 2 sdf.
                employers_sdfs_id = self.env['sdf.tracking'].search([('partner_id','=',employer_id),('status','=','approved'),('sdf_register_id','=',self.id)])
                employers_sdfs = self.env['sdf.tracking'].search([('partner_id','=',employer_id),('status','=','approved')])
#                 if len(employers_sdfs)>1 :
#                     raise Warning(_('Employer %s already having 2 SDF')%(employer.employer_id.name))
                ###
                for existing_sdf in employers_sdfs:
                    if existing_sdf.sdf_type == 'primary' and self.primary_secondary == 'primary' and existing_sdf.status == 'approved':
                        sdf_type = self.primary_secondary
                        existing_sdf.write({'status':'dormant'})
                    elif existing_sdf.sdf_type == 'secondary' and self.primary_secondary == 'secondary' and existing_sdf.status == 'approved':
                        sdf_type = self.primary_secondary
                        existing_sdf.write({'status':'dormant'})
                    elif existing_sdf.sdf_type == 'consultant' and self.primary_secondary == 'primary' and existing_sdf.status == 'approved':
                        sdf_type = self.primary_secondary
                        existing_sdf.write({'status':'dormant'})                        
                    elif existing_sdf.sdf_type != 'primary' and self.primary_secondary == 'primary':
                        sdf_type = self.primary_secondary
                    elif existing_sdf.sdf_type != 'secondary' and self.primary_secondary == 'secondary':
                        sdf_type = self.primary_secondary
                    elif existing_sdf.sdf_type == 'consultant' and self.sdf_type == 'consultant' and existing_sdf.status == 'approved':
                        sdf_type = self.sdf_type        
                        existing_sdf.write({'status':'dormant'})
                    elif existing_sdf.sdf_type == 'primary' and self.sdf_type == 'consultant' and existing_sdf.status == 'approved':
                        sdf_type = self.sdf_type
                        existing_sdf.write({'status':'dormant'})                         
                    elif existing_sdf.sdf_type != 'consultant' and self.sdf_type == 'consultant':
                        sdf_type = self.sdf_type

                                               
                res = {}
                sdf_track_data = self.env['sdf.tracking'].search([('sdf_register_id','=',self.id),('partner_id','=',employer_id)])
#                 if sdf_track_data and employer.status == 'approved':
                if sdf_track_data and employer.status == 'waiting_approval':       
                    employer.write({'employer_status':'Approved'})
                    res = {
                           'employer_id':employer_id,
                           'employer_trading_name':employer.employer_trading_name,
                           'sdl_no':employer.sdl_no,
                           'seta_id':employer.seta_id,
                           'registration_number':employer.registration_number,
                           'emp_add':False,
                           'status':'approved',
                           'confirm_sdf_appointment_letter_from_employer':employer.confirm_sdf_appointment_letter_from_employer and employer.confirm_sdf_appointment_letter_from_employer.id,
                           }
                    employer_values.append((0,0,res))
#                     sdf_data.write({'employer_ids':[(0,0,res)]})
                    sdf_track_data.write({'sdf_approved_denied':True,'status':'approved','employer_status':'Approved','sdf_type':sdf_type})
            password = ''.join(random.choice('admin') for _ in range(10))
            self.write({'sdf_password':password})
            ## Creating SDF after Registration.
            sdf_data = sdf_obj.create({
                             'name' : self.name,
                             'work_email' : self.work_email,
                             'work_phone' : self.work_phone,
                             'sdf_type' : self.sdf_type,
                             'work_address' : self.work_address,
                             'work_address2' : self.work_address2,
                             'work_address3' : self.work_address3,
                             'person_suburb' : self.person_suburb and self.person_suburb.id,
                             'work_city' : self.work_city and self.work_city.id,
                             'work_zip':self.work_zip,
                             'work_province':self.work_province and self.work_province.id,
                             'work_country':self.work_country and self.work_country.id,
                             'work_location' : self.work_location,
                             'department' : self.department,
                             'job_title' : self.job_title,
                             'manager' : self.manager,
                             'coach_id' : self.coach_id and self.coach_id.id or False,
                             'notes' : self.notes,
                             'same_as_home' : self.same_as_home,
                             'person_title' : self.person_title,
                             'person_name' : self.person_name,
                             'person_last_name': self.person_last_name,
                             'person_birth_date' : self.person_birth_date,
                             'cont_number_home' : self.cont_number_home,
                             'cont_number_office' : self.cont_number_office,
                             'person_cell_phone_number' : self.cell_phone_number,
                             'country_id' : self.country_id and self.country_id.id,
                             'identification_id' : self.identification_id,
                             'passport_id' : self.passport_id,
                             'citizen_resident_status_code' : self.citizen_resident_status_code,
                             'national_id' : self.national_id,
                             'id_document':self.id_document and self.id_document.id,
                             'home_language_code' : self.home_language_code and self.home_language_code.id,
                             'gender' : self.gender,
                             'marital' : self.marital,
                             'dissability' : self.dissability,
                             'is_sdf':True,
                             'seta_elements':True,
                             'person_home_address_1' : self.person_home_address_1,
                             'person_home_address_2' : self.person_home_address_2,
                             'person_home_address_3' : self.person_home_address_3,
                             'person_home_suburb' : self.person_home_suburb and self.person_home_suburb.id,
                             'person_home_city': self.person_home_city and self.person_home_city.id,
                             'person_home_province_code':self.person_home_province_code and self.person_home_province_code.id,
                             'person_home_zip' : self.person_home_zip,
                             'country_home': self.country_home and self.country_home.id,
                             'person_postal_address_1' : self.person_postal_address_1,
                             'person_postal_address_2' : self.person_postal_address_2,
                             'person_postal_address_3' : self.person_postal_address_3,
                             'person_postal_suburb' : self.person_postal_suburb and self.person_postal_suburb.id,
                             'person_postal_city':self.person_postal_city and self.person_postal_city.id,
                             'person_postal_province_code':self.person_postal_province_code and self.person_postal_province_code.id,
                             'person_postal_zip':self.person_postal_zip,
                             'country_postal':self.country_postal and self.country_postal.id,
                             'sdf_reg_id' : self.id,
                             'employer_ids':employer_values,
                             'sdf_letter_from_employer':self.sdf_letter_from_employer.id, 
                             'password':self.sdf_password,
                             'primary_secondary':self.primary_secondary,
                                                    })
            ## Sending Email Notification.
            ir_model_data_obj = self.env['ir.model.data']
            mail_template_id = ir_model_data_obj.get_object_reference('hwseta_sdp', 'email_template_sdf_register_approve')
            if mail_template_id:
                self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True,context=self.env.context)
            self.write({'related_sdf':sdf_data.id,'state':'approved','approved':True,'final_state':'Approved','sdf_approval_date' : datetime.today().date(),})
          
        employer_tracking_ids = self.env['sdf.tracking'].search([('sdf_register_id','=',self.id)])
        for employer_data in self.employer_ids:
            employer_id = employer_data.employer_id and employer_data.employer_id.id
            for employer_track in employer_tracking_ids: 
                employer_track.write({'sdf_id':sdf_data.id})
                if employer_track.partner_id.id==employer_data.employer_id.id and employer_track.status=='approved':
                    email_template_obj = self.env['email.template']
                    ir_model_data_obj = self.env['ir.model.data']
                    mail_template_id = ir_model_data_obj.get_object_reference('hwseta_sdp', 'email_template_individual_sdf_register_approve')
                    if mail_template_id:
                        temp_obj = email_template_obj.browse(mail_template_id[1])
                        body="""
                        <table>
                        <tbody><tr><td>SDF Name :</td><td><b>%s</b></td></tr>
                        </tbody></table>
                        <br>
                         
                        <table>
                        <tbody><tr><td><div>Name of Organisation : <b>%s</b></div></td></tr>
                        </tbody></table>
                        <br>
                         
                        <table>
                        <tbody><tr><td>SDL Number of Organisation :</td><td><b>%s</b></td> </tr>
                        </tbody></table>
                        <br>
                         
                        <table>
                        <tbody><tr><td>Application Unique Number :</td><td><b>%s</b></td> </tr>
                        </tbody></table>
                        <br>
                         
                        <table>
                        <tbody><tr><td>Date :</td><td><b>2016-02-05</b></td> 
                        </tr>
                        </tbody></table>
                        <br>
                         
                         
                        <p>Acceptance of Skills Development Facilitator Registration</p><br>
                         
                        <p>This email is to confirm that you have been accepted as the Skills Development Facilitator for <b>%s<span>-</span>%s
                        </b>
                        .<br><br>
                         
                        Please use your login and password indicated below to access the HWSETA system:<br><br>
                         
                        </p><table>
                        <tbody><tr><td>Login :</td><td><b>%s</b></td></tr>
                        <tr><td>Password :</td><td><b>%s</b></td></tr>
                        </tbody></table>
                        <br>
                         
                        If you should have any queries please contact Ms Motshidisi Marera on <a href="#">motshidisim@hwseta.org</a> or 011 607 7026.<br><br><br>
                         
                        <table>
                        <tbody><tr><td>Regards</td></tr>
                        <tr><td>Bronwen du Plessis</td> </tr>
                        <tr><td>WSP Manager</td></tr>
                        </tbody></table>
                        """%(self.name,employer_data.employer_id.name,employer_data.employer_id.employer_sdl_no,self.sdf_reference_no,employer_data.employer_id.name,employer_data.employer_id.employer_sdl_no,self.work_email,self.sdf_password)
                         
                        temp_obj.write({'email_to' : employer_data.employer_id.email,'body_html':body})
                        self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id,force_send=True,context=self.env.context)
        return True
    
    @api.multi
    def check_alpha(self, field_string, msg):
        for st in field_string :
            if st.isalpha():
                raise Warning(_(msg))
        return True
    
    @api.multi
    def write(self, vals):
        res = super(sdf_register, self).write(vals)
        sdl_number = []
        for employer in self.employer_ids :
            if employer.sdl_no in sdl_number :
                raise Warning(_('You can not add same employer multiple time!!.'))
            else :
                sdl_number.append(employer.sdl_no)        
        context = self._context
        if context.get('submit') == True:
            pass
        if self.state == "pending" and self.submitted == False:
            raise Warning(_('Sorry! you can not change status to Pending first submit application.'))
        if self.state == "approved" and self.approved == False:
            raise Warning(_('Sorry! you can not change status to Approved.'))
        if self.state == "denied" and self.denied == False:
            raise Warning(_('Sorry! you can not change status to Rejected.'))
        if self.state == "pending" and self.approved == True:
            raise Warning(_('Sorry! You can not change status to Pending. This transaction is already Approved!.'))
        if self.state == "pending" and self.denied == True:
            raise Warning(_('Sorry! You can not change status to Pending. This transaction is already Rejected!.'))
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
                return {'value':{'identification_id':''},'warning':{'title':'Invalid Identification Number','message':'Incorrect Identification Number!'}}
            else:
                # # Calculating last day of month.
                x_year = int(year)
                if x_year == 00:
                    x_year = 2000
                last_day = calendar.monthrange(int(x_year),int(month))[1]
                if int(day) > last_day :
                    return {'value':{'identification_id':''},'warning':{'title':'Invalid Identification Number','message':'Incorrect Identification Number!'}}
            if int(year) == 00 or int(year) >= 01 and int(year) <= 20:
                birth_date = datetime.strptime('20' + year + '-' + month + '-' + day, '%Y-%m-%d').date()
            else:
                birth_date = datetime.strptime('19' + year + '-' + month + '-' + day, '%Y-%m-%d').date()
            
            val.update({'person_birth_date':birth_date})
            res.update({'value':val})
            return res
        else:
            return {'value':{'identification_id':''},'warning':{'title':'Invalid Identification Number','message':'Identification Number should be numeric!'}}
    
sdf_register()

class sdf_employer_rel(models.Model):
    _name = 'sdf.employer.rel'
    
    employer_id = fields.Many2one("res.partner", string="Employer", domain="[('employer','=',True)]")
    employer_trading_name = fields.Char(string='Trading Name')
    sdl_no = fields.Char(string='SDL No.', size=10)
    seta_id = fields.Char(string='SETA Id.', size=3)
    registration_number = fields.Char(string='Registration Number', size=20)
    sdf_id = fields.Many2one("sdf.register", string="SDF", ondelete='cascade')
    sdf_prof_id = fields.Many2one("hr.employee", string="SDF Profile", ondelete='cascade')
    state = fields.Selection([('draft','Draft'),('assessment_done', 'Assessment Done'), ('transche_payment','TP Done')], string="State")
    status = fields.Selection([('draft','Draft'),('waiting_approval','Waiting Approval'),('approved', 'Approved'), ('rejected','Rejected')], string="Status", default='draft')
    emp_add = fields.Boolean(string='Add Organization', default=True)
    request_send = fields.Boolean(string='Send Request', default=False)
    confirm_sdf_appointment_letter_from_employer=fields.Many2one('ir.attachment',string="SDF Appointment Letter")
    employer_status = fields.Char("Status")

    @api.multi
    def onchange_employer_id(self, employer_id):
        if not employer_id:
            return False
        else:
            result = {}
            employer_data = self.env['res.partner'].browse(employer_id)
            result = {'value':{
                               'sdl_no'             : employer_data.employer_sdl_no,
                               'employer_trading_name':employer_data.employer_trading_name,
                               'seta_id'            : employer_data.employer_seta_id,
                               'registration_number': employer_data.employer_registration_number
                               }
                      }
        return result
    
    @api.multi
    def onchange_sdl_number(self, sdl_no):
        if not sdl_no:
            return False
        else:
            result = {}
            employer_data = self.env['res.partner'].search([('employer_sdl_no','=',sdl_no)])
            if not employer_data:
                raise Warning(_('Enter the valid SDL Number!')) 
            result = {'value':{
                               'employer_id':employer_data.id,
                               'employer_trading_name':employer_data.employer_trading_name,
                               'seta_id'            : employer_data.employer_seta_id,
                               'registration_number': employer_data.employer_registration_number
                               },
                      'domain':{
                                'employer_id':[('id','in',[employer_data.id])]
                                }
                      }
        return result    
    
    @api.multi
    def action_send_request(self):
        employer_data = self.employer_id
        sdf_data = self.sdf_prof_id
        if employer_data and sdf_data:
            employer_id = employer_data.id
            self.write({'status':'waiting_approval','request_send':True})
            res = {
                   'sdf_register_id':sdf_data.sdf_reg_id.id,
                   'status':'requested_approval',
                   'sdf_id':sdf_data.id,
                   'partner_id':employer_id,
                   'sdf_employer_rel_id':self.id,
                   }
            partner_data = self.env['res.partner'].browse(employer_id)
            partner_data.write({'sdf_tracking_ids':[(0, 0, res)]})    
        # Mail notification Organisation
        ir_model_data_obj = self.env['ir.model.data']
        mail_template_id = ir_model_data_obj.get_object_reference('hwseta_sdp', 'email_template_sdf_register_organisation_post_submit')
        if mail_template_id:
            self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True,context=self.env.context)           
        
        ## Sending Email Notification.
        ir_model_data_obj = self.env['ir.model.data']
        mail_template_id = ir_model_data_obj.get_object_reference('hwseta_sdp', 'email_template_sdf_register_sdp_managers_post_submit') 
        if mail_template_id:
            self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True,context=self.env.context)     
        return True
    
sdf_employer_rel()

class sdf_tracking(models.Model):
    _name = 'sdf.tracking'
    sdf_id = fields.Many2one("hr.employee", string="SDF", ondelete='cascade')
    sdf_register_id = fields.Many2one("sdf.register", string="SDF Registering", ondelete='cascade')
    status = fields.Selection([('requested_approval','Requested Approval'),
                               ('approved','Approved'),
                               ('denied','Denied'),
                               ('dormant','Dormant'),
                               ('pending','Pending')],
                              string='State', readonly=True)
    partner_id = fields.Many2one("res.partner", string="Partner", domain="[('employer','=',True)]")
    sdf_approved_denied = fields.Boolean(string='SDF Approved Denied')
    sdf_employer_rel_id = fields.Many2one("sdf.employer.rel", string="sdf employer rel")
    sdf_type = fields.Selection([('primary','Primary'),('secondary','Secondary'),('consultant','Consultant')])
    sdf_dormant = fields.Boolean("SDF dormant",default=False)
    
    @api.multi
    def action_approve_sdf(self):
        sdf_register_data = self.sdf_register_id
        employer_data = self.partner_id
        ## Existing Code Base
#         if sdf_register_data and self.partner_id:
#             self.sdf_register_id.write({'waiting_approval':True})
#             self.write({'status':'approved', 'sdf_approved_denied':True})

        ##
        ## Add Employer Directly.
        if self.sdf_employer_rel_id:
            sdf_emp_rel_data = self.env['sdf.employer.rel'].browse(self.sdf_employer_rel_id.id)
            if sdf_emp_rel_data:
                sdf_emp_rel_data.write({'status':'approved'})
                self.write({'status':'approved', 'sdf_approved_denied':True})
                
                ## Sending Email Notification.
                ir_model_data_obj = self.env['ir.model.data']
                mail_template_id = ir_model_data_obj.get_object_reference('hwseta_sdp', 'email_template_sdf_register_post_approve')
                if mail_template_id:
                    self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True,context=self.env.context)
                
                
                ## Sending Email Notification.
                ir_model_data_obj = self.env['ir.model.data']
                mail_template_id = ir_model_data_obj.get_object_reference('hwseta_sdp', 'email_template_sdf_register_post_approve_manager')
                if mail_template_id:
                    self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True,context=self.env.context)
        ##
        ## Checking SDF Registration State. IF registration already approved. Then directly add Employer to SDF
        if sdf_register_data.final_state == 'Approved' :
            sdf_data = self.env['hr.employee'].search([('sdf_reg_id','=',sdf_register_data.id)])
            reg_no = ''
            if not self.sdf_employer_rel_id:
                for emp_data in sdf_register_data.employer_ids :
                    if emp_data.employer_id and emp_data.employer_id.id == employer_data.id :
                        reg_no = emp_data.registration_number
                self.env['sdf.employer.rel'].create({
                                                     'sdf_prof_id' : sdf_data.id,
                                                     'employer_id' : employer_data.id,
                                                     'sdl_no' : employer_data.employer_sdl_no,
                                                     'registration_number' : reg_no,
                                                     'emp_add':False,
                                                     'status':'approved',
                                                     })
                self.write({'status':'approved', 'sdf_approved_denied':True})
        else:
            if sdf_register_data and employer_data :
                for emp_data in sdf_register_data.employer_ids :
                    if emp_data.employer_id and emp_data.employer_id.id == employer_data.id :
                        emp_data.write({'status':'approved'})
                self.sdf_register_id.write({'waiting_approval':True})
                self.write({'status':'approved', 'sdf_approved_denied':True})
#             self.sdf_register_id.action_approve_button()
            
        return True
    
    @api.multi
    def action_deny_sdf(self):
        self.write({'status':'denied', 'sdf_approved_denied':True})
        # TODO: Creation of SDF Master from SDF Registration Information Object. 
        return True
    
    @api.multi
    def action_dormant_sdf(self):
        self.write({'status':'dormant', 'sdf_dormant':True})
        return True    
    
sdf_tracking()

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    sdf_tracking_ids = fields.One2many('sdf.tracking', 'partner_id', string='SDF tracking')

#     #this method is used to improve performance of employer selection

#     def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=None):
#         if not args:
#             args = []
#         if not(name and operator in ('=', 'ilike', '=ilike', 'like', '=like')):
#             self.check_access_rights(cr, uid, 'read')
#             where_query = self._where_calc(cr, uid, args, context=context)
#             self._apply_ir_rules(cr, uid, where_query, 'read', context=context)
#             from_clause, where_clause, where_clause_params = where_query.get_sql()
#             where_str = where_clause and (" WHERE %s AND " % where_clause) or ' WHERE '
#      
#             # search on the name of the contacts and of its company
#             search_name = name
#             if operator in ('ilike', 'like'):
#                 search_name = '%%%s%%' % name
#             if operator in ('=ilike', '=like'):
#                 operator = operator[1:]
#      
#             unaccent = get_unaccent_wrapper(cr)
#      
#             query = """SELECT id
#                          FROM res_partner
#                       {where} ({email} {operator} {percent}
#                            OR {display_name} {operator} {percent})
#                      ORDER BY {display_name}
#                     """.format(where=where_str, operator=operator,
#                                email=unaccent('email'),
#                                display_name=unaccent('display_name'),
#                                percent=unaccent('%s'))
#      
#             where_clause_params += [search_name, search_name]
#             if limit:
#                 query += ' limit %s'
#                 where_clause_params.append(limit)
#             cr.execute(query, where_clause_params)
#             ids = map(lambda x: x[0], cr.fetchall())
#      
#             if ids:
#                 return self.name_get(cr, uid, ids, context)
#             else:
#                 return []
#         return super(res_partner,self).name_search(cr, uid, name, args, operator=operator, context=context, limit=limit)

#     
#     
# res_partner()

class provider_assessment(models.Model):
    _name = 'provider.assessment'
    _inherit = 'mail.thread'
    _description = 'Provider Assessment'
    
    assessed = fields.Boolean(string='Assessed')
    
provider_assessment()

class EOI_ID_configuration(models.Model):
    _name = 'eoi_id.configuration'
    _inherit = 'mail.thread'
    _description = 'EOI ID'
    _rec_name = "eoi_id"

    eoi_id = fields.Char(string='EOI ID', track_visibility='onchange')
    eoi_description = fields.Char(string='EOI Description',track_visibility='onchange')
   
    @api.model
    def create(self, vals):
        vals['eoi_id'] = self.env['ir.sequence'].get('eoi_id.configuration')
        return super(EOI_ID_configuration, self).create(vals)

EOI_ID_configuration()
