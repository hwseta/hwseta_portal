import werkzeug
from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers.main import login_redirect
from datetime import datetime
import openerp.addons.website.controllers.main
# from docutils.nodes import contact
import base64
import datetime
import json
import ast
from openerp.addons.web.controllers.main import ensure_db
from openerp.addons.web.controllers.main import Home
from operator import itemgetter

class Website(openerp.addons.website.controllers.main.Website):
    qualification=[]
    @http.route(['/page/sdf_registration'], type='http', auth="public", website=True)
    def get_sdfDetails(self, **post): 
        value={}
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
#         res_country_state_obj = registry.get('res.country.state')
#         state_ids = res_country_state_obj.search(cr,SUPERUSER_ID,[],context=context)
#         state_objs = res_country_state_obj.browse(cr,SUPERUSER_ID,state_ids,context=context)
#         cr.execute("select id, name from res_country_state")
#         state_data = cr.fetchall()    
#         cr.commit()
#         value.update({'state':state_data})
#         value.update({'state1':state_data})
#         value.update({'state2':state_data})

#         res_country_obj = registry.get('res.country')
#         country_ids = res_country_obj.search(cr,SUPERUSER_ID,[],context=context)
#         country_objs = res_country_obj.browse(cr,SUPERUSER_ID,country_ids,context=context)
        cr.execute("select id, name from res_country")
        country_data = cr.fetchall() 
        cr.commit()
        value.update({'nationality':country_data})
        value.update({'nationality1':country_data})
        value.update({'nationality2':country_data})
        value.update({'nationality3':country_data})
        
#         res_city_obj = registry.get('res.city')
#         city_ids = res_city_obj.search(cr,SUPERUSER_ID,[],context=context)
#         city_objs = res_city_obj.browse(cr,SUPERUSER_ID,city_ids,context=context)
#         cr.execute("select id, name from res_city")
#         city_data = cr.fetchall()    
#         cr.commit()
#         value.update({'city':city_data})
#         value.update({'city1':city_data})
#         value.update({'city2':city_data})  

#         res_suburb_obj = registry.get('res.suburb')
#         suburb_ids = res_suburb_obj.search(cr,SUPERUSER_ID,[],context=context)
#         suburb_objs = res_suburb_obj.browse(cr,SUPERUSER_ID,suburb_ids,context=context)
#         cr.execute("select id, name from res_suburb")
#         suburb_data = cr.fetchall()
#         cr.commit()
#         value.update({'suburb':suburb_data})
#         value.update({'suburb1':suburb_data})
#         value.update({'suburb2':suburb_data})
           
#         res_lang_obj = registry.get('res.lang')
#         lang_ids = res_lang_obj.search(cr,SUPERUSER_ID,[],context=context)
#         lang_objs = res_lang_obj.browse(cr,SUPERUSER_ID,lang_ids,context=context)
        cr.execute("select id, name from res_lang")
        lang_data = cr.fetchall()
        cr.commit()        
        value.update({'language':lang_data})
        
#         res_partner_obj = registry.get('res.partner')
#         partner_ids = res_partner_obj.search(cr,SUPERUSER_ID,[('employer','=',True)],context=context)
#         partner_objs = res_partner_obj.browse(cr,SUPERUSER_ID,partner_ids,context=context)


#         cr.execute("select id,name,employer_trading_name,employer_sdl_no from res_partner where employer=True")
#         partner_data = cr.fetchall()
#         cr.commit()        
#         value.update({'partner':partner_data})
        
        ir_sequence_obj = registry.get('ir.sequence')
        value.update({'sdfref':ir_sequence_obj.get(cr, SUPERUSER_ID,'sdf.register.reference')})
        return request.website.render("website.sdf_registration", value)
        
    @http.route(['/hwseta/confirm_sdf'], type='http', auth="public", website=True)
    def confirm_sdf(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        values, dict = {}, {}
        employer_line=[]
        sdf_reg_obj = registry.get('sdf.register')
        res_partner_obj = registry.get('res.partner')
        if post:
            values['person_middle_name'] = post.get('txtMiddleName','')
            values['name'] = post.get('txtFirstName','')+' '+ post.get('txtSurname','')
            values['person_name'] = post.get('txtFirstName','')     
            values['person_last_name'] = post.get('txtSurname','')
            values['person_title'] = post.get('cboTitle','')
            values['cont_number_home'] = post.get('txtCntNoHome','')
            values['cont_number_office'] = post.get('txtCntNoOffice','')
#             values['initials'] = post.get('txtInitials','')
            values['work_email'] = post.get('txtWorkEmail','')
            values['work_phone'] = post.get('txtWorkPhone','')
            values['work_address'] = post.get('txtAddress1','')
            values['work_address2'] = post.get('txtAddress2','')
            values['work_address3'] = post.get('txtAddress3','')
            values['person_suburb'] = post.get('txtSuburb','')
            values['work_city'] = post.get('txtCity','')
            values['work_province'] = post.get('cboState','')
            values['work_zip'] = post.get('txtZip','')
            values['work_country'] = post.get('cboCountry','')
            values['mobile_phone'] = post.get('txtMobile','')
            values['department'] = post.get('txtDept','')
            values['job_title'] = post.get('txtJobTitle','')
            values['manager'] = post.get('txtManager','')
            values['notes'] = post.get('txtNotes','')
            if post.get('txtID','')!='':
                values['identification_id'] = post.get('txtID','')
            values['gender'] = post.get('cboGender','')
            if post.get('radioIC',''):
                if post.get('radioIC','')=='Internal':
                    values['sdf_type']='internal'
                    if post.get('radioPS',''):
                        values['primary_secondary']=post.get('radioPS')
                        values['check_sdf_type']=True
                if post.get('radioIC','')=='Consultant':
                    values['sdf_type']='consultant'                
            values['country_id'] = post.get('cboNationality','')
#             values['person_alternate_id'] = post.get('txtPersonAltNo','')
#             values['alternate_id_type_id'] = post.get('txtPersonAltType','')
            values['passport_id'] = post.get('txtPassportNo','')
#             values['bank_account_number'] = post.get('txtBankAccountNo','')
#             values['equity_code'] = post.get('txtEquityCode','')
#             values['filler01'] = post.get('txtFiller01','')
#             values['otherid'] = post.get('txtOtherId','')
            values['home_language_code'] = post.get('txtHomeLanguageCode','')
            values['citizen_resident_status_code'] = str(post.get('txtCitizenResStatusCode',''))
#             values['filler02'] = post.get('txtFiller02','')
            values['national_id'] = post.get('txtNationalId','')
            if post['txtIdDocument']:
                doc_id = registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('txtIdDocument','').filename,
                                                                                 'datas': base64.encodestring(post['txtIdDocument'].read()),'datas_fname':post.get('txtIdDocument','').filename,})
                values['id_document'] = doc_id
            if post.get('BirthDate','') != '':
                values['person_birth_date'] =datetime.datetime.strptime(post.get('BirthDate',''), "%d/%m/%Y")
            values['dissability']=post.get('disability','')
#             values['highest_level_of_education'] = post.get('txtHighestEducationLevel','')
#             values['current_occupation'] = post.get('txtOccupationCurrent','')
#             values['citizen_status'] = post.get('cboCitizenStatus','')
            values['marital'] = post.get('cboMaritalStatus','')
#             values['experiance'] = post.get('txtOccupationExperience','')
#             values['experiance_dur'] = post.get('txtOccupationYears','')
            values['cell_phone_number'] = post.get('txtWorkPhone','')
            values['cont_home_number'] = post.get('txtCntNoHome','')
            values['work_phone'] = post.get('txtCntNoOffice','')
            values['cont_number_office'] = post.get('txtCntNoOffice','')
#             values['fax_number'] = post.get('txtFaxNo','')
#             values['cell_phone_number'] = post.get('txtEMail','')
            values['person_home_address_1'] = post.get('txtHomeAddress1','')
            values['person_home_address_2'] = post.get('txtHomeAddress2','')
            values['person_home_address_3'] = post.get('txtHomeAddress3','')
            values['person_home_suburb'] = post.get('txtHomeSuburb','')
            values['person_home_city'] = post.get('txtHomeCity','')
            values['person_home_province_code'] = post.get('cboHomeState','')
            values['person_home_zip'] = post.get('txtHomeZip','')
            values['country_home'] = post.get('cboHomeCountry','')
#             values['person_cell_phone_number'] = post.get('txtHomeMobile','')
#             values['person_fax_number'] = post.get('txtHomeFax','')
            values['person_postal_address_1'] = post.get('txtPostalAddress1','')
            values['person_postal_address_2'] = post.get('txtPostalAddress2','')
            values['person_postal_address_3'] = post.get('txtPostalAddress3','')
            values['person_postal_suburb'] = post.get('txtPostalSuburb','')
            values['person_postal_city'] = post.get('txtPostalCity','')
            values['person_postal_province_code'] = post.get('cboPostalState','')
            values['person_postal_zip'] = post.get('txtPostalZip','')
            values['country_postal'] = post.get('cboPostalCountry','')
            values['provider_code'] = post.get('txtProviderCode','')
            values['sdf_reference_no'] = post.get('sdf_reference_no','')
            if post.get('same_address'):
                if int(str(post.get('same_address')))==1:
                    values['same_as_home']=True
                elif int(str(post.get('same_address')))==0:
                    values['same_as_home']=False            
            
            optionCount=post.get('optionCount',0);
            for i in range(0, int(optionCount)):
                tempsdl=post.get('opt'+str(i),False)
                if tempsdl:
                    employer_ids = res_partner_obj.search(cr,SUPERUSER_ID,[('employer_sdl_no','=',tempsdl)],context=context)
                    employer_obj = res_partner_obj.browse(cr,SUPERUSER_ID,employer_ids,context=context)
                    for lines in employer_obj:
                        sdf_appointment_letter='{}_sdf_appointment_letter'.format(tempsdl)
                        val = {
                                 'employer_id':lines.id,
                                 'sdl_no':lines.employer_sdl_no,
                                 'employer_seta_id':lines.employer_seta_id and lines.employer_seta_id.name,
                                 'registration_number':lines.employer_registration_number,
                                 'confirm_sdf_appointment_letter_from_employer':registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get(sdf_appointment_letter,False).filename,
                                 'datas': base64.encodestring(post.get(sdf_appointment_letter).read()),'datas_fname':post.get(sdf_appointment_letter,False).filename,}),
                                 'employer_status':'Draft'
                                 }
                        employer_line.append((0, 0, val))
            values['employer_ids'] = employer_line
            values['final_state'] = 'Draft'
            values['state'] = 'employer_info'
            todays_date = str(datetime.datetime.now().date())
            values['sdf_register_date'] = datetime.datetime.strptime(todays_date, "%Y-%m-%d").date()
            context.update({'from_website':True})
            res = sdf_reg_obj.create(cr, SUPERUSER_ID, values,context)
            ####
            dict.update({'sdf_reference_no':post.get('sdf_reference_no','NA')})
        return request.website.render("website.RegistrationConfirmationMessage",dict)
#         return request.redirect("/")
    
    @http.route(['/page/providerAccreditation'], type='http', auth="public", website=True)
    def get_aacreditationDetails(self, **post): 
        value={}
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        
        cr.execute("select id, name,saqa_qual_id,m_credits from provider_qualification where seta_branch_id = 1 order by id desc limit 10 ")
        qualification_data=cr.fetchall() 
        value.update({'qualification':qualification_data})
        value.update({'campus_qualification':qualification_data})
        
        cr.execute("select id, name,code from skills_programme where seta_branch_id = 1 order by id desc limit 10")
        skill_data=cr.fetchall() 
        value.update({'skills':skill_data})
        value.update({'campus_skills':skill_data})
        
        cr.execute("select id, name,code from etqe_learning_programme where seta_branch_id = 1 order by id desc limit 10")
        learning_data=cr.fetchall() 
        value.update({'learnings':learning_data})
        
        
        cr.execute("select id,person_name from hr_employee where is_assessors=True order by id desc limit 10")
        assessor_data=cr.fetchall() 
        value.update({'assessor':assessor_data})
        value.update({'campus_assessor':assessor_data})
                
        cr.execute("select id,person_name from hr_employee where is_moderators=True order by id desc limit 10")
        moderator_data=cr.fetchall() 
        value.update({'moderator':moderator_data})
        value.update({'campus_moderator':moderator_data})       
        
#         res_country_state_obj = registry.get('res.country.state')
#         state_ids = res_country_state_obj.search(cr,SUPERUSER_ID,[],context=context)
#         state_objs = res_country_state_obj.browse(cr,SUPERUSER_ID,state_ids,context=context)
#         value.update({'state':state_objs})
#         value.update({'state1':state_objs})
#         value.update({'state2':state_objs})
#         value.update({'state3':state_objs})
        
        cr.execute("select id, name from res_country")
        country_data=cr.fetchall()         
        value.update({'countries':country_data})
        value.update({'countries1':country_data})
        value.update({'countries2':country_data})
        value.update({'countries3':country_data})
        
#         res_city_obj = registry.get('res.city')
#         city_ids = res_city_obj.search(cr,SUPERUSER_ID,[],context=context)
#         city_objs = res_city_obj.browse(cr,SUPERUSER_ID,city_ids,context=context)
#         value.update({'city':city_objs})
#         value.update({'city1':city_objs})
#         value.update({'city2':city_objs})
#         value.update({'city3':city_objs})  
#         res_suburb_obj = registry.get('res.suburb')
#         suburb_ids = res_suburb_obj.search(cr,SUPERUSER_ID,[],context=context)
#         suburb_objs = res_suburb_obj.browse(cr,SUPERUSER_ID,suburb_ids,context=context)
#         value.update({'suburb':suburb_objs})
#         value.update({'suburb1':suburb_objs})
#         value.update({'suburb2':suburb_objs})
#         value.update({'suburb3':suburb_objs})          
        
        cr.execute("select id,code,name from hwseta_sic_master")
        sic_data=cr.fetchall()   
        value.update({'sic_data':sic_data})        
        
#         hwseta_organisation_legal_status_pool = registry.get('hwseta.organisation.legal.status')
#         hwseta_organisation_legal_status_pool_ids = hwseta_organisation_legal_status_pool.search(cr,SUPERUSER_ID,[],context=context)
#         hwseta_organisation_legal_status_pool_objs = hwseta_organisation_legal_status_pool.browse(cr,SUPERUSER_ID,hwseta_organisation_legal_status_pool_ids,context=context)
#         value.update({'organisation_legal_status':hwseta_organisation_legal_status_pool_objs})
        
        cr.execute("select id, name from hwseta_organisation_legal_status")
        hwseta_organisation_legal_status_data=cr.fetchall()        
        value.update({'organisation_legal_status':hwseta_organisation_legal_status_data})        
           
        cr.execute("select id, name from hwseta_chamber_master")
        hwseta_chamber_master_data=cr.fetchall()            
        value.update({'chamber_master':hwseta_chamber_master_data})
        
        cr.execute("select id, name from hwseta_provider_focus_master")
        hwseta_provider_focus_master_data=cr.fetchall()            
        value.update({'provider_focus':hwseta_provider_focus_master_data})
        
        cr.execute("select id, name from hwseta_relation_to_provider_status")
        hwseta_relation_to_provider_status_data=cr.fetchall() 
        value.update({'hwseta_relation_to_provider_status':hwseta_relation_to_provider_status_data})
        
#         hwseta_relation_to_provider_status_pool1 = registry.get('hwseta.relation.to.provider.status')
#         hwseta_relation_to_provider_status_ids1 = hwseta_relation_to_provider_status_pool1.search(cr,SUPERUSER_ID,[],context=context)
#         hwseta_relation_to_provider_status_objs1 = hwseta_relation_to_provider_status_pool1.browse(cr,SUPERUSER_ID,hwseta_relation_to_provider_status_ids1,context=context)
#         value.update({'hwseta_relation_to_provider_status1':hwseta_relation_to_provider_status_objs1})
        
        cr.execute("select id, name from hwseta_master")
        hwseta_master_data=cr.fetchall()
        value.update({'hwseta_master':hwseta_master_data})
        
        ir_sequence_obj = registry.get('ir.sequence')
        value.update({'provider_accreditation_ref':ir_sequence_obj.get(cr, SUPERUSER_ID,'provider.accreditation.reference')})
        
#         if post.get('filter_qualification'):
#             qualification_ids=ast.literal_eval(post.get('filter_qualification'))
#             temp=qualification_ids[0].values()
#             campus_qualification_obj=qualification.browse(cr,SUPERUSER_ID,[int(key) for key,val in ast.literal_eval(temp[0]).iteritems()])
#             if campus_qualification_obj:
#                 value.update({'campus_qualification':campus_qualification_obj})
#             else:
#                 value.update({'campus_qualification':False})
        return request.website.render("website.providerAccreditation", value)

    @http.route(['/hwseta/confirmProviderAccreditation'], type='http', auth="public", website=True)
    def confirm_accreditation(self,**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        values,dict = {},{}
        provider_accreditation_obj = registry.get('provider.accreditation')
        provider_qualification_obj = registry.get('provider.qualification')
        skill_obj = registry.get('skills.programme')
        learning_obj = registry.get('etqe.learning.programme')
        hr_employee_obj = registry.get('hr.employee')
        if post:
            if post.get('already_register')=='already_exist' :
                values['accreditation_number'] = post.get('accreditation_number')
                values['is_existing_provider'] = True
            if post.get('material'):
                values['material']=post.get('material')
            if post.get('optYesNo'):
                if str(post.get('optYesNo'))=='yes':
                    values['optYesNo']=True
                    values['alternate_acc_number']=post.get('SETA')
                elif str(post.get('optYesNo'))=='no':
                    values['optYesNo']=False                
            values['street'] = post.get('txtCmpStreet1','')
            values['street2'] = post.get('txtCmpStreet2','')
            values['street3'] = post.get('txtCmpStreet3','')
            values['provider_suburb'] = post.get('txtSuburb','')
            values['city'] = post.get('txtCmpCity','')
            if post.get('txtCmpProvince',False):
                values['state_id'] = post.get('txtCmpProvince','')
            values['zip'] = post.get('txtCmpZip','')
            if post.get('txtCmpCountry',False):
                values['country_id'] = post.get('txtCmpCountry','')
            if post['ciproDocument']:
                values['cipro_documents'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('ciproDocument','').filename,
                                                                                 'datas': base64.encodestring(post['ciproDocument'].read()),'datas_fname':post.get('ciproDocument','').filename,})                
            if post['taxDocument']:
                values['tax_clearance'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('taxDocument','').filename,
                                                                                 'datas': base64.encodestring(post['taxDocument'].read()),'datas_fname':post.get('taxDocument','').filename,})                
            if post['cvDocument']:
                values['director_cv'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('cvDocument','').filename,
                                                                                 'datas': base64.encodestring(post['cvDocument'].read()),'datas_fname':post.get('cvDocument','').filename,})
            if post['qualificationDocument']:
                values['certified_copies_of_qualifications'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('qualificationDocument','').filename,
                                                                                 'datas': base64.encodestring(post['qualificationDocument'].read()),'datas_fname':post.get('qualificationDocument','').filename,})                

            if post['lease_agreement']:
                values['lease_agreement_document'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('lease_agreement','').filename,
                                                                                 'datas': base64.encodestring(post['lease_agreement'].read()),'datas_fname':post.get('lease_agreement','').filename,})                

            if post['professional_body_registration']:
                values['professional_body_registration'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('professional_body_registration','').filename,
                                                                                 'datas': base64.encodestring(post['professional_body_registration'].read()),'datas_fname':post.get('professional_body_registration','').filename,})                
            if post['workplace_agreement']:
                values['workplace_agreement'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('workplace_agreement','').filename,
                                                                                 'datas': base64.encodestring(post['workplace_agreement'].read()),'datas_fname':post.get('workplace_agreement','').filename,})
            if post['business_residence_proof']:
                values['business_residence_proof'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('business_residence_proof','').filename,
                                                                                 'datas': base64.encodestring(post['business_residence_proof'].read()),'datas_fname':post.get('business_residence_proof','').filename,})                
            if post['provider_learning_material']:
                values['provider_learning_material'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('provider_learning_material','').filename,
                                                                                 'datas': base64.encodestring(post['provider_learning_material'].read()),'datas_fname':post.get('provider_learning_material','').filename,})                
            if post['skills_programme_registration_letter']:
                values['skills_programme_registration_letter'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('skills_programme_registration_letter','').filename,
                                                                                 'datas': base64.encodestring(post['skills_programme_registration_letter'].read()),'datas_fname':post.get('skills_programme_registration_letter','').filename,})            
            if post['company_profile_and_organogram']:
                values['company_profile_and_organogram'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('company_profile_and_organogram','').filename,
                                                                                 'datas': base64.encodestring(post['company_profile_and_organogram'].read()),'datas_fname':post.get('company_profile_and_organogram','').filename,})                
            if post['quality_management_system']:
                values['quality_management_system'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('quality_management_system','').filename,
                                                                                 'datas': base64.encodestring(post['quality_management_system'].read()),'datas_fname':post.get('quality_management_system','').filename,})                
            values['city_physical'] = post.get('txtPhysicalCity','')
            if post.get('txtPhysicalProvince',False):
                values['province_code_physical'] = post.get('txtPhysicalProvince','')
            values['zip_physical'] = post.get('txtPhysicalZip','')
            if post.get('txtPhysicalCountry',False):
                values['country_code_physical'] = post.get('txtPhysicalCountry','')
            values['provider_physical_suburb'] = post.get('txtPhysicalSuburb','')
            values['provider_postal_suburb'] = post.get('txtPostalAddressSuburb','')  
            values['city_postal'] = post.get('txtPostalAddressCity','')
            if post.get('txtPostalAddressProvince',False):
                values['province_code_postal'] = post.get('txtPostalAddressProvince','')
            values['zip_postal'] = post.get('txtPostalAddressZip','')
            if post.get('txtPostalAddressCountry',False):
                values['country_code_postal'] = post.get('txtPostalAddressCountry','')
            if post.get('same_address'):
                if int(str(post.get('same_address')))==1:
                    values['same_as_home']=True
                elif int(str(post.get('same_address')))==0:
                    values['same_as_home']=False
            values['name'] = post.get('txtRegName','')
            values['phone'] = post.get('txtCmpPhone','')
            values['mobile'] = post.get('txtContactCell','')
            values['fax'] = post.get('txtFaxNo','') 
            values['email'] = post.get('txtCmpEmail','')
            values['website'] = post.get('txtWebSite','') 
            values['txtAltContactFax'] = post.get('txtAltContactFax','')
            values['cboAltContactStatus'] = post.get('cboAltContactStatus','') 
            values['cboProviderFocus'] = post.get('cboProviderFocus','') 
            values['txtPostalAddressLine2'] = post.get('txtPostalAddressLine2','') 
            values['txtPostalAddressLine3'] = post.get('txtPostalAddressLine3','') 
            values['txtPostalAddressLine1'] = post.get('txtPostalAddressLine1','') 
            values['cboOrgSICCode'] = post.get('empl_sic_code_id','')
            values['empl_sic_code_id'] = post.get('cboOrgSICCode','')
            values['txtContactTel'] = post.get('txtContactTel','') 
#             values['SICCode'] = post.get('SICCode','') 
            values['txtEmail'] = post.get('txtEmail','') 
            values['txtRegName'] = post.get('txtRegName','')
            values['txtNumStaffMembers'] = post.get('txtNumStaffMembers','') 
            values['txtSDLNo'] = post.get('txtSDLNo','')
            values['AccreditationStatus'] = post.get('AccreditationStatus','') 
            values['txtAltContactDesignation'] = post.get('txtAltContactDesignation','')
            values['txtPhysicalAddressLine3'] = post.get('txtPhysicalAddressLine3','') 
            values['txtCompanyRegNo'] = post.get('txtCompanyRegNo','') 
            values['txtContactDesignation'] = post.get('txtContactDesignation','') 
            values['txtContactEmail'] = post.get('txtContactEmail','') 
            values['StatusReason'] = post.get('StatusReason','')
#             values['txtAltContactNameSurname'] = post.get('txtAltContactNameSurname','') 
            values['txtContactFax'] = post.get('txtContactFax','')
            values['txtContactSurname'] = post.get('txtContactSurname','') 
            values['cboTHETAChamberSelect'] = post.get('cboTHETAChamberSelect','')  
            values['txtVATRegNo'] = post.get('txtVATRegNo','') 
            values['txtStateAccNumber'] = post.get('txtStateAccNumber','')
            values['txtPostalCode'] = post.get('txtPostalCode','') 
            values['cboOrgLegalStatus'] = post.get('cboOrgLegalStatus','') 
            values['cmdNext'] = post.get('cmdNext','') 
            values['txtAltContactEmail'] = post.get('txtAltContactEmail','') 
#             values['txtWorkEmail'] = post['txtWorkEmail'] 
            values['OrgLegalStatus'] = post.get('OrgLegalStatus','') 
#             values['txtWorkPhone'] = post['txtWorkPhone'] 
            values['cboContactStatus'] = post.get('cboContactStatus','')  
            values['txtPhysicalAddressLine2'] = post.get('txtPhysicalAddressLine2','')
            values['cboSETA'] = post.get('cboSETA','')
            values['txtContactNameSurname'] = post.get('txtContactNameSurname','') 
            values['txtPhysicalCode'] = post.get('txtPhysicalCode','') 
            values['txtAltContactTel'] = post.get('txtAltContactTel','') 
            values['txtTradeName'] = post.get('txtTradeName','') 
            values['AppliedToAnotherSETA'] = post.get('AppliedToAnotherSETA','') 
            values['txtAbbrTradeName'] = post.get('txtAbbrTradeName','') 
            values['optAccStatus'] = post.get('optAccStatus','') 
            values['txtNumYearsCurrentBusiness'] = post.get('txtNumYearsCurrentBusiness','')
            values['txtPhysicalAddressLine1'] = post.get('txtPhysicalAddressLine1','')
            values['qualification_id'] = post.get('cboQualification','')
            accreditation_qualification_line=[]
            if post:
                post_len=len(post)
                i=0
                provider_campus_line=[]
                while i<=post_len:
                    i+=1
                    campus_qual='ID{}_campusqualificationids'.format(i)
                    campus_learning="ID{}_campuslearningsids".format(i)
                    campus_skill='ID{}_campusskillsids'.format(i)
                    campus_name='ID{}_campusname'.format(i)
                    campus_assessor='ID{}_campusassesorset'.format(i)
                    campus_moderator='ID{}_campusmoderatorset'.format(i)
                    campus_street='ID{}_street'.format(i)
                    campus_street2='ID{}_street2'.format(i)
                    campus_street3='ID{}_street3'.format(i)
                    campus_suburb='ID{}_suburb'.format(i)
                    campus_city='ID{}_city'.format(i)
                    campus_province='ID{}_province'.format(i)
                    campus_zip='ID{}_zip'.format(i)
                    campus_country='ID{}_country'.format(i)
                    campus_email='ID{}_email'.format(i)
                    campus_phone='ID{}_phone'.format(i)
#                     campus_mobile='ID{}_mobile'.format(i)
                    campus_fax='ID{}_fax'.format(i)
#                     campus_designation='ID{}_designation'.format(i)
#                     campus_status='ID{}_status'.format(i)
                    campus_contact_name='ID{}_txtContactNameSurname'.format(i)
                    campus_contact_email='ID{}_txtContactEmail'.format(i)
                    campus_contact_telephone='ID{}_txtContactTel'.format(i)
                    campus_contact_cell='ID{}_txtContactCell'.format(i)
                    campus_contact_surname='ID{}_txtContactSurname'.format(i)
                    campus_contact_jobtitle='ID{}_txtJobTitle'.format(i)
                    campus_assessors_list=[]
                    campus_moderators_list=[]
                    cq_vals_line = []
                    campus_assessor_vals = {}
                    if post.get(campus_assessor):
                        campus_assessor=str(post.get(campus_assessor)).split(" ")
                        campus_assessor_obj=hr_employee_obj.browse(cr,SUPERUSER_ID,[int(ids) for ids in campus_assessor if ids])
                        for hr in campus_assessor_obj:
                            campus_assessor_sla='ID_{}_assessor_agreement_campus_ID{}'.format(hr.id,i)
                            campus_assessor_vals={
                                    'assessors_id':hr.id,
                                    'awork_email':hr.work_email,
                                    'awork_phone':hr.person_cell_phone_number,
                                    'campus_assessor_sla_document':registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get(campus_assessor_sla,False).filename,
                                                                                 'datas': base64.encodestring(post.get(campus_assessor_sla,False).read()),'datas_fname':post.get(campus_assessor_sla,False).filename,})
                                    }
                            campus_assessors_list.append((0, 0,campus_assessor_vals))
                    campus_moderator_vals = {}
                    if post.get(campus_moderator):
                        campus_moderator=str(post.get(campus_moderator)).split(" ")
                        campus_moderator_obj=hr_employee_obj.browse(cr,SUPERUSER_ID,[int(ids) for ids in campus_moderator if ids])
                        for moderator_hr in campus_moderator_obj:
                            campus_moderator_sla='ID_{}_moderator_agreement_campus_ID{}'.format(moderator_hr.id,i)
                            campus_moderator_vals={
                                    'moderators_id':moderator_hr.id,
                                    'mwork_email':moderator_hr.work_email,
                                    'mwork_phone':moderator_hr.person_cell_phone_number,
                                    'campus_moderator_sla_document':registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get(campus_moderator_sla,False).filename,
                                                                                 'datas': base64.encodestring(post.get(campus_moderator_sla,False).read()),'datas_fname':post.get(campus_moderator_sla,False).filename,})
                                    }
                            campus_moderators_list.append((0, 0,campus_moderator_vals))
                    if post.get(campus_qual):
                        campus_qualification_line_list=[]
                        qualification_ids=ast.literal_eval(post.get(campus_qual))
                        qualification_id=ast.literal_eval(qualification_ids[0]['qualification_str'])
                        for key, value in qualification_id.iteritems():
                            for val in value:
                                campus_qualification_line_list.append(val)
                        idx = 0
                        for q_lines in provider_qualification_obj.browse(cr,SUPERUSER_ID,[int(key) for key, value in qualification_id.iteritems()]):
                            campus_qualification_line = []
                            for lines in q_lines.qualification_line:
                                if lines.id in campus_qualification_line_list:
                                    for data in  lines:
                                        val = {
                                             'name':data.name,
                                             'type':data.type,
                                             'id_no':data.id_no,
                                             'title':data.title,
                                             'level1':data.level1,
                                             'level2':data.level2,
                                             'level3': data.level3,
                                              'selection':True,
                                              'is_seta_approved':data.is_seta_approved,
                                              'is_provider_approved':data.is_provider_approved,
                                            }
                                        campus_qualification_line.append((0, 0, val))
                            q_vals = {
                                        'qualification_id':q_lines.id,
                                        'saqa_qual_id':q_lines.saqa_qual_id,
                                        'qualification_line':campus_qualification_line,
                                        }
                            if campus_assessor_vals:
                                q_vals.update({                                
                                        'assessors_id':campus_assessors_list[idx][2]['assessors_id'],
                                        'assessor_sla_document':campus_assessors_list[idx][2]['campus_assessor_sla_document'],
                                        })
                            if campus_moderator_vals:
                                q_vals.update({                                
                                            'moderators_id':campus_moderators_list[idx][2]['moderators_id'],
                                            'moderator_sla_document':campus_moderators_list[idx][2]['campus_moderator_sla_document'],
                                            })
                            cq_vals_line.append((0, 0, q_vals))
                            #idx += 1
                    cs_vals_line = []
                    if post.get(campus_skill):
                        campus_skill_line_list=[]
                        skill_ids=ast.literal_eval(post.get(campus_skill))
                        skill_id=ast.literal_eval(skill_ids[0]['skill_str'])
                        for key, value in skill_id.iteritems():
                            for val in value:
                                campus_skill_line_list.append(val)
                        for s_lines in skill_obj.browse(cr,SUPERUSER_ID,[int(key) for key, value in skill_id.iteritems()]):
                            campus_skill_line = []
                            for lines in s_lines.unit_standards_line:
                                if lines.id in campus_skill_line_list:
                                    for data in  lines:
                                        val = {
                                             'name':data.name,
                                             'type':data.type,
                                             'id_no':data.id_no,
                                             'title':data.title,
                                             'level1':data.level1,
                                             'level2':data.level2,
                                             'level3': data.level3,
                                              'selection':True,
                                            }
                                        campus_skill_line.append((0, 0, val))
                            cs_vals = {
                                          'skills_programme_id':s_lines.id,
                                          'saqa_skill_id':s_lines.saqa_qual_id,
                                          'unit_standards_line':campus_skill_line,
                                        }
                            cs_vals_line.append((0, 0, cs_vals)) 
                    #Added by shoaib
                    cl_vals_line = []
                    if post.get(campus_learning):
                        campus_learning_line_list=[]
                        learning_ids=ast.literal_eval(post.get(campus_learning))
                        learning_id=ast.literal_eval(learning_ids[0]['learnings_str'])
                        for key, value in learning_id.iteritems():
                            for val in value:
                                campus_learning_line_list.append(val)
                        for l_lines in learning_obj.browse(cr,SUPERUSER_ID,[int(key) for key, value in learning_id.iteritems()]):
                            campus_learning_line = []
                            for lines in l_lines.unit_standards_line:
                                if lines.id in campus_learning_line_list:
                                    for data in lines:
                                        val = {
                                             'name':data.name,
                                             'type':data.type,
                                             'id_no':data.id_no,
                                             'title':data.title,
                                             'level1':data.level1,
                                             'level2':data.level2,
                                             'level3': data.level3,
                                              'selection':True,
                                              'seta_approved_lp':data.seta_approved_lp,
                                              'provider_approved_lp':data.provider_approved_lp,
                                            }
                                        campus_learning_line.append((0, 0, val))
                            cl_vals = {
                                          'learning_programme_id':l_lines.id,
                                          'saqa_qual_id':l_lines.saqa_qual_id,
                                          'unit_standards_line':campus_learning_line,
                                        }
                            cl_vals_line.append((0, 0, cl_vals))

                    campus_contact_vals={
                                         'name':post.get(campus_contact_name) or '',
                                         'email':post.get(campus_contact_email) or '',
                                         'mobile':post.get(campus_contact_cell) or '',
                                         'phone':post.get(campus_contact_telephone) or '',
                                         'sur_name':post.get(campus_contact_surname) or '',
                                         'designation':post.get(campus_contact_jobtitle) or '',
                                         }
                    campus_contact_list=[]
                    campus_contact_list.append((0,0,campus_contact_vals))
                    if post.get(campus_name):
                        provider_campus_data = {
                                             'name':post.get(campus_name),
                                             'street':post.get(campus_street),
                                             'street2':post.get(campus_street2),
                                             'street3':post.get(campus_street3),
                                             'suburb':post.get(campus_suburb),
                                             'zip':post.get(campus_zip),
                                             'city':post.get(campus_city),
                                             'state_id':post.get(campus_province),
                                             'country_id':post.get(campus_country),
                                             'email': post.get(campus_email),
                                             'phone':post.get(campus_phone),
#                                              'mobile': post.get(campus_mobile),
                                             'fax':post.get(campus_fax),
#                                              'designation':post.get(campus_designation),
#                                              'status':post.get(campus_status),                                               
                                             'qualification_ids':cq_vals_line,
                                             'skills_programme_ids':cs_vals_line,
                                             'learning_programme_ids':cl_vals_line,
                                            'assessors_ids':campus_assessors_list,
                                            'moderators_ids':campus_moderators_list,
                                            'provider_accreditation_campus_contact_ids':campus_contact_list
                                            }  
                        provider_campus_line.append((0,0,provider_campus_data))                                              
            values['provider_accreditation_campus_ids']=provider_campus_line                            
            values['assessors_id'] = post.get('cboAssessor','')
            values['moderators_id'] = post.get('cboModerator','')
            contact_data=[]
            line_vals = {
                            'name':post['txtContactNameSurname'],
                            'designation':post['txtJobTitle'],
                            'phone':post['txtContactTel'],
#                            'fax':post['txtContactFax'],
                            'email':post['txtContactEmail'],
                            'mobile':post['txtContactCell'],
#                             'status':post['cboContactStatus'],
                            'sur_name':post['txtContactSurname'],
                        }
            contact_data.append( ( 0, 0, line_vals ) )
#             line_vals = {
#                             'name':post['txtAltContactNameSurname'],
#                             'designation':post['txtAltContactDesignation'],
#                             'phone':post['txtAltContactTel'],
#                             'fax':post['txtAltContactFax'],
#                             'email':post['txtAltContactEmail'],
#                             'status':post['cboAltContactStatus'],
#                         }
#             contact_data.append( ( 0, 0, line_vals ) )
#             line_vals = {
#                             'name':post['txtCmpName'],
#                             'phone':post['txtCmpPhone'],
#                             'email':post['txtCmpEmail'],
#                             
#                         }
#             contact_data.append( ( 0, 0, line_vals ) )
            values['provider_accreditation_contact_ids']=contact_data
#             if values['assessors_id']:
#                 employee_objs = hr_employee_obj.browse(cr,SUPERUSER_ID,int(values['assessors_id']),context=context)
#                 values['awork_email'] = employee_objs.work_email
#                 values['awork_phone'] = employee_objs.work_phone
#                 
#             if values['moderators_id']:
#                 employee_objs = hr_employee_obj.browse(cr,SUPERUSER_ID,int(values['moderators_id']),context=context)
#                 values['mwork_email'] = employee_objs.work_email
#                 values['mwork_phone'] = employee_objs.work_phone
            assessor_line=[]
            assessor_vals = {}
            if post.get('assesor'):
                assessor=str(post.get('assesor')).split(" ")
                assessor_obj=hr_employee_obj.browse(cr,SUPERUSER_ID,[int(ids) for ids in assessor if ids])
                for hr in assessor_obj:
                    assessor_sla_dcument_key=''
                    assessor_notification_key=''
                    for key, value in post.iteritems():   # iter on both keys and values
                        if key.endswith('assessor_agreement'):
                            sla_document_key=key.split("_")
                            if int(str(sla_document_key[1]))==hr.id:
                                assessor_sla_dcument_key=key
                        if key.endswith('assessor_notification'):
                            notification_key=key.split("_")
                            if int(str(notification_key[1]))==hr.id:
                                assessor_notification_key=key    

                    assessor_vals={
                            'assessors_id':hr.id,
                            'awork_email':hr.work_email,
                            'awork_phone':hr.person_cell_phone_number,
                            'assessor_sla_document':registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get(assessor_sla_dcument_key).filename,
                                                                                 'datas': base64.encodestring(post.get(assessor_sla_dcument_key).read()),'datas_fname':post.get(assessor_sla_dcument_key).filename,}),
                            'assessor_notification_letter':registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get(assessor_notification_key).filename,
                                                                                 'datas': base64.encodestring(post.get(assessor_notification_key).read()),'datas_fname':post.get(assessor_notification_key).filename,})
                            }
                    assessor_line.append((0, 0, assessor_vals))
                values['assessors_ids'] = assessor_line
            moderator_line=[]
            moderator_vals = {}
            if post.get('moderator'):
                moderator=str(post.get('moderator')).split(" ")
                moderator_obj=hr_employee_obj.browse(cr,SUPERUSER_ID,[int(ids) for ids in moderator if ids])
                for hr_moderator in moderator_obj:
                    moderator_sla_document_key=''
                    moderator_notification_key=''
                    for key, value in post.iteritems():   # iter on both keys and values
                        if key.endswith('moderator_agreement'):
                            sla_document_key=key.split("_")
                            if int(str(sla_document_key[1]))==hr_moderator.id:
                                moderator_sla_document_key=key                       
                        if key.endswith('moderator_notification'):
                            notification_document_key=key.split("_")
                            if int(str(notification_document_key[1]))==hr_moderator.id:
                                moderator_notification_key=key                       

                    moderator_vals={
                            'moderators_id':hr_moderator.id,
                            'mwork_email':hr_moderator.work_email,
                            'mwork_phone':hr_moderator.person_cell_phone_number,
                            'moderator_sla_document':registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get(moderator_sla_document_key).filename,
                                                                                 'datas': base64.encodestring(post.get(moderator_sla_document_key).read()),'datas_fname':post.get(moderator_sla_document_key).filename,}),                            
                            'moderator_notification_letter':registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get(moderator_notification_key).filename,
                                                                                 'datas': base64.encodestring(post.get(moderator_notification_key).read()),'datas_fname':post.get(moderator_notification_key).filename,})                            

                            }
                    moderator_line.append((0, 0, moderator_vals))
                values['moderators_ids'] = moderator_line

            q_vals_line = []
            if post.get('qualification_idss'):
                qualification_line_list=[]
                qualification_ids=ast.literal_eval(post.get('qualification_idss'))
                qualification_id=ast.literal_eval(qualification_ids[0]['qualification_str'])
                for key, value in qualification_id.iteritems():
                    for val in value:
                        qualification_line_list.append(val)
                idx = 0
                for q_lines in provider_qualification_obj.browse(cr,SUPERUSER_ID,[int(key) for key, value in qualification_id.iteritems()]):
                    provider_qualification_line = []
                    for lines in q_lines.qualification_line:
                        if lines.id in qualification_line_list:
                            for data in  lines:
                                val = {
                                     'name':data.name,
                                     'type':data.type,
                                     'id_no':data.id_no,
                                     'title':data.title,
                                     'level1':data.level1,
                                     'level2':data.level2,
                                     'level3': data.level3,
                                      'selection': True,
                                      'is_seta_approved':data.is_seta_approved,
                                      'is_provider_approved':data.is_provider_approved,
                                    }
                                provider_qualification_line.append((0, 0, val))
#                     assessor_line.append((0, 0,assessor_vals))
#                     moderator_line.append((0, 0,moderator_vals))
                    q_vals = {
                                'qualification_id':q_lines.id,
                                'saqa_qual_id':q_lines.saqa_qual_id,
                                'qualification_line':provider_qualification_line,
                                }
                    if assessor_vals:
                        q_vals.update({                                
                                    'assessors_id':assessor_line[idx][2]['assessors_id'],
                                    'assessor_sla_document':assessor_line[idx][2]['assessor_sla_document'],
                                    })
                    if moderator_vals:
                        q_vals.update({                                
                                    'moderators_id':moderator_line[idx][2]['moderators_id'],
                                    'moderator_sla_document':moderator_line[idx][2]['moderator_sla_document'],
                                    })
                    q_vals_line.append((0, 0, q_vals))
                    #idx += 1
            s_vals_line = []
            if post.get('skill_idss'):
                skill_line_list=[]
                skill_ids=ast.literal_eval(post.get('skill_idss'))
                skill_id=ast.literal_eval(skill_ids[0]['skill_str'])
                for key, value in skill_id.iteritems():
                    for val in value:
                        skill_line_list.append(val)
                idx = 0
                for s_lines in skill_obj.browse(cr,SUPERUSER_ID,[int(key) for key, value in skill_id.iteritems()]):
                    provider_skill_line = []
                    for lines in s_lines.unit_standards_line:
                        if lines.id in skill_line_list:
                            for data in  lines:
                                val = {
                                     'name':data.name,
                                     'type':data.type,
                                     'id_no':data.id_no,
                                     'title':data.title,
                                     'level1':data.level1,
                                     'level2':data.level2,
                                     'level3': data.level3,
                                      'selection':True,
                                    }
                                provider_skill_line.append((0, 0, val))
                    s_vals = {
                                'skills_programme_id':s_lines.id,
                                'saqa_skill_id':s_lines.saqa_qual_id,
                                'unit_standards_line':provider_skill_line,
                                }
                    if assessor_vals:
                        s_vals.update({                                
                                    'assessors_id':assessor_line[idx][2]['assessors_id'],
                                    'assessor_sla_document':assessor_line[idx][2]['assessor_sla_document'],
                                    })
                    if moderator_vals:
                        s_vals.update({                                
                                    'moderators_id':moderator_line[idx][2]['moderators_id'],
                                    'moderator_sla_document':moderator_line[idx][2]['moderator_sla_document'],
                                    })
                    s_vals_line.append((0, 0, s_vals))
                    #idx += 1

            #Added by shoaib
            l_vals_line = []
            if post.get('learning_idss'):
                learning_line_list=[]
                learning_ids=ast.literal_eval(post.get('learning_idss'))
                learning_id=ast.literal_eval(learning_ids[0]['learnings_str'])
                for key, value in learning_id.iteritems():
                    for val in value:
                        learning_line_list.append(val)
                idx = 0
                for l_lines in learning_obj.browse(cr,SUPERUSER_ID,[int(key) for key, value in learning_id.iteritems()]):
                    provider_learning_line = []
                    for lines in l_lines.unit_standards_line:
                        if lines.id in learning_line_list:
                            for data in  lines:
                                val = {
                                     'name':data.name,
                                     'type':data.type,
                                     'id_no':data.id_no,
                                     'title':data.title,
                                     'level1':data.level1,
                                     'level2':data.level2,
                                     'level3': data.level3,
                                      'selection':True,
                                      'seta_approved_lp':data.seta_approved_lp,
                                      'provider_approved_lp':data.provider_approved_lp,
                                    }
                                provider_learning_line.append((0, 0, val))
                    l_vals = {
                                'learning_programme_id':l_lines.id,
                                'saqa_qual_id':l_lines.saqa_qual_id,
                                'unit_standards_line':provider_learning_line,
                                }
                    if assessor_vals:
                        l_vals.update({
                                    'assessors_id':assessor_line[idx][2]['assessors_id'],
                                    'assessor_sla_document':assessor_line[idx][2]['assessor_sla_document'],
                                    })
                    if moderator_vals:
                        l_vals.update({
                                    'moderators_id':moderator_line[idx][2]['moderators_id'],
                                    'moderator_sla_document':moderator_line[idx][2]['moderator_sla_document'],
                                    })
                    l_vals_line.append((0, 0, l_vals))
                    #idx += 1
            doc_vals = []
            if post.get('Document1') and post.get('Document2') and post.get('optYesNo') == 'yes':
                doc_list = [post.get('Document1'),post.get('Document2')]
                for doc in doc_list:
                    val = {
                           'name':doc.filename,
                           'doc_file':registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : doc.filename,
                                                                                     'datas': base64.encodestring(doc.read()),'datas_fname':doc.filename,})
                           }
                    doc_vals.append((0, 0, val))
            
            todays_date = str(datetime.datetime.now().date())
            values['provider_register_date'] = datetime.datetime.strptime(todays_date, "%Y-%m-%d").date()                
            context.update({'from_website':True})
            res = provider_accreditation_obj.create(cr,SUPERUSER_ID,values,context)
#             if q_vals_line:
#                 provider_accreditation_obj.browse(cr,SUPERUSER_ID,res).write({'qualification_ids':q_vals_line,'skills_programme_ids':s_vals_line,'provider_accreditation_ref':post.get('provider_accreditation_ref',''),'acc_multi_doc_upload_ids':doc_vals})
            provider_accreditation_obj.browse(cr,SUPERUSER_ID,res).write({'qualification_ids':q_vals_line,'skills_programme_ids':s_vals_line,'learning_programme_ids':l_vals_line,'provider_accreditation_ref':post.get('provider_accreditation_ref',''),'acc_multi_doc_upload_ids':doc_vals})
        
            dict.update({'provider_accreditation_ref':post.get('provider_accreditation_ref','NA')})
        return request.website.render("website.RegistrationConfirmationMessage",dict)
        #return request.redirect("/")    
 
    @http.route(['/page/assessorModerator'], type='http', auth="public", website=True)
    def get_assessorModeratorDetails(self, **post): 
        value={}
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        
        cr.execute("select id, name from res_country")
        country_data = cr.fetchall() 
        cr.commit()  
        value.update({'countries':country_data})
        value.update({'countries1':country_data})
        value.update({'countries2':country_data})
        value.update({'countries3':country_data})
        
        cr.execute("select id, name,saqa_qual_id from provider_qualification where seta_branch_id = 1 or is_ass_mod_linked = True order by id desc limit 100 ")
        qualification_data=cr.fetchall() 
        value.update({'qualification':qualification_data})
        
#         res_country_state_obj = registry.get('res.country.state')
#         state_ids = res_country_state_obj.search(cr,SUPERUSER_ID,[],context=context)
#         state_objs = res_country_state_obj.browse(cr,SUPERUSER_ID,state_ids,context=context)
#         value.update({'state':state_objs})
#         value.update({'state1':state_objs})
#         value.update({'state2':state_objs})
#         
#         res_city_obj = registry.get('res.city')
#         city_ids = res_city_obj.search(cr,SUPERUSER_ID,[],context=context)
#         city_objs = res_city_obj.browse(cr,SUPERUSER_ID,city_ids,context=context)
#         value.update({'city':city_objs})
#         value.update({'city1':city_objs})
#         value.update({'city2':city_objs})  
#         value.update({'city3':city_objs})        
#         res_suburb_obj = registry.get('res.suburb')
#         suburb_ids = res_suburb_obj.search(cr,SUPERUSER_ID,[],context=context)
#         suburb_objs = res_suburb_obj.browse(cr,SUPERUSER_ID,suburb_ids,context=context)
#         value.update({'suburb':suburb_objs})
#         value.update({'suburb1':suburb_objs})
#         value.update({'suburb2':suburb_objs})
#         value.update({'suburb3':suburb_objs})
        cr.execute("select id, name from res_lang")
        lang_data = cr.fetchall()             
        value.update({'language':lang_data})               
#         ir_sequence_obj = registry.get('ir.sequence')
#         value.update({'assessors_moderators_ref':ir_sequence_obj.get(cr, SUPERUSER_ID,'assessors.moderators.reference')})
#         if post.get('qualification_id'):
#             qualification_id = qualification.search(cr,SUPERUSER_ID,[('id','=',post.get('qualification_id'))],context=context)
#             if qualification_id:
#                 qualification_obj = qualification.browse(cr,SUPERUSER_ID,qualification_id,context=context)
#                 value.update({'qualification_selected':qualification_obj})
        return request.website.render("website.assessorModerator", value)
        
    @http.route(['/hwseta/confirmAssessorModerator'], type='http', auth="public", website=True)
    def confirm_assessor_moderator(self,**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        provider_qualification=registry.get('provider.qualification')
        qualification_obj = registry.get('provider.qualification')
        qualification_line_obj = registry.get('provider.qualification.line')
        assessors_moderators_register_obj = registry.get('assessors.moderators.register')
        qualification_list = []
        values,dict = {},{} 
        if post:
#             values ['assessors_moderators_ref'] = post.get('assessors_moderators_ref','')
            values['name'] = post.get('name','')
            values['tags'] = post.get('tags','')
            values['work_email'] = post.get('email','')
            values['person_cell_phone_number'] = post.get('phone_number','')
            if post.get('radioAssMod',False) and post.get('radioAssMod') == 'already_registered' and post.get('ex_ass_mod') == 'ex_ass':
                values['already_registered'] = True
                values['search_by'] = 'number'
                values['existing_assessor_moderator'] = 'ex_assessor'
                values['assessors_moderators_ref'] = post.get('assessors_moderators_ref','')
            if post.get('radioAssMod',False) and post.get('radioAssMod') == 'already_registered' and post.get('ex_ass_mod') == 'ex_mod':
                values['already_registered'] = True
                values['search_by'] = 'number'
                values['existing_assessor_moderator'] = 'ex_moderator'
                values['assessors_moderators_ref'] = post.get('assessors_moderators_ref','')
            if post.get('radioAssMod',False) and post.get('radioAssMod') == 'assessor':
                values ['is_assessors'] = True
                if post['txtIdDocument']:
                    values['id_document'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('txtIdDocument','').filename,
                                                                                     'datas': base64.encodestring(post['txtIdDocument'].read()),'datas_fname':post.get('txtIdDocument','').filename,})
                if post['registrationDoc']:
                    values['registrationdoc'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('registrationDoc','').filename,
                                                                                     'datas': base64.encodestring(post['registrationDoc'].read()),'datas_fname':post.get('registrationDoc','').filename,})                
                if post['professionalbodyDoc']:
                    values['professionalbodydoc'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('professionalbodyDoc','').filename,
                                                                                     'datas': base64.encodestring(post['professionalbodyDoc'].read()),'datas_fname':post.get('professionalbodyDoc','').filename,})                
                if post['SRAM_Doc']:
                    values['sram_doc'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('SRAM_Doc','').filename,
                                                                                 'datas': base64.encodestring(post['SRAM_Doc'].read()),'datas_fname':post.get('SRAM_Doc','').filename,})
                if post.get('type_document',False):
                    values['unknown_type_document'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('type_document','').filename,
                                                                                 'datas': base64.encodestring(post['type_document'].read()),'datas_fname':post.get('type_document','').filename,})
                if post['cv_document']:
                    values['cv_document'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('cv_document','').filename,
                                                                                 'datas': base64.encodestring(post['cv_document'].read()),'datas_fname':post.get('cv_document','').filename,})
                                                        
                values['assessor_moderator']='assessor'
            if post.get('radioAssMod',False) and post.get('radioAssMod') == 'moderator':
                values ['is_moderators'] = True
                values['assessor_moderator']='moderator'
                if post['txtIdDocument']:
                    values['id_document'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('txtIdDocument','').filename,
                                                                                     'datas': base64.encodestring(post['txtIdDocument'].read()),'datas_fname':post.get('txtIdDocument','').filename,})
                else:
                    if post['txtIdDocument_mod']:
                        values['id_document'] =int(str(post['txtIdDocument_mod']))    
                if post['registrationDoc']:
                    values['registrationdoc'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('registrationDoc','').filename,
                                                                                     'datas': base64.encodestring(post['registrationDoc'].read()),'datas_fname':post.get('registrationDoc','').filename,})
                else:
                    if post['registrationDoc_mod']:
                        values['registrationdoc'] =int(str(post['registrationDoc_mod']))                     
                if post['professionalbodyDoc']:
                    values['professionalbodydoc'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('professionalbodyDoc','').filename,
                                                                                    'datas': base64.encodestring(post['professionalbodyDoc'].read()),'datas_fname':post.get('professionalbodyDoc','').filename,})
                else:    
                    if post['professionalbodyDoc_mod']:
                        values['professionalbodydoc'] =int(str(post['professionalbodyDoc_mod']))                                      
                if post['SRAM_Doc']:
                    values['sram_doc'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('SRAM_Doc','').filename,
                                                                                 'datas': base64.encodestring(post['SRAM_Doc'].read()),'datas_fname':post.get('SRAM_Doc','').filename,})
                else:
                    if post['SRAM_Doc_mod']:
                        values['sram_doc'] = int(str(post['SRAM_Doc_mod']))                     
                if post.get('type_document',False):
                    values['unknown_type_document'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('type_document','').filename,
                                                                                 'datas': base64.encodestring(post['type_document'].read()),'datas_fname':post.get('type_document','').filename,})
                else:
                    if post.get('type_document_mod'):
                        values['unknown_type_document'] =int(str(post['type_document_mod']))                     
                if post['cv_document']:
                    values['cv_document'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('cv_document','').filename,
                                                                                 'datas': base64.encodestring(post['cv_document'].read()),'datas_fname':post.get('cv_document','').filename,})
                else:
                    if post.get('cv_document_mod'):
                        values['cv_document'] =int(str(post['cv_document_mod']))    

            if post.get('radioPC',''):
                if post.get('radioPC','')=='Permanent':
                    values['type']='permanent'
                    if post.get('organisation_id'):
                        values['organisation']=int(str(post.get('organisation_id')))
                    values['organisation_sdl_no']=post.get('organisation_sdl_no')
                if post.get('radioPC','')=='Consultant':
                    values['type']='consultant'
            if post.get('unknown_type',''):                    
                if post.get('unknown_type','')=='political_asylum':
                    values['unknown_type']='political_asylum'    
                if post.get('unknown_type','')=='refugee':
                    values['unknown_type']='refugee' 
                
            if post.get('assesor_number',''):
                values['assessor_id']=post.get('assesor_number','')
            values ['work_address'] = post.get('add_line1','')
            values ['work_address2'] = post.get('add_line2','')
            values ['work_address3'] = post.get('add_line3','')
            values ['work_city'] = post.get('city','')
            values ['work_zip'] = post.get('zip','')
            values ['work_province'] = post.get('p_country','')
            values ['work_country'] = post.get('country','')
            values ['mobile_phone'] = post.get('mobile','')
            values ['department'] = post.get('department','')
            values ['job_title'] = post.get('job_title','')
            values ['manager'] = post.get('manager','')
            values ['notes'] = post.get('note','')
            values ['country_id'] = post.get('nationality','')
            values ['identification_id'] = post.get('id_no','')
            values ['passport_id'] = post.get('pass_no','')
            values ['bank_account_number'] = post.get('bank_no','')
            values ['otherid'] = post.get('other_id','')
            values ['national_id'] = post.get('nat_id','')
            values ['home_language_code'] = post.get('home_lang','')
            values ['citizen_resident_status_code'] = post.get('cit_res','')
            values ['filler01'] = post.get('fil','')
            values ['address_home'] = post.get('home_add','')
            values ['person_alternate_id'] = post.get('alt_id','')
            values ['alternate_id_type_id'] = post.get('type_id','')
            values ['equity_code'] = post.get('eq_code','')
            values ['filler02'] = post.get('fil0','')
            values ['person_middle_name'] = post.get('mid_name','')
            values ['person_last_name'] = post.get('last_name','')
            values ['person_title'] = post.get('title','')
            values ['gender'] = post.get('gender','')
            values ['marital'] = post.get('marital','')
            if post.get('birth_date','') != '':
                values ['birthday'] = post.get('birth_date','')
            values ['person_home_address_1'] = post.get('home_line1','')
            values ['person_home_address_2'] = post.get('home_line2','')
            values ['person_home_address_3'] = post.get('home_line3','')
            values ['person_home_city'] = post.get('home_city','')
            values ['person_home_province_code'] = post.get('home_p_country','')
            values ['person_home_zip'] = post.get('home_zip','')
            values ['country_home'] = post.get('home_country','')
            values ['person_postal_address_1'] = post.get('postal_line1','')
            values ['person_postal_address_2'] = post.get('postal_line2','')
            values ['person_postal_address_3'] = post.get('postal_line3','')
            values ['person_postal_city'] = post.get('postal_city','')
            values ['person_postal_province_code'] = post.get('postal_p_country','')
            values ['person_postal_zip'] = post.get('postal_zip','')
            values ['country_postal'] = post.get('postal_country','')
            values['qualification_id'] = post.get('cboQualification','')
#             if post['txtIdDocument']:
#                 values['id_document'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('txtIdDocument','').filename,
#                                                                                  'datas': base64.encodestring(post['txtIdDocument'].read()),'datas_fname':post.get('txtIdDocument','').filename,})
#             if post['registrationDoc']:
#                 values['registrationdoc'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('registrationDoc','').filename,
#                                                                                  'datas': base64.encodestring(post['registrationDoc'].read()),'datas_fname':post.get('registrationDoc','').filename,})                
#             if post['professionalbodyDoc']:
#                 values['professionalbodydoc'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('professionalbodyDoc','').filename,
#                                                                                  'datas': base64.encodestring(post['professionalbodyDoc'].read()),'datas_fname':post.get('professionalbodyDoc','').filename,})                
#             if post['SRAM_Doc']:
#                 values['sram_doc'] =registry.get('ir.attachment').create(cr, SUPERUSER_ID, {'name' : post.get('SRAM_Doc','').filename,
#                                                                                  'datas': base64.encodestring(post['SRAM_Doc'].read()),'datas_fname':post.get('SRAM_Doc','').filename,})                
                                                                                           
            values['person_suburb'] = post.get('txtWorkSuburb','')
            values['person_home_suburb'] = post.get('txtHomeSuburb','')
            values['person_postal_suburb'] = post.get('txtPostalSuburb','')
            values['cont_number_office'] = post.get('txtCntNoOffice','')
            values['cont_number_home'] = post.get('txtCntNoHome','')
            values['person_name'] = post.get('name','')
            values['person_last_name'] = post.get('txtSurname','')
            values['person_title'] = post.get('title','')
            values['dissability'] = post.get('disability','')
            if post.get('birth_date_value',''):
                values['person_birth_date']=datetime.datetime.strptime(post.get('birth_date_value',''), "%m/%d/%Y")
            values ['state']="general_info"
            if post.get('address'):
                if int(str(post.get('address')))==1:
                    values['same_as_home']=True
                elif int(str(post.get('address')))==0:
                    values['same_as_home']=False
            q_vals_line = []
            if post.get('qualification_idss'):
                qualification_line_list=[]
                qualification_ids=ast.literal_eval(post.get('qualification_idss'))
                qualification_id=ast.literal_eval(qualification_ids[0]['qualification_str'])
                for key, value in qualification_id.iteritems():
                    qualification_list.append(key)
                    for val in value:
                        qualification_line_list.append(val)
                for q_lines in qualification_obj.browse(cr,SUPERUSER_ID,[int(key) for key, value in qualification_id.iteritems()]):
                    assessors_moderators_qualification_line = []
                    for lines in q_lines.qualification_line:
                        if lines.id in qualification_line_list:
                            for data in  lines:
                                val = {
                                     'name':data.name,
                                     'type':data.type,
                                     'id_no':data.id_no,
                                     'title':data.title,
                                     'level1':data.level1,
                                     'level2':data.level2,
                                     'level3': data.level3,
                                      'selection':True,
                                    }
                                assessors_moderators_qualification_line.append((0, 0, val))
                    q_vals = {
                                'qual_unit_type': 'qual',
                                'qualification_id':q_lines.id,
                                'saqa_qual_id':q_lines.saqa_qual_id,
                                'qualification_line':assessors_moderators_qualification_line,
                                }
                    q_vals_line.append((0, 0, q_vals))
            if post.get('qualification_unit_idss'):
                qualification_line_list=[]
                qualification_ids=ast.literal_eval(post.get('qualification_unit_idss'))
                qualification_id=ast.literal_eval(qualification_ids[0]['qualification_unit_str'])
                for qual in qualification_list:
                    if qualification_id.get(qual):
                        del qualification_id[qual]
                for key, value in qualification_id.iteritems():
                    for val in value:
                        qualification_line_list.append(val)
                for q_lines in qualification_obj.browse(cr,SUPERUSER_ID,[int(key) for key, value in qualification_id.iteritems()]):
                    assessors_moderators_qualification_line = []
                    for lines in q_lines.qualification_line:
                        if lines.id in qualification_line_list:
                            for data in  lines:
                                val = {
                                     'name':data.name,
                                     'type':data.type,
                                     'id_no':data.id_no,
                                     'title':data.title,
                                     'level1':data.level1,
                                     'level2':data.level2,
                                     'level3': data.level3,
                                     'selection':True,
                                    }
                                assessors_moderators_qualification_line.append((0, 0, val))
                    q_vals = {
                                'qual_unit_type': 'unit',
                                'qualification_id':q_lines.id,
                                'saqa_qual_id':q_lines.saqa_qual_id,
                                'qualification_line':assessors_moderators_qualification_line,
                                }
                    q_vals_line.append((0, 0, q_vals))
            context.update({'from_website1':True})  
            todays_date = str(datetime.datetime.now().date())
            values['assessor_moderator_register_date'] = datetime.datetime.strptime(todays_date, "%Y-%m-%d").date()
            res=assessors_moderators_register_obj.create(cr,SUPERUSER_ID,values,context)
            assessors_moderators_register_obj.write(cr,SUPERUSER_ID,res,{'qualification_ids':q_vals_line,'assessors_moderators_ref':post.get('assessors_moderators_ref','')})
            
            dict.update({'assessors_moderators_ref':post.get('assessors_moderators_ref','NA')})
            if post.get('radioAssMod') == 'assessor':
                dict['assessor'] = True
            elif post.get('radioAssMod') == 'moderator':
                dict['moderator'] = True
        return request.website.render("website.RegistrationConfirmationMessage",dict)
    
    @http.route(['/hwseta/validate_minimum_credit'], type='http', auth="public", website=True)    
    def validate_minimum_credit(self,**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result=[]
        if not post.get('unit_line_ids'):
            result.append({'check_limit':False})
            return json.dumps(result)
        if post.get('qual_ids') and post.get('unit_line_ids'): 
            qual_obj=registry.get('provider.qualification')
            qual_id =qual_obj.search(cr,SUPERUSER_ID, [('id','=',str(post.get('qual_ids')))], context=context)
            if qual_id:
                qual_data =qual_obj.browse(cr,SUPERUSER_ID,qual_id,context=context)
            unit_line_list = []
            for unit_id in str(post.get('unit_line_ids')).split(',')[:-1]:
                unit_line_list.append(int(unit_id))
            qual_line_obj=registry.get('provider.qualification.line')
            qual_line_ids =qual_line_obj.search(cr,SUPERUSER_ID, [('id','in',unit_line_list)], context=context)    
            if qual_line_ids:
                qual_line_data =qual_line_obj.browse(cr,SUPERUSER_ID,qual_line_ids,context=context)
                checked_credit_sum = 0
                for q_line_obj in qual_line_data:
                    checked_credit_sum += int(q_line_obj.level3)
                    
            if checked_credit_sum < qual_data.m_credits:
                result.append({'check_limit':False})
            elif not checked_credit_sum < qual_data.m_credits:
                result.append({'check_limit': True})
            return json.dumps(result)
        return False
    
    @http.route(['/hwseta/qualification_assessor_moderator'], type='http', auth="public", website=True)    
    def qualification_assessor_moderator(self,**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result=[]
        if post:
            result.append({'qualification_str':post.keys()[0]})
            return json.dumps(result)
        return False
    
    @http.route(['/hwseta/qualification_unit_assessor_moderator'], type='http', auth="public", website=True)    
    def qualification_unit_assessor_moderator(self,**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result=[]
        if post:
            result.append({'qualification_unit_str':post.keys()[0]})
            return json.dumps(result)
        return False
    
    @http.route(['/hwseta/providerAccreditation/skills'], type='http', auth="public", website=True)    
    def skills(self,**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result=[]
        if post:
            result.append({'skill_str':post.keys()[0]})
            return json.dumps(result)
        return False
    
    @http.route(['/hwseta/providerAccreditation/learnings'], type='http', auth="public", website=True)    
    def learnings(self,**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result=[]
        if post:
            result.append({'learnings_str':post.keys()[0]})
            return json.dumps(result)
        return False
    
    @http.route(['/page/assessorModerator/validate_assesor_number'], type='http', auth="public", website=True)
    def validate_assesor_number(self,search='',**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result=[]
        vals={}
        assessor_obj=registry.get('hr.employee')
        provider_obj=registry.get('provider.qualification')
        assessors_id =assessor_obj.search(cr,SUPERUSER_ID, [('assessor_seq_no','=',str(post['assesor_number']))], context=context)
        if assessors_id:
            data_assesor=assessor_obj.browse(cr,SUPERUSER_ID,assessors_id,context=context)
            for data in data_assesor:
                vals={
                      'type':data.type or '',
                      'name':data.name,
                      'surname':data.person_last_name,
                      'work_email':data.work_email,
                      'person_cell_phone_number':data.person_cell_phone_number,
                      'title':data.person_title,
                      
                      'work_address':data.work_address or '',
                      'work_address2':data.work_address2 or '',
                      'work_address3':data.work_address3 or '',
                      'work_suburb':data.person_suburb.id ,
                      'work_city':data.work_city.id,
                      'work_province':data.work_province.id ,
                      'work_zip':data.work_zip or '',
                      'work_country':data.work_country.id,
                      
                      'department':data.department or '',
                      'job':data.job_title or '',
                      'manager':data.manager or '',
                      'note':data.notes or '',
                      
                      'contact_home':data.cont_number_home or '',
                      'contact_office':data.cont_number_office or '',
                      'contact_cell':data.person_cell_phone_number or '',
                      
                      'citizen_code':data.citizen_resident_status_code ,
                      'nationality':data.country_id.id ,
                      'identification_id':data.assessor_moderator_identification_id or '',
                      'person_birth_date':data.person_birth_date or '',
                      'passport_id':data.passport_id or '',
                      'id_document':data.id_document.id or None,
                      'national_id':data.national_id or '',
                      'home_language':data.home_language_code.id,
                      
                      'registrationdoc':data.registrationdoc.id or None,
                      'professionalbodydoc':data.professionalbodydoc.id or None,
                      'sram_doc':data.sram_doc.id or None,
                      
                      'gender':data.gender ,
                      'marital':data.marital ,
                      'dissability':data.dissability,
                        
                      'person_home_address':data.person_home_address_1 or '',
                      'person_home_address2':data.person_home_address_2 or '',
                      'person_home_address3':data.person_home_address_3 or '',
                      'person_home_suburb':data.person_home_suburb.id ,
                      'person_home_city':data.person_home_city.id ,
                      'person_home_province':data.person_home_province_code.id ,
                      'person_home_zip':data.person_home_zip or '',
                      'person_home_country':data.country_home.id ,
                      'same_as_home':data.same_as_home,
                      
                      'person_postal_address':data.person_postal_address_1 or '',
                      'person_postal_address2':data.person_postal_address_2 or '',
                      'person_postal_address3':data.person_postal_address_3 or '',
                      'person_postal_suburb':data.person_postal_suburb.id,
                      'person_postal_city':data.person_postal_city.id ,
                      'person_postal_province':data.person_postal_province_code.id,
                      'person_postal_zip':data.person_postal_zip or '',
                      'person_postal_country':data.country_postal.id ,
                      'unknown_type':data.unknown_type,
                      'unknown_type_document':data.unknown_type_document.id or None,
                      'unknown_type_document':data.unknown_type_document.id or None,
                      'cv_document':data.cv_document.id or None,
                      }
                
                main=[]
                main_quali={}
                main_unit = []
                main_unit_quali = {}
                for qualifcation in data.qualification_ids:
                    main_quali_line=[]
                    print "qualifcation===",qualifcation.qual_unit_type
                    if qualifcation.qual_unit_type == 'qual':
                        for asssessor_qualifcation in qualifcation:
                            for lines in asssessor_qualifcation.qualification_line_hr:
                                for quali in provider_obj.browse(cr,SUPERUSER_ID,asssessor_qualifcation.qualification_hr_id.id):
                                    for q_line in quali.qualification_line:
                                        if q_line.id_no==lines.id_no:
                                            main_quali_line.append(q_line.id)
                        main_quali={
                                    asssessor_qualifcation.qualification_hr_id.id:( asssessor_qualifcation.qualification_hr_id.name,main_quali_line),
                                    }
                        main.append(main_quali)
                    if qualifcation.qual_unit_type == 'unit':
                        for asssessor_qualifcation in qualifcation:
                            for lines in asssessor_qualifcation.qualification_line_hr:
                                for quali in provider_obj.browse(cr,SUPERUSER_ID,asssessor_qualifcation.qualification_hr_id.id):
                                    for q_line in quali.qualification_line:
                                        if q_line.id_no==lines.id_no:
                                            main_quali_line.append(q_line.id)
                        main_unit_quali={
                                    asssessor_qualifcation.qualification_hr_id.id:( asssessor_qualifcation.qualification_hr_id.name,main_quali_line),
                                    }
                        main_unit.append(main_unit_quali)
            vals.update({'qualification':main,
                         'unit_qualification':main_unit})
            result.append(vals)
            return json.dumps(result)
            
    @http.route(['/page/assessorModerator/get_qualification'], type='http', auth="public", website=True)
    def get_qualification(self,search='',**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        qual=[]
        if post.get('qualification_ids'):
            main_quali=str(post.get('qualification_ids'))
            qual=main_quali.split(' ')
        ids=[int(ids) for ids in qual if ids not in ['']]
        result=[]
        values={}
        final_list = []
        qualification = registry.get('provider.qualification')
        if ids:
            qualification_objs = qualification.browse(cr,SUPERUSER_ID,ids,context=context)
            for quali in qualification_objs:
                res = []
                for line in  quali.qualification_line:
                    if line.type in ('Elective', 'Core', 'Fundamental'):
                        values={
                               'id':quali.id,
                               'saqa_qual_id':quali.saqa_qual_id,
                               'qualification_name':quali.name, 
                               'qualification_title':quali.name,
                               'line_id':line.id,
                               'name':line.name,
                               'type':line.type,
                               'id_no':line.id_no,
                               'title':line.title,
                               'level1':line.level1,
                               'level2':line.level2,
                               'level3':line.level3,
                               'is_seta_approved':line.is_seta_approved,
                               'is_provider_approved':line.is_provider_approved,
                               }
                        res.append(values)
                    else:
                        values={
                               'id':quali.id,
                               'saqa_qual_id':quali.saqa_qual_id,
                               'qualification_name':quali.name, 
                               'qualification_title':quali.name,
                               'line_id':line.id,
                               'name':line.name,
                               'type':line.type,
                               'id_no':line.id_no,
                               'title':line.title,
                               'level1':line.level1,
                               'level2':line.level2,
                               'level3':line.level3,
                               'is_seta_approved':line.is_seta_approved,
                               'is_provider_approved':line.is_provider_approved,
                               }
                        res.append(values)
                result = sorted(res, key = itemgetter('qualification_title'))
                for item in result:
                    if item['type'] == 'Core':
                        final_list.append(item)
                for item in result:
                    if item['type'] == 'Fundamental':
                        final_list.append(item)
                for item in result:
                    if item['type'] == 'Elective':
                        final_list.append(item)
                for item in result:
                    if item['type'] not in ['Core' , 'Fundamental', 'Elective']:
                        final_list.append(item)
        return json.dumps(final_list)
    
    @http.route(['/page/assessorModerator/get_unit_qualification'], type='http', auth="public", website=True)
    def get_unit_qualification(self,search='',**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        qual=[]
        if post.get('qualification_ids'):
            main_quali=str(post.get('qualification_ids'))
            qual=main_quali.split(' ')
        ids=[int(ids) for ids in qual if ids not in ['']]
        result=[]
        values={}
        final_list = []
        qualification = registry.get('provider.qualification')
        if ids:
            qualification_objs = qualification.browse(cr,SUPERUSER_ID,ids,context=context)
            for quali in qualification_objs:
                res = []
                for line in  quali.qualification_line:
                    if line.type in ('Elective', 'Core', 'Fundamental'):
                        values={
                               'id':quali.id,
                               'saqa_qual_id':quali.saqa_qual_id,
                               'qualification_name':quali.name, 
                               'qualification_title':quali.name,
                               'line_id':line.id,
                               'name':line.name,
                               'type':line.type,
                               'id_no':line.id_no,
                               'title':line.title,
                               'level1':line.level1,
                               'level2':line.level2,
                               'level3':line.level3,
                               'is_seta_approved':line.is_seta_approved,
                               'is_provider_approved':line.is_provider_approved,
                               }
                        res.append(values)
                    else:
                        values={
                               'id':quali.id,
                               'saqa_qual_id':quali.saqa_qual_id,
                               'qualification_name':quali.name, 
                               'qualification_title':quali.name,
                               'line_id':line.id,
                               'name':line.name,
                               'type':line.type,
                               'id_no':line.id_no,
                               'title':line.title,
                               'level1':line.level1,
                               'level2':line.level2,
                               'level3':line.level3,
                               'is_seta_approved':line.is_seta_approved,
                               'is_provider_approved':line.is_provider_approved,
                               }
                        res.append(values)
                result = sorted(res, key = itemgetter('qualification_title'))
                for item in result:
                    if item['type'] == 'Core':
                        final_list.append(item)
                for item in result:
                    if item['type'] == 'Fundamental':
                        final_list.append(item)
                for item in result:
                    if item['type'] == 'Elective':
                        final_list.append(item)
                for item in result:
                    if item['type'] not in ['Core' , 'Fundamental', 'Elective']:
                        final_list.append(item)
        return json.dumps(final_list)

    @http.route(['/page/providerAccreditation/get_campus_qualification'], type='http', auth="public", website=True)
    def get_campus_qualification(self,search='',**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        campus_qual=[]
        if post.get('qualification_ids'):
            main_quali=str(post.get('qualification_ids'))
            campus_qual=main_quali.split(' ')
        ids=[int(ids) for ids in campus_qual if ids not in ['']]       
#         ids=[int(ids) for ids in list(str(post['qualification_ids']))[::2]]
        result=[]
        values={}
        final_list = []
        if post.get('sub_ids'):
            sub_ids=ast.literal_eval(str(post.get('sub_ids')))
            sub_ids_dict=ast.literal_eval(sub_ids[0].values()[0])
            sub_ids_list=[]
            for key,val in sub_ids_dict.iteritems():
                sub_ids_list=sub_ids_list+val
        qualification = registry.get('provider.qualification')
        if ids:
            qualification_objs = qualification.browse(cr,SUPERUSER_ID,ids,context=context)
            for quali in qualification_objs:
                res = []
                for line in quali.qualification_line:
                    if line.id in sub_ids_list:
                        if line.type in ('Elective', 'Core', 'Fundamental'):
                            values={
                               'id':quali.id,
                               'qualification_name':quali.name, 
                               'qualification_title':quali.name,
                               'saqa_qual_id':quali.saqa_qual_id,
                               'line_id':line.id,
                               'name':line.name,
                               'type':line.type,
                               'id_no':line.id_no,
                               'title':line.title,
                               'level1':line.level1,
                               'level2':line.level2,
                               'level3':line.level3,
                               'is_seta_approved':line.is_seta_approved,
                               'is_provider_approved':line.is_provider_approved,
                                   }
                            res.append(values)
                        else:
                            values={
                               'id':quali.id,
                               'qualification_name':quali.name, 
                               'qualification_title':quali.name,
                               'saqa_qual_id':quali.saqa_qual_id,
                               'line_id':line.id,
                               'name':line.name,
                               'type':line.type,
                               'id_no':line.id_no,
                               'title':line.title,
                               'level1':line.level1,
                               'level2':line.level2,
                               'level3':line.level3,
                               'is_seta_approved':line.is_seta_approved,
                               'is_provider_approved':line.is_provider_approved,
                                   }
                            res.append(values)
                result = sorted(res, key = itemgetter('qualification_title'))
                for item in result:
                    if item['type'] == 'Core':
                        final_list.append(item)
                for item in result:
                    if item['type'] == 'Fundamental':
                        final_list.append(item)
                for item in result:
                    if item['type'] == 'Elective':
                        final_list.append(item)
                for item in result:
                    if item['type'] not in ['Core' , 'Fundamental', 'Elective']:
                        final_list.append(item)
        return json.dumps(final_list)  
    
    @http.route(['/page/providerAccreditation/get_skill'], type='http', auth="public", website=True)
    def get_skill(self,search='',**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        skill=[]
        if post.get('skill_ids'):
            main_skill=str(post.get('skill_ids'))
            skill=main_skill.split(' ')
        ids=[int(ids) for ids in skill if ids not in ['']]
        result=[]
        values={}
        final_list = []
        skills = registry.get('skills.programme')
        if ids:
            skill_objs = skills.browse(cr,SUPERUSER_ID,ids,context=context)
            for skill in skill_objs:
                res = []
                for line in skill.unit_standards_line:
                    if line.type in ('Elective', 'Core', 'Fundamental') and line.selection:
                        values={
                               'id':skill.id,   
                               'saqa_qual_id':skill.saqa_qual_id,
                               'code':skill.code,
                               'skill_name':skill.name, 
                               'skill_title':skill.name,
                               'type':line.type,
                               'line_id':line.id,
                               'name':line.name,
                               'id_no':line.id_no,
                               'title':line.title,
                               'level1':line.level1,
                               'level2':line.level2,
                               'level3':line.level3,
                               }
                        res.append(values)
                result = sorted(res, key = itemgetter('skill_title'))
                for item in result:
                    if item['type'] == 'Core':
                        final_list.append(item)
                for item in result:
                    if item['type'] == 'Fundamental':
                        final_list.append(item)
                for item in result:
                    if item['type'] == 'Elective':
                        final_list.append(item)
        return json.dumps(final_list) 

    @http.route(['/page/providerAccreditation/get_campus_skill'], type='http', auth="public", website=True)
    def get_campus_skill(self,search='',**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        skill=[]
        if post.get('skill_ids'):
            main_skill=str(post.get('skill_ids'))
            skill=main_skill.split(' ')
        ids=[int(ids) for ids in skill if ids not in ['']]            
        result=[]
        final_list = []
        values={}
        if post.get('sub_ids'):
            sub_ids=ast.literal_eval(str(post.get('sub_ids')))
            sub_ids_dict=ast.literal_eval(sub_ids[0].values()[0])
            sub_ids_list=[]
            for key,val in sub_ids_dict.iteritems():
                sub_ids_list=sub_ids_list+val
        skills = registry.get('skills.programme')
        if ids:
            skill_objs = skills.browse(cr,SUPERUSER_ID,ids,context=context)
            for skill in skill_objs:
                res = []
                for line in skill.unit_standards_line:
                    if line.id in sub_ids_list:
                        values={
                               'id':skill.id,
                               'skill_name':skill.name, 
                               'skill_title':skill.name,
                               'saqa_qual_id':skill.saqa_qual_id,
                               'code':skill.code,
                                'type':line.type,
                               'line_id':line.id,
                               'name':line.name,
                               'id_no':line.id_no,
                               'title':line.title,
                               'level1':line.level1,
                               'level2':line.level2,
                               'level3':line.level3,
                               }
                        res.append(values)
                result = sorted(res, key = itemgetter('skill_title'))
                for item in result:
                    if item['type'] == 'Core':
                        final_list.append(item)
                for item in result:
                    if item['type'] == 'Fundamental':
                        final_list.append(item)
                for item in result:
                    if item['type'] == 'Elective':
                        final_list.append(item)
        return json.dumps(final_list)

    @http.route(['/page/providerAccreditation/get_learning_skill'], type='http', auth="public", website=True)
    def get_learning_skill(self,search='',**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        learnings_ids=[]
        core_lst, fundamental_lst, elective_lst, other_lst = [], [], [], []
        if post.get('learning_ids'):
            main_skill=str(post.get('learning_ids'))
            learnings_ids=main_skill.split(' ')
        ids=[int(ids) for ids in learnings_ids if ids not in ['']]
        result=[]
        values={}
        learnings = registry.get('etqe.learning.programme')
        if ids:
            learnings_objs = learnings.browse(cr,SUPERUSER_ID,ids,context=context)
            for learnings in learnings_objs:
                for line in learnings.unit_standards_line:
                    if line.type in ('Elective', 'Core', 'Fundamental') and line.selection:
                        values={
                               'id':learnings.id,
                               'saqa_qual_id':learnings.saqa_qual_id,
                               'code':learnings.code,
                               'learning_name':learnings.name, 
                               'lp_title':learnings.name,
                               'type':line.type,
                               'line_id':line.id,
                               'name':line.name,
                               'id_no':line.id_no,
                               'title':line.title,
                               'level1':line.level1,
                               'level2':line.level2,
                               'level3':line.level3,
                               'seta_approved_lp':line.seta_approved_lp,
                               'provider_approved_lp':line.provider_approved_lp
                               }
                        core_lst.append(values)
            result = core_lst + fundamental_lst + elective_lst + other_lst
        return json.dumps(result)

    @http.route(['/page/providerAccreditation/get_campus_learning'], type='http', auth="public", website=True)
    def get_campus_learning(self,search='',**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        lp=[]
        if post.get('learning_ids'):
            main_skill=str(post.get('learning_ids'))
            lp=main_skill.split(' ')
        ids=[int(ids) for ids in lp if ids not in ['']]            
        result=[]
        values={}
        if post.get('sub_ids'):
            sub_ids=ast.literal_eval(str(post.get('sub_ids')))
            sub_ids_dict=ast.literal_eval(sub_ids[0].values()[0])
            sub_ids_list=[]
            for key,val in sub_ids_dict.iteritems():
                sub_ids_list=sub_ids_list+val
        lps = registry.get('etqe.learning.programme')
        if ids:
            lp_objs =lps.browse(cr,SUPERUSER_ID,ids,context=context)
            for lp in lp_objs:
                for line in lp.unit_standards_line:
                    if line.id in sub_ids_list:
                        values={
                               'id':lp.id,
                               'learning_name':lp.name, 
                               'lp_title':lp.name,
                               'saqa_qual_id':lp.saqa_qual_id,
                               'code':lp.code,
                                'type':line.type,
                               'line_id':line.id,
                               'name':line.name,
                               'id_no':line.id_no,
                               'title':line.title,
                               'level1':line.level1,
                               'level2':line.level2,
                               'level3':line.level3,
                               'seta_approved_lp':line.seta_approved_lp,
                               'provider_approved_lp':line.provider_approved_lp
                               }
                        result.append(values)
        return json.dumps(result)

    @http.route(['/page/hwseta_website.assessor_moderator'], type='http', auth="public", website=True)
    def get_assessor_moderator_details(self, **post): 
        value={}
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        assessor_moderator=registry.get('hr.employee')
        moderator_ids = assessor_moderator.search(cr,SUPERUSER_ID,[('is_moderators','=',True)])
        assessor_ids = assessor_moderator.search(cr,SUPERUSER_ID,[('is_assessors','=',True)])
        if assessor_ids:
            assessors=assessor_moderator.browse(cr,SUPERUSER_ID,assessor_ids,context=context)
            value.update({'assessors':assessors})
        if moderator_ids:
            moderators=assessor_moderator.browse(cr,SUPERUSER_ID,moderator_ids,context=context)
            value.update({'moderators':moderators})
        return request.website.render("hwseta_website.assessor_moderator", value)
       
    @http.route(['/web/login/hwseta_reset_password'], type='http', auth="public", website=True)
    def hwseta_reset_password(self, **post): 
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value={}
        result=[]
        if post.get('user_email_id'):
            email=str(post.get('user_email_id'))
            user=registry.get('res.users').search(cr,SUPERUSER_ID,[('login','=',email)])
            if user:
                res=registry.get('res.users').action_reset_password(cr, SUPERUSER_ID, user, context=context)
                value.update({'email':True})
            if len(user)==0:
                value.update({'email':False})
        result.append(value)
        return json.dumps(result)
    
    @http.route(['/web/login/get_dormant'], type='http', auth="public", website=True)
    def get_dormant(self, **post): 
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value={}
        result=[]
        if post.get('user_email_id'):
            email=str(post.get('user_email_id'))
            user_id=registry.get('res.users').search(cr,SUPERUSER_ID,[('login','=',email)])
            res_user_id=registry.get('res.users').browse(cr,SUPERUSER_ID,user_id).partner_id
            if res_user_id:
                res_user=registry.get('res.partner').browse(cr,SUPERUSER_ID,res_user_id.id)
                if res_user.dormant==True:
                    value.update({'email':True,'user':user_id})
                if res_user.dormant==False:
                    value.update({'email':False,'user':user_id})
        result.append(value)
        return json.dumps(result) 
    
    @http.route(['/web/login/deselect_dormant'], type='http', auth="public", website=True)
    def deselect_dormant(self, **post): 
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        if post.get('user_id'):
            user_id=post.get('user_id')
            res_user_id=registry.get('res.users').browse(cr,SUPERUSER_ID,int(str(user_id))).partner_id
            registry.get('res.partner').browse(cr,SUPERUSER_ID,res_user_id.id).write({'dormant':False})
        
    @http.route(['/web/login/in_active'], type='http', auth="public", website=True)
    def in_active(self, **post): 
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        if post.get('user_id'):
            user_id=int(str(post.get('user_id')))
            registry.get('res.users').browse(cr,SUPERUSER_ID,user_id).write({'active':False})
            
    @http.route(['/page/get_locality'], type='http', auth="public", website=True)
    def get_locality(self, **post): 
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value={}
        result=[]
        if post.get('suburb'):
            cr.execute("select city_id,province_id,country_id,postal_code from res_suburb where id=%s"%(int(str(post.get('suburb')))))
            suburb= cr.fetchone()
#             suburb=registry.get('res.suburb').browse(cr,SUPERUSER_ID,int(str(post.get('suburb'))))
            value.update({'city':suburb[0],'province':suburb[1],'country':suburb[2],'postal_code':suburb[3]})
            result.append(value)
        if post.get('province'):
            cr.execute("select country_id from res_country_state where id=%s"%(int(str(post.get('province')))))
            province= cr.fetchone()            
#             province=registry.get('res.country.state').browse(cr,SUPERUSER_ID,int(str(post.get('province'))))
            value.update({'country':province[0] })
            result.append(value)       
        if post.get('city'):
            cr.execute("select province_id,country_id from res_city where id=%s"%(int(str(post.get('city')))))
            city= cr.fetchone() 
#             city=registry.get('res.city').browse(cr,SUPERUSER_ID,int(str(post.get('city'))))
            value.update({'province':city[0],'country':city[1] })
            result.append(value) 
        return json.dumps(result)
    
    @http.route(['/page/check_sdl_number'], type='http', auth="public", website=True)
    def check_sdl_number(self, **post): 
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value={}
        result=[]
        cr.execute("select id,name,employer_trading_name,employer_sdl_no from res_partner where employer=True  and employer_sdl_no='%s'"%(str(post.get('sdl_no'))))
        partner= cr.fetchall()
        if len(partner)==0:
            return json.dumps(result)
        else:
            value={
                   'id':partner[0][0],
                   'name':partner[0][1],
                   'employer_trading_name':partner[0][2],
                   'employer_sdl_no':partner[0][3],
                   } 
            result.append(value)
            cr.commit()            
            return json.dumps(result)    
        
    @http.route(['/page/load_data'], type='http', auth="public", website=True)
    def load_data(self, **post): 
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value={}
        result=[]
        suburb_list=[]
        suburb_dict={}
        cr.execute("select id,name from res_suburb")
        suburb= cr.fetchall()
        for sub in suburb:
            suburb_dict={
                   'id':sub[0],
                   'name':sub[1],
                   } 
            suburb_list.append(suburb_dict)
            value.update({'suburb':suburb_list})
                
        city_list=[]
        city_dict={}
        cr.execute("select id,name from res_city")
        cities= cr.fetchall()
        for city in cities:
            city_dict={
                   'id':city[0],
                   'name':city[1],
                   } 
            city_list.append(city_dict)
            value.update({'city':city_list})       
                
        province_list=[]
        province_dict={}
        cr.execute("select id, name from res_country_state")
        provinces= cr.fetchall()
        for province in provinces:
            province_dict={
                   'id':province[0],
                   'name':province[1],
                   } 
            province_list.append(province_dict)
            value.update({'province':province_list})  
            
        country_list=[]
        country_dict={}
        cr.execute("select id, name from res_country")
        countries= cr.fetchall()
        for country in countries:
            country_dict={
                   'id':country[0],
                   'name':country[1],
                   } 
            country_list.append(country_dict)
            value.update({'country':country_list})                                              
                
        result.append(value)
        return json.dumps(result)      
    
    @http.route(['/page/get_province'], type='http', auth="public", website=True)
    def get_province(self, **post): 
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value={}
        result=[]
        if post.get('country'):
            cr.execute("select id,name from res_country_state where country_id=%s"%(int(str(post.get('country')))))
            provinces= cr.fetchall()
            for province in provinces:
                value={'id':province[0],'name':province[1]}
                result.append(value)
        return json.dumps(result)

    @http.route(['/page/get_city'], type='http', auth="public", website=True)
    def get_city(self, **post): 
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value={}
        result,cities = [],[]
        if post.get('province'):
            #cr.execute("select id,name,urban_rural from res_city where province_id=%s"%(int(str(post.get('province')))))
            cr.execute("select name,urban_rural from res_city where active = True and province_id=%s"%(int(str(post.get('province')))))
            all_cities= cr.fetchall()
            unique_cities = list(set(all_cities))
            sorted_cities = sorted(sorted(unique_cities, key = lambda x : x[0]), reverse = False)
            for rec in sorted_cities:
                cr.execute("select id,name,urban_rural from res_city where active = True and name = '%s' and urban_rural = '%s'"%((rec[0]),(rec[1])))
                city = cr.fetchone()
                if city:
                    cities.append(city)
            for city in cities:
                value={'id':city[0],'name':city[1],'region':city[2]}
                result.append(value)
        return json.dumps(result)    
    
    @http.route(['/page/get_suburb'], type='http', auth="public", website=True)
    def get_suburb(self, **post): 
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value={}
        result,suburbs=[],[]
        if post.get('city'):
            cr.execute("select name,urban_rural from res_suburb where city_id=%s"%(int(str(post.get('city')))))
            all_suburbs= cr.fetchall()
            unique_suburbs = list(set(all_suburbs))
            sorted_suburbs = sorted(sorted(unique_suburbs, key = lambda x : x[0]), reverse = False)
            for rec in sorted_suburbs:
                cr.execute("select id,name,urban_rural from res_suburb where name = '%s' and urban_rural = '%s'"%((rec[0]),(rec[1])))
                suburb = cr.fetchone()
                if suburb:
                    suburbs.append(suburb)
            for suburb in suburbs:
                value={'id':suburb[0],'name':suburb[1],'region':suburb[2]}
                result.append(value)
        return json.dumps(result) 
    
    @http.route(['/page/check_identification_no'], type='http', auth="public", website=True)
    def check_identification_no(self, **post): 
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value={}
        result=[]
        if post.get('identification_no'):
            cr.execute("select id,state,sdf_reference_no from sdf_register where identification_id='%s'"%str(post.get('identification_no')))
            sdf= cr.fetchall()
            if len(sdf)==0:
                cr.execute("select id from hr_employee where is_sdf=true and identification_id='%s'"%str(post.get('identification_no')))
                sdf_master= cr.fetchall()
                if len(sdf_master)==0:
                    value.update({'result':0})
                elif len(sdf_master):
                    value.update({'result':1})
            elif len(sdf)>0:
                value.update({'result':1,'state':sdf[0][1],'ref':sdf[0][2]})
            result.append(value)
        return json.dumps(result)
    
    @http.route(['/page/check_identification_no_assessor'], type='http', auth="public", website=True)
    def check_identification_no_assessor(self, **post): 
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value={}
        result=[]
        if post.get('identification_no'):
            cr.execute("select id from assessors_moderators_register where final_state != 'Rejected' and identification_id='%s'"%str(post.get('identification_no')))
            assessor= cr.fetchall()
            if len(assessor)==0:
                cr.execute("select id from hr_employee where is_assessors=true and assessor_moderator_identification_id='%s'"%str(post.get('identification_no')))
                assessor_master= cr.fetchall()
                if len(assessor_master)==0:
                    value.update({'result':0})
                elif len(assessor_master)>0:
                    value.update({'result':1})
            elif len(assessor)>0:
                value.update({'result':1})
            result.append(value)
        return json.dumps(result)    
    
    @http.route(['/page/check_email_id'], type='http', auth="public", website=True)
    def check_email_id(self, **post): 
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value={}
        result=[]
        if post.get('email'):
            if '@' not in post.get('email'):
                value.update({'result': 2})
                result.append(value)
                return json.dumps(result)
            cr.execute("select id from res_users where login='%s'"%str(post.get('email')).strip())
            user = cr.fetchall()
            cr.execute("select id from sdf_register where work_email='%s'"%str(post.get('email')).strip())
            sdf = cr.fetchall()
            cr.execute("select id from assessors_moderators_register where work_email='%s' and final_state != 'Rejected'" %str(post.get('email')).strip())
            assessor = cr.fetchall()
            cr.execute("select id from provider_accreditation where email='%s' and final_state != 'Rejected'"%str(post.get('email')).strip())
            provider = cr.fetchall()
            if len(user) == 0 and len(sdf) == 0 and len(assessor) == 0 and len(provider) == 0:
                value.update({'result': 0})
            elif len(user) > 0 or len(sdf) > 0 or len(assessor) > 0 or len(provider) > 0:
                value.update({'result': 1})
            result.append(value)
        return json.dumps(result)

    @http.route(['/page/check_sdlnumber'], type='http', auth="public", website=True)
    def check_sdl_numbers(self, **post): 
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value={}
        result=[]
        if post.get('sdl_number'):
            cr.execute("""select id from provider_accreditation where provider_accreditation."txtSDLNo"='%s'"""%str(post.get('sdl_number')))
            provider= cr.fetchall()
            if len(provider)==0:
                value.update({'result':0})
            elif len(provider)>0:
                value.update({'result':1})
            result.append(value)
        return json.dumps(result)      
    
    @http.route(['/page/check_vat_registartion_no'], type='http', auth="public", website=True)
    def check_vat_registartion_no(self, **post): 
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value={}
        result=[]
        if post.get('vat_registration_no'):
            cr.execute("""select id from provider_accreditation where provider_accreditation."txtVATRegNo"='%s'"""%str(post.get('vat_registration_no')))
            provider= cr.fetchall()
            if len(provider)==0:
                value.update({'result':0})
                cr.execute("""select id from provider_accreditation where provider_accreditation."txtVATRegNo"='%s'"""%str(post.get('vat_registration_no')))
                provider_master=cr.fetchall()
                if len(provider_master)==0:
                    value.update({'result':0})
                elif len(provider_master)>0:
                    value.update({'result':1})            
            elif len(provider)>0:
                value.update({'result':1})
            result.append(value)
        return json.dumps(result)   
    
    @http.route('/load_sic_code',type='http', auth="public", website=True)
    def load_sic_code(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result=[]
        value={}
        if post.get('sic_code'):
            cr.execute("select name,code from hwseta_sic_master where id=%s "%(int(str(post.get('sic_code')))))
            sic_code_data=cr.fetchone()
            if sic_code_data:
                value.update({'sic_description':sic_code_data[0],'code':sic_code_data[1]})
            result.append(value)
            return json.dumps(result)   
    
    @http.route('/load_sic_description',type='http', auth="public", website=True)
    def load_sic_description(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result=[]
        value={}
        if post.get('sic_code'):
            cr.execute("select name,code,id from hwseta_sic_master where code= '%s' "%(str(post.get('sic_code'))))
            sic_code_data=cr.fetchone()
            if sic_code_data:
                value.update({'sic_description':sic_code_data[0],'code':sic_code_data[1],'id':sic_code_data[2]})
        result.append(value)
        return json.dumps(result) 
    
    @http.route('/page/get_assessor_moderator_number',type='http', auth="public", website=True)
    def get_assessor_moderator_number(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result=[]
        value={}
        if str(post.get('assessor_moderator'))=='assessor':
            
            value.update({'assessor_moderator':registry['ir.sequence'].get(cr,SUPERUSER_ID,'assessors.register')})
        if str(post.get('assessor_moderator'))=='moderator':
            value.update({'assessor_moderator':registry['ir.sequence'].get(cr,SUPERUSER_ID,'moderators.register')})            
        if str(post.get('assessor_moderator'))=='already_registered' and str(post.get('ex_assessor_ex_moderator'))=='ex_ass':
            value.update({'assessor_moderator':registry['ir.sequence'].get(cr,SUPERUSER_ID,'assessors.register')})
        if str(post.get('assessor_moderator'))=='already_registered' and str(post.get('ex_assessor_ex_moderator'))=='ex_mod':
            value.update({'assessor_moderator':registry['ir.sequence'].get(cr,SUPERUSER_ID,'moderators.register')})            
        result.append(value)
        return json.dumps(result)             
      
    @http.route('/load_more_qualification',type='http', auth="public", website=True)
    def load_more_qualification(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result=[]
        value={}
        cr.execute("select id, name,saqa_qual_id,m_credits from provider_qualification where id<%s and seta_branch_id = 1 order by id desc limit 100"%(int(str(post.get('last_qualification_id')))))
        qualification_data=cr.fetchall() 
        for qualification in qualification_data:
            value={'id':qualification[0],'name':qualification[1],'saqa_qual_id':qualification[2],'m_credits':qualification[3]}
            result.append(value)
        return json.dumps(result)
    
    @http.route('/load_more_unit_qualification',type='http', auth="public", website=True)
    def load_more_unit_qualification(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result=[]
        value={}
        cr.execute("select id, name,saqa_qual_id,m_credits from provider_qualification where id<%s and seta_branch_id = 1 order by id desc limit 100"%(int(str(post.get('last_qualification_id')))))
        qualification_data=cr.fetchall() 
        for qualification in qualification_data:
            value={'id':qualification[0],'name':qualification[1],'saqa_qual_id':qualification[2],'m_credits':qualification[3]}
            result.append(value)
        return json.dumps(result)

    @http.route('/load_more_skill',type='http', auth="public", website=True)
    def load_more_skill(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result=[]
        value={}
        cr.execute("select id, name,code from skills_programme where id<%s and seta_branch_id = 1 order by id desc limit 100"%(int(str(post.get('last_skill_id')))))
        skill_data=cr.fetchall() 
        for skill in skill_data:
            value={'id':skill[0],'name':skill[1],'code':skill[2]}
            result.append(value)
        return json.dumps(result)

    @http.route('/load_more_lp',type='http', auth="public", website=True)
    def load_more_lp(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result=[]
        value={}
        cr.execute("select id, name,code from etqe_learning_programme where id<%s and seta_branch_id = 1 order by id desc limit 100"%(int(str(post.get('last_lp_id')))))
        lp_data=cr.fetchall() 
        for lp in lp_data:
            value={'id':lp[0],'name':lp[1],'code':lp[2]}
            result.append(value)
        return json.dumps(result)

    @http.route('/load_more_assessor',type='http', auth="public", website=True)
    def load_more_assessor(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result=[]
        value={}
        cr.execute("select id, person_name from hr_employee where id<%s and is_assessors=True order by id desc limit 100"%(int(str(post.get('assessor_id')))))
        assessor_data=cr.fetchall() 
        for assessor in assessor_data:
            value={'id':assessor[0],'name':assessor[1]}
            result.append(value)
        return json.dumps(result)    
      
    @http.route('/page/get_organisation_name',type='http', auth="public", website=True)
    def get_organisation_name(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result=[]
        value={}
        cr.execute("select id,name from res_partner where employer_sdl_no='%s' and employer=True"%(str(post.get('organisation_sdl_no'))))
        employer_data=cr.fetchone() 
        if employer_data:
            value={'id':employer_data[0],'name':employer_data[1]}
            result.append(value)
        if not employer_data:
            result=[]
        return json.dumps(result) 
    
    @http.route(['/page/check_assessor_number'], type='http', auth="public", website=True)
    def check_assessor_number(self, **post): 
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value={}
        result=[]
        qual, skill, lp, skill_qual_id, lp_qual_id = [], [], [], [], []
        if post.get('qualification'):
            main_quali = str(post.get('qualification'))
            qual = main_quali.split(' ')
        if post.get('skill'):
            main_skill = str(post.get('skill'))
            skill = main_skill.split(' ')
        if post.get('learning_programme'):
            main_lp = str(post.get('learning_programme'))
            lp = main_lp.split(' ')
        selected_qualification_ids = [int(ids) for ids in qual if ids not in ['']]
        # Added by Ganesh To Get Qualification ID From Skills- SAQA QUAL ID
        selected_skill_ids = [int(ids) for ids in skill if ids not in ['']]
        for skill_id in selected_skill_ids:
            if skill_id:
                cr.execute("select saqa_qual_id from skills_programme where seta_branch_id = 1 and id = '%s'",([skill_id]))
                skill_qual_id = cr.fetchone()
                if skill_qual_id:
                    cr.execute("select id from provider_qualification where seta_branch_id = 1 and saqa_qual_id = %s",([skill_qual_id[0]]))
                    qual_id = cr.fetchone()
                    if qual_id:
                        selected_qualification_ids.append(qual_id[0])
        # Added by Ganesh To Get Qualification ID From Learning Programme- SAQA QUAL ID
        selected_lp_ids = [int(ids) for ids in lp if ids not in ['']]
        for lp_id in selected_lp_ids:
            if lp_id:
                cr.execute("select saqa_qual_id from etqe_learning_programme where seta_branch_id = 1 and id = '%s'",([lp_id]))
                lp_qual_id = cr.fetchone()
                if lp_qual_id:
                    cr.execute("select id from provider_qualification where seta_branch_id = 1 and saqa_qual_id = %s",([lp_qual_id[0]]))
                    qual_id = cr.fetchone()
                    if qual_id:
                        selected_qualification_ids.append(qual_id[0])
        assessor_obj = registry.get('hr.employee')
        assessors_id = assessor_obj.search(cr,SUPERUSER_ID, [('is_active_assessor','=',True),('assessor_seq_no','=',str(post.get('assessor_no')))], context=context)
        cr.execute("select id,assessor_seq_no,person_name from hr_employee where is_assessors=True  and assessor_seq_no='%s'"%(str(post.get('assessor_no'))))
        assessor = cr.fetchall()
        if len(assessor) == 0:
            return json.dumps(result)
        else:
            flag = False
            assessor_qualification = []
            assessors = assessor_obj.browse(cr,SUPERUSER_ID,assessors_id)
            if assessors.qualification_ids : 
                for qualification in assessors.qualification_ids : 
                    assessor_qualification.append(qualification.qualification_hr_id.id)
            for selected_quali in list(set(selected_qualification_ids)):
                if selected_quali in assessor_qualification:
                    flag = True
            if flag:
                value = {
                           'id':assessor[0][0],
                           'assessor_seq_no':assessor[0][1],
                           'display_name':assessor[0][2],
                        } 
                result.append(value)
                cr.commit()
            return json.dumps(result)

    @http.route(['/page/check_moderator_number'], type='http', auth="public", website=True)
    def check_moderator_number(self, **post): 
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        value={}
        result=[]
        qual, skill, lp, skill_qual_id, lp_qual_id = [], [], [], [], []
        if post.get('qualification'):
            main_quali = str(post.get('qualification'))
            qual = main_quali.split(' ')
        if post.get('skill'):
            main_skill = str(post.get('skill'))
            skill = main_skill.split(' ')
        if post.get('learning_programme'):
            main_lp = str(post.get('learning_programme'))
            lp = main_lp.split(' ')
        selected_qualification_ids = [int(ids) for ids in qual if ids not in ['']]
        # Added by Ganesh To Get Qualification ID From Skills- SAQA QUAL ID
        selected_skill_ids = [int(ids) for ids in skill if ids not in ['']]
        for skill_id in selected_skill_ids:
            if skill_id:
                cr.execute("select saqa_qual_id from skills_programme where seta_branch_id = 1 and id = '%s'",([skill_id]))
                skill_qual_id = cr.fetchone()
                if skill_qual_id:
                    cr.execute("select id from provider_qualification where seta_branch_id = 1 and saqa_qual_id = %s",([skill_qual_id[0]]))
                    qual_id = cr.fetchone()
                    if qual_id:
                        selected_qualification_ids.append(qual_id[0])
        # Added by Ganesh To Get Qualification ID From Learning Programme- SAQA QUAL ID
        selected_lp_ids = [int(ids) for ids in lp if ids not in ['']]
        for lp_id in selected_lp_ids:
            if lp_id:
                cr.execute("select saqa_qual_id from etqe_learning_programme where seta_branch_id = 1 and id = '%s'",([lp_id]))
                lp_qual_id = cr.fetchone()
                if lp_qual_id:
                    cr.execute("select id from provider_qualification where seta_branch_id = 1 and saqa_qual_id = %s",([lp_qual_id[0]]))
                    qual_id = cr.fetchone()
                    if qual_id:
                        selected_qualification_ids.append(qual_id[0])
        moderator_obj = registry.get('hr.employee')
        moderator_id = moderator_obj.search(cr,SUPERUSER_ID, [('is_active_moderator','=',True),('moderator_seq_no','=',str(post.get('moderator_no')))], context=context)
        cr.execute("select id,moderator_seq_no,person_name from hr_employee where is_moderators=True and moderator_seq_no='%s'"%(str(post.get('moderator_no'))))
        moderator = cr.fetchall()
        if len(moderator) == 0:
            return json.dumps(result)
        else:
            flag = False
            assessor_qualification = []
            moderators = moderator_obj.browse(cr,SUPERUSER_ID,moderator_id)
            if moderators.qualification_ids : 
                for qualification in moderators.qualification_ids : 
                    assessor_qualification.append(qualification.qualification_hr_id.id)
            for selected_quali in list(set(selected_qualification_ids)):
                if selected_quali in assessor_qualification:
                    flag = True
            if flag:
                value = {
                           'id':moderator[0][0],
                           'moderator_seq_no':moderator[0][1],
                           'display_name':moderator[0][2],
                        } 
                result.append(value)
                cr.commit()            
            return json.dumps(result)                 

    #For Assessor Re - registration 
    @http.route(['/page/assessorModerator/validate_ex_assesor_number'], type='http', auth="public", website=True)
    def validate_ex_assesor_number(self,search='',**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result=[]
        vals={}
        assessor_obj=registry.get('hr.employee')
        provider_obj=registry.get('provider.qualification')
        assessors_id =assessor_obj.search(cr,SUPERUSER_ID, [('assessor_seq_no','=',str(post['txtAssNumber']))], context=context)
        if assessors_id:
            data_assesor=assessor_obj.browse(cr,SUPERUSER_ID,assessors_id,context=context)
            for data in data_assesor:
                vals={
                      'type':data.type or '',
                      'name':data.name,
                      'surname':data.person_last_name,
                      'work_email':data.work_email,
                      'work_phone':data.work_phone,
                      'title':data.person_title,
                      
                      'work_address':data.work_address or '',
                      'work_address2':data.work_address2 or '',
                      'work_address3':data.work_address3 or '',
                      'work_suburb':data.person_suburb.id ,
                      'work_city':data.work_city.id,
                      'work_province':data.work_province.id ,
                      'work_zip':data.work_zip or '',
                      'work_country':data.work_country.id,
                      
                      'department':data.department or '',
                      'job':data.job_title or '',
                      'manager':data.manager or '',
                      'note':data.notes or '',
                      
                      'contact_home':data.cont_number_home or '',
                      'contact_office':data.cont_number_office or '',
                      'contact_cell':data.person_cell_phone_number or '',
                      
                      'citizen_code':data.citizen_resident_status_code ,
                      'nationality':data.country_id.id ,
                      'identification_id':data.identification_id or '',
                      'person_birth_date':data.person_birth_date or '',
                      'passport_id':data.passport_id or '',
                      'id_document':data.id_document.id or None,
                      'national_id':data.national_id or '',
                      'home_language':data.home_language_code.id,
                      
                      'registrationdoc':data.registrationdoc.id or None,
                      'professionalbodydoc':data.professionalbodydoc.id or None,
                      'sram_doc':data.sram_doc.id or None,
                      
                      'gender':data.gender ,
                      'marital':data.marital ,
                      'dissability':data.dissability,
                        
                      'person_home_address':data.person_home_address_1 or '',
                      'person_home_address2':data.person_home_address_2 or '',
                      'person_home_address3':data.person_home_address_3 or '',
                      'person_home_suburb':data.person_home_suburb.id ,
                      'person_home_city':data.person_home_city.id ,
                      'person_home_province':data.person_home_province_code.id ,
                      'person_home_zip':data.person_home_zip or '',
                      'person_home_country':data.country_home.id ,
                      'same_as_home':data.same_as_home,
                      
                      'person_postal_address':data.person_postal_address_1 or '',
                      'person_postal_address2':data.person_postal_address_2 or '',
                      'person_postal_address3':data.person_postal_address_3 or '',
                      'person_postal_suburb':data.person_postal_suburb.id,
                      'person_postal_city':data.person_postal_city.id ,
                      'person_postal_province':data.person_postal_province_code.id,
                      'person_postal_zip':data.person_postal_zip or '',
                      'person_postal_country':data.country_postal.id ,
                      'unknown_type':data.unknown_type,
                      'unknown_type_document':data.unknown_type_document.id or None,
                      'unknown_type_document':data.unknown_type_document.id or None,
                      'cv_document':data.cv_document.id or None,
                      }
                
                main=[]
                main_quali={}
                for qualifcation in data.qualification_ids:
                    main_quali_line=[]
                    for asssessor_qualifcation in qualifcation:
                        for lines in asssessor_qualifcation.qualification_line_hr:
                            for quali in provider_obj.browse(cr,SUPERUSER_ID,asssessor_qualifcation.qualification_hr_id.id):
                                for q_line in quali.qualification_line:
                                    if q_line.id_no==lines.id_no:
                                        main_quali_line.append(q_line.id)
                    main_quali={
                                asssessor_qualifcation.qualification_hr_id.id:( asssessor_qualifcation.qualification_hr_id.name,main_quali_line),
                                }
                    main.append(main_quali)
            vals.update({'qualification':main})
            result.append(vals)
            return json.dumps(result)

    #For Existing Moderator Re - registration 
    @http.route(['/page/assessorModerator/validate_ex_moderator_number'], type='http', auth="public", website=True)
    def validate_ex_moderator_number(self,search='',**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result=[]
        vals={}
        moderator_obj=registry.get('hr.employee')
        provider_obj=registry.get('provider.qualification')
        moderator_id =moderator_obj.search(cr,SUPERUSER_ID, [('moderator_seq_no','=',str(post['txtModNumber']))], context=context)
        if moderator_id:
            data_moderator=moderator_obj.browse(cr,SUPERUSER_ID,moderator_id,context=context)
            for data in data_moderator:
                vals={
                      'type':data.type or '',
                      'name':data.name,
                      'surname':data.person_last_name,
                      'work_email':data.work_email,
                      'work_phone':data.work_phone,
                      'title':data.person_title,
                      
                      'work_address':data.work_address or '',
                      'work_address2':data.work_address2 or '',
                      'work_address3':data.work_address3 or '',
                      'work_suburb':data.person_suburb.id ,
                      'work_city':data.work_city.id,
                      'work_province':data.work_province.id ,
                      'work_zip':data.work_zip or '',
                      'work_country':data.work_country.id,
                      
                      'department':data.department or '',
                      'job':data.job_title or '',
                      'manager':data.manager or '',
                      'note':data.notes or '',
                      
                      'contact_home':data.cont_number_home or '',
                      'contact_office':data.cont_number_office or '',
                      'contact_cell':data.person_cell_phone_number or '',
                      
                      'citizen_code':data.citizen_resident_status_code ,
                      'nationality':data.country_id.id ,
                      'identification_id':data.identification_id or '',
                      'person_birth_date':data.person_birth_date or '',
                      'passport_id':data.passport_id or '',
                      'id_document':data.id_document.id or None,
                      'national_id':data.national_id or '',
                      'home_language':data.home_language_code.id,
                      
                      'registrationdoc':data.registrationdoc.id or None,
                      'professionalbodydoc':data.professionalbodydoc.id or None,
                      'sram_doc':data.sram_doc.id or None,
                      
                      'gender':data.gender ,
                      'marital':data.marital ,
                      'dissability':data.dissability,
                        
                      'person_home_address':data.person_home_address_1 or '',
                      'person_home_address2':data.person_home_address_2 or '',
                      'person_home_address3':data.person_home_address_3 or '',
                      'person_home_suburb':data.person_home_suburb.id ,
                      'person_home_city':data.person_home_city.id ,
                      'person_home_province':data.person_home_province_code.id ,
                      'person_home_zip':data.person_home_zip or '',
                      'person_home_country':data.country_home.id ,
                      'same_as_home':data.same_as_home,
                      
                      'person_postal_address':data.person_postal_address_1 or '',
                      'person_postal_address2':data.person_postal_address_2 or '',
                      'person_postal_address3':data.person_postal_address_3 or '',
                      'person_postal_suburb':data.person_postal_suburb.id,
                      'person_postal_city':data.person_postal_city.id ,
                      'person_postal_province':data.person_postal_province_code.id,
                      'person_postal_zip':data.person_postal_zip or '',
                      'person_postal_country':data.country_postal.id ,
                      'unknown_type':data.unknown_type,
                      'unknown_type_document':data.unknown_type_document.id or None,
                      'unknown_type_document':data.unknown_type_document.id or None,
                      'cv_document':data.cv_document.id or None,
                      }
                
                main=[]
                main_quali={}
                for qualifcation in data.qualification_ids:
                    main_quali_line=[]
                    for asssessor_qualifcation in qualifcation:
                        for lines in asssessor_qualifcation.qualification_line_hr:
                            for quali in provider_obj.browse(cr,SUPERUSER_ID,asssessor_qualifcation.qualification_hr_id.id):
                                for q_line in quali.qualification_line:
                                    if q_line.id_no==lines.id_no:
                                        main_quali_line.append(q_line.id)
                    main_quali={
                                asssessor_qualifcation.qualification_hr_id.id:( asssessor_qualifcation.qualification_hr_id.name,main_quali_line),
                                }
                    main.append(main_quali)
            vals.update({'qualification':main})
            result.append(vals)
            return json.dumps(result)

        
    @http.route(['/get-accreditation-details'], type='http', auth="public", website=True)
    def get_accreditation_details(self,search='',**post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        result =[]
        vals ={}
        accreditation_obj = registry.get('res.partner')
        provider_qualification_obj = registry.get('provider.qualification')
        provider_skill_obj = registry.get('skills.programme')
        provider_id = accreditation_obj.search(cr,SUPERUSER_ID, [('provider_accreditation_num','=',str(post['accreditation_number']))], context=context)
        if provider_id: 
            data_provider = accreditation_obj.browse(cr,SUPERUSER_ID,provider_id,context=context)
            for data in data_provider:     
                vals = {
                        'name':data.name,
                        'trading_name':data.txtTradeName,
                        'street':data.street,
                        'street2':data.street2,
                        'street3':data.street3,
                        'suburb':data.suburb and data.suburb.id or None,
                        'city':data.city and data.city.id  or None,
                        'province':data.state_id and data.state_id.id or None,
                        'zip':data.zip,
                        'country':data.country_id and data.country_id.id or None,
                        'phone':data.phone,
                        'mobile':data.mobile,
                        'fax':data.fax,
                        'email':data.email,
                        'vat_number':data.txtVATRegNo,
                        'material':data.material,
                        'current_business_year':data.txtNumYearsCurrentBusiness,
                        'no_of_staff':data.txtNumStaffMembers,
                        'company_registration_no':data.txtCompanyRegNo,
                        'sic_code':data.cboOrgSICCode and data.cboOrgSICCode.id or None,
                        
                        }    
                main_qualifications = []
                main_quali={}
                if data.qualification_ids:
                    for qualifcation in data.qualification_ids:
                        main_quali_line=[]
                        for provider_qualifcation in qualifcation:
                            for lines in provider_qualifcation.qualification_line:
                                for quali in provider_qualification_obj.browse(cr,SUPERUSER_ID,provider_qualifcation.qualification_id.id):
                                    for q_line in quali.qualification_line:
                                        if q_line.id_no==lines.id_data:
                                            main_quali_line.append(q_line.id)
                        main_quali={
                                    provider_qualifcation.qualification_id.id:( provider_qualifcation.qualification_id.name,main_quali_line),
                                    }  
                        main_qualifications.append(main_quali)
                        
                        
                main_skills = []
                skills={}
                if data.skills_programme_ids:
                    for provider_skills in data.skills_programme_ids:
                        main_skill_line=[]
                        for provider_skill in provider_skills:
                            for lines in provider_skill.unit_standards_line:
                                for p_skill in provider_skill_obj.browse(cr,SUPERUSER_ID,provider_skill.skills_programme_id.id):
                                    for s_line in p_skill.unit_standards_line:
                                        if s_line.id_no==lines.id_no:
                                            main_skill_line.append(s_line.id)
                        skills={
                                    provider_skill.skills_programme_id.id:( provider_skill.skills_programme_id.name,main_skill_line),
                                    }  
                        main_skills.append(skills)
                
                assessor_list = []
                assessor_dict = {}
                if data.assessors_ids:
                    for assessors in data.assessors_ids:
                        assessor_dict = {
                                         'id':assessors.assessors_id.id,
                                         'name':assessors.assessors_id.assessor_seq_no,
                                         }
                        assessor_list.append(assessor_dict)
                        
                moderator_list = []
                moderator_dict = {}
                if data.moderators_ids:
                    for moderators in data.moderators_ids:
                        moderator_dict = {
                                         'id':moderators.moderators_id.id,
                                         'name':moderators.moderators_id.moderator_seq_no,
                                         }
                        moderator_list.append(moderator_dict)
                                
                contact_list = []
                contact_dict = {}       
                if data.provider_master_contact_ids:
                    for contacts in data.provider_master_contact_ids:
                        contact_dict = {
                                         'name':contacts.name,
                                         'email':contacts.email,
                                         'phone':contacts.phone,
                                         'mobile':contacts.mobile,
                                         'fax':contacts.fax,
                                         }
                        contact_list.append(contact_dict)                                             
                        
                    
            vals.update({'master_qualifications':main_qualifications,'master_skills':main_skills,'assessors':assessor_list,'moderators':moderator_list,'contacts':contact_list})       
            result.append(vals)
        return json.dumps(result)
Website()

