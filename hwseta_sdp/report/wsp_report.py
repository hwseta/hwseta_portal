from openerp.report import report_sxw
from openerp.osv import osv

class report_wsp(report_sxw.rml_parse):
   
    def __init__(self, cr, uid, name, context=None):
        super(report_wsp, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_total_employment_profile' : self.get_total_employment_profile,
            'get_planed_training':self.get_planed_training,
            'get_adult_education_and_training':self.get_adult_education_and_training,
            'get_vacancies_hard_to_fill':self.get_vacancies_hard_to_fill,
            'get_wsp_details':self.get_wsp_details,
            'get_total':self.get_total,
       })
    def get_wsp_details(self,wsp):
        result=[]
        value={}
        wsp_plan_data = self.pool.get('wsp.plan').browse(self.cr,self.uid,wsp)
        if wsp_plan_data :
                value={
                       'wsp_no':wsp_plan_data.name,
                       'sdf':wsp_plan_data.sdf_id.name or '',
                       'employer':wsp_plan_data.employer_id.name,
                       'sdl_no':wsp_plan_data.sdl_no,
                       'fiscal_year':wsp_plan_data.fiscal_year.name,
                       'wsp_submission_date':wsp_plan_data.wsp_submission_date or False,
                       }
        result.append(value)
        return value          
   
    def get_total_employment_profile(self,wsp):
        result=[]
        value={}
        wsp_plan_data = self.pool.get('wsp.plan').browse(self.cr,self.uid,wsp)
        if wsp_plan_data.total_employment_profile_ids :
            for total_employment_profile_data in wsp_plan_data.total_employment_profile_ids:
                value={
                       'sdl_number':total_employment_profile_data.sdl_number and total_employment_profile_data.sdl_number.name,
                       'name':total_employment_profile_data.name,
                       'surname':total_employment_profile_data.surname,
                       'citizen_resident_status_code':total_employment_profile_data.citizen_resident_status_code,
                       'employee_id':total_employment_profile_data.employee_id,
                       'id_type':total_employment_profile_data.id_type,
                       'dob':total_employment_profile_data.dob,
                       'ofo_code':total_employment_profile_data.ofo_code and total_employment_profile_data.ofo_code.name,
                       'occupation':total_employment_profile_data.occupation and total_employment_profile_data.occupation.name,
                       'specialization':total_employment_profile_data.ofo_code and total_employment_profile_data.specialization.name,
                       'city_id':total_employment_profile_data.city_id and total_employment_profile_data.city_id.name,
                       'province':total_employment_profile_data.province and total_employment_profile_data.province.name,
                       'urban':total_employment_profile_data.urban,
                       'highest_education_level':total_employment_profile_data.highest_education_level,
                       'population_group':total_employment_profile_data.population_group,
                       'gender':total_employment_profile_data.gender,
                       'dissability':total_employment_profile_data.dissability,
                       
                       }
                result.append(value)
        return result

    def get_total(self,wsp):
        learner_cost=0
        wsp_plan_data = self.pool.get('wsp.plan').browse(self.cr,self.uid,wsp)
        if wsp_plan_data.training_planned_ids :
            for training_planned_data in wsp_plan_data.training_planned_ids:
                learner_cost+=training_planned_data.training_cost
        return learner_cost
        
    def get_planed_training(self,wsp):
        result=[]
        value={}
        wsp_plan_data = self.pool.get('wsp.plan').browse(self.cr,self.uid,wsp)
        if wsp_plan_data.training_planned_ids :
            for training_planned_data in wsp_plan_data.training_planned_ids:
                value={
                       'training_type':training_planned_data.training_type,
                       'name':training_planned_data.name,
                       'surname':training_planned_data.surname,
                       'employee_id':training_planned_data.employee_id,
                       'code':training_planned_data.code and training_planned_data.code.name,
                       'occupation':training_planned_data.occupation and training_planned_data.occupation.name,
                       'specialization':training_planned_data.specialization and training_planned_data.specialization.name or '',
                       'city_id':training_planned_data.city_id and training_planned_data.city_id.name,
                       'urban':training_planned_data.urban,
                       'learner_province':training_planned_data.learner_province and training_planned_data.learner_province.name,
                       'socio_economic_status':training_planned_data.socio_economic_status,
                       'type_training':training_planned_data.type_training and training_planned_data.type_training.name,
                       'other_type_of_intervention':training_planned_data.other_type_of_intervention,
                       'name_training':training_planned_data.name_training,
                       'pivotal_programme_qualification':training_planned_data.pivotal_programme_qualification,
                       'pivotal_programme_institution':training_planned_data.pivotal_programme_institution,
                       'training_cost':training_planned_data.training_cost,
                       'start_date':training_planned_data.start_date,
                       'end_date':training_planned_data.end_date,
                       'nqf_aligned':training_planned_data.nqf_aligned,
                       'nqf_level':training_planned_data.nqf_level,
                       'population_group':training_planned_data.population_group,
                       'gender':training_planned_data.gender,
                       'dissability':training_planned_data.dissability,
                       }
                result.append(value)
        return result    
    
    def get_adult_education_and_training(self,wsp):
        result=[]
        value={}
        wsp_plan_data = self.pool.get('wsp.plan').browse(self.cr,self.uid,wsp)
        if wsp_plan_data.planned_adult_education_ids :
            for planned_adult_education_data in wsp_plan_data.planned_adult_education_ids:
                value={
                       'name':planned_adult_education_data.name,
                       'surname':planned_adult_education_data.surname,
                       'id_number':planned_adult_education_data.id_number,
                       'population_group':planned_adult_education_data.population_group,
                       'gender':planned_adult_education_data.gender,
                       'dissability_status_and_type':planned_adult_education_data.dissability_status_and_type,
                       'city_id':planned_adult_education_data.city_id and planned_adult_education_data.city_id.name,
                       'province':planned_adult_education_data.province and planned_adult_education_data.province.name,
                       'urban':planned_adult_education_data.urban,
                       'start_date':planned_adult_education_data.start_date,
                       'end_date':planned_adult_education_data.end_date,
                       'provider':planned_adult_education_data.provider,
                       'aet_level':planned_adult_education_data.aet_level,
#                        'aet_subject':planned_adult_education_data.aet_subject,
                       'aet_subject':planned_adult_education_data.get_aet_subject(),
                       }
                result.append(value)
        return result      
    
    def get_vacancies_hard_to_fill(self,wsp):
        result=[]
        value={}
        wsp_plan_data = self.pool.get('wsp.plan').browse(self.cr,self.uid,wsp)
        if wsp_plan_data.scarce_and_critical_skills_ids :
            for scarce_and_critical_skills_data in wsp_plan_data.scarce_and_critical_skills_ids:
                value={
                       'ofo_code':scarce_and_critical_skills_data.ofo_code and scarce_and_critical_skills_data.ofo_code.name,
                       'occupation':scarce_and_critical_skills_data.occupation and scarce_and_critical_skills_data.occupation.name,
                       'specialization':scarce_and_critical_skills_data.specialization and scarce_and_critical_skills_data.specialization.name,
                       'province':scarce_and_critical_skills_data.province and scarce_and_critical_skills_data.province.name,
                       'number_of_vacancies':scarce_and_critical_skills_data.number_of_vacancies,
                       'gender':scarce_and_critical_skills_data.gender,
                       'population_group':scarce_and_critical_skills_data.population_group,
                       'no_of_months':scarce_and_critical_skills_data.no_of_months,
                       'comments':scarce_and_critical_skills_data.comments,
                       }
                result.append(value)
        return result    
           
class report_daily_sales(osv.AbstractModel):
    _name = "report.hwseta_sdp.wsp_report"
    _inherit = "report.abstract_report"
    _template = "hwseta_sdp.wsp_report"
    _wrapped_report_class = report_wsp