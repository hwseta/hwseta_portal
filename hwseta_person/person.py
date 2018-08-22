from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import datetime,date
import calendar
from openerp import tools

class seta_branches(models.Model):
    _name = 'seta.branches'
    
    name = fields.Char(string='Branch Code')
    branch_address = fields.Char(string='Branch Address')
    
    _sql_constraints = [('branch_uniq', 'unique(name)',
            'Branch Code must be unique!'),]
    
seta_branches()

class project_project(models.Model):
    _inherit = 'project.project'
    
#     @api.model
#     def default_get(self, fields_list):
#         res = super(project_project, self).default_get(fields_list=fields_list)
#         all_employers = self.env['res.partner'].search([('employer','=',True)])
#         all_providers = self.env['res.partner'].search([('provider','=',True)])
#         employer_list = [(0,0,{'employer_id':employer.id}) for employer in all_employers]
#         provider_list = [(0,0,{'provider_id':provider.id}) for provider in all_providers]
#         res.update({'emp_ids':employer_list, 'pro_ids':provider_list})
#         return res

    select_all_employer = fields.Boolean(string='Select All Employer')
    select_all_provider = fields.Boolean(string='Select All Provider')
    emp_ids = fields.One2many('partner.project.rel', 'emp_project_id', string='Employers')
    selected_emp_ids = fields.One2many('partner.project.rel.one', 'selected_emp_project_id', string='Employers')
    pro_ids = fields.One2many('partner.project.rel', 'pro_project_id', string='Providers')
    selected_pro_ids = fields.One2many('partner.project.rel.one', 'selected_pro_project_id', string='Providers')

#     employer_ids = fields.Many2many('res.partner', 'empl_proj_rel', 'emp_project_id', string="Employers", domain=[('employer','=',True)])
#     provider_ids = fields.Many2many('res.partner', 'pro_proj_rel', 'pro_project_id', string="Providers", domain=[('provider','=',True)])
#     employer_names = fields.Html(string="Employer Names")
#     provider_names = fields.Html(string="Provider Names")

    ## Employer Groups
    emp_levy_paying = fields.Boolean(string='Levy Paying')
    emp_non_levy_paying = fields.Boolean(string='Non Levy Paying')
    emp_exempt = fields.Boolean(string='Levy Exempt')
    emp_government = fields.Boolean(string='Government')
    emp_university = fields.Boolean(string='University (CHE)')
    emp_tvet_college = fields.Boolean(string='TVET College (DHET)')
    emp_other_group = fields.Boolean(string='Other')
    emp_wsp_status = fields.Boolean(string='WSP Status')
    emp_sanc = fields.Boolean(string='SANC')
    emp_hpsca = fields.Boolean(string='HPSCA')
    emp_sapc = fields.Boolean(string='SAPC')
    emp_ngo_npo = fields.Boolean(string='NGO/NPO')
    emp_cbo = fields.Boolean(string='CBO')
    emp_fbo = fields.Boolean(string='FBO')
    emp_section = fields.Boolean(string='Section 21')
    emp_other_group_info = fields.Char(string='Other', size=70)
    ##
    
#     @api.multi
#     def add_partners(self):
#         context = self._context
#         if context.get('employer',False):
#             emp_proj_data = self.env['partner.project.rel'].search([('select_emp','=',True),('emp_project_id','=',self.id)])
#             for emp_proj in emp_proj_data :
#                 emp_proj.write({'project_terms_and_condition':self.project_terms_and_condition.id,})
#             employer_data = [employer.employer_id for employer in emp_proj_data]
#             msg = "<u><b>Employers Participated</b></u><br>"
#             for employer in employer_data :
#                 msg += "<br><b>"+employer.name+"</b>"
#             self.write({'employer_names':msg})
#         if context.get('provider',False):
#             pro_proj_data = self.env['partner.project.rel'].search([('select_pro','=',True),('pro_project_id','=',self.id)])
#             provider_data = [provider.provider_id for provider in pro_proj_data]
#             msg = "<u><b>Providers Participated</b></u><br>"
#             for provider in provider_data :
#                 msg += "<br><b>"+provider.name+"</b>"
#             self.write({'provider_names':msg})
#         return True

    @api.multi
    def add_partners(self):
        context = self._context
        if context.get('employer', False):
            emp_proj_data = self.env['partner.project.rel'].search([('select_emp','=',True),('emp_project_id','=',self.id)])
            employer_data = [employer.employer_id for employer in emp_proj_data]
            for emp_id in self.selected_emp_ids:
                emp_id.unlink()
            for emp_proj in employer_data:
                emp_proj.write({'project_terms_and_condition': self.project_terms_and_condition.id,})
                employer_vals = [(0, 0, {'select_emp': True,
                                         'employer_id': emp_proj.id,
                                         'employer_sdl_no': emp_proj.employer_sdl_no,
                                        })]
                self.write({'selected_emp_ids': employer_vals})
        if context.get('provider', False):
            pro_proj_data = self.env['partner.project.rel'].search([('select_pro','=',True),('pro_project_id','=',self.id)])
            provider_data = [provider.provider_id for provider in pro_proj_data]
            for pro_id in self.selected_pro_ids:
                pro_id.unlink()
            for pro_proj in provider_data:
                pro_proj.write({'project_terms_and_condition': self.project_terms_and_condition.id,})
                provider_vals = [(0, 0, {'select_pro': True,
                                         'provider_id': pro_proj.id,
                                         'provider_acc_no': pro_proj.provider_accreditation_num,
                                        })]
                self.write({'selected_pro_ids': provider_vals})
        return True

#     @api.multi
#     def add_all_partners(self):
#         context = self._context
#         if context.get('employer',False):
#             emp_proj_data = self.env['partner.project.rel'].search([('emp_project_id','=',self.id)])
#             for emp_proj in emp_proj_data:
#                 emp_proj.write({'select_emp':True,'project_terms_and_condition':self.project_terms_and_condition.id,})
#             employer_data = [employer.employer_id for employer in emp_proj_data]
#             print "employer_data----",employer_data
#             msg = "<u><b>Employers Participated</b></u><br>"
#             for employer in employer_data :
#                 msg += "<br><b>"+employer.name+"</b>"
#             self.write({'employer_names':msg})
#         if context.get('provider',False):
#             pro_proj_data = self.env['partner.project.rel'].search([('pro_project_id','=',self.id)])
#             pro_proj_data.write({'select_pro':True})
#             provider_data = [provider.provider_id for provider in pro_proj_data]
#             msg = "<u><b>Providers Participated</b></u><br>"
#             for provider in provider_data :
#                 msg += "<br><b>"+provider.name+"</b>"
#             self.write({'provider_names':msg})
#         return True

    @api.multi
    def add_all_partners(self):
        context = self._context
        if context.get('employer', False):
            emp_proj_data = self.env['partner.project.rel'].search([('emp_project_id','=',self.id)])
            employer_data = [employer.employer_id for employer in emp_proj_data]
            for emp_id in self.selected_emp_ids:
                emp_id.unlink()
            for emp_proj in employer_data:
                emp_proj.write({'project_terms_and_condition': self.project_terms_and_condition.id,})
                employer_vals = [(0, 0, {'select_emp': True,
                                         'employer_id': emp_proj.id,
                                         'employer_sdl_no': emp_proj.employer_sdl_no,
                                        })]
                self.write({'selected_emp_ids': employer_vals})
        if context.get('provider',False):
            pro_proj_data = self.env['partner.project.rel'].search([('pro_project_id','=',self.id)])
            provider_data = [provider.provider_id for provider in pro_proj_data]
            for pro_id in self.selected_pro_ids:
                pro_id.unlink()
            for pro_proj in provider_data:
                pro_proj.write({'project_terms_and_condition': self.project_terms_and_condition.id,})
                provider_vals = [(0, 0, {'select_pro': True,
                                         'provider_id': pro_proj.id,
                                         'provider_acc_no': pro_proj.provider_accreditation_num,
                                        })]
                self.write({'selected_pro_ids': provider_vals})
        return True

#     @api.multi
#     def clear_partners(self):
#         context = self._context
#         if context.get('employer',False):
#             emp_proj_data = self.env['partner.project.rel'].search([('select_emp','=',True),('emp_project_id','=',self.id)])
#             for employer_proj in emp_proj_data :
#                 employer_proj.write({'select_emp':False})
#             self.write({'employer_names':''})
#         if context.get('provider',False):
#             pro_proj_data = self.env['partner.project.rel'].search([('pro_project_id','=',self.id)])
#             for provider_proj in pro_proj_data :
#                 provider_proj.write({'select_pro':False})
#             self.write({'provider_names':''})
#         return True

    @api.multi
    def clear_partners(self):
        context = self._context
        if context.get('employer',False):
            emp_proj_data = self.env['partner.project.rel.one'].search([('select_emp','=',True),('selected_emp_project_id','=',self.id)])
            for employer_proj in emp_proj_data :
                employer_proj.write({'select_emp':False})
                employer_proj.unlink()
        if context.get('provider',False):
            pro_proj_data = self.env['partner.project.rel.one'].search([('select_pro','=',True),('selected_pro_project_id','=',self.id)])
            for provider_proj in pro_proj_data :
                provider_proj.write({'select_pro':False})
                provider_proj.unlink()
        return True

    @api.multi
    @api.depends('project_types')
    def onchange_category(self, emp_levy_paying, emp_non_levy_paying, emp_exempt, emp_ngo_npo, emp_cbo, emp_fbo, emp_section, emp_government, emp_university, emp_tvet_college, emp_other_group,emp_wsp_status,emp_sanc,emp_hpsca,emp_sapc) :
        res = {}
        domain_val = []
        if emp_levy_paying :
            domain_val.append(('emp_levy_paying','=',True))
        if emp_non_levy_paying :
            domain_val.append(('emp_non_levy_paying','=',True))
        if emp_exempt :
            domain_val.append(('emp_exempt','=',True))
        if emp_ngo_npo :
            domain_val.append(('emp_ngo_npo','=',True))
        if emp_cbo :
            domain_val.append(('emp_cbo','=',True))
        if emp_fbo :
            domain_val.append(('emp_fbo','=',True))
        if emp_section :
            domain_val.append(('emp_section','=',True))
        if emp_government :
            domain_val.append(('emp_government','=',True))
        if emp_university :
            domain_val.append(('emp_university','=',True))
        if emp_tvet_college :
            domain_val.append(('emp_tvet_college','=',True))
        if emp_other_group :
            domain_val.append(('emp_other_group','=',True))
        if emp_wsp_status :
            domain_val.append(('emp_wsp_status','=',True))
        if emp_sanc :
            domain_val.append(('emp_sanc','=',True))
        if emp_hpsca :
            domain_val.append(('emp_hpsca','=',True))
        if emp_sapc :
            domain_val.append(('emp_sapc','=',True))
        if not domain_val :
            return res
        else :
#             print "self.project_types.seta_funding_year.id-------",self.project_types
#             wsp_submission_data = self.env['wsp.submission.track'].search([('fiscal_year','=',self.project_types.seta_funding_year.id)])
#             print "\n\n\n\nwsp_submission_data----------------",wsp_submission_data
#             employer_ids = [employers.employer_id for employers in wsp_submission_data]
#             print " \n\n\n\n\n\nemployers ids -----------------------",employer_ids
            employer_vals = [(0,0,{'employer_id':employer.id,
                                   'employer_sdl_no' : employer.employer_sdl_no,
                                   'project_description':self.project_description,
                                   'category': self.category.id,
                                   'category_type': self.category_type,
                                   }) for employer in self.env['res.partner'].search(domain_val) ]
            res.update({'value':{ 'emp_ids' : employer_vals }})
        return res

project_project()

class res_country_state(models.Model):
    _inherit = 'res.country.state'
    
    user_id = fields.Many2one('res.users', string='Related Users')
    province_code_id = fields.Char("Province Code Id")
res_country_state()

class res_users(models.Model):
    _inherit = 'res.users'
    
    province_ids = fields.One2many('res.country.state','user_id', string='Provinces')
    ## for resolving assert group_ext_id and '.' in group_ext_id, "External ID must be fully qualified"
    @tools.ormcache(skiparg=2)
    def has_group(self, cr, uid, group_ext_id):
        """Checks whether user belongs to given group.

        :param str group_ext_id: external ID (XML ID) of the group.
           Must be provided in fully-qualified form (``module.ext_id``), as there
           is no implicit module to use..
        :return: True if the current user is a member of the group with the
           given external ID (XML ID), else False.
        """
        if group_ext_id:
            assert group_ext_id and '.' in group_ext_id, "External ID must be fully qualified"
            module, ext_id = group_ext_id.split('.')
            cr.execute("""SELECT 1 FROM res_groups_users_rel WHERE uid=%s AND gid IN
                            (SELECT res_id FROM ir_model_data WHERE module=%s AND name=%s)""",
                       (uid, module, ext_id))
            return bool(cr.fetchone())
res_users()

class partner_project_rel(models.Model):
    _name = 'partner.project.rel'
    _inherit = 'mail.thread'
    _rec_name = 'employer_id'

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ Override read_group to show correct group count and default EOI ID group in SDF Portal"""
        domain = [['select_emp', '=', True]]
        ret_val = super(partner_project_rel, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if ret_val:
            for rec in ret_val:
                if rec.has_key('eoi_id_reference_new'):
                    ppr_obj = self.env['partner.project.rel'].search([('eoi_id_reference_new','=',rec['eoi_id_reference_new'])])
                    if ppr_obj:
                        ppr_ids = [ppr_id.id for ppr_id in ppr_obj] 
                        domain.append(['id','in',ppr_ids])
                    else:
                        rec['eoi_id_reference_new_count'] = 0L
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
                return super(partner_project_rel, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            if group.name == "SDP Manager":
                return super(partner_project_rel, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            if group.name == "Provincial Manager":
                return super(partner_project_rel, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            if group.name == "WSP Officer":
                return super(partner_project_rel, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            if group.name == "Provincial Officer":
                return super(partner_project_rel, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            if group.name == "WSP Administrator":
                return super(partner_project_rel, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            if group.name == "General Access":
                return super(partner_project_rel, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
            if group.name == "Auditor Access":
                return super(partner_project_rel, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
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
        return super(partner_project_rel, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)    
    
    select_emp = fields.Boolean(string='Select Employer')
    select_pro = fields.Boolean(string='Select Provider')
    employer_id = fields.Many2one('res.partner', string='Employer', domain=[('employer','=',True)], track_visibility='onchange')
    provider_id = fields.Many2one('res.partner', string='Provider', domain=[('provider','=',True)], track_visibility='onchange')
    emp_project_id = fields.Many2one('project.project', string="Emp Project",track_visibility='onchange')
    category = fields.Many2one('hwseta.project.category', string='Project Category')
    category_type = fields.Selection([('18.1','Employed Learners (18.1)'),('18.2','Unemployed Learners (18.2)')], string="Category Type")
    project_description = fields.Text("Description")
    employer_sdl_no = fields.Char(string='SDL No.', track_visibility='onchange')
    provider_accreditation_num = fields.Char(string='Accreditation No.', track_visibility='onchange')
    pro_project_id = fields.Many2one('project.project', string="Pro Project")

    eoi_apply = fields.Boolean("Apply For EOI",default=False, track_visibility='always')
    eoi_apply_date = fields.Datetime("Apply Date")
    eoi_ext_date = fields.Datetime("EOI Extension Date")
    eoi_ext_request = fields.Boolean("EOI Extension Request",default=False, track_visibility='onchange')
    load_learner_ext_date = fields.Datetime("Load Learner Extension Date", track_visibility='onchange')
    load_learner_ext_request = fields.Boolean("Learner Extension Request",default=False)
    is_extension = fields.Boolean("Is Extension",default=False)
    project_terms_and_condition = fields.Many2one('ir.attachment',string='Project Terms and Conditions', track_visibility='onchange')
    agree_terms = fields.Boolean(string='Agree',default=False, track_visibility='onchange',)
#     is_applicable = fields.Boolean("Is Applicable",default=False)
#     eoi_id_reference = fields.Char(related='emp_project_id.name', store=True, readonly=True, copy=False)
#     eoi_id_reference = fields.Char(related='emp_project_id.eoi_id.', store=True, readonly=True, copy=False)

    @api.multi
    def action_eoi_apply(self):
        if not self.agree_terms:
            raise Warning(_("Please agree for project terms and coditions!!!"))
        if self.emp_project_id:
            qualification_ids = []
            if self.emp_project_id.qualification_ids:
                for qualification in self.emp_project_id.qualification_ids:
                        if qualification.qualification_id:
                            qualification_ids.append(qualification.qualification_id.id)
            project_vals ={
                           'project_types':self.emp_project_id.project_types.id,
                           'project_id':self.emp_project_id.id,
                           'state':'draft',
                           }
            if qualification_ids:
                project_vals.update({ 'qualifications': [(6,0,qualification_ids)]})
            eoi_vals = {
                        'employer_id':self.employer_id.id,
                        'enroll_project_ids':[(0,0,project_vals)],
                        'learning_project_type_id':self.emp_project_id.project_types.id,
                        'learning_project_id':self.emp_project_id.id,
                        'category': self.category.id,
                        'category_type': self.category_type,
                        'employer_sdl_no':self.employer_id.employer_sdl_no,
                        'empl_sic_code':self.employer_id.empl_sic_code and self.employer_id.empl_sic_code.id,
                        'employer_registration_number':self.employer_id.employer_registration_number,
                        'employer_site_no':self.employer_id.employer_site_no,
                        'employer_trading_name':self.employer_id.employer_trading_name,
                        'employer_seta_id':self.employer_id.employer_seta_id and self.employer_id.employer_seta_id.id,
                        
                        }
            self.env['learning.programme'].create(eoi_vals)
            self.write({'eoi_apply':True,'eoi_apply_date':datetime.now(),'agree_terms':True})
        return True
    
    @api.multi
    def action_request_eoi_extension(self):
        self.write({'eoi_ext_request':True})
        if self.eoi_apply == False:
            raise Warning(_("Sorry! Please apply for EOI first"))
        # Mail notification HWSETA Team
        ir_model_data_obj = self.env['ir.model.data']
        mail_template_id = ir_model_data_obj.get_object_reference('hwseta_person', 'email_template_eoi_extension')
        if mail_template_id:
            self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True,context=self.env.context)        
        return True
    
    @api.multi
    def action_request_learner_extension(self):
        self.write({'load_learner_ext_request':True})
        if self.eoi_apply == False:
            raise Warning(_("Sorry! Please apply for EOI first"))
        # Mail notification HWSETA Team
        ir_model_data_obj = self.env['ir.model.data']
        mail_template_id = ir_model_data_obj.get_object_reference('hwseta_person', 'email_template_load_learner_extension')
        if mail_template_id:
            self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True,context=self.env.context)        
        return True    
    
    def action_check_eoi_date(self,cr,uid,context=None):
        current_date = datetime.now()
        employer_ids=self.pool.get('partner.project.rel').search(cr,uid,[('select_emp','=',True)])
        emp_obj = self.pool.get('partner.project.rel').browse(cr,uid,employer_ids)
        for employer in emp_obj:
            project_obj= self.pool.get('project.project').browse(cr,uid,employer.emp_project_id.id)
            if str(current_date) > project_obj.eoi_end_date:
                employer.write({'eoi_apply_date':current_date,'is_extension':True})
            if str(current_date) > project_obj.load_learner_end_date:
                employer.write({'eoi_apply_date':current_date,'is_extension':True})
        return True
       
    @api.multi
    def write(self,vals):
        res=super(partner_project_rel,self).write(vals)
        project_obj = self.env['project.project'].search([('id','=',self.emp_project_id.id)])
        if self.eoi_ext_date:
            if self.eoi_ext_date < project_obj.start_date or self.eoi_ext_date > project_obj.end_date:
                raise Warning(_("Sorry!! EOI Extension Date should be between the range of Project Start Date and Project End Date"))
        if self.load_learner_ext_date:
            if self.eoi_ext_date:
                if self.load_learner_ext_date < project_obj.eoi_start_date or self.load_learner_ext_date > self.eoi_ext_date:
                    raise Warning(_("Sorry!! Load Learner Extension Date should be between the range of EOI Start Date and EOI Extension Date "))
            elif not self.eoi_ext_date:
                if self.load_learner_ext_date < project_obj.eoi_start_date or self.load_learner_ext_date < project_obj.eoi_end_date:
                    raise Warning(_("Sorry!! Load Learner Extension Date should be between the range of EOI Start Date and EOI End Date"))        
        return res
    
partner_project_rel()


class partner_project_rel_one(models.Model):
    _name = 'partner.project.rel.one'
#     _rec_name = 'employer_id'

    select_emp = fields.Boolean(string='Select Employer')
    employer_id = fields.Many2one('res.partner', string='Employer', domain=[('employer','=',True)])
    employer_sdl_no = fields.Char(string='SDL No.', track_visibility='onchange')
    selected_emp_project_id = fields.Many2one('project.project', string="Emp Project",track_visibility='onchange')

    select_pro = fields.Boolean(string='Select Provider')
    provider_id = fields.Many2one('res.partner', string='Provider', domain=[('provider','=',True)])
    provider_acc_no = fields.Char(string='Accreditation No.', track_visibility='onchange')
    selected_pro_project_id = fields.Many2one('project.project', string="Pro Project")

class employer_type(models.Model):
    _name = 'employer.type'
    
    name = fields.Char(string='Name')
    
employer_type()

## Adding Banking related fields in partner bank details
class res_partner_bank(models.Model):
    _inherit = 'res.partner.bank'
    
    grant_type = fields.Selection([('mandatory','Mandatory'),('discretionary','Discretionary'),('both','Both')], string='Grant Account Type')
    branch_name = fields.Char(string='Branch Name')
    branch_code = fields.Char(string='Branch Code')
    ifsc_code = fields.Char(string='IFSC Code')
    other = fields.Text(string='Other')
    city = fields.Many2one('res.city', string='City') 
    
    @api.model
    def create(self, vals):
        account_number = vals.get('acc_number',False)
        if account_number:
            ## Getting existing bank account numbers    
            acc_numbers = [partner_bank.acc_number for partner_bank in self.search([])]
            if account_number in acc_numbers :
                raise Warning(_('Account number already exists !'))
            ## TO DO : Parent and child employer should share the same account number. Need to add enhancement in the future for the same.
        res = super(res_partner_bank, self).create(vals)
        return res
    
#     _sql_constraints = [('acc_no_uniq', 'unique(acc_number)',
#             'Account Number must be unique!'),]
    
res_partner_bank()

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    @api.multi
    def _get_default_seta(self):
        seta_id = None
        seta_data = self.env['seta.branches'].search([('name','=','11')])
        if seta_data :
            seta_id = seta_data.id
        return seta_id
    
    @api.one
    @api.depends('employees_count')
    def _get_organisation_size(self):
        if not self.env['res.users'].has_group('hwseta_etqe.group_providers'):
            if self.employees_count <= 49:
                self.organisation_size= 'small'
            elif self.organisation_size > 49 or self.organisation_size <=149:
                self.organisation_size = 'medium'
            else:
                self.organisation_size = 'large'
            
    ## Employer Fields
    employer = fields.Boolean(string='Employer')
    employer_department = fields.Boolean(string='Department')
    employer_sdl_no = fields.Char(string='SDL No.', track_visibility='onchange', size=10)
    employer_site_no = fields.Char(string='Site No.', track_visibility='onchange', size=10)
    employer_seta_id = fields.Many2one('seta.branches', string='Employer SETA Id.', default=_get_default_seta, track_visibility='onchange')
    
#     employer_seta_id = fields.Char(string='SETA Id.', size=3)
#     employer_sic_code = fields.Char(string='SIC Code',track_visibility='onchange', size=10)
    emp_reg_number_type = fields.Selection([('cipro_number','Cipro Number'),('comp_reg_no','Company Registration Number')], string='Registration Number Type')
    employer_registration_number = fields.Char(string='Registration Number',track_visibility='onchange', size=20)
    employer_vat_number = fields.Char(string='VAT Number',track_visibility='onchange', size=20)
    employer_trading_name = fields.Char(string='Trading Name',track_visibility='onchange')
    partnership = fields.Selection([('private','Private'),('public','Public'),('private_public','Private Public')], string='Partnership')
    total_annual_payroll = fields.Float(string='Total Anual Payroll')
    organisation_size = fields.Selection([('small','Small (0-49)'),('medium','Medium (50-149)'),('large','Large (150+)')], compute='_get_organisation_size', string='Organisation Size', readonly=True)
    
    ## Will be in seperate Employer Address Tab
    #TODO : Needs to remove duplicate fields postal,physical address, longitude and lattitude.
    employer_approval_status_id = fields.Char(string='Approval Status Id',track_visibility='onchange', size=10)
    employer_approval_status_start_date = fields.Date(string='Approval Status Start Date',track_visibility='onchange')
    employer_approval_status_end_date = fields.Date(string='Approval Status End Date',track_visibility='onchange')
    employer_approval_status_num = fields.Char(string='Approval Status Number',track_visibility='onchange', size=20)
    ## May be gmapper module will replace this.
    employer_latitude_degree = fields.Char(string='Latitude Degree',track_visibility='onchange',size=3)
    employer_latitude_minutes = fields.Char(string='Latitude Minutes',track_visibility='onchange',size=2)
    employer_latitude_seconds = fields.Char(string='Latitude Seconds',track_visibility='onchange',size=6)
    employer_longitude_degree = fields.Char(string='Longitude Degree',track_visibility='onchange',size=2)
    employer_longitude_minutes = fields.Char(string='Longitude Minutes',track_visibility='onchange',size=2)
    employer_longitude_seconds = fields.Char(string='Longitude Seconds',track_visibility='onchange',size=6)
    
    employer_main_sdl_no = fields.Char(string='Main SDL No.', track_visibility='onchange',size=10)
    employer_filler01 = fields.Char(string='Filler01', track_visibility='onchange',size=20)
    employer_filler02 = fields.Char(string='Filler02', track_visibility='onchange',size=4)
    employer_date_stamp = fields.Date(string='Date Stamp',track_visibility='onchange')
    dormant = fields.Boolean(string='Dormant')
    university = fields.Boolean(string='University')
    college = fields.Boolean(string='College')
    nsfas = fields.Boolean(string='NSFAS')
    
#     added by Prathmesh As anil sir told before UAT for Org.Sector
    emp_health = fields.Boolean(string='Health')
    emp_walfare = fields.Boolean(string='Welfare')
    emp_other = fields.Boolean(string='Other')
    emp_other_info = fields.Char(string='Other',track_visibility='onchange', size=70)
    
    emp_levy_paying = fields.Boolean(string='Levy Paying')
    emp_non_levy_paying = fields.Boolean(string='Non Levy Paying')
    emp_exempt = fields.Boolean(string='Levy Exempt')
    emp_government = fields.Boolean(string='Government')
    emp_university = fields.Boolean(string='University (CHE)')
    emp_tvet_college = fields.Boolean(string='TVET College (DHET)')
    emp_other_group = fields.Boolean(string='Other')
    emp_wsp_status = fields.Boolean(string='WSP Status')
    emp_sanc = fields.Boolean(string='SANC')
    emp_hpsca = fields.Boolean(string='HPSCA')
    emp_sapc = fields.Boolean(string='SAPC')
    emp_other_group_info = fields.Char(string='Other', size=70)
    emp_ngo_npo = fields.Boolean(string='NGO/NPO')
    emp_cbo = fields.Boolean(string='CBO')
    emp_fbo = fields.Boolean(string='FBO')
    emp_section = fields.Boolean(string='Section 21')
    employees_count = fields.Integer(string='Employees as per Employment Profile',readonly = True)
    ## Extra groups found in Learnership Approval Schedule Doc
#     emp_public = fields.Boolean(string='Public')
#     emp_private = fields.Boolean(string='Private')
#     emp_sme = fields.Boolean(string='SME')
    type_of_employer = fields.Many2one('employer.type', String='Employer Type')
    ## Provider Fields
    provider_suburb = fields.Char(string='Suburb')
#     provider_physical_suburb = fields.Char(string='Physical Suburb')
    provider_physical_suburb = fields.Many2one('res.suburb',string='Physical Suburb')
#     provider_postal_suburb = fields.Char(string='Postal Suburb')

    provider_trading_name = fields.Char(string='Trading Name',track_visibility='onchange', size=70)

    provider_postal_suburb = fields.Many2one('res.suburb',string='Postal Suburb')
    provider = fields.Boolean(string='Provider')
    provider_code = fields.Char(string='Code', help="Provider_Code",track_visibility='onchange',size=50)
    provider_etqe_id = fields.Char(string='ETQE Id', help="Provider_ETQE_Id",track_visibility='onchange',size=10)
    provider_sars_number = fields.Char(string='SDL No.',track_visibility='onchange', help="Provider_Sars_Number",size=50)
    provider_contact_name = fields.Char(string='Contact Name',track_visibility='onchange', help="Provider_Contact_Name",size=50)
    provider_accreditation_num = fields.Char(string='Accreditation No.',track_visibility='onchange', help="Provider_Accreditation_Num",size=50)
    provider_etqa_decision_number = fields.Char(string='Decision No.',track_visibility='onchange', help="Etqe_Decision_Number",size=20)
    provider_type_id = fields.Char(string='Provider Type',track_visibility='onchange', help="Provider_Type_Id",size=50)
    provider_start_date = fields.Date(string='Start Date',track_visibility='onchange', default=datetime.now() ,help="Provider_Start_Date")
    provider_end_date = fields.Date(string='End Date',track_visibility='onchange', help="Provider_End_Date")
    provider_class_Id = fields.Char(string='Provider Class',track_visibility='onchange', help="Provider_Class_Id",size=50)
    provider_status_Id = fields.Char(string='Provider Status',track_visibility='onchange', help="Provider_Status_Id",size=50)
    provider_sdl_no = fields.Char(string='SDL No',track_visibility='onchange', help="SDL_No",size=50)
    provider_date_stamp = fields.Datetime(string='Date Stamp',track_visibility='onchange', help="Date_Stamp")
    is_qdm_provider = fields.Boolean("QDM")
    #TODO : Needs to remove duplicate fields postal,physical address, longitude and lattitude.
    provider_latitude_degree = fields.Char(string='Latitude ( Degree )', help="Latitude_Degree",track_visibility='onchange',size=50)
    provider_latitude_minutes = fields.Char(string='Latitude ( Minutes )', help="Latitude_Minutes",track_visibility='onchange',size=50)
    provider_latitude_seconds = fields.Char(string='Latitude ( Seconds )', help="Latitude_Seconds",track_visibility='onchange',size=50)
    provider_longitude_degree = fields.Char(string='Longitude ( Degree )', help="Longitude_Degree",track_visibility='onchange',size=50)
    provider_longitude_minutes = fields.Char(string='Longitude ( Minutes )', help="Longitude_Minutes",track_visibility='onchange',size=50)
    provider_longitude_seconds = fields.Char(string='Longitude ( Seconds )', help="Longitude_Seconds",track_visibility='onchange',size=50)
    
    provider_latitude_degree_p = fields.Char(string='Latitude ( Degree )', help="Latitude_Degree",track_visibility='onchange',size=50)
    provider_latitude_minutes_p = fields.Char(string='Latitude ( Minutes )', help="Latitude_Minutes",track_visibility='onchange',size=50)
    provider_latitude_seconds_p = fields.Char(string='Latitude ( Seconds )', help="Latitude_Seconds",track_visibility='onchange',size=50)
    provider_longitude_degree_p = fields.Char(string='Longitude ( Degree )', help="Longitude_Degree",track_visibility='onchange',size=50)
    provider_longitude_minutes_p = fields.Char(string='Longitude ( Minutes )', help="Longitude_Minutes",track_visibility='onchange',size=50)
    provider_longitude_seconds_p = fields.Char(string='Longitude ( Seconds )', help="Longitude_Seconds",track_visibility='onchange',size=50)
  
    
    
    provider_website_address = fields.Char(string='Website Address', help="Provider_Website_Address",track_visibility='onchange',size=50)
    accreditation = fields.Boolean(string='Accreditation')
    
    ## Fields for both Provider and Employer.
    physical_address_1 = fields.Char(string='Physical Address1', help="Provider Physical Address 1",track_visibility='onchange',size=50)
    physical_address_2 = fields.Char(string='Physical Address2', help="Provider Physical Address 2",track_visibility='onchange',size=50)
    physical_address_3 = fields.Char(string='Physical Address3', help="Provider Physical Address 3",track_visibility='onchange',size=50)
    
    emp_physical_address_1 = fields.Char(string='Employer Physical Address 1', help="Employer Physical Address 1",track_visibility='onchange',size=50)
    emp_physical_address_2 = fields.Char(string='Employer Physical Address 2', help="Employer Physical Address 2",track_visibility='onchange',size=50)
    emp_physical_address_3 = fields.Char(string='Employer Physical Address 3', help="Employer Physical Address 3",track_visibility='onchange',size=50)
#     emp_physical_suburb = fields.Char(string='Employer Physical Suburb', help='Employer Physical Suburb', size=50)
    emp_physical_suburb = fields.Many2one('res.suburb',string='Employer Physical Suburb')
    
    postal_address_1 = fields.Char(string='Postal Address1', help="Provider Postal Address 1",track_visibility='onchange',size=50)
    postal_address_2 = fields.Char(string='Postal Address2', help="Provider Postal Address 2",track_visibility='onchange',size=50)
    postal_address_3 = fields.Char(string='Postal Address3', help="Provider Postal Address 3",track_visibility='onchange',size=50)
    
    emp_postal_address_1 = fields.Char(string='Employer Postal Address 1', help="Employer Postal Address 1",track_visibility='onchange',size=50)
    emp_postal_address_2 = fields.Char(string='Employer Postal Address 2', help="Employer Postal Address 2",track_visibility='onchange',size=50)
    emp_postal_address_3 = fields.Char(string='Employer Postal Address 3', help="Employer Postal Address 3",track_visibility='onchange',size=50)
    city = fields.Many2one('res.city', string='Work City', track_visibility='onchange')
    street3 = fields.Char(string='Street3', help='Street3', size=50)
#     suburb = fields.Char(string='Suburb', help='Employer Suburb', size=50)
    suburb = fields.Many2one('res.suburb',string='Suburb',track_visibility='onchange')
#     emp_postal_suburb = fields.Char(string='Employer Postal Suburb', help='Employer Postal Suburb', size=50)
    emp_postal_suburb = fields.Many2one('res.suburb',string='Employer Postal Suburb')
    
    postal_address_code = fields.Char(string='Postal Address Code',track_visibility='onchange', size=4)
    physical_address_code = fields.Char(string='Physical Address Code',track_visibility='onchange', size=4)
    
    emp_postal_address_code = fields.Char(string='Employer Postal Address Code',track_visibility='onchange', size=4)
    emp_physical_address_code = fields.Char(string='Employer Physical Address Code',track_visibility='onchange', size=4)
    
#     city_physical = fields.Char(string='Physical City',track_visibility='onchange')
    city_physical = fields.Many2one('res.city', string='Provider Physical City', track_visibility='onchange')
#     city_postal = fields.Char(string='Postal City',track_visibility='onchange')
    city_postal = fields.Many2one('res.city', string='Provider Postal City', track_visibility='onchange')
    
#     emp_city_physical = fields.Char(string='Physical City',track_visibility='onchange')
#     emp_city_postal = fields.Char(string='Postal City',track_visibility='onchange')
    emp_city_physical = fields.Many2one('res.city', string='Physical City',track_visibility='onchange')
    emp_city_postal = fields.Many2one('res.city', string='Postal City',track_visibility='onchange')
    
    zip_physical = fields.Char(string='Provider Physical Zip',track_visibility='onchange')
    zip_postal = fields.Char(string='Provider Postal Zip',track_visibility='onchange')
    
    emp_zip_physical = fields.Char(string='Employer Physical Zip',track_visibility='onchange')
    emp_zip_postal = fields.Char(string='Employer Postal Zip',track_visibility='onchange')
    
    country_code_physical = fields.Many2one('res.country', string='Provider Physical Country Code', track_visibility='onchange')
    country_code_postal = fields.Many2one('res.country', string='Provider Postal Country Code', track_visibility='onchange')
    
    emp_country_code_physical = fields.Many2one('res.country', string='Employer Physical Country Code', track_visibility='onchange')
    emp_country_code_postal = fields.Many2one('res.country', string='Employer Postal Country Code', track_visibility='onchange')
    
    province_code_physical = fields.Many2one('res.country.state', string='Physical Province Code',track_visibility='onchange')
    province_code_postal = fields.Many2one('res.country.state', string='Postal Province Code',track_visibility='onchange')
    
    emp_province_code_physical = fields.Many2one('res.country.state', string='Employer Physical Province Code',track_visibility='onchange')
    emp_province_code_postal = fields.Many2one('res.country.state', string='Employer Postal Province Code',track_visibility='onchange')
    ## Extra documents
    levy_exempt_certificate = fields.Many2one('ir.attachment', string='Levy Exempt Certificate')
    npo_certificate = fields.Many2one('ir.attachment', string='NPO Certificate')
    mand_grant_banking_details = fields.Many2one('ir.attachment', string='Mandatory Grant Banking Details')
    disc_grant_banking_details = fields.Many2one('ir.attachment', string='Discretionary Grant Banking Details')
    bbee_certificate = fields.Many2one('ir.attachment', string='B-BEE Certificate')
    
    ## Organisation Contact Fields
    surname = fields.Char(string='Surname')
    initials = fields.Char(string='Initials')
    ## Use title existing field
    ## Use fax existing field
    urban_rural = fields.Char(string='Urban Rural')
    
    _sql_constraints = [('vat_no_uniq', 'unique(employer_vat_number)',
            'VAT number must be unique!'),]
    
#     emp_project_id = fields.Many2one('project.project', string="Emp Project")
#     pro_project_id = fields.Many2one('project.project', string="Pro Project")
#     select_emp = fields.Boolean(string='Select Employer')
#     select_pro = fields.Boolean(string='Select Provider')
#     provider_contact_ids = fields.One2many('provider.contact', 'provider_contact_id', 'Provider Contact',readonly=True )
#     qualification_line = fields.One2many('provider.qualification.line.partner', 'line_id', 'Qualification Lines', readonly=True)
#     qualification_id =  fields.Many2one("provider.qualification", 'Qualification', ondelete='restrict')
    
    @api.multi
    def open_map_addr(self, street, city, state, country, zip):
        url="http://maps.google.com/maps?oi=map&q="
        if street:
            url+=street.replace(' ','+')
        if city:
            url+='+'+city.name.replace(' ','+')
        if state:
            url+='+'+state.name.replace(' ','+')
        if country:
            url+='+'+country.name.replace(' ','+')
        if zip:
            url+='+'+zip.replace(' ','+')
        return {
        'type': 'ir.actions.act_url',
        'url':url,
        'target': 'new'
        }
        
    @api.multi
    def onchange_provider_postal_suburb(self, person_postal_suburb):
        res = {}
        if not person_postal_suburb:
            return res
        if person_postal_suburb:
            sub_res = self.env['res.suburb'].browse(person_postal_suburb)
            res.update({'value':{'zip_postal':sub_res.postal_code}})
        return res
    
    @api.multi
    def onchange_provider_physical_suburb(self, provider_physical_suburb):
        res = {}
        if not provider_physical_suburb:
            return res
        if provider_physical_suburb:
            sub_res = self.env['res.suburb'].browse(provider_physical_suburb)
            res.update({'value':{'zip_physical':sub_res.postal_code}})
        return res
    
    
    
    
    
    @api.multi
    def country_for_province(self, province):
        state = self.env['res.country.state'].browse(province)
        return state.country_id.id
    
    @api.multi
    def physical_addr_map(self):
        return self.open_map_addr(self.physical_address_1, self.city_physical, self.province_code_physical, self.country_code_physical, self.zip_physical)    
    
    @api.multi
    def postal_addr_map(self):
        return self.open_map_addr(self.postal_address_1, self.city_postal, self.province_code_postal, self.country_code_postal, self.zip_postal)
    
res_partner()


class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    ## SDF Related Fields
    
    national_id = fields.Char(string='National Id',track_visibility='onchange', size=13)
    person_alternate_id = fields.Char(string='Person Alternate Id',track_visibility='onchange', size=20)
    alternate_id_type_id = fields.Char(string='Alternate Type Id',track_visibility='onchange', size=3)
    alternate_id_type = fields.Selection([('saqa_member', '521 - SAQA Member ID'), ('passport_number', '527 - Passport Number'), ('drivers_license','529 - Drivers License'), ('temporary_id_number','531 - Temporary ID number'), ('none', '533 - None'), ('unknown','535 - Unknown'), ('student_number', '537 - Student number'), ('work_permit_number', '538 - Work Permit Number'),('employee_number','539 - Employee Number'),('birth_certificate_number','540 - Birth Certificate Number'),('hsrc_register_number',' 541 - HSRC Register Number'),('etqe_record_number','561 - ETQA Record Number'),('refugee_number','565 - Refugee Number')], string='Alternate ID Type')
#     equity_code = fields.Char(string='Equity Code',track_visibility='onchange', size=10)
    home_language_code = fields.Many2one('res.lang', string='Home Language Code',track_visibility='onchange', size=6)
    home_lang_saqa_code = fields.Selection([('eng','Eng'),('afr','Afr'),('xho','Xho'),('set','Set'),('zul','Zul'),('sep','Sep'),('tsh','Tsh'),('ses','Ses'),('xit','Xit'),('swa','Swa'),('nde','Nde'),('u','U'),('oth','Oth')], string='Home Lanaguage SAQA Code')
    nationality_saqa_code = fields.Selection([('sa','SA')], string='Nationality SAQA Code')
    citizen_resident_status_code = fields.Selection([('sa','SA - South Africa'),('dual','D - Dual (SA plus other)'),('other','O - Other'),('PR','PR - Permanent Resident'),('unknown','U - Unknown')],string='Citizen Status')
    citizen_status_saqa_code = fields.Selection([('sa','SA'),('d','D'),('o','O'),('pr','PR'),('u','U')], string='Citizen Status SAQA Code')
    
    filler01 = fields.Char(string='Filler01',track_visibility='onchange', size=2)
    filler02 = fields.Char(string='Filler02',track_visibility='onchange', size=10)
    person_last_name = fields.Char(string='Last Name',track_visibility='onchange', size=45)
    person_middle_name = fields.Char(string='Middle Name',track_visibility='onchange', size=50)
    person_title = fields.Selection([('adv', 'Adv.'), ('dr', 'Dr'),('mr', 'Mr'),('mrs', 'Mrs'), ('ms', 'Ms'), ('prof', 'Prof')], string='Title', track_visibility='onchange')
    person_name = fields.Char(string='First Name',track_visibility='onchange', size=50)
    
    person_birth_date = fields.Date(string='Birth Date',track_visibility='onchange')
    person_suburb = fields.Many2one('res.suburb',string='Suburb')
    person_home_suburb = fields.Many2one('res.suburb',string='Home Suburb')
    person_postal_suburb = fields.Many2one('res.suburb',string='Postal Suburb')
    person_home_address_1 = fields.Char(string='Home Address 1',track_visibility='onchange', size=50)
    person_home_address_2 = fields.Char(string='Home Address 2',track_visibility='onchange', size=50)
    person_home_address_3 = fields.Char(string='Home Address 3',track_visibility='onchange', size=50)
    person_postal_address_1 = fields.Char(string='Postal Address 1',track_visibility='onchange', size=50)
    person_postal_address_2 = fields.Char(string='Postal Address 2',track_visibility='onchange', size=50)
    person_postal_address_3 = fields.Char(string='Postal Address 3',track_visibility='onchange', size=50)
    person_home_addr_postal_code = fields.Char(string='Home Addr Postal Code',track_visibility='onchange', size=4)
    person_home_addr_post_code = fields.Char(string='Home Addr Post Code',track_visibility='onchange', size=4)
    person_cell_phone_number = fields.Char(string='Cell Phone Number',track_visibility='onchange', size=10)
    person_fax_number = fields.Char(string='Tele Fax Number ',track_visibility='onchange', size=10)
    person_home_city = fields.Many2one('res.city', string='Home City',track_visibility='onchange')
    person_postal_city = fields.Many2one('res.city', string='Postal City',track_visibility='onchange')
    person_home_zip = fields.Char(string='Home Zip',track_visibility='onchange')
    person_postal_zip = fields.Char(string='Postal Zip',track_visibility='onchange')
    country_home = fields.Many2one('res.country', string='Home Country', track_visibility='onchange')
    country_postal = fields.Many2one('res.country', string='Postal Country', track_visibility='onchange')
    work_address2 = fields.Char(string='Work Address 2', track_visibility='onchange')
    work_address3 = fields.Char(string='Work Address 3', track_visibility='onchange')
    work_city = fields.Many2one('res.city', string='Work City', track_visibility='onchange')
    work_province = fields.Many2one('res.country.state', string='Work Province',track_visibility='onchange')
    work_zip = fields.Char(string='Work Zip', track_visibility='onchange')
    work_country= fields.Many2one('res.country', string='Work Country', track_visibility='onchange') 

    province_code = fields.Many2one('res.country.state', string='Province Code', track_visibility='onchange')
    person_home_province_code = fields.Many2one('res.country.state', string='Home Province Code', track_visibility='onchange')
    person_postal_province_code = fields.Many2one('res.country.state', string='Postal Province Code',track_visibility='onchange')
    provider_code = fields.Char(string='Provider Code',track_visibility='onchange', size=20)
    
    provider_etqe_id = fields.Integer(string='Provider ETQE Id',track_visibility='onchange', size=10)
    person_previous_lastname = fields.Char(string='Previous Lastname',track_visibility='onchange', size=45)
    person_previous_alternate_id = fields.Char(string='Previous Alternate Id',track_visibility='onchange', size=20)
    person_previous_alternate_id_type_id = fields.Char(string='Previous Alternate Id Type Id',track_visibility='onchange', size=3)
    person_previous_provider_code = fields.Char(string='Previous Provider Code',track_visibility='onchange', size=20)
    person_previous_provider_etqe_id = fields.Integer(string='Previous Provider ETQE Id',track_visibility='onchange', size=10)
    
    seeing_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')],string='Seeing Rating Id',track_visibility='onchange')
    hearing_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')],string='Hearing Rating Id',track_visibility='onchange')
    walking_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')],string='Walking Rating Id',track_visibility='onchange')
    remembering_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')],string='Remembering Rating Id',track_visibility='onchange')
    communicating_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')],string='Communicating Rating Id',track_visibility='onchange')
    self_care_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')],string='Self Care Rating Id',track_visibility='onchange')
    last_school_emis_no = fields.Char(string='Last School EMIS No',track_visibility='onchange',size=20)
    last_school_year = fields.Integer(string='Last School Year',track_visibility='onchange',size=4)
    statssa_area_code = fields.Integer(string='STATSSA Area Code',track_visibility='onchange',size=20)
    popi_act_status_id = fields.Integer(string='POPI Act Status Id',track_visibility='onchange',size=2)
    popi_act_status_date = fields.Date(string='POPI Act Status Date',track_visibility='onchange')
    date_stamp = fields.Date(string='Date Stamp',track_visibility='onchange')
    is_sdf = fields.Boolean(string='SDF',track_visibility='onchange')
    is_learner = fields.Boolean(string='Learner',track_visibility='onchange')
    is_learner_from_assessment = fields.Boolean(string='Learner', default=False, track_visibility='onchange')

    seta_elements = fields.Boolean(string='Seta Elements',track_visibility='onchange')
    
    department = fields.Char(string='Department',track_visibility='onchange')
    job_title = fields.Char(string='Job Name',track_visibility='onchange')
    manager = fields.Char(string='Manager',track_visibility='onchange')
    work_address = fields.Char(string='Work Address',track_visibility='onchange')
    address_home = fields.Char(string='Home Address',track_visibility='onchange')
    bank_account_number = fields.Char(string='Bank Account Number',track_visibility='onchange')
    certificate_no = fields.Char(string='Qualification & Certificate No',track_visibility='onchange')
    maiden_name = fields.Char(string='Maiden Name',track_visibility='onchange')
    detail_surname = fields.Char(string='Detail Surname',track_visibility='onchange')
    rsa_identity_no = fields.Char(string='RSA Identity No',track_visibility='onchange')
    learner_reg_no = fields.Char(string='Learner Reg No',track_visibility='onchange')
    method_of_communication = fields.Selection([('cell_phone','Cell Phone'),('email','Email')],string='Method of Communication')
    learner_status = fields.Char(string='Learners Status',track_visibility='onchange')
    record_last_update = fields.Date(string='Record Last Updated',track_visibility='onchange')
    status_comments = fields.Char(string='Status Comment',track_visibility='onchange')
    disability_status = fields.Selection([
                                                    ('sight','Sight ( even with glasses )'),
                                                    ('hearing','Hearing ( even with h.aid )'),
                                                    ('communication','Communication ( talk/listen)'),
                                                    ('physical','Physical ( move/stand, etc)'),
                                                    ('intellectual','Intellectual ( learn,etc)'),
                                                    ('emotional','Emotional ( behav/psych)'),
                                                    ('multiple','Multiple'),
                                                    ('disabled','Disabled but unspecified'),
                                                    ('none','None')], string='Disability Status')
    disability_status_saqa = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('9','9'),('n','N')], string='Disability SAQA Code')
    dissability = fields.Selection([('yes','Yes'),('no','No')], string="Disability")
#     highest_education = fields.Char(string='Highest Education',track_visibility='onchange')
    highest_education_level = fields.Selection([('abet_level_1','Abet Level 1'),('abet_level_2','Abet Level 2'),('abet_level_3','Abet Level 3'),('abet_level_4','Abet Level 4'),('nqf123','NQF 1,2,3'),('nqf45','NQF 4,5'),('nqf67','NQF 6,7'),('nqf8910','NQF 8,9,10')],string='Highest Education Level')
    cell = fields.Char(string='Mobile Number ',track_visibility='onchange')
    status_reason = fields.Selection([('workplace_learning', '500 - Workplace learning')],'Learner Status Reason',track_visibility='onchange')
    wsp_year = fields.Selection([('2015', '2015'),('2016', '2016')],'WSP Year',track_visibility='onchange') 
    status_effective_date = fields.Date(string='Status Effective Date',track_visibility='onchange')
    last_updated_operator = fields.Char(string='Last Updated Operator',track_visibility='onchange')
    branch_id = fields.Many2one('hr.department', string='Branch',track_visibility='onchange', domain=[('is_branch','=',True)])
    
    ## Assesors Related Fields
    is_assessors = fields.Boolean(string='Assessors')
    
    ## Moderators Related Fields
    is_moderators = fields.Boolean(string='Moderators')
    assessor_seq_no = fields.Char(string='Assessor ID ')
    moderator_seq_no = fields.Char(string='Moderator ID')
    
    start_date = fields.Date(string = "Start Date")
    end_date = fields.Date(string = "End Date")
    signature = fields.Binary(string='Signature')
    
    provider_id = fields.Many2one('res.partner', string="Provider",track_visibility='onchange', domain=[('provider','=',True)])
    provider_accreditation_num = fields.Char(string='Provider Identity Number',track_visibility='onchange', help="Provider Identity Number",size=50)
    cont_number_home = fields.Char(string='Home Number', track_visibility='onchange', size=10)
    cont_number_office = fields.Char(string='Office Number', track_visibility='onchange', size=10)
#     id_document = fields.Binary(string='ID Document')
    id_document = fields.Many2one('ir.attachment', string='ID Document', help='Upload Document')
    
    african = fields.Boolean(string='Is African')
#     dissability = fields.Selection([('yes','Yes'),('no','No')], string="Dissability")
    ## Banking Details
    bank_name = fields.Char(string='Bank Name')
    branch_code = fields.Char(string='Branch Code')
    same_as_home = fields.Boolean(string='Same As Home Address')
    sdf_type = fields.Selection([('internal','Internal'),('consultant','Consultant')], string='SDF Type')
    #Assessor Document
    registrationdoc = fields.Many2one('ir.attachment', string='Registration Documents')
    professionalbodydoc = fields.Many2one('ir.attachment', string='Professional body')
    sram_doc = fields.Many2one('ir.attachment', string='Statement')
    cv_document = fields.Many2one('ir.attachment',string="CV Document")
    #Moderator Document
    moderator_registrationdoc = fields.Many2one('ir.attachment', string='Registration Documents')
    moderator_professionalbodydoc = fields.Many2one('ir.attachment', string='Professional body')
    moderator_sram_doc = fields.Many2one('ir.attachment', string='Statement')
    moderator_cv_document = fields.Many2one('ir.attachment',string="CV Document")
    moderator_unknown_type_document = fields.Many2one('ir.attachment',string="Type Document")
    
    gender_saqa_code = fields.Selection([('m','M'),('f','F')], string='Gender SAQA Code')
    equity = fields.Selection([('black_african', 'Black: African'), ('black_indian', 'Black: Indian / Asian'), ('black_coloured', 'Black: Coloured'), ('other', 'Other'), ('unknown', 'Unknown'), ('white', 'White')], string='Equity')
    equity_saqa_code = fields.Selection([('ba','BA'),('bi','BI'),('bc','BC'),('oth','Oth'),('u','U'),('wh','Wh')], string='Equity SAQA Code')
    socio_economic_status = fields.Selection([('employed','Employed'),('unemployed','Unemployed, seeking work'),
                                            ('Not working, not looking','Not working, not looking'),
                                            ('Home-maker (not working)','Home-maker (not working)'),
                                            ('Scholar/student (not w.)','Scholar/student (not w.)'),
                                            ('Pensioner/retired (not w.)','Pensioner/retired (not w.)'),
                                            ('Not working - disabled','Not working - disabled'),
                                            ('Not working - no wish to w','Not working - no wish to w'),
                                            ('Not working - N.E.C.','Not working - N.E.C.'),
                                            ('N/A: aged <15','N/A: aged <15'),
                                            ('N/A: Institution','N/A: Institution'),
                                            ('Unspecified','Unspecified'),], string='Socio Economic Status')
    socio_economic_saqa_code = fields.Selection([('1','01'),('2','02'),('3','03'),('4','04'),('6','6'),('7','07'),('8','08'),('9','09'),('10','10'),('97','97'),('98','98'),('U','U')], string='Socio Economic Status SAQA Code')
    highest_education = fields.Char(string='Highest Education')
    current_occupation = fields.Char(string='Current Occupation')
    years_in_occupation = fields.Char(string='Years in Occupation')
    initials = fields.Char(string='Initials')
    work_municipality = fields.Many2one('res.municipality', string='Working Municipality')
    physical_municipality = fields.Many2one('res.municipality', string='Physical Municipality')
    postal_municipality = fields.Many2one('res.municipality', string='Postal Municipality')
    marital = fields.Selection(selection_add=[('widow','Widow')])
    sdf_letter_from_employer=fields.Many2one("ir.attachment",string="Letter of SDF appointment from employer")
    unknown_type = fields.Selection([
              ('political_asylum','Political Asylum'),
              ('refugee', 'Refugee'),
           ], string='Type',
           track_visibility='onchange', copy=False)
    unknown_type_document=fields.Many2one('ir.attachment',string="Type Document")    
    password = fields.Char("Password")
    primary_secondary = fields.Selection([('primary','Primary'),('secondary','Secondary')], string='Internal Type')
    
#     _sql_constraints = [('idno_uniq', 'unique(identification_id)',
#             'R.S.A.Identification No. must be unique per SDF!'),
#                         ('am_idno_uniq', 'unique(assessor_moderator_identification_id)',
#         'R.S.A.Identification No. must be unique per Assessor/Moderator!'),
#                         ('learner_idno_uniq', 'unique(learner_identification_id)',
#             'Learner Identification Number must be unique per Learner!'),]
    
#     @api.multi
#     def onchange_country_id(self, country_id):
#         res = {}
#         if not country_id:
#             return res
#         country_data = self.env['res.country'].browse(country_id)
#         if country_data.code == 'ZA':
#             res.update({'value':{'african':True, 'citizen_resident_status_code':'sa'}})
#         else:
#             res.update({'value':{'african':False}})
#         return res
    _defaults = {'end_date':'2018-03-31',
                 'start_date': date.today().strftime('%Y-%m-%d'),
                 }
    
    #  adding validation 
    @api.multi
    @api.onchange('work_phone','cell','person_fax_number','work_email')
    def onchange_validate_number(self):
            
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
            if self.person_fax_number:
                if not self.person_fax_number.isdigit() or len(self.person_fax_number) != 10:
                    self.person_fax_number = ''
                    return {'warning':{'title':'Invalid input','message':'Please enter 10 digits Fax number'}}
       
    @api.multi
    def onchange_crc(self, citizen_resident_status_code):
        res = {}
        if not citizen_resident_status_code:
            res.update({'value':{'citizen_status_saqa_code':''}})
            return res
        if citizen_resident_status_code == 'sa':
            country_data = self.env['res.country'].search(['|',('code','=','ZA'),('name','=','South Africa')],limit=1)
            res.update({'value':{'citizen_status_saqa_code':'sa','country_id':country_data and country_data.id},'domain':{'country_id':[('id','in',[country_data.id])]}})
        elif citizen_resident_status_code == 'dual':
            res.update({'value':{'citizen_status_saqa_code':'d'}})
        elif citizen_resident_status_code == 'other':
            res.update({'value':{'citizen_status_saqa_code':'o'}})
        elif citizen_resident_status_code == 'PR':
            res.update({'value':{'citizen_status_saqa_code':'pr'}})
        elif citizen_resident_status_code == 'unknown':
            res.update({'value':{'citizen_status_saqa_code':'u'}})
        else:
            res.update({'domain':{'country_id':[('id','in',[country_data.id for country_data in self.env['res.country'].search([])])]}})
        return res

    @api.multi
    def onchange_citizen_status_saqa_code(self,citizen_status_saqa_code):
        res = {}
        if not citizen_status_saqa_code:
            res.update({'value':{'citizen_resident_status_code':''}})
            return res
        if citizen_status_saqa_code == 'sa':
            #country_data = self.env['res.country'].search(['|',('code','=','ZA'),('name','=','South Africa')],limit=1)
            res.update({'value':{'citizen_resident_status_code':'sa'}})
        elif citizen_status_saqa_code == 'd':
            res.update({'value':{'citizen_resident_status_code':'dual'}})
        elif citizen_status_saqa_code == 'o':
            res.update({'value':{'citizen_resident_status_code':'other'}})
        elif citizen_status_saqa_code == 'pr':
            res.update({'value':{'citizen_resident_status_code':'PR'}})
        elif citizen_status_saqa_code == 'u':
            res.update({'value':{'citizen_resident_status_code':'unknown'}})
        return res
    
    @api.multi
    def onchange_person_postal_suburb(self, person_postal_suburb):
        res = {}
        if not person_postal_suburb:
            return res
        if person_postal_suburb:
            sub_res = self.env['res.suburb'].browse(person_postal_suburb)
            res.update({'value':{'person_postal_zip':sub_res.postal_code,'postal_municipality':sub_res.municipality_id,'person_postal_city':sub_res.city_id,'person_postal_province_code':sub_res.province_id}})
        return res
    
    @api.multi
    def onchange_person_home_suburb(self, person_home_suburb):
        res = {}
        if not person_home_suburb:
            return res
        if person_home_suburb:
            sub_res = self.env['res.suburb'].browse(person_home_suburb)
            res.update({'value':{'person_home_zip':sub_res.postal_code,'physical_municipality':sub_res.municipality_id,'person_home_city':sub_res.city_id,'person_home_province_code':sub_res.province_id}})
        return res
    
    
    @api.multi
    def onchange_person_suburb(self, person_suburb):
        res = {}
        
        if not person_suburb:
            return res
        if person_suburb:
            sub_res = self.env['res.suburb'].browse(person_suburb)
            res.update({'value':{'work_zip':sub_res.postal_code,'work_municipality':sub_res.municipality_id,'work_city':sub_res.city_id,'work_province':sub_res.province_id}})
        return res
    
    @api.multi
    def onchange_id_no(self, identification_id, citizen_residential_status=None):
        res, val = {}, {}
        if not identification_id:
            return res
        if citizen_residential_status in ['dual','sa']:
            for identification_ids in self.search([('identification_id','=', str(identification_id))]):
                if identification_ids:
                    if identification_ids.id != self.id:
                        raise Warning(_('Duplicate Identification Number!'))
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
    
    @api.multi
    def onchange_sameas_home(self, same_as_home):
        res = {}
        if not same_as_home:
            return res
        result = {
                  'person_postal_address_1' : self.person_home_address_1,
                  'person_postal_address_2' : self.person_home_address_2,
                  'person_postal_address_3' : self.person_home_address_3,
                  'person_postal_suburb' : self.person_home_suburb,
                  'person_postal_city' : self.person_home_city,
                  'person_postal_province_code' : self.person_home_province_code and self.person_home_province_code.id,
                  'person_postal_zip' : self.person_home_zip,
                  'country_postal' : self.country_home and self.country_home.id
                  }
        res.update({'value':result})
        return res
    
    
    @api.multi
    def open_map(self, street, city, state, country, zip):
        url="http://maps.google.com/maps?oi=map&q="
        if street:
            url+=street.replace(' ','+')
        if city:
            url+='+'+city.name.replace(' ','+')
        if state:
            url+='+'+state.name.replace(' ','+')
        if country:
            url+='+'+country.name.replace(' ','+')
        if zip:
            url+='+'+zip.replace(' ','+')
        return {
        'type': 'ir.actions.act_url',
        'url':url,
        'target': 'new'
        }
        
    
    @api.multi
    def work_addr_map(self):
        return self.open_map(self.work_address, self.work_city, self.work_province, self.work_country, self.work_zip)
    
    @api.multi
    def home_addr_map(self):
        return self.open_map(self.person_home_address_1, self.person_home_city, self.person_home_province_code, self.country_home, self.person_home_zip)
    
    @api.multi
    def postal_addr_map(self):
        return self.open_map(self.person_postal_address_1, self.person_postal_city, self.person_postal_province_code, self.country_postal, self.person_postal_zip)

hr_employee()  

class mail_message(models.Model):
    _inherit = 'mail.message'
    
    @api.model
    def create(self,vals):
        if vals.get('model',False) == 'hr.employee':
            employee_data = self.env['hr.employee'].browse(int(vals['res_id']))
            if employee_data.is_sdf and 'created' in vals.get('body') :
                vals.update({'body':'<p>SDF Created</p>'})
            if employee_data.is_learner and 'created' in vals.get('body') : 
                vals.update({'body':'<p>Learner Created</p>'})
            if employee_data.is_assessors and 'created' in vals.get('body') :
                vals.update({'body':'<p>Assessor Created</p>'})
            if employee_data.is_moderators and 'created' in vals.get('body') :
                vals.update({'body':'<p>Moderator Created</p>'})
        if vals.get('model',False) == 'res.partner':
            partner_data = self.env['res.partner'].browse(int(vals['res_id']))
            if  partner_data.employer and 'created' in vals.get('body') :
                vals.update({'body':'<p>Employer Created</p>'})           
            if  partner_data.provider and 'created' in vals.get('body'):             
                vals.update({'body':'<p>Provider Created</p>'})                      
        res = super(mail_message, self).create(vals)
        return res
    
mail_message()

class hr_department(models.Model):
    _inherit = 'hr.department'
    
    is_branch = fields.Boolean(string='Branch')
    code = fields.Char(string='Code')
    branch_address1 = fields.Char(string='Address 1')
    branch_address2 = fields.Char(string='Address 2')
    branch_address3 = fields.Char(string='Address 3')
    branch_city = fields.Char(string='City')
    branch_province = fields.Many2one('res.country.state', string='Province')
    branch_zip = fields.Char(string='Zip')
    branch_country= fields.Many2one('res.country', string='Country') 
    parent_branch = fields.Many2one('hr.department', string='Parent Branch')
    dept_branch = fields.Many2one('hr.department', string='Branch')
    
    @api.multi
    def onchange_branch_province(self, province):
        if province:
            state = self.env['res.country.state'].browse(province)
            country_id = state.country_id.id
            return {'value': {'branch_country': country_id }}
        else :
            return {}
        
hr_department()


## For Locality in South Africa
class res_district(models.Model):
    _name = 'res.district'
    
    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    province_id = fields.Many2one('res.country.state', string='Province')
    country_id = fields.Many2one('res.country', string='Country')
    urban_rural = fields.Selection([('urban','Urban'),('rural','Rural'),('unknown','Unknown')], string='Urban/Rural')
    
res_district()

class res_city(models.Model):
    _name = 'res.city'
    
    name = fields.Char(string='Name')
    district_id = fields.Many2one('res.district', string='District')
    province_id = fields.Many2one('res.country.state', string='Province')
    country_id = fields.Many2one('res.country', string='Country')
    urban_rural = fields.Selection([('urban','Urban'),('rural','Rural'),('unknown','Unknown')], string='Urban/Rural')
    latitude = fields.Char("Latitude")
    longitude = fields.Char("Longitude")
res_city()

class res_municipality(models.Model):
    _name = 'res.municipality'
    
    name = fields.Char(string='Name')
    city_id = fields.Many2one('res.city', string='City')
    district_id = fields.Many2one('res.district', string='District')
#     code = fields.Char(string='Code')
    province_id = fields.Many2one('res.country.state', string='Province')
    country_id = fields.Many2one('res.country', string='Country')
    urban_rural = fields.Selection([('urban','Urban'),('rural','Rural'),('unknown','Unknown')], string='Urban/Rural')

res_municipality()

class res_suburb(models.Model):
    _name = 'res.suburb'
    
    name = fields.Char(string='Name')
    postal_code = fields.Char(string='Postal Code')
    municipality_id = fields.Many2one('res.municipality', string='Municipality')
    city_id = fields.Many2one('res.city',string='City')
    district_id = fields.Many2one('res.district', string='District')
    province_id = fields.Many2one('res.country.state', string='Province')
    country_id = fields.Many2one('res.country', string='Country') 
    urban_rural = fields.Selection([('urban','Urban'),('rural','Rural'),('unknown','Unknown')], string='Urban/Rural')
    statssa_area_code = fields.Char(string='StatsSA Area Code')
res_suburb()

class project_document(models.Model):
    _name = 'project.document'
    
    name = fields.Char(string='Name')

project_document()
