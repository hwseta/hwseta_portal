from openerp import models, fields, api, _
from datetime import datetime, timedelta
from openerp.exceptions import Warning
from calendar import monthrange

class object_state(models.Model):
    _name = 'object.state'
    
    state_key = fields.Char(string='State Key')
    name = fields.Char(string='State Value')
    model_id = fields.Many2one('ir.model', string='Model')
    
object_state()

class tranche_fees(models.Model):
    _name = 'tranche.fees'
    
    fees_id = fields.Many2one('fees.structure', string='Fees Name')
    percentage = fields.Float(string='Percentage(%)')
    tranche_payment_id = fields.Many2one('transche.payment', string='Related Tranche')
    ## New field added for define type of tranche and for which type of employee 
    tranche_type = fields.Selection([('percent','Percentage(%)'),('month','Months')],string="Tranche Type")
    employee_type = fields.Selection([('employed','Employed'),('unemployed','Unemployed')], string="18.1/18.2")
    @api.model
    def create(self,vals):
        return super(tranche_fees,self).create(vals)
    
    
tranche_fees()

class hwseta_tranche_document(models.Model):
    _name =  'hwseta.tranche.document'
    
    @api.model
    def default_get(self, fields_list):
        ''' This method will set the documents by default within document library. '''
        res = super(hwseta_tranche_document, self).default_get(fields_list)
        trigger_jv = self._context.get('trigger_jv')
        res.update({'value':{'trigger_jv':trigger_jv}})
        return res    
    
    name = fields.Many2one('project.document',string="Document Name")
    required = fields.Boolean("Document Required")
    tranche_payment_id = fields.Many2one('transche.payment', string='Related Tranche')

hwseta_tranche_document()

class transche_payment(models.Model):
    _name = 'transche.payment'
    _inherit = 'mail.thread'
    
    name = fields.Char(string='Tranche Payment Number', track_visibility='onchange')
    trigger_jv = fields.Many2one('ir.model',string='Trigger JV Action', track_visibility='onchange')
    object_state_id = fields.Many2one('object.state', string='State', track_visibility='onchange')
    project_type = fields.Many2one('hwseta.project.types', string='Project Type', track_visibility='onchange')
    project_id = fields.Many2one('project.project', string='Project', track_visibility='onchange')
    ## Fields for percentage of budget to be assigned.
    tranche_fees_ids = fields.One2many('tranche.fees', 'tranche_payment_id', string='Fees Structure')
    journal_id = fields.Many2one('account.journal', string='Journal', track_visibility='onchange')
    emp_sdlno_cr_account_id = fields.Many2one('account.account', string='Credit Account', track_visibility='onchange')
    disc_grant_dr_account_id = fields.Many2one('account.account', string='Debit Account', track_visibility='onchange')
    disc_expense_acc = fields.Many2one('account.account', string='Project Expense Account', track_visibility='onchange')
    
    ## Field for categorizing Employed (18.1) / Unemployed (18.2)
    employed_unemployed = fields.Selection([('employed','Employed'),('unemployed','Unemployed')], string='18.1/18.2')
    
    ##for show get fees button
    get_fees = fields.Boolean(string="Get Fees",default=False)
    tranche_document_ids = fields.One2many('hwseta.tranche.document', 'tranche_payment_id', string='Tranche Document')
    no_of_tranche = fields.Integer("Tranche Number(18.1)")
    no_of_tranche_18_2 = fields.Integer("Tranche Number(18.2)")

    funding_year = fields.Many2one('account.fiscalyear', string='Funding Year')
    category_type = fields.Selection([('18.1','Employed Learners (18.1)'),('18.2','Unemployed Learners (18.2)')], string="Category Type")
    category = fields.Many2one('hwseta.project.category', string='Project Category')

    @api.multi
    def action_tranche_fees_structure(self):
        '''Get fees structure for employed and unemployed'''
        #commented below line, As per new requirement we are getting fees structure as per Project instead of Project Type. November 2017 
        #project_type_data = self.project_type
        project_type_data = self.project_id
        fees_employed = [fees_data.course_id.id for fees_data in project_type_data.fees_employed]
        fees_unemployed = [fees_data.course_id.id for fees_data in project_type_data.fees_unemployed]
        #nov 2017
        #fees_employed = [fees_data.id for fees_data in project_type_data.fees_employed]
        #fees_unemployed = [fees_data.id for fees_data in project_type_data.fees_unemployed]
        self.write({'tranche_fees_ids' : [(2,fees_data.id) for fees_data in self.tranche_fees_ids]})
        if fees_employed or fees_unemployed:
            self.with_context({'from_get_fees':True}).write({'tranche_fees_ids' : [(0,0,{'fees_id' : fees_id, 'tranche_payment_id':self.id,'employee_type':'employed'}) for fees_id in fees_employed],'get_fees':True})
            self.with_context({'from_get_fees':True}).write({'tranche_fees_ids' : [(0,0,{'fees_id' : fees_id, 'tranche_payment_id':self.id,'employee_type':'unemployed'}) for fees_id in fees_unemployed],'get_fees':True})
        else :
            raise Warning(_('Fees structure not defined for %s')%(project_type_data.name))             
#         if self.employed_unemployed =='employed':
#             if fees_employed:
#                 self.with_context({'from_get_fees':True}).write({'tranche_fees_ids' : [(0,0,{'fees_id' : fees_id, 'tranche_payment_id':self.id,'employee_type':'employed'}) for fees_id in fees_employed],'get_fees':True})
#             else :
#                 raise Warning(_('Fees structure not defined for %s')%(project_type_data.name))             
#         if self.employed_unemployed =='unemployed':                
#             if fees_unemployed:
#                 self.with_context({'from_get_fees':True}).write({'tranche_fees_ids' : [(0,0,{'fees_id' : fees_id, 'tranche_payment_id':self.id,'employee_type':'unemployed'}) for fees_id in fees_unemployed],'get_fees':True})                
#             else :
#                 raise Warning(_('Fees structure not defined for %s')%(project_type_data.name))             
        return True  
    
    @api.multi
    def onchange_funding_year(self, funding_year) :
        res = {}
        if not funding_year :
            res.update({'domain':{'project_type':[('id','in',[])]}})
            return res
        project_types = [project_types.id for project_types in self.env['hwseta.project.types'].search([('seta_funding_year','=',funding_year)])]
        res.update({'domain':{'project_type':[('id','in',project_types)]}})
        print "res----", res
        return res
        
    @api.multi
    def onchange_project_type(self, project_type) :
        res = {}
        if not project_type :
            res.update({'domain':{'project_id':[('id','in',[])]}})
            print "inside---", res
            return res 
        ##Onchange of project type filled projects in tranche
        project=[project.id for project in self.env['project.project'].search([('project_types','=',project_type)])]
        res.update({'domain':{'project_id':[('id','in',project)]},'value':{'get_fees':False}})
        ## Onchange of project type filled document required for tranche
        self.write({'tranche_document_ids' : [(2,tranche_data.id) for tranche_data in self.tranche_document_ids]})
        document_vals = [(0,0,{'name':document.name,'required':document.required}) for document in self.env['hwseta.project.document'].search([('project_type_id','=',project_type)]) ]
        res.update({'value':{ 'tranche_document_ids' : document_vals }})
        return res

    @api.multi
    def onchange_project(self, project_id):
        res = {}
        vals = {}
        if not project_id:
            return res
        ##Onchange of project get no of tranche
        project = self.env['project.project'].search([('id','=',project_id)])
        if project.category_type == '18.1':
            vals.update({'category_type': '18.1'})
        elif project.category_type == '18.2':
            vals.update({'category_type': '18.2'})
        if project.category:
                vals.update({'category': project.category.id})
        if project.category_type == '18.1':
            tranche_count = len([tranche.id for tranche in self.env['transche.payment'].search([('project_id','=',project_id)])])
            print "tranche_count--", tranche_count
            remaining_tranche_no = ((project.no_of_tranche)-(tranche_count))
            print "remaining_tranche_no---", remaining_tranche_no
            tranche_no = ((project.no_of_tranche)-(remaining_tranche_no))+1
            print "tranche_no---", tranche_no
            vals.update({'no_of_tranche': int(tranche_no)})
            res.update({'value': vals})
        if project.category_type == '18.2':
            tranche_count = len([tranche.id for tranche in self.env['transche.payment'].search([('project_id','=',project_id)])])
            print "tranche_count--", tranche_count
            remaining_tranche_no = ((project.no_of_tranche_18_2)-(tranche_count))
            print "remaining_tranche_no---", remaining_tranche_no
            tranche_no = ((project.no_of_tranche_18_2)-(remaining_tranche_no))+1
            print "tranche_no---", tranche_no
            vals.update({'no_of_tranche_18_2': int(tranche_no)})
            res.update({'value': vals})
        print "res----#######", res
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

    @api.multi
    def onchange_trigger(self, trigger):
        if not trigger:
            return {}
        model_data = self.env['ir.model'].search([('id','=',trigger)])
        model_name = str(model_data.model)
        object_state_obj = self.env['object.state']
        all_fields = self.env[model_name].fields_get().keys()
        ## Getting Key Value pair from state field from object.
        if 'state' in all_fields :
            key_val_list = self.env[model_name].fields_get(allfields=['state'])['state']['selection']
            ## Checkin if state for selected objects are already in object state table.
            obj_state_id = object_state_obj.search([('model_id','=',trigger)])
            if not obj_state_id :
                for key_val_tuple in key_val_list:
                    object_state_obj.create({
                                             'state_key':key_val_tuple[0],
                                             'name':key_val_tuple[1],
                                             'model_id':trigger,
                                             })
        return True
    
    
    ##  Added  Sequence for Transche Payment.
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('transche.payment')
        print "Vals---", vals
        if vals.get('category_type') == '18.1':
            if vals.get('no_of_tranche') and vals.get('project_id') : 
                project = self.env['project.project'].search([('id','=',vals.get('project_id')),('seta_funding_year','=',vals.get('funding_year'))])
                if int(vals.get('no_of_tranche')) > int(project.no_of_tranche) :
                    raise Warning(_("You can not create more than %s tranche for %s project!")%(project.no_of_tranche,project.name)) 
        if vals.get('category_type') == '18.2':
            if vals.get('no_of_tranche_18_2') and vals.get('project_id') : 
                project = self.env['project.project'].search([('id','=',vals.get('project_id')),('seta_funding_year','=',vals.get('funding_year'))])
                if int(vals.get('no_of_tranche_18_2')) > int(project.no_of_tranche_18_2) :
                    raise Warning(_("You can not create more than %s tranche for %s project!")%(project.no_of_tranche_18_2,project.name)) 
        return super(transche_payment, self).create(vals)
    
    
    @api.multi
    def get_line(self, name, debit, credit, account_id, partner_id, ref_name,tranche_info):
        result = {
                  'analytic_account_id' : False,
                  'tax_code_id' : False,
                  'analytic_lines' : [],
                  'tax_amount' : False,
                  'name' : name,
                  'ref' : ref_name,
                  'asset_id' : False,
                  'currency_id' : False,
                  'credit' : credit,
                  'product_id' : False,
                  'date_maturity' : False,
                  'debit':debit,
                  'date':datetime.now().date(),
                  'amount_currency' : 0,
                  'product_uom_id' : False,
                  'quantity' : 0,
                  'partner_id':partner_id,
                  'account_id':account_id,
                  'project_id':tranche_info.project_id.id,
                  }
        return result
    
    @api.multi
    def get_move_line(self, credit_account, debit_account,fees_structure, tot_fee, partner_id, ref_name, journal_item_name,tranche_info):
        result = []
        if fees_structure:
            for fees_key ,fees_value in fees_structure.iteritems() :
                fee_line = self.get_line(journal_item_name+'-'+' '+fees_key, fees_value, 0, debit_account, partner_id, ref_name,tranche_info)
                result.append((0,0,fee_line))
        debit_total_line =  self.get_line('/', 0, tot_fee, credit_account, partner_id, ref_name,tranche_info)
        result.append((0,0,debit_total_line))
        return result
        
#     @api.multi
#     def get_move_line(self, credit_account, debit_account, course_fee, allowance_fee, uniform_fee, tot_fee, partner_id, ref_name, journal_item_name):
#         result = []
#         if course_fee :
#             course_fee_line = self.get_line(journal_item_name+'-'+'Course Fee', course_fee, 0, debit_account, partner_id, ref_name)
#             result.append((0,0,course_fee_line))
#         if allowance_fee :
#             allowance_fee_line = self.get_line(journal_item_name+'-'+'Allowance', allowance_fee, 0, debit_account, partner_id, ref_name)
#             result.append((0,0,allowance_fee_line))
#         if uniform_fee :
#             uniform_fee_line = self.get_line(journal_item_name+'-'+'Uniform', uniform_fee, 0, debit_account , partner_id, ref_name)
#             result.append((0,0,uniform_fee_line))
#         debit_total_line =  self.get_line('/', 0, tot_fee, credit_account, partner_id, ref_name)
#         result.append((0,0,debit_total_line))
#         return result
    
#     @api.multi
#     def transche_payment_invoice(self, projects, employer_data, invoice_obj, product_obj, journal_obj, line_name, module_name):
#         ''' Creates Employer Invoice(Supplier Invoice) for Tranche Payment. So that Bank Payment made accessible.'''
#         for enrolled_project in projects: 
#             if module_name == 'assessment':
#                 project_data = enrolled_project
#             else:
#                 project_data = enrolled_project.project_id
#             course_fee = project_data.course_fee
#             allowance = project_data.allowance
#             uniform = project_data.uniform
#             if not (course_fee > 0 and allowance > 0 and uniform > 0):
#                 raise Warning('Assign budget for course fee, allowance and uniform in project %s'%(project_data.name))
#             tot_course_fee = course_fee*(self.course_fee/100)
#             tot_allowance = allowance*(self.allowance/100)
#             tot_uniform = uniform*(self.uniform/100)
#             product_info_dict = {
#                                  'course' : (product_obj.search([('name','=','Course Fee')]),tot_course_fee),
#                                  'allowance' : (product_obj.search([('name','=','Allowance')]),tot_allowance),
#                                  'uniform' : (product_obj.search([('name','=','Uniform')]),tot_uniform)
#                                  }
#             invoice_lines = []
#             journal = journal_obj.search([('type','=','purchase')])
#             if len(journal)>1:
#                 journal = journal[0]
#             for product_key, product_val in product_info_dict.iteritems():
#                 invoice_line_dict = {
#                                         'product_id' : product_val[0].id,
#                                         'name' : product_val[0].name+line_name,
#                                         'quantity':1,
#                                         'price_unit':product_val[1],
#                                      }
#                 invoice_lines.append((0,0,invoice_line_dict))
#             invoice_dict = {
#                             'partner_id':employer_data.id,
#                             'invoice_line':invoice_lines,
#                             'employer':True,
#                             'state':'draft',
#                             'account_id':employer_data.property_account_payable.id,
#                             'type':'in_invoice',
#                             'journal_id':journal.id,
#                             }
#             invoice_data = invoice_obj.create(invoice_dict)
#             ## Validating Customer Invoice.
#             invoice_data.signal_workflow('invoice_open')
#             project_data.write({'course_fee':(course_fee-tot_course_fee),'allowance':(allowance-tot_allowance),'uniform':(uniform-tot_uniform)})
#         return True
    
    @api.multi
    def transche_payment_invoice(self, projects_dict, employer_data, invoice_obj, product_obj, journal_obj, line_name, module_name):
        ''' Creates Employer Invoice(Supplier Invoice) for Tranche Payment. So that Bank Payment made accessible.'''
        i = 0
        product_info_list = []
        while(i < len(projects_dict)) :
            project_names = projects_dict.keys()
            prod_fees_info = projects_dict.values()
            prod_dict = {}
            for prod_info in prod_fees_info[i]:
                prod_dict = prod_info
                prod_dict.update({'project_name':project_names[i]})
                product_info_list.append(prod_dict)
            i += 1
        journal = journal_obj.search([('type','=','purchase')])
        if len(journal)>1:
            journal = journal[0]
        invoice_lines = []
        for product_info_dict in product_info_list :
            price = 0
            key_name = ''
            for info_key in product_info_dict.keys() :
                if info_key not in ['product_id','project_name']:
                    price = product_info_dict[info_key]
                    key_name = info_key
            invoice_line_dict = {
                                 'product_id' : product_info_dict.get('product_id',False),
                                 'name' : line_name+' for '+key_name+' for project '+product_info_dict.get('project_name',''),
                                 'quantity' : 1,
                                 'price_unit' : price
                                 }
            invoice_lines.append((0,0,invoice_line_dict))
        invoice_dict = {
                        'partner_id':employer_data.id,
                        'invoice_line':invoice_lines,
                        'employer':True,
                        'state':'draft',
                        'account_id':employer_data.property_account_payable.id,
                        'type':'in_invoice',
                        'journal_id':journal.id,
                        }
        invoice_data = invoice_obj.create(invoice_dict)
        ## Validating Customer Invoice.
        invoice_data.signal_workflow('invoice_open')
        return True

    @api.multi
    def transche_payment_jv(self, project, employer_data, name, tranche_info, emp_status):
        ''' Creates Journal Entries for Tranche Payment'''
#         for enrolled_project in projects :
#             project_data = enrolled_project.project_id
#             course_fee = project_data.course_fee
#             allowance = project_data.allowance
#             uniform = project_data.uniform
#             if not (course_fee > 0 and allowance > 0 and uniform > 0):
#                 raise Warning('Assign budget for course fee, allowance and uniform in project %s'%(project_data.name))
#             tot_course_fee = course_fee*(self.course_fee/100)
#             tot_allowance = allowance*(self.allowance/100)
#             tot_uniform = uniform*(self.uniform/100)
#             tot_fee = tot_course_fee+tot_allowance+tot_uniform
        print "Inside transche_payment_jv====", project,employer_data,name,tranche_info,emp_status
        final_dict = tranche_info.calculate_tranche(project, employer_data, emp_status)
        print "final_dict inside----transche_payment_jv---", final_dict
        if final_dict.get('employed'):
            tot_fee = reduce(lambda x,y: float(x)+float(y),final_dict.get('employed').values())
            ## Debit and credit account
            admin_config_data = self.env['leavy.income.config'].search([])
            if isinstance(admin_config_data, list):
                admin_config_data = admin_config_data[0]
            dbt_acc = tranche_info.disc_expense_acc and tranche_info.disc_expense_acc.id
            cr_acc = admin_config_data.disc_provision_acc and admin_config_data.disc_provision_acc.id
#             line_val = self.get_move_line(cr_acc, dbt_acc, final_dict.get('employed').get('Course Fees'), final_dict.get('employed').get('Allowance'), final_dict.get('employed').get('Uniform Fees'), tot_fee, employer_data.id, self.name, name+'for Employed')
            line_val = self.get_move_line(cr_acc, dbt_acc, final_dict.get('employed'), tot_fee, employer_data.id, self.name, name+'for Employed',tranche_info)
            ## Taking purchase type journal.
            journal = self.env['account.journal'].search([('type','=','purchase')])
            if len(journal)>1:
                journal = journal[0]
            move_val = {
                        'ref':name+' for Employed',
                        'line_id':line_val,
                        'journal_id':journal.id,
                        'date':datetime.now().date(),
                        'narration':name+' for Employed',
                        'company_id':employer_data.company_id.id,
                        }
            self.env['account.move'].create(move_val)
        if final_dict.get('unemployed'):
            tot_fee = reduce(lambda x,y: float(x)+float(y),final_dict.get('unemployed').values())
            ## Debit and credit account
            admin_config_data = self.env['leavy.income.config'].search([])
            if isinstance(admin_config_data, list):
                admin_config_data = admin_config_data[0]
            dbt_acc = tranche_info.disc_expense_acc and tranche_info.disc_expense_acc.id
            cr_acc = admin_config_data.disc_provision_acc and admin_config_data.disc_provision_acc.id
            #line_val = self.get_move_line(cr_acc, dbt_acc, final_dict.get('unemployed').get('Course Fees'), final_dict.get('unemployed').get('Allowance'), final_dict.get('unemployed').get('Uniform Fees'), tot_fee, employer_data.id, self.name, name+'for Unemployed')
            line_val = self.get_move_line(cr_acc, dbt_acc, final_dict.get('unemployed'), tot_fee, employer_data.id, self.name, name+'for Unemployed',tranche_info)            
            ## Taking purchase type journal.
            journal = self.env['account.journal'].search([('type','=','purchase')])
            if len(journal)>1:
                journal = journal[0]
            move_val = {
                        'ref':name+' for Unemployed',
                        'line_id':line_val,
                        'journal_id':journal.id,
                        'date':datetime.now().date(),
                        'narration':name +' for Unemployed',
                        'company_id':employer_data.company_id.id,
                        }
            self.env['account.move'].create(move_val)            
        ## Updating Values from project(deducting the amount whose journal entry is fired)
#         project_data.write({'course_fee':(course_fee-tot_course_fee),'allowance':(allowance-tot_allowance),'uniform':(uniform-tot_uniform)})
        return True
    
    @api.multi
    def date_difference_month(self,start_date, end_date):
        delta = 0
        while True:
            mdays = monthrange(start_date.year, start_date.month)[1]
            start_date += timedelta(days=mdays)
            if start_date <= end_date:
                delta += 1
            else:
                break
        return delta    
        
    @api.multi
#     def calculate_tranche(self, tranche_data, project_datas, employer_data):
    def calculate_tranche(self, project_datas, employer_data, emp_status):
        print "Inside calculate tranche==========="
#         invoice_dict = {}
#         for project_data in project_datas :
#         project_info = project_data.project_id
        project_info = project_datas.project_id
        ## project duration in month
        project_start_date = datetime.strptime(project_info.start_date, '%Y-%m-%d  %H:%M:%S').date()
        project_end_date = datetime.strptime(project_info.end_date, '%Y-%m-%d  %H:%M:%S').date()
        project_duration = self.date_difference_month(project_start_date, project_end_date)
        ## Considering one employer can enroll for one project one time.
        emp_req_data = self.env['employer.requests'].search([('employer_id','=',employer_data.id),('project_id','=',project_info.id)], limit=1)
#         employed_learner = 0
#         unemployed_learner = 0
#         if emp_req_data.eoi_id.learner_ids :
#             employed_learner = [learner.id for learner in emp_req_data.eoi_id.learner_ids if learner.state in ['active']]
#             unemployed_learner = [learner.id for learner in emp_req_data.eoi_id.learner_ids if learner.state in ['active']]
#         if not emp_req_data.eoi_id.learner_ids :
        employed_learner = emp_req_data.app_employed
        unemployed_learner = emp_req_data.app_unemployed
        ## Collecting amount fee wise in tranche.
        emp_val = 0
        final_dict = {}
        dict_employed_cost = {}
        dict_unemployed_cost = {}
        print "project_info----", project_info
        if not project_info.fees_employed and project_info.category_type == '18.1':
            raise Warning(_('Please enter fees for employed for project %s')%(project_info.name))
        if not project_info.fees_unemployed and project_info.category_type == '18.2':
            raise Warning(_('Please enter fees for unemployed for project %s')%(project_info.name))
        dict_emp_fees = {};dict_unemp_fees = {}
        # if emp_status == 'employed':
        if project_info.category_type == '18.1':
            for fees_info in project_info.fees_employed :
                if fees_info.course_amount <= 0:
                    raise Warning(_('Please enter course amount for %s for Fees 18.1 for project %s')%(fees_info.course_id.name,project_info.name))
                if employed_learner <= 0:
                    raise Warning(_('Please Compute Employers Learners Approval and Update To EOI inside project before generating tranche!' ))
                emp_val = fees_info.course_amount * employed_learner
                dict_emp_fees.update({fees_info.course_id.name:emp_val}) 
            for fees_key in dict_emp_fees.keys():
                for tranche_fees_data in self.tranche_fees_ids :
                    if fees_key == tranche_fees_data.fees_id.name and  tranche_fees_data.employee_type == 'employed':
                        if tranche_fees_data.tranche_type == 'percent':
                            final_amount = float(tranche_fees_data.percentage)/100 * dict_emp_fees[fees_key]
                        if tranche_fees_data.tranche_type == 'month':
                            final_amount = dict_emp_fees[fees_key]/int(project_duration) * int(tranche_fees_data.percentage)
                        dict_employed_cost.update({fees_key : final_amount})
            # if emp_status == 'unemployed' :
        if project_info.category_type == '18.2':
            for fees_info in project_info.fees_unemployed :
                print "inside---1",fees_info
                if fees_info.course_amount <= 0:
                    raise Warning(_('Please enter course amount for %s for Fees 18.2 for project %s')%(fees_info.course_id.name,project_info.name))
                print "fees_info.course_amount---", fees_info.course_amount
                print "unemployed_learner----", unemployed_learner
                if unemployed_learner <= 0:
                    raise Warning(_('Please Compute Employers Learners Approval and Update To EOI inside project before generating tranche!' ))
                emp_val = fees_info.course_amount * unemployed_learner
                print "emp_val---", emp_val
                dict_unemp_fees.update({fees_info.course_id.name:emp_val})
                print "dict_unemp_fees---", dict_unemp_fees
            for fees_key in dict_unemp_fees.keys():
                print "inside---2"
                for tranche_fees_data in self.tranche_fees_ids :
                    if fees_key == tranche_fees_data.fees_id.name and  tranche_fees_data.employee_type == 'unemployed':
                        if tranche_fees_data.tranche_type == 'percent':
                            final_amount = float(tranche_fees_data.percentage)/100 * dict_unemp_fees[fees_key]
                        if tranche_fees_data.tranche_type == 'month':
                            final_amount = dict_unemp_fees[fees_key]/int(project_duration) * int(tranche_fees_data.percentage)                        
                        dict_unemployed_cost.update({fees_key : final_amount})
        final_dict.update({'employed':dict_employed_cost,'unemployed':dict_unemployed_cost})
        ## Following dictionary will merge employed fees and unemployed fees
#         dict_merge = dict_emp_fees.copy()
#         for unemp_key in dict_unemp_fees.keys():
#             found = 0
#             for emp_key in dict_emp_fees.keys():
#                 if  unemp_key == emp_key :
#                     found = 1
#                     dict_merge.update({emp_key : dict_emp_fees[emp_key] + dict_unemp_fees[unemp_key]})
#             if found == 0 :
#                 dict_merge.update({unemp_key : dict_unemp_fees[unemp_key]})
#         print "dict_merge =============",dict_merge
        # Following dictionary will have the updated value for fees , calculated using percentage in tranche.
        ## Previous code for creating final dict
#         for fees_key in dict_merge.keys():
#             for tranche_fees_data in self.tranche_fees_ids :
#                 if fees_key == tranche_fees_data.fees_id.name :
#                     final_amount = float(tranche_fees_data.percentage)/100 * dict_merge[fees_key]
#                     final_dict.update({fees_key : final_amount}) 
#         print "final dict =============",final_dict
        ## Computing final dictionary for Invoice.
#         fees_list = []
#         for final_key in final_dict.keys() :
#             fees_dict = {}
#             fees_data = self.env['fees.structure'].search([('name','=',final_key)])
#             fees_dict.update({
#                               final_key : final_dict[final_key],
#                               'product_id' : fees_data.related_product and fees_data.related_product.id,
#                               })
#             fees_list.append(fees_dict)    
#         print "fees_list ==========",fees_list
#         invoice_dict[project_info.name] = fees_list
#         print "invoice_dict =======",invoice_dict
#         return invoice_dict
        print "final----dict===========", final_dict
        return final_dict
    
transche_payment()

## Inheriting Class for Generating 1st Transche Payment.
class learning_programme(models.Model):
    _inherit = 'learning.programme'
    
    transche_paid = fields.Boolean(string='Transche Paid')
    
    @api.multi
    def write(self, vals):
        ''' Tranche payment project based'''
        result = super(learning_programme, self).write(vals)
#         employer_data = self.employer_id
# #         final_dict = {}
# #         ## Getting Project Wise Tranche.
#         for project_data in self.enroll_project_ids :
#             project_info = project_data.project_id
#             model_data = self.env['ir.model'].search([('model','=','learning.programme')])
#             ## Previously single tranche payment generated for both emp and unemp.
# #             transche_payment_data = self.env['transche.payment'].search([('project_id','=',project_info.id),('trigger_jv','=',model_data.id)])
#             ## Now tranche payment generated for emp and unemp seperately.
#             transche_payment_data_emp = self.env['transche.payment'].search([('project_id','=',project_info.id),('trigger_jv','=',model_data.id),('employed_unemployed','=','employed')])
#             transche_payment_data_unemp = self.env['transche.payment'].search([('project_id','=',project_info.id),('trigger_jv','=',model_data.id),('employed_unemployed','=','unemployed')])
#             if not transche_payment_data_emp :
#                 raise Warning(_('No Tranche Payment Configuration defined for project %s for EOI for Employed!')%(project_info.name))
#             if not transche_payment_data_unemp :
#                 raise Warning(_('No Tranche Payment Configuration defined for project %s for EOI for Unemployed!')%(project_info.name))
#             tranche_data_emp = False;tranche_data_unemp = False
# #             if transche_payment_data.trigger_jv and (vals.get('state',False) == transche_payment_data.object_state_id.state_key):
# #                 tranche_data = transche_payment_data
#             if transche_payment_data_emp.trigger_jv and (vals.get('state',False) == transche_payment_data_emp.object_state_id.state_key):
#                 
#                 tranche_data_emp = transche_payment_data_emp
#             if transche_payment_data_unemp.trigger_jv and (vals.get('state',False) == transche_payment_data_unemp.object_state_id.state_key):
#                 tranche_data_unemp = transche_payment_data_unemp
#             if tranche_data_emp :
#                 self.env['transche.payment'].transche_payment_jv(project_data, employer_data, '- Tranche Payment for EOI '+self.name+' for Employed', transche_payment_data_emp, 'employed')
#             if tranche_data_unemp :
#                 self.env['transche.payment'].transche_payment_jv(project_data, employer_data, '- Tranche Payment for EOI '+self.name+' for Unemployed', transche_payment_data_unemp, 'unemployed')
                
                ##already commented
#                 invoice_dict = transche_payment_data.calculate_tranche(project_data, employer_data)
#                 final_dict.update({invoice_dict.keys()[0] : invoice_dict[invoice_dict.keys()[0]]})
#         if final_dict :
#             self.env['transche.payment'].transche_payment_invoice(final_dict, employer_data, self.env['account.invoice'], self.env['product.product'], self.env['account.journal'], '- Tranche Payment for EOI '+self.name, 'learning')
        return result
    
learning_programme()

## Inheriting Class for Generating 2nd Transche Payment.
class monitor_and_evaluate(models.Model):
    _inherit = 'monitor.and.evaluate'
    _description = 'Monitoring and Evaluation'
    
    monitored = fields.Boolean(string='Monitored')

    @api.multi
    def write(self, vals):
        result = super(monitor_and_evaluate, self).write(vals)
#         employer_data = self.employer_id
#         final_dict = {}
#         ## Getting Project Wise Tranche.
#         for project_data in self.project_info_ids :
#             project_info = project_data.project_id
#             model_data = self.env['ir.model'].search([('model','=','monitor.and.evaluate')])
#             transche_payment_data = self.env['transche.payment'].search([('project_id','=',project_info.id),('trigger_jv','=',model_data.id)])
#             if not transche_payment_data :
#                 raise Warning(_('No Tranche Payment Configuration defined for project %s for Monitoring and Evaluation!')%(project_info.name))
#             tranche_data = False
#             if transche_payment_data.trigger_jv and (vals.get('state',False) == transche_payment_data.object_state_id.state_key):
#                 tranche_data = transche_payment_data
#             if tranche_data :
#                 self.env['transche.payment'].transche_payment_jv(project_data, employer_data, '- Tranche Payment for Monitoring and Evaluation '+self.name, transche_payment_data)
        return result
    
monitor_and_evaluate()

