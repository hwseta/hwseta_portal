from openerp import models, fields, api
import csv
from StringIO import StringIO
import itertools

GENDERS = {
           'am':'African Male',
           'af':'African Female',
           'ad':'African Dissable',
           'cm':'Coloured Male',
           'cf':'Coloured Female',
           'cd':'Coloured Dissable',
           'im':'Indian Male',
           'if':'Indian Female',
           'id':'Indian Dissable',
           'wm':'White Male',
           'wf':'White Female',
           'wd':'White Dissable'
           }

class import_csv(models.Model):
    _name = 'import.csv'
    
    name = fields.Char(string='Filename')
    import_csv_file = fields.Binary(string='Import CSV')
    
    @api.multi
    def get_gender(self, val):
        gender = str(val)
        gen = ''
        for gender_key,gender_val in GENDERS.iteritems():
            if gender_val == gender:
                gen = gender_key
        return gen
    
    @api.multi
    def get_specialization(self, val):
        specialize_data = self.env['specialize.subject'].search([('name','ilike',str(val))])
        if type([specialize_data]) == 'list':
            specialize_data = specialize_data[0]
        return specialize_data and specialize_data.id
    
    @api.multi
    def get_nqf_aligned(self, val):
        if str(val) == 'TRUE':
            nqf_aligned = True
        return nqf_aligned
        
    ## Following function is used to Import CSV's.
    @api.multi
    def csv_file_import(self):
        context = self._context
        options = {'headers': True, 'quoting': '"', 'separator': ',', 'encoding': 'utf-8'}
        file_content = self.import_csv_file.decode('base64')
        csv_iterator = csv.reader(
           StringIO(file_content),
           quotechar=str(options['quoting']),
           delimiter=str(options['separator']))
        csv_nonempty = itertools.ifilter(None, csv_iterator)
        encoding = options.get('encoding', 'utf-8')
        result = itertools.imap(
           lambda row: [item.decode(encoding) for item in row],
           csv_nonempty)
        if context.get('val') == 'actual_training':
            actual_training_obj = self.env['actual.training.d1']
            
            count = 0
            for row in result:
                ## Skipping Header Fields.
                if count > 0:
                    ofo_data = self.env['ofo.code'].search([('name','=',str(row[2]))])
                    actual_training_fields = {
                                              'name' : row[0],
                                              'surname' : row[1],
                                              'code' : ofo_data and ofo_data.id,
                                              'major': row[3],
                                              'sub_major_group' : row[4],
                                              'occupation' : row[5],
                                              'specialization' : self.get_specialization(row[6]),
                                              'municipality' : row[7],
                                              'urban' : row[8],
                                              'type_training' : row[9],
                                              'name_training' : row[10],
                                              'training_cost' : row[11],
                                              'non_aligned' : self.get_nqf_aligned(row[12]),
                                              'nqf_level' : row[13],
                                              'gender' : self.get_gender(row[14]),
                                              'age_group' : row[15],
                                              'total_cost' : row[16],
                                              }
                    wsp_id = self._context['active_id']
                    actual_training_data = actual_training_obj.search([('related_wsp','=',wsp_id)])
                    ## If Records are already their in the Actual Training Wizard, Then needs to update the values.
                    if actual_training_data :
                        actual_training_data.write({
                                                    'actual_training_fields_ids' : [(0,0,actual_training_fields)],
                                                    })
                    ## If Records are not there then create new records in the Actual Training Wizard.
                    else:
                        actual_training_id = actual_training_obj.create({
                                                               'actual_training_fields_ids' : [(0,0,actual_training_fields)],
                                                               'related_wsp' : wsp_id,
                                                               })
                        wsp_plan_data = self.env['wsp.plan'].browse(wsp_id)
                        wsp_plan_data.write({'actual_training_id':actual_training_id})
                count += 1                
        ## TODO : Needs to check whether code import csv or not.
        elif context.get('val') == 'adult_edu':
            actual_adult_edu_obj = self.env['actual.adult.education']
            count = 0
            for row in result:
                ## Skipping Header Fields.
                if count > 0:
                    ## For Province
                    learner_province_id = self.env['res.country.state'].search([('name','=',str(row[6]))])
                    actual_adult_education_fields = {
                                                'name' : row[0],
                                                'surname' : row[1],
                                                'id_number' : int(row[2]),
                                                'population_group': row[3],
                                                'gender' : self.get_gender(row[4]),
                                                'dissability_status_and_type' : row[5],
                                                'learner_province' : learner_province_id and learner_province_id.id,
                                                'municipality' : row[7],
                                                'urban' : row[8],
                                                'aet_start_date' : row[9],
                                                'aet_end_date' : row[10],
                                                'provider' : row[11],
                                                'aet_level' : row[12],
                                                'aet_subject' : row[13],
                                                'free_text' : row[14],
                                              }
                    wsp_id = self._context['active_id']
                    actual_edu_training_data = actual_adult_edu_obj.search([('related_wsp','=',wsp_id)])
                    ## If Records are already their in the Actual Training Wizard, Then needs to update the values.
                    if actual_edu_training_data :
                        actual_edu_training_data.write({
                                                    'actual_adult_education_fields_ids' : [(0,0,actual_adult_education_fields)],
                                                    })
                    ## If Records are not there then create new records in the Actual Training Wizard.
                    else:
                        actual_adult_education_id = actual_adult_edu_obj.create({
                                                               'actual_adult_education_fields_ids' : [(0,0,actual_adult_education_fields)],
                                                               'related_wsp' : int(wsp_id),
                                                               })
                        wsp_plan_data = self.env['wsp.plan'].browse(wsp_id)
                        wsp_plan_data.write({'actual_adult_education_id':actual_adult_education_id})
                count += 1
        elif context.get('val') == 'pivotal_trainig':   
            actual_pivotal_obj = self.env['actual.pivotal.training']
            count = 0
            for row in result:
                ## Skipping Header Fields.
                if count > 0:
                    ## For OFO
                    ofo_data = self.env['ofo.code'].search([('name','=',str(row[2]))])
                    ## For Province
                    province_id = self.env['res.country.state'].search([('name','=',str(row[14]))])
                    actual_pivotal_training_fields = {
                                              'name' : row[0],
                                              'surname' : row[1],
                                              'ofo_code' : ofo_data and ofo_data.id,
                                              'major': row[3],
                                              'sub_major_group' : row[4],
                                              'occupation' : row[5],
                                              'specialization' : self.get_specialization(row[6]),
                                              'socio_economic_status' : row[7],
                                              'pivotal_programme_institution' : row[8],
                                              'pivotal_programme_qualification' : row[9],
                                              'pivotal_programme_type' : row[10],
                                              'cost' : row[11],
                                              'municipality' : row[12],
                                              'urban' : row[13],
                                              'province' : province_id and province_id.id,
                                              'start_date' : row[15],
                                              'end_date' : row[16],
                                              'gender' : self.get_gender(row[17]),
                                              'total_person' : row[18],
                                              'age_group' : row[19],
                                              'total_cost' : row[20],
                                              }
                    wsp_id = self._context['active_id']
                    actual_pivotal_training_data = actual_pivotal_obj.search([('related_wsp','=',wsp_id)])
                    ## If Records are already their in the Actual Training Wizard, Then needs to update the values.
                    if actual_pivotal_training_data :
                        actual_pivotal_training_data.write({
                                                    'actual_pivotal_training_fields_ids' : [(0,0,actual_pivotal_training_fields)],
                                                    })
                    ## If Records are not there then create new records in the Actual Training Wizard.
                    else:
                        actual_pivotal_training_id = actual_pivotal_obj.create({
                                                               'actual_pivotal_training_fields_ids' : [(0,0,actual_pivotal_training_fields)],
                                                               'related_wsp' : wsp_id,
                                                               })
                        wsp_plan_data = self.env['wsp.plan'].browse(wsp_id)
                        wsp_plan_data.write({'actual_pivotal_training_id':actual_pivotal_training_id})
                count += 1
        elif context.get('val') == 'total_emp':   
            total_employment_profile_obj = self.env['total.employment.profile']
            count = 0
            for row in result:
                ## Skipping Header Fields.
                if count > 0:
                    ofo_data = self.env['ofo.code'].search([('name','=',str(row[2]))])
                    province_id = self.env['res.country.state'].search([('name','=',str(row[6]))])
                    total_employment_profile_fields = {
                                              'name' : row[0],
                                              'surname' : row[1],
                                              'ofo_code' : ofo_data and ofo_data.id,
                                              'occupation': row[3],
                                              'specialization' : self.get_specialization(row[4]),
                                              'municipality' : row[5],
                                              'province' : province_id and province_id.id,
                                              'urban' : row[7],
                                              'highest_education_level' : row[8],
                                              'scarce_skill' : row[9],
                                              'gender':self.get_gender(row[10]),
                                              'age_group' : row[11],
                                              }
                    wsp_id = self._context['active_id']
                    total_employment_profile_data = total_employment_profile_obj.search([('related_wsp','=',wsp_id)])
                    ## If Records are already their in the Actual Training Wizard, Then needs to update the values.
                    if total_employment_profile_data :
                        total_employment_profile_data.write({
                                                    'total_employment_profile_fields_ids' : [(0,0,total_employment_profile_fields)],
                                                    })
                    ## If Records are not there then create new records in the Actual Training Wizard.
                    else:
                        total_employment_profile_id = total_employment_profile_obj.create({
                                                               'total_employment_profile_fields_ids' : [(0,0,total_employment_profile_fields)],
                                                               'related_wsp' : wsp_id,
                                                               })
                        wsp_plan_data = self.env['wsp.plan'].browse(wsp_id)
                        wsp_plan_data.write({'total_employment_profile_id':total_employment_profile_id})
                count += 1
        elif context.get('val') == 'non_pivotal_b':   
            planned_training_non_pivotal_obj = self.env['planned.training.non.pivotal']
            count = 0
            for row in result:
                ## Skipping Header Fields.
                if count > 0:
                    ## For OFO
                    ofo_data = self.env['ofo.code'].search([('name','=',str(row[3]))])
                    ## For Province
                    province_id = self.env['res.country.state'].search([('name','=',str(row[7]))])
                    planned_training_non_pivotal_fields = {
                                              'name' : row[0],
                                              'surname' : row[1],
                                              'type_of_training' : row[2],
                                              'ofo_code': ofo_data and ofo_data.id,
                                              'occupation' : row[4],
                                              'specialization' : self.get_specialization(row[5]),
                                              'municipality' : row[6],
                                              'province' : province_id and province_id.id,
                                              'urban' : row[8],
                                              'socio_economic_status' : row[9],
                                              'type_of_training_inter' : row[10],
                                              'name_of_training_inter' : row[11],
                                              'training_cost_per_learner' : row[12],
                                              'nqf_aligned' : self.get_nqf_aligned(row[13]),
                                              'nqf_level' : row[14],
                                              'gender':self.get_gender(row[15]),
                                              'age_group' : row[16],
                                              'total_cost': row[17],
                                              }
                    wsp_id = self._context['active_id']
                    planned_training_non_pivotal_data = planned_training_non_pivotal_obj.search([('related_wsp','=',wsp_id)])
                    ## If Records are already their in the Actual Training Wizard, Then needs to update the values.
                    if planned_training_non_pivotal_data :
                        planned_training_non_pivotal_data.write({
                                                    'planned_training_non_pivotal_fields_ids' : [(0,0,planned_training_non_pivotal_fields)],
                                                    })
                    ## If Records are not there then create new records in the Actual Training Wizard.
                    else:
                        planned_training_non_pivotal_id = planned_training_non_pivotal_obj.create({
                                                               'planned_training_non_pivotal_fields_ids' : [(0,0,planned_training_non_pivotal_fields)],
                                                               'related_wsp' : wsp_id,
                                                               })
                        wsp_plan_data = self.env['wsp.plan'].browse(wsp_id)
                        wsp_plan_data.write({'planned_training_non_pivotal_id':planned_training_non_pivotal_id})
                count += 1
        elif context.get('val') == 'planned_pivotal': 
            planned_training_pivotal_obj = self.env['planned.training.pivotal']
            count = 0
            for row in result:
                ## Skipping Header Fields.
                if count > 0:
                    ## For OFO
                    ofo_data = self.env['ofo.code'].search([('name','=',str(row[3]))])
                    ## For Province
                    province_id = self.env['res.country.state'].search([('name','=',str(row[13]))])
                    planned_training_pivotal_fields = {
                                              'name' : row[0],
                                              'surname' : row[1],
                                              'type_of_training' : row[2],
                                              'ofo_code': ofo_data and ofo_data.id,
                                              'occupation' : row[4],
                                              'specialization' : self.get_specialization(row[5]),
                                              'socio_economic_status' : row[6],
                                              'pivotal_programme_institute' : row[7],
                                              'pivotal_programme_qualification' : row[8],
                                              'pivotal_programme_type' : row[9],
                                              'cost_per_learner' : row[10],
                                              'municipality' : row[11],
                                              'urban' : row[12],
                                              'province' : province_id and province_id.id,
                                              'start_date' : row[14],
                                              'end_date' : row[15],
                                              'nqf_aligned' : self.get_nqf_aligned(row[16]),
                                              'nqf_level' : row[17],
                                              'gender':self.get_gender(row[18]),
                                              'age_group' : row[19],
                                              'total_cost' : row[20],
                                              }
                    wsp_id = self._context['active_id']
                    planned_training_pivotal_fields_data = planned_training_pivotal_obj.search([('related_wsp','=',wsp_id)])
                    ## If Records are already their in the Actual Training Wizard, Then needs to update the values.
                    if planned_training_pivotal_fields_data :
                        planned_training_pivotal_fields_data.write({
                                                    'planned_training_pivotal_fields_ids' : [(0,0,planned_training_pivotal_fields)],
                                                    })
                    ## If Records are not there then create new records in the Actual Training Wizard.
                    else:
                        planned_training_pivotal_id = planned_training_pivotal_obj.create({
                                                               'planned_training_pivotal_fields_ids' : [(0,0,planned_training_pivotal_fields)],
                                                               'related_wsp' : wsp_id,
                                                               })
                        wsp_plan_data = self.env['wsp.plan'].browse(wsp_id)
                        wsp_plan_data.write({'planned_training_pivotal_id':planned_training_pivotal_id})
                count += 1
        elif context.get('val') == 'planned_adult_edu':
            planned_adult_education_training_obj = self.env['planned.adult.education.training']
            count = 0
            for row in result:
                ## Skipping Header Fields.
                if count > 0:
                    ## For Province
                    province_id = self.env['res.country.state'].search([('name','=',str(row[6]))])
                    planned_adult_education_fields = {
                                              'name' : row[0],
                                              'surname' : row[1],
                                              'id_number' : row[2],
                                              'population_group': row[3],
                                              'gender' : self.get_gender(row[4]),
                                              'dissability_status_and_type' : row[5],
                                              'province' : province_id and province_id.id,
                                              'municipality' : row[7],
                                              'urban' : row[8],
                                              'start_date' : row[9],
                                              'end_date' : row[10],
                                              'provider' : row[11],
                                              'aet_level' : row[12],
                                              'aet_subject' : row[13],
                                              'reason' : row[14],
                                              }
                    wsp_id = self._context['active_id']
                    planned_adult_education_fields_data = planned_adult_education_training_obj.search([('related_wsp','=',wsp_id)])
                    ## If Records are already their in the Actual Training Wizard, Then needs to update the values.
                    if planned_adult_education_fields_data :
                        planned_adult_education_fields_data.write({
                                                    'planned_adult_education_fields_ids' : [(0,0,planned_adult_education_fields)],
                                                    })
                    ## If Records are not there then create new records in the Actual Training Wizard.
                    else:
                        planned_adult_education_training_id = planned_adult_education_training_obj.create({
                                                               'planned_adult_education_fields_ids' : [(0,0,planned_adult_education_fields)],
                                                               'related_wsp' : wsp_id,
                                                               })
                        wsp_plan_data = self.env['wsp.plan'].browse(wsp_id)
                        wsp_plan_data.write({'planned_adult_education_training_id':planned_adult_education_training_id})
                count += 1
        elif context.get('val') == 'scarce_critical':
            scarce_and_critical_skills_obj = self.env['scarce.and.critical.skills']
            count = 0
            for row in result:
                ## Skipping Header Fields.
                if count > 0:
                    ## For OFO
                    ofo_data = self.env['ofo.code'].search([('name','=',str(row[2]))])
                    ## For Province
                    province_id = self.env['res.country.state'].search([('name','=',str(row[14]))])
                    scarce_and_critical_skills_fields = {
                                              'name' : row[0],
                                              'surname' : row[1],
                                              'ofo_code' : ofo_data and ofo_data.id,
                                              'occupation': row[3],
                                              'specialization' : self.get_specialization(row[4]),
                                              'scarce_skill' : row[5],
                                              'critical_skill' : row[6],
                                              'number_of_vacancies' : row[7],
                                              'number_of_potential_vacancies' : row[8],
                                              'nqf_level' : row[9],
                                              'degree_of_scarcity' : row[10],
                                              'reason_for_scarcity' : row[11],
                                              'gender':self.get_gender(row[12]),
                                              'planned_strategy_address' : row[13],
                                              'province' : province_id and province_id.id,
                                              'is_reflected' : row[15],
                                              'comments' : row[16],
                                              }
                    wsp_id = self._context['active_id']
                    scarce_and_critical_skills_fields_data = scarce_and_critical_skills_obj.search([('related_wsp','=',wsp_id)])
                    ## If Records are already their in the Actual Training Wizard, Then needs to update the values.
                    if scarce_and_critical_skills_fields_data :
                        scarce_and_critical_skills_fields_data.write({
                                                    'scarce_and_critical_skills_fields_ids' : [(0,0,scarce_and_critical_skills_fields)],
                                                    })
                    ## If Records are not there then create new records in the Actual Training Wizard.
                    else:
                        scarce_and_critical_skills_id = scarce_and_critical_skills_obj.create({
                                                               'scarce_and_critical_skills_fields_ids' : [(0,0,scarce_and_critical_skills_fields)],
                                                               'related_wsp' : wsp_id,
                                                               })
                        wsp_plan_data = self.env['wsp.plan'].browse(wsp_id)
                        wsp_plan_data.write({'scarce_and_critical_skills_id':scarce_and_critical_skills_id})
                count += 1
        return True
    

import_csv()    
