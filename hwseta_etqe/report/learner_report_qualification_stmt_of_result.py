from openerp.osv import fields, osv
from openerp.report import report_sxw
DEBUG = True

if DEBUG:
	import logging

	logger = logging.getLogger(__name__)


	def dbg(msg):
		logger.info(msg)
else:
	def dbg(msg):
		pass


class learner_qualification_stmt_of_result(report_sxw.rml_parse):

	def __init__(self, cr, uid, name, context=None):
		super(learner_qualification_stmt_of_result, self).__init__(
			cr, uid, name, context=context)
		self.localcontext.update({
			'get_qualification': self.get_qualification,
			'get_unit_standard': self.get_unit_standard,
			'get_status': self.get_status,
			'get_saqa_qual_id': self.get_saqa_qual_id,
			'get_certificate_no': self.get_certificate_no,
			'get_qual_nqf_level': self.get_qual_nqf_level,
			'get_qual_credits_value': self.get_qual_credits_value,
		})

	def get_qualification(self, achieved_id):
		"""
		This function is used to retrieve qualification data
		"""
		self.cr.execute(
			"select qual_achieve_learner_assessment_line_id from achieved_asse_qual_rel where qualification_achieved_id=%s" % (achieved_id.id))
		qualification_ids = map(lambda x: x[0], self.cr.fetchall())
		qualification = [str(qualification.name) for qualification in self.pool.get(
			'provider.qualification').browse(self.cr, self.uid, qualification_ids)]
		return ','.join(qualification)

	def get_saqa_qual_id(self, achieved_id):
		"""
		This function is used to retrieve qualification data
		"""
		self.cr.execute(
			"select qual_achieve_learner_assessment_line_id from achieved_asse_qual_rel where qualification_achieved_id=%s" % (achieved_id.id))
		qualification_ids = map(lambda x: x[0], self.cr.fetchall())
		qualification = [str(qualification.saqa_qual_id) for qualification in self.pool.get(
			'provider.qualification').browse(self.cr, self.uid, qualification_ids)]
		return ','.join(qualification)

	def get_qual_nqf_level(self, achieved_id):
		"""
		This function is used to retrieve qualification's nqf level
		"""
		self.cr.execute(
			"select qual_achieve_learner_assessment_line_id from achieved_asse_qual_rel where qualification_achieved_id=%s" % (achieved_id.id))
		qualification_ids = map(lambda x: x[0], self.cr.fetchall())
		qualification = [str(qualification.n_level) for qualification in self.pool.get(
			'provider.qualification').browse(self.cr, self.uid, qualification_ids)]
		qualification
		return ','.join(qualification)

	def get_qual_credits_value(self, achieved_id):
		"""
		This function is used to retrieve qualification's nqf level
		"""
		self.cr.execute(
			"select qual_achieve_learner_assessment_line_id from achieved_asse_qual_rel where qualification_achieved_id=%s" % (achieved_id.id))
		qualification_ids = map(lambda x: x[0], self.cr.fetchall())
		qualification = [str(qualification.m_credits) for qualification in self.pool.get(
			'provider.qualification').browse(self.cr, self.uid, qualification_ids)]
		return ','.join(qualification)

	def get_unit_standard(self, achieved_id):
		"""
		This function is used to retrieve Unit standard data
		"""
		dbg("get_unit_standard:" + str(achieved_id))
		unit_standard, unit_standard_type = [], []
		self.cr.execute(
			"select unit_standards_learner_assessment_achieve_line_id from achieved_asse_unit_rel where unit_standards_achieved_id=%s" % (achieved_id.id))
		qualification_line_ids = map(lambda x: x[0], self.cr.fetchall())
		dbg("all qualification_line_ids" + str(qualification_line_ids))
		for qualification_line in self.pool.get('provider.qualification.line').browse(self.cr, self.uid, qualification_line_ids):
			unit_standard_type.append(qualification_line.type)
		dbg("unit_standard_type list:" + str(unit_standard_type))
		total_line = []
		newlist = []
		for u_type in list(set(unit_standard_type)):
			val_lst = []
			total_credits = 0
			nfq_level = 0
			total_nfq_level = 0
			for qualification_line in self.pool.get('provider.qualification.line').browse(self.cr, self.uid, qualification_line_ids):
				total_line.append((qualification_line))
				if u_type == qualification_line.type:
					key =  qualification_line.type_key
					val_lst.append({
						'name': qualification_line.title,
						'credit': qualification_line.level3,
						'nqf_level': qualification_line.level2,
						'nlrd_number': int(qualification_line.id_no),
					})
					try:
						nfq_level += int(qualification_line.level2)
						total_credits += int(qualification_line.level3)
					except:
						pass
			for line_level in list(set(total_line)):
				try:
					total_nfq_level += int(line_level.level2)
				except:
						pass
			if total_nfq_level == 0:
				total_nfq_level += 1
			unit_standard_list = sorted(val_lst, key = lambda k: k ['nlrd_number'], reverse=True)
			dbg("unit_standard_list nlrd_number:" + str(unit_standard_list[0].get('nlrd_number')))
			unit_standard.append({'type_key': key, 'type': u_type, 'value': unit_standard_list[
								 ::-1], 't_credits': total_credits, 'percentage': nfq_level * 100 / total_nfq_level, 'counter': len(list(set(unit_standard_type)))})
			newlist = sorted(unit_standard, key=lambda k: k['type_key'])
		return newlist

	def get_status(self, achieved_id):
		"""
		This function is used to retrieve Unit standards achieve status
		"""
		d = {'achieve': False}
		for a_line in achieved_id:
			for q_line in a_line.learner_id.learner_qualification_ids:
				if q_line.learner_qualification_parent_id.id == a_line.qual_learner_assessment_achieved_line_id.id:
					d.update({'achieve': q_line.is_learner_achieved})
		return d

	def get_certificate_no(self, achieved_id):
		"""
		This function is used to retrieve certificate no. of the achieved qualification
		"""
		d = {'certificate_no': False}
		for a_line in achieved_id:
			for q_line in a_line.learner_id.learner_qualification_ids:
				if q_line.learner_qualification_parent_id.id == a_line.qual_learner_assessment_achieved_line_id.id:
					d.update({'certificate_no': q_line.certificate_no})
		return d


class learner_qualification_sor_report_view(osv.AbstractModel):
	_name = 'report.hwseta_etqe.qualification_stmt_of_result_report'
	_inherit = 'report.abstract_report'
	_template = 'hwseta_etqe.qualification_stmt_of_result_report'
	_wrapped_report_class = learner_qualification_stmt_of_result
