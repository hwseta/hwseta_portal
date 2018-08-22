from openerp.osv import fields, osv
from openerp.report import report_sxw


class learner_skills_statement_of_results(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        print "\n\n\n\n\n #############report calling#######################", name
        super(learner_skills_statement_of_results, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'get_skill': self.get_skill,
            'get_unit_standard': self.get_unit_standard,
            'get_status': self.get_status,
            'get_saqa_qual_id': self.get_saqa_qual_id,
            'get_certificate_no': self.get_certificate_no,
            'get_qual_nqf_level': self.get_qual_nqf_level,
            'get_qual_credits_value': self.get_qual_credits_value,
            'get_skills_saqa_qual_id': self.get_skills_saqa_qual_id,
        })

    def get_skill(self, achieved_id):
        print "\n\n\n SKILLS#################inside get_qualification############", achieved_id
        """
        This function is used to retrieve skill data
        """
        self.cr.execute(
            "select skill_learner_assessment_achieved_line_id from skills_assessment_achieved_rel where skills_achieved_id=%s" % (achieved_id.id))
        skill_ids = map(lambda x: x[0], self.cr.fetchall())
        skill = [str(skill.name) for skill in self.pool.get(
            'skills.programme').browse(self.cr, self.uid, skill_ids)]
        return ','.join(skill)

    def get_saqa_qual_id(self, achieved_id):
        print "\n\n\n get_saqa_qual_id() called########"
        """
        This function is used to retrieve skill data
        """
        self.cr.execute(
            "select skill_learner_assessment_achieved_line_id from skills_assessment_achieved_rel where skills_achieved_id=%s" % (achieved_id.id))
        skill_ids = map(lambda x: x[0], self.cr.fetchall())
        skill = [str(skill.code) for skill in self.pool.get(
            'skills.programme').browse(self.cr, self.uid, skill_ids)]
        return ','.join(skill)

    def get_skills_saqa_qual_id(self, achieved_id):
        print "\n\n\n Get Qualification Details() called########"
        """
        This function is used to retrieve Qualification data
        """
        self.cr.execute(
            "select skill_learner_assessment_achieved_line_id from skills_assessment_achieved_rel where skills_achieved_id=%s" % (achieved_id.id))
        skill_ids = map(lambda x: x[0], self.cr.fetchall())
        skill_saqa_qual_id = [str(skill.saqa_qual_id) for skill in self.pool.get(
            'skills.programme').browse(self.cr, self.uid, skill_ids)]
        print "skill_saqa_qual_id----", skill_saqa_qual_id
        qual_details = []
        if skill_saqa_qual_id:
            qual_list = []
            self.cr.execute("select saqa_qual_id, name, n_level, m_credits from provider_qualification where seta_branch_id = 1 and saqa_qual_id = %s", ([str(skill_saqa_qual_id[0])]))
            qual_id = self.cr.fetchone()
            print "qual_id======", qual_id
            if qual_id:
                qual_list.append({
                                  'saqa_qual_id': qual_id[0],
                                  'lp_id': False,
                                  'name': qual_id[1],
                                  'n_level': qual_id[2],
                                  'm_credits': qual_id[3],
                                  })
                print "qual_list---", qual_list[::-1]
                qual_details.append({'value': qual_list[::-1]})
                return qual_details
            if not qual_id:
                self.cr.execute("select saqa_qual_id, code from etqe_learning_programme where seta_branch_id = 1 and code = %s", ([str(skill_saqa_qual_id[0])]))
                lp_id = self.cr.fetchone()
                print "lp_id===",lp_id
                if lp_id:
                    self.cr.execute("select saqa_qual_id, name, n_level, m_credits from provider_qualification where seta_branch_id = 1 and saqa_qual_id = %s", ([str(lp_id[0])]))
                    qual_id = self.cr.fetchone()
                    print "qual id===", qual_id
                    if qual_id:
                        qual_list.append({
                                          'saqa_qual_id': qual_id[0],
                                          'lp_id': lp_id[1],
                                          'name': qual_id[1],
                                          'n_level': qual_id[2],
                                          'm_credits': qual_id[3],
                                          })
                        print "qual_list---", qual_list[::-1]
                        qual_details.append({'value': qual_list[::-1]})
                        return qual_details
        return qual_details

    def get_qual_nqf_level(self, achieved_id):
        print "\n\n\n get_qual_nqf_level() called########"
        """
        This function is used to retrieve skill's nqf level
        """
        self.cr.execute(
            "select skill_learner_assessment_achieved_line_id from skills_assessment_achieved_rel where skills_achieved_id=%s" % (achieved_id.id))
        skill_ids = map(lambda x: x[0], self.cr.fetchall())
        skill = [str(skill.seta_branch_id.name) for skill in self.pool.get(
            'skills.programme').browse(self.cr, self.uid, skill_ids)]
        return ','.join(skill)

    def get_qual_credits_value(self, achieved_id):
        print "\n\n\n get_qual_credits_value() called########"
        """
        This function is used to retrieve skill's nqf level
        """
        self.cr.execute(
            "select skill_learner_assessment_achieved_line_id from skills_assessment_achieved_rel where skills_achieved_id=%s" % (achieved_id.id))
        skill_ids = map(lambda x: x[0], self.cr.fetchall())
        skill = [str(skill.total_credit) for skill in self.pool.get(
            'skills.programme').browse(self.cr, self.uid, skill_ids)]
        return ','.join(skill)

    def get_unit_standard(self, achieved_id):
        print "\n\n\n get_unit_standard() called########"
        """
        This function is used to retrieve Unit standard data
        """
        unit_standard, unit_standard_type = [], []
        self.cr.execute(
            "select skill_unit_standards_learner_assessment_achieved_line_id from skills_unit_assessment_achieved_rel where skills_unit_standards_achieved_id=%s" % (achieved_id.id))
        skills_line_ids = map(lambda x: x[0], self.cr.fetchall())
        for skill_line in self.pool.get('skills.programme.unit.standards').browse(self.cr, self.uid, skills_line_ids):
            unit_standard_type.append(skill_line.type)
        total_line = []
        newlist = []
        for u_type in list(set(unit_standard_type)):
            val_lst = []
            total_credits = 0
#             nfq_level = 0
#             total_nfq_level = 0
            for skill_line in self.pool.get('skills.programme.unit.standards').browse(self.cr, self.uid, skills_line_ids):
                total_line.append((skill_line))
                if u_type == skill_line.type:
                    val_lst.append({
                        'name': skill_line.title,
                        'credit': skill_line.level3,
                        'nqf_level': skill_line.level2,
                        'saqa_us_id': skill_line.id_no,
                    })
#                     nfq_level += int(skill_line.level2)
                    total_credits += int(skill_line.level3)
#             for line_level in list(set(total_line)):
#                 total_nfq_level += int(line_level.level2)
#             if total_nfq_level == 0:
#                 total_nfq_level += 1
#             unit_standard.append({'value': val_lst[
#                                  ::-1], 't_credits': total_credits, 'percentage': nfq_level * 100 / total_nfq_level, 'counter': len(list(set(unit_standard_type)))})
            unit_standard.append({'value': val_lst[
                                 ::-1], 't_credits': total_credits, 'counter': len(list(set(unit_standard_type)))})
            newlist = sorted(unit_standard)
        return newlist

    def get_status(self, achieved_id):
        print "\n\n\n get_status() called########"
        """
        This function is used to retrieve Unit standards achieve status
        """
        d = {'achieve': False}
        for a_line in achieved_id:
            for s_line in a_line.learner_id.skills_programme_ids:
                if s_line.skills_programme_id.id == a_line.skill_learner_assessment_achieved_line_id.id:
                    #d.update({'achieve': s_line.is_learner_achieved })
                    # static updated because Skills Program required only
                    # statement of results
                    d.update({'achieve': False})
        return d

    def get_certificate_no(self, achieved_id):
        print "\n\n\n get_certificate_no() called########"
        """
        This function is used to retrieve certificate no. of the achieved qualification
        """
        d = {'certificate_no': False}
        for a_line in achieved_id:
            for s_line in a_line.learner_id.skills_programme_ids:
                if s_line.skills_programme_id.id == a_line.skill_learner_assessment_achieved_line_id.id:
                    d.update({'certificate_no': s_line.certificate_no})
        return d


class skill_report_view(osv.AbstractModel):
    _name = 'report.hwseta_etqe.report_skills_programme_statement_of_results'
    _inherit = 'report.abstract_report'
    _template = 'hwseta_etqe.report_skills_programme_statement_of_results'
    _wrapped_report_class = learner_skills_statement_of_results
