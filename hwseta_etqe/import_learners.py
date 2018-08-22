from openerp import models, fields, api, _
import base64
import xlrd
from openerp.exceptions import Warning
import datetime
import re


class import_learners_template(models.TransientModel):
    _name = 'import.learners.template'

    learner_file = fields.Binary(string='Upload Learners File')

    @api.multi
    def validate_id_number(self, id_number):
        if type(id_number) == unicode:
            id_number = id_number
        if type(id_number) == float:
            id_number = int(id_number)
        id_number = str(id_number).strip()
        return id_number

    @api.multi
    def validate_long_number(self, number):
        print "type of number=----------", type(number)
        if type(number) == unicode:
            number = number
        if type(number) == float:
            number = int(number)
        if type(number) == str:
            number = number.split('.')[0]
        number = str(number).strip()
        return number

    @api.multi
    def get_genders(self, gender_value):
        gender = ''
        print "Gender======", gender_value, type(gender_value)
        if gender_value == 'M - Male' or gender_value == 'Male' or gender_value == 'male':
            gender = 'male'
        if gender_value == 'F - Female' or gender_value == 'Female' or gender_value == 'female':
            gender = 'female'
        return gender

    @api.multi
    def validate_date(self, input_date, excel):
        try:
            if type(input_date) == unicode:
                input_date = datetime.datetime.strptime(
                    str(input_date), '%d/%m/%Y').date()
            elif type(input_date) == float:
                input_date = datetime.datetime(
                    *xlrd.xldate_as_tuple(input_date, excel.datemode)).date()
            else:
                input_date = str(input_date)
        except:
            input_date = str(input_date)
        return input_date

    @api.multi
    def get_gender_saqa_code(self, gender_saqa_value):
        gender_saqa_code = ''
        if gender_saqa_value == 'M' or gender_saqa_value == 'm':
            gender_saqa_code = 'm'
        if gender_saqa_value == 'F' or gender_saqa_value == 'f':
            gender_saqa_code = 'f'
        return gender_saqa_code

    @api.multi
    def get_disability_status(self, disability_value):
        disability_status = ''
        if disability_value == 'Sight ( even with glasses )':
            disability_status = 'sight'
        if disability_value == 'Hearing ( even with h.aid )':
            disability_status = 'hearing'
        if disability_value == 'Communication ( talk/listen)':
            disability_status = 'communication'
        if disability_value == 'Physical ( move/stand, etc)':
            disability_status = 'physical'
        if disability_value == 'Intellectual ( learn,etc)':
            disability_status = 'intellectual'
        if disability_value == 'Emotional ( behav/psych)':
            disability_status = 'emotional'
        if disability_value == 'Multiple':
            disability_status = 'multiple'
        if disability_value == 'Disabled but unspecified':
            disability_status = 'disabled'
        if disability_value == 'None' or disability_value == 'none':
            disability_status = 'none'
        return disability_status

    @api.multi
    def get_equity(self, race_value):
        race = ''
        if race_value == 'Black: African':
            race = 'black_african'
        if race_value == 'Black: Indian / Asian':
            race = 'black_indian'
        if race_value == 'Black: Coloured':
            race = 'black_coloured'
        if race_value == 'Other':
            race = 'other'
        if race_value == 'Unknown':
            race = 'unknown'
        if race_value == 'Indian':
            race = 'indian'
        if race_value == 'White':
            race = 'white'
        return race

    @api.multi
    def get_language(self, lang_value):
        lang = None
        lang_data = self.env['res.lang'].search(
            [('name', '=', lang_value)], limit=1)
        if lang_data:
            lang = lang_data.id
        return lang

    @api.multi
    def get_country(self, country_value):
        country = None
        country_data = self.env['res.country'].search(
            [('name', '=', country_value)], limit=1)
        if country_data:
            country = country_data.id
        return country

    @api.multi
    def get_province(self, province_value):
        province = None
        province_data = self.env['res.country.state'].search(
            [('name', '=', province_value)], limit=1)
        if province_data:
            province = province_data.id
        return province

    @api.multi
    def get_city(self, city_value):
        city = None
        city_data = self.env['res.city'].search(
            [('name', '=', city_value)], limit=1)
        if city_data:
            city = city_data.id
        return city

    @api.multi
    def get_suburb(self, suburb_value):
        suburb = None
        suburb_data = self.env['res.suburb'].search(
            [('name', '=', suburb_value)], limit=1)
        if suburb_data:
            suburb = suburb_data.id
        return suburb

    @api.multi
    def get_municipality(self, municipality_value):
        municipality_data = self.env['res.municipality'].search(
            [('name', '=', municipality_value)], limit=1)
        municipality = None
        if municipality_data:
            municipality = municipality_data.id
        return municipality

    @api.multi
    def import_learners(self):
        learner_data = ''
        if self.learner_file:
            learner_data = base64.decodestring(self.learner_file)
        if learner_data:
            try:
                excel = xlrd.open_workbook(file_contents=learner_data)
            except:
                raise Warning(_('Incorrect File Format!'))
            sheet_names = excel.sheet_names()
            # # Reading file Sheet by Sheet
            sheet_count = 0
            for sheet_name in sheet_names:
                sheet_count += 1
                xl_sheet = excel.sheet_by_name(sheet_name)
                row_count = 0
                for row_idx in range(0, xl_sheet.nrows):
                    row_count += 1
                count = 0
                sheet_row = []
                while count < row_count:
                    sheet_row = xl_sheet.row(count)
                    # Loading Learner Data.
                    blank_row = 0
                    for col in sheet_row:
                        if col.value:
                            blank_row += 1
                    if count > 0 and sheet_count == 1 and blank_row > 0:
                        # # ## Validating import learners Excel Sheet file for Invalid data
                        gender, gender_saqa_code, disability_status, equity = '', '', '', ''
                        work_suburb, work_city, work_province, work_country = None, None, None, None
                        home_suburb, home_city, home_province, home_country = None, None, None, None
                        postal_suburb, postal_city, postal_province, postal_country = None, None, None, None
                        country_of_nationality, language, work_phone, cell, fax_number = None, None, None, None, None
                        val_id_number = self.validate_id_number(
                            sheet_row[30].value)
                        print "str(sheet_row[20].value)???????????", sheet_row[20].value
                        gender = self.get_genders(str(sheet_row[20].value))
                        gender_saqa_code = self.get_gender_saqa_code(
                            str(sheet_row[21].value))
                        disability_status = self.get_disability_status(
                            str(sheet_row[24].value))
                        country_of_nationality = self.get_country(
                            str(sheet_row[29].value))
                        work_phone = self.validate_long_number(
                            str(sheet_row[6].value))
                        cell = self.validate_long_number(
                            str(sheet_row[39].value))
                        fax_number = self.validate_long_number(
                            str(sheet_row[40].value))
                        work_zip = self.validate_long_number(
                            str(sheet_row[13].value))
                        home_zip = self.validate_long_number(
                            str(sheet_row[57].value))
                        postal_zip = self.validate_long_number(
                            str(sheet_row[66].value))
                        equity = self.get_equity(str(sheet_row[37].value))
                        work_suburb = self.get_suburb(str(sheet_row[10].value))
                        work_city = self.get_city(str(sheet_row[11].value))
                        work_province = self.get_province(
                            str(sheet_row[12].value))
                        work_country = self.get_country(
                            str(sheet_row[14].value))
                        home_suburb = self.get_suburb(str(sheet_row[54].value))
                        home_city = self.get_city(str(sheet_row[55].value))
                        home_province = self.get_province(
                            str(sheet_row[56].value))
                        home_country = self.get_country(
                            str(sheet_row[58].value))
                        postal_suburb = self.get_suburb(
                            str(sheet_row[63].value))
                        postal_city = self.get_city(str(sheet_row[64].value))
                        postal_province = self.get_province(
                            str(sheet_row[65].value))
                        postal_country = self.get_country(
                            str(sheet_row[67].value))
                        language = self.get_language(str(sheet_row[36].value))
                        learner_exist = ''
                        master_learner_obj = self.env['hr.employee']
                        learner_obj = self.env['learner.registration']
                        if val_id_number:
                            learner_exist = master_learner_obj.search(
                                [('learner_identification_id', '=', val_id_number)])
                        is_existing_learner = False
                        if learner_exist:
                            is_existing_learner = True
                        print "val_id_number---------", val_id_number
                        if val_id_number:
                            if not is_existing_learner:
                                learner_id = learner_obj.create({
                                    'is_existing_learner': False,
                                    'person_title': str(sheet_row[0].value),
                                    'name': str(sheet_row[1].value),
                                    'middle_name': str(sheet_row[2].value),
                                    'maiden_name': str(sheet_row[3].value),
                                    'person_last_name': str(sheet_row[4].value),
                                    'work_email': str(sheet_row[5].value),
                                    'work_phone': work_phone,
                                    'work_address': str(sheet_row[7].value),
                                    'work_address2': str(sheet_row[8].value),
                                    'work_address3': str(sheet_row[9].value),
                                    'person_suburb': work_suburb,
                                    'work_city': work_city,
                                    'work_province': work_province,
                                    'work_zip': work_zip,
                                    'work_country': work_country,
                                    'status_reason': str(sheet_row[15].value),
                                    'notes': str(sheet_row[16].value),
                                    'department': str(sheet_row[17].value),
                                    'job_title': str(sheet_row[18].value),
                                    'manager': str(sheet_row[19].value),
                                    'gender': gender,
                                    'gender_saqa_code': gender_saqa_code,
                                    'marital': str(sheet_row[22].value),
                                    'dissability': str(sheet_row[23].value),
                                    'disability_status': disability_status,
                                    'socio_economic_status': str(sheet_row[25].value),
                                    'current_occupation': str(sheet_row[26].value),
                                    'years_in_occupation': int(float(sheet_row[27].value)),
                                    'citizen_resident_status_code': str(sheet_row[28].value),
                                    'country_id': country_of_nationality,
                                    'identification_id': val_id_number,
                                    'alternate_id_type': str(sheet_row[31].value),
                                    'national_id': str(sheet_row[32].value),
                                    #'person_birth_date': str(sheet_row[33].value),
                                    'passport_id': str(sheet_row[34].value),
                                    'id_document': str(sheet_row[35].value),
                                    'home_language_code': language,
                                    'equity': equity,
                                    'initials': str(sheet_row[38].value),
                                    'cell': cell,
                                    'person_fax_number': fax_number,
                                    'method_of_communication': str(sheet_row[41].value),
                                    'highest_education': str(sheet_row[42].value),
                                    #'enrollment_date': str(sheet_row[43].value),
                                    'status_comments': str(sheet_row[44].value),
                                    'person_home_address_1': str(sheet_row[51].value),
                                    'person_home_address_2': str(sheet_row[52].value),
                                    'person_home_address_3': str(sheet_row[53].value),
                                    'person_home_suburb': home_suburb,
                                    'person_home_city': home_city,
                                    'person_home_province_code': home_province,
                                    'person_home_zip': home_zip,
                                    'country_home': home_country,
                                    'same_as_home': str(sheet_row[59].value),
                                    'person_postal_address_1': str(sheet_row[60].value),
                                    'person_postal_address_2': str(sheet_row[61].value),
                                    'person_postal_address_3': str(sheet_row[62].value),
                                    'person_postal_suburb': postal_suburb,
                                    'person_postal_city': postal_city,
                                    'person_postal_province_code': postal_province,
                                    'person_postal_zip': postal_zip,
                                    'country_postal': postal_country,
                                    'learner_status': 'Enrolled',
                                    'is_learner': True,
                                    'provider_learner': True,
                                    'seta_elements': True,
                                })
                            elif is_existing_learner:
                                learner_id = learner_obj.create({
                                    'is_existing_learner': True,
                                    'onchange_identification_number': val_id_number,
                                    'person_title': str(sheet_row[0].value),
                                    'name': str(sheet_row[1].value),
                                    'middle_name': str(sheet_row[2].value),
                                    'maiden_name': str(sheet_row[3].value),
                                    'person_last_name': str(sheet_row[4].value),
                                    'work_email': str(sheet_row[5].value),
                                    'work_phone': work_phone,
                                    'work_address': str(sheet_row[7].value),
                                    'work_address2': str(sheet_row[8].value),
                                    'work_address3': str(sheet_row[9].value),
                                    'person_suburb': work_suburb,
                                    'work_city': work_city,
                                    'work_province': work_province,
                                    'work_zip': work_zip,
                                    'work_country': work_country,
                                    'status_reason': str(sheet_row[15].value),
                                    'notes': str(sheet_row[16].value),
                                    'department': str(sheet_row[17].value),
                                    'job_title': str(sheet_row[18].value),
                                    'manager': str(sheet_row[19].value),
                                    'gender': gender,
                                    'gender_saqa_code': gender_saqa_code,
                                    'marital': str(sheet_row[22].value),
                                    'dissability': str(sheet_row[23].value),
                                    'disability_status': disability_status,
                                    'socio_economic_status': str(sheet_row[25].value),
                                    'current_occupation': str(sheet_row[26].value),
                                    'years_in_occupation': int(float(sheet_row[27].value)),
                                    'citizen_resident_status_code': str(sheet_row[28].value),
                                    'country_id': country_of_nationality,
                                    'identification_id': val_id_number,
                                    'alternate_id_type': str(sheet_row[31].value),
                                    'national_id': str(sheet_row[32].value),
                                    #'person_birth_date': str(sheet_row[33].value),
                                    'passport_id': str(sheet_row[34].value),
                                    'id_document': str(sheet_row[35].value),
                                    'home_language_code': language,
                                    'equity': equity,
                                    'initials': str(sheet_row[38].value),
                                    'cell': cell,
                                    'person_fax_number': fax_number,
                                    'method_of_communication': str(sheet_row[41].value),
                                    'highest_education': str(sheet_row[42].value),
                                    #'enrollment_date': str(sheet_row[43].value),
                                    'status_comments': str(sheet_row[44].value),
                                    'person_home_address_1': str(sheet_row[51].value),
                                    'person_home_address_2': str(sheet_row[52].value),
                                    'person_home_address_3': str(sheet_row[53].value),
                                    'person_home_suburb': home_suburb,
                                    'person_home_city': home_city,
                                    'person_home_province_code': home_province,
                                    'person_home_zip': home_zip,
                                    'country_home': home_country,
                                    'same_as_home': str(sheet_row[59].value),
                                    'person_postal_address_1': str(sheet_row[60].value),
                                    'person_postal_address_2': str(sheet_row[61].value),
                                    'person_postal_address_3': str(sheet_row[62].value),
                                    'person_postal_suburb': postal_suburb,
                                    'person_postal_city': postal_city,
                                    'person_postal_province_code': postal_province,
                                    'person_postal_zip': postal_zip,
                                    'country_postal': postal_country,
                                    'learner_status': 'Enrolled',
                                    'is_learner': True,
                                    'provider_learner': True,
                                    'seta_elements': True,
                                })
                                
                            batch_master_obj = self.env['batch.master'].search(
                                        [('batch_id', '=', str(sheet_row[68].value).strip()),('batch_status','=','open')])
                            # Adding Qualification
                            if learner_id and batch_master_obj.qual_skill_batch == 'qual':
                                qual_master_obj = self.env['provider.qualification']
                                if str(sheet_row[68].value):
                                    start_date = ''
                                    end_date = ''
                                    qual_obj = qual_master_obj.browse(
                                        batch_master_obj.qualification_id.id)
                                    print "qual_obj =======", qual_obj
                                    if qual_obj:
                                        if not re.search('[a-zA-Z]', str(sheet_row[69].value)):
                                            start_date = self.validate_date(
                                                sheet_row[69].value, excel)
                                        else:
                                            start_date = str(
                                                sheet_row[69].value)
                                        if not re.search('[a-zA-Z]', str(sheet_row[70].value)):
                                            end_date = self.validate_date(
                                                sheet_row[70].value, excel)
                                        else:
                                            end_date = str(sheet_row[70].value)

                                        assessor_id, assessor_date, moderator_id, moderator_date = '', '', '', ''
                                        assessor_obj = self.env['hr.employee'].search(
                                            [('is_assessors', '=', True), ('assessor_moderator_identification_id', '=', str(sheet_row[71].value).strip())])
                                        if assessor_obj:
                                            assessor_id = assessor_obj.id
                                            assessor_date = assessor_obj.end_date
                                        moderator_obj = self.env['hr.employee'].search([('is_moderators', '=', True), (
                                            'assessor_moderator_identification_id', '=', str(sheet_row[75].value).strip())])
                                        if moderator_obj:
                                            moderator_id = moderator_obj.id
                                            moderator_date = moderator_obj.moderator_end_date
                                        learner_qual_obj = self.env['learner.registration.qualification']
                                        qual_id = learner_qual_obj.create({
                                                                  'learner_qualification_id': learner_id.id,
                                                                  'learner_qualification_parent_id': qual_obj.id,
                                                                  'start_date': start_date,
                                                                  'end_date': end_date,
                                                                  'assessors_id': assessor_id,
                                                                  'assessor_date': assessor_date,
                                                                  'moderators_id': moderator_id,
                                                                  'moderator_date': moderator_date,
                                                                  'batch_id': batch_master_obj.id,
                                                                  })
                                        if qual_id:
                                            unit_standard_obj = self.env['learner.registration.qualification.line']
                                            for unit_line in qual_obj.qualification_line:
                                                unit_id = unit_standard_obj.create({
                                                    'learner_reg_id': qual_id.id,
                                                    'id_data': unit_line.id_no,
                                                    'type': unit_line.type,
                                                    'title': unit_line.title,
                                                    'level1': unit_line.level1,
                                                    'level2': unit_line.level2,
                                                    'level3': unit_line.level3,
                                                    'selection': True,
                                                })
                            # Addning Skills Programme
                            elif learner_id and batch_master_obj.qual_skill_batch == 'skill':
                                skill_master_obj = self.env['skills.programme']
                                if str(sheet_row[68].value):
                                    start_date = ''
                                    end_date = ''
                                    skill_obj = skill_master_obj.browse(
                                        batch_master_obj.skills_programme_id.id)
                                    print "skill_obj =======", skill_obj
                                    if skill_obj:
                                        if not re.search('[a-zA-Z]', str(sheet_row[69].value)):
                                            start_date = self.validate_date(
                                                sheet_row[69].value, excel)
                                        else:
                                            start_date = str(
                                                sheet_row[69].value)
                                        if not re.search('[a-zA-Z]', str(sheet_row[70].value)):
                                            end_date = self.validate_date(
                                                sheet_row[70].value, excel)
                                        else:
                                            end_date = str(sheet_row[70].value)

                                        assessor_id, assessor_date, moderator_id, moderator_date = '', '', '', ''
                                        assessor_obj = self.env['hr.employee'].search(
                                            [('is_assessors', '=', True), ('assessor_moderator_identification_id', '=', str(sheet_row[71].value).strip())])
                                        if assessor_obj:
                                            assessor_id = assessor_obj.id
                                            assessor_date = assessor_obj.end_date
                                        moderator_obj = self.env['hr.employee'].search([('is_moderators', '=', True), (
                                            'assessor_moderator_identification_id', '=', str(sheet_row[75].value).strip())])
                                        if moderator_obj:
                                            moderator_id = moderator_obj.id
                                            moderator_date = moderator_obj.moderator_end_date
                                        learner_skill_obj = self.env['skills.programme.learner.rel']
                                        skill_id = learner_skill_obj.create({
                                                                  'skills_programme_learner_rel_id': learner_id.id,
                                                                  'skills_programme_id': skill_obj.id,
                                                                  'saqa_skill_id': skill_obj.code, 
                                                                  'start_date': start_date,
                                                                  'end_date': end_date,
                                                                  'assessors_id': assessor_id,
                                                                  'assessor_date': assessor_date,
                                                                  'moderators_id': moderator_id,
                                                                  'moderator_date': moderator_date,
                                                                  'batch_id': batch_master_obj.id,
                                                                  })
                                        if skill_id:
                                            unit_standard_obj = self.env[
                                                'skills.programme.unit.standards.learner.rel']
                                            for unit_line in skill_obj.unit_standards_line:
                                                if unit_line.selection:
                                                    unit_id = unit_standard_obj.create({
                                                        'skills_programme_id': skill_id.id,
                                                        'id_no': unit_line.id_no,
                                                        'type': unit_line.type,
                                                        'title': unit_line.title,
                                                        'level1': unit_line.level1,
                                                        'level2': unit_line.level2,
                                                        'level3': unit_line.level3,
                                                        'selection': True,
                                                    })
                            # Adding Learning Programme
                            elif learner_id and batch_master_obj.qual_skill_batch == 'lp':
                                lp_master_obj = self.env['etqe.learning.programme']
                                if str(sheet_row[68].value):
                                    start_date = ''
                                    end_date = ''
                                    lp_obj = lp_master_obj.browse(batch_master_obj.learning_programme_id.id)
                                    print "lp_obj =======", lp_obj
                                    if lp_obj:
                                        if not re.search('[a-zA-Z]', str(sheet_row[69].value)):
                                            start_date = self.validate_date(
                                                sheet_row[69].value, excel)
                                        else:
                                            start_date = str(
                                                sheet_row[69].value)
                                        if not re.search('[a-zA-Z]', str(sheet_row[70].value)):
                                            end_date = self.validate_date(
                                                sheet_row[70].value, excel)
                                        else:
                                            end_date = str(sheet_row[70].value)

                                        assessor_id, assessor_date, moderator_id, moderator_date = '', '', '', ''
                                        assessor_obj = self.env['hr.employee'].search(
                                            [('is_assessors', '=', True), ('assessor_moderator_identification_id', '=', str(sheet_row[71].value).strip())])
                                        if assessor_obj:
                                            assessor_id = assessor_obj.id
                                            assessor_date = assessor_obj.end_date
                                        moderator_obj = self.env['hr.employee'].search([('is_moderators', '=', True), (
                                            'assessor_moderator_identification_id', '=', str(sheet_row[75].value).strip())])
                                        if moderator_obj:
                                            moderator_id = moderator_obj.id
                                            moderator_date = moderator_obj.moderator_end_date
                                        learner_lp_obj = self.env['learning.programme.learner.rel']
                                        lp_id = learner_lp_obj.create({
                                                                  'learning_programme_learner_rel_id': learner_id.id,
                                                                  'learning_programme_id': lp_obj.id,
                                                                  'lp_saqa_id': lp_obj.code, 
                                                                  'start_date': start_date,
                                                                  'end_date': end_date,
                                                                  'assessors_id': assessor_id,
                                                                  'assessor_date': assessor_date,
                                                                  'moderators_id': moderator_id,
                                                                  'moderator_date': moderator_date,
                                                                  'batch_id': batch_master_obj.id,
                                                                  })
                                        if lp_id:
                                            unit_standard_obj = self.env['learning.programme.unit.standards.learner.rel']
                                            for unit_line in lp_obj.unit_standards_line:
                                                if unit_line.selection:
                                                    unit_id = unit_standard_obj.create({
                                                        'learning_programme_id': lp_id.id,
                                                        'id_no': unit_line.id_no,
                                                        'type': unit_line.type,
                                                        'title': unit_line.title,
                                                        'level1': unit_line.level1,
                                                        'level2': unit_line.level2,
                                                        'level3': unit_line.level3,
                                                        'selection': True,
                                                        'seta_approved_lp':unit_line.seta_approved_lp,
                                                    })
                    count += 1
import_learners_template()
