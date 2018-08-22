from openerp import models, fields, api, _
import base64
import xlrd,datetime
from openerp.exceptions import Warning
import xlsxwriter
import cStringIO
import re
import unicodedata
class import_wsp_xls(models.TransientModel):
    _name = 'import.wsp.xls'
    _description = 'Importing WSP from XLS files'
    
    actual_atr_file = fields.Binary(string='Upload Actual(ATR)')
    planned_wsp_file = fields.Binary(string='Upload Planned(WSP)')
    planned_current_file = fields.Binary(string='Upload Planned(2015-2016)')

    @api.multi
    def get_population_group(self, race_value):
        race = ''
        if race_value == 'African':
            race = 'african'
        if race_value == 'Coloured':
            race = 'coloured'
        if race_value == 'Indian':
            race = 'indian'
        if race_value == 'White':
            race = 'white'
        return race
    
    @api.multi
    def get_genders(self, gender_value):
        gender = ''
        if gender_value == 'M - Male':
            gender = 'male'
        if gender_value == 'F - Female':
            gender = 'female'
        return gender
    
    @api.multi
    def get_disability_status(self, disability_value):
        disability_status = ''
        if disability_value == '01 - Sight ( even with glasses )':
            disability_status = 'site'
        if disability_value == '02 - Hearing ( even with h.aid )':
            disability_status = 'hearing'
        if disability_value == '03 - Communication ( talk/listen)':
            disability_status = 'communication'
        if disability_value == '04 - Physical ( move/stand, etc)':
            disability_status = 'physical'
        if disability_value == '05 - Intellectual ( learn,etc)':
            disability_status = 'intellectual'
        if disability_value == '06 - Emotional ( behav/psych)':
            disability_status = 'emotional'
        if disability_value == '07 - Multiple':
            disability_status = 'multiple'
        if disability_value == '09 - Disabled':
            disability_status = 'disabled'
        if disability_value == 'N-None':
            disability_status = 'none'
        return disability_status
    
    @api.multi
    def get_province(self, province_value):
        province = None
        province_data = self.env['res.country.state'].search([('name','=',province_value)],limit=1)
        if province_data :
            province = province_data.id
        return province    
    
    @api.multi
    def get_city(self, city_value):
        city = None
        city_data = self.env['res.city'].search([('name','=',city_value)],limit=1)
        if city_data :
            city = city_data.id
        return city
    
    @api.multi
    def get_suburb(self, suburb_value):
        suburb = None
        suburb_data = self.env['res.suburb'].search([('name','=',suburb_value)], limit=1)
        if suburb_data :
            suburb = suburb_data.id
        return suburb
    
    @api.multi
    def get_municipality(self, municipality_value):
        municipality_data = self.env['res.municipality'].search([('name','=',municipality_value)],limit=1)
        municipality = None
        if municipality_data :
            municipality = municipality_data.id
        return municipality
    
    @api.multi
    def get_urban_rural(self, urban_value):
        urban_rural = ''
        if urban_value == 'Urban' :
            urban_rural = 'urban'
        if urban_value == 'Rural' :
            urban_rural = 'rural'
        if urban_rural == 'Unknown' :
            urban_rural = 'unknown'
        return urban_rural
    
    @api.multi
    def get_aet_level(self, aet_level_value):
        aet_level = ''
        if aet_level_value == 'AET Level 1':
            aet_level = 'aet_level_1'
        if aet_level_value == 'AET Level 2':
            aet_level = 'aet_level_2'
        if aet_level_value == 'AET Level 3':
            aet_level = 'aet_level_3'
        if aet_level_value == 'AET Level 4':
            aet_level = 'aet_level_4'
        return aet_level
    
    @api.multi
    def get_aet_subject(self, aet_subject_value):
        aet_subject = ''
        if aet_subject_value == 'Life Skills':
            aet_subject = 'life_skills'
        if aet_subject_value == 'Numeracy':
            aet_subject = 'numeracy'
        if aet_subject_value == 'Literacy':
            aet_subject = 'literacy'
        return aet_subject
    
    @api.multi
    def get_multiple_aet_subject(self, aet_subject_value):
        aet_subject_ids = []
        if aet_subject_value :
            aet_subject = aet_subject_value.split(',')
            for aet_sub in aet_subject :
                aet_subject_id = self.env['aet.subject'].search([('name','=',aet_sub)])
                if aet_subject_id :
                    aet_subject_ids.append(aet_subject_id.id)
            if aet_subject_ids : 
                return aet_subject_ids
            if not aet_subject_ids:
                return None 
        return None
    
    @api.multi
    def get_training_type(self, training_type_value):
        training_type = ''
        if training_type_value == 'Pivotal':
            training_type = 'pivotal'
        if training_type_value == 'NonPivotal':
            training_type = 'non-pivotal'
        return training_type    
    
    @api.multi
    def get_ofo_code(self, ofo_code_value):
        ofo_code = None
        if type(ofo_code_value) == float :
            ofo_code_value = str(int(ofo_code_value))
        if type(ofo_code_value) == int :
            ofo_code_value = str(ofo_code_value)
        ofo_code_data = self.env['ofo.code'].search([('name','=',ofo_code_value)], limit=1)
        if ofo_code_data :
            ofo_code = ofo_code_data.id
        return ofo_code
    
    @api.multi
    def get_occupation(self,ofo_code_value, occ_value):
        if type(ofo_code_value) == float :
            ofo_code_value = str(int(ofo_code_value))
        if type(ofo_code_value) == int :
            ofo_code_value = str(ofo_code_value)
        ofo_code_data = self.env['ofo.code'].search([('name','=',ofo_code_value)], limit=1)

        occupation = None
        occupation_data = self.env['occupation.ofo'].search([('name','=',occ_value)])
        if occupation_data :
            occupation = occupation_data.id
        if ofo_code_data and occupation:
            if ofo_code_data.occupation.id == occupation:
                return occupation
        return None
    
    @api.multi
    def check_specialisation_exists(self, ofo_code_value):
        specialisation_exists=False
        if ofo_code_value:
            ofo_obj = self.env['ofo.code'].browse(ofo_code_value)
            if ofo_obj:
                for spec in ofo_obj.specialization_ids:
                    specialisation_exists=True
        return specialisation_exists
    
    @api.multi
    def get_specialization(self,ofo_code_value,specialize_value):
        if type(ofo_code_value) == float :
            ofo_code_value = str(int(ofo_code_value))
        if type(ofo_code_value) == int :
            ofo_code_value = str(ofo_code_value)
        ofo_code_data = self.env['ofo.code'].search([('name','=',ofo_code_value)], limit=1)
        
        specialization_data = self.env['specialize.subject'].search([('name','=',specialize_value)])
        specialization = None
        if specialization_data :
            specialization = specialization_data.id
        
        if ofo_code_data.id and specialization:
            self._cr.execute("select * from specialisation_ofo_rel where ofo_id=%s and specialise_id=%s"%(ofo_code_data.id,specialization))
            result = self._cr.fetchall()
            if not result:
                return None
            if len(result[0]) == 2:
                return specialization
        return None
    
    @api.multi
    def get_socio_eco_status(self, socio_value):
        socio = ''
        if socio_value == 'Employed' :
            socio = 'employed'
        if socio_value == 'Unemployed':
            socio = 'unemployed'
        return socio
    
    @api.multi
    def get_type_of_training(self, type_train_value):
        type_of_training = ''
        if type_train_value == 'Continuous Development Programmes' :
            type_of_training = 'continuous_development_programmes'
        if type_train_value == 'Standard Operating Procedures' :
            type_of_training = 'standard_operating_procedures'
        if type_train_value == 'Refresher Courses' :
            type_of_training = 'refresher_courses'
        if type_train_value == 'Short Courses' :
            type_of_training = 'short_courses'
        if type_train_value == 'Product Specific Courses' :
            type_of_training = 'product_specific_courses'
        if type_train_value == 'Life Skills' :
            type_of_training = 'life_skills'
        if type_train_value == 'Other' :
            type_of_training = 'other'
        return type_of_training
    
    @api.multi
    def get_complete_type_of_training(self, type_train_value):
        type_training_data = self.env['training.intervention'].search([('name','=',type_train_value)])
        type_of_training = None
        if type_training_data :
            type_of_training = type_training_data.id
        return type_of_training
#         type_of_training = ''
#         if type_train_value == 'Continuous Development Programmes' :
#             type_of_training = 'continuous_development_programmes'
#         if type_train_value == 'Standard Operating Procedures' :
#             type_of_training = 'standard_operating_procedures'
#         if type_train_value == 'Refresher Courses' :
#             type_of_training = 'refresher_courses'
#         if type_train_value == 'Short Courses' :
#             type_of_training = 'short_courses'
#         if type_train_value == 'Product Specific Courses' :
#             type_of_training = 'product_specific_courses'
#         if type_train_value == 'Life Skills' :
#             type_of_training = 'life_skills'
#         if type_train_value == 'Internship':
#             type_of_training = 'internship'
#         if type_train_value == 'Workplace Experience':
#             type_of_training = 'workplace_experience'
#         if type_train_value == 'Nation Certificate Vocational':
#             type_of_training = 'nation_certificate_vocational'
#         if type_train_value == 'Learnership':
#             type_of_training = 'learnership'
#         if type_train_value == 'Apprenticeship':
#             type_of_training = 'apprenticeship'
#         if type_train_value == 'Academic Qualification':
#             type_of_training = 'academic_qualification'
#         if type_train_value == 'Skills Programme':
#             type_of_training = 'skills_programme'
#         if type_train_value == 'Other' :
#             type_of_training = 'other'
#         return type_of_training
                  
    @api.multi
    def get_pivotal_programme_type(self, pivotal_prog_value):
        pivotal_type = ''
        if pivotal_prog_value == 'Internship':
            pivotal_type = 'internship'
        if pivotal_prog_value == 'Workplace Experience':
            pivotal_type = 'workplace_experience'
        if pivotal_prog_value == 'Nation Certificate Vocational':
            pivotal_type = 'nation_certificate_vocational'
        if pivotal_prog_value == 'Learnership':
            pivotal_type = 'learnership'
        if pivotal_prog_value == 'Apprenticeship':
            pivotal_type = 'apprenticeship'
        if pivotal_prog_value == 'Academic Qualification':
            pivotal_type = 'academic_qualification'
        if pivotal_prog_value == 'Skills Programme':
            pivotal_type = 'skills_programme'
        return pivotal_type
    
    @api.multi
    def get_nqf_aligned(self, nqf_aligned_value):
        nqf_aligned = ''
        if nqf_aligned_value == 'Yes' or nqf_aligned_value == 'YES':
            nqf_aligned = 'yes'
        if nqf_aligned_value == 'No' or nqf_aligned_value == 'NO':
            nqf_aligned = 'no'
        return nqf_aligned
    
    @api.multi
    def get_nqf_level(self, nqf_level_value):
        nqf_level = ''
        if nqf_level_value == 'ABET':
            nqf_level = 'abet'
        if nqf_level_value == 'Level 1':
            nqf_level = 'level1'
        if nqf_level_value == 'Level 2':
            nqf_level = 'level2'
        if nqf_level_value == 'Level 3':
            nqf_level = 'level3'
        if nqf_level_value == 'Level 4':
            nqf_level = 'level4'
        if nqf_level_value == 'Level 5':
            nqf_level = 'level5'
        if nqf_level_value == 'Level 6':
            nqf_level = 'level6'
        if nqf_level_value == 'Level 7':
            nqf_level = 'level7'
        if nqf_level_value == 'Level 8':
            nqf_level = 'level8'
        if nqf_level_value == 'Level 9':
            nqf_level = 'level9'
        if nqf_level_value == 'Level 10':
            nqf_level = 'level10'
        if nqf_level_value == 'Below Level 1':
            nqf_level = 'below_level_1'
        return nqf_level
    
    @api.multi
    def get_disability(self, disability_value):
        disability = ''
        if disability_value == 'Yes':
            disability = 'yes'
        if disability_value == 'No':
            disability = 'no'
        return disability
    
    @api.multi
    def get_citizen_status(self, citizen_value):
        citizen_status = ''
        if citizen_value == 'D - Dual (SA plus other)' :
            citizen_status = 'dual'
        if citizen_value == 'O - Other' :
            citizen_status = 'other'
        if citizen_value == 'SA - South Africa':
            citizen_status = 'sa'
        if citizen_value == 'U - Unknown' :
            citizen_status = 'unknown'
        return citizen_status
    
    @api.multi
    def get_highest_edu(self, high_edu_value):
        highest_edu = ''
        if high_edu_value == 'Abet Level 1':
            highest_edu = 'abet_level_1'
        if high_edu_value == 'Abet Level 2':
            highest_edu = 'abet_level_2'
        if high_edu_value == 'Abet Level 3':
            highest_edu = 'abet_level_3'
        if high_edu_value == 'Abet Level 4':
            highest_edu = 'abet_level_4'
        if high_edu_value == 'NQF 1,2,3':
            highest_edu = 'nqf123'
        if high_edu_value == 'NQF 4,5':
            highest_edu = 'nqf45'
        if high_edu_value == 'NQF 6,7':
            highest_edu = 'nqf67'
        if high_edu_value == 'NQF 8,9,10':
            highest_edu = 'nqf8910'
        return highest_edu
    
    @api.multi
    def validate_id_number(self, id_number):
        if type(id_number) == unicode :
            id_number = id_number
        if type(id_number) == float :
            id_number = int(id_number)
        id_number = str(id_number).strip()
        return id_number
    
    @api.multi
    def validate_date(self, input_date, excel):
        try:
            if type(input_date) == unicode :
                input_date = datetime.datetime.strptime(str(input_date),'%d/%m/%Y').date()
            elif type(input_date) == float :
                input_date = datetime.datetime(*xlrd.xldate_as_tuple(input_date, excel.datemode)).date()
            else:
                input_date = str(input_date)
        except:    
            input_date = str(input_date)
        return input_date
 
    @api.multi
    def import_wsp(self):
        context = self._context
        wsp_plan_data = self.env['wsp.plan'].browse(context.get('active_id',False))
        admin_config_data = self.env['leavy.income.config'].search([])
        if admin_config_data :
            if admin_config_data.wsp_financial_year.id != wsp_plan_data.fiscal_year.id:
                raise Warning(_('You can not Import WSP for %s  financial year!!!')%(wsp_plan_data.fiscal_year.name)) 
        actual_csv_data = ''
        planned_csv_data = ''
        planned_current_csv_data = ''
        
        if self.actual_atr_file : 
            actual_csv_data = base64.decodestring(self.actual_atr_file)
            ## Removing Existing records if importing again by mistake.
            ## For Actual Training Sheets.
            
#             if wsp_plan_data.training_actual_ids :
#                 wsp_plan_data.write({'training_actual_ids':[(2,actual_data.id) for actual_data in wsp_plan_data.training_actual_ids]})
#             if wsp_plan_data.actual_adult_education_ids :
#                 wsp_plan_data.write({'actual_adult_education_ids':[(2,actual_data.id) for actual_data in wsp_plan_data.actual_adult_education_ids]})
        if self.planned_wsp_file :
            planned_csv_data = base64.decodestring(self.planned_wsp_file)
            ## Removing Existing records if importing again by mistake.
            ## For Planned Training Sheets.
            
#             if wsp_plan_data.total_employment_profile_ids :
#                 wsp_plan_data.write({'total_employment_profile_ids':[(2,planned_data.id) for planned_data in wsp_plan_data.total_employment_profile_ids]})
#             if wsp_plan_data.training_planned_ids :
#                 wsp_plan_data.write({'training_planned_ids':[(2,planned_data.id) for planned_data in wsp_plan_data.training_planned_ids]})
#             if wsp_plan_data.planned_adult_education_ids :
#                 wsp_plan_data.write({'planned_adult_education_ids':[(2,planned_data.id) for planned_data in wsp_plan_data.planned_adult_education_ids]})
#             if wsp_plan_data.scarce_and_critical_skills_ids :
#                 wsp_plan_data.write({'scarce_and_critical_skills_ids':[(2,planned_data.id) for planned_data in wsp_plan_data.scarce_and_critical_skills_ids]})
        if self.planned_current_file :
            planned_current_csv_data = base64.decodestring(self.planned_current_file)
            ## Removing Existing records if importing again by mistake.
            ## For Planned 2015-2016 Sheets.
            if wsp_plan_data.training_actual_planned_ids :
                wsp_plan_data.write({'training_actual_planned_ids':[(2,planned_current_data.id) for planned_current_data in wsp_plan_data.training_actual_planned_ids]})
            if wsp_plan_data.actual_planned_adult_education_ids :
                wsp_plan_data.write({'actual_planned_adult_education_ids':[(2,planned_current_data.id) for planned_current_data in wsp_plan_data.actual_planned_adult_education_ids]})
        
        ##    
        ## For Loading Actual Data.
        msg = ''
        actual_training_list = []
        adult_education_training_list = []
        if actual_csv_data :
            try:
                excel = xlrd.open_workbook(file_contents = actual_csv_data)  
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
                count = 0
                sheet_row = []
                while count < row_count:
                    sheet_row = xl_sheet.row(count)
                    #TODO: Later on we need to change the condition according to macro csv.
                    # Loading Actual Training Data.
                    blank_row = 0
                    for col in sheet_row :
                        if col.value :
                            blank_row += 1
                    if count > 0 and sheet_count == 1 and blank_row > 0:
                        ## ## Validating Actual Training Excel Sheet file for Invalid data
                        check_cost_atr = True
                        val_training_type = self.get_training_type(sheet_row[0].value)
                        val_id_number = self.validate_id_number(sheet_row[3].value)
                        val_ofo_code = self.get_ofo_code(sheet_row[4].value)
                        val_occupation = self.get_occupation(sheet_row[4].value,sheet_row[5].value)
                        specialisation_exists = self.check_specialisation_exists(val_ofo_code)
                        val_specialisation = self.get_specialization(sheet_row[4].value,sheet_row[6].value)
                        val_province = self.get_province(sheet_row[7].value)
                        val_city = self.get_city(sheet_row[8].value)
                        val_urban = self.get_urban_rural(sheet_row[9].value)
                        val_socio = self.get_socio_eco_status(sheet_row[10].value)
                        val_type_training = self.get_complete_type_of_training(sheet_row[11].value)
#                         val_type_training1 = self.get_complete_type_of_training(sheet_row[14].value)
                        
                        if not re.search('[a-zA-Z]', str(sheet_row[18].value)) :
                            start_date = self.validate_date(sheet_row[18].value, excel)
                        else:
                            start_date = str(sheet_row[18].value)
                        if not re.search('[a-zA-Z]', str(sheet_row[19].value)) :
                            end_date = self.validate_date(sheet_row[19].value, excel)
                        else:
                            end_date = str(sheet_row[19].value)

                        val_nqf_aligned = self.get_nqf_aligned(sheet_row[20].value)
                        val_nqf_level = self.get_nqf_level(sheet_row[21].value)
                        val_population = self.get_population_group(sheet_row[22].value)
                        val_genders = self.get_genders(sheet_row[23].value)
                        val_disability = self.get_disability(sheet_row[24].value)
                        if val_training_type == '':
                            msg+='<b>Type of Training '+str(sheet_row[0].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 1 in the Actual Training Sheet.='
#                         if sheet_row[1].value == '' :
#                             msg+='<b>Name '+sheet_row[1].value+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 2 in the Actual Training Sheet.='
#                         if sheet_row[2].value == '' :
#                             msg+='<b>SurName '+sheet_row[2].value+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 3 in the Actual Training Sheet.='
#                         if val_id_number.isdigit() == True and len(val_id_number) != 13:
#                             msg+='<b>Employee ID '+str(sheet_row[3].value)+'</b> length should be 13 digits. Found at row <b>'+str(count+1)+'</b> and columns 4 in the Actual Training Sheet.='
                        if val_id_number == '':
                            msg+='<b>Employee ID '+str(sheet_row[3].value).encode('utf-8')+'</b> should not be blank. Found at row <b>'+str(count+1)+'</b> and columns 4 in the Actual Training Sheet.='
                        if val_ofo_code == None :
                            msg+='<b>OFO Code '+str(sheet_row[4].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 5 in the Actual Training Sheet.='
                        if val_occupation == None:
                            msg+='<b>Occupation '+str(sheet_row[5].value).encode('utf-8')+'</b> should be linked with ofo code. Found at row <b>'+str(count+1)+'</b> and columns 6 in the Actual Training Sheet.='
                        if val_specialisation == None and specialisation_exists == True:
                            msg+='<b>Specialisation '+str(sheet_row[6].value).encode('utf-8')+'</b> should be linked with ofo code. Found at row <b>'+str(count+1)+'</b> and columns 7 in the Actual Training Sheet.='
                        if val_province == None:
                            msg+='<b>Province '+str(sheet_row[7].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 8 in the Actual Training Sheet.='
                        if val_city == None :
                            msg+='<b>City '+str(sheet_row[8].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 9 in the Actual Training Sheet.='
                        if val_urban == '':
                            msg+='<b>Urban/Rural '+str(sheet_row[9].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 10 in the Actual Training Sheet.='
                        if val_socio == '':
                            msg+='<b>Employed/UnEmployed '+str(sheet_row[10].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 11 in the Actual Training Sheet.='
                        if val_training_type == 'non-pivotal' and val_socio == 'unemployed' :
                            msg+='<b>Socio Economic Status should not be Unemployed for NonPivotal Type of Training, Found at row <b>'+str(count+1)+'</b> and columns 11 in the Actual Training Sheet.='
                        if val_type_training == None:
                            msg+='<b>Type of Training Intervention '+str(sheet_row[11].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 12 in the Actual Training Sheet.='
                        #if str(sheet_row[12].value).isdigit() == True:
                        #    msg+='<b>Other Type Of Training Intervention '+sheet_row[12].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 13 in the Actual Training Sheet.='
                        if sheet_row[13].value == '':
                            msg+='<b>Name of training Intervention '+str(sheet_row[13].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 14 in the Actual Training Sheet.='
#                         if val_type_training1 == None:
#                             msg+='<b>Pivotal programme Type '+sheet_row[14].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 15 in the Actual Training Sheet.='
                        if (sheet_row[15].value == '' or  sheet_row[15].value ==' ') and (sheet_row[0].value =='Pivotal'):
                            msg+='<b>Pivotal Programme Qualification '+str(sheet_row[15].value).encode('utf-8')+'</b> should not be blank, not integer or float. Found at row <b>'+str(count+1)+'</b> and columns 16 in the Actual Training Sheet.='
                        if (sheet_row[16].value == '' or  sheet_row[16].value ==' ') and (sheet_row[0].value =='Pivotal'):
                            msg+='<b>Pivotal Programme Institution '+str(sheet_row[16].value).encode('utf-8')+'</b> should not be blank, not integer or float. Found at row <b>'+str(count+1)+'</b> and columns 17 in the Actual Training Sheet.='
                        try:
                            if float(sheet_row[17].value) == 0 or type(float(sheet_row[17].value)) != float and (sheet_row[17].value == '' or (sheet_row[17].value).isdigit() == False):
                                check_cost_atr = False
                                msg+='<b>Cost '+str(sheet_row[17].value)+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 18 in the Actual Training Sheet.='
                        except:
                            check_cost_atr = False
                            msg+='<b>Cost '+str(sheet_row[17].value)+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 18 in the Actual Training Sheet.='
#                         if re.search('[a-zA-Z]', str(start_date)) :
#                             msg+='<b>AET Start Date '+str(sheet_row[18].value)+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 19 in the Actual Training Sheet.='
#                         if re.search('[a-zA-Z]', str(end_date)) :
#                             msg+='<b>AET End Date '+str(sheet_row[19].value)+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 20 in the Actual Training Sheet.='
                        if val_nqf_aligned == '':
                            msg+='<b>NQF Aligned '+str(sheet_row[20].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 21 in the Actual Training Sheet.='
                        if val_nqf_aligned == 'yes' and val_nqf_level == '':
                            msg+='<b>NQF Level '+str(sheet_row[21].value)+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 22 in the Actual Training Sheet.='
                        if not type(val_population) == str or val_population == '':
                            msg+='<b>Race '+str(sheet_row[22].value).encode('utf-8')+'</b> should be any one string from African/Coloured/Indian/White. Found at row <b>'+str(count+1)+'</b> and columns 23 in the Actual Training Sheet.='
                        if not type(val_genders) == str or val_genders == '':
                            msg+='<b>Gender '+str(sheet_row[23].value).encode('utf-8')+'</b> should be string as either M - Male or F - Female. Found at row <b>'+str(count+1)+'</b> and columns 24 in the Actual Training Sheet.='
                        if not type(val_disability) == str or val_disability == '':
                            msg+='<b>Disability '+str(sheet_row[24].value).encode('utf-8')+'</b> should be string as either Yes or No . Found at row <b>'+str(count+1)+'</b> and columns 25 in the Actual Training Sheet.='
                        ## Validation for Actual Training ends.
                        ## Dictionary for Actual Training.
                        actual_training_dict = {}
                        if not val_ofo_code is None and not val_training_type is '' \
                        and not val_occupation is None and not val_province is None \
                        and not val_city is None and not val_urban is '' and not (val_training_type == 'non-pivotal' and val_socio == 'unemployed')\
                        and not val_socio is '' and not val_type_training is None \
                        and not val_nqf_aligned == '' and not (val_nqf_aligned == 'yes' and val_nqf_level == '') \
                        and not val_population == '' and not val_genders == '' and not val_disability == '' \
                        and not sheet_row[17].value == '' and check_cost_atr == True\
                        and not (type(sheet_row[18].value) == str or re.search('[a-zA-Z]', str(sheet_row[18].value)))\
                        and not (type(sheet_row[19].value) == str or re.search('[a-zA-Z]', str(sheet_row[19].value)))\
                        and not (sheet_row[13].value == '') and (not ((sheet_row[15].value == '' or  sheet_row[15].value ==' ') and (sheet_row[0].value =='Pivotal')) or (sheet_row[0].value =='NonPivotal')) and (not ((sheet_row[16].value == '' or  sheet_row[16].value ==' ') and (sheet_row[0].value =='Pivotal')) or (sheet_row[0].value =='NonPivotal')):
                            self._cr.execute("insert into actual_training_fields (training_type,name,surname,employee_id,code,occupation, specialization, learner_province, city_id, urban, socio_economic_status, type_training,other_type_of_intervention,name_training,pivotal_programme_qualification,pivotal_programme_institution, training_cost, start_date, end_date,nqf_aligned, nqf_level, population_group,gender,dissability,actual_wsp_id) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                             (val_training_type,sheet_row[1].value,sheet_row[2].value,val_id_number,val_ofo_code,val_occupation , val_specialisation, val_province, val_city, val_urban, val_socio, val_type_training,sheet_row[12].value,sheet_row[13].value,sheet_row[15].value,sheet_row[16].value,sheet_row[17].value,start_date,end_date, val_nqf_aligned, val_nqf_level,val_population,val_genders,val_disability, wsp_plan_data.id))
                        else:
                            actual_training_list.append([sheet_row[0].value,sheet_row[1].value,sheet_row[2].value,sheet_row[3].value,sheet_row[4].value,sheet_row[5].value,sheet_row[6].value,sheet_row[7].value,sheet_row[8].value,sheet_row[9].value,sheet_row[10].value,sheet_row[11].value,sheet_row[12].value,sheet_row[13].value,sheet_row[14].value,sheet_row[15].value,sheet_row[16].value,sheet_row[17].value,str(start_date)[8:10]+"/"+str(start_date)[5:7]+"/"+str(start_date)[:4],str(end_date)[8:10]+"/"+str(end_date)[5:7]+"/"+str(end_date)[:4],sheet_row[20].value,sheet_row[21].value,sheet_row[22].value,sheet_row[23].value,sheet_row[24].value])
                
                    # Loading Actual Adult Education and Training Data.
                    if count > 0 and sheet_count == 2 and blank_row > 0:
#                         start_date = ''
#                         if sheet_row[9].value :
#                             start_date = datetime.datetime(*xlrd.xldate_as_tuple(sheet_row[9].value, excel.datemode)).date()
#                         end_date = ''
#                         if sheet_row[10].value :
#                             end_date = datetime.datetime(*xlrd.xldate_as_tuple(sheet_row[10].value, excel.datemode)).date()
                        start_date = self.validate_date(sheet_row[9].value, excel)
                        end_date = self.validate_date(sheet_row[10].value, excel)
                        ## Validating Actual Adult Education and Training Excel Sheet file for Invalid data
                        val_population = self.get_population_group(sheet_row[3].value)
                        val_genders = self.get_genders(sheet_row[4].value)
                        val_dissability_status = self.get_disability_status(sheet_row[5].value)
                        val_province = self.get_province(sheet_row[6].value)
#                         val_suburb = self.get_suburb(sheet_row[7].value)
#                         val_municipality = self.get_municipality(sheet_row[7].value)
                        val_city = self.get_city(sheet_row[7].value)
                        val_urban = self.get_urban_rural(sheet_row[8].value)
                        val_aet_level = self.get_aet_level(sheet_row[12].value)
                        val_aet_subject = self.get_multiple_aet_subject(sheet_row[13].value)
                        val_id_number = self.validate_id_number(sheet_row[2].value)
                        
                        if sheet_row[0].value == '':
                            msg+='<b>Name '+str(sheet_row[0].value).encode('utf-8')+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 1 in the Actual Adult Education and Training Sheet.='
                        if sheet_row[1].value == '':
                            msg+='<b>SurName '+str(sheet_row[1].value).encode('utf-8')+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 2 in the Actual Adult Education and Training Sheet.='
                        if val_id_number.isdigit() == True and len(val_id_number) != 13:
                            msg+='<b>Id Number '+sheet_row[2].value+'</b> length should be 13 digits. Found at row <b>'+str(count+1)+'</b> and columns 3 in the Actual Adult Education and Training Sheet.='
                        elif val_id_number == '':
                            msg+='<b>Id Number '+sheet_row[2].value+'</b> should not be blank. Found at row <b>'+str(count+1)+'</b> and columns 3 in the Actual Adult Education and Training Sheet.='
                        if val_population == '':
                            msg+='<b>Population Group '+str(sheet_row[3].value).encode('utf-8')+'</b> should be any one string from African/Coloured/Indian/White. Found at row <b>'+str(count+1)+'</b> and columns 4 in the Actual Adult Education and Training Sheet.='
                        if val_genders == '':
                            msg+='<b>Gender '+str(sheet_row[4].value).encode('utf-8')+'</b> should be string as either M - Male or F - Female. Found at row <b>'+str(count+1)+'</b> and columns 5 in the Actual Adult Education and Training Sheet.='
                        if val_dissability_status == '':
                            msg+='<b>Disability Status '+str(sheet_row[5].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 6 in the Actual Adult Education and Training Sheet.='
                        if val_province == None :
                            msg+='<b>Learner Province '+str(sheet_row[6].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 8 in the Actual Adult Education and Training Sheet.='
                        if val_city == None :
                            msg+='<b>City '+str(sheet_row[7].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 7 in the Actual Adult Education and Training Sheet.='
                        if val_urban == '':
                            msg+='<b>Urban/Rural '+str(sheet_row[8].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 9 in the Actual Adult Education and Training Sheet.='
                        if type(sheet_row[9].value) == str or sheet_row[9].value == '':
                            msg+='<b>AET Start Date '+str(sheet_row[9].value)+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 10 in the Actual Adult Education and Training Sheet.='
                        if type(sheet_row[10].value) == str or sheet_row[10].value == '':
                            msg+='<b>AET End Date '+str(sheet_row[10].value)+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 11 in the Actual Adult Education and Training Sheet.='
                        if sheet_row[11].value == '':
                            msg+='<b>Provider '+str(sheet_row[11].value).encode('utf-8')+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 12 in the Actual Adult Education and Training Sheet.='
                        if val_aet_level == '':
                            msg+='<b>AET Level '+str(sheet_row[12].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 13 in the Actual Adult Education and Training Sheet.='
                        if val_aet_subject == None:
                            msg+='<b>AET Subject '+str(sheet_row[13].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 14 in the Actual Adult Education and Training Sheet.='
                        
                        adult_education_training_dict = {}
                        if str(sheet_row[0].value).isdigit() == False and str(sheet_row[1].value).isdigit() == False\
                        and not val_population is '' and not val_genders is ''  and not val_dissability_status is ''\
                        and not val_province is None and not val_urban is None and not val_aet_level is '' and\
                        not val_aet_subject is None and not (val_id_number.isdigit() == True and len(val_id_number) != 13):
                                self._cr.execute("insert into actual_adult_education_fields (name, surname, id_number, population_group, gender, dissability_status_and_type, province, city_id, urban, start_date, end_date, provider, aet_level, actual_adult_wsp_id) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(sheet_row[0].value, sheet_row[1].value,val_id_number, val_population,val_genders,val_dissability_status, val_province, val_city, val_urban,start_date,end_date,sheet_row[11].value,val_aet_level, wsp_plan_data.id))
                                self._cr.execute("select max(id) from actual_adult_education_fields")
                                adult_education_id = self._cr.fetchone() 
                                for aet_subject_id in val_aet_subject :
                                    self._cr.execute("insert into aet_subject_rel(actual_adult_education_ids,aet_subject_id) values(%s,%s)",(adult_education_id[0],aet_subject_id)) 
                        else:
                            adult_education_training_list.append([sheet_row[0].value,sheet_row[1].value,sheet_row[2].value,sheet_row[3].value,sheet_row[4].value,sheet_row[5].value,sheet_row[6].value,sheet_row[7].value,sheet_row[8].value,sheet_row[9].value,sheet_row[10].value,sheet_row[11].value,sheet_row[12].value,sheet_row[13].value])
                    count += 1
            #This code is recently added out of for loop to show warning msg at once
            if msg :
                ##This code will write incorrect data into newly created xls file
                buffered = cStringIO.StringIO()
                workbook = xlsxwriter.Workbook(buffered)
                worksheet1 = workbook.add_worksheet('Actual Training')
                worksheet1.set_column(0, 40, 16)
                merge_format = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'})

                worksheet1.write('A1', 'Type Of Training',merge_format)
                worksheet1.write('B1', 'Name',merge_format)
                worksheet1.write('C1', 'Surname',merge_format)
                worksheet1.write('D1', 'Employee ID',merge_format)
                worksheet1.write('E1', 'OFO Code',merge_format)
                worksheet1.write('F1', 'Occupation',merge_format)
                worksheet1.write('G1', 'Specialisation',merge_format)
                worksheet1.write('H1', 'Province',merge_format)
                worksheet1.write('I1', 'City',merge_format)
                worksheet1.write('J1', 'Urban/Rural',merge_format)
                worksheet1.write('K1', 'Employed/UnEmployed',merge_format)
                worksheet1.write('L1', 'Type of Training Intervention',merge_format)
                worksheet1.write('M1', 'Other Type Of Training Intervention',merge_format)
                worksheet1.write('N1', 'Name of Training Intervention',merge_format)
                worksheet1.write('O1', 'Pivotal Programme Type',merge_format)
                worksheet1.write('P1', 'Pivotal Programme Qualification',merge_format)
                worksheet1.write('Q1', 'Pivotal Programme institution',merge_format)
                worksheet1.write('R1', 'Cost Per Learner',merge_format)
                worksheet1.write('S1', 'Start Date',merge_format)
                worksheet1.write('T1', 'End Date',merge_format)
                worksheet1.write('U1', 'NQF Aligned',merge_format)
                worksheet1.write('V1', 'NQF Level',merge_format)
                worksheet1.write('W1', 'Race',merge_format)
                worksheet1.write('X1', 'Gender',merge_format)
                worksheet1.write('Y1', 'Disability',merge_format)

                row = 1
                for l in actual_training_list:
                    col = 0
                    for e in l:
                        if e:
                            worksheet1.write(row, col, e)
                        col+=1
                    row+=1
                worksheet2 = workbook.add_worksheet('Adult Education And Training')
                worksheet2.set_column(0, 40, 16)                
                worksheet2.write('A1', 'First Name',merge_format)
                worksheet2.write('B1', 'SurName',merge_format)
                worksheet2.write('C1', 'Id Number',merge_format)
                worksheet2.write('D1', 'Population Group',merge_format)
                worksheet2.write('E1', 'Gender',merge_format)
                worksheet2.write('F1', 'Disability Status And Type',merge_format)
                worksheet2.write('G1', 'Learner Province',merge_format)
                worksheet2.write('H1', 'City',merge_format)
                worksheet2.write('I1', 'Urban/Rural',merge_format)
                worksheet2.write('J1', 'AET Start Date',merge_format)
                worksheet2.write('K1', 'AET End Date',merge_format)
                worksheet2.write('L1', 'Provider',merge_format)
                worksheet2.write('M1', 'AET Level',merge_format)
                worksheet2.write('N1', 'AET Subject',merge_format)
                row = 1
                for l in adult_education_training_list:
                    col = 0
                    for e in l:
                        if e:
                            worksheet2.write(row, col, e)
                        col+=1
                    row+=1
                workbook.close()
                xlsx_data = buffered.getvalue()
                out_data = base64.encodestring(xlsx_data)
                attachment_obj = self.env['ir.attachment']
                new_attach = attachment_obj.create({
                    'name':'Incorrect ATR.xlsx',
                    'res_name': 'wsp_import',
                    'type': 'binary',
                    'res_model': 'wsp.plan',
                    'datas':out_data,
                })
                self = self.with_context({'error_log_msg':msg,'incorrect_id':new_attach.id})
                return {
                            'name' : 'XLS Import Error Log',
                            'type' : 'ir.actions.act_window',
                            'view_type' : 'form',
                            'view_mode' : 'form',
                            'res_model' : 'xls.error.validation',
                            'target' : 'new',
                            'context' : self._context,
                        }                            

        ## This will be removed by next to next year. Planned 2015-2016
        if planned_current_csv_data :
            try:
                excel = xlrd.open_workbook(file_contents = planned_current_csv_data)  
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
                count = 0
                sheet_row = []
                while count < row_count:
                    sheet_row = xl_sheet.row(count)
                    #TODO: Later on we need to change the condition according to macro csv.
                    # Loading Planned 2015-2016 Training Data.
                    blank_row = 0
                    for col in sheet_row :
                        if col.value :
                            blank_row += 1
                    if count > 1 and sheet_count == 1 and blank_row > 0:
                        start_date = ''
                        if sheet_row[14].value :
                            start_date = datetime.datetime(*xlrd.xldate_as_tuple(sheet_row[14].value, excel.datemode)).date()
                        end_date = ''
                        if sheet_row[15].value :
                            end_date = datetime.datetime(*xlrd.xldate_as_tuple(sheet_row[15].value, excel.datemode)).date()
                        ## Validating Planned 2015-2016 Training for invalid occurances.
                        val_ofo_code = self.get_ofo_code(sheet_row[0].value)
                        val_training_type = self.get_training_type(sheet_row[1].value)
                        val_occupation = self.get_occupation(sheet_row[0].value,sheet_row[2].value)
                        specialisation_exists = self.check_specialisation_exists(val_ofo_code)
                        val_specialisation = self.get_specialization(sheet_row[0].value,sheet_row[3].value)
                        val_municipality = self.get_municipality(sheet_row[4].value)
                        val_urban = self.get_urban_rural(sheet_row[5].value)
                        val_province = self.get_province(sheet_row[6].value)
                        val_socio = self.get_socio_eco_status(sheet_row[7].value)
                        val_type_training = self.get_complete_type_of_training(sheet_row[8].value)
                        val_nqf_aligned = self.get_nqf_aligned(sheet_row[11].value)
                        val_nqf_level = self.get_nqf_level(sheet_row[12].value)
                        if val_ofo_code == None :
                            msg+='<b>OFO Code '+sheet_row[0].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 1 in the Planned Training Sheet.='
                        if val_training_type == '':
                            msg+='<b>Type of Training '+sheet_row[1].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 2 in the Planned Training Sheet.='
                        if val_occupation == None:
                            msg+='<b>Occupation '+sheet_row[2].value+'</b> should be linked with ofo code. Found at row <b>'+str(count+1)+'</b> and columns 3 in the Planned Training Sheet.='
                        if val_specialisation == None and specialisation_exists == True:
                            msg+='<b>Specialisation '+sheet_row[3].value+'</b> should be linked with ofo code. Found at row <b>'+str(count+1)+'</b> and columns 4 in the Planned Training Sheet.='
                        if val_municipality == None :
                            msg+='<b>Municipality '+sheet_row[4].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 5 in the Planned Training Sheet.='
                        if val_urban == '':
                            msg+='<b>Urban/Rural '+sheet_row[5].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 6 in the Planned Training Sheet.='
                        if val_province == None:
                            msg+='<b>Province '+sheet_row[6].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 7 in the Planned Training Sheet.='
                        if val_socio == '':
                            msg+='<b>Socio Economic Status '+sheet_row[7].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 8 in the Planned Training Sheet.='
                        if val_type_training == None:
                            msg+='<b>Type of Training Intervention/Pivotal Programme Type '+sheet_row[8].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 9 in the Planned Training Sheet.='
                        if str(sheet_row[9].value).isdigit() == True:
                            msg+='<b>Name of Training Intervention/Pivotal Programme Qualification '+sheet_row[9].value+'</b> should be string, not integer or float. Found at row <b>'+str(count+1)+'</b> and columns 10 in the Planned Training Sheet.='
                        if str(sheet_row[10].value).isdigit() == True:
                            msg+='<b>Pivotal Programme Institution '+sheet_row[10].value+'</b> should be string, not integer or float. Found at row <b>'+str(count+1)+'</b> and columns 11 in the Planned Training Sheet.='
                        if val_nqf_aligned == '':
                            msg+='<b>NQF Aligned '+sheet_row[11].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 12 in the Planned Training Sheet.='
                        if val_nqf_level == '':
                            msg+='<b>NQF Level '+sheet_row[12].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 13 in the Planned Training Sheet.='
                        try:
                            if type(float(sheet_row[13].value)) != float and (sheet_row[13].value == '' or (sheet_row[13].value).isdigit() == False):
                                msg+='<b>Cost '+sheet_row[13].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 14 in the Planned Training Sheet.='
                        except:
                            msg+='<b>Cost '+sheet_row[13].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 14 in the Planned Training Sheet.='
                        if type(sheet_row[14].value) == str:
                            msg+='<b>AET Start Date '+sheet_row[14].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 15 in the Planned Training Sheet.='
                        if type(sheet_row[15].value) == str:
                            msg+='<b>AET End Date '+sheet_row[15].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 16 in the Planned Training Sheet.='
                        if type(sheet_row[16].value) == str:
                            msg+='<b>AFRICAN M '+sheet_row[16].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 17 in the Planned Training Sheet.='
                        if int(sheet_row[16].value) < 0 :
                            msg+='<b>AFRICAN M '+sheet_row[16].value+'</b> should not be negative. Found at row <b>'+str(count+1)+'</b> and columns 17 in the Planned Training Sheet.='
                        if type(sheet_row[17].value) == str:
                            msg+='<b>AFRICAN F '+sheet_row[17].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 18 in the Planned Training Sheet.='
                        if int(sheet_row[17].value) < 0 :
                            msg+='<b>AFRICAN F '+sheet_row[17].value+'</b> should not be negative. Found at row <b>'+str(count+1)+'</b> and columns 18 in the Planned Training Sheet.='
                        if type(sheet_row[18].value) == str:
                            msg+='<b>AFRICAN D '+sheet_row[18].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 19 in the Planned Training Sheet.='
                        if int(sheet_row[18].value) < 0 :
                            msg+='<b>AFRICAN D '+sheet_row[18].value+'</b> should not be negative. Found at row <b>'+str(count+1)+'</b> and columns 19 in the Planned Training Sheet.='
                        if type(sheet_row[19].value) == str:
                            msg+='<b>COLOURED M '+sheet_row[19].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 20 in the Planned Training Sheet.='
                        if int(sheet_row[19].value) < 0 :
                            msg+='<b>COLOURED M '+sheet_row[19].value+'</b> should not be negative. Found at row <b>'+str(count+1)+'</b> and columns 20 in the Planned Training Sheet.='
                        if type(sheet_row[20].value) == str:
                            msg+='<b>COLOURED F '+sheet_row[20].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 21 in the Planned Training Sheet.='
                        if int(sheet_row[20].value) < 0 :
                            msg+='<b>COLOURED F '+sheet_row[20].value+'</b> should not be negative. Found at row <b>'+str(count+1)+'</b> and columns 21 in the Planned Training Sheet.='
                        if type(sheet_row[21].value) == str:
                            msg+='<b>COLOURED D '+sheet_row[21].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 22 in the Planned Training Sheet.='
                        if int(sheet_row[21].value) < 0 :
                            msg+='<b>COLOURED D '+sheet_row[21].value+'</b> should not be negative. Found at row <b>'+str(count+1)+'</b> and columns 22 in the Planned Training Sheet.='
                        if type(sheet_row[22].value) == str:
                            msg+='<b>INDIAN M '+sheet_row[22].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 23 in the Planned Training Sheet.='
                        if int(sheet_row[22].value) < 0 :
                            msg+='<b>INDIAN M '+sheet_row[22].value+'</b> should not be negative. Found at row <b>'+str(count+1)+'</b> and columns 23 in the Planned Training Sheet.='
                        if type(sheet_row[23].value) == str:
                            msg+='<b>INDIAN F '+sheet_row[23].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 24 in the Planned Training Sheet.='
                        if int(sheet_row[23].value) < 0 :
                            msg+='<b>INDIAN F '+sheet_row[23].value+'</b> should not be negative. Found at row <b>'+str(count+1)+'</b> and columns 24 in the Planned Training Sheet.='
                        if type(sheet_row[24].value) == str:
                            msg+='<b>INDIAN D '+sheet_row[24].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 25 in the Planned Training Sheet.='
                        if int(sheet_row[24].value) < 0 :
                            msg+='<b>INDIAN D '+sheet_row[24].value+'</b> should not be negative. Found at row <b>'+str(count+1)+'</b> and columns 25 in the Planned Training Sheet.='
                        if type(sheet_row[25].value) == str:
                            msg+='<b>WHITE M '+sheet_row[25].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 26 in the Planned Training Sheet.='
                        if int(sheet_row[25].value) < 0 :
                            msg+='<b>WHITE M '+sheet_row[25].value+'</b> should not be negative. Found at row <b>'+str(count+1)+'</b> and columns 26 in the Planned Training Sheet.='
                        if type(sheet_row[26].value) == str:
                            msg+='<b>WHITE F '+sheet_row[26].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 27 in the Planned Training Sheet.='
                        if int(sheet_row[26].value) < 0 :
                            msg+='<b>WHITE F '+sheet_row[26].value+'</b> should not be negative. Found at row <b>'+str(count+1)+'</b> and columns 27 in the Planned Training Sheet.='
                        if type(sheet_row[27].value) == str:
                            msg+='<b>WHITE D '+sheet_row[27].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 28 in the Planned Training Sheet.='
                        if int(sheet_row[27].value) < 0 :
                            msg+='<b>WHITE D '+sheet_row[27].value+'</b> should not be negative. Found at row <b>'+str(count+1)+'</b> and columns 28 in the Planned Training Sheet.='
                        if type(sheet_row[31].value) == str:
                            msg+='<b>AGE GROUP <35 '+sheet_row[31].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 32 in the Planned Training Sheet.='
                        if int(sheet_row[31].value) < 0 :
                            msg+='<b>AGE GROUP <35 '+sheet_row[31].value+'</b> should not be negative. Found at row <b>'+str(count+1)+'</b> and columns 32 in the Planned Training Sheet.='
                        if type(sheet_row[32].value) == str:
                            msg+='<b>AGE GROUP 35-55 '+sheet_row[32].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 33 in the Planned Training Sheet.='
                        if int(sheet_row[32].value) < 0 :
                            msg+='<b>AGE GROUP 35-55 '+sheet_row[32].value+'</b> should not be negative. Found at row <b>'+str(count+1)+'</b> and columns 33 in the Planned Training Sheet.='
                        if type(sheet_row[33].value) == str:
                            msg+='<b>AGE GROUP >55 '+sheet_row[33].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 34 in the Planned Training Sheet.='
                        if int(sheet_row[33].value) < 0 :
                            msg+='<b>AGE GROUP >55 '+sheet_row[33].value+'</b> should not be negative. Found at row <b>'+str(count+1)+'</b> and columns 34 in the Planned Training Sheet.='
                        if type(sheet_row[34].value) == str:
                            msg+='<b>Total Cost '+sheet_row[34].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 35 in the Planned Training Sheet.=' 
                        if int(sheet_row[34].value) < 0 :
                            msg+='<b>Total Cost '+sheet_row[34].value+'</b> should not be negative. Found at row <b>'+str(count+1)+'</b> and columns 35 in the Planned Training Sheet.='
                        if msg :
                            self = self.with_context({'error_log_msg':msg})
                            return {
                                        'name' : 'XLS Import Error Log',
                                        'type' : 'ir.actions.act_window',
                                        'view_type' : 'form',
                                        'view_mode' : 'form',
                                        'res_model' : 'xls.error.validation',
                                        'target' : 'new',
                                        'context' : self._context,
                                    }
                        ## Dictionary for Planned Current Training.
                        actual_training_dict = {
                                                'code' : val_ofo_code,
                                                'training_type' : val_training_type,
                                                'occupation' : val_occupation,
                                                'specialization' : val_specialisation,
                                                'municipality_id' : val_municipality,
                                                'urban' : val_urban,
                                                'learner_province' : val_province,
                                                'socio_economic_status' : val_socio,
                                                'type_training' : val_type_training,
                                                'name_training' : sheet_row[9].value,
                                                'pivotal_programme_institution' : sheet_row[10].value,
                                                'nqf_aligned' : val_nqf_aligned,
                                                'nqf_level' : val_nqf_level,
                                                'training_cost' : sheet_row[13].value,
                                                'start_date' : start_date,
                                                'end_date' : end_date,
                                                'african_male' : sheet_row[16].value,
                                                'african_female' : sheet_row[17].value,
                                                'african_dissabled' : sheet_row[18].value,
                                                'coloured_male' : sheet_row[19].value,
                                                'coloured_female' : sheet_row[20].value,
                                                'coloured_dissabled' : sheet_row[21].value,
                                                'indian_male' : sheet_row[22].value,
                                                'indian_female' : sheet_row[23].value,
                                                'indian_dissabled' : sheet_row[24].value,
                                                'white_male' : sheet_row[25].value,
                                                'white_female' : sheet_row[26].value,
                                                'white_dissabled' : sheet_row[27].value,
                                                'age_group_less' : sheet_row[31].value,
                                                'age_group_upto' : sheet_row[32].value,
                                                'age_group_greater' : sheet_row[33].value,
                                                'total_cost' : sheet_row[34].value,
                                                'actual_planned_wsp_id' : wsp_plan_data.id
                                                }
                        wsp_plan_data.write({'training_actual_planned_ids':[(0,0,actual_training_dict)]})
                    # Loading Planned Current Education and Training Data.
                    if count > 0 and sheet_count == 2 and blank_row > 0:
                        start_date = ''
                        if sheet_row[9].value :
                            start_date = datetime.datetime(*xlrd.xldate_as_tuple(sheet_row[9].value, excel.datemode)).date()
                        end_date = ''
                        if sheet_row[10].value :
                            end_date = datetime.datetime(*xlrd.xldate_as_tuple(sheet_row[10].value, excel.datemode)).date()
                        ## Validating Planned Adult Education and Training 2015-2016 WSP for invalid occurances.
                        val_population = self.get_population_group(sheet_row[3].value)
                        val_genders = self.get_genders(sheet_row[4].value)
                        val_dissability_status = self.get_disability_status(sheet_row[5].value)
                        val_municipality = self.get_municipality(sheet_row[6].value)
                        val_province = self.get_province(sheet_row[7].value)
                        val_urban = self.get_urban_rural(sheet_row[8].value)
                        val_aet_level = self.get_aet_level(sheet_row[12].value)
                        val_aet_subject = self.get_aet_subject(sheet_row[13].value)
                        if str(sheet_row[0].value).isdigit() == True:
                            msg+='<b>Name '+sheet_row[0].value+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 1 in the Planned Adult Education and Training Sheet.='
                        if str(sheet_row[1].value).isdigit() == True:
                            msg+='<b>SurName '+sheet_row[1].value+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 2 in the Planned Adult Education and Training Sheet.='
#                         if str(sheet_row[2].value).isdigit() == True:
#                             msg+='<b>Id Number '+sheet_row[2].value+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 3 in the Planned Adult Education and Training Sheet.='
                        if val_population == '':
                            msg+='<b>Population Group '+sheet_row[3].value+'</b> should be any one string from African/Coloured/Indian/White. Found at row <b>'+str(count+1)+'</b> and columns 4 in the Planned Adult Education and Training Sheet.='
                        if val_genders == '':
                            msg+='<b>Gender '+sheet_row[4].value+'</b> should be string as either M - Male or F - Female. Found at row <b>'+str(count+1)+'</b> and columns 5 in the Planned Adult Education and Training Sheet.='
                        if val_dissability_status == '':
                            msg+='<b>Disability Status '+sheet_row[5].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 6 in the Planned Adult Education and Training Sheet.='
                        if val_municipality == None :
                            msg+='<b>Municipality '+sheet_row[6].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 7 in the Planned Adult Education and Training Sheet.='
                        if val_province == None :
                            msg+='<b>Learner Province '+sheet_row[7].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 8 in the Planned Adult Education and Training Sheet.='
                        if val_urban == '':
                            msg+='<b>Urban/Rural '+sheet_row[8].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 9 in the Planned Adult Education and Training Sheet.='
                        if type(sheet_row[9].value) == str:
                            msg+='<b>AET Start Date '+sheet_row[9].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 10 in the Planned Adult Education and Training Sheet.='
                        if type(sheet_row[10].value) == str:
                            msg+='<b>AET End Date '+sheet_row[10].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 11 in the Planned Adult Education and Training Sheet.='
                        if str(sheet_row[11].value).isdigit() == True :
                            msg+='<b>Provider '+sheet_row[11].value+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 12 in the Planned Adult Education and Training Sheet.='
                        if val_aet_level == '':
                            msg+='<b>AET Level '+sheet_row[12].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 13 in the Planned Adult Education and Training Sheet.='
                        if val_aet_subject == '':
                            msg+='<b>AET Subject '+sheet_row[13].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 14 in the Planned Adult Education and Training Sheet.='
                        if msg :
                            self = self.with_context({'error_log_msg':msg})
                            return {
                                        'name' : 'XLS Import Error Log',
                                        'type' : 'ir.actions.act_window',
                                        'view_type' : 'form',
                                        'view_mode' : 'form',
                                        'res_model' : 'xls.error.validation',
                                        'target' : 'new',
                                        'context' : self._context,
                                    }
                        adult_education_training_dict = {
                                                        'name' : sheet_row[0].value,
                                                        'surname' : sheet_row[1].value,
                                                        'id_number' : sheet_row[2].value,
                                                        'population_group' : val_population,
                                                        'gender' : val_genders,
                                                        'dissability_status_and_type' : val_dissability_status,
                                                        'municipality_id' : val_municipality,
                                                        'province' : val_province,
                                                        'urban' : val_urban,
                                                        'start_date' : start_date,
                                                        'end_date' : end_date,
                                                        'provider' : sheet_row[11].value,
                                                        'aet_level' : val_aet_level,
                                                        'aet_subject' : val_aet_subject,
                                                        'actual_planned_adult_wsp_id' : wsp_plan_data.id
                                                         }
                        wsp_plan_data.write({'actual_planned_adult_education_ids':[(0,0,adult_education_training_dict)]})
                    count += 1
        ## For Planned
        #msg = ''
        total_employment_list = []
        planned_training_list = []
        planned_adult_education_list = []
        scarce_and_critical_list = []
        if planned_csv_data :
            try:
                excel = xlrd.open_workbook(file_contents = planned_csv_data)  
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
                count = 0
                sheet_row = []
                while count < row_count:
                    sheet_row = xl_sheet.row(count)
                    blank_row = 0
                    for col in sheet_row :
                        if col.value :
                            blank_row += 1
                    ## Loading Total Employment Profile
                    if count > 0 and sheet_count == 1 and blank_row > 0:
                        ## ID Type
                        id_type = ''
                        if sheet_row[5].value == 'ID Document':
                            id_type = 'id_document'
                        if sheet_row[5].value == 'Passport':
                            id_type = 'passport'
                        if not re.search('[a-zA-Z]', str(sheet_row[6].value)) :
                            birth_date = self.validate_date(sheet_row[6].value, excel)
                        else:
                            birth_date = str(sheet_row[6].value)
                        ## Validating Planned Total Employment Profile Training for invalid occurances.
#                         sdl_number = wsp_plan_data.employer_id and wsp_plan_data.employer_id.employer_sdl_no
                        
                        sdl_no = None
                        if str(type(sheet_row[0].value)) == "<type 'unicode'>":
                            sdl_no = unicodedata.normalize('NFKD', sheet_row[0].value).encode('ascii','ignore')
                        else:
                            sdl_no = str(sheet_row[0].value).encode('utf-8')
                            
                        sdl_number_data = self.env['employer.sdl.no'].search([('name', '=', sdl_no.strip())])
                        val_citizen_status = self.get_citizen_status(sheet_row[3].value)
                        val_ofo_code = self.get_ofo_code(sheet_row[7].value)
                        val_occupation = self.get_occupation(sheet_row[7].value,sheet_row[8].value)
                        specialisation_exists = self.check_specialisation_exists(val_ofo_code)
                        val_specialisation = self.get_specialization(sheet_row[7].value,sheet_row[9].value)
#                         val_municipality = self.get_municipality(sheet_row[10].value)
                        val_province = self.get_province(sheet_row[10].value)
#                         val_suburb = self.get_suburb(sheet_row[11].value)
                        val_city = self.get_city(sheet_row[11].value)
                        val_urban = self.get_urban_rural(sheet_row[12].value)
                        val_highest_edu = self.get_highest_edu(sheet_row[13].value)
                        val_population = self.get_population_group(sheet_row[14].value)
                        val_genders = self.get_genders(sheet_row[15].value)
                        val_disability = self.get_disability(sheet_row[16].value)
                        ## Validating ID Number since id number coming as sometime unicode or sometime float.
                        val_id_number = self.validate_id_number(sheet_row[4].value)
                        if not sdl_number_data :
                            msg+='<b>SDL Number '+str(sheet_row[0].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 1 in the Planned Total Employment Profile Sheet.='
                        if sheet_row[1].value == '':
                            msg+='<b>Name '+str(sheet_row[1].value).encode('utf-8')+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 2 in the Planned Total Employment Profile Sheet.='
                        if sheet_row[2].value == '':
                            msg+='<b>SurName '+str(sheet_row[2].value).encode('utf-8')+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 3 in the Planned Total Employment Profile Sheet.='
                        if val_citizen_status == '':
                            msg+='<b>Citizen Status '+str(sheet_row[3].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 4 in the Planned Total Employment Profile Sheet.='
                        
                        if (val_citizen_status == 'sa' and len(val_id_number) != 13 and val_id_number.isdigit() == True) or (val_citizen_status != 'sa' and val_id_number.isalnum() == False) or (val_id_number == ''):
                            msg+='<b>Employee Id '+str(val_id_number)+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 5 in the Planned Total Employment Profile Sheet.='
                        if id_type == '':
                            msg+='<b>ID Type '+str(sheet_row[5].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 6 in the Planned Total Employment Profile Sheet.='
                        if type(sheet_row[6].value) == str or re.search('[a-zA-Z]', str(sheet_row[6].value)) :
                            msg+='<b>Date Of Birth '+sheet_row[6].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 7 in the Planned Total Employment Profile Sheet.='
                        if val_ofo_code == None :
                            ofo = sheet_row[7].value
                            if type(sheet_row[7].value) == float:
                                ofo = str(sheet_row[7].value)
                            msg+='<b>OFO Code '+ofo+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 8 in the Planned Total Employment Profile Sheet.='
                        if val_occupation == None :
                            msg+='<b>Occupation '+str(sheet_row[8].value).encode('utf-8')+'</b> should be linked with ofo code. Found at row <b>'+str(count+1)+'</b> and columns 9 in the Planned Total Employment Profile Sheet.='
                        if val_specialisation == None and specialisation_exists == True:
                            msg+='<b>Specialisation '+str(sheet_row[9].value).encode('utf-8')+'</b> should be linked with ofo code. Found at row <b>'+str(count+1)+'</b> and columns 10 in the Planned Total Employment Profile Sheet.='
                        if val_province == None :
                            msg+='<b>Province '+str(sheet_row[10].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 11 in the Planned Total Employment Profile Sheet.='
                        if val_city == None :
                            msg+='<b>City '+str(sheet_row[11].value.encode('utf-8'))+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 12 in the Planned Total Employment Profile Sheet.='
                        if val_urban == '':
                            msg+='<b>Urban/Rural '+str(sheet_row[12].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 13 in the Planned Total Employment Profile Sheet.='
                        if val_highest_edu == '':
                            msg+='<b>Highest Education Level '+str(sheet_row[13].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 14 in the Planned Total Employment Profile Sheet.='
                        if val_population == '':
                            msg+='<b>Race '+str(sheet_row[14].value).encode('utf-8')+'</b> should be any one string from African/Coloured/Indian/White. Found at row <b>'+str(count+1)+'</b> and columns 15 in the Planned Total Employment Profile Sheet.='
                        if val_genders == '':
                            msg+='<b>Gender '+str(sheet_row[15].value).encode('utf-8')+'</b> should be string as either M - Male or F - Female. Found at row <b>'+str(count+1)+'</b> and columns 16 in the Planned Total Employment Profile Sheet.='
                        if val_disability == '':
                            msg+='<b>Disability '+str(sheet_row[16].value).encode('utf-8')+'</b> should be string as either Yes or No. Found at row <b>'+str(count+1)+'</b> and columns 17 in the Planned Total Employment Profile Sheet.='
                        specialisation_exists=False
                        if val_specialisation:
                            specialisation_exists=True
                        if sdl_number_data and not sheet_row[1].value == '' and not sheet_row[2].value == '' \
                        and not val_citizen_status == '' and not id_type == '' and not (type(sheet_row[6].value) == str or re.search('[a-zA-Z]', str(sheet_row[6].value)))\
                        and not val_ofo_code == None and not val_occupation == None and not val_province == None \
                        and not val_city == None and not val_urban == '' and not val_highest_edu == '' and \
                        not val_population == '' and not val_genders == '' and not val_disability == '' and \
                         not (val_citizen_status == 'sa' and len(val_id_number) != 13 and val_id_number.isdigit() == True) or (val_citizen_status != 'sa' and val_id_number.isalnum() == False) or (val_id_number == ''):  
                            self._cr.execute("insert into total_employment_profile_fields (sdl_number, name, surname, citizen_resident_status_code, employee_id, id_type, dob, ofo_code, occupation, specialization, province, city_id, urban, highest_education_level, population_group, gender, dissability, total_employment_wsp_id) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(sdl_number_data.id,sheet_row[1].value, sheet_row[2].value, val_citizen_status, val_id_number, id_type, birth_date, val_ofo_code, val_occupation, val_specialisation, val_province, val_city, val_urban, val_highest_edu, val_population, val_genders, val_disability,wsp_plan_data.id ))
                        else:
                            total_employment_list.append([sheet_row[0].value,sheet_row[1].value,sheet_row[2].value,sheet_row[3].value,sheet_row[4].value,sheet_row[5].value,str(birth_date)[8:10]+"/"+str(birth_date)[5:7]+"/"+str(birth_date)[:4],sheet_row[7].value,sheet_row[8].value,sheet_row[9].value,sheet_row[10].value,sheet_row[11].value,sheet_row[12].value,sheet_row[13].value or '0',sheet_row[14].value,sheet_row[15].value,sheet_row[16].value])
                            
                    ## Loading Planned Training
                    if count > 0 and sheet_count == 2 and blank_row > 0:
#                         start_date = ''
                        check_cost_wsp = True
                        try:
                            if not re.search('[a-zA-Z]', str(sheet_row[18].value)) :
                                start_date = self.validate_date(sheet_row[18].value, excel)
                            else:
                                start_date = str(sheet_row[18].value)
                        except:
                            start_date = str(sheet_row[18].value)
                        try:
                            if not re.search('[a-zA-Z]', str(sheet_row[19].value)) :
                                end_date = self.validate_date(sheet_row[19].value, excel)
                            else:
                                end_date = str(sheet_row[19].value)
                        except:
                            end_date = str(sheet_row[19].value)
                        ## Validating Planned Training for invalid occurances.
                        val_training_type = self.get_training_type(sheet_row[0].value)
                        
                        val_ofo_code = self.get_ofo_code(sheet_row[4].value)
                        val_occupation = self.get_occupation(sheet_row[4].value,sheet_row[5].value)
                        specialisation_exists = self.check_specialisation_exists(val_ofo_code)
                        val_specialisation = self.get_specialization(sheet_row[4].value,sheet_row[6].value)
                        val_province = self.get_province(sheet_row[7].value)
                        val_city = self.get_city(sheet_row[8].value)
                        val_urban = self.get_urban_rural(sheet_row[9].value)
                        
                        val_socio = self.get_socio_eco_status(sheet_row[10].value)
                        val_type_training = self.get_complete_type_of_training(sheet_row[11].value)
#                         val_pivotal_programme_type = self.get_pivotal_programme_type(sheet_row[14].value)
                        val_nqf_aligned = self.get_nqf_aligned(sheet_row[20].value)
                        val_nqf_level = self.get_nqf_level(sheet_row[21].value)
                        val_population = self.get_population_group(sheet_row[22].value)
                        val_genders = self.get_genders(sheet_row[23].value)
                        val_disability = self.get_disability(sheet_row[24].value)
                        val_id_number = self.validate_id_number(sheet_row[3].value)
                        if val_training_type == '':
                            msg+='<b>Type Of Training '+str(sheet_row[0].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 1 in the Planned Training Sheet.='
                        if val_socio == 'employed' and sheet_row[1].value == '':
                            msg+='<b>Name '+str(sheet_row[1].value).encode('utf-8')+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 2 in the Planned Training Sheet.='
                        if val_socio == 'employed' and sheet_row[2].value == '':
                            msg+='<b>Sur Name '+str(sheet_row[2].value).encode('utf-8')+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 3 in the Planned Training Sheet.='
                        if val_id_number.isdigit() == True and len(val_id_number) != 13:
                            msg+='<b>Employee Id '+str(val_id_number)+'</b> length should be 13 digits. Found at row <b>'+str(count+1)+'</b> and columns 4 in the Planned Training Sheet.='
                        elif val_id_number == '' and val_training_type == 'non-pivotal':
                            msg+='<b>Employee Id '+str(val_id_number)+'</b> should not be blank if Type of Training is NonPivotal. Found at row <b>'+str(count+1)+'</b> and columns 4 in the Planned Training Sheet.='
                        if val_ofo_code == None :
                            msg+='<b>OFO Code '+str(sheet_row[4].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 5 in the Planned Training Sheet.='
                        if val_occupation == None:
                            msg+='<b>Occupation '+str(sheet_row[5].value).encode('utf-8')+'</b> should be linked with ofo code. Found at row <b>'+str(count+1)+'</b> and columns 6 in the Planned Training Sheet.='
                        if val_specialisation == None and specialisation_exists == True:
                            msg+='<b>Specialization '+str(sheet_row[6].value).encode('utf-8')+'</b> should be linked with ofo code. Found at row <b>'+str(count+1)+'</b> and columns 7 in the Planned Training Sheet.='
                        if val_province == None :
                            msg+='<b>Province '+str(sheet_row[7].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 8 in the Planned Training Sheet.='
                        if val_city == None:
                            msg+='<b>City '+str(sheet_row[8].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 9 in the Planned Training Sheet.='
                        if val_urban == '':
                            msg+='<b>Urban/Rural '+str(sheet_row[9].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 10 in the Planned Training Sheet.='
                        if val_socio == '':
                            msg+='<b>Employeed/UnEmployeed '+str(sheet_row[10].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 11 in the Planned Training Sheet.='
                        
                        if val_training_type == 'non-pivotal' and val_socio == 'unemployed' :
                            msg+='<b>Socio Economic Status should not be Unemployed for NonPivotal Type of Training, Found at row <b>'+str(count+1)+'</b> and columns 11 in the Planned Training Sheet.='

                        if val_type_training == None:
                            msg+='<b>Type of Training Intervention '+str(sheet_row[11].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 12 in the Planned Training Sheet.='
                        #if sheet_row[12].value == '':
                        #    msg+='<b>Other Type Of Training Intervention '+sheet_row[12].value+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 13 in the Planned Training Sheet.='
                        if sheet_row[13].value == '':
                            msg+='<b>Name Of Training Intervention '+str(sheet_row[13].value).encode('utf-8')+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 14 in the Planned Training Sheet.='
#                         if val_pivotal_programme_type == '':
#                             msg+='<b>Pivotal Programme Type '+sheet_row[14].value+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 15 in the Planned Training Sheet.='
                        if (sheet_row[15].value == '') and (sheet_row[0].value =='Pivotal') :
                            msg+='<b>Pivotal Programme Qualification '+str(sheet_row[15].value).encode('utf-8')+'</b> should not be blank. Found at row <b>'+str(count+1)+'</b> and columns 15 in the Planned Training Sheet.='
                        if (sheet_row[16].value == '') and (sheet_row[0].value =='Pivotal'):
                            msg+='<b>Pivotal Programme Institution '+str(sheet_row[16].value).encode('utf-8')+'</b> should not be blank. Found at row <b>'+str(count+1)+'</b> and columns 16 in the Planned Training Sheet.='
                        #if sheet_row[17].value == '':
                        #    raise Warning(_('Cost Per Learner %s is invalid. Found at row %s and column 17 in the Planned Training Sheet.')%(sheet_row[17].value,str(count+1)))
                        try:
                            if sheet_row[17].value == '' or float(sheet_row[17].value) == 0 or type(float(sheet_row[17].value)) != float and (sheet_row[17].value == '' or (sheet_row[17].value).isdigit() == False):
                                check_cost_wsp = False
                                msg+='<b>Cost Per Learner '+str(sheet_row[17].value)+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 17 in the Planned Training Sheet.='
                        except:
                            check_cost_wsp = False
                            msg+='<b>Cost Per Learner '+str(sheet_row[17].value)+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 17 in the Planned Training Sheet.='
                        
                        if type(sheet_row[18].value) == str or re.search('[a-zA-Z]', str(sheet_row[18].value)) :
                            msg+='<b>Start Date '+sheet_row[18].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 18 in the Planned Training Sheet.='
                        if type(sheet_row[19].value) == str or re.search('[a-zA-Z]', str(sheet_row[19].value)) :
                            msg+='<b>End Date '+sheet_row[19].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 19 in the Planned Training Sheet.='
                        if val_nqf_aligned == '':
                            msg+='<b>NQF Aligned '+str(sheet_row[20].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 20 in the Planned Training Sheet.='
                        if val_nqf_aligned == 'yes' and val_nqf_level == '':
                            msg+='<b>NQF Level '+str(sheet_row[21].value)+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 21 in the Planned Training Sheet.='
                        if val_population == '':
                            msg+='<b>Race '+str(sheet_row[22].value).encode('utf-8')+'</b> should be any one string from African/Coloured/Indian/White. Found at row <b>'+str(count+1)+'</b> and columns 22 in the Planned Training Sheet.='
                        if val_genders == '':
                            msg+='<b>Gender '+str(sheet_row[23].value).encode('utf-8')+'</b> should be string as either M - Male or F - Female. Found at row <b>'+str(count+1)+'</b> and columns 23 in the Planned Training Sheet.='
                        if val_disability == '':
                            msg+='<b>Disability '+str(sheet_row[24].value).encode('utf-8')+'</b> should be string as either Yes or No. Found at row <b>'+str(count+1)+'</b> and columns 24 in the Planned Training Sheet.='
                        if not val_training_type == '' and not (val_socio == 'employed' and sheet_row[1].value == '') and \
                        not (val_socio == 'employed' and sheet_row[2].value == '') and not (val_id_number.isdigit() == True and len(val_id_number) != 13)\
                        and not (val_id_number == '' and val_training_type == 'non-pivotal')\
                        and not val_ofo_code == None \
                        and not val_occupation == None and not (val_specialisation == None and specialisation_exists == True) \
                        and not val_province == None and not val_city == None and not val_urban == '' and not val_socio == ''\
                        and not (val_training_type == 'non-pivotal' and val_socio == 'unemployed' ) \
                        and not val_type_training == None and not sheet_row[13].value == ''\
                        and not sheet_row[17].value == '' and check_cost_wsp == True \
                        and (not ((sheet_row[15].value == '' or  sheet_row[15].value ==' ') and (sheet_row[0].value =='Pivotal')) or (sheet_row[0].value =='NonPivotal')) and (not ((sheet_row[16].value == '' or  sheet_row[16].value ==' ') and (sheet_row[0].value =='Pivotal')) or (sheet_row[0].value =='NonPivotal')) \
                        and not (type(start_date) == str or re.search('[a-zA-Z]', str(start_date))) and \
                        not (type(end_date) == str or re.search('[a-zA-Z]', str(end_date))) and not val_nqf_aligned == '' and not (val_nqf_aligned == 'yes' and val_nqf_level == '')\
                        and not val_population == '' and not val_genders == '' and not val_disability == '':
                            self._cr.execute("insert into planned_training_fields (training_type, name, surname, employee_id, code, occupation, specialization, learner_province, city_id, urban, socio_economic_status, type_training, other_type_of_intervention, name_training, pivotal_programme_qualification, pivotal_programme_institution, training_cost, start_date, end_date, nqf_aligned, nqf_level, population_group, gender, dissability, planned_training_non_wsp_id) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(val_training_type,sheet_row[1].value, sheet_row[2].value, val_id_number, val_ofo_code, val_occupation, val_specialisation, val_province, val_city, val_urban, val_socio, val_type_training, sheet_row[12].value, sheet_row[13].value, sheet_row[15].value, sheet_row[16].value,sheet_row[17].value, start_date, end_date, val_nqf_aligned, val_nqf_level, val_population, val_genders, val_disability, wsp_plan_data.id))
                        else:
                            planned_training_list.append([sheet_row[0].value,sheet_row[1].value,sheet_row[2].value,sheet_row[3].value,sheet_row[4].value,sheet_row[5].value,sheet_row[6].value,sheet_row[7].value,sheet_row[8].value,sheet_row[9].value,sheet_row[10].value,sheet_row[11].value,sheet_row[12].value,sheet_row[13].value,sheet_row[14].value,sheet_row[15].value,sheet_row[16].value,sheet_row[17].value,str(start_date)[8:10]+"/"+str(start_date)[5:7]+"/"+str(start_date)[:4],str(end_date)[8:10]+"/"+str(end_date)[5:7]+"/"+str(end_date)[:4],sheet_row[20].value,sheet_row[21].value,sheet_row[22].value,sheet_row[23].value,sheet_row[24].value])
                    ## Loading Planned Adult Education Training
                    if count > 0 and sheet_count == 3 and blank_row > 0:
                        try:
                            if not re.search('[a-zA-Z]',str(sheet_row[9].value)) :
                                start_date = self.validate_date(sheet_row[9].value, excel)
                            else:
                                start_date = str(sheet_row[9].value)
                        except:
                            start_date = str(sheet_row[9].value)

                        try:
                            if not re.search('[a-zA-Z]', str(sheet_row[10].value)) :
                                end_date = self.validate_date(sheet_row[10].value, excel)
                            else:
                                end_date = str(sheet_row[10].value)
                        except:
                            end_date = str(sheet_row[10].value)    
                            
                        ## Validating Planned Adult Education and Training sheet for invalid occurances.
                        val_population = self.get_population_group(sheet_row[3].value)
                        val_genders = self.get_genders(sheet_row[4].value)
                        val_disability_status = self.get_disability_status(sheet_row[5].value)
                        val_province = self.get_province(sheet_row[6].value)
                        val_city = self.get_city(sheet_row[7].value)
                        val_urban = self.get_urban_rural(sheet_row[8].value)
                        val_aet_level = self.get_aet_level(sheet_row[12].value)
                        val_aet_subject = self.get_multiple_aet_subject(sheet_row[13].value)
                        val_id_number = self.validate_id_number(sheet_row[2].value)
                        
                        if sheet_row[0].value == '':
                            msg+='<b>Name '+str(sheet_row[0].value).encode('utf-8')+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 1 in the Planned Adult Education and Training Sheet.='
                        if sheet_row[1].value == '':
                            msg+='<b>Sur Name '+str(sheet_row[1].value).encode('utf-8')+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 2 in the Planned Adult Education and Training Sheet.='
                        if val_id_number.isdigit() == True and len(val_id_number) != 13:
                            msg+='<b>Employee Id '+str(val_id_number)+'</b> length should be 13 digits. Found at row <b>'+str(count+1)+'</b> and columns 3 in the Planned Adult Education and Training Sheet.='
                        elif val_id_number == '':
                            msg+='<b>Employee Id '+str(val_id_number)+'</b> should not be blank. Found at row <b>'+str(count+1)+'</b> and columns 3 in the Planned Adult Education and Training Sheet.='
 
                        
                        
                        if val_population == '':
                            msg+='<b>Population Group '+str(sheet_row[3].value).encode('utf-8')+'</b> should be any one string from African/Coloured/Indian/White. Found at row <b>'+str(count+1)+'</b> and columns 4 in the Planned Adult Education and Training Sheet.='
                        if val_genders == '':
                            msg+='<b>Gender '+str(sheet_row[4].value).encode('utf-8')+'</b> should be string as either M - Male or F - Female. Found at row <b>'+str(count+1)+'</b> and columns 5 in the Planned Adult Education and Training Sheet.='
                        if val_disability_status == '':
                            msg+='<b>Disability Status and Type '+str(sheet_row[5].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 6 in the Planned Adult Education and Training Sheet.='
                        if val_province == None :
                            msg+='<b>Learner Province '+str(sheet_row[6].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 7 in the Planned Adult Education and Training Sheet.='
                        if val_city == None :
                            msg+='<b>City '+str(sheet_row[7].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 8 in the Planned Adult Education and Training Sheet.='
                        if val_urban == '':
                            msg+='<b>Urban/Rural '+str(sheet_row[8].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 9 in the Planned Adult Education and Training Sheet.='
                        if type(sheet_row[9].value) == str or re.search('[a-zA-Z]', str(sheet_row[9].value)) :
                            msg+='<b>AET Start Date '+str(sheet_row[9].value)+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 10 in the Planned Adult Education and Training Sheet.='
                        if type(sheet_row[10].value) == str or re.search('[a-zA-Z]', str(sheet_row[10].value)) :
                            msg+='<b>AET End Date '+str(sheet_row[10].value)+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and columns 11 in the Planned Adult Education and Training Sheet.='
                        if sheet_row[11].value == '' :
                            msg+='<b>Provider '+str(sheet_row[11].value).encode('utf-8')+'</b> should be string. Found at row <b>'+str(count+1)+'</b> and columns 12 in the Planned Adult Education and Training Sheet.='
                        if val_aet_level == '':
                            msg+='<b>AET Level '+str(sheet_row[12].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 13 in the Planned Adult Education and Training Sheet.='
                        if val_aet_subject is None:
                            msg+='<b>AET Subject '+str(sheet_row[13].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and columns 14 in the Planned Adult Education and Training Sheet.='
                        if not sheet_row[0].value == '' and not sheet_row[1].value == '' and not (val_id_number.isdigit() == True and len(val_id_number) != 13) \
                        and not val_population == '' and not val_genders == '' and not val_disability_status == ''  \
                        and not val_disability_status == '' and not val_province == None and not val_city == None \
                        and not val_urban == '' and not (type(sheet_row[9].value) == str or re.search('[a-zA-Z]', str(sheet_row[9].value))) and not (type(sheet_row[10].value) == str or re.search('[a-zA-Z]', str(sheet_row[10].value)))\
                        and not sheet_row[11].value == '' and not val_aet_level == '' and not val_aet_subject is None:
                            self._cr.execute("insert into planned_adult_education_training_fields(name, surname, id_number, population_group, gender, dissability_status_and_type, province, city_id, urban, start_date, end_date, provider, aet_level, planned_adult_education_wsp_id) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(sheet_row[0].value, sheet_row[1].value, val_id_number, val_population,val_genders,val_disability_status, val_province, val_city, val_urban,start_date,end_date,sheet_row[12].value,val_aet_level, wsp_plan_data.id))
                            self._cr.execute("select max(id) from planned_adult_education_training_fields")
                            planned_adult_education_id = self._cr.fetchone() 
                            for aet_subject_id in val_aet_subject :
                                self._cr.execute("insert into aet_subject_planned_rel(planed_adult_education_training_id,aet_subject_id) values(%s,%s)",(planned_adult_education_id[0],aet_subject_id))                            
                            
                        else:
                            planned_adult_education_list.append([sheet_row[0].value,sheet_row[1].value,sheet_row[2].value,sheet_row[3].value,sheet_row[4].value,sheet_row[5].value,sheet_row[6].value,sheet_row[7].value,sheet_row[8].value,str(start_date)[8:10]+"/"+str(start_date)[5:7]+"/"+str(start_date)[:4],str(end_date)[8:10]+"/"+str(end_date)[5:7]+"/"+str(end_date)[:4],sheet_row[11].value,sheet_row[12].value,sheet_row[13].value])
                    ## Loading Planned Vacancies Hard to fill
                    if count > 0 and sheet_count == 4 and blank_row > 0:
                        ## Validating Vacancies Hard to fill for invalid occurances,
                        val_ofo_code = self.get_ofo_code(sheet_row[0].value)
                        val_occupation = self.get_occupation(sheet_row[0].value,sheet_row[1].value)
                        specialisation_exists = self.check_specialisation_exists(val_ofo_code)
                        val_specialisation = self.get_specialization(sheet_row[0].value,sheet_row[2].value)
                        val_province = self.get_province(sheet_row[3].value)
                        val_genders = self.get_genders(sheet_row[5].value)
                        val_population = self.get_population_group(sheet_row[6].value)
                        if val_ofo_code == None:
                            msg+='<b>OFO Code '+str(sheet_row[0].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and column 1 in the Vacancies Hard to fill sheet.='
                        if val_occupation == None :
                            msg+='<b>Occupation '+str(sheet_row[1].value).encode('utf-8')+'</b> should be linked with ofo code. Found at row <b>'+str(count+1)+'</b> and column 2 in the Vacancies Hard to fill sheet.='
                        if val_specialisation == None and specialisation_exists == True:
                            msg+='<b>Specialisation '+str(sheet_row[2].value).encode('utf-8')+'</b> should be linked with ofo code. Found at row <b>'+str(count+1)+'</b> and column 3 in the Vacancies Hard to fill sheet.='
                        if val_province == None :
                            msg+='<b>Province '+str(sheet_row[3].value).encode('utf-8')+'</b> not present in the system. Found at row <b>'+str(count+1)+'</b> and column 4 in the Vacancies Hard to fill sheet.='
                        if type(sheet_row[4].value) == unicode :
                            raise Warning(_('Number Of Vacancies %s is invalid. Found at row %s and column 5 in the Vacancies Hard to fill sheet.')%(sheet_row[4].value,str(count+1)))
                        if type(sheet_row[4].value) == str :
                            raise Warning(_('Number Of Vacancies %s is invalid. Found at row %s and column 5 in the Vacancies Hard to fill sheet.')%(sheet_row[4].value,str(count+1)))
#                             msg+='<b>Number Of Vacancies '+sheet_row[4].value+'</b> is invalid. Found at row <b>'+str(count+1)+'</b> and column 5 in the Vacancies Hard to fill sheet.='
                        if int(sheet_row[4].value) < 0  :
                            msg+='<b>Number Of Vacancies '+str(sheet_row[4].value)+'</b> should not be negative. Found at row <b>'+str(count+1)+'</b> and column 5 in the Vacancies Hard to fill sheet.='
                        if val_genders == '' :
                            msg+='<b>Gender '+str(sheet_row[5].value).encode('utf-8')+'</b> should be string as either M - Male or F - Female. Found at row <b>'+str(count+1)+'</b> and column 6 in the Vacancies Hard to fill sheet.='
                        if val_population == '':
                            msg+='<b>Race '+str(sheet_row[6].value).encode('utf-8')+'</b> should be any one string from African/Coloured/Indian/White. Found at row <b>'+str(count+1)+'</b> and column 7 in the Vacancies Hard to fill sheet.='
                        if type(sheet_row[7].value) == unicode :
                            raise Warning(_('Number Of months position has %s  is invalid. Found at row %s and column 8 in the Vacancies Hard to fill sheet.')%(sheet_row[7].value,str(count+1)))
                        if type(sheet_row[7].value) == str :
                            raise Warning(_('Number Of months position has %s  is invalid. Found at row %s and column 8 in the Vacancies Hard to fill sheet.')%(sheet_row[7].value,str(count+1)))
                        if not val_ofo_code == None and not val_occupation == None and \
                        not (val_specialisation == None and specialisation_exists == True) and \
                        not val_province == None and not type(sheet_row[4].value) == unicode and \
                        not (int(sheet_row[4].value) < 0) and not val_genders == '' and not val_population == ''\
                        and not type(sheet_row[7].value) == unicode and not type(sheet_row[7].value) == str: 
                            self._cr.execute("insert into scarce_and_critical_skills_fields (ofo_code, occupation, specialization, province, number_of_vacancies, gender, population_group, no_of_months, comments, scarce_and_critical_wsp_id) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(val_ofo_code, val_occupation, val_specialisation, val_province, sheet_row[4].value, val_genders, val_population, sheet_row[7].value, sheet_row[8].value,wsp_plan_data.id))
                        else:
                            scarce_and_critical_list.append([sheet_row[0].value,sheet_row[1].value,sheet_row[2].value,sheet_row[3].value,sheet_row[4].value,sheet_row[5].value,sheet_row[6].value,sheet_row[7].value])
                    count+=1
            #This code is recently added out of for loop to show warning msg at once
            if msg :
                ##This code will write incorrect data into newly created xls file
                wsp_buffered = cStringIO.StringIO()
                workbook = xlsxwriter.Workbook(wsp_buffered)                
                worksheet1 = workbook.add_worksheet('Total Employment Profile')
                worksheet2 = workbook.add_worksheet('Planned Training')
                worksheet3 = workbook.add_worksheet('Adult Education And Training')
                worksheet4 = workbook.add_worksheet('Vacancies Hard to fill')
                
                worksheet1.set_column(0, 40, 16)
                worksheet2.set_column(0, 40, 16)
                worksheet3.set_column(0, 40, 16)
                worksheet4.set_column(0, 40, 16)
                
                merge_format = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'})
                
                worksheet1.write('A1', 'SDL Number',merge_format)
                worksheet1.write('B1', 'First Name',merge_format)
                worksheet1.write('C1', 'Last Name',merge_format)
                worksheet1.write('D1', 'Citizen Status',merge_format)
                worksheet1.write('E1', 'Employee ID',merge_format)
                worksheet1.write('F1', 'ID Type',merge_format)
                worksheet1.write('G1', 'Date Of Birth',merge_format)
                worksheet1.write('H1', 'OFO Code',merge_format)
                worksheet1.write('I1', 'Occupation',merge_format)
                worksheet1.write('J1', 'Specialisation',merge_format)
                worksheet1.write('K1', 'Province',merge_format)
                worksheet1.write('L1', 'City',merge_format)
                worksheet1.write('M1', 'Urban/Rural',merge_format)
                worksheet1.write('N1', 'Highest Education Level',merge_format)
                worksheet1.write('O1', 'Race',merge_format)
                worksheet1.write('P1', 'Gender',merge_format)
                worksheet1.write('Q1', 'Disability',merge_format)
                row = 1
                for l in total_employment_list:
                    col = 0
                    for e in l:
                        if e:
                            worksheet1.write(row, col, e)
                        col+=1
                    row+=1
                    
                worksheet2.write('A1', 'Type Of Training',merge_format)
                worksheet2.write('B1', 'Name',merge_format)
                worksheet2.write('C1', 'Surname',merge_format)
                worksheet2.write('D1', 'Employee ID',merge_format)
                worksheet2.write('E1', 'OFO Code',merge_format)
                worksheet2.write('F1', 'Occupation',merge_format)
                worksheet2.write('G1', 'Specialisation',merge_format)
                worksheet2.write('H1', 'Province',merge_format)
                worksheet2.write('I1', 'City',merge_format)
                worksheet2.write('J1', 'Urban/Rural',merge_format)
                worksheet2.write('K1', 'Employed/UnEmployed',merge_format)
                worksheet2.write('L1', 'Type of Training Intervention',merge_format)
                worksheet2.write('M1', 'Other Type Of Training Intervention',merge_format)
                worksheet2.write('N1', 'Name of training Intervention',merge_format)
                worksheet2.write('O1', 'Pivotal Programme Type',merge_format)
                worksheet2.write('P1', 'Pivotal Programme Qualification',merge_format)
                worksheet2.write('Q1', 'Pivotal Programme institution',merge_format)
                worksheet2.write('R1', 'Cost Per Learner',merge_format)
                worksheet2.write('S1', 'Start Date',merge_format)
                worksheet2.write('T1', 'End Date',merge_format)
                worksheet2.write('U1', 'NQF Aligned',merge_format)
                worksheet2.write('V1', 'NQF Level',merge_format)
                worksheet2.write('W1', 'Race',merge_format)
                worksheet2.write('X1', 'Gender',merge_format)
                worksheet2.write('Y1', 'Disability',merge_format)
                row = 1
                for l in planned_training_list:
                    col = 0
                    for e in l:
                        if e:
                            worksheet2.write(row, col, e)
                        col+=1
                    row+=1
                
                worksheet3.write('A1', 'First Name',merge_format)
                worksheet3.write('B1', 'Surname',merge_format)
                worksheet3.write('C1', 'ID Number',merge_format)
                worksheet3.write('D1', 'Population Group',merge_format)
                worksheet3.write('E1', 'Gender',merge_format)
                worksheet3.write('F1', 'Disability Status And Type',merge_format)
                worksheet3.write('G1', 'Learner Province',merge_format)
                worksheet3.write('H1', 'City',merge_format)
                worksheet3.write('I1', 'Urban/Rural',merge_format)
                worksheet3.write('J1', 'AET Start Date',merge_format)
                worksheet3.write('K1', 'AET End Date',merge_format)
                worksheet3.write('L1', 'Provider',merge_format)
                worksheet3.write('M1', 'AET Level',merge_format)
                worksheet3.write('N1', 'AET Subject',merge_format)

                row = 1
                for l in planned_adult_education_list:
                    col = 0
                    for e in l:
                        if e:
                            worksheet3.write(row, col, e)
                        col+=1
                    row+=1

                worksheet4.write('A1', 'OFO Code',merge_format)
                worksheet4.write('B1', 'Occupation',merge_format)
                worksheet4.write('C1', 'Specialisation',merge_format)
                worksheet4.write('D1', 'Province',merge_format)
                worksheet4.write('E1', 'Number of Vacancies',merge_format)
                worksheet4.write('F1', 'Gender',merge_format)
                worksheet4.write('G1', 'Race',merge_format)
                worksheet4.write('H1', 'Number of months position has',merge_format)
                worksheet4.write('I1', 'Comments',merge_format)

                row = 1
                for l in scarce_and_critical_list:
                    col = 0
                    for e in l:
                        if e:
                            worksheet4.write(row, col, e)
                        col+=1
                    row+=1
                workbook.close()
                wsp_xlsx_data = wsp_buffered.getvalue()
                wsp_out_data = base64.encodestring(wsp_xlsx_data)
                attachment_obj = self.env['ir.attachment']
                wsp_new_attach = attachment_obj.create({
                    'name':'Incorrect WSP.xlsx',
                    'res_name': 'wsp_import',
                    'type': 'binary',
                    'res_model': 'wsp.plan',
                    'datas':wsp_out_data,
                })                
                self = self.with_context({'error_log_msg':msg,'incorrect_id':wsp_new_attach.id})
                return {
                            'name' : 'XLS Import Error Log',
                            'type' : 'ir.actions.act_window',
                            'view_type' : 'form',
                            'view_mode' : 'form',
                            'res_model' : 'xls.error.validation',
                            'target' : 'new',
                            'context' : self._context,
                        }
        return True
    
import_wsp_xls()