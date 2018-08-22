from openerp.report import report_sxw
from openerp.osv import osv

class report_atr(report_sxw.rml_parse):
   
    def __init__(self, cr, uid, name, context=None):
        super(report_atr, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_data' : self.get_data,
            'get_adult_education_and_training':self.get_adult_education_and_training,
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
                       'wsp_submission_date':wsp_plan_data.wsp_submission_date or False
                       }
        result.append(value)
        return value   
    def get_total(self,wsp):
        wsp_plan_data = self.pool.get('wsp.plan').browse(self.cr,self.uid,wsp)
        atr_cost=0
        total_cost=0
        if wsp_plan_data.training_actual_ids :
            for actual_training_data in wsp_plan_data.training_actual_ids:
                atr_cost+=actual_training_data.training_cost
                total_cost+=actual_training_data.total_cost
            values={
                    'atr_cost':atr_cost,
                    'total_cost':total_cost
                    } 
        return values   
    def get_data(self,wsp):
        result=[]
        value={}
        wsp_plan_data = self.pool.get('wsp.plan').browse(self.cr,self.uid,wsp)
        if wsp_plan_data.training_actual_ids :
            for actual_training_data in wsp_plan_data.training_actual_ids:
                value={
                       'wsp_no':wsp_plan_data.name,
                       'sdf':wsp_plan_data.sdf_id.name or '',
                       'employer':wsp_plan_data.employer_id.name,
                       'sdl_no':wsp_plan_data.sdl_no,
                       'fiscal_year':wsp_plan_data.fiscal_year,
                       'wsp_submission_date':wsp_plan_data.wsp_submission_date,
                       'first_name':actual_training_data.name,
                       'last_name':actual_training_data.surname,
                       'employee_id':actual_training_data.employee_id,
                       'training_type': actual_training_data.training_type or '',
                       'occupation':actual_training_data.occupation and actual_training_data.occupation.name,
                       'specialization':actual_training_data.specialization and actual_training_data.specialization.name,
                       'municipality_id':actual_training_data.municipality_id and actual_training_data.municipality_id.name,
                       'city_id':actual_training_data.city_id and actual_training_data.city_id.name,
                       'urban':actual_training_data.urban,
                       'learner_province':actual_training_data.learner_province and actual_training_data.learner_province.name,
                       'socio_economic_status':actual_training_data.socio_economic_status,
                       'type_training':actual_training_data.type_training and actual_training_data.type_training.name,
                       'other_type_intervention':actual_training_data.other_type_of_intervention,
                       'name_training':actual_training_data.name_training,
                       'pivotal_programme_qualification':actual_training_data.pivotal_programme_qualification,
                       'pivotal_programme_institution':actual_training_data.pivotal_programme_institution,
                       'nqf_aligned':actual_training_data.nqf_aligned,
                       'nqf_level':actual_training_data.nqf_level,
                       'training_cost':actual_training_data.training_cost,
                       'start_date':actual_training_data.start_date,
                       'end_date':actual_training_data.end_date,
                       'race':actual_training_data.population_group,
                       'disability':actual_training_data.dissability,
                       'gender':actual_training_data.gender,
                       'african_male':actual_training_data.african_male,
                       'african_female':actual_training_data.african_female,
                       'african_dissabled':actual_training_data.african_dissabled,
                       'coloured_male':actual_training_data.coloured_male,
                       'coloured_female':actual_training_data.coloured_female,
                       'coloured_dissabled':actual_training_data.coloured_dissabled,
                       'indian_male':actual_training_data.indian_male,
                       'indian_female':actual_training_data.indian_female,
                       'indian_dissabled':actual_training_data.indian_dissabled,
                       'white_male':actual_training_data.white_male,
                       'white_female':actual_training_data.white_female,
                       'white_dissabled':actual_training_data.white_dissabled,
                       'total_male':actual_training_data.total_male,
                       'total_female':actual_training_data.total_female,
                       'total_dissabled':actual_training_data.total_dissabled,
                       'age_group_less':actual_training_data.age_group_less,
                       'age_group_upto':actual_training_data.age_group_upto,
                       'age_group_greater':actual_training_data.age_group_greater,
                       'total_cost':actual_training_data.total_cost,
                       }
                result.append(value)
        return result
    
    def get_adult_education_and_training(self,wsp):
        result=[]
        value={}
        wsp_plan_data = self.pool.get('wsp.plan').browse(self.cr,self.uid,wsp)
        if wsp_plan_data.actual_adult_education_ids :
            for actual_adult_data in wsp_plan_data.actual_adult_education_ids:
                value={
                       'name':actual_adult_data.name,
                       'surname':actual_adult_data.surname,
                       'id_number':actual_adult_data.id_number,
                       'population_group':actual_adult_data.population_group,
                       'gender':actual_adult_data.gender,
                       'dissability_status_and_type':actual_adult_data.dissability_status_and_type,
                       'municipality_id':actual_adult_data.municipality_id and actual_adult_data.municipality_id.name,
                       'city_id':actual_adult_data.city_id and actual_adult_data.city_id.name,
                       'province':actual_adult_data.province and actual_adult_data.province.name,
                       'urban':actual_adult_data.urban,
                       'start_date':actual_adult_data.start_date,
                       'end_date':actual_adult_data.end_date,
                       'provider':actual_adult_data.provider,
                       'aet_level':actual_adult_data.aet_level,
#                        'aet_subject':actual_adult_data.aet_subject,
                       'aet_subject':actual_adult_data.get_aet_subject(),
                       }
                result.append(value)
        return result   
           
class report_daily_sales(osv.AbstractModel):
    _name = "report.hwseta_sdp.atr_report"
    _inherit = "report.abstract_report"
    _template = "hwseta_sdp.atr_report"
    _wrapped_report_class = report_atr