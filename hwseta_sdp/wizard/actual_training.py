from openerp import fields, models, api


# class specialize_subject(models.Model):
#     _inherit = 'specialize.subject'
#     
#     actual_training_d1_id = fields.Many2one('actual.training.d1.fields', string='Actual Training')
# specialize_subject()

_get_genders = [
               ('am','African Male'),
               ('af','African Female'),
               ('ad','African Dissable'),
               ('cm','Coloured Male'),
               ('cf','Coloured Female'),
               ('cd','Coloured Dissable'),
               ('im','Indian Male'),
               ('if','Indian Female'),
               ('id','Indian Dissable'),
               ('wm','White Male'),
               ('wf','White Female'),
               ('wd','White Dissable'),
               ]

## Defining Global Function for getting specialization.##
def get_occupation_and_specialization(ofo_code_data):
    data = []
    occupation = ofo_code_data.occupation or False
    data.append(occupation)
    special_sub = ''
    specializations = ofo_code_data.specialize_ids
    if specializations:
        len_sub = len(specializations)
        count = 0
        while len_sub > 0:
            if count == 0:
                special_sub = specializations[len_sub-1].name
            else :
                special_sub = special_sub+','+specializations[len_sub-1].name
            len_sub -= 1
            count += 1
    if special_sub:
        data.append(special_sub)
    else:
        data.append(False)
    return data
############# Actual Related Wizards #####################

## Wizard for Actual Training.
class actual_training_d1(models.Model):
    _name = 'actual.training.d1'
    
    actual_training_fields_ids = fields.One2many('actual.training.d1.fields', 'actual_training_id', string='Actual Training D1')  
    related_wsp = fields.Many2one('wsp.plan',string="Related WSP")
    
    @api.v7
    def save_btn(self,cr,uid,ids,context=None):
        if context.get('active_id',False):
            self.write(cr, uid, ids[0], {'related_wsp':context['active_id']})
            self.pool.get('wsp.plan').write(cr, uid, context['active_id'], {'actual_training_id': ids[0]})
            return {
                'name': 'WSP',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'wsp.plan',
                'res_id': context['active_id'],
            }
actual_training_d1()

class actual_training_d1_fields(models.Model):
    _name = 'actual.training.d1.fields'
    ##
    name = fields.Char(string='First Name')
    surname = fields.Char(string='Surname')
#     code = fields.Char(string='OFO Code')
    code = fields.Many2one('ofo.code',string='OFO')
    major = fields.Char(string='Major')
    sub_major_group = fields.Char(string='Sub Major Group')
    occupation = fields.Char(string='Occupation')
#     specialization = fields.Char(string='Specialization')
    specialization = fields.Many2one('specialize.subject', string='Specialisation')
    # One2many field having view problem after onchange so keeping simple char field.
    municipality = fields.Char(string='Municipality')
    urban = fields.Char(string='Urban')
    type_training = fields.Char(string='Type of Training Intervention')
    name_training = fields.Char(string='Name of Training Intervention')
    training_cost = fields.Float(string='Training Cost Per Learning')
    non_aligned = fields.Boolean(string='Non Aligned')
    nqf_level = fields.Char(string='NQF Level')
    gender = fields.Selection(_get_genders, string='Gender')
    age_group = fields.Selection([('less_than_thirty_five','<35'),
                                  ('thirty_five_to_fifty_five','35-55'),
                                  ('greater_than_fifty_five','>55')], string='Age Group')
    total_cost = fields.Float(string='Total Cost')
    actual_training_id = fields.Many2one('actual.training.d1', string='Actual Training Fields')
    
    
    @api.multi
    def onchange_code(self, ofo_code):
        res = {}
        ofo_code_data = self.env['ofo.code'].browse(ofo_code)
        values = get_occupation_and_specialization(ofo_code_data)
        values = {
              'occupation' : values and values[0] != False and values[0] or ' ',
              'specialization' : values and values[1] != False and values[1] or ' ',
              }
        res['value'] = values
        return res
    ##
actual_training_d1_fields()

## Wizard for Actual Adult Education.
class actual_adult_education(models.Model):  
    _name = 'actual.adult.education'
     
    actual_adult_education_fields_ids = fields.One2many('actual.adult.education.fields', 'actual_adult_education_id', string='Actual Adult Education')
    related_wsp = fields.Many2one('wsp.plan',string="Related WSP")
     
    @api.v7
    def save_btn(self,cr,uid,ids,context=None):
        if context.get('active_id',False):
            self.write(cr, uid, ids[0], {'related_wsp':context['active_id']})
            self.pool.get('wsp.plan').write(cr, uid, context['active_id'], {'actual_adult_education_id': ids[0]})
            return {
                'name': 'WSP',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'wsp.plan',
                'res_id': context['active_id'],
            }
     
actual_adult_education()

class actual_adult_education_fields(models.Model):
    _name = 'actual.adult.education.fields'
     
    name = fields.Char(string='First Name')
    surname = fields.Char(string='Surname')
    id_number = fields.Char(string='Id Number')
    population_group = fields.Selection([('african','African'),('coloured','Coloured'),('indian','Indian'),('white','White')], string='Population Group')
#     gender = fields.Selection([('male','Male'),('female','Female')], string='Gender')
    gender = fields.Selection(_get_genders, string='Gender')
    dissability_status_and_type = fields.Selection([('unknown_dissability_status','Unknown Dissability Status')],string='Dissability Status Type')
    learner_province = fields.Many2one('res.country.state', string='Learner Province')
    municipality = fields.Char(string='Municipality')
    urban = fields.Char(string='Urban')
    aet_start_date = fields.Date(string='AET Start Date')
    aet_end_date = fields.Date(string='AET End Date')
    provider = fields.Char(string='Provider')
    aet_level = fields.Selection([('aet_level_1','AET Level 1')],string='AET Level')
    aet_subject = fields.Selection([('numeracy','Numeracy')],string='AET Subject')
    free_text = fields.Char(string='Free Text')
    actual_adult_education_id = fields.Many2one('actual.adult.education',string='Actual Adult Education Id')
     
actual_adult_education_fields()

## Wizard for Actual Pivotal Training.
class actual_pivotal_training(models.Model):  
    _name = 'actual.pivotal.training'
     
    actual_pivotal_training_fields_ids = fields.One2many('actual.pivotal.training.fields', 'actual_pivotal_training_id', string='Actual Pivotal Training')
    related_wsp = fields.Many2one('wsp.plan',string="Related WSP")
     
    @api.v7
    def save_btn(self,cr,uid,ids,context=None):
        if context.get('active_id',False):
            self.write(cr, uid, ids[0], {'related_wsp':context['active_id']})
            self.pool.get('wsp.plan').write(cr, uid, context['active_id'], {'actual_pivotal_training_id': ids[0]})
            return {
                'name': 'WSP',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'wsp.plan',
                'res_id': context['active_id'],
            }
actual_pivotal_training()
 
class actual_pivotal_training_fields(models.Model):  
    _name = 'actual.pivotal.training.fields'
     
    name = fields.Char(string='First Name')
    surname = fields.Char(string='Surname')
#     ofo_code = fields.Char(string='OFO Code')
    ofo_code = fields.Many2one('ofo.code',string='OFO')
    major = fields.Char(string='Major')
    sub_major_group = fields.Char(string='Sub Major')
    occupation = fields.Char(string='Occupation')
#     specialization = fields.Char(string='Specialization')
    specialization = fields.Many2one('specialize.subject', string='Specialisation')
    socio_economic_status = fields.Selection([('employed','Employed'),('unemployed','Unemployed')], string='Socio Economic Status')
    pivotal_programme_institution = fields.Char(string='Pivotal Programme Institution')
    pivotal_programme_qualification = fields.Char(string='Pivotal Programme Qualification')
    pivotal_programme_type = fields.Selection([('academic','Academic')],string='Pivotal Programme Type')
    cost = fields.Float(string='Cost')
    municipality = fields.Char(string='Municipality')
    urban = fields.Char(string='Urban')
    province = fields.Many2one('res.country.state', string='Province')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    gender = fields.Selection(_get_genders, string='Gender')
#     african = fields.Selection([('am','AM'),('af','AF'),('ad','AD')], string='African')
#     coloured = fields.Selection([('cm','CM'),('cf','CF'),('cd','CD')], string='Coloured')
#     indian = fields.Selection([('im','IM'),('if','IF'),('id','ID')], string='Indian')
#     white = fields.Selection([('wm','WM'),('wf','WF'),('wd','WD')], string='White')
    total_person = fields.Integer(string='Total Person')
#     total_male = fields.Integer(string='Total Male')
#     total_female = fields.Integer(string='Total Female')
#     total_disabbled = fields.Integer(string='Total Dissabled')
    age_group = fields.Selection([('less_than_thirty_five','<35'),
                                  ('thirty_five_to_fifty_five','35-55'),
                                  ('greater_than_fifty_five','>55')], string='Age Group')    
    total_cost = fields.Float(string='Total Cost')
    actual_pivotal_training_id = fields.Many2one('actual.pivotal.training', string='Actual Pivotal Training')
    
    @api.multi
    def onchange_code(self, ofo_code):
        res = {}
        ofo_code_data = self.env['ofo.code'].browse(ofo_code)
        values = get_occupation_and_specialization(ofo_code_data)
        values = {
              'occupation' : values and values[0] != False and values[0] or ' ',
              'specialization' : values and values[1] != False and values[1] or ' ',
              }
        res['value'] = values
        return res
    
actual_pivotal_training_fields()

############# Planned Related Wizards ##############
class total_employment_profile(models.Model):
    _name = 'total.employment.profile'
    
    total_employment_profile_fields_ids = fields.One2many('total.employment.profile.fields', 'total_employment_profile_id', string='Total Employment Profile')
    related_wsp = fields.Many2one('wsp.plan',string="Related WSP")
    
    @api.v7
    def save_btn(self,cr,uid,ids,context=None):
        if context.get('active_id',False):
            self.write(cr, uid, ids[0], {'related_wsp':context['active_id']})
            self.pool.get('wsp.plan').write(cr, uid, context['active_id'], {'total_employment_profile_id': ids[0]})
            return {
                'name': 'WSP',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'wsp.plan',
                'res_id': context['active_id'],
            }
total_employment_profile()

class total_employment_profile_fields(models.Model):
    _name = 'total.employment.profile.fields'
    
    name = fields.Char(string='First Name')
    surname = fields.Char(string='Surname')
#     ofo_code = fields.Char(string='OFO Code')
    ofo_code = fields.Many2one('ofo.code',string='OFO')
    occupation = fields.Char(string='Occupation')
#     specialization = fields.Char(string='Specialization')
    specialization = fields.Many2one('specialize.subject', string='Specialisation')
    municipality = fields.Char(string='Municipality')
    province = fields.Many2one('res.country.state', string='Province')
    urban = fields.Selection([('urban','Urban'),('rural','Rural')],string='Urban/Rural')
    highest_education_level = fields.Char(string='Highest Education Level')
    scarce_skill = fields.Char(string='Scarce Skill')
    gender = fields.Selection(_get_genders, string='Gender')
#     african = fields.Selection([('am','AM'),('af','AF'),('ad','AD')], string='African')
#     coloured = fields.Selection([('cm','CM'),('cf','CF'),('cd','CD')], string='Coloured')
#     indian = fields.Selection([('im','IM'),('if','IF'),('id','ID')], string='Indian')
#     white = fields.Selection([('wm','WM'),('wf','WF'),('wd','WD')], string='White')
    age_group = fields.Selection([('less_than_thirty_five','<35'),
                                  ('thirty_five_to_fifty_five','35-55'),
                                  ('greater_than_fifty_five','>55')], string='Age Group')
    total_employment_profile_id = fields.Many2one('total.employment.profile', string='Total Employment Profile')
    
    @api.multi
    def onchange_code(self, ofo_code):
        res = {}
        ofo_code_data = self.env['ofo.code'].browse(ofo_code)
        values = get_occupation_and_specialization(ofo_code_data)
        values = {
              'occupation' : values and values[0] != False and values[0] or ' ',
              'specialization' : values and values[1] != False and values[1] or ' ',
              }
        res['value'] = values
        return res
    
total_employment_profile_fields()

class planned_training_non_pivotal(models.Model):
    _name = 'planned.training.non.pivotal'
    
    planned_training_non_pivotal_fields_ids = fields.One2many('planned.training.non.pivotal.fields','planned_training_non_pivotal_id', string='Planned Training Non Pivotal')
    related_wsp = fields.Many2one('wsp.plan',string="Related WSP")
    
    @api.v7
    def save_btn(self,cr,uid,ids,context=None):
        if context.get('active_id',False):
            self.write(cr, uid, ids[0], {'related_wsp':context['active_id']})
            self.pool.get('wsp.plan').write(cr, uid, context['active_id'], {'planned_training_non_pivotal_id': ids[0]})
            return {
                'name': 'WSP',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'wsp.plan',
                'res_id': context['active_id'],
            }
    
planned_training_non_pivotal()

class planned_training_non_pivotal_fields(models.Model):
    _name = 'planned.training.non.pivotal.fields'
    
    name = fields.Char(string='First Name')
    surname = fields.Char(string='Surname')
    type_of_training = fields.Selection([('non_pivotal','Non Pivotal')], string='Type Of Training')
#     ofo_code = fields.Char(string='OFO Code')
    ofo_code = fields.Many2one('ofo.code',string='OFO')
    occupation = fields.Char(string='Occupation')
#     specialization = fields.Char(string='Specialization')
    specialization = fields.Many2one('specialize.subject', string='Specialisation')
    municipality = fields.Char(string='Municipality')
    province = fields.Many2one('res.country.state', string='Province')
    urban = fields.Selection([('urban','Urban'),('rural','Rural')],string='Urban/Rural')
    socio_economic_status = fields.Selection([('employed','Employed'),('unemployed','Unemployed')], string='Socio Economic Status')
    type_of_training_inter = fields.Char(string='Type of Training Intervention')
    name_of_training_inter = fields.Char(string='Name of Training Intervention')
    training_cost_per_learner = fields.Float(string='Training Cost Per Learner')
    nqf_aligned = fields.Boolean(string='NQF Aligned')
    nqf_level = fields.Char(string='NQF Level')
    gender = fields.Selection(_get_genders, string='Gender')
#     african = fields.Selection([('am','AM'),('af','AF'),('ad','AD')], string='African')
#     coloured = fields.Selection([('cm','CM'),('cf','CF'),('cd','CD')], string='Coloured')
#     indian = fields.Selection([('im','IM'),('if','IF'),('id','ID')], string='Indian')
#     white = fields.Selection([('wm','WM'),('wf','WF'),('wd','WD')], string='White')
    age_group = fields.Selection([('less_than_thirty_five','<35'),
                                  ('thirty_five_to_fifty_five','35-55'),
                                  ('greater_than_fifty_five','>55')], string='Age Group')
    total_cost = fields.Float(string='Total Cost')
    planned_training_non_pivotal_id = fields.Many2one('planned.training.non.pivotal', string='Planned Training Non Pivotal')
    
    @api.multi
    def onchange_code(self, ofo_code):
        res = {}
        ofo_code_data = self.env['ofo.code'].browse(ofo_code)
        values = get_occupation_and_specialization(ofo_code_data)
        values = {
              'occupation' : values and values[0] != False and values[0] or ' ',
              'specialization' : values and values[1] != False and values[1] or ' ',
              }
        res['value'] = values
        return res
    
planned_training_non_pivotal_fields()

class planned_training_pivotal(models.Model):
    _name = 'planned.training.pivotal'
    
    planned_training_pivotal_fields_ids = fields.One2many('planned.training.pivotal.fields','planned_training_pivotal_id', string='Planned Training Pivotal')
    related_wsp = fields.Many2one('wsp.plan',string="Related WSP")
    
    @api.v7
    def save_btn(self,cr,uid,ids,context=None):
        if context.get('active_id',False):
            self.write(cr, uid, ids[0], {'related_wsp':context['active_id']})
            self.pool.get('wsp.plan').write(cr, uid, context['active_id'], {'planned_training_pivotal_id': ids[0]})
            return {
                'name': 'WSP',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'wsp.plan',
                'res_id': context['active_id'],
            }
    
planned_training_non_pivotal()

class planned_training_pivotal_fields(models.Model):
    _name = 'planned.training.pivotal.fields'
    
    name = fields.Char(string='First Name')
    surname = fields.Char(string='Surname')
    type_of_training = fields.Selection([('non_pivotal','Non Pivotal')], string='Type Of Training')
#     ofo_code = fields.Char(string='OFO Code')
    ofo_code = fields.Many2one('ofo.code',string='OFO')
    occupation = fields.Char(string='Occupation')
#     specialization = fields.Char(string='Specialization')
    specialization = fields.Many2one('specialize.subject', string='Specialisation')
    socio_economic_status = fields.Selection([('employed','Employed'),('unemployed','Unemployed')], string='Socio Economic Status')
    pivotal_programme_institute = fields.Char(string='Pivotal Programme Institute')
    pivotal_programme_qualification = fields.Char(string='Pivotal Programme Qualification')
    pivotal_programme_type = fields.Char(string='Pivotal Programme Type')
    cost_per_learner = fields.Float(string='Cost Per Learner')
    municipality = fields.Char(string='Municipality')
    urban = fields.Selection([('urban','Urban'),('rural','Rural')],string='Urban/Rural')
    province = fields.Many2one('res.country.state', string='Province')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    nqf_aligned = fields.Boolean(string='NQF Aligned')
    nqf_level = fields.Char(string='NQF Level')
    gender = fields.Selection(_get_genders, string='Gender')
#     african = fields.Selection([('am','AM'),('af','AF'),('ad','AD')], string='African')
#     coloured = fields.Selection([('cm','CM'),('cf','CF'),('cd','CD')], string='Coloured')
#     indian = fields.Selection([('im','IM'),('if','IF'),('id','ID')], string='Indian')
#     white = fields.Selection([('wm','WM'),('wf','WF'),('wd','WD')], string='White')
    age_group = fields.Selection([('less_than_thirty_five','<35'),
                                  ('thirty_five_to_fifty_five','35-55'),
                                  ('greater_than_fifty_five','>55')], string='Age Group')
    total_cost = fields.Float(string='Total Cost')
    planned_training_pivotal_id = fields.Many2one('planned.training.pivotal', string='Planned Training Pivotal')
    
    @api.multi
    def onchange_code(self, ofo_code):
        res = {}
        ofo_code_data = self.env['ofo.code'].browse(ofo_code)
        values = get_occupation_and_specialization(ofo_code_data)
        values = {
              'occupation' : values and values[0] != False and values[0] or ' ',
              'specialization' : values and values[1] != False and values[1] or ' ',
              }
        res['value'] = values
        return res
    
planned_training_pivotal_fields()

class planned_adult_education_training(models.Model):
    _name = 'planned.adult.education.training'
    
    planned_adult_education_fields_ids = fields.One2many('planned.adult.education.training.fields','planned_adult_education_training_id', string='Planned Training Pivotal')
    related_wsp = fields.Many2one('wsp.plan',string="Related WSP")
    
    @api.v7
    def save_btn(self,cr,uid,ids,context=None):
        if context.get('active_id',False):
            self.write(cr, uid, ids[0], {'related_wsp':context['active_id']})
            self.pool.get('wsp.plan').write(cr, uid, context['active_id'], {'planned_adult_education_training_id': ids[0]})
            return {
                'name': 'WSP',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'wsp.plan',
                'res_id': context['active_id'],
            }
    
planned_adult_education_training()

class planned_adult_education_training_fields(models.Model):
    _name = 'planned.adult.education.training.fields'
    
    name = fields.Char(string='First Name')
    surname = fields.Char(string='Surname')
    id_number = fields.Char(string='Id Number')
    population_group = fields.Selection([('african','African'),('coloured','Coloured'),('indian','Indian'),('white','White')], string='Population Group')
#     gender = fields.Selection([('male','Male'),('female','Female')], string='Gender')
    gender = fields.Selection(_get_genders, string='Gender')
    dissability_status_and_type = fields.Selection([('unknown','Unknown')], string='Dissability Status and Type')
    province = fields.Many2one('res.country.state', string='Learner Province')
    municipality = fields.Char(string='Municipality')
    urban = fields.Selection([('urban','Urban'),('rural','Rural')],string='Urban/Rural')
    start_date = fields.Date(string='AET Start Date')
    end_date = fields.Date(string='AET End Date')
    provider = fields.Char(string='Provider')
    aet_level = fields.Selection([('aet_level_1','AET Level 1')],string='AET Level')
    aet_subject = fields.Selection([('numeracy','Numeracy')],string='AET Subject')
    reason = fields.Char(string='Reason')
    planned_adult_education_training_id = fields.Many2one('planned.adult.education.training', string='Planned Adult Education Training')
    
planned_adult_education_training_fields()

class scarce_and_critical_skills(models.Model):
    _name = 'scarce.and.critical.skills'
    
    scarce_and_critical_skills_fields_ids = fields.One2many('scarce.and.critical.skills.fields','scarce_and_critical_skills_id', string='Scarce and Critical Skills')
    related_wsp = fields.Many2one('wsp.plan',string="Related WSP")
    
    @api.v7
    def save_btn(self,cr,uid,ids,context=None):
        if context.get('active_id',False):
            self.write(cr, uid, ids[0], {'related_wsp':context['active_id']})
            self.pool.get('wsp.plan').write(cr, uid, context['active_id'], {'scarce_and_critical_skills_id': ids[0]})
            return {
                'name': 'WSP',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'wsp.plan',
                'res_id': context['active_id'],
            }
    
scarce_and_critical_skills()    

class scarce_and_critical_skills_fields(models.Model):
    _name = 'scarce.and.critical.skills.fields'
    
    name = fields.Char(string='First Name')
    surname = fields.Char(string='Surname')
#     ofo_code = fields.Char(string='OFO Code')
    ofo_code = fields.Many2one('ofo.code',string='OFO')
    occupation = fields.Char(string='Occupation')
#     specialization = fields.Char(string='Specialization')
    specialization = fields.Many2one('specialize.subject', string='Specialisation')
    scarce_skill = fields.Char(string='Scarce Skills')
    critical_skill = fields.Char(string='Critical Skills')
    number_of_vacancies = fields.Integer(string='Number Of Vacancies')
    number_of_potential_vacancies = fields.Integer(string='Number Of Potential Vacancies')
    nqf_level = fields.Char(string='NQF Level')
    degree_of_scarcity = fields.Char(string='Degree of Scarcity')
    reason_for_scarcity = fields.Char(string='Reason for Scarcity/Critical')
    gender = fields.Selection(_get_genders, string='Gender')
#     african = fields.Selection([('am','AM'),('af','AF'),('ad','AD')], string='African')
#     coloured = fields.Selection([('cm','CM'),('cf','CF'),('cd','CD')], string='Coloured')
#     indian = fields.Selection([('im','IM'),('if','IF'),('id','ID')], string='Indian')
#     white = fields.Selection([('wm','WM'),('wf','WF'),('wd','WD')], string='White')
    planned_strategy_address = fields.Char(string='Planned Strategy to address the scarcity')
    province = fields.Many2one('res.country.state', string='Province')
    is_reflected = fields.Boolean(string='Is this reflected to your EE Plan?')
    comments = fields.Char(string='Comments')
    scarce_and_critical_skills_id = fields.Many2one('scarce.and.critical.skills', string='Scarce and Critical Skills')
    
    @api.multi
    def onchange_code(self, ofo_code):
        res = {}
        ofo_code_data = self.env['ofo.code'].browse(ofo_code)
        values = get_occupation_and_specialization(ofo_code_data)
        values = {
              'occupation' : values and values[0] != False and values[0] or ' ',
              'specialization' : values and values[1] != False and values[1] or ' ',
              }
        res['value'] = values
        return res
    
scarce_and_critical_skills_fields()