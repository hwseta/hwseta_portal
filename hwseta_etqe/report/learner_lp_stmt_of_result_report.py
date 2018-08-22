from openerp.osv import fields, osv
from openerp.report import report_sxw


class learner_lp_statement_of_result(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(learner_lp_statement_of_result, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'get_lp': self.get_lp,
            'get_unit_standard': self.get_unit_standard,
            'get_status': self.get_status,
            'get_saqa_qual_id': self.get_saqa_qual_id,
            'get_certificate_no': self.get_certificate_no,
            'get_lp_nqf_level': self.get_lp_nqf_level,
            'get_lp_credits_value': self.get_lp_credits_value,
            'get_lp_saqa_qual_id':self.get_lp_saqa_qual_id,
        })

    def get_lp(self, achieved_id):
        """
        This function is used to retrieve Learning Programme data
        """
        self.cr.execute(
            "select lp_learner_assessment_achieved_line_id from lp_assessment_achieved_rel where lp_achieved_id=%s" % (achieved_id.id))
        lp_ids = map(lambda x: x[0], self.cr.fetchall())
        lp = [str(lp.name) for lp in self.pool.get(
            'etqe.learning.programme').browse(self.cr, self.uid, lp_ids)]
        return ','.join(lp)

    def get_saqa_qual_id(self, achieved_id):
        """
        This function is used to retrieve SAQA QUAL ID
        """
        self.cr.execute(
            "select lp_learner_assessment_achieved_line_id from lp_assessment_achieved_rel where lp_achieved_id=%s" % (achieved_id.id))
        lp_ids = map(lambda x: x[0], self.cr.fetchall())
        lp = [str(lp.code) for lp in self.pool.get(
            'etqe.learning.programme').browse(self.cr, self.uid, lp_ids)]
        return ','.join(lp)

    def get_lp_saqa_qual_id(self, achieved_id):
        """
        This function is used to retrieve Qualification data
        """
        self.cr.execute(
            "select lp_learner_assessment_achieved_line_id from lp_assessment_achieved_rel where lp_achieved_id=%s" % (achieved_id.id))
        lp_ids = map(lambda x: x[0], self.cr.fetchall())
        lp_saqa_qual_id = [str(lp.saqa_qual_id) for lp in self.pool.get(
            'etqe.learning.programme').browse(self.cr, self.uid, lp_ids)]
        lp_id = [str(lp.code) for lp in self.pool.get(
            'etqe.learning.programme').browse(self.cr, self.uid, lp_ids)]
        qual_details = []
        if lp_saqa_qual_id:
            self.cr.execute("select saqa_qual_id,name, n_level, m_credits from provider_qualification where saqa_qual_id = %s", ([str(lp_saqa_qual_id[0])]))
            qual_id = self.cr.fetchone()
            qual_list = []
            if qual_id:
                qual_list.append({
                                  'saqa_qual_id': qual_id[0],
                                  'name': qual_id[1],
                                  'lp_id': lp_id[0],
                                  'n_level': qual_id[2],
                                  'm_credits': qual_id[3],
                                  })
                qual_details.append({'value': qual_list[::-1]})
        return qual_details

    def get_lp_nqf_level(self, achieved_id):
        """
        This function is used to retrieve Learning Programme nqf level
        """
        self.cr.execute(
            "select lp_learner_assessment_achieved_line_id from lp_assessment_achieved_rel where lp_achieved_id=%s" % (achieved_id.id))
        lp_ids = map(lambda x: x[0], self.cr.fetchall())
        lp = [str(lp.n_level) for lp in self.pool.get(
            'etqe.learning.programme').browse(self.cr, self.uid, lp_ids)]
        return ','.join(lp)
    
    def get_lp_credits_value(self, achieved_id):
        """
        This function is used to retrieve Learning Programme credit Value
        """
        self.cr.execute(
            "select lp_learner_assessment_achieved_line_id from lp_assessment_achieved_rel where lp_achieved_id=%s" % (achieved_id.id))
        lp_ids = map(lambda x: x[0], self.cr.fetchall())
        lp = [str(lp.total_credit) for lp in self.pool.get(
            'etqe.learning.programme').browse(self.cr, self.uid, lp_ids)]
        return ','.join(lp)

    def get_unit_standard(self, achieved_id):
        """
        This function is used to retrieve Unit standard data
        """
        unit_standard, unit_standard_type = [], []
        self.cr.execute(
            "select lp_unit_standards_learner_assessment_achieved_line_id from lp_unit_assessment_achieved_rel where lp_unit_standards_achieved_id=%s" % (achieved_id.id))
        lp_line_ids = map(lambda x: x[0], self.cr.fetchall())
        for lp_line in self.pool.get('etqe.learning.programme.unit.standards').browse(self.cr, self.uid, lp_line_ids):
            unit_standard_type.append(lp_line.type)
        total_line = []
        newlist = []
        for u_type in list(set(unit_standard_type)):
            val_lst = []
            total_credits = 0
            nfq_level = 0
            total_nfq_level = 0
            for lp_line in self.pool.get('etqe.learning.programme.unit.standards').browse(self.cr, self.uid, lp_line_ids):
                total_line.append((lp_line))
                if u_type == lp_line.type:
                    key =  lp_line.type_key
                    val_lst.append({
                        'name': lp_line.title,
                        'credit': lp_line.level3,
                        'nqf_level': lp_line.level2,
                        'saqa_us_id': lp_line.id_no,
                    })
                    try:
                        nfq_level += int(lp_line.level2)
                        total_credits += int(lp_line.level3)
                    except:
                        pass
            for line_level in list(set(total_line)):
                try:
                    total_nfq_level += int(line_level.level2)
                except:
                        pass
            if total_nfq_level == 0:
                total_nfq_level += 1
            unit_standard.append({'type_key': key, 'type': u_type, 'value': val_lst[
                                 ::-1], 't_credits': total_credits, 'percentage': nfq_level * 100 / total_nfq_level, 'counter': len(list(set(unit_standard_type)))})
            newlist = sorted(unit_standard, key=lambda k: k['type_key'])
        return newlist

    def get_status(self, achieved_id):
        """
        This function is used to retrieve Unit standards achieve status
        """
        d = {'achieve': False}
        for a_line in achieved_id:
            for s_line in a_line.learner_id.learning_programme_ids:
                if s_line.learning_programme_id.id == a_line.lp_learner_assessment_achieved_line_id.id:
                    d.update({'achieve': s_line.is_learner_achieved})
        return d

    def get_certificate_no(self, achieved_id):
        """
        This function is used to retrieve certificate no. of the achieved Learning Programme
        """
        d = {'certificate_no': False}
        for a_line in achieved_id:
            for s_line in a_line.learner_id.learning_programme_ids:
                if s_line.learning_programme_id.id == a_line.lp_learner_assessment_achieved_line_id.id:
                    d.update({'certificate_no': s_line.certificate_no})
        return d


class lp_statement_of_result_report_view(osv.AbstractModel):
    _name = 'report.hwseta_etqe.report_learning_programme_statement_of_result'
    _inherit = 'report.abstract_report'
    _template = 'hwseta_etqe.report_learning_programme_statement_of_result'
    _wrapped_report_class = learner_lp_statement_of_result
