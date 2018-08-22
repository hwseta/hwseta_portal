from openerp import models, fields, api, _
from openerp.exceptions import Warning, ValidationError, MissingError
from datetime import datetime, timedelta
import csv
from StringIO import StringIO
import itertools
import calendar
import os
import math
import subprocess
from openerp.addons.base.workflow.workflow import workflow
import xlrd
import base64
import openpyxl
from openpyxl import Workbook
import cStringIO
import xlwt
import openerp.addons.decimal_precision as dp
from datetime import date
from dateutil.relativedelta import relativedelta
import xlsxwriter
from lxml import etree

class sdf_register(models.Model):
    _name = 'sdf.register'
    _inherit = 'mail.thread'
    _description = 'SDF Registration'
    
sdf_register()

class product_template(models.Model):
    _inherit = 'product.template'

    mark_asset = fields.Boolean(string='Mark as Asset')
    
product_template()

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    mark_asset = fields.Boolean(string='Declare as Asset')
    journal_id = fields.Many2one('account.journal', string='Related Journal')
    asset_acc_id = fields.Many2one('account.account', string='Asset Account')
    
    
stock_picking()

class account_move(models.Model):
    _inherit = 'account.move'
    
    is_expense_voucher_created = fields.Boolean(string = "Expense Voucher", default=False)
    batch_no = fields.Char(string='Batch No')
    is_lump_sum = fields.Boolean(string='Is a DHET Entry ?')
    scheme_year_id = fields.Many2one('scheme.year','Scheme Year')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
#     is_cfo = fields.Boolean(string='Allow CFO')
    
    @api.multi
    def name_get(self):
        res = super(account_move, self).name_get()
        new_res = [(res_val[0],self.browse(res_val[0]).name) for res_val in res]
        return new_res
    
    @api.multi
    def onchange_lump_sum(self, is_lump_sum) :
        res = {}
        if not is_lump_sum :
            return res
        if is_lump_sum is True :
            dhet_journal_data = self.env['account.journal'].search([('name','=','DHET Journal')])
            res.update({'value':{'journal_id' : dhet_journal_data.id}})
        return res
    
    @api.multi
    def onchange_journal_id(self, journal_id) :
        res = {}
        if not journal_id :
            return res
        analytic_acc_journal_data = self.env['account.journal'].browse(journal_id).account_analytic_id
        if not analytic_acc_journal_data :
            return res
        else :
            res.update({'value':{'account_analytic_id' : analytic_acc_journal_data.id}})
        return res
    
    @api.multi
    def button_validate(self):
        result = super(account_move, self).button_validate()
        users_of_cfo = [ user_data.id for user_data in self.env['res.groups'].search([('name','=','CFO')]).users ]
#         users_of_acc_mngr = [ user_data.id for user_data in self.env['res.groups'].search([('name','=','Financial Manager')]).users ]
        # Getting Financial Manager amount approval limit.
        admin_config = self.env['leavy.income.config'].search([])
        if isinstance(admin_config, list):
            admin_config = admin_config[0]
        fm_max_limit = admin_config.fm_approval_limit
        if fm_max_limit == 0 :
            raise Warning(_('Please configure Financial Manager amount approval limit inside Admin Configuration!'))
        ##
        credit = 0 ; debit = 0
        for line in self:
            for line_data in line.line_id :
                credit += line_data.credit
                debit += line_data.debit
        if credit == debit and credit > fm_max_limit :
            if self._uid in users_of_cfo :
                pass
            else :
                raise Warning(_('Only CFO can post this entry. Since amount exceeding R %s !')%(fm_max_limit))
#         elif credit == debit and credit <= 100000 :
#             if self._uid in users_of_acc_mngr :
#                 pass
#             else :
#                 raise Warning(_('Only Financial Manager can post this entry. Since amount is less than R100000!!'))
        
        ###################Expence Organisation Invoice Creation########################
        
        for rec in self:
            for line in rec.line_id:
                invoice_line_vals = []
                wsp_submission_data = []
                if line.name.startswith("Mandatory Grant") and line.move_line_type == 'income':
                    product_id = self.env['product.product'].search([('name', '=', 'Mandatory Grant')])
                    ##########Checking WSP submitted for not and whether scheme year is closed or not#########
                    self._cr.execute("select id from wsp_submission_track where employer_id = %s AND status = 'accepted' AND scheme_year_id = %s",([line.partner_id.id, line.scheme_year_id.id]))
                    res_wsp = self._cr.fetchall()
                    wsp_submission_data = self.env['wsp.submission.track'].browse([i[0] for i in res_wsp])
                    if line.scheme_year_id.state == 'closed' and wsp_submission_data:
                        vals = {'product_id':product_id.id,
                                'name': 'Mandatory Grant',
                                'quantity': 1,
                                'price_unit': line.credit or line.debit,
                                'account_id': product_id.property_account_income and product_id.property_account_income.id or \
                                               product_id.categ_id and product_id.categ_id.property_account_income_categ and product_id.categ_id.property_account_income_categ.id
                                }
                        invoice_line_vals.append((0,0,vals))
                    if wsp_submission_data and invoice_line_vals :
                        expense_voucher_id = self.env['account.invoice'].create({'partner_id': line.partner_id.id,\
                                        'levy_period_id': line.period_id.id,
                                        'period_id': line.period_id.id,
                                        'journal_id': line.journal_id.id,
                                        'scheme_year_id': line.scheme_year_id.id,
                                        'batch_no': rec.batch_no,
                                        'journal_entry_ref': rec.name,
                                        'type': 'in_invoice',
                                        'employer': True,
                                        'date_invoice': datetime.now().date(),
                                        'account_id': line.partner_id.property_account_payable.id,
                                        'invoice_line': invoice_line_vals,
                                        })
                        print "--------Expense Voucher ID-----------", expense_voucher_id
                        self.write({'is_expense_voucher_created': True})
                        
#                     else:
#                         raise Warning('Scheme Year not closed OR WSP not accepted selected employer!!!')

        return result
account_move()


class account_move_line(models.Model):
    _inherit = 'account.move.line'
    
    
    @api.model
    def default_get(self, fields_list):
        res = super(account_move_line, self).default_get(fields_list)
        context = self._context
        analytic_account = context.get('analytic_account')
        if analytic_account :
            res.update({'analytic_account_id' : analytic_account})
        return res
    
    scheme_year_id = fields.Many2one('scheme.year','Scheme Year')
    project_id = fields.Many2one('project.project', string="Project")
    move_line_type = fields.Selection([('income','Income'),('expense','Expense')], string='Type') 
    
account_move_line()

class wsp_submission_track(models.Model):
    _name = 'wsp.submission.track'
    
    name = fields.Char(string='Name')
    fiscal_year = fields.Many2one('account.fiscalyear', string='Year')
#   status = fields.Selection([('draft','Draft'),('submitted','Submitted'),('evaluated2','Evaluated'),('evaluated','Evaluated'),('rejected','Rejected'),('accepted','Accepted'),('query','Query')], string='Status')
    status = fields.Selection([('draft','Draft'),('submitted','Submitted'),('evaluated','Evaluated'),('rejected','Rejected'),('accepted','Accepted'),('query','Query')], string='Status')


    employer_id = fields.Many2one('res.partner', string='Related Employer')
    
#     added new field as per requirement
#     scheme_year=fields.Char("Scheme Year")
    scheme_year_id = fields.Many2one('scheme.year', 'Scheme Year')
    date_created=fields.Date("Date Created")
    wsp_date_submitted=fields.Date("WSP Date Submitted")
    last_user_evaluated_updated=fields.Char("Submitted by")
#     wsp_last_change_date=fields.Date("WSP Last Date Changed")
    approved_date=fields.Date("Approved Date")
    approved_by=fields.Char("Approved By")
    rejected_date=fields.Date("Rejected Date")
    rejected_by=fields.Char("Rejected By")    

    
wsp_submission_track()

class stock_transfer_details(models.Model):
    _inherit = 'stock.transfer_details'
    
#     @api.multi
#     def get_line(self, name, product, debit, credit, account_id):
#         result = {
#                   'analytic_account_id' : False,
#                   'tax_code_id' : False,
#                   'analytic_lines' : [],
#                   'tax_amount' : False,
#                   'name' : name,
#                   'ref' : self.name,
#                   'asset_id' : False,
#                   'currency_id' : False,
# #                   'credit' : amount,
#                   'product_id' : product,
#                   'date_maturity' : False,
# #                   'debit':amount,
#                   'date':datetime.now().date(),
#                   'amount_currency' : 0,
#                   'product_uom_id' : False,
#                   'quantity' : 0,
#                   'partner_id':self.employer_id.id,
#                   'account_id':account_id,
#                   }
#         return result
    
    ## Inherited to create Assets
    @api.one
    def do_detailed_transfer(self):
        res = super(stock_transfer_details, self).do_detailed_transfer()
        picking_data = self.picking_id
#         location_dest_id=picking_data.location_dest_id
        if picking_data.mark_asset:
#             move_obj = self.env['account.move']
#             move_line_obj = self.env['account.move.line']
            purchase_order_name = picking_data.group_id and picking_data.group_id.name
            if not purchase_order_name:
                raise Warning(_('No Purchase Order linked to this group!'))
            purchase_data = self.env['purchase.order'].search([('name','=',purchase_order_name)])
            asset_category_obj = self.env['account.asset.category']
            ## Creating Asset Category and Asset.
            ## Checking whether Asset Category already exists or not.
            asset_category_data = asset_category_obj.search([('name','=','HWSETA Assets')])
            if not asset_category_data :
                asset_category_data = asset_category_obj.create({
                                                           'name':'HWSETA Assets',
                                                           'journal_id':picking_data.journal_id.id,
                                                           'account_asset_id':picking_data.asset_acc_id.id,
                                                           'account_depreciation_id':picking_data.asset_acc_id.id,
                                                           'account_expense_depreciation_id':picking_data.asset_acc_id.id,
                                                           })
            for move_line in picking_data.move_lines :
                product_data = move_line.product_id
                amount = 0
                if not product_data.mark_asset:
                    raise Warning(_('Please add product of Asset type only!'))
                for purchase_line_data in purchase_data.order_line:
                    if purchase_line_data.product_id.id == product_data.id:
                        amount = purchase_line_data.price_unit
                ## Creating Asset
                asset_data = self.env['account.asset.asset'].create({
                                                                'name':product_data.name,
                                                                'category_id':asset_category_data.id,
                                                                'purchase_value':amount,
                                                                'product_id':purchase_line_data.product_id.id,
                                                                'asset_location':picking_data.location_dest_id[0].id
                                                                })
                
#                 result = []
#                 line_val = self.get_line(picking_data.name, move_line.product_id.id, amount)
#             move_val = {
#                         'ref':picking_data.name,
#                         'line_id':line_val,
#                         'journal_id':picking_data.journal_id.id,
#                         'date':datetime.now().date(),
#                         'narration':self.name,
#                         'company_id':picking_data.employer_id.company_id.id,
#                         }
#             move_obj.create(move_val)
        
                    
        return res
    
stock_transfer_details()

class ir_attachment(models.Model):
    _inherit = 'ir.attachment'
    
    @api.model
    def default_get(self, fields_list):
        res = super(ir_attachment, self).default_get(fields_list)
        context = self._context.copy()
        if context and context.get('emp_doc',False):
            res.update({'name':'Document'})
        if context and context.get('doc_name',False):
            res.update({'name':context['doc_name']})
        return res
    
    @api.model
    def create(self, vals):
        context = self._context.copy()
        if context and context.get('emp_doc',False) and vals.get('datas_fname',False):
            vals.update({'name' : vals.get('datas_fname',False)})
        return super(ir_attachment,self).create(vals)
    
ir_attachment()

class employer_document_upload(models.Model):
    _name = 'employer.document.upload'
    
    name = fields.Char(string='Name')
    document = fields.Many2one('ir.attachment', string='Document')
    employer_id = fields.Many2one('res.partner', string='Name', domain=[('employer','=',True)])
    
employer_document_upload()

class res_partner_childs(models.Model):
    _name = 'res.partner.childs'
     
    name = fields.Char(string='Name')
    employer_id = fields.Many2one('res.partner', string='Employer')
    emp_child_id = fields.Many2one('res.partner', string='Related Employer')
    sdl_number = fields.Char(string='SDL Number')
    seta_id = fields.Many2one('seta.branches', string='SETA Id')
    sic_code = fields.Many2one('hwseta.sic.master')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone', size=10)
    mobile = fields.Char(string='Mobile', size=10)
     
    @api.multi
    def onchange_employer_id(self, employer_id):
        res = {}
        if not employer_id :
            return res
        employer_data = self.env['res.partner'].browse(employer_id)
        res.update({
                    'value':{
                                'sdl_number' : employer_data.employer_sdl_no,
                                'seta_id' : employer_data.employer_seta_id and employer_data.employer_seta_id.id,
                                'sic_code' : employer_data.empl_sic_code and employer_data.empl_sic_code.id,
                                'email' : employer_data.email,
                                'phone' : employer_data.phone,
                                'mobile' : employer_data.mobile
                             }
                    }) 
        return res
     
res_partner_childs()

class employer_sdl_no(models.Model):
    _name = 'employer.sdl.no'
    
    name = fields.Char(string='Name')
    employer_id = fields.Many2one('res.partner', string='Employer')

employer_sdl_no()

## Employer Related fields can be accessed here from hwseta_person module.
class res_partner(models.Model):
    _inherit = 'res.partner'
    
    sdf_id = fields.Many2one('sdf.register', string='SDF')
    wsp_submitted = fields.Boolean(string='WSP Submitted')
    leavy_exempted = fields.Boolean(string='Levy Exempted')
    leavy_history_ids = fields.One2many('leavy.history','employer_id', string='Levy History')
    empl_sic_code = fields.Many2one('hwseta.sic.master', string='SIC Code')
    empl_sic_code_id = fields.Char(string='SIC Code ID')
    npo_ngo = fields.Boolean(string='NPO/NGO')
    other = fields.Boolean(string='Other')
    empl_status = fields.Char(string="Employer Status")
    participated_project_ids = fields.One2many('project.participated', 'participated_employer_id', string='Participated in Projects')
    doc_upload_ids = fields.One2many('employer.document.upload','employer_id', string='Document Uploads')
    parent_employer_id = fields.Many2one('res.partner', string='Parent Employer', domain=[('employer','=',True)])
    child_employer_ids = fields.One2many('res.partner.childs','emp_child_id', string='Child Organisations')
    child_emp_ids = fields.One2many('res.partner','parent_employer_id', string='Child Organisations')
    ## Fields for keeping WSP history.
    wsp_submission_ids = fields.One2many('wsp.submission.track','employer_id', string='WSP Submissions')
    ### Employer Master extra fields.
    ext_emp_reg_number_type = fields.Selection([('cipro_number','Cipro Number'),('comp_reg_no','Company Registration Number')], string='Extra Registration Number Type')
    ext_partnership = fields.Selection([('private','Private'),('public','Public'),('private_public','Private Public')], string='Extra Partnership')
    ext_total_annual_payroll = fields.Float(string='Extra Total Anual Payroll')
    sars_number = fields.Char(string='SARS Number')
    cipro_number = fields.Char(string='Cipro Number')
    extra_cipro_number = fields.Char(string='Extra Cipro Number')
    ext_organisation_size = fields.Selection([('small','Small (0-49)'),('medium','Medium (50-149)'),('large','Large (150+)')], string='Ext Organisation Size')
    ext_employer_registration_number = fields.Char(string='Extra Registration Number',track_visibility='onchange', size=20)
    ext_phone_number = fields.Char(string='Extra Phone Number')
    ext_fax_number = fields.Char(string='Extra Fax Number')
    ext_empl_sic_code_id = fields.Char(string='Extra SIC Code ID')
    ext_employees_count = fields.Integer(string='Extra Employees as per Employment Profile')
    
    ext_physical_address_1 = fields.Char(string='Extra Physical Address1', help="Extra Physical Address 1",track_visibility='onchange',size=50)
    ext_physical_address_2 = fields.Char(string='Extra Physical Address2', help="Extra Physical Address 2",track_visibility='onchange',size=50)
    ext_physical_address_3 = fields.Char(string='Extra Physical Address3', help="Extra Physical Address 3",track_visibility='onchange',size=50)
    ext_physical_code = fields.Char(string='Extra Physical Zip',track_visibility='onchange')
    ext_province_code_physical = fields.Many2one('res.country.state', string='Extra Physical Province Code',track_visibility='onchange')
    physical_municipality = fields.Many2one('res.municipality', string='Physical Municipality')
    ext_physical_municipality = fields.Many2one('res.municipality', string='Extra Physical Municipality')
    
    ext_postal_address_1 = fields.Char(string='Extra Postal Address1', help="Extra Postal Address 1",track_visibility='onchange',size=50)
    ext_postal_address_2 = fields.Char(string='Extra Postal Address2', help="Extra Postal Address 2",track_visibility='onchange',size=50)
    ext_postal_address_3 = fields.Char(string='Extra Postal Address3', help="Extra Postal Address 3",track_visibility='onchange',size=50)
    ext_postal_code = fields.Char(string='Extra Postal Zip',track_visibility='onchange')
    ext_province_code_postal = fields.Many2one('res.country.state', string='Extra Postal Province Code',track_visibility='onchange')
    postal_municipality = fields.Many2one('res.municipality', string='Postal Municipality')
    ext_postal_municipality = fields.Many2one('res.municipality', string='Extra Postal Municipality')
    
    #Added extra added field according to DHET 
    ext_nature_of_person=fields.Char("Nature Of Person")
    ext_area_code=fields.Char("Area code")
    ext_partner_initial=fields.Char("Partner Initial")
    ext_partner_surname=fields.Char("Partner Surname")
    ext_date_of_birth=fields.Date("Date Of Birth")
    ext_identity_number=fields.Char("Identity Number")
    ext_date_business_commenced=fields.Date("Date Business Commenced")
    ext_date_person_became_liable=fields.Date("Date Person Became Liable")
    ext_capacity_rep_employer=fields.Char("Capacity Rep Employer")
    ext_home_address_rep_emp3=fields.Char("Home Address Rep. Emp 3")
    ext_home_address_rep_emp4=fields.Char("Home Address Rep. Emp 4")
    ext_dial_code_rep_emp=fields.Char("Dial Code Rep. Emp")
    ext_telephone_number_rep_emp=fields.Char("Telephone Number Rep. Emp")
    ext_fax_dial_code_rep_emp=fields.Char("Fax Dial Rep. Emp")
    ext_fax_number_rep_emp=fields.Char("Fax Number Rep. Emp")
    ext_bus_cell_number=fields.Char("Bus Cell Number")
    ext_magisterial_district=fields.Char("Magisterial District")
    ext_chamber_code=fields.Char("Chamber Code")
    ext_exemption_code=fields.Char("Exemption Code")
    ext_bat_type=fields.Char("Bat Type")
    ext_number_of_branches=fields.Char("Number Of Branches")
    ext_no_seperate_reg_business=fields.Char("No Seperate Reg Business")
    ext_other_name_of_business1=fields.Char("Other Name Of Business 1")
    ext_other_name_of_business2=fields.Char("Other Name Of Business 2")
    ext_other_name_of_business3=fields.Char("Other Name Of Business 3")
    ext_status=fields.Char("Extra Status")
    ext_branch_type_indicator=fields.Char("Branch Type Indicator")
    ext_main_reference_number=fields.Char("Main Reference Number")
    ext_registration_indicator=fields.Char("Registration Indicator")
    
    _sql_constraints = [('sdl_uniq', 'unique(employer_sdl_no)',
            'SDL Number must be unique per Employer!'),]
    
    @api.multi
    def onchange_sic_code(self, empl_sic_code):
        res = {}
        if not empl_sic_code :
            return res
        sic_code_data = self.env['hwseta.sic.master'].browse(empl_sic_code)
        res.update({'value':{ 'empl_sic_code_id' : sic_code_data.name }})
        return res
    
    @api.multi
    def onchange_province_physical(self, province):
        if province:
            country_id = self.country_for_province(province)
            return {'value': {'emp_country_code_physical': country_id }}
        return {}
    
    @api.multi
    def onchange_city_physical(self,city):
        if city:
            return {'value':{'emp_province_code_physical': self.env['res.city'].browse(city).province_id.id }}
        return {}    
    
    @api.multi
    def onchange_suburb_physical(self,suburb):
        if suburb:
            return {'value':{'emp_city_physical': self.env['res.suburb'].browse(suburb).city_id.id }}
        return {}     
    
    @api.multi
    def onchange_city_postal(self,city):
        if city:
            return {'value':{'emp_province_code_postal': self.env['res.city'].browse(city).province_id.id }}
        return {}    
    
    @api.multi
    def onchange_suburb_postal(self,suburb):
        if suburb:
            return {'value':{'emp_city_postal': self.env['res.suburb'].browse(suburb).city_id.id }}
        return {}      
    
    @api.multi
    def onchange_city(self,city):
        if city:
            return {'value':{'state_id': self.env['res.city'].browse(city).province_id.id }}
        return {}    
    
    @api.multi
    def onchange_suburb(self,suburb):
        res = {}
        if not suburb:
            return res
        if suburb:
            sub_res = self.env['res.suburb'].browse(suburb)
        if suburb:
            return {'value':{'city': self.env['res.suburb'].browse(suburb).city_id.id ,'zip':sub_res.postal_code}}
        return {}    
       
    @api.multi
    def onchange_province_postal(self, province):
        if province:
            country_id = self.country_for_province(province)
            return {'value': {'emp_country_code_postal': country_id }}
        return {}
    
#     @api.multi
#     def onchange_sdl_no(self, employer_sdl_no) :
#         result = {}
#         employer_sdl_obj = self.env['employer.sdl.no']
#         empl_sdl_datas = employer_sdl_obj.search([('employer_id','=',self.id)])
#         for empl_sdl in empl_sdl_datas :
#             self._cr.execute("delete from employer_sdl_no where id = %s"%(empl_sdl.id))
#         sdl_id = employer_sdl_obj.create({ 'name' : employer_sdl_no , 'employer_id' : self.id })
#         return True
    
    @api.model
    def create(self, vals):
        ## Checking for Employer Domain
        if vals.get('npo_ngo'):
            vals.update({'empl_status':'NPO / NGO'})
        if vals.get('university'):
            vals.update({'empl_status':'University'})
        if vals.get('college'):
            vals.update({'empl_status':'TVET College'})
        if vals.get('employer_department'):
            vals.update({'empl_status':'Government'})
        if vals.get('other'):
            vals.update({'empl_status':'Other'})
        ###
        employer_data = super(res_partner, self).create(vals)
        ## Creating Employer SDL Number entry into Employer SDL Number table.
        self.env['employer.sdl.no'].create({'name' : employer_data.employer_sdl_no ,'employer_id' : employer_data.id})
        user_obj = self.env['res.users']
        group_obj = self.env['res.groups']
        group_list = []
        if employer_data.employer == True :
            ## Applying Portal and Employer Groups to the Employer's User. 
            group_data = group_obj.search(['|',('name','=','Portal'),('name','=','Employer')])
            for data in group_data:
                tup = (4,data.id)
                group_list.append(tup)
            ## Removing the Employer's User from Contact Creation and Employee Groups.
            rem_group_data = group_obj.search(['|',('name', '=', 'Contact Creation'),('name','=','Employee')])
            for data in rem_group_data:
                tup = (3,data.id)
                group_list.append(tup)
#         if (employer_data.parent_id and not (employer_data.parent_id.customer or employer_data.parent_id.supplier)) or not (employer_data.customer or employer_data.supplier):
            user_obj.create({
                             'name':employer_data.name, 
                             'login':str(employer_data.employer_sdl_no), 
                             'partner_id':employer_data.id,
                             'password':'admin',
                             'groups_id':group_list,
                             'internal_external_users':'Employer',
                             })
        return employer_data
    
    ## Method for checking whether the string is in Uppercase or not.
    @api.multi
    def check_for_uppercase(self, field_string, msg):
        char_length = len(field_string)
        while char_length > 0:
            if field_string[char_length-1].islower() == True:
                raise Warning(_(msg))
            char_length-=1
        return True
    
    @api.multi
    def ignore_char(self, field_string):
        if field_string in ['%UNKNOWN%','%AS ABOVE%','%SOOSBO%','%DELETE%','%N/A%', 'NA','U','NONE','GEEN','0','TEST','%ONTBREEK%','NILL']:
            raise Warning(_('This Character is not allowed in this Field!'))
        return True
    
    @api.multi
    def validate_employer(self, vals):
        ## Validation for Employer Trading Name.
#         if vals.get('employer_trading_name') == False or not self.employer_trading_name :
#             raise Warning(_('Employer Trading Name should not be blank!'))
#         elif vals.get('employer_trading_name') and vals['employer_trading_name'][0] == ' ':
#             raise Warning(_('Employer Trading Name should not start with blank space!'))
#         elif vals.get('employer_trading_name') and self.check_for_uppercase(vals['employer_trading_name'],'Employer Trading Name should be in Uppercase!'):
#             pass
#         elif vals.get('employer_trading_name') and self.ignore_char(vals['employer_trading_name']) :
#             pass
         
        ## Validation for Employer
        if vals.get('employer_sdl_no') :
            if vals['employer_sdl_no'][0] == ' ':
                raise Warning(_('SDL No. should not start with blank space.!'))
            if vals['employer_sdl_no'][0] not in ['L','N']:
                raise Warning(_('SDL No. should start with L (For Leavy Paying) or N (For Non-Leavy Paying).!'))
            if vals.get('employer_sdl_no') and vals['employer_sdl_no'][1:]:
                exclude_first_char = vals['employer_sdl_no'][1:]
                char_len = len(exclude_first_char) 
                while char_len > 0:
                    if exclude_first_char[char_len-1].isalpha():
                        raise Warning(_('SDL No. should be combination of L or N followed by 0-9 digits only!')) 
                    char_len-=1
            if len(vals['employer_sdl_no']) < 10:
                raise Warning(_('SDL Number should be of 10 digits'))
            
        ## Validation for Employer Site No.
        if vals.get('employer_site_no') :
            if vals['employer_site_no'][0] == ' ':
                raise Warning(_('Site No. should not start with blank space.!'))
            self.check_for_uppercase(vals['employer_site_no'],'Site No. should be in Uppercase!')
            for site_no_char in  vals['employer_site_no'] :
                if site_no_char not in 'ABCDEFGHIJKLMNOPQRTSUVWXYZ1234567890@#&+() /\:._-':
                    raise Warning(_('Site No. should contain characters within ABCDEFGHIJKLMNOPQRTSUVWXYZ1234567890@#&+() /\:._-'))
         
        ## Validation for Employer Registration No.
        if vals.get('employer_registration_number') and vals['employer_registration_number'][0] == ' ':
            raise Warning(_('Registration Number should not start with blank space.!'))
        elif vals.get('employer_registration_number') and self.check_for_uppercase(vals['employer_registration_number'],'Registration Number should be in Uppercase!'):
            pass
         
        ## Validation for Employer Phone No.
        if vals.get('phone') and vals['phone'][0] == ' ':
            raise Warning(_('Employer Phone No should not start with blank space!'))
        elif vals.get('phone') :
            phone_char = vals['phone']
            char_len = len(phone_char)  
            while char_len > 0:
                if phone_char[char_len-1].isalpha():
                    raise Warning(_('Employer Phone No should contain only Numbers!')) 
                char_len-=1
        elif vals.get('phone') and self.ignore_char(vals['phone']) :
            pass
         
        ## Validation for Employer Fax No.
        if vals.get('fax') and vals['fax'][0] == ' ':
            raise Warning(_('Employer Fax No should not start with blank space!'))
        elif vals.get('fax') and vals['fax'].isalpha():
            raise Warning(_('Employer Fax No should contain only Digits!'))
        elif vals.get('fax') and self.ignore_char(vals['fax']) :
            pass
         
        ## Validation for Employer SETA ID.
#             if vals.get('employer_seta_id') == False or not self.employer_seta_id:
#                 raise Warning(_('SETA ID. should not be blank!'))
#             elif vals.get('employer_seta_id') and vals['employer_seta_id'][0] == ' ':
#                 raise Warning(_('SETA ID. should not start with blank space.!'))
#             elif vals.get('employer_seta_id') and vals.get('employer_seta_id').isalpha():
#                 raise Warning(_('SETA ID. should contains only Numbers.!'))
         
        ## Validation for Employer SIC Code.
        if vals.get('employer_sic_code') and vals['employer_sic_code'][0] == ' ':
            raise Warning(_('SIC Code should not start with blank space.!'))
        elif vals.get('employer_sic_code') and self.check_for_uppercase(vals['employer_sic_code'],'SIC Code should be in Uppercase!'):
            pass
         
        ## Validation for Employer Physical Address1.
        if vals.get('employer_physical_address1') == False or not self.employer_physical_address1 :
            raise Warning(_('Employer Physical Address1 should not be blank!'))
        elif vals.get('employer_physical_address1') and vals['employer_physical_address1'][0] == ' ':
            raise Warning(_('Employer Physical Address1 should not start with blank space!'))
        elif vals.get('employer_physical_address1') and self.check_for_uppercase(vals['employer_physical_address1'], 'Employer Physical Address1 should be in Uppercase!'):
            pass
         
        ## Validation for Employer Physical Address2.
        if vals.get('employer_physical_address2') == False or not self.employer_physical_address2 :
            raise Warning(_('Employer Physical Address2 should not be blank!'))
        elif vals.get('employer_physical_address2') and vals['employer_physical_address2'][0] == ' ':
            raise Warning(_('Employer Physical Address2 should not start with blank space!'))
        elif vals.get('employer_physical_address2') and self.check_for_uppercase(vals['employer_physical_address2'], 'Employer Physical Address2 should be in Uppercase!'):
            pass
         
        ## Validation for Employer Physical Address3.
        if vals.get('employer_physical_address3') == False or not self.employer_physical_address3 :
            raise Warning(_('Employer Physical Address3 should not be blank!'))
        elif vals.get('employer_physical_address3') and vals['employer_physical_address3'][0] == ' ':
            raise Warning(_('Employer Physical Address3 should not start with blank space!'))
        elif vals.get('employer_physical_address3') and self.check_for_uppercase(vals['employer_physical_address3'], 'Employer Physical Address3 should be in Uppercase!'):
            pass
         
        ## Validation for Employer Physical Address Code.
        if vals.get('employer_physical_address_code') == False or not self.employer_physical_address_code :
            raise Warning(_('Employer Physical Address Code should not be blank!'))
        elif vals.get('employer_physical_address_code') and vals['employer_physical_address_code'][0] == ' ':
            raise Warning(_('Employer Physical Address Code should not start with blank space!'))
        elif vals.get('employer_physical_address_code') and vals['employer_physical_address_code'].isalpha():
            raise Warning(_('Employer Physical Address Code should contain only Digits!'))
         
        ## Validation for Employer Postal Address 1.
        if vals.get('employer_postal_address1') == False or not self.employer_postal_address1 :
            raise Warning(_('Employer Postal Address1 should not be blank!'))
        elif vals.get('employer_postal_address1') and vals['employer_postal_address1'][0] == ' ':
            raise Warning(_('Employer Postal Address1 should not start with blank space!'))
        elif vals.get('employer_postal_address1') and self.check_for_uppercase(vals['employer_postal_address1'], 'Employer Postal Address1 should be in Uppercase!'):
            pass
         
        ## Validation for Employer Postal Address 2.
        if vals.get('employer_postal_address2') == False or not self.employer_postal_address2 :
            raise Warning(_('Employer Postal Address2 should not be blank!'))
        elif vals.get('employer_postal_address2') and vals['employer_postal_address2'][0] == ' ':
            raise Warning(_('Employer Postal Address2 should not start with blank space!'))
        elif vals.get('employer_postal_address2') and self.check_for_uppercase(vals['employer_postal_address2'], 'Employer Postal Address2 should be in Uppercase!'):
            pass
         
        ## Validation for Employer Postal Address 3.
        if vals.get('employer_postal_address3') == False or not self.employer_postal_address2 :
            raise Warning(_('Employer Postal Address3 should not be blank!'))
        elif vals.get('employer_postal_address3') and vals['employer_postal_address3'][0] == ' ':
            raise Warning(_('Employer Postal Address3 should not start with blank space!'))
        elif vals.get('employer_postal_address3') and self.check_for_uppercase(vals['employer_postal_address3'], 'Employer Postal Address3 should be in Uppercase!'):
            pass
        ## Validation for Employer Postal Address Code.
        if vals.get('employer_postal_address_code') == False or not self.employer_postal_address_code :
            raise Warning(_('Employer Postal Address Code should not be blank!'))
        elif vals.get('employer_postal_address_code') and vals['employer_postal_address_code'][0] == ' ':
            raise Warning(_('Employer Postal Address Code should not start with blank space!'))
        elif vals.get('employer_postal_address_code') and vals['employer_postal_address_code'].isalpha():
            raise Warning(_('Employer Postal Address Code should contain only Digits!'))
         
        ## Validation for Lattitude Degree.
        if vals.get('employer_latitude_degree') == False or not self.employer_latitude_degree :
            raise Warning(_('Employer Lattitude Degree should not be blank!'))
        elif vals.get('employer_latitude_degree') and vals['employer_latitude_degree'][0] == ' ':
            raise Warning(_('Employer Lattitude Degree should not start with blank space!'))
        elif vals.get('employer_latitude_degree') and vals['employer_latitude_degree'].isalpha():
            raise Warning(_('Employer Lattitude Degree should contain only Digits!'))
         
        ## Validation for Lattitude Minutes.
        if vals.get('employer_latitude_minutes') == False or not self.employer_latitude_minutes :
            raise Warning(_('Employer Lattitude Minutes should not be blank!'))
        elif vals.get('employer_latitude_minutes') and vals['employer_latitude_minutes'][0] == ' ':
            raise Warning(_('Employer Lattitude Minutes should not start with blank space!'))
        elif vals.get('employer_latitude_minutes') and vals['employer_latitude_minutes'].isalpha():
            raise Warning(_('Employer Lattitude Minutes should contain only Digits!'))
         
        ## Validation for Lattitude Seconds
        if vals.get('employer_latitude_seconds') == False or not self.employer_latitude_seconds :
            raise Warning(_('Employer Lattitude Seconds should not be blank!'))
        elif vals.get('employer_latitude_seconds') and vals['employer_latitude_seconds'][0] == ' ':
            raise Warning(_('Employer Lattitude Seconds should not start with blank space!'))
        elif vals.get('employer_latitude_seconds') and vals['employer_latitude_seconds'].isalpha():
            raise Warning(_('Employer Lattitude Seconds should contain only Digits!'))
          
        ## Validation for Longitude Degree.
        if vals.get('employer_longitude_degree') == False or not self.employer_longitude_degree :
            raise Warning(_('Employer Longitude Degree should not be blank!'))
        elif vals.get('employer_longitude_degree') and vals['employer_longitude_degree'][0] == ' ':
            raise Warning(_('Employer Longitude Degree should not start with blank space!'))
        elif vals.get('employer_longitude_degree') and vals['employer_longitude_degree'].isalpha():
            raise Warning(_('Employer Longitude Degree should contain only Digits!'))
         
        ## Validation for Longitude Minutes.
        if vals.get('employer_longitude_minutes') == False or not self.employer_longitude_minutes :
            raise Warning(_('Employer Longitude Minutes should not be blank!'))
        elif vals.get('employer_longitude_minutes') and vals['employer_longitude_minutes'][0] == ' ':
            raise Warning(_('Employer Longitude Minutes should not start with blank space!'))
        elif vals.get('employer_longitude_minutes') and vals['employer_longitude_minutes'].isalpha():
            raise Warning(_('Employer Longitude Minutes should contain only Digits!'))
         
        ## Validation for Longitude Seconds
        if vals.get('employer_longitude_seconds') == False or not self.employer_longitude_seconds :
            raise Warning(_('Employer Longitude Seconds should not be blank!'))
        elif vals.get('employer_longitude_seconds') and vals['employer_longitude_seconds'][0] == ' ':
            raise Warning(_('Employer Longitude Seconds should not start with blank space!'))
        elif vals.get('employer_longitude_seconds') and vals['employer_longitude_seconds'].isalpha():
            raise Warning(_('Employer Longitude Seconds should contain only Digits!'))
         
        # TODO: Validation for Contact Name.
        ## Validation for Employer Approval Status Id.
        if vals.get('employer_approval_status_id') == False or not self.employer_approval_status_id:
            raise Warning(_('Employer Approval Status Id should not be blank!'))
        elif vals.get('employer_approval_status_id') and vals['employer_approval_status_id'][0] == ' ':
            raise Warning(_('Employer Approval Status Id should not start with blank spaces!'))
        elif vals.get('employer_approval_status_id') and vals['employer_approval_status_id'].isalpha():
            raise Warning(_('Employer Approval Status Id should contain only Digits!'))
         
        ## Validation for Employer Approval Status Start Date.
        if vals.get('employer_approval_status_start_date') == False or not self.employer_approval_status_start_date:
            raise Warning(_('Employer Approval Status Start Date should not be blank!'))
        elif vals.get('employer_approval_status_start_date'):
            approval_start_date = datetime.datetime.strptime(vals['employer_approval_status_start_date'],'%Y-%m-%d').date()
            if approval_start_date > datetime.date.today() :
                raise Warning(_('Employer Approval Status Start Date should not be greater than todays date!'))
         
        ## Validation for Employer Approval Status End Date.
        if int(self.employer_approval_status_id) == 2 and (self.employer_approval_status_end_date == False or vals.get('employer_approval_status_end_date') == False):
            raise Warning(_('You must need to add Employer Approval Status End Date!'))
        elif vals.get('employer_approval_status_end_date'):
            approval_start = self.employer_approval_status_start_date
            approval_end = self.employer_approval_status_end_date
            approval_start_date = approval_start and datetime.datetime.strptime(approval_start,'%Y-%m-%d').date() or \
                (vals.get('employer_approval_status_start_date') and datetime.datetime.strptime(vals['employer_approval_status_start_date'],'%Y-%m-%d').date())
            approval_end_date = approval_end and  datetime.datetime.strptime(approval_end,'%Y-%m-%d').date() or \
                (vals.get('employer_approval_status_end_date') and datetime.datetime.strptime(vals['employer_approval_status_end_date'],'%Y-%m-%d').date())
            if approval_start_date > approval_end_date :
                raise Warning(_('Employer Start Date should not be greater than Employer End Date!'))
        
        ## Validation for Employer Approval Status Number.
        if vals.get('employer_approval_status_num') == False or not self.employer_approval_status_num:
            raise Warning(_('Employer Approval Status Number should not be blank!'))
        elif vals.get('employer_approval_status_num') and vals['employer_approval_status_num'][0] == ' ':
            raise Warning(_('Employer Approval Status Number should not start with blank spaces!'))
        elif vals.get('employer_approval_status_num') and self.check_for_uppercase(vals['employer_approval_status_num'], 'Employer Approval Status Number should be in Uppercase!'):
            pass
          
        ## Validation for Main SDL No.
        if vals.get('employer_main_sdl_no') == False or not self.employer_main_sdl_no :
            raise Warning(_('Employer Main SDL no should not be blank!'))
        elif vals.get('employer_main_sdl_no') and vals['employer_main_sdl_no'][0] == ' ':
            raise Warning(_('Employer Main SDL no should not not start with blank spaces!'))
        elif vals.get('employer_main_sdl_no') and vals['employer_main_sdl_no'][0] not in ['L','N']:
            raise Warning(_('Main SDL No. should start with L (For Leavy Paying) or N (For Non-Leavy Paying).!'))
        elif vals.get('employer_main_sdl_no') and vals['employer_main_sdl_no'][1:]:
            exclude_first_char = vals['employer_main_sdl_no'][1:]
            char_len = len(exclude_first_char) 
            while char_len > 0:
                if exclude_first_char[char_len-1].isalpha():
                    raise Warning(_('Main SDL No. should be combination of L or N followed by 0-9 digits only!')) 
                char_len-=1
         
        ## Validation for Date Stamp.
        if vals.get('employer_date_stamp') == False or not self.employer_date_stamp:
            raise Warning(_('Employer Date Stamp should not be blank!'))
        elif vals.get('employer_date_stamp'):
            date_stamp = vals['employer_date_stamp']
            emp_date_stamp = date_stamp and datetime.datetime.strptime(date_stamp,'%Y-%m-%d').date()
            ## Date stamp should not be greater than todays date.
            if emp_date_stamp > datetime.date.today():
                raise Warning(_('Date Stamp should not be greater than Todays Date!'))
            ## Year in Date Stamp should be greater than 1900.
            if emp_date_stamp.year < 1900:
                raise Warning(_('Date Stamp year should not be less than 1900!'))
    
    
    ## This function is written to provide validations on fields.
    @api.multi
    def write(self, vals):
        user_obj = self.env['res.users']
        employer_user = user_obj.search([('partner_id','=',self.id)])
        ## Checking for Employer Domain
        if vals.get('npo_ngo'):
            vals.update({'empl_status':'NPO / NGO'})
        if vals.get('university'):
            vals.update({'empl_status':'University'})
        if vals.get('college'):
            vals.update({'empl_status':'TVET College'})
        if vals.get('employer_department'):
            vals.update({'empl_status':'Government'})
        if vals.get('other'):
            vals.update({'empl_status':'Other'})
        ###
        res = super(res_partner, self).write(vals)
        if (self.employer == True or vals.get('employer') == True) and employer_user:
            group_data = self.env['res.groups'].search([('name','=','Enrollment')])
            group_list = []
            current_date = datetime.now().date()
            fiscal_year = None
            for fiscal_year_data in self.env['account.fiscalyear'].search([]):
                if current_date >=  datetime.strptime(fiscal_year_data.date_start, '%Y-%m-%d').date() and current_date <= datetime.strptime(fiscal_year_data.date_stop, '%Y-%m-%d').date() :
                    fiscal_year = fiscal_year_data.id
            emp_wsp_sub_status = False
            if fiscal_year :
                for wsp_submission_data in self.wsp_submission_ids :
                    if wsp_submission_data.fiscal_year and wsp_submission_data.fiscal_year.id == fiscal_year and self._context.get('from_wsp_evaluated',False):
                        emp_wsp_sub_status = True
#             if vals.get('wsp_submitted',False):
            if emp_wsp_sub_status == True :
                for data in group_data:
                    tup = (4,data.id)
                    group_list.append(tup)
                employer_user.write({'groups_id':group_list})
            else:
                for data in group_data:
                    tup = (3,data.id)
                    group_list.append(tup)
                employer_user.write({'groups_id':group_list})
        ## Validation for Employer SDL No
#         if self.employer == True :
#             self.validate_employer(vals)
        return res
    
res_partner()

class project_participated(models.Model):
    _name = 'project.participated'
    
    project_id = fields.Many2one('project.project', string='Project')
    project_type_id = fields.Many2one('hwseta.project.types', string='Project Types')
    participated_employer_id = fields.Many2one('res.partner', string='Employer', domain=[('employer','=',True)])
    participated_provider_id = fields.Many2one('res.partner', string='Provider', domain=[('provider','=',True)])
    participate_date = fields.Date(string='Date')
    
    
project_participated()

class project_project(models.Model):
    _inherit = 'project.project'
        
    @api.multi
    def add_partners(self):
        ''' Inheriting add button for adding records under employer master for maintaining project history.'''
        res = super(project_project, self).add_partners()
        emp_proj_data = self.env['partner.project.rel'].search([('select_emp','=',True),('emp_project_id','=',self.id)])
        employer_data = [employer.employer_id for employer in emp_proj_data]
        proj_part = self.env['project.participated']
        for employer in employer_data :
            project_datas = proj_part.search([('project_id','=',self.id),('participated_employer_id','=',employer.id)])
            if project_datas :
                employer.write({'participated_project_ids':[(2, project.id) for project in project_datas]})
            proj_part.create({
                              'project_id':self.id,
                              'project_type_id':self.project_types and self.project_types.id,
                              'participated_employer_id':employer.id,
                              'participate_date' : datetime.now().date(),
                              })
        return res
    
    @api.multi
    def add_all_partners(self):
        ''' Inheriting add all button for adding records under employer master for maintaining project history.'''
        res = super(project_project, self).add_all_partners()
        emp_proj_data = self.env['partner.project.rel'].search([('emp_project_id','=',self.id)])
        employer_data = [employer.employer_id for employer in emp_proj_data]
        proj_part = self.env['project.participated']
        for employer in employer_data :
            project_datas = proj_part.search([('project_id','=',self.id),('participated_employer_id','=',employer.id)])
            if project_datas :
                employer.write({'participated_project_ids':[(2, project.id) for project in project_datas]})
            proj_part.create({
                              'project_id':self.id,
                              'project_type_id':self.project_types and self.project_types.id,
                              'participated_employer_id':employer.id,
                              'participate_date' : datetime.now().date()
                              })
        return res
    
    @api.multi
    def clear_partners(self):
        res = super(project_project, self).clear_partners()
        emp_proj_data = self.env['partner.project.rel'].search([('emp_project_id','=',self.id)])
        employer_data = [employer.employer_id for employer in emp_proj_data]
        proj_part = self.env['project.participated']
        for employer in employer_data :
            project_datas = proj_part.search([('project_id','=',self.id),('participated_employer_id','=',employer.id)])
            if project_datas :
                employer.write({'participated_project_ids':[(2, project.id) for project in project_datas]})
        return res
    
project_project()

class account_journal(models.Model):
    _inherit = 'account.journal'
    
    is_leavy_journal = fields.Boolean('Leavy Journal')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    
account_journal()

## This class is used to maintain Leavy Paid History for perticular Employer.
class leavy_history(models.Model):
    _name = 'leavy.history'
    
    period = fields.Char(string='Period')
    leavy_month = fields.Char(string='Levy Month')
    scheme_year_id = fields.Many2one('scheme.year','Scheme Year')
    mand_grant_amt = fields.Float(string='Mand. Grant Amt')
    desc_grant_amt = fields.Float(string='Desc. Grant Amt')
    admn_grant_amt = fields.Float(string='Adm. Grant Amt')
    penalties = fields.Float(string='Penalty')
    interest = fields.Float(string='Interest')
    total_amt = fields.Float(string='Total Amt')
    employer_id = fields.Many2one('res.partner', string='Employer', domain=[('employer','=',True)])
    
leavy_history()

class account_invoice(models.Model):
    _inherit = 'account.invoice'
    
    employer = fields.Boolean(string='Employer')
    employer_department = fields.Boolean(string='Department')
    levy_period_id = fields.Many2one('account.period', string='Leavy Period')
    scheme_year_id = fields.Many2one('scheme.year','Scheme Year')
    state = fields.Selection(selection_add=[('suspend', 'Suspend')])
    batch_no = fields.Char('Batch No.')
    journal_entry_ref = fields.Char('Reference')
    
    ####################This method is overriden to update values in account move lines###########
    @api.model
    def line_get_convert(self, line, part, date, scheme_year_id):
        return {
            'date_maturity': line.get('date_maturity', False),
            'partner_id': part,
            'name': line['name'][:64],
            'date': date,
            'debit': line['price']>0 and line['price'],
            'credit': line['price']<0 and -line['price'],
            'account_id': line['account_id'],
            'analytic_lines': line.get('analytic_lines', []),
            'amount_currency': line['price']>0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
            'currency_id': line.get('currency_id', False),
            'tax_code_id': line.get('tax_code_id', False),
            'tax_amount': line.get('tax_amount', False),
            'ref': line.get('ref', False),
            'quantity': line.get('quantity',1.00),
            'product_id': line.get('product_id', False),
            'product_uom_id': line.get('uos_id', False),
            'analytic_account_id': line.get('account_analytic_id', False),
            'move_line_type': 'expense',
            'scheme_year_id': scheme_year_id
        }
        
    #############Overriden this method because needed to make changes in sequence numbers###########
    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_invoice_tax = self.env['account.invoice.tax']
        account_move = self.env['account.move']
        for inv in self:
            if not inv.journal_id.sequence_id:
                raise except_orm(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise except_orm(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice

            company_currency = inv.company_id.currency_id
            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
            # check if taxes are all computed
            compute_taxes = account_invoice_tax.compute(inv.with_context(lang=inv.partner_id.lang))
            inv.check_tax_lines(compute_taxes)

            # I disabled the check_total feature
            if self.env['res.users'].has_group('account.group_supplier_inv_check_total'):
                if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding / 2.0):
                    raise except_orm(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise except_orm(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # one move line per tax line
            iml += account_invoice_tax.move_line_get(inv.id)

            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = inv.number

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)

#             name = inv.supplier_invoice_number or inv.name or '/'
            name = inv.supplier_invoice_number or inv.name or 'Mandatory Grant' or '/' 
            totlines = []
            if inv.payment_term:
                totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]
            if totlines:
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'ref': ref,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref
                })

            date = date_invoice
            scheme_year_id = inv.scheme_year_id.id
            print ""
            ####Commented because not getting commercial partner
            #part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            part = self.env['res.partner'].browse(inv.partner_id.id)
            line = [(0, 0, self.line_get_convert(l, part.id, date, scheme_year_id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise except_orm(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = inv.finalize_invoice_move_lines(line)
#             exp_jv_seq = 'EXP'+'-'+ inv.journal_entry_ref + '-' + str(self.env['ir.sequence'].get('account.invoice'))
            move_vals = {
#                 'ref': inv.reference or inv.name,
                 'ref': inv.journal_entry_ref,
#                 'name': exp_jv_seq,
                'line_id': line,
                'journal_id': journal.id,
                'batch_no': inv.batch_no,
                'scheme_year_id': inv.scheme_year_id.id,
                'date': inv.date_invoice,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }
            ctx['company_id'] = inv.company_id.id
            period = inv.period_id
            if not period:
                period = period.with_context(ctx).find(date_invoice)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx['invoice'] = inv
            move = account_move.with_context(ctx).create(move_vals)
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
        self._log_event()
        return True
account_invoice()


class account_voucher(models.Model):
    _inherit = 'account.voucher'
     
    @api.v7
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for sheet in doc.xpath("//sheet"):
                parent = sheet.getparent()
                index = parent.index(sheet)
                for child in sheet:
                    parent.insert(index, child)
                    index += 1
                parent.remove(sheet)
            res['arch'] = etree.tostring(doc)
        return res
    
    # working code +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    @api.multi
    def action_print_payment_report(self):
        print('Button called####################################################################################')
        data1 = self.read()
        data = data1[0]
        if self._context is None:
            self._context = {}
        datas = {
            'ids': self._context.get('active_ids', []),
            'model': 'account.voucher',
            'form': data,
        }
        return self.pool['report'].get_action(self._cr, self._uid, [],'hwseta_finance.organisation_payment_report', data=datas, context=self._context)
    
    employer = fields.Boolean(string='Employer')
    organisation = fields.Many2one('res.partner', string='')
    #### Fields for Implementing Organisation Bulk Payment. ####
    
    ## Boolean for identifying organisation bulk payment.
    bulk_payment = fields.Boolean(string='Organisation Bulk Payment')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    scheme_year_id = fields.Many2one('scheme.year','Scheme Year')
    ## Inherited account_id field because it is required=True by default but it will mess up with bulk  payment functionality.Removing required
    ## will put it required in xml conditionally ( i.e., when regular payments will be done then it will be mandatory.)
    
    @api.multi
    def onchange_bulk_payment(self, bulk_payment, journal) :
        res = {}
        if not bulk_payment :
            return res
        journal_data = self.env['account.journal'].browse(journal)
        account_id = journal_data.default_credit_account_id.id or journal_data.default_debit_account_id.id
        res.update({'value':{'account_id':account_id}})
        return res
    
    ## Inherting Validate button method for adding email notification functionality.
    @api.multi
    def proforma_voucher(self):
        res = super(account_voucher, self).proforma_voucher()
        #### Email Notification to Employer
        #### TODO : Need to notify multiple employer with email if bulk payment will be implemented.
        ir_model_data_obj = self.env['ir.model.data']
        mail_template_id = ir_model_data_obj.get_object_reference('hwseta_finance', 'email_template_org_payment')
        if mail_template_id:
            self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
        ####
        return res
    
    @api.multi
    def recompute_voucher_lines_datewise(self, from_date, to_date, journal_id, price, currency_id, ttype, date, scheme_year):
        ''' This function is similar to recompute_voucher_lines except this function will compute voucher lines
         based on date range whereas recompute_voucher_lines  will compute voucher lines based on partner.'''
        context = self._context
        def _remove_noise_in_o2m():
            """if the line is partially reconciled, then we must pay attention to display it only once and
                in the good o2m.
                This function returns True if the line is considered as noise and should not be displayed
            """
            if line.reconcile_partial_id:
                if currency_id == line.currency_id.id:
                    if line.amount_residual_currency <= 0:
                        return True
                else:
                    if line.amount_residual <= 0:
                        return True
            return False
 
        if context is None:
            context = {}
        move_line_pool = self.env['account.move.line']
        journal_pool = self.env['account.journal']
        line_pool = self.env['account.voucher.line']
 
        #set default values
        default = {
            'value': {'line_dr_ids': [], 'line_cr_ids': [], 'pre_line': False},
        }
 
        # drop existing lines
        line_datas = line_pool.search([('voucher_id', '=', self.id)])
         
        for line in line_datas :
            if line.type == 'cr':
                self.write({'line_cr_ids':[(2, line.id)]})
            else:
                self.write({'line_dr_ids':[(2, line.id)]})
 
        if not journal_id:
            return default
 
        journal = journal_pool.browse(journal_id)
        currency_id = currency_id or journal.company_id.currency_id.id
 
        total_credit = 0.0
        total_debit = 0.0
        account_type = None
        if context.get('account_id'):
            account_type = self.pool['account.account'].browse(context['account_id']).type
        if ttype == 'payment':
            if not account_type:
                account_type = 'payable'
            total_debit = price or 0.0
        else:
            total_credit = price or 0.0
            if not account_type:
                account_type = 'receivable'
        if not context.get('move_line_ids', False):
            ## Need to check datewise
            valid_move_line_ids = []
            ### Taking mandatory provision account from levy configuration.
            ## Provision account should be payable. and we need to show only provision accounts entry for all
            ## according to discussion.
            admin_config = self.env['leavy.income.config'].search([])
            if isinstance(admin_config, list) :
                admin_config = admin_config[0]
            provision_account = admin_config.provision_acc and admin_config.provision_acc.id
            print "1. Account Type:", account_type
            print "2. Provision Account:", provision_account
            print "3. Scheme Year:", scheme_year
            if scheme_year:
                move_lines = move_line_pool.search([('state','=','valid'), ('account_id.type', '=', account_type), ('account_id','=',provision_account), ('reconcile_id', '=', False), ('scheme_year_id', '=', scheme_year)])
            else:
                move_lines = move_line_pool.search([('state','=','valid'), ('account_id.type', '=', account_type), ('account_id','=',provision_account), ('reconcile_id', '=', False)])
            print "======Move Lines=======", move_lines
            for move_line in move_lines :
                move_date = datetime.strptime(move_line.move_id.date, '%Y-%m-%d').date()
                print "--------Move Date--------", from_date, move_date, to_date
                if from_date and to_date:
                    from_date = datetime.strptime(str(from_date), '%Y-%m-%d').date()
                    to_date = datetime.strptime(str(to_date), '%Y-%m-%d').date()
                    if move_date >= from_date and move_date <= to_date :
                        print "----Inside----"
                        valid_move_line_ids.append(move_line.id)
                else:
                    valid_move_line_ids.append(move_line.id)
            ids = valid_move_line_ids
            print "Valid Move Lines>>>>>>>>>>>>>>>>>", ids
        else:
            ids = context['move_line_ids']
        company_currency = journal.company_id.currency_id.id
        move_lines_found = []
 
        #order the lines by most old first
        ids.reverse()
        account_move_lines = move_line_pool.browse(ids)
        remaining_amount = price
        #voucher line creation
        for line in account_move_lines:
            ## Because of -ve and +ve amounts in levy file, provision account values goes in both debit and credit
            if _remove_noise_in_o2m():
                continue
 
            if line.currency_id and currency_id == line.currency_id.id:
                amount_original = abs(line.amount_currency)
                amount_unreconciled = abs(line.amount_residual_currency)
            else:
                amount_original = line.credit or line.debit or 0.0
                amount_unreconciled = abs(line.amount_residual)
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            rs = {
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'employer_id' : line.partner_id.id,
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': amount_original,
                'amount': (line.id in move_lines_found) and min(abs(remaining_amount), amount_unreconciled) or 0.0,
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': line_currency_id,
            }
            remaining_amount -= rs['amount']
            #in case a corresponding move_line hasn't been found, we now try to assign the voucher amount
            #on existing invoices: we split voucher amount by most old first, but only for lines in the same currency
            if not move_lines_found:
                if currency_id == line_currency_id:
                    if line.credit:
                        amount = min(amount_unreconciled, abs(total_debit))
                        rs['amount'] = amount
                        total_debit -= amount
                    else:
                        amount = min(amount_unreconciled, abs(total_credit))
                        rs['amount'] = amount
                        total_credit -= amount
            if rs['amount_unreconciled'] == rs['amount']:
                rs['reconcile'] = True
 
            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)
            if len(default['value']['line_cr_ids']) > 0:
                default['value']['pre_line'] = 1
            elif len(default['value']['line_dr_ids']) > 0:
                default['value']['pre_line'] = 1
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(default['value']['line_dr_ids'], default['value']['line_cr_ids'], price, ttype)
        return default
     
    @api.multi
    def compute_lines(self):
        ''' This function is used to compute credit and debit voucher lines.'''
        context = self._context
        res = {}
        journal_id = self.journal_id
        currency_id = self.currency_id
        if not self.journal_id :
            return {}
        if context is None:
            context = {}
        #TODO: comment me and use me directly in the sales/purchases views
        if self.type in ['sale', 'purchase']:
            pass
        ctx = context.copy()
        # not passing the payment_rate currency and the payment_rate in the context but it's ok because they are reset in recompute_payment_rate
        ctx.update({'date': self.date})
        vals = self.recompute_voucher_lines_datewise(self.from_date, self.to_date, journal_id.id, self.amount, currency_id.id, self.type, self.date, self.scheme_year_id.id)
        debt_dicts = []; cdt_dicts = []
        if vals.get('value', False) and vals['value']['line_dr_ids']:
            debt_dicts = [(0,0,debit_dict) for debit_dict in vals['value']['line_dr_ids'] if isinstance(debit_dict, dict)]
        if vals.get('value', False) and vals['value']['line_cr_ids']:
            cdt_dicts = [(0,0,credit_dict) for credit_dict in vals['value']['line_cr_ids'] if isinstance(credit_dict, dict)]
        self.write({'line_dr_ids' : debt_dicts , 'line_cr_ids' : cdt_dicts})
        return res
    
    
    @api.multi
    def onchange_amount(self, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id):
        res = {}
        if self.bulk_payment :
            pass
        else :
            res = super(account_voucher, self).onchange_amount(amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id)
        return res
           
account_voucher()

class account_voucher_line(models.Model):
    _inherit = 'account.voucher.line'
     
    employer_id = fields.Many2one('res.partner', string='Employer', domain="[('employer','=',True)]")
     
account_voucher_line()


### Inherited this class for implementing bulk payment condition.
class account_move_reconcile(models.Model):
    _inherit = 'account.move.reconcile'
    

    @api.v7
    def _check_same_partner(self, cr, uid, ids, context=None):
        ''' Overriden this method so as to add bulk payment condition. For normal payment
        it will check for the move line partner with voucher partner. in bulk payment this condition will not be considered.'''
        for reconcile in self.browse(cr, uid, ids, context=context):
            move_lines = []
            if not reconcile.opening_reconciliation:
                if reconcile.line_id:
                    first_partner = reconcile.line_id[0].partner_id.id
                    move_lines = reconcile.line_id
                elif reconcile.line_partial_ids:
                    first_partner = reconcile.line_partial_ids[0].partner_id.id
                    move_lines = reconcile.line_partial_ids
                ### Condition for Bulk Payment
                for move_line in move_lines :
                    voucher_line_id = self.pool.get('account.voucher.line').search(cr, uid,[('move_line_id','=',move_line.id)])
                    if voucher_line_id :
                        voucher_line_data = self.pool.get('account.voucher.line').browse(cr,uid,voucher_line_id[0])
                        if voucher_line_data.voucher_id.bulk_payment :
                            return True
                if any([(line.account_id.type in ('receivable', 'payable') and line.partner_id.id != first_partner) for line in move_lines]):
                    return False
        return True
    
    _constraints = [
        (_check_same_partner, 'You can only reconcile journal items with the same partner.', ['line_id', 'line_partial_ids']),
    ]
    
account_move_reconcile()

class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'
    
    period_id = fields.Many2one('account.period', string='Leavy Period')
    scheme_year_id = fields.Many2one('scheme.year','Scheme Year')
    
account_invoice_line()

class leavy_income(models.Model):
    _name = 'leavy.income'
    _description = "Leavy Income"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    
#     import_leavy = fields.Binary(string='Import Levy')
    leavy_file_upload_ids = fields.One2many('leavy.file.upload','leavy_income_id', string='Leavy Files Upload')
    desc = fields.Text(string='Description', default='This will import all uploaded Levy Files and will create -\n'
            '- Journal Entries for Discretionary and Admin Grants.\n'
            '- Creates Levy History for Individual Employer.', readonly=True)
    
    month = fields.Char(string='Month')
    year = fields.Char(string='Year')
    period_id = fields.Many2one('account.period', string='Leavy Period')
    seta_code = fields.Char(string='SETA Code')
    total_leavy = fields.Integer(string='Total Levy Imported')
    progress = fields.Float(string='Progress')
    
    @api.multi
    def get_line(self, name, debit, credit, account_id, partner, analytic_account_id, scheme_year_id):
        result = {
                  'analytic_account_id' : analytic_account_id,
                  'tax_code_id' : False,
                  'analytic_lines' : [],
                  'tax_amount' : False,
                  'name' : name,
                  'ref' : name,
                  'asset_id' : False,
                  'currency_id' : False,
                  'credit' : credit,
                  'product_id' : False,
                  'date_maturity' : False,
                  'debit':debit,
                  'date':datetime.now().date() + relativedelta(months=+1),
                  'amount_currency' : 0,
                  'product_uom_id' : False,
                  'quantity' : 0,
                  'partner_id':partner,
                  'account_id':account_id,
                  'scheme_year_id': scheme_year_id,
                  'move_line_type': 'income',
                  }
        return result
    
    @api.multi
    def get_move_line(self, name, amount, credit_account_id, debit_account_id, partner_id):
        result = []
        credit_line_dict = self.get_line(name, 0, amount, credit_account_id, partner_id)
        result.append((0,0,credit_line_dict))
        debit_line_dict = self.get_line(name, amount, 0, debit_account_id, partner_id)
        result.append((0,0,debit_line_dict))
        return result
    
    @api.multi
    def get_file_read(self, file_to_read):
        options = {'headers': True, 'quoting': '"', 'separator': '|', 'encoding': 'utf-8'}
        csv_iterator = csv.reader(
        file_to_read,
        quotechar=str(options['quoting']),
        delimiter=str(options['separator']))
        csv_nonempty = itertools.ifilter(None, csv_iterator)
        encoding = options.get('encoding', 'utf-8')
        result = itertools.imap(
           lambda row: [item.decode(encoding) for item in row],
           csv_nonempty)
        return result
    
    @api.multi
    def check_year_count(self, filename):
        current_year = datetime.now().date().year
        count = 0
        ## Checking filename having current year 2 times.
        if filename.endswith('.SDL'):
            count = filename.count(str(current_year))
        return count
    
    @api.multi
    def get_invoice_line_dict(self, product, name, account, qty, price_unit, leavy_period, scheme_year):
        line_dict = {
                    'product_id' : product,
                    'name' : name,
                    'account_id':account,
                    'quantity' : qty,
                    'price_unit' : price_unit,
                    'period_id' : leavy_period,
                    'scheme_year_id' : scheme_year
                     }
        return line_dict
    
    @api.multi
    def get_invoice_dict(self, partner, name, invoice_line, employer, state, account, acc_type, journal, leavy_period, due_date, scheme_year):
        invoice_dict = { 
                        'partner_id' : partner,
                        'name' : name,
                        'invoice_line' : invoice_line,
                        'employer' : employer,
                        'state' : state,
                        'account_id' : account,
                        'type' : acc_type,
                        'journal_id' : journal,
                        'period_id':leavy_period,
                        'date_due':due_date,
                        'scheme_year_id':scheme_year,
                        }
        return invoice_dict
    
    @api.multi
    def get_move_val(self, entry_name, ref, line_id, journal_id, date, narration, company_id, batch_no, period, scheme_year):
        result = {
                    'name' : entry_name,
                    'ref' : ref,
                    'line_id' : line_id,
                    'journal_id' : journal_id,
                    'date' : date,
                    'narration' : narration,
                    'company_id' : company_id,
                    'batch_no' : batch_no,
                    'state' : 'draft',
                    'period_id': period,
                    'scheme_year_id': scheme_year, 
                    'is_expense_voucher_created': False
                  }
        return result
    
#     ## Fetching from directory location. Old Code when it was decided to read current year .SDL file from "Levy_Files_HWSETA" directory location. 
#     @api.multi
#     def import_file(self):
#         ## Getting  missing sdl numbers
#         ''' 
#             This method will import Leavies csv and will create Employer Invoices
#             and Employer Payment Automatically. In return generates Journal Entries
#             at the same time with regards to Employer Invoice and Employer Payments.
#         '''
#         invoice_obj = self.env['account.invoice']
#         product_obj = self.env['product.product']
#         partner_obj = self.env['res.partner']
#         journal_obj = self.env['account.journal']
#         mail_msg_obj = self.env['mail.message']
#         mail_msg_data = mail_msg_obj.search([('res_id','=',self.id),('model','=','leavy.income')])
#         ## variable for checking status
#         ## Getting Directory Location from system.
#         ## If problem exist for locating directory, and it is there, Then need to enter command "sudo updatedb" on the terminal then again try importing.
#         proc = subprocess.Popen(["locate 'Levy_Files_HWSETA' | grep 'Levy_Files_HWSETA'$"], stdout=subprocess.PIPE, shell=True)
#         (out, err) = proc.communicate()
#         if len(out.split('\n')) > 2 :
#             raise Warning(_('Please keep "Levy_Files_HWSETA" in any one location, not even in Trash! Currently this directory is on %s locations. Please remove this directory from unwanted locations.')%(out))
#         if not out:
#             raise Warning(_('Please create Directory named "Levy_Files_HWSETA" on server machine and copy levy files there!'))
#         location = out.replace('\n','/')
#         if err is not None:
#             raise Warning(_('Please create Directory named "Levy_Files_HWSETA" on server machine and copy levy files there!'))
#         try :
#             directory_listing = os.listdir(location)
#         except Exception:
#             raise Warning(_('Please create Directory named "Levy_Files_HWSETA" on server machine and copy levy files there!'))
#         levy_count = 0
#         for filename in directory_listing:
#             ## Taking the latest CSV.
#             ## Current year occurance 2 times in filename of latest csv.
#             count = self.check_year_count(filename)
#             if filename.endswith('.SDL') and filename.find('Employers') == -1 and count == 2:
# #             if filename.endswith('.SDL') and filename.find('Employers') == -1
#                 with open(location+filename, 'rb') as f:
#                     ## TODO : Needs to Import Multiple CSV from Location.
#                     result = self.get_file_read(f)
#                     missing_sdl = []
#                     for row in result:
#                         levy_count += 1
#                         employer_data = partner_obj.search([('employer_sdl_no','=',row[2])])
#                         if not employer_data:
#                             missing_sdl.append(row[2])
#                     if missing_sdl:
#                         self = self.with_context({'missing_sdl':missing_sdl})
#                         return {
#                                     'name': 'Missing Employers',
#                                     'type': 'ir.actions.act_window',
#                                     'view_type': 'form',
#                                     'view_mode': 'form',
#                                     'res_model': 'leavy.income.wiz',
#                                     'target':'new',
#                                     'context':self._context,
#                                 }
#         for filename in os.listdir(location):
#             ## If you want to select latest from multiple then use check_year_count function otherwise skip it.
#             ## Take the file if filename having current year 2 times.
#             ## Taking the latest CSV
#             count = self.check_year_count(filename)
#             if filename.endswith('.SDL') and filename.find('Employers') == -1 and count == 2:
#                 with open(location+filename, 'rb') as f:
#                     result = self.get_file_read(f)
#                     price_mandatory = 0;price_discretionary = 0;price_admin = 0;price_penalty = 0
#                     price_interest = 0;products = {}
#                     mandatory_data = product_obj.search([('name','=','Mandatory Grant')])
#                     disc_data = product_obj.search([('name','=','Discretionary Grant')])
#                     admin_data = product_obj.search([('name','=','Admin Grant')])
#                     penalty_data = product_obj.search([('name','=','Levy Penalty')])
#                     interest_data = product_obj.search([('name','=','Levy Interest')])
#                     month_name = '';scheme_year = '';leavy_period = '';seta_code = ''
#                     ## Counting number of records from leavy csv that are imported.
#                     count_leavy = 0
#                     for row in result:
#                         ## product and price required for Customer Invoice for DHET.
#                         scheme_year = row[12]
#                         leavy_period = row[0]
#                         seta_code = row[1]
#                          
#                         products.update({mandatory_data.id:0,admin_data.id:0,disc_data.id:0,penalty_data.id:0,interest_data.id:0})
#                          
#                         price_mandatory += float(row[4])*-1 if float(row[4]) < 0 else float(row[4])
#                         price_discretionary += float(row[5])*-1 if float(row[5]) < 0 else float(row[5])
#                         price_admin += float(row[6])*-1 if float(row[6]) < 0 else float(row[6])
#                         price_penalty += float(row[7])*-1 if float(row[7]) < 0 else float(row[7])
#                         price_interest += float(row[8])*-1 if float(row[8]) < 0 else float(row[8])
#                         ###
#                         employer_data = partner_obj.search([('employer_sdl_no','=',row[2])])
#                         if employer_data:
#                             month_leavy = row[0][4]+row[0][5]
#                             ## Checking for whether Employer Invoice of perticular Employer already raised for the year.
#                             inv_exist = 0
#                             all_invoices_employer = invoice_obj.search([('partner_id','=',employer_data.id),('employer','=',True),('leavy_period','=',row[0]),('scheme_year','=',row[12]),('state','!=','cancel')])
#                             if all_invoices_employer :
#                                 inv_exist = 1
# #                             for empl_invoice in all_invoices_employer:
# #                                 leavy_period_list = [inv_line.leavy_period for inv_line in empl_invoice.invoice_line]
# #                                 scheme_year_list = [inv_line.scheme_year for inv_line in empl_invoice.invoice_line]
# #                                 if (row[0] in leavy_period_list) and (row[12] in scheme_year_list):
# #                                     inv_exist = 1
#                             month_name = calendar.month_name[int(month_leavy)]
#                             ## Code for creating Employer Invoice for Mandatory Grant.
#                             ## If leavy exempted employer then amount should be total amount.
#                             if inv_exist == 0 :
#                                 if employer_data.leavy_exempted:
#                                     amount = row[9]
#                                 else:
#                                     amount = row[4]
#                                 if float(amount) < 0:
#                                     amount = float(amount) * -1
#                                 inv_line_desc = 'Mandatory Grant Amt -'+month_name+' '+str(row[12])
#                                 journal = journal_obj.search([('type','=','purchase'),('is_leavy_journal','=',True)])
#                                 if not journal:
#                                     raise Warning(_('Please Create Levy Journal!'))
#                                 if len(journal) > 1:
#                                     journal = journal[0]
#                                 product_data = product_obj.search([('name','=','Mandatory Grant')])
#                                 ## Taking product expense account
#                                 account = product_data.property_account_expense and product_data.property_account_expense.id or product_data.categ_id.property_account_expense_categ and product_data.categ_id.property_account_expense_categ.id
#                                 invoice_line_dict = self.get_invoice_line_dict(product_data.id, inv_line_desc, account, 1, amount, row[0], '')
#                                 invoice_dict = self.get_invoice_dict(int(employer_data.id), month_name+'/'+str(row[12]), [(0,0,invoice_line_dict)], True, 'draft', int(employer_data.property_account_payable.id), 'in_invoice', journal.id,'',datetime.now().date(), row[12])
#                                 invoice_data = invoice_obj.create(invoice_dict)
#                                 invoice_data.write({'leavy_period':row[0],'scheme_year':row[12]})
#                                 invoice_data.signal_workflow('invoice_open')
#                                 ## Creating Employer Levy History.
#                                 leavy_history_data = self.env['leavy.history'].search([('period','=',row[0]),('scheme_year','=',row[12]),('employer_id','=',employer_data.id)])
#                                 if not leavy_history_data:
#                                     leavy_history_dict = {
#                                                             'period':row[0],
#                                                             'leavy_month':month_name,
#                                                             'scheme_year':scheme_year,
#                                                             'mand_grant_amt':row[4],
#                                                             'desc_grant_amt':row[5],
#                                                             'admn_grant_amt':row[6],
#                                                             'penalties':row[7],
#                                                             'interest':row[8],
#                                                             'total_amt':row[9],
#                                                             'employer_id':employer_data.id,
#                                                           }
#                                     employer_data.write({'leavy_history_ids':[(0,0,leavy_history_dict)]})
#                                 ##
#                                 ## Creating Journal Entries for Discretionary, Admin Grants and Mandatory Grant.
#                                 ## Credit and Debit Account should be refered from Leavy Configuration.
# #                                 move_obj = self.env['account.move']
# #                                 current_date = datetime.now().date()
# #                                 fiscal_year = False
# #                                 for fiscalyear_data in self.env['account.fiscalyear'].search([]) :
# #                                     if current_date >= datetime.strptime(fiscalyear_data.date_start,'%Y-%m-%d').date() and current_date <= datetime.strptime(fiscalyear_data.date_stop,'%Y-%m-%d').date() :
# #                                         fiscal_year = fiscalyear_data.id
# #                                 if not fiscal_year :
# #                                     raise Warning(_('No Fiscal Year defined for the current year!'))
# #                                 leavy_config_data = self.env['leavy.income.config'].search([('wsp_financial_year','=',fiscal_year)], limit=1)
# #                                 if leavy_config_data:
# #                                     if isinstance(leavy_config_data,list):
# #                                         leavy_config_data = leavy_config_data[0]
# #                                 else:
# #                                     raise Warning(_('Please create Admin Configuration!'))
# #                                 ##
# #                                 mand_amount = row[4]  
# #                                 if float(mand_amount) < 0: 
# #                                     mand_amount = float(mand_amount) * -1
# #                                 disc_amount = row[5]
# #                                 if float(disc_amount) < 0:
# #                                     disc_amount = float(disc_amount) * -1
# #                                 admins_amount = row[6]
# #                                 if float(admins_amount) < 0:
# #                                     admins_amount = float(admins_amount) * -1
# #                                 journal_data = journal_obj.search([('is_leavy_journal','=',True)])
# #                                 if len(journal_data)>1:
# #                                     journal_data = journal_data[0]
# #                                 if not journal_data:
# #                                     raise Warning(_('Please Create Levy Journal!'))
# #                                 if not employer_data.leavy_exempted:
# #                                     if not float(disc_amount) == 0:
# #                                         disc_val = self.get_move_line('Disc. Grant Amt', disc_amount, leavy_config_data.discretionary_credit_acc.id, leavy_config_data.discretionary_debit_acc.id, employer_data.id)
# #                                         move_val = self.get_move_val('Disc Grant/'+month_name+'/'+str(row[12])+'/'+row[2], disc_val, journal_data.id, datetime.now().date(), 'Discretionary Grant', employer_data.company_id.id, row[0])
# #                                         move_obj.create(move_val)
# #                                     if not float(admins_amount) == 0:
# #                                         admins_val = self.get_move_line('Admins Grant Amt', admins_amount, leavy_config_data.admins_credit_acc.id, leavy_config_data.admins_debit_acc.id, employer_data.id)
# #                                         move_val = self.get_move_val('Admins Grant/'+month_name+'/'+str(row[12])+'/'+row[2], admins_val, journal_data.id, datetime.now().date(), 'Admins Grant', employer_data.company_id.id, row[0])
# #                                         move_obj.create(move_val)
#                         count_leavy += 1
# #                         total_progress = 100*(float(count_leavy)/float(levy_count))
# #                         self.write({'total_progress':float(total_progress)})
#                     self.write({'total_leavy':count_leavy})
#                     ## Customer Invoice for DHET.
#                     ## Checking whether cust. invoice is already raised for this period.
#                     customer_data = partner_obj.search([('name','=','DHET')])
#                     invoice_datas = invoice_obj.search([('partner_id','=',customer_data.id),('state','!=','cancel')]) 
#                     cust_inv_exists = 0
#                     for invoice_data in invoice_datas :
#                         if invoice_data.leavy_period == row[0] and invoice_data.scheme_year == row[12]:
#                             cust_inv_exists = 1
#                     ##
#                     if cust_inv_exists == 0:
#                         products.update({
#                                          mandatory_data.id:price_mandatory,
#                                          disc_data.id:price_discretionary,
#                                          admin_data.id:price_admin,
#                                          penalty_data.id:price_penalty,
#                                          interest_data.id:price_interest
#                                          })
#                         invoice_line = []
#                         for product_key, product_val in products.iteritems():
#                             product_data = product_obj.browse(product_key)
#                             ## Taking product income account for DHET
#                             account = product_data.property_account_income and product_data.property_account_income.id or product_data.categ_id.property_account_income_categ and product_data.categ_id.property_account_income_categ.id
#                             cust_invoice_line_dict = self.get_invoice_line_dict(product_key, product_data.name+'/'+month_name+'/'+str(row[12]), account, 1, product_val, '', scheme_year)
#                             invoice_line.append((0,0,cust_invoice_line_dict))
#                         journal = journal_obj.search([('type','=','sale')])
#                         if len(journal) > 1:
#                             journal = journal[0]
#                         cust_invoice_dict = self.get_invoice_dict(customer_data.id, 'Amount from DHET for -'+month_name+'/'+str(row[12]), invoice_line, False, 'draft', int(employer_data.property_account_receivable.id), 'out_invoice', journal.id, row[0],datetime.now().date(), row[12])
#                         cust_inv_data = invoice_obj.create(cust_invoice_dict)
#                         ## Validating Customer Invoice.
#                         cust_inv_data.signal_workflow('invoice_open')
#                     ##
#                     ## Code for Making employer Dormant if he didnt paid from last 3 months.
#                     ## otherwise make it Incative if he didnt paid from last 6 months.
# #                     current_date = datetime.now().date()
# #                     date_dormant = datetime.strptime((current_date - timedelta(3*365/12)).isoformat()[:10],'%Y-%m-%d').date()
# #                     date_inactive = datetime.strptime((current_date - timedelta(6*365/12)).isoformat()[:10],'%Y-%m-%d').date()
# #                     dormant_employers = []
# #                     inactive_employers = []
# #                     for employer in partner_obj.search([('employer','=',True)]) :
# #                         dormant = 0
# #                         inactive = 0
# #                         for leavy_history in employer.leavy_history_ids:
# #                             period = leavy_history.period
# #                             month_day = period[-4:]
# #                             period_date = datetime.strptime(period[:4]+'-'+month_day[:2]+'-'+period[-2:], '%Y-%m-%d').date()
# #                             ## Dormant Condition.
# #                             if period_date >= date_dormant:
# #                                 dormant = 1
# #                             ## Inactive Condition.
# #                             if period_date >= date_inactive:
# #                                 inactive = 1
# #                         if dormant == 0:
# #                             dormant_employers.append(employer)
# #                         if inactive == 0:
# #                             inactive_employers.append(employer)
# #                     ## Marking Dormant Employers.
# #                     for do_emp in dormant_employers :
# #                         do_emp.write({'dormant':True})
# #                     for in_emp in inactive_employers :   
# #                         in_emp.write({'active':False})
#                     self.write({'month' : month_name, 'year' : scheme_year, 'leavy_period':leavy_period, 'seta_code':seta_code})    
#         mail_msg_data.write({'body':'<p>Leavies Imported Successfully!</p>'})
#         return True                 


    ## Fetching from directory location.
    ## Process is slow because multiple time file read
#     @api.multi
#     def import_file(self):
#         ## Getting  missing sdl numbers
#         ''' 
#             This method will import Leavies csv and will create Employer Invoices
#             and Employer Payment Automatically. In return generates Journal Entries
#             at the same time with regards to Employer Invoice and Employer Payments.
#         '''
# #         invoice_obj = self.env['account.invoice']
# #         product_obj = self.env['product.product']
#         partner_obj = self.env['res.partner']
#         journal_obj = self.env['account.journal']
# #         mail_msg_obj = self.env['mail.message']
# #         mail_msg_data = mail_msg_obj.search([('res_id','=',self.id),('model','=','leavy.income')])
#         ## variable for checking status
#         ## Getting Directory Location from system.
#         ## If problem exist for locating directory, and it is there, Then need to enter command "sudo updatedb" on the terminal then again try importing.
#         proc = subprocess.Popen(["locate 'Levy_Files_HWSETA' | grep 'Levy_Files_HWSETA'$"], stdout=subprocess.PIPE, shell=True)
#         (out, err) = proc.communicate()
#         if len(out.split('\n')) > 2 :
#             raise Warning(_('Please keep "Levy_Files_HWSETA" in any one location, not even in Trash! Currently this directory is on %s locations. Please remove this directory from unwanted locations.')%(out))
#         if not out:
#             raise Warning(_('Please create Directory named "Levy_Files_HWSETA" on server machine and copy levy files there!'))
#         location = out.replace('\n','/')
#         if err is not None:
#             raise Warning(_('Please create Directory named "Levy_Files_HWSETA" on server machine and copy levy files there!'))
#         try :
#             directory_listing = os.listdir(location)
#         except Exception:
#             raise Warning(_('Please create Directory named "Levy_Files_HWSETA" on server machine and copy levy files there!'))
#         levy_count = 0
#         ## Collecting all .SDL files except Employers.SDL file from Levy_Files_HWSETA directory.
#         valid_files = [filename for filename in directory_listing if filename.endswith('.SDL') and filename.find('Employers') == -1]
#         ##
#         ## Code for checking the list of employers which are not present in the system.
#         ## If some employers does not exist in the system. This code will populate wizard 
#         ## showing list of SDL number of employer which do not exist in the system but exist in .SDL file of levy.
#         missing_sdl = []
#         for filename in valid_files :
#             with open(location+filename, 'rb') as f:
#                 result = self.get_file_read(f)
#                 for row in result:
#                     levy_count += 1
#                     employer_data = partner_obj.search([('employer_sdl_no','=',row[2])])
#                     if not employer_data:
#                         missing_sdl.append(row[2])
#         if missing_sdl:
#             self = self.with_context({'missing_sdl':missing_sdl})
#             return {
#                         'name': 'Missing Employers',
#                         'type': 'ir.actions.act_window',
#                         'view_type': 'form',
#                         'view_mode': 'form',
#                         'res_model': 'leavy.income.wiz',
#                         'target':'new',
#                         'context':self._context,
#                     }
#         ##
#         ## Calculation total amount received from DHET.
#         total_amnt = 0
#         levy_month = 0
#         levy_year = 0
#         file_year = 0
#         for filename in valid_files:
#             with open(location+filename, 'rb') as f:
#                 for row in self.get_file_read(f) :
#                     total_amnt += float(row[9])
#                     levy_month = int(row[0][4:-2])
#                     levy_year = int(row[0][0:4])
#                     file_year = int(row[12])
#         if total_amnt < 0 :
#             total_amnt *= -1
#         ##
#         ## Getting lump sum amount received from DHET form JV for current month.
#         ## TODO : Need to discuss with Ridwaan.
# #         current_month = datetime.now().date().month
#         move_obj = self.env['account.move']
#         dhet_journal = self.env['account.journal'].search([('name','=','DHET Journal')])
#         if len(dhet_journal) > 1 :
#             raise Warning(_('There could not be more than 1 DHET Journal!'))
#         move_ids = []
#         ## Validating period of the lump sum JV with the JV's that we are entering.
# #         for account_move_data in move_obj.search([('journal_id','=',dhet_journal.id),('state','in',['draft','posted'])]):
# #             period_data = account_move_data.period_id
# #             period_strt_dt_month = datetime.strptime(period_data.date_start,'%Y-%m-%d').date().month
# #             period_strt_dt_year = datetime.strptime(period_data.date_start,'%Y-%m-%d').date().year
# #             if (period_strt_dt_month == levy_month) and (period_strt_dt_year == levy_year):
# #                 move_ids.append(account_move_data.id)
#         ###
#         ## Validating period ( now analytic account for period will be made manually in the format mm/yyyy) of the JV with the JV's that we are entering.
#         for account_move_data in move_obj.search([('journal_id','=',dhet_journal.id),('state','in',['draft','posted'])]):
#             ## Checking JV level analytic account for month and year comparison.
# #             analytic_acc_data = account_move_data.account_analytic_id
#             move_line_data = self.env['account.move.line'].search([('move_id','=',account_move_data.id),('credit','>',0)])
#             ## Checking JV line level analytic account for month and year comparison.
#             analytic_acc_data = move_line_data.analytic_account_id
#             if analytic_acc_data and analytic_acc_data.name and analytic_acc_data.name.find('/') != -1 :
#                 month,year = analytic_acc_data.name.split('/')
#                 period_month = int(month); period_year = int(year)
#                 if (period_month == levy_month) and (period_year == levy_year):
#                     move_ids.append(account_move_data.id)
#             else :
#                 raise Warning(_('Analytic account should be in format "mm/yyyy" for DHET JV %s!')%(account_move_data.name))
#         ###
#         if not move_ids :
#             month_name = calendar.month_name[levy_month]
#             raise Warning(_('There is no DHET JV for period %s - %s!')%(month_name,levy_year,))
#         if len(move_ids) > 1 :
#             raise Warning(_('There could not be multiple entries for DHET!'))
#         ## Levy Config data
#         levy_config_data = self.env['leavy.income.config'].search([])
#         if isinstance(levy_config_data,list):
#             levy_config_data = levy_config_data[0]
#         if not levy_config_data :
#             raise Warning(_('Please enter levy configuration inside Admin Configuration!'))
#         ##
#         if move_ids :
#             move_data = move_obj.browse(move_ids[0])
#             total_debit = 0
#             for line_data in move_data.line_id :
#                 total_debit += line_data.debit
#             ## Comparing lump sum amount in the (DHET JV) system with above total amount. If these are equal then JV's for all 5 account will be executed in the system.
#             ## Entering JV's for all the employer in all the file.##
#             if round(total_amnt,2) == round(total_debit,2) :
#                 move_obj = self.env['account.move']
#                 for filename in valid_files:
#                     month_name =''
#                     with open(location+filename, 'rb') as f:
#                         jv_sequence = 1
#                         for row in self.get_file_read(f) :
#                             employer_data = self.env['res.partner'].search([('employer','=',True),('employer_sdl_no','=',str(row[2]) )])
#                             if isinstance(employer_data, list):
#                                 raise Warning(_('Mulitple employers found for SDL No. %s')%(str(row[2]),))
#                             ## Amounts
#                             ## These entries again going to change because still didnt got clarification from SETA.
#                             amt_mandatory = float(row[4])
#                             amt_discretionary = float(row[5])
#                             amt_admin = float(row[6])
#                             amt_penalty = float(row[7])
#                             amt_interest = float(row[8])
#                             amt_total = float(row[9])
#                             ##
#                             month_leavy = row[0][4]+row[0][5]
#                             month_name = calendar.month_name[int(month_leavy)]
#                             ## Accounts related to each financial entity in levy file.
#                             man_account_id = levy_config_data.mandatory_credit_acc and levy_config_data.mandatory_credit_acc.id
#                             dis_account_id = levy_config_data.discretionary_credit_acc and levy_config_data.discretionary_credit_acc.id
#                             adm_account_id = levy_config_data.admins_credit_acc and levy_config_data.admins_credit_acc.id 
#                             pen_account_id = levy_config_data.penalty_acc and levy_config_data.penalty_acc.id 
#                             int_account_id = levy_config_data.interest_acc and levy_config_data.interest_acc.id 
#                             control_acc_id = levy_config_data.control_acc and levy_config_data.control_acc.id
#                             ## Validation for checking every account in levy configuration.
#                             if not (man_account_id or dis_account_id or adm_account_id or pen_account_id or int_account_id or control_acc_id):
#                                 raise Warning(_('Please fill all accounts in levy configuration in Admin Configuration'))
#                             ## Creating Journal items for Journal entries 
#                             ## Credit line entries
#                             ## Receipts from DHET SDL Dump File
#                             ## For -ve balance put credit and +ve balance put debit. For control acc is just opposite
#                             analytic_account_data = self.env['account.analytic.account'].search([('name','=',str(row[12]))])
#                             if isinstance(analytic_account_data,list) :
#                                 analytic_account_data = analytic_account_data[0]
#                             move_lines = []
#                             ## Mandatory entry
#                             if not amt_mandatory == 0 :
#                                 if amt_mandatory < 0 :
#                                     mand_line_dict = self.env['leavy.income'].get_line('Mandatory Amount for'+'-'+month_name+'-'+str(row[12]), 0, (amt_mandatory*(-1)), man_account_id, employer_data.id, analytic_account_data.id)
#                                     move_lines.append((0,0,mand_line_dict))
#                                 else :
#                                     mand_line_dict = self.env['leavy.income'].get_line('Mandatory Amount for'+'-'+month_name+'-'+str(row[12]), amt_mandatory, 0, man_account_id, employer_data.id, analytic_account_data.id)
#                                     move_lines.append((0,0,mand_line_dict))
#                             ## Discretionary entry
#                             if not amt_discretionary == 0 :
#                                 if amt_discretionary < 0 :
#                                     dis_line_dict = self.env['leavy.income'].get_line('Discretionary Amount for'+'-'+month_name+'-'+str(row[12]), 0, (amt_discretionary*(-1)), dis_account_id, employer_data.id, analytic_account_data.id)
#                                     move_lines.append((0,0,dis_line_dict))
#                                 else :
#                                     dis_line_dict = self.env['leavy.income'].get_line('Discretionary Amount for'+'-'+month_name+'-'+str(row[12]), amt_discretionary, 0, dis_account_id, employer_data.id, analytic_account_data.id)
#                                     move_lines.append((0,0,dis_line_dict))
#                             ## Admin entry
#                             if not amt_admin == 0 :
#                                 if amt_admin < 0 :
#                                     adm_line_dict = self.env['leavy.income'].get_line('Admins Amount for'+'-'+month_name+'-'+str(row[12]), 0, (amt_admin*(-1)), adm_account_id, employer_data.id, analytic_account_data.id)
#                                     move_lines.append((0,0,adm_line_dict))
#                                 else :
#                                     adm_line_dict = self.env['leavy.income'].get_line('Admins Amount for'+'-'+month_name+'-'+str(row[12]), amt_admin, 0, adm_account_id, employer_data.id, analytic_account_data.id)
#                                     move_lines.append((0,0,adm_line_dict))
#                             ## Penalty entry
#                             if not amt_penalty == 0 :
#                                 if amt_penalty < 0:
#                                     pen_line_dict = self.env['leavy.income'].get_line('Penalty Amount for'+'-'+month_name+'-'+str(row[12]), 0, (amt_penalty*(-1)), pen_account_id, employer_data.id, analytic_account_data.id)
#                                     move_lines.append((0,0,pen_line_dict))
#                                 else :
#                                     pen_line_dict = self.env['leavy.income'].get_line('Penalty Amount for'+'-'+month_name+'-'+str(row[12]), amt_penalty, 0, pen_account_id, employer_data.id, analytic_account_data.id)
#                                     move_lines.append((0,0,pen_line_dict))
#                             ## Interest entry
#                             if not amt_interest == 0:
#                                 if amt_interest < 0:
#                                     int_line_dict = self.env['leavy.income'].get_line('Interest Amount for'+'-'+month_name+'-'+str(row[12]), 0, (amt_interest*(-1)), int_account_id, employer_data.id, analytic_account_data.id)
#                                     move_lines.append((0,0,int_line_dict))
#                                 else :
#                                     int_line_dict = self.env['leavy.income'].get_line('Interest Amount for'+'-'+month_name+'-'+str(row[12]), amt_interest, 0, int_account_id, employer_data.id, analytic_account_data.id)
#                                     move_lines.append((0,0,int_line_dict))
#                             ## Debit line entry
#                             if not amt_total == 0:
#                                 if amt_total < 0 :
#                                     debit_line_dict = self.env['leavy.income'].get_line('Amount for employer'+''+employer_data.name+'-'+month_name+'-'+str(row[12]), (amt_total*(-1)), 0, control_acc_id, employer_data.id, analytic_account_data.id)
#                                     move_lines.append((0,0,debit_line_dict))
#                                 else :
#                                     debit_line_dict = self.env['leavy.income'].get_line('Amount for employer'+''+employer_data.name+'-'+month_name+'-'+str(row[12]), 0, amt_total, control_acc_id, employer_data.id, analytic_account_data.id)
#                                     move_lines.append((0,0,debit_line_dict))
#                             ## Journal Entry
#                             journal_data = journal_obj.search([('type','=','general'),('code','=','GEN')])
#                             if len(journal_data) > 1:
#                                 journal_data = journal_data[0]
#                             journal_data.id, datetime.now().date(), 'Admins Grant', employer_data.company_id.id, row[0]
#                               
#                             filename = filename.split('.')[0]
#                             entry_name = filename+'-'+str(jv_sequence)
#                             ## Getting Posting Date
#                             posting_date = datetime.strptime(row[0][0:4]+'-'+row[0][4:6]+'-'+row[0][6:], "%Y-%m-%d").date()
#                             ##
#                             ## Getting Period as per .SDL File levy period. By default system will take current date period. ##
#                             period = None
#                             for period_data in self.env['account.period'].search([]) :
#                                 period_strt_dt_month = datetime.strptime(period_data.date_start,'%Y-%m-%d').date().month
#                                 period_strt_dt_year = datetime.strptime(period_data.date_start,'%Y-%m-%d').date().year
#                                 if (period_strt_dt_month == int(row[0][4:6])) and (period_strt_dt_year == int(row[0][0:4])):
#                                     period = period_data.id
#                             ##
#                             move_val = self.env['leavy.income'].get_move_val(entry_name,filename, move_lines, journal_data.id, posting_date, 'Employer entry', employer_data.company_id.id, row[0], period)
#                             move_obj.create(move_val)
#                             jv_sequence += 1
#                             #####
#                     self.write({'month' : month_name, 'year' : str(row[12]), 'leavy_period' : str(row[0]), 'seta_code' : str(row[1]), 'total_leavy' : levy_count})
#             else :
#                 ## Calculating difference
#                 diff = 0
#                 if total_amnt > total_debit :
#                     diff = total_amnt - total_debit
#                 else :
#                     diff = total_debit - total_amnt
#                 raise Warning(_('DHET entry does not matching the total amount!. Total Amount = %s and Total Amnt DHET = %s. Difference is %s.')%(total_amnt,total_debit,diff))
#             ## Entering 2nd set of JV's for Mandatory expense and provision.
#             ## These can be entered parallely along with income levy JV entry.
#             ## But needs to confirm because it has been decided that once all income JV's are completed then expense
#             ## JV's will be entered. If both these JV's will be entered simultaneously then these process will happen
#             ## within above for loop ( single for loop instead of two )
#             emp_wsp_not_approved = []
#             for filename in valid_files:
#                 month_name = ''
#                 with open(location+filename, 'rb') as f:
#                     jv_sequence = 1
#                     for row in self.get_file_read(f) :
#                         employer_data = self.env['res.partner'].search([('employer','=',True),('employer_sdl_no','=',str(row[2]))])
#                         # TODO : Needs to add exempt condition.
#                         if not employer_data.emp_exempt :
#                             wsp_submission_data = self.env['wsp.submission.track'].search([('employer_id','=',employer_data.id),('status','=','accepted'),('scheme_year','=',str(row[12])) ])
#                             if wsp_submission_data :
#                                 amt_mandatory = float(row[4])
#                                 expense_acc_id = levy_config_data.expense_acc and levy_config_data.expense_acc.id
#                                 provision_acc_id = levy_config_data.provision_acc and levy_config_data.provision_acc.id
#                                 month_leavy = row[0][4]+row[0][5]
#                                 month_name = calendar.month_name[int(month_leavy)]
#                                 analytic_account_data = self.env['account.analytic.account'].search([('name','=',str(row[12]))])
#                                 if isinstance(analytic_account_data,list) :
#                                     analytic_account_data = analytic_account_data[0]
#                                 move_lines = []
#                                 if not amt_mandatory == 0 :
#                                     if amt_mandatory < 0 :
#                                         mand_line_dict = self.env['leavy.income'].get_line('Mandatory Grant Expense'+'-'+month_name+'-'+str(row[12]), (amt_mandatory*(-1)), 0, expense_acc_id, employer_data.id, analytic_account_data.id)
#                                         move_lines.append((0,0,mand_line_dict))
#                                         prov_line_dict = self.env['leavy.income'].get_line('Mandatory Grant Provision'+'-'+month_name+'-'+str(row[12]), 0,(amt_mandatory*(-1)), provision_acc_id, employer_data.id, analytic_account_data.id)
#                                         move_lines.append((0,0,prov_line_dict))
#                                     else :
#                                         mand_line_dict = self.env['leavy.income'].get_line('Mandatory Grant Expense'+'-'+month_name+'-'+str(row[12]), 0, amt_mandatory, expense_acc_id, employer_data.id, analytic_account_data.id)
#                                         move_lines.append((0,0,mand_line_dict))
#                                         prov_line_dict = self.env['leavy.income'].get_line('Mandatory Grant Provision'+'-'+month_name+'-'+str(row[12]), amt_mandatory,0, provision_acc_id, employer_data.id, analytic_account_data.id)
#                                         move_lines.append((0,0,prov_line_dict))
#                                   
#                                 journal_data = journal_obj.search([('type','=','general'),('code','=','GEN')])
#                                 if len(journal_data) > 1:
#                                     journal_data = journal_data[0]
#                                 filename = filename.split('.')[0]
#                                 entry_name = 'EXP'+'-'+filename+'-'+str(jv_sequence)
#                                 ## Getting Posting Date
#                                 posting_date = datetime.strptime(row[0][0:4]+'-'+row[0][4:6]+'-'+row[0][6:], "%Y-%m-%d").date()
#                                 ##
#                                 ## Getting Period as per .SDL File levy period. By default system will take current date period. ##
#                                 period = None
#                                 for period_data in self.env['account.period'].search([]) :
#                                     period_strt_dt_month = datetime.strptime(period_data.date_start,'%Y-%m-%d').date().month
#                                     period_strt_dt_year = datetime.strptime(period_data.date_start,'%Y-%m-%d').date().year
#                                     if (period_strt_dt_month == int(row[0][4:6])) and (period_strt_dt_year == int(row[0][0:4])):
#                                         period = period_data.id
#                                 ##
#                                 move_val = self.env['leavy.income'].get_move_val(entry_name, filename, move_lines, journal_data.id, posting_date, 'Employer entry', employer_data.company_id.id, row[0], period)
#                                 move_obj.create(move_val)
#                                 jv_sequence += 1    
#                             else :
#                                 emp_wsp_not_approved.append((wsp_submission_data.id,employer_data.id))
#         else :
#             raise Warning(_('Please enter DHET Entry manually!'))
#                 ## TODO : Need to enter other sets of JV's and Levy History.
#         return True
      
    ## Optimised code for levy income import
    @api.multi
    def import_file(self):
        ## Getting  missing sdl numbers
        ''' 
            This method will import Leavies csv and will create Employer Invoices
            and Employer Payment Automatically. In return generates Journal Entries
            at the same time with regards to Employer Invoice and Employer Payments.
        '''
        partner_obj = self.env['res.partner']
        journal_obj = self.env['account.journal']
        move_obj = self.env['account.move']
        levy_income_obj = self.env['leavy.income']
        levy_count = 0
        ## Collecting all .SDL files except Employers.SDL file from Levy_Files_HWSETA directory.
        valid_files,file_name = [], []
        if self.leavy_file_upload_ids:
            for leavy_file in self.leavy_file_upload_ids:
                if leavy_file.attachment_file_id.name.endswith('.SDL') and leavy_file.attachment_file_id.name.find('Employers') == -1:
                    valid_files.append(leavy_file.attachment_file_id.name)
                if "Employers" in leavy_file.attachment_file_id.name and leavy_file.attachment_file_id.name.endswith('.SDL'):
                    file_name.append(leavy_file.attachment_file_id.name)
        else:
            raise Warning(_('Please upload Levy Files!'))
        employer_file = []
        if file_name:
            employer_file = file_name
        ## Code for checking the list of employers which are not present in the system.
        ## If some employers does not exist in the system. This code will populate wizard 
        ## showing list of SDL number of employer which do not exist in the system but exist in .SDL file of levy.
        missing_sdl = [];levy_records = []
        total_amnt = 0;levy_month = 0;levy_year = 0;file_year = 0
        for filename in valid_files:
            self._cr.execute("select max(id) from ir_attachment where name = '%s'" %(filename))
            ir_attachment_id = self._cr.fetchone()
            attachment_id = self.env['ir.attachment'].search([('id', '=', ir_attachment_id[0])])
            if attachment_id:
                attachment_file = base64.b64decode(attachment_id.datas)
                for line in attachment_file.split('\n'):
                    row = line.split('|')
                    ## Collecting all levies in a tuple
                    try:
                        row[12] = str(row[12])[:-1]
                        levy_tuple = (row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],filename)
                        ## for skiping the Zero amount JV for L Number
                        if float(row[9]) != 0.0:
                            levy_records.append(levy_tuple)
                            levy_count += 1 
                        ## Collecting all SDL numbers from Levy Files which are not in the system.
                        self._cr.execute("select id from res_partner where employer_sdl_no = %s " %("'"+row[2]+"'" ))
                        re_p =self._cr.fetchall()
                        employer_data1 = partner_obj.browse([i[0] for i in re_p])
                        employer_data = partner_obj.browse([i[0] for i in re_p])
                        if not employer_data:
                            missing_sdl.append(row[2])
                        ## Calculating total of all levies
                        total_amnt += float(row[9])
    #                     levy_month = int(row[0][4:-2])+1 commented on 26th sept due to unable to import
                        levy_month = int(row[0][4:-2])
                        levy_year = int(row[0][0:4])
                        file_year = int(row[12])
                    except:
                        pass
        ## Showing SDL number list which are not exists in the system but exist in the levy file.
        if missing_sdl:
            missing_emp_details_list = [['Employer','SARS Number','SDL No.','Name','Registration Number','Trading Name','Extra Physical Address1','Extra Physical Address2','Extra Physical Address3','Extra Physical Zip','Total Anual Payroll','Phone']]
            if not employer_file:
                raise Warning(_('Please upload Employer File!'))
            self._cr.execute("select max(id) from ir_attachment where name = '%s'" %(employer_file[0]))
            ir_attachment_id = self._cr.fetchone()
            attachment_id = self.env['ir.attachment'].search([('id', '=', ir_attachment_id[0])])
            if attachment_id:
                attachment_file = base64.b64decode(attachment_id.datas)
                for line in attachment_file.split('\n'):
                    row = line.split('|')
                    for sdl in missing_sdl:
                        if str(sdl) == row[0]:
                            missing_emp_details_list.append(['True',row[0],row[0],row[4],row[9],row[14],row[15],row[16],row[17],row[20],row[46],row[60]])
            #This code will write missing employers details into newly created xls file
            buf = cStringIO.StringIO()
            writer = csv.writer(buf, dialect=csv.Dialect.lineterminator)
            writer.writerows(missing_emp_details_list)
            out = base64.encodestring(buf.getvalue())
            attachment_obj = self.env['ir.attachment']
            new_attach = attachment_obj.create({
                'name':'Missing Employer Data.csv',
                'res_name': 'leavy_income',
                'type': 'binary',
                'res_model': 'leavy.income',
                'datas':out,
            })
            self = self.with_context({'missing_sdl':missing_sdl,'incorrect_id':new_attach.id})
            return {
                        'name': 'Missing Employers',
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'leavy.income.wiz',
                        'target':'new',
                        'context': self._context,
                    }
        ## If total is negative then make it positive.
        if total_amnt < 0 :
            total_amnt *= -1
#         dhet_journal = journal_obj.search([('name','=','DHET Journal')])
        move_ids = []
        ## Validating period ( now analytic account for period will be made manually in the format mm/yyyy) of the JV with the JV's that we are entering.
        
        self._cr.execute("select id,name from account_move where journal_id = (select id from account_journal where name = 'DHET Journal') and state in ('draft','posted')")
        account_move_list =self._cr.fetchall()
#         print "LLLLLLLLLLLLLLLLLLLLL",move_obj.search([('journal_id','=',dhet_journal.id),('state','in',['draft','posted'])])
#         for account_move_data in move_obj.browse(lst):
        for account_move_data in account_move_list:     
            self._cr.execute("select analytic_account_id from account_move_line where move_id = %s and credit > 0"%(account_move_data[0],))
            lst_line =[i[0] for i in self._cr.fetchall()]
#             move_line_data = self.env['account.move.line'].search([('move_id','=',account_move_data.id),('credit','>',0)])
            ## Checking JV line level analytic account for month and year comparison.
#             analytic_acc_data = self.env['account.analytic.account'].browse(lst_line)
            if lst_line:
                if lst_line[0] is not None:
                    self._cr.execute("select name from account_analytic_account where id = %s"%(lst_line[0],))
                    analytic_acc_data = self._cr.fetchone()
                    if not analytic_acc_data :
                        raise Warning(_('Please include analytic account inside DHET JV!'))
                    elif analytic_acc_data and analytic_acc_data[0] and analytic_acc_data[0].find('/') != -1 :
                        month,year = analytic_acc_data[0].split('/')
                        period_month = int(month); period_year = int(year)
                        if (period_month == levy_month) and (period_year == levy_year):
                            move_ids.append(account_move_data[0])
                    else :
                        raise Warning(_('Analytic account should be in format "mm/yyyy" for DHET JV %s!')%(account_move_data[1],))
        ###
        if not move_ids :
            month_name = calendar.month_name[levy_month]
            if month_name:
                raise Warning(_('There is no DHET JV for period %s - %s!')%(month_name,levy_year,))
            else:
                raise Warning('Attachment Name should be same as file name!')
        ## Levy Config data
        levy_config_data = self.env['leavy.income.config'].search([])
        if isinstance(levy_config_data,list):
            levy_config_data = levy_config_data[0]
        if not levy_config_data :
            raise Warning(_('Please enter levy configuration inside Admin Configuration!'))
        move_data = move_obj.browse(move_ids[0])
        ## Total from system DHET JV.
        total_debit = 0
        for line_data in move_data.line_id :
            total_debit += line_data.debit
        ## Comparing lump sum amount in the (DHET JV) system with above total amount. If these are equal then JV's for all 5 account will be executed in the system.
        ## Showing warning message if total from levy and total of lump sum entry from the system does not matches.
        if not (round(total_amnt,2) == round(total_debit,2)):
            month_name = calendar.month_name[levy_month]
            diff = 0
            if total_amnt > total_debit :
                diff = total_amnt - total_debit
            else :
                diff = total_debit - total_amnt
            raise Warning(_('DHET entry variance on total amount for the period: %s - %s\nTotal Levy Amount = %s\nCurrent DHET voucher amount = %s\nDifference Amount = %s')%(month_name,levy_year,total_amnt,total_debit,diff))
        ## Entering Income and Expense JV's ( Mandatory ) for all the employer in all the file if total matches ##
        else :
            jv_sequence = 1; jv_seq_exp = 1
            
            prev_file_name = ''
            for row in levy_records :
                try:
                    self._cr.execute("select id,name,company_id,emp_exempt from res_partner where employer_sdl_no = %s and employer = True" %("'"+row[2]+"'" ))
                    employer_data =self._cr.fetchone()
    #                 employer_data = self.env['res.partner'].browse(lst_res)
                    if isinstance(employer_data, list):
                        raise Warning(_('Mulitple employers found for SDL No. %s')%(str(row[2]),))
                    ## 1st Set of JV's for Icome JV ##
                    ## These entries again going to change because still didnt got clarification from SETA.
    #                 amt_mandatory = float(row[4])
    #                 amt_discretionary = float(row[5])
    #                 amt_admin = float(row[6])
                    amt_penalty = float(row[7])
                    amt_interest = float(row[8])
                    amt_total = float(row[9])
                    if amt_total>0:
                        cr_sum = amt_total 
                        dr_sum = 0
                    else:
                        cr_sum = 0
                        dr_sum = amt_total*-1
                    
                    diff1 = 0
                    diff2 = 0
                    debit1 = 0
                    credit1 = 0
                        ##
                    month_leavy = row[0][4]+row[0][5]
                    month_name = calendar.month_name[int(month_leavy)]
                    ## Accounts related to each financial entity in levy file.
                    man_account_id = levy_config_data.mandatory_credit_acc and levy_config_data.mandatory_credit_acc.id
                    dis_account_id = levy_config_data.discretionary_credit_acc and levy_config_data.discretionary_credit_acc.id
                    adm_account_id = levy_config_data.admins_credit_acc and levy_config_data.admins_credit_acc.id 
                    pen_account_id = levy_config_data.penalty_acc and levy_config_data.penalty_acc.id 
                    int_account_id = levy_config_data.interest_acc and levy_config_data.interest_acc.id 
                    control_acc_id = levy_config_data.control_acc and levy_config_data.control_acc.id
                    ## Validation for checking every account in levy configuration.
                    if not (man_account_id or dis_account_id or adm_account_id or pen_account_id or int_account_id or control_acc_id):
                        raise Warning(_('Please fill all accounts in levy configuration in Admin Configuration'))
                    ## Creating Journal items for Journal entries 
                    ## Credit line entries
                    ## Receipts from DHET SDL Dump File
                    ## For -ve balance put credit and +ve balance put debit. For control acc is just opposite
                    self._cr.execute("select id from account_analytic_account where name = %s " %("'"+row[12]+"'"))
                    analytic_account_data = self._cr.fetchone()
                     
                    if not analytic_account_data :
                        raise Warning(_('Analytical account not created for the %s ')%(str(row[12])))
                    move_lines = []
                    ## Mandatory entry
                    period = None
                    self._cr.execute("select id from grant_config_new where scheme_yr = (select id from scheme_year where name = %s )" %("'"+row[12]+"'" )) 
                    res = self._cr.fetchall()
                    grant_cc =[i[0] for i in res]
                    grant_conf = self.env['grant.config.new'].browse(grant_cc)
                    scheme_year_id = self.env['scheme.year'].search([('name', '=',str(row[12]))]).id
                    if float(grant_conf.hwseta_rec) == 0:
                        raise Warning(_('Please Configure the SDL file Calculation Parameters'))
                    else:
                        if levy_config_data.grand_acc: 
                            for acc in levy_config_data.grand_acc:
                                amt_mandatory =0
                                if grant_conf.grant_assign_id:
                                    for grant_assign in grant_conf.grant_assign_id:
                                        if grant_assign.grant_id == acc.grant_id:
                                            amt_mandatory = float(float(grant_assign.value)/float(grant_conf.hwseta_rec))*(float(row[9]))
                                if not amt_mandatory == 0 :
                                    if amt_mandatory < 0 :
                                        mand_line_dict = levy_income_obj.get_line(acc.grant_id.name+' Amount for'+'-'+month_name+'-'+str(row[12]), 0, (amt_mandatory*(-1)), acc.account_id.id, employer_data[0], analytic_account_data[0], scheme_year_id)
                                        move_lines.append((0,0,mand_line_dict))
                                        cr_sum=cr_sum+(amt_mandatory*(-1))
                                    else :
                                        mand_line_dict = levy_income_obj.get_line(acc.grant_id.name+' Amount for'+'-'+month_name+'-'+str(row[12]), amt_mandatory, 0, acc.account_id.id, employer_data[0],analytic_account_data[0], scheme_year_id)
                                        move_lines.append((0,0,mand_line_dict))
                                        dr_sum=dr_sum+amt_mandatory
                    ## Debit line entry
                    if not amt_total == 0:
                        if amt_total < 0 :
                            debit_line_dict = levy_income_obj.get_line('Amount for employer'+' '+employer_data[1]+'-'+month_name+'-'+str(row[12]), (amt_total*(-1)), 0, control_acc_id, employer_data[0], analytic_account_data[0], scheme_year_id)
                            move_lines.append((0,0,debit_line_dict))
                        else :
                            debit_line_dict = levy_income_obj.get_line('Amount for employer'+' '+employer_data[1]+'-'+month_name+'-'+str(row[12]), 0, amt_total, control_acc_id, employer_data[0], analytic_account_data[0], scheme_year_id)
                            move_lines.append((0,0,debit_line_dict))
                    ## Journal Entry
                    self._cr.execute("select id from account_journal where type = 'general' and code ='GEN' " ) 
                    journal_data = self._cr.fetchone()
                    if not journal_data:
                        raise Warning(_('Please create General Journal (ZAR)  '))
    #                 journal_data.id, datetime.now().date(), 'Admins Grant', employer_data[2], row[0]
                    if row[13].split('.')[0] != prev_file_name:
                        jv_sequence = 1
                    filename = row[13].split('.')[0]
                    prev_file_name = filename
                    
                    entry_name = filename+'-'+str(jv_sequence)
                    ## Getting Posting Date
                    posting_date1 = datetime.strptime(row[0][0:4]+'-'+str((row[0][4:6]))+'-'+row[0][6:], "%Y-%m-%d").date()
                    posting_date = posting_date1 + relativedelta(months=+1)
                    ## Getting Period as per .SDL File levy period. By default system will take current date period. ##
                    period = None
                    self._cr.execute("select id from account_period" ) 
                    period_q =[i[0] for i in self._cr.fetchall()]
                    for period_data in self.env['account.period'].browse(period_q):
                        period_strt_dt_month = datetime.strptime(period_data.date_start,'%Y-%m-%d').date().month
                        period_strt_dt_year = datetime.strptime(period_data.date_start,'%Y-%m-%d').date().year
                        if int(row[0][4:6])+1 > 12:
                            if (period_strt_dt_month == int(row[0][4:6])) and (period_strt_dt_year == int(row[0][0:4])+1):
                                period = period_data.id
                        else:
                            if (period_strt_dt_month == int(row[0][4:6])+1) and (period_strt_dt_year == int(row[0][0:4])):
                                period = period_data.id
                    query_string = """select id from account_move where ref='%s' and
                                         journal_id=%s and 
                                         date='%s' and 
                                         partner_id=%s and 
                                         narration='Employer entry' and
                                        batch_no='%s' and period_id=%s """%(filename,journal_data[0],posting_date,employer_data[0],row[0],int(period),)
                    self._cr.execute(query_string)
                     
                    exiting_move_line = self._cr.fetchone()
                    
                    if not exiting_move_line:
                        move_val = levy_income_obj.get_move_val(entry_name,filename, move_lines, journal_data[0], posting_date, 'Employer entry', employer_data[2], row[0], period, scheme_year_id)
                        mv_id = move_obj.create(move_val)
                        #  Balancing Unbalanced move lines
                        total_credit = 0.0
                        total_debit = 0.0
                        for move in mv_id.line_id:
                            if move.credit:
                                total_credit = total_credit + move.credit
                            if move.debit:
                                total_debit = total_debit + move.debit
                        if str(total_credit) != str(total_debit):
                            for move in mv_id.line_id:
                                if total_credit < total_debit:
                                    if move.name.startswith("Discretionary"):
                                        if move.debit != 0.00:
                                            move.debit = move.debit - (.01)
                                        if move.credit != 0.00:
                                            move.credit = move.credit + (.01)
                                elif total_credit > total_debit:
                                    if move.name.startswith("Discretionary"):
                                        if move.debit != 0.0:
                                            move.debit = move.debit + (.01)
                                        if move.credit != 0.0:
                                            move.credit = move.credit - (.01)
                        self._cr.commit()
                        jv_sequence += 1
                    ## Creating Employer Levy History.
                    employer_obj = partner_obj.search([('id', '=', employer_data[0])])
                    if employer_obj:
                        leavy_history_data = self.env['leavy.history'].search([('period','=',row[0]),('scheme_year_id','=',scheme_year_id),('employer_id','=',employer_data[0])])
                        if not leavy_history_data:
                            leavy_history_dict = {
                                                    'period':row[0],
                                                    'leavy_month':month_name,
                                                    'scheme_year_id':scheme_year_id,
                                                    'mand_grant_amt':row[4],
                                                    'desc_grant_amt':row[5],
                                                    'admn_grant_amt':row[6],
                                                    'penalties':row[7],
                                                    'interest':row[8],
                                                    'total_amt':row[9],
                                                    'employer_id':employer_data[0],
                                                  }
                            print "========Employer ID==========", employer_data[0]
                            employer_obj.write({'leavy_history_ids':[(0,0,leavy_history_dict)]})
                except MissingError:
                    pass
            self.write({'month' : month_name, 'year' : levy_year, 'period_id' : period, 'seta_code' : str(row[1]), 'total_leavy' : levy_count})
            self = self.with_context({'message': 'Levy Files Imported Successfully!!!'})
            return {
                        'name': 'Levy Import Log',
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'levy.import.log',
                        'target':'new',
                        'context':self._context,
                    }
        return True
leavy_income()

class leavy_file_upload(models.Model):
    _name = 'leavy.file.upload'
    
    name = fields.Char(string='Name')
    attachment_file_id = fields.Many2one('ir.attachment', string='File')
    leavy_income_id = fields.Many2one('leavy.income', string='Leavy Income')

class leavy_income_config(models.Model):
    _name = 'leavy.income.config'
    _inherit = 'mail.thread'
    _rec_name = 'wsp_financial_year'
    
    active = fields.Boolean(string='Active', default=True)
    mandatory_credit_acc = fields.Many2one('account.account', string='Mandatory Cr Acc')
#     mandatory_debit_acc = fields.Many2one('account.account', string='Mandatory Dr Acc')
    discretionary_credit_acc = fields.Many2one('account.account', string='Discretionary Cr Acc', track_visibility='onchange')
#     discretionary_debit_acc = fields.Many2one('account.account', string='Discretionary Dr Acc', track_visibility='onchange')
    admins_credit_acc = fields.Many2one('account.account', string='Admins Cr Acc', track_visibility='onchange')
    penalty_acc = fields.Many2one('account.account', string='Penalty Account', track_visibility='onchange')
    interest_acc = fields.Many2one('account.account', string='Interest Account', track_visibility='onchange')
#     admins_debit_acc = fields.Many2one('account.account', string='Admins Dr Acc', track_visibility='onchange')
    control_acc = fields.Many2one('account.account', string='DHET Clearing Account', track_visibility='onchange')
    expense_acc = fields.Many2one('account.account', string='Mandatory Grant Expense Account', track_visibility='onchange')
    provision_acc = fields.Many2one('account.account', string='Mandatory Grant Provision Account', track_visibility='onchange')
#     disc_expense_acc = fields.Many2one('account.account', string='Discretionary Grant Expense Account', track_visibility='onchange')
    disc_provision_acc = fields.Many2one('account.account', string='Discretionary Grant Provision Account', track_visibility='onchange')
    
    project_budget_acc = fields.Many2one('account.account', string='Project Budget Acc', track_visibility='onchange')
    total_budget = fields.Float(string='Total Budget')
    rem_budget = fields.Float(string='Remaining Budget')
    state = fields.Selection([('new','New'),('close','Close')], string="State")
    ## WSP Configuration Fields
    wsp_start_date = fields.Date(string='WSP Start Date')
    wsp_end_date = fields.Date(string='WSP End Date')
    wsp_extension_date = fields.Date(string='WSP Extension Date')
    wsp_financial_year = fields.Many2one('account.fiscalyear', string='Financial Year')
    ##
    ## Discretionary Reserve Account Configurations
    discretionary_reserve_acc = fields.Many2one('account.account', string='Discretionary Reserve Acc', track_visibility='onchange')
    submission_end_date = fields.Date(string='Submission End Date')
    ##
    ## Fields for Government Levy
    percent_one = fields.Float(string='Percent One')
    percent_two = fields.Float(string='Percent Two')
    percent_three = fields.Float(string='Percent Three')
    ##
    ##Fields for Levy Exempt Periods Limits
    period_one = fields.Float(string='Period One')
    period_two = fields.Float(string='Period Two')
    period_three = fields.Float(string='Period Three')
    period_four = fields.Float(string='Period Four')
    ##  Field for Petty cash limit configuration.
    petty_limit = fields.Float(string='Petty Cash Limit')
    ##
    
    ## Financial manager amount approval limit
    fm_approval_limit = fields.Float(string='FM Approval Limit')
    ##
    grand_acc = fields.One2many('grant.account','grant1', string='Grant')
    scheme_year_id = fields.Many2one('scheme.year','Scheme Year')
    
    # Added contraint
    _sql_constraints = [
     ('unique', 'unique(active)', 'There should be only one active record in Admin Configuration! '), ]
    
    @api.multi
    def onchange_budget_acc(self, project_budget_acc):
        res = {}
        if not project_budget_acc :
            return res
        budget_account_data = self.env['account.account'].browse(project_budget_acc)
        res.update({'value':{'total_budget' : budget_account_data.balance}})
        return res
    
    @api.onchange('wsp_financial_year')
    def onchnage_wsp_financial_year(self):
        self.scheme_year_id = self.wsp_financial_year.scheme_year_id
        
leavy_income_config()


class account_asset_asset(models.Model):
    _inherit = 'account.asset.asset'
    
    product_id = fields.Many2one('product.product', string='Product Id')
    asset_location = fields.Many2one('stock.location', string='Asset Location')
    
account_asset_asset()

class account_asset_depreciation_line(models.Model):
    _inherit = 'account.asset.depreciation.line'
    
    comment = fields.Text(string='comment')
    
account_asset_depreciation_line()

class employer_in_system(models.TransientModel):
    _name = 'employer.in.system'
    
    employer_file = fields.Binary(string='Employer CSV')
    
    @api.multi
    def employer_not_in_system(self):
        employer=self.env['res.partner']
        employer_data = ''
        wb = xlwt.Workbook(encoding = 'utf-8')
        buffer1 = cStringIO.StringIO()
        sheet1 = wb.add_sheet("New Employer Sheet")
        if self.employer_file : 
            employer_data = base64.decodestring(self.employer_file)        
        if employer_data :
            try:
                excel = xlrd.open_workbook(file_contents = employer_data)  
            except:
                raise Warning(_('Incorrect File Format!'))
            sheet_names = excel.sheet_names()
            ## Reading file Sheet by Sheet
            sheet_count = 0
            for sheet_name in sheet_names :
                sheet_count+=1
                xl_sheet = excel.sheet_by_name(sheet_name)
                row_count = 0
                for row_idx in range(0, xl_sheet.nrows):
                    row_count += 1
                sheet_row = []
                count=0  
                rowcount=0                   
                while count < row_count:
                    sheet_row = xl_sheet.row(count) 
                    # Loading Employer Data.
                    sdl_no = sheet_row[0].value
                    employer_sdl_number=employer.search([('employer','=',True),('employer_sdl_no','=',sdl_no)])
                    if employer_sdl_number:
                        pass
                    else:
                        column=0
                        for sheet_content in sheet_row :
                            sheet1.write(rowcount,column,sheet_content.value)
                            column+=1
                        rowcount+=1
                    count+=1
                    
            wb.save(buffer1)
            out = base64.encodestring(buffer1.getvalue())
            attachment_obj = self.env['ir.attachment']
            new_attach = attachment_obj.create({
                'name':'Employer to Import.xlsx',
                'res_name': 'employer_in_system',
                'type': 'binary',
                'res_model': 'wsp.plan',
                'datas':out,
            }) 
        return {
        'type' : 'ir.actions.act_url',
        'url': '/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=%s' % ( new_attach.id, ),
        'target': 'self',
        }
        
employer_in_system()                            
                            
                    
class government_levy(models.Model):
    _name = 'government.levy'
    
    period_id = fields.Many2one('account.period', string='For Period')
    date_creation = fields.Datetime(string='Date')
    
    @api.multi
    def create_invoice_gov_levy(self):
        ### Getting employers which are of type government
        employer_datas = self.env['res.partner'].search([('employer','=',True),('emp_government','=',True)])
        gov_levy_config_data = self.env['leavy.income.config'].search([])
        if isinstance(gov_levy_config_data,list):
            gov_levy_config_data = gov_levy_config_data[0]
        if not (gov_levy_config_data.percent_one and gov_levy_config_data.percent_two and gov_levy_config_data.percent_three):
            raise Warning(_('Please enter all configuration related to Government Levy inside Admin configuration!'))
        for emp_data in employer_datas :
            admin_product_data = self.env['product.product'].search([('name','=','Admin Grant')])
            disc_product_data = self.env['product.product'].search([('name','=','Discretionary Grant')])
            total_payroll = emp_data.total_annual_payroll
            if total_payroll :
                final_amount = (((total_payroll * (gov_levy_config_data.percent_one/100))*(gov_levy_config_data.percent_two/100))*(gov_levy_config_data.percent_three/100))
                admin_amount = final_amount/3
                disc_amount = (final_amount*2)/3
                invoice_line = []
                cust_invoice_line_dict_admin = {   
                                               'product_id' : admin_product_data.id,
                                               'name' : admin_product_data.name+'/'+'Government Levy',
                                               'quantity' : 1,
                                               'price_unit' : admin_amount,
                                               'account_id' : admin_product_data.property_account_income and admin_product_data.property_account_income.id or \
                                               admin_product_data.categ_id and admin_product_data.categ_id.property_account_income_categ and admin_product_data.categ_id.property_account_income_categ.id 
                                            }
                invoice_line.append((0,0,cust_invoice_line_dict_admin))
                cust_invoice_line_dict_disc = {   
                                               'product_id' : disc_product_data.id,
                                               'name' : disc_product_data.name+'/'+'Government Levy',
                                               'quantity' : 1,
                                               'price_unit' : disc_amount,
                                               'account_id' : disc_product_data.property_account_income and disc_product_data.property_account_income.id or \
                                               disc_product_data.categ_id and disc_product_data.categ_id.property_account_income_categ and disc_product_data.categ_id.property_account_income_categ.id
                                            }
                invoice_line.append((0,0,cust_invoice_line_dict_disc))
                cust_invoice_dict = {
                                    'partner_id':emp_data.id,
                                    'name':'Government Levy',
                                    'invoice_line':invoice_line,
                                    'state':'draft',
                                    'type':'out_invoice',
                                    'account_id':emp_data.property_account_receivable and emp_data.property_account_receivable.id
                                    }
                a = self.env['account.invoice'].create(cust_invoice_dict)
        return True
    
government_levy()