import base64
import calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, tools, api, _
from openerp.exceptions import Warning
from openerp.osv import fields as fields2, osv
import random
from lxml import etree
DEBUG = True

if DEBUG:
	import logging

	logger = logging.getLogger(__name__)


	def dbg(msg):
		logger.info(msg)
else:
	def dbg(msg):
		pass

class learner_inactive_status(models.Model):
	_name = 'learner.inactive.status'
	_description = 'Learner Inactive Status'

	inactive_status = fields.Selection([('de-enrolled', 'De-Enrolled'),
							   ('discontinued', 'Discontinued'),
							   ('withdrawn', 'Withdrawn')],
							  string='Select In Active Status', required=True,)
	reason = fields.Char("Reason")
	learner_id = fields.Many2one('hr.employee',string = "Learner Id")

	@api.multi
	def action_in_active_status_button(self):
		current_leanrer_obj =self.env['hr.employee'].browse([self.env.context.get('active_id')])
		current_leanrer_obj.write({'learner_status':self.inactive_status,'state':'inactive', 'is_active':False, 'learners_status':'in_active', 'learner_master_status_ids':[(0, 0, {'learner_master_uid':self.env['res.users'].browse(self._uid).name, 'learner_master_status':'In Active', 'learner_master_date':datetime.now(), 'learner_master_comment':self.reason})]})
		qual_obj = self.env['learner.registration.qualification'].search([('learner_id','=',current_leanrer_obj.id)])
		if qual_obj:
			end_date_lst = [qual.end_date for qual in qual_obj if qual.end_date]
			if end_date_lst:
				latest_qual_obj = self.env['learner.registration.qualification'].search([('end_date','=',max(end_date_lst))])
				if latest_qual_obj:
					latest_qual_obj.write({'qual_status':self.inactive_status})
		return True
learner_inactive_status()

class learner_dropout_status(models.Model):
	_name = 'learner.dropout.status'
	_description = 'Learner Drop Out Status'

	reason = fields.Char("Reason")
	learner_id = fields.Many2one('hr.employee',string = "Learner Id")

	@api.multi
	def action_dropout_button(self):
		current_leanrer_obj =self.env['hr.employee'].browse([self.env.context.get('active_id')])
		current_leanrer_obj.write({'learner_status':'Drop Out','state':'dropout', 'is_drop_out':True, 'learners_status':'drop_out', 'learner_master_status_ids':[(0, 0, {'learner_master_uid':self.env['res.users'].browse(self._uid).name, 'learner_master_status':'Drop Out', 'learner_master_date':datetime.now(), 'learner_master_comment':self.reason})]})
		qual_obj = self.env['learner.registration.qualification'].search([('learner_id','=',current_leanrer_obj.id)])
		if qual_obj:
			end_date_lst = [qual.end_date for qual in qual_obj if qual.end_date]
			if end_date_lst:
				latest_qual_obj = self.env['learner.registration.qualification'].search([('end_date','=',max(end_date_lst))])
				if latest_qual_obj:
					latest_qual_obj.write({'qual_status':'Drop Out'})
		return True
learner_dropout_status()

class batch_master(models.Model):
	_name = 'batch.master'
	_description = 'Batch Master'
	_rec_name = 'batch_name'

	@api.model
	def default_get(self, fields):
		res = super(batch_master, self).default_get(fields)
		p_id = self.env.user.partner_id.id
		res.update(provider_id = p_id)
		return res

	@api.multi
	@api.depends('batch_name', 'batch_id')
	def name_get(self):
		res = []
		for record in self:
			rec_str = ''
			if record.batch_id:
				rec_str += '[' + record.batch_id + '] '
			if record.batch_name:
				rec_str += record.batch_name
			res.append((record.id, rec_str))
		return res

	@api.model
	def name_search(self, name='', args=[], operator='ilike', limit=1000):
		args += ['|', ('batch_name', operator, name), ('batch_id', operator, name)]
		cuur_ids = self.search(args, limit=limit)
		return cuur_ids.name_get()

	@api.model
	def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
		""" Override read_group to filter Batch Master status count based on logged provider """
		if self.env.user.id != 1 and self.env.user.partner_id.provider == True:
			batch_list = []
			self._cr.execute("select id from batch_master where provider_id='%s'" % (self.env.user.partner_id.id,))
			batch_ids = map(lambda x:x[0], self._cr.fetchall())
			batch_list.extend(batch_ids)
			self._cr.execute("select id from batch_master where create_uid='%s'" % (self.env.user.id,))
			batch_uids = map(lambda x:x[0], self._cr.fetchall())
			batch_list.extend(batch_uids)
			domain.append(('id', 'in', batch_list))
		return super(batch_master, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

	@api.model
	def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
		user = self._uid
		user_obj = self.env['res.users']
		user_data = user_obj.browse(user)
		user_groups = user_data.groups_id
		for group in user_groups:
			if group.name in ['ETQE Manager', 'ETQE Executive Manager', 'ETQE Provincial Manager', 'ETQE Officer', 'ETQE Provincial Officer', 'ETQE Administrator', 'ETQE Provincial Administrator', 'Applicant Skills Development Provider', 'CEO']:
				return super(batch_master, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		if user == 1:
			return super(batch_master, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		if user_data.partner_id.provider:
			batch_master_ids = []
			self._cr.execute("select id from batch_master where provider_id='%s'" % (user_data.partner_id.id,))
			batch_ids = map(lambda x:x[0], self._cr.fetchall())
			batch_master_ids.extend(batch_ids)
			self._cr.execute("select id from batch_master where create_uid='%s'" % (user_data.id,))
			batch_uids = map(lambda x:x[0], self._cr.fetchall())
			batch_master_ids.extend(batch_uids)
			args.append(('id', 'in', batch_master_ids))
			return super(batch_master, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		return super(batch_master, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

	provider_id = fields.Many2one('res.partner', string="Provider", track_visibility='onchange')
	batch_id = fields.Char("Batch ID")
	batch_name = fields.Char("Batch Name")
	batch_ids = fields.One2many('learner.registration.qualification','batch_id',string = "Batch")
	skills_batch_ids = fields.One2many('skills.programme.learner.rel','batch_id',string = "Batch")
	provider_master_batch_ids = fields.One2many('etqe.batch.provider.rel','batch_master_id','Batch provider reference')
	batch_ids = fields.One2many('provider.assessment', 'batch_id', 'Assessment Batch Rel')
	qual_skill_batch = fields.Selection([('qual', 'Qualifications'),
							   ('skill', 'Skills Programme'),
							   ('lp', 'Learning Programme'),],
							  string="Batch Type")
	is_learner_import = fields.Boolean('Learner Import')
	batch_status = fields.Selection([('open', 'Open'), ('closed', 'Closed'),], 'Status', default= 'open')
	qualification_id = fields.Many2one('provider.qualification', 'Qualification')
	skills_programme_id = fields.Many2one('skills.programme', 'Skills Programme')
	learning_programme_id = fields.Many2one('etqe.learning.programme', 'Learning Programme')
	_sql_constraints = [('batch_uniq', 'unique(batch_name)',
			'Batch Name must be unique!'),]

	@api.multi
	@api.onchange('is_learner_import')
	def onchange_is_learner_import(self):
		user = self._uid
		user_obj = self.env['res.users']
		user_data = user_obj.browse(user)
		qual_list, skill_list, lp_list = [], [], []
		if user_data.partner_id.provider:
			if self.env.user.partner_id.qualification_ids:
				for line in self.env.user.partner_id.qualification_ids:
					qualification_obj = self.env['provider.qualification'].search([('seta_branch_id','=','11'),('id','=',line.qualification_id.id)])
					if qualification_obj.id not in qual_list:
						qual_list.append(qualification_obj.id)
			if self.env.user.partner_id.qualification_ids:
				for line in self.env.user.partner_id.skills_programme_ids:
					skill_obj = self.env['skills.programme'].search([('seta_branch_id','=','11'),('id','=',line.skills_programme_id.id)])
					if skill_obj.id not in skill_list:
						skill_list.append(skill_obj.id)
			if self.env.user.partner_id.qualification_ids:
				for line in self.env.user.partner_id.learning_programme_ids:
					lp_obj = self.env['etqe.learning.programme'].search([('seta_branch_id','=','11'),('id','=',line.learning_programme_id.id)])
					if lp_obj.id not in lp_list:
						lp_list.append(lp_obj.id)
		return {'domain': {'qualification_id': [('id', 'in', qual_list)], 'skills_programme_id': [('id', 'in', skill_list)], 'learning_programme_id': [('id', 'in', lp_list)]}}



	@api.model
	def create(self, vals):
		if vals['qual_skill_batch'] == 'qual':
			vals['batch_id'] = self.env['ir.sequence'].get('batch.master')
		elif vals['qual_skill_batch'] == 'skill':
			vals['batch_id'] = self.env['ir.sequence'].get('batch.master.skills')
		elif vals['qual_skill_batch'] == 'lp':
			vals['batch_id'] = self.env['ir.sequence'].get('batch.master.lp')
		rec = super(batch_master, self).create(vals)
		partner_id = self.env.user.partner_id
		partner_id.write({'provider_batch_ids':[(0, 0, {'batch_master_id':rec.id, 'batch_status':rec.batch_status})]})
		return rec

	@api.multi
	def write(self, vals):
		context = self._context
		if context is None:
			context = {}
		res = super(batch_master, self).write(vals)
		# To update batch status in provider master==>>> Batches Tab
		partner_id =  self.env['res.partner'].search([('id','=',self.provider_id.id)])
		batch_id = self.env['etqe.batch.provider.rel'].search([('batch_provider_id','=',partner_id.id),('batch_master_id','=',self.id) ])
		if self.batch_status == 'open' and batch_id:
			batch_id.write({'batch_status': 'open'})
		if self.batch_status == 'closed' and batch_id:
			batch_id.write({'batch_status': 'closed'})
		return res

batch_master()

class etqe_batch_provider_rel(models.Model):
	_name = 'etqe.batch.provider.rel'

	batch_master_id = fields.Many2one("batch.master", 'Batch Name', ondelete='restrict')
	batch_status = fields.Selection([('open', 'Open'), ('closed', 'Closed'),], 'Status', default= 'open')
	batch_provider_id = fields.Many2one("res.partner",string = "Batch provider rel")

etqe_batch_provider_rel()

class moderators_qualification_line_hr(models.Model):
	_name = 'moderators.qualification.line.hr'
	_description = 'moderators_qualification_line_hr'
	_rec_name = 'type'

	name = fields.Char(string='Name')
#     type = fields.Char(string='Type')
	type = fields.Selection([
		('Core', 'Core'),
		('Fundamental', 'Fundamental'),
		('Elective', 'Elective'),
		('Knowledge Module', 'Knowledge Module'),
		('Practical Skill Module', 'Practical Skill Module'),
		('Work Experience Module', 'Work Experience Module'),
		('Exit Level Outcomes', 'Exit Level Outcomes'),
		], string='Type', track_visibility='onchange')
	id_no = fields.Char(string='ID NO')
	title = fields.Char(string='UNIT STANDARD TITLE')
	level1 = fields.Char(string='PRE-2009 NQF LEVEL')
	level2 = fields.Char(string='NQF LEVEL')
	level3 = fields.Char(string='CREDITS')
	selection = fields.Boolean(string="SELECTION")
	approved_denied = fields.Boolean(string='Approved Denied')
	status = fields.Selection([('requested_approval', 'Requested Approval'),
							   ('approved', 'Approved'),
							   ('denied', 'Denied')],
							  string='State', readonly=True, default='requested_approval')
	line_hr_id = fields.Many2one('moderators.qualification.hr', 'Qualification Hr Reference', required=True, ondelete='cascade')

	@api.multi
	def action_approve_unit(self):
		self.write({'approved_denied':True, 'status':'approved'})
		return True

	@api.multi
	def action_deny_unit(self):
		self.write({'approved_denied':False, 'status':'denied'})
moderators_qualification_line_hr()

class moderators_qualification_hr(models.Model):
	_name = 'moderators.qualification.hr'
	_description = 'Moderators Qualification Hr'

	qualification_hr_id = fields.Many2one("provider.qualification", 'Qualification', ondelete='restrict')
	qualification_line_hr = fields.One2many('moderators.qualification.line.hr', 'line_hr_id', 'Qualification hr Lines', domain=[('selection', '=', True)])
	moderators_qualification_hr_id = fields.Many2one('hr.employee', 'Hr Employee Reference', required=True, ondelete='cascade')
	current_hr_id = fields.Integer('hr_id')
	saqa_qual_id = fields.Char(string='ID')
	qualification_status = fields.Selection([('draft', 'Draft'), ('waiting_approval', 'Waiting Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], string="State", default='draft')
	request_send = fields.Boolean(string='Send Request', default=False)
	approval_request = fields.Boolean(string='Approval Request', default=False)
	reject_request = fields.Boolean(string="Reject Request", default=False)
	qual_unit_type = fields.Selection([('qual','Qualification'),('unit','Unit Standards')], default='qual')

	@api.multi
	def onchange_qualification(self, qualification_evaluation_id):
		accreditation_qualification_line = []
		current_hr_obj = self.env['hr.employee'].browse(self.current_hr_id)
		same_id_no_list = []
		if current_hr_obj:
			for hr_qual_line in current_hr_obj.qualification_ids:
				if hr_qual_line.qualification_hr_id.id == qualification_evaluation_id:
					for lines in hr_qual_line.qualification_line_hr:
						same_id_no_list.append(lines.id_no)
		if qualification_evaluation_id:
			qualification_obj = self.env['provider.qualification'].browse(qualification_evaluation_id)
			for qualification_lines in qualification_obj.qualification_line:
				if qualification_lines.id_no not in same_id_no_list:
					val = {
							 'name':qualification_lines.name,
							 'type':qualification_lines.type,
							 'id_no':qualification_lines.id_no,
							 'title':qualification_lines.title,
							 'level1':qualification_lines.level1,
							 'level2':qualification_lines.level2,
							 'level3': qualification_lines.level3,
							}
					accreditation_qualification_line.append((0, 0, val))
			return {'value':{'saqa_qual_id':qualification_obj.saqa_qual_id, 'qualification_line_hr':accreditation_qualification_line, 'qualification_status':'draft'}}
		return {}

	@api.multi
	def action_send_request(self):
		self.write({'qualification_status':'waiting_approval', 'request_send':True})

	@api.multi
	def action_approved_request(self):
		self.write({'qualification_status':'approved', 'approval_request':True})

	@api.multi
	def action_rejected_request(self):
		self.write({'qualification_status':'rejected', 'reject_request':True})
moderators_qualification_hr()

class assessors_moderators_qualification_line_hr(models.Model):
	_name = 'assessors.moderators.qualification.line.hr'
	_description = 'assessors_moderators_qualification_line_hr'
	_rec_name = 'type'

	name = fields.Char(string='Name')
#     type = fields.Char(string='Type')
	type = fields.Selection([
	('Core', 'Core'),
	('Fundamental', 'Fundamental'),
	('Elective', 'Elective'),
	('Knowledge Module', 'Knowledge Module'),
	('Practical Skill Module', 'Practical Skill Module'),
	('Work Experience Module', 'Work Experience Module'),
	('Exit Level Outcomes', 'Exit Level Outcomes'),
	], string='Type', track_visibility='onchange')
	id_no = fields.Char(string='ID NO')
	title = fields.Char(string='UNIT STANDARD TITLE')
	level1 = fields.Char(string='PRE-2009 NQF LEVEL')
	level2 = fields.Char(string='NQF LEVEL')
	level3 = fields.Char(string='CREDITS')
	selection = fields.Boolean(string="SELECTION")
	approved_denied = fields.Boolean(string='Approved Denied')
	status = fields.Selection([('requested_approval', 'Requested Approval'),
							   ('approved', 'Approved'),
							   ('denied', 'Denied')],
							  string='State', readonly=True, default='requested_approval')

	line_hr_id = fields.Many2one('assessors.moderators.qualification.hr', 'Qualification Hr Reference', required=True, ondelete='cascade')

	@api.multi
	def action_approve_unit(self):
		self.write({'approved_denied':True, 'status':'approved'})
		return True

	@api.multi
	def action_deny_unit(self):
		self.write({'approved_denied':False, 'status':'denied'})
assessors_moderators_qualification_line_hr()

class assessors_moderators_qualification_hr(models.Model):
	_name = 'assessors.moderators.qualification.hr'
	_description = 'Assessors Moderators Qualification Hr'

	qualification_hr_id = fields.Many2one("provider.qualification", 'Qualification', ondelete='restrict')
	qualification_line_hr = fields.One2many('assessors.moderators.qualification.line.hr', 'line_hr_id', 'Qualification hr Lines', domain=[('selection', '=', True)])
	assessors_moderators_qualification_hr_id = fields.Many2one('hr.employee', 'Hr Employee Reference', required=True, ondelete='cascade')
	current_hr_id = fields.Integer('hr_id')
	saqa_qual_id = fields.Char(string='ID')
	qualification_status = fields.Selection([('draft', 'Draft'), ('waiting_approval', 'Waiting Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], string="State", default='draft')
	request_send = fields.Boolean(string='Send Request', default=False)
	approval_request = fields.Boolean(string='Approval Request', default=False)
	reject_request = fields.Boolean(string="Reject Request", default=False)
	qual_unit_type = fields.Selection([('qual','Qualification'),('unit','Unit Standards')], default='qual')

	@api.multi
	def onchange_qualification(self, qualification_evaluation_id):
		accreditation_qualification_line = []
		current_hr_obj = self.env['hr.employee'].browse(self.current_hr_id)
		same_id_no_list = []
		if current_hr_obj:
			for hr_qual_line in current_hr_obj.qualification_ids:
				if hr_qual_line.qualification_hr_id.id == qualification_evaluation_id:
					for lines in hr_qual_line.qualification_line_hr:
						same_id_no_list.append(lines.id_no)
		if qualification_evaluation_id:
			qualification_obj = self.env['provider.qualification'].browse(qualification_evaluation_id)
			for qualification_lines in qualification_obj.qualification_line:
				if qualification_lines.id_no not in same_id_no_list:
					val = {
							 'name':qualification_lines.name,
							 'type':qualification_lines.type,
							 'id_no':qualification_lines.id_no,
							 'title':qualification_lines.title,
							 'level1':qualification_lines.level1,
							 'level2':qualification_lines.level2,
							 'level3': qualification_lines.level3,
							}
					accreditation_qualification_line.append((0, 0, val))
			return {'value':{'saqa_qual_id':qualification_obj.saqa_qual_id, 'qualification_line_hr':accreditation_qualification_line, 'qualification_status':'draft'}}
		return {}

	@api.multi
	def action_send_request(self):
		self.write({'qualification_status':'waiting_approval', 'request_send':True})

	@api.multi
	def action_approved_request(self):
		self.write({'qualification_status':'approved', 'approval_request':True})

	@api.multi
	def action_rejected_request(self):
		self.write({'qualification_status':'rejected', 'reject_request':True})
assessors_moderators_qualification_hr()

class assessors_moderators_qualification_line_evaluation(models.Model):
	_name = 'assessors.moderators.qualification.line.evaluation'
	_description = 'assessors_moderators_qualification_line_evaluation'
	_rec_name = 'type'

	name = fields.Char(string='Name')
#     type = fields.Char(string='Type')
	type = fields.Selection([
	('Core', 'Core'),
	('Fundamental', 'Fundamental'),
	('Elective', 'Elective'),
	('Knowledge Module', 'Knowledge Module'),
	('Practical Skill Module', 'Practical Skill Module'),
	('Work Experience Module', 'Work Experience Module'),
	('Exit Level Outcomes', 'Exit Level Outcomes'),
	], string='Type', track_visibility='onchange')
	id_no = fields.Char(string='ID NO')
	title = fields.Char(string='UNIT STANDARD TITLE')
	level1 = fields.Char(string='PRE-2009 NQF LEVEL')
	level2 = fields.Char(string='NQF LEVEL')
	level3 = fields.Char(string='CREDITS')
	selection = fields.Boolean(string="SELECTION")
	line_evaluation_id = fields.Many2one('assessors.moderators.qualification.evaluation', 'Qualification Evaluation Reference', required=True, ondelete='cascade')
assessors_moderators_qualification_line_evaluation()

class learner_registration_qualification(models.Model):
	_name = 'learner.registration.qualification'
	_description = 'Learner Registration Qualification'

	@api.one
	@api.depends('learner_registration_line_ids.selection')
	def _cal_limit(self):
		total_credit_point = 0
		if self.learner_registration_line_ids:
			for unit_line in self.learner_registration_line_ids:
				try:
					if unit_line.selection:
						if unit_line.level3:
							total_credit_point += int(unit_line.level3)
				except:
					pass
		self.total_credits = total_credit_point

	@api.model
	def default_get(self, fields):
		context = self._context
		if context is None:
			context = {}
		res = super(learner_registration_qualification, self).default_get(fields)
		return res

	learner_qualification_id = fields.Many2one('learner.registration')
	learner_qualification_parent_id = fields.Many2one('provider.qualification', 'Qualification')
	learner_registration_line_ids = fields.One2many('learner.registration.qualification.line', 'learner_reg_id')
	start_date = fields.Date()
	end_date = fields.Date()
	approval_date = fields.Date()
	provider_id = fields.Many2one('res.partner', string="Provider", track_visibility='onchange', default=lambda self:self.env.user.partner_id.id)
	learner_id = fields.Many2one('hr.employee', string="Learner")
	is_learner_achieved = fields.Boolean(string="Competent", default=False)
	assessors_id = fields.Many2one("hr.employee", string='Assessor', domain=[('is_active_assessor','=',True),('is_assessors', '=', True)])
	assessor_date = fields.Date("Assessor End Date")
	moderators_id = fields.Many2one("hr.employee", string='Moderator', domain=[('is_active_moderator','=',True),('is_moderators', '=', True)])
	moderator_date = fields.Date("Moderator End Date")
	minimum_credits = fields.Integer(related="learner_qualification_parent_id.m_credits", string="Minimum Credits")
	total_credits = fields.Integer(compute="_cal_limit" , string="Total Credits", store=True)
	certificate_no = fields.Char("Certificate No.")
	is_complete = fields.Boolean("Achieve", default=False)
	batch_id = fields.Many2one('batch.master',string = 'Batch')
	certificate_date = fields.Date("Certificate Date")
	qual_status = fields.Char("Status")

	@api.multi
	@api.onchange('learner_qualification_parent_id')
	def onchange_qualification(self, learner_qualification_parent_id):
		user = self._uid
		user_obj = self.env['res.users']
		user_data = user_obj.browse(user)
		assessors_lst, moderators_lst, batch_lst, qual_id = [], [], [], []
		if user_data.partner_id.provider:
			if self.env.user.partner_id.assessors_ids:
				for assessor in self.env.user.partner_id.assessors_ids:
					if assessor.assessors_id.is_active_assessor:
						assessors_lst.append(assessor.assessors_id.id)
			if self.env.user.partner_id.moderators_ids:
				for moderator in self.env.user.partner_id.moderators_ids:
					if moderator.moderators_id.is_active_moderator:
						moderators_lst.append(moderator.moderators_id.id)
			if self.env.user.partner_id.provider_batch_ids:
				for batch in self.env.user.partner_id.provider_batch_ids:
					if batch.batch_master_id.qual_skill_batch == 'qual' and batch.batch_status == 'open':
						batch_lst.append(batch.batch_master_id.id)
			for line in self.env.user.partner_id.qualification_ids:
				qualification_obj = self.env['provider.qualification'].search([('seta_branch_id','=','11'),('id','=',line.qualification_id.id)])
				if qualification_obj.id not in qual_id:
					qual_id.append(qualification_obj.id)
		if not user_data.partner_id.provider:
			batch_obj = self.env['batch.master'].search([('qual_skill_batch', '=', 'qual'),('batch_status','=','open')])
			if batch_obj:
				for obj in batch_obj:
					batch_lst.append(obj.id)
		learner_qualification_line, core_lst, fundamental_lst, elective_lst, other_lst = [], [], [], [], []
		# Commented following code Giving problem when we fetch non-SA learners because context is passed based on identification id
		'''Code to avoid those qualifications which are already exist in learner master in extension of scope learner process'''
#         if self._context.get('existing_learner') == True and not self._context.get('learner_master_id_number'):
#             return {'warning':{'title':'Warning','message':'Please Enter Identification Number to fetch existing learner details!!'}}
		if self._context.get('existing_learner') == True and self._context.get('learner_master_id_number'):
			learner_master_object = self.env['hr.employee'].search([('learner_identification_id', '=', self._context.get('learner_master_id_number'))])
			if learner_master_object:
				learner_master_qualification_obj = self.env['learner.registration.qualification'].search([('learner_id', '=',learner_master_object.id)])
				if learner_master_qualification_obj:
					for master_qual in learner_master_qualification_obj:
						if master_qual.learner_qualification_parent_id.id in qual_id:
							qual_id.remove(master_qual.learner_qualification_parent_id.id)
		if learner_qualification_parent_id:
			if user_data.partner_id.provider:
				qualification_obj = self.env['provider.master.qualification'].browse(learner_qualification_parent_id)
				for line in self.env.user.partner_id.qualification_ids:
					if qualification_obj.id == line.qualification_id.id:
						for u_line in line.qualification_line:
							if u_line.selection == True or u_line.type == 'Exit Level Outcomes':
								select = True
							else:
								select = False
							is_achieve = False
							if self._context.get('learner_master_id_number'):
								learner_master_obj = self.env['hr.employee'].search([('learner_identification_id', '=', self._context.get('learner_master_id_number'))])
								if learner_master_obj:
									learner_line_obj = self.env['learner.registration.qualification.line'].search([('learner_reg_id','=',learner_qualification_parent_id),('id_data', '=', u_line.id_data)])
									for line_obj in learner_line_obj:
										if line_obj.learner_reg_id.learner_id.id == learner_master_obj.id :
											for q_line in line_obj.learner_reg_id.learner_id.learner_qualification_ids:
												for unit_line in q_line.learner_registration_line_ids:
													if u_line.title == unit_line.title:
														is_achieve = unit_line.achieve
											break
							val = {
									'name':u_line.name,
									'type':u_line.type,
									'id_data':u_line.id_data,
									'title':u_line.title,
									'level1':u_line.level1,
									'level2':u_line.level2,
									'level3': u_line.level3,
									'selection':select,
									'is_seta_approved': u_line.is_seta_approved,
									'is_provider_approved': u_line.is_provider_approved,
									'achieve':is_achieve,
									}
							if select == True:
								learner_qualification_line.append((0, 0, val))
							else:
								pass
			elif not user_data.partner_id.provider:
				qualification_obj = self.env['provider.qualification'].search([('seta_branch_id','=','11'),('id','=',learner_qualification_parent_id)])
				for qualification_lines in qualification_obj.qualification_line:
					if qualification_lines.type == 'Core' :
						val = {
							   'name':qualification_lines.name,
							   'type':qualification_lines.type,
							   'id_data':qualification_lines.id_no,
							   'title':qualification_lines.title,
								'level1':qualification_lines.level1,
								'level2':qualification_lines.level2,
								'level3': qualification_lines.level3,
								'selection':True
							   }
						core_lst.append((0, 0, val))
					elif qualification_lines.type == 'Fundamental':
						val = {
							   'name':qualification_lines.name,
							   'type':qualification_lines.type,
							   'id_data':qualification_lines.id_no,
							   'title':qualification_lines.title,
								'level1':qualification_lines.level1,
								'level2':qualification_lines.level2,
								'level3': qualification_lines.level3,
								'selection':True
							   }
						fundamental_lst.append((0, 0, val))
					elif qualification_lines.type == 'Elective':
						val = {
								'name':qualification_lines.name,
								'type':qualification_lines.type,
								'id_data':qualification_lines.id_no,
								'title':qualification_lines.title,
								'level1':qualification_lines.level1,
								'level2':qualification_lines.level2,
								'level3': qualification_lines.level3,
								'is_seta_approved': qualification_lines.is_seta_approved,
								'is_provider_approved': qualification_lines.is_provider_approved,
							   }
						if qualification_lines.is_seta_approved:
							val.update({
										 'selection':True,
										})
						elective_lst.append((0, 0, val))
					else:
						val = {
								'name':qualification_lines.name,
								'type':qualification_lines.type,
								'id_data':qualification_lines.id_no,
								'title':qualification_lines.title,
								'level1':qualification_lines.level1,
								'level2':qualification_lines.level2,
								'level3': qualification_lines.level3,
							   }
						other_lst.append((0, 0, val))
				learner_qualification_line = core_lst + fundamental_lst + elective_lst + other_lst
			return {'value':{'learner_registration_line_ids':learner_qualification_line},
					'domain':{'learner_qualification_parent_id': [('id', 'in', qual_id)],
							  'assessors_id': [('id', 'in', assessors_lst)],
							  'moderators_id':[('id', 'in', moderators_lst)],
							  'batch_id':[('id','in',batch_lst)]}}
#             return {'domain':{'learner_qualification_parent_id': [('id', 'in', qual_id)]}}
		elif qual_id:
			return {'domain': {'learner_qualification_parent_id': [('id', 'in', qual_id)],
							   'assessors_id': [('id', 'in', assessors_lst)],
							   'moderators_id':[('id', 'in', moderators_lst)],
							   'batch_id':[('id','in',batch_lst)]}}
		elif not learner_qualification_parent_id and not user_data.partner_id.provider:
			q_lst = []
			qualification_obj = self.env['provider.qualification'].search([('seta_branch_id','=','11')])
			if qualification_obj:
				for obj in qualification_obj:
					q_lst.append(obj.id)
				return {'domain': {'learner_qualification_parent_id': [('id', 'in', q_lst)],
								   'batch_id':[('id','in',batch_lst)]}}
		return {'domain': {'learner_qualification_parent_id': [('id', 'in', [])]}}

	@api.multi
	def onchange_assessors_id(self, assessors_id):
		res = {}
		if not assessors_id:
			return res
		if assessors_id:
			assessor_brw_id = self.env['hr.employee'].search([('id', '=', assessors_id)])
			res.update({'value':{'assessor_date':assessor_brw_id.end_date}})
		return res

	@api.multi
	def onchange_moderators_id(self, moderators_id):
		res = {}
		if not moderators_id:
			return res
		if moderators_id:
			moderator_brw_id = self.env['hr.employee'].search([('id', '=', moderators_id)])
			res.update({'value':{'moderator_date':moderator_brw_id.end_date}})
		return res

	@api.model
	def _search(self, args, offset=0, limit=80, order=None, count=False, access_rights_uid=None):
		user = self._uid
		user_obj = self.env['res.users']
		user_data = user_obj.browse(user)
		user_groups = user_data.groups_id
		for group in user_groups:
			if group.name in ['ETQE Manager', 'ETQE Executive Manager', 'ETQE Provincial Manager', 'ETQE Officer', 'ETQE Provincial Officer', 'ETQE Administrator', 'ETQE Provincial Administrator', 'Applicant Skills Development Provider', 'CEO']:
				return super(learner_registration_qualification, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		if user == 1 :
			return super(learner_registration_qualification, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		self._cr.execute("select id from learner_registration_qualification where provider_id=%s" % (user_data.partner_id.id))
		learner_ids = self._cr.fetchall()
		args.append(('id', 'in', learner_ids))
		return super(learner_registration_qualification, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

learner_registration_qualification()

class learner_registration_qualification_line(models.Model):
	_name = 'learner.registration.qualification.line'
	_description = 'Learner Registration Qualification Line'

	@api.multi
	def _get_provider(self):
		context = self._context
		provider_id = context.get('provider_id')
		return provider_id

	name = fields.Char(string='Name')
#     type = fields.Char(string='Type')
	type = fields.Selection([
	('Core', 'Core'),
	('Fundamental', 'Fundamental'),
	('Elective', 'Elective'),
	('Knowledge Module', 'Knowledge Module'),
	('Practical Skill Module', 'Practical Skill Module'),
	('Work Experience Module', 'Work Experience Module'),
	('Exit Level Outcomes', 'Exit Level Outcomes'),
	], string='Type', track_visibility='onchange')
	id_data = fields.Char(string='ID')
	title = fields.Char(string='UNIT STANDARD TITLE')
	level1 = fields.Char(string='PRE-2009 NQF LEVEL')
	level2 = fields.Char(string='NQF LEVEL')
	level3 = fields.Char(string='CREDITS')
	selection = fields.Boolean(string="SELECTION")
	learner_reg_id = fields.Many2one('learner.registration.qualification')
	provider_id = fields.Many2one('res.partner', string="Provider", track_visibility='onchange', _default=_get_provider)
	is_seta_approved = fields.Boolean(
		string='SETA Learning Material', track_visibility='onchange')
	is_provider_approved = fields.Boolean(
		string='PROVIDER Learning Material', track_visibility='onchange')
	achieve = fields.Boolean("ACHIEVE", default=False)
	is_rpl_learner = fields.Boolean("RPL Learner", default=False)
learner_registration_qualification_line()

class assessors_moderators_qualification_evaluation(models.Model):
	_name = 'assessors.moderators.qualification.evaluation'
	_inherit = 'mail.thread'
	_description = 'Assessors Moderators Qualification Evaluation'

	qualification_evaluation_id = fields.Many2one("provider.qualification", 'Qualification', ondelete='restrict',  track_visibility="always")
	saqa_qual_id = fields.Char(string='ID')
	qualification_line_evaluation = fields.One2many('assessors.moderators.qualification.line.evaluation', 'line_evaluation_id', 'Qualification Lines', domain=[('selection', '=', True)])
	assessors_moderators_qualification_evaluation_id = fields.Many2one('assessors.moderators.register', 'Assessors Moderators Register Reference', required=True, ondelete='cascade')
	minimum_credits = fields.Integer(string="Minimum Credits")
	total_credits = fields.Integer(string="Total Credits", store=True)
	select = fields.Boolean("Selection", default=True)
	verify = fields.Boolean('Verify', default=False, track_visibility="onchange")
	qual_unit_type = fields.Selection([('qual','Qualification'),('unit','Unit Standards')])

	@api.multi
	def onchange_qualification(self, qualification_evaluation_id):
		accreditation_qualification_line = []
		if qualification_evaluation_id:
			qualification_obj = self.env['provider.qualification'].browse(qualification_evaluation_id)
			for qualification_lines in qualification_obj.qualification_line:
				val = {
						 'name':qualification_lines.name,
						 'type':qualification_lines.type,
						 'id_no':qualification_lines.id_no,
						 'title':qualification_lines.title,
						 'level1':qualification_lines.level1,
						 'level2':qualification_lines.level2,
						 'level3': qualification_lines.level3,
						}
				accreditation_qualification_line.append((0, 0, val))
			return {'value':{'saqa_qual_id':qualification_obj.saqa_qual_id, 'qualification_line_evaluation':accreditation_qualification_line}}
		return {}
assessors_moderators_qualification_evaluation()

class assessors_moderators_qualification_line(models.Model):
	_name = 'assessors.moderators.qualification.line'
	_description = 'assessors_moderators_qualification_line'
	_rec_name = 'type'

	name = fields.Char(string='Name')
#     type = fields.Char(string='Type')
	type = fields.Selection([
	('Core', 'Core'),
	('Fundamental', 'Fundamental'),
	('Elective', 'Elective'),
	('Knowledge Module', 'Knowledge Module'),
	('Practical Skill Module', 'Practical Skill Module'),
	('Work Experience Module', 'Work Experience Module'),
	('Exit Level Outcomes', 'Exit Level Outcomes'),
	], string='Type', track_visibility='onchange')
	id_no = fields.Char(string='ID NO')
	title = fields.Char(string='UNIT STANDARD TITLE')
	level1 = fields.Char(string='PRE-2009 NQF LEVEL')
	level2 = fields.Char(string='NQF LEVEL')
	level3 = fields.Char(string='CREDITS')
	selection = fields.Boolean(string="SELECTION")
	is_unit = fields.Boolean("Is Unit")
	line_id = fields.Many2one('assessors.moderators.qualification', 'Qualification Reference', required=True, ondelete='cascade')
assessors_moderators_qualification_line()

class assessors_moderators_status(models.Model):
	_name = 'assessors.moderators.status'
	_description = 'Assessors Moderators Status'

	assessors_moderators_status_mo_id = fields.Many2one('assessors.moderators.register', string='Assessors Moderators Status Reference')
	am_name = fields.Char(string="Name")
	am_status = fields.Char(string="Status")
	am_comment = fields.Char(string="Comment")
	am_date = fields.Datetime(string="Date")
	am_updation_date = fields.Datetime(string="Update Date")

assessors_moderators_status()

class assessors_moderators_qualification(models.Model):
	_name = 'assessors.moderators.qualification'
	_description = 'Assessors Moderators Qualification'

	qualification_id = fields.Many2one("provider.qualification", 'Qualification', ondelete='restrict')
	saqa_qual_id = fields.Char(string='ID')
	qualification_line = fields.One2many('assessors.moderators.qualification.line', 'line_id', 'Qualification Lines')
	assessors_moderators_qualification_id = fields.Many2one('assessors.moderators.register', 'Assessors Moderators Register Reference', required=True, ondelete='cascade')
	select = fields.Boolean('Selection', default=True)
	minimum_credits = fields.Integer(related="qualification_id.m_credits", string="Minimum Credits")
	total_credits = fields.Integer(compute="_cal_limit" , string="Total Credits", store=True)
	qual_unit_type = fields.Selection([('qual','Qualification'),('unit','Unit Standards')], default='qual')

	@api.onchange('qual_unit_type')
	def onchange_qual_unit_type(self):
		if self.qual_unit_type:
			self.qualification_id = False

	@api.one
	@api.depends('qualification_line.selection')
	def _cal_limit(self):
		total_credit_point = 0
		if self.qualification_line:
			for unit_line in self.qualification_line:
				if unit_line.selection:
					if unit_line.level3:
						total_credit_point += int(unit_line.level3)
		self.total_credits = total_credit_point

	@api.multi
	def onchange_qualification(self, qual_unit_type, qualification_id):
		accreditation_qualification_line, core_lst, fundamental_lst, elective_lst, other_lst = [], [], [], [], []
		qual_list = []
		qualification_obj = self.env['provider.qualification'].search(['|',('seta_branch_id','=','11'),('is_ass_mod_linked','=',True)])
		if qualification_obj:
			for q in qualification_obj:
				qual_list.append(q.id)
		'''Code to avoid those qualifications which are already exist in assessor/moderator master in extension of scope provider process'''
		if self._context.get('extension_of_scope') == True and self._context.get('ass_or_mod') == 'ex_assessor' and self._context.get('search_by') == 'id' and not self._context.get('ex_as_id'):
			return {'warning':{'title':'Warning','message':'Please Enter Assessor Identification No. in General Information to fetch existing Assessor details then only apply for Qualification!!'}}
		if self._context.get('extension_of_scope') == True and self._context.get('ass_or_mod') == 'ex_assessor' and self._context.get('search_by') == 'number' and not self._context.get('ex_as_num'):
			return {'warning':{'title':'Warning','message':'Please Enter Assessor Number. in General Information to fetch existing Assessor details then only apply for Qualification!!'}}
		if self._context.get('extension_of_scope') == True and self._context.get('ass_or_mod') == 'ex_moderator' and self._context.get('search_by') == 'id' and not self._context.get('ex_mo_id'):
			return {'warning':{'title':'Warning','message':'Please Enter Moderator Identification No. in General Information to fetch existing Moderator details then only apply for Qualification!!'}}
		if self._context.get('extension_of_scope') == True and self._context.get('ass_or_mod') == 'ex_moderator' and self._context.get('search_by') == 'number' and not self._context.get('ex_mo_num'):
			return {'warning':{'title':'Warning','message':'Please Enter Moderator Number. in General Information to fetch existing Moderator details then only apply for Qualification!!'}}

		'''For Assessor Extension of Scope'''
		assessor_master_objects = []
		if self._context.get('extension_of_scope') == True and self._context.get('ass_or_mod') == 'ex_assessor' and self._context.get('search_by') == 'id' and self._context.get('ex_as_id'):
			assessor_master_objects = self.env['hr.employee'].search([('assessor_moderator_identification_id', '=', self._context.get('ex_as_id'))])
		elif self._context.get('extension_of_scope') == True and self._context.get('ass_or_mod') == 'ex_assessor' and self._context.get('search_by') == 'number' and self._context.get('ex_as_num'):
			assessor_master_objects = self.env['hr.employee'].search([('assessor_seq_no', '=', self._context.get('ex_as_num'))])
		if assessor_master_objects:
			pro_lst = []
			for pro_obj in assessor_master_objects:
				pro_lst.append(pro_obj.id)
			assessor_obj = self.env['hr.employee'].search([('id', '=', max(pro_lst))])
			if assessor_obj:
				if assessor_obj.qualification_ids:
					for master_qual in assessor_obj.qualification_ids:
						if master_qual.qualification_hr_id.id in qual_list:
							qual_list.remove(master_qual.qualification_hr_id.id)
		'''For Moderator Extension of Scope'''
		moderator_master_objects = []
		if self._context.get('extension_of_scope') == True and self._context.get('ass_or_mod') == 'ex_moderator' and self._context.get('search_by') == 'id' and self._context.get('ex_mo_id'):
			moderator_master_objects = self.env['hr.employee'].search([('assessor_moderator_identification_id', '=', self._context.get('ex_mo_id'))])
		elif self._context.get('extension_of_scope') == True and self._context.get('ass_or_mod') == 'ex_moderator' and self._context.get('search_by') == 'number' and self._context.get('ex_mo_num'):
			moderator_master_objects = self.env['hr.employee'].search([('moderator_seq_no', '=', self._context.get('ex_mo_num'))])
		if moderator_master_objects:
			pro_lst = []
			for pro_obj in moderator_master_objects:
				pro_lst.append(pro_obj.id)
			moderator_obj = self.env['hr.employee'].search([('id', '=', max(pro_lst))])
			if moderator_obj:
				if moderator_obj.moderator_qualification_ids:
					for master_qual in moderator_obj.moderator_qualification_ids:
						if master_qual.qualification_hr_id.id in qual_list:
							qual_list.remove(master_qual.qualification_hr_id.id)

		if qualification_id:
			qualification_obj = self.env['provider.qualification'].browse(qualification_id)
			for qualification_lines in qualification_obj.qualification_line:
				if qualification_lines.type == 'Core' :
					val = {
							 'name':qualification_lines.name,
							 'type':qualification_lines.type,
							 'id_no':qualification_lines.id_no,
							 'title':qualification_lines.title,
							 'level1':qualification_lines.level1,
							 'level2':qualification_lines.level2,
							 'level3': qualification_lines.level3,
							 'selection':True
							}
					if qual_unit_type == 'qual':
						val.update({'is_unit':True})
					else:
						val.update({'is_unit':False, 'selection':False})
					core_lst.append((0, 0, val))
				elif qualification_lines.type == 'Fundamental':
					val = {
							 'name':qualification_lines.name,
							 'type':qualification_lines.type,
							 'id_no':qualification_lines.id_no,
							 'title':qualification_lines.title,
							 'level1':qualification_lines.level1,
							 'level2':qualification_lines.level2,
							 'level3': qualification_lines.level3,
							 'selection':True
							}
					if qual_unit_type == 'qual':
						val.update({'is_unit':True})
					else:
						val.update({'is_unit':False,'selection':False})
					fundamental_lst.append((0, 0, val))
				elif qualification_lines.type == 'Elective':
					val = {
							 'name':qualification_lines.name,
							 'type':qualification_lines.type,
							 'id_no':qualification_lines.id_no,
							 'title':qualification_lines.title,
							 'level1':qualification_lines.level1,
							 'level2':qualification_lines.level2,
							 'level3': qualification_lines.level3,
							 'selection':True
							}
					if qual_unit_type == 'qual':
						val.update({'is_unit':True})
					else:
						val.update({'is_unit':False, 'selection':False})
					elective_lst.append((0, 0, val))
				else:
					val = {
							 'name':qualification_lines.name,
							 'type':qualification_lines.type,
							 'id_no':qualification_lines.id_no,
							 'title':qualification_lines.title,
							 'level1':qualification_lines.level1,
							 'level2':qualification_lines.level2,
							 'level3': qualification_lines.level3,
							}
					other_lst.append((0, 0, val))
			accreditation_qualification_line = core_lst + fundamental_lst + elective_lst + other_lst
			return {'value':{'qualification_line':accreditation_qualification_line, 'saqa_qual_id':qualification_obj.saqa_qual_id}}
		return {'domain': {'qualification_id': [('id', 'in',qual_list)]}}
assessors_moderators_qualification()

class etqe_config(models.Model):
	_name = 'etqe.config'

#     from_effective_date = fields.Date(string='Effective From Date' , required=True)
#     etqa_end_date = fields.Integer("ETQA End Date")
	seta_license_end_date = fields.Date(string='Seta License End Date' , required=True)
	etqa_end_date = fields.Integer("ETQA End Date in No. of Years" , required=True)
	before_expiry_visible_days = fields.Integer("Enter date period in number of days")
etqe_config()

class assessors_moderators_register(models.Model):
	_name = 'assessors.moderators.register'
	_inherit = 'mail.thread'

	@api.v7
	def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
		res = models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
		if view_type == 'form':
			doc = etree.XML(res['arch'])
			for sheet in doc.xpath("//sheet"):
				parent = sheet.getparent()
				index = parent.index(sheet)
				for child in sheet:
					parent.insert(index, child)
					index += 1
				parent.remove(sheet)
			res['arch'] = etree.tostring(doc)
		return res

	@api.depends('state')
	def _get_qulification_md(self):
		if self.state == 'qualification_info' and self.assessor_moderator == 'moderator' and not self.is_extension_of_scope and not self.already_registered:
			self.is_md = True
		else:
			self.is_md = False

	temp_assessor_seq_no = fields.Char("Assessor ID")
	temp_moderator_seq_no = fields.Char("Moderator ID")
	already_registered = fields.Boolean("Re-registration", default=False)
	is_extension_of_scope = fields.Boolean("Extension of Scope", default=False)
	existing_assessor_moderator = fields.Selection([('ex_assessor', 'Assessor'), ('ex_moderator', 'Moderator')], string="Existing Assessor/Moderator")
	search_by = fields.Selection([('id', 'Identification No'), ('number', 'Assessor/Moderator Number')], string="Search by")
	existing_assessor_id = fields.Char('Assessor Identification No')
	existing_moderator_id = fields.Char('Moderator Identification No')
	existing_assessor_number = fields.Char('Assessor Number')
	existing_moderator_number = fields.Char('Moderator Number')
	name = fields.Char(string="Name", required=True)
	work_email = fields.Char(string='Work Email', required=True)
	work_phone = fields.Char(string='Work Phone', size=10)
	mobile_phone = fields.Char(string='Work Mobile', size=10)
	work_location = fields.Char(string='Office Location')
	coach_id = fields.Many2one('hr.employee', string='Coach')
	user_id = fields.Many2one('res.users', string='Related User')
	notes = fields.Text(string='Notes')
	company_id = fields.Many2one('res.company', string='Company')
	department = fields.Char(string='Department')
	job_title = fields.Char(string='Job Title')
	manager = fields.Char(string='Manager')
	work_address = fields.Char(string='Work Address')
	work_address2 = fields.Char(string='Street2')
	work_address3 = fields.Char(string='Street3')
	work_city = fields.Many2one('res.city', string='Work City', track_visibility='onchange')
	work_province = fields.Many2one('res.country.state', string='Province')
	work_zip = fields.Char(string='Zip')
	work_country = fields.Many2one('res.country', string='Country')
	country_id = fields.Many2one('res.country', string='Nationality')
	identification_id = fields.Char(string='Identification No', size=13)
	passport_id = fields.Char(string='Passport No')
	bank_account_number = fields.Char(string='Bank Account Number')
	otherid = fields.Char(string='Other Id')
	national_id = fields.Char(string='National Id', size=13)
	home_language_code = fields.Many2one('res.lang', string='Home Language Code', track_visibility='onchange', size=6)
	citizen_resident_status_code = fields.Selection([('dual', 'D - Dual (SA plus other)'), ('other', 'O - Other'), ('PR', 'PR - Permanent Resident'), ('sa', 'SA - South Africa'), ('unknown', 'U - Unknown')], string='Citizen Status')
	filler01 = fields.Char(string='Filler01', size=2)
	filler02 = fields.Char(string='Filler02', size=10)
	address_home_id = fields.Many2one('res.partner', string='Home Address')
	person_alternate_id = fields.Char(string='Person Alternate Id', size=20)
	alternate_id_type_id = fields.Char(string='Alternate Type Id', size=3)
	equity_code = fields.Char(string='Equity Code', size=10)
	person_last_name = fields.Char(string='Surname', size=45)
	person_middle_name = fields.Char(string='Middle Name', size=50)
	person_title = fields.Selection([('adv', 'Adv.'), ('dr', 'Dr.'), ('mr', 'Mr.'), ('mrs', 'Mrs.'), ('ms', 'Ms.'), ('prof', 'Prof.')], string='Title', track_visibility='onchange')
	person_birth_date = fields.Date(string='Birth Date')
	gender = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Gender')
	marital = fields.Selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')], 'Marital Status')
	birthday = fields.Date(string='Date of Birth')
	address_home = fields.Char(string='Home Address')
	person_home_address_1 = fields.Char(string='Home Address 1', size=50)
	person_home_address_2 = fields.Char(string='Home Address 2', size=50)
	person_home_address_3 = fields.Char(string='Home Address 3', size=50)
	person_postal_address_1 = fields.Char(string='Postal Address 1', size=50)
	person_postal_address_2 = fields.Char(string='Postal Address 2', size=50)
	person_postal_address_3 = fields.Char(string='Postal Address 3', size=50)
	person_home_addr_postal_code = fields.Char(string='Home Addr Postal Code', size=4)
	person_home_addr_post_code = fields.Char(string='Home Addr Post Code', size=4)
	person_cell_phone_number = fields.Char(string='Cell Phone Number', size=10)
	person_fax_number = fields.Char(string='Fax Number', size=10)
	person_home_province_code = fields.Many2one('res.country.state' , string='Province Code')
	person_postal_province_code = fields.Many2one('res.country.state' , string='Province Code')
	provider_code = fields.Char(string='Provider Code', size=20)
	country_home = fields.Many2one('res.country', string='Country')
	country_postal = fields.Many2one('res.country', string='Country')
	person_home_city = fields.Many2one('res.city', string='Home City', track_visibility='onchange')
	person_postal_city = fields.Many2one('res.city', string='Postal City', track_visibility='onchange')
	person_home_zip = fields.Char(string='Zip')
	person_postal_zip = fields.Char(string='Zip')
	state = fields.Selection([
			('general_info', 'General Information'),
			('public_info', 'Public Information'),
			('personal_info', 'Personal Information'),
			('address_info', 'Address Information'),
			('qualification_info', 'Qualification'),
			('verification', 'Verification'),
			('evaluation', 'Evaluation'),
			('approved', 'Approved'),
			('denied', 'Rejected'),
		], string='Status', index=True, default='general_info',
		track_visibility='onchange', copy=False,
		help=" * The 'Public Information' status is used when user fills Public Information.\n"
			 " * The 'Personal Information' status is used when user fills Personal Information.\n"
			 " * The 'Address Information' status is used when user fills Address Information.\n"
			 " * The 'Pending' is used when user submit Registration Information.\n"
			 " * The 'Approved' status is used when user has been approved by Department.\n"
			 " * The 'Denied' status is used when user has been denied by Department.")
	submitted = fields.Boolean(string='Submitted')
	verify = fields.Boolean(string='Verify')
	approved = fields.Boolean(string='Approved')
	evaluate = fields.Boolean(string='Evaluate')
	denied = fields.Boolean(string='Denied')
	is_assessors = fields.Boolean(string='Assessor')
	is_moderators = fields.Boolean(string='Moderator')
	qualification_id = fields.Many2one("provider.qualification", 'Qualification', ondelete='restrict')
	assessors_moderators_ref = fields.Char(string='Reference Number', help="Reference Number", track_visibility='onchange', size=50, readonly=True)
	person_suburb = fields.Many2one('res.suburb', string='Suburb')
	person_home_suburb = fields.Many2one('res.suburb', string='Home Suburb')
	person_postal_suburb = fields.Many2one('res.suburb', string='Postal Suburb')
	person_name = fields.Char(string='Name', track_visibility='onchange', size=50)
	cont_number_home = fields.Char(string='Home Number', track_visibility='onchange', size=10)
	cont_number_office = fields.Char(string='Office Number', track_visibility='onchange', size=10)
	id_document = fields.Many2one('ir.attachment', string='ID Document')
	registrationdoc = fields.Many2one('ir.attachment', string='Qualification Documents')
	professionalbodydoc = fields.Many2one('ir.attachment', string='Professional Body')
	sram_doc = fields.Many2one('ir.attachment', string='Statement')
	id_document_bool = fields.Boolean(string='Verify')
	registrationdoc_bool = fields.Boolean(string='Verify')
	professionalbodydoc_bool = fields.Boolean(string='Verify')
	sram_doc_bool = fields.Boolean(string='Verify')
	bank_name = fields.Char(string='Bank Name')
	branch_code = fields.Char(string='Branch Code')
	same_as_home = fields.Boolean(string='Same As Home Address')
	dissability = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Dissability")
	type = fields.Selection([('permanent', 'Permanent'), ('consultant', 'Consultant')], string="Type", default='permanent')
	assessor_moderator = fields.Selection([('assessor', 'Assessor'), ('moderator', 'Moderator')], string="Assessor/Moderator", default='assessor')
	assessor_id = fields.Char(string='Assessor ID')
	qualification_ids = fields.One2many('assessors.moderators.qualification', 'assessors_moderators_qualification_id', 'Qualification Lines')
	qualification_evaluation_ids = fields.One2many('assessors.moderators.qualification.evaluation', 'assessors_moderators_qualification_evaluation_id', 'Qualification Evaluation Lines')
	assessors_moderators_status_ids = fields.One2many('assessors.moderators.status', 'assessors_moderators_status_mo_id', 'Status Line')
	comment_line = fields.Text(string="Status Comment")
	ass_mod_state = fields.Selection([
			  ('draft', 'Draft'),
			  ('submit', 'Submitted'),
		   ], string='Status', index=True, readonly=True, default='draft',
		   track_visibility='onchange', copy=False)
	organisation_sdl_no = fields.Char("Organisation SDL No")
	organisation = fields.Many2one('res.partner', string='Organisation')
	assessor_moderator_approval_date = fields.Date(string='Assessor/Moderator Approval Date')
	assessor_moderator_register_date = fields.Date(string='Assessor/Moderator Application Date')
	final_state = fields.Char(string='Status')
	reg_start = fields.Date(string='Registration Start Date')
	reg_end = fields.Date(string='Registration End Date')
	unknown_type = fields.Selection([
			  ('political_asylum', 'Political Asylum'),
			  ('refugee', 'Refugee'),
		   ], string='Type',
		   track_visibility='onchange', copy=False)
	unknown_type_document = fields.Many2one('ir.attachment', string="Type Document")
	password = fields.Char("Password")
	cv_document = fields.Many2one('ir.attachment', string="CV Document")
	cv_document_bool = fields.Boolean(string='Verify')
	related_assessor_moderator = fields.Many2one('hr.employee', string='Related Assessor Moderator')
	is_md = fields.Boolean("Id MD", compute='_get_qulification_md', store=False)

	@api.multi
	@api.onchange('work_phone','cont_number_home','cont_number_office','person_cell_phone_number')
	def onchange_validate_number(self):
		if self.already_registered == False and self.is_extension_of_scope == False and self.assessor_id == '':
			if self.person_cell_phone_number:
				if not self.person_cell_phone_number.isdigit() or len(self.person_cell_phone_number) != 10:
					self.person_cell_phone_number = ''
					return {'warning':{'title':'Invalid input','message':'Please enter 10 digits Mobile number'}}
			if self.work_phone:
				if not self.work_phone.isdigit() or len(self.work_phone) != 10:
					self.work_phone = ''
					return {'warning':{'title':'Invalid input','message':'Please enter 10 digits Work Phone number'}}
			if self.cont_number_home:
				if not self.cont_number_home.isdigit() or len(self.cont_number_home) != 10:
					self.cont_number_home = ''
					return {'warning':{'title':'Invalid input','message':'Please enter 10 digits Home number'}}
			if self.cont_number_office:
				if not self.cont_number_office.isdigit() or len(self.cont_number_office) != 10:
					self.cont_number_office = ''
					return {'warning':{'title':'Invalid input','message':'Please enter 10 digits Office number'}}
		elif self.already_registered == True or self.is_extension_of_scope == True or self.assessor_id:
			if self.person_cell_phone_number:
				if not self.person_cell_phone_number.isdigit() or len(self.person_cell_phone_number) != 10:
					self.person_cell_phone_number = ''
			if self.work_phone:
				if not self.work_phone.isdigit() or len(self.work_phone) != 10:
					self.work_phone = ''
			if self.cont_number_home:
				if not self.cont_number_home.isdigit() or len(self.cont_number_home) != 10:
					self.cont_number_home = ''
			if self.cont_number_office:
				if not self.cont_number_office.isdigit() or len(self.cont_number_office) != 10:
					self.cont_number_office = ''

	@api.onchange('work_email')
	def onchange_validate_email(self):
		if self.is_extension_of_scope == False and self.already_registered == False and self.assessor_id == '':
			if self.work_email:
				if '@' not in self.work_email:
					self.work_email = ''
					return {'warning':{'title':'Invalid input','message':'Please enter valid email address'}}
				unicode_email = self.work_email
				email = unicode_email.encode("utf-8")
				duplicate_match_user = self.env['res.users'].search(['|',('login','=',email.strip()),('login','=',self.work_email)])
				duplicate_match_ass_mod = self.env['assessors.moderators.register'].search([('final_state','!=','Rejected'),('work_email','=',email.strip())])
				if duplicate_match_user or duplicate_match_ass_mod:
					if duplicate_match_user.assessor_moderator_id or duplicate_match_ass_mod:
						self.work_email = ''
						return {'warning':{'title':'Invalid input','message':'Sorry!! Assessor/Moderator is already registered with this email Id !'}}

	@api.multi
	def onchange_already_registered(self, already_registered):
		res = {}
		if already_registered:
			res.update({'value':{'is_extension_of_scope':False}})
		return res

	@api.multi
	def onchange_is_extension_of_scope(self, is_extension_of_scope):
		res = {}
		if is_extension_of_scope:
			res.update({'value':{'already_registered':False}})
		return res

	@api.multi
	def onchange_existing_assessor_id(self, existing_assessor_id, existing_assessor_moderator, already_registered, is_extension_of_scope):
		res = {}
		if not existing_assessor_id:
			return res
		if existing_assessor_id:
			if is_extension_of_scope:
				ass_mod_obj = self.env['assessors.moderators.register'].search([('existing_assessor_moderator', '=', 'ex_assessor'),('identification_id', '=', existing_assessor_id),('is_extension_of_scope', '=', True),('approved', '=', False),('final_state','!=','Rejected')])
				if ass_mod_obj:
					return {'value': {'existing_assessor_moderator':'', 'existing_assessor_id':'', 'search_by':'', 'is_extension_of_scope': False}, 'warning':{'title':'Duplicate Entry','message':'You have already applied for assessors extension of scope.'}}
				else:
					assessor_objects = self.env['hr.employee'].search([('is_active_assessor','=',True),('assessor_moderator_identification_id', '=', existing_assessor_id)])
					if not assessor_objects:
						return {'value': {'existing_assessor_moderator':'', 'existing_assessor_id':'', 'search_by':'', 'is_extension_of_scope': False}, 'warning':{'title':'Invalid Identification Number','message':'Please Enter Correct/Active Assessor Identification Number'}}
					elif assessor_objects:
						ase_lst = []
						for ase_obj in assessor_objects:
							ase_lst.append(ase_obj.id)
						if ase_lst:
							assessor_obj = self.env['hr.employee'].search([('id', '=', max(ase_lst))])
						if assessor_obj:
							if already_registered and str(datetime.today().date()) < assessor_obj.end_date and existing_assessor_moderator == 'ex_assessor':
								return {'value': {'existing_assessor_moderator':'', 'search_by':'', 'already_registered': False, 'existing_assessor_id':''}, 'warning': {'title': 'Already Registered', 'message': "You are already registered, Your end date is %s" % (assessor_obj.end_date)}}
							q_vals_line = []
							if not already_registered:
								if assessor_obj.qualification_ids:
									for q_lines in assessor_obj.qualification_ids:
										if q_lines.qualification_status == 'approved':
											qual_master_obj = self.env['provider.qualification'].search([('id','=',q_lines.qualification_hr_id.id),('seta_branch_id','=','11')])
											if qual_master_obj:
												accreditation_qualification_line = []
												for lines in q_lines.qualification_line_hr:
													for data in lines:
														val = {
															 'name':data.name,
															 'type':data.type,
															 'id_no':data.id_no,
															 'title':data.title,
															 'level1':data.level1,
															 'level2':data.level2,
															 'level3': data.level3,
															 'selection':data.selection,
															}
														accreditation_qualification_line.append((0, 0, val))

												q_vals = {
															'qual_unit_type': q_lines.qual_unit_type,
															'qualification_id':qual_master_obj.id,
															'saqa_qual_id':qual_master_obj.saqa_qual_id,
															'minimum_credits':qual_master_obj.m_credits,
															'qualification_line':accreditation_qualification_line,
															}
												q_vals_line.append((0, 0, q_vals))
							vals = {
									'name':assessor_obj.name,
									'work_email':assessor_obj.work_email,
									'work_phone':assessor_obj.work_phone,
									'person_cell_phone_number':assessor_obj.person_cell_phone_number,
									'work_address':assessor_obj.work_address,
									'work_address2':assessor_obj.work_address2,
									'work_address3':assessor_obj.work_address3,
									'person_suburb':assessor_obj.person_suburb.id,
									'work_municipality':assessor_obj.work_municipality.id,
									'work_city':assessor_obj.work_city.id,
									'work_province':assessor_obj.work_province.id,
									'work_zip':assessor_obj.work_zip,
									'work_country':assessor_obj.work_country.id,
									'organisation':assessor_obj.organisation.id,
									'organisation_sdl_no':assessor_obj.organisation_sdl_no,
									'department':assessor_obj.department,
									'job_title':assessor_obj.job_title,
									'manager':assessor_obj.manager,
									'notes':assessor_obj.notes,
									'person_title':assessor_obj.person_title,
									'person_name':assessor_obj.person_name,
									'person_last_name':assessor_obj.person_last_name,
									'initials':assessor_obj.initials,
									'cont_number_home':assessor_obj.cont_number_home,
									'cont_number_office':assessor_obj.cont_number_office,
									'citizen_resident_status_code':assessor_obj.citizen_resident_status_code,
									'country_id':assessor_obj.country_id.id,
									'unknown_type':assessor_obj.unknown_type,
									'unknown_type_document':assessor_obj.unknown_type_document,
									'identification_id':assessor_obj.assessor_moderator_identification_id,
									'alternate_id_type':assessor_obj.alternate_id_type,
									'person_birth_date':assessor_obj.person_birth_date,
									'passport_id':assessor_obj.passport_id,
									'national_id':assessor_obj.national_id,
									'id_document':assessor_obj.id_document.id,
									'home_language_code':assessor_obj.home_language_code.id,
									'certificate_no':assessor_obj.certificate_no,
									'record_last_update':assessor_obj.record_last_update,
									'gender':assessor_obj.gender,
									'marital':assessor_obj.marital,
									'dissability':assessor_obj.dissability,
									'person_home_address_1':assessor_obj.person_home_address_1,
									'person_home_address_2':assessor_obj.person_home_address_2,
									'person_home_address_3':assessor_obj.person_home_address_3,
									'person_home_suburb':assessor_obj.person_home_suburb.id,
									'physical_municipality':assessor_obj.physical_municipality.id,
									'person_home_city':assessor_obj.person_home_city.id,
									'person_home_province_code':assessor_obj.person_home_province_code.id,
									'person_home_zip':assessor_obj.person_home_zip,
									'country_home':assessor_obj.country_home.id,
									'same_as_home':assessor_obj.same_as_home,
									'person_postal_address_1':assessor_obj.person_postal_address_1,
									'person_postal_address_2':assessor_obj.person_postal_address_2,
									'person_postal_address_3':assessor_obj.person_postal_address_3,
									'person_postal_suburb':assessor_obj.person_postal_suburb.id,
									'postal_municipality':assessor_obj.postal_municipality.id,
									'person_postal_city':assessor_obj.person_postal_city.id,
									'person_postal_province_code':assessor_obj.person_postal_province_code.id,
									'person_postal_zip':assessor_obj.person_postal_zip,
									'country_postal':assessor_obj.country_postal.id,
									'professionalbodydoc':assessor_obj.professionalbodydoc.id,
									'sram_doc':assessor_obj.sram_doc.id,
									'cv_document':assessor_obj.cv_document.id,
									'registrationdoc':assessor_obj.registrationdoc.id,
									'qualification_ids':q_vals_line,
								  }
				if existing_assessor_moderator == 'ex_assessor':
						res.update({'value':vals})
			elif already_registered:
				ass_mod_obj = self.env['assessors.moderators.register'].search([('existing_assessor_moderator', '=', 'ex_assessor'),('identification_id', '=', existing_assessor_id),('already_registered', '=', True),('approved', '=', False),('final_state','!=','Rejected')])
				if ass_mod_obj:
					return {'value': {'existing_assessor_moderator':'', 'already_registered': False, 'existing_assessor_id':'', 'search_by':''}, 'warning':{'title':'Duplicate Entry','message':'You have already applied for re-registration.'}}
				assessor_objects = self.env['hr.employee'].search([('assessor_moderator_identification_id', '=', existing_assessor_id)])
				if not assessor_objects:
					return {'value': {'existing_assessor_moderator':'', 'already_registered': False, 'existing_assessor_id':'', 'search_by':''}, 'warning':{'title':'Invalid Identification Number','message':'Please Enter Correct Assessor Identification Number'}}
				elif assessor_objects:
					ase_lst = []
					q_vals_line = []
					for ase_obj in assessor_objects:
						ase_lst.append(ase_obj.id)
					if ase_lst:
						assessor_obj = self.env['hr.employee'].search([('id', '=', max(ase_lst))])
					if assessor_obj:
						if already_registered and str(datetime.today().date()) < assessor_obj.end_date and existing_assessor_moderator == 'ex_assessor':
							return {'value': {'existing_assessor_moderator':'', 'search_by':'', 'already_registered': False, 'existing_assessor_id':''}, 'warning': {'title': 'Already Registered', 'message': "You are already registered, Your end date is %s" % (assessor_obj.end_date)}}
						if already_registered:
							if assessor_obj.qualification_ids:
								for q_lines in assessor_obj.qualification_ids:
									if q_lines.qualification_status == 'approved':
										qual_master_obj = self.env['provider.qualification'].search([('id','=',q_lines.qualification_hr_id.id),('seta_branch_id','=','11')])
										if qual_master_obj:
											accreditation_qualification_line = []
											for lines in q_lines.qualification_line_hr:
												for data in lines:
													val = {
														 'name':data.name,
														 'type':data.type,
														 'id_no':data.id_no,
														 'title':data.title,
														 'level1':data.level1,
														 'level2':data.level2,
														 'level3': data.level3,
														 'selection':data.selection,
														}
													accreditation_qualification_line.append((0, 0, val))
											q_vals = {
														'qual_unit_type': q_lines.qual_unit_type,
														'qualification_id':qual_master_obj.id,
														'saqa_qual_id':qual_master_obj.saqa_qual_id,
														'minimum_credits':qual_master_obj.m_credits,
														'qualification_line':accreditation_qualification_line,
														}
											q_vals_line.append((0, 0, q_vals))
						vals = {
								'name':assessor_obj.name,
								'work_email':assessor_obj.work_email,
								'work_phone':assessor_obj.work_phone,
								'person_cell_phone_number':assessor_obj.person_cell_phone_number,
								'work_address':assessor_obj.work_address,
								'work_address2':assessor_obj.work_address2,
								'work_address3':assessor_obj.work_address3,
								'person_suburb':assessor_obj.person_suburb.id,
								'work_municipality':assessor_obj.work_municipality.id,
								'work_city':assessor_obj.work_city.id,
								'work_province':assessor_obj.work_province.id,
								'work_zip':assessor_obj.work_zip,
								'work_country':assessor_obj.work_country.id,
								'organisation':assessor_obj.organisation.id,
								'organisation_sdl_no':assessor_obj.organisation_sdl_no,
								'department':assessor_obj.department,
								'job_title':assessor_obj.job_title,
								'manager':assessor_obj.manager,
								'notes':assessor_obj.notes,
								'person_title':assessor_obj.person_title,
								'person_name':assessor_obj.person_name,
								'person_last_name':assessor_obj.person_last_name,
								'initials':assessor_obj.initials,
								'cont_number_home':assessor_obj.cont_number_home,
								'cont_number_office':assessor_obj.cont_number_office,
								'citizen_resident_status_code':assessor_obj.citizen_resident_status_code,
								'country_id':assessor_obj.country_id.id,
								'unknown_type':assessor_obj.unknown_type,
								'unknown_type_document':assessor_obj.unknown_type_document,
								'identification_id':assessor_obj.assessor_moderator_identification_id,
								'alternate_id_type':assessor_obj.alternate_id_type,
								'person_birth_date':assessor_obj.person_birth_date,
								'passport_id':assessor_obj.passport_id,
								'national_id':assessor_obj.national_id,
								'id_document':assessor_obj.id_document.id,
								'home_language_code':assessor_obj.home_language_code.id,
								'certificate_no':assessor_obj.certificate_no,
								'record_last_update':assessor_obj.record_last_update,
								'gender':assessor_obj.gender,
								'marital':assessor_obj.marital,
								'dissability':assessor_obj.dissability,
								'person_home_address_1':assessor_obj.person_home_address_1,
								'person_home_address_2':assessor_obj.person_home_address_2,
								'person_home_address_3':assessor_obj.person_home_address_3,
								'person_home_suburb':assessor_obj.person_home_suburb.id,
								'physical_municipality':assessor_obj.physical_municipality.id,
								'person_home_city':assessor_obj.person_home_city.id,
								'person_home_province_code':assessor_obj.person_home_province_code.id,
								'person_home_zip':assessor_obj.person_home_zip,
								'country_home':assessor_obj.country_home.id,
								'same_as_home':assessor_obj.same_as_home,
								'person_postal_address_1':assessor_obj.person_postal_address_1,
								'person_postal_address_2':assessor_obj.person_postal_address_2,
								'person_postal_address_3':assessor_obj.person_postal_address_3,
								'person_postal_suburb':assessor_obj.person_postal_suburb.id,
								'postal_municipality':assessor_obj.postal_municipality.id,
								'person_postal_city':assessor_obj.person_postal_city.id,
								'person_postal_province_code':assessor_obj.person_postal_province_code.id,
								'person_postal_zip':assessor_obj.person_postal_zip,
								'country_postal':assessor_obj.country_postal.id,
								'professionalbodydoc':assessor_obj.professionalbodydoc.id,
								'sram_doc':assessor_obj.sram_doc.id,
								'cv_document':assessor_obj.cv_document.id,
								'registrationdoc':assessor_obj.registrationdoc.id,
								'qualification_ids': q_vals_line,
							  }
					if existing_assessor_moderator == 'ex_assessor':
						res.update({'value':vals})
		return res

	@api.multi
	def onchange_existing_assessor_number(self, existing_assessor_number, existing_assessor_moderator, already_registered, is_extension_of_scope):
		res = {}
		if not existing_assessor_number:
			return res
		if existing_assessor_number:
			if is_extension_of_scope:
				ass_mod_obj = self.env['assessors.moderators.register'].search([('existing_assessor_moderator', '=', 'ex_assessor'),('existing_assessor_number', '=', existing_assessor_number),('is_extension_of_scope', '=', True),('approved', '=', False),('final_state','!=','Rejected')])
				if ass_mod_obj:
					return {'value':{'existing_assessor_moderator':'', 'existing_assessor_number':'', 'search_by':'', 'is_extension_of_scope': False}, 'warning':{'title':'Duplicate Entry','message':'You have already applied for assessors extension of scope.'}}
				else:
					assessor_objects = self.env['hr.employee'].search([('is_active_assessor','=',True),('assessor_seq_no', '=', existing_assessor_number)])
					if not assessor_objects:
						return {'value':{'existing_assessor_moderator':'', 'existing_assessor_number':'', 'search_by':'', 'is_extension_of_scope': False}, 'warning':{'title':'Invalid Assessor Number','message':'Please Enter Correct/Active Assessor Number'}}
					elif assessor_objects:
						ase_lst = []
						for ase_obj in assessor_objects:
							ase_lst.append(ase_obj.id)
						assessor_obj = self.env['hr.employee'].search([('id', '=', max(ase_lst))])
						if already_registered and str(datetime.today().date()) < assessor_obj.end_date and existing_assessor_moderator == 'ex_assessor':
							return {'value': {'existing_assessor_moderator':'', 'search_by':'', 'already_registered': False, 'existing_assessor_number':''}, 'warning': {'title': 'Already Registered', 'message': "You are already registered, Your end date is %s" % (assessor_obj.end_date)}}
						q_vals_line = []
						if not already_registered:
							if assessor_obj.qualification_ids:
								for q_lines in assessor_obj.qualification_ids:
									if q_lines.qualification_status == 'approved':
										qual_master_obj = self.env['provider.qualification'].search([('id','=',q_lines.qualification_hr_id.id),('seta_branch_id','=','11')])
										if qual_master_obj:
											accreditation_qualification_line = []
											for lines in q_lines.qualification_line_hr:
												for data in lines:
													val = {
														 'name':data.name,
														 'type':data.type,
														 'id_no':data.id_no,
														 'title':data.title,
														 'level1':data.level1,
														 'level2':data.level2,
														 'level3': data.level3,
														 'selection':data.selection,
														}
													accreditation_qualification_line.append((0, 0, val))
											q_vals = {
														'qual_unit_type': q_lines.qual_unit_type,
														'qualification_id':qual_master_obj.id,
														'saqa_qual_id':qual_master_obj.saqa_qual_id,
														'minimum_credits':qual_master_obj.m_credits,
														'qualification_line':accreditation_qualification_line,
														}
											q_vals_line.append((0, 0, q_vals))

						vals = {
								'name':assessor_obj.name,
								'work_email':assessor_obj.work_email,
								'work_phone':assessor_obj.work_phone,
								'person_cell_phone_number':assessor_obj.person_cell_phone_number,
								'work_address':assessor_obj.work_address,
								'work_address2':assessor_obj.work_address2,
								'work_address3':assessor_obj.work_address3,
								'person_suburb':assessor_obj.person_suburb.id,
								'work_municipality':assessor_obj.work_municipality.id,
								'work_city':assessor_obj.work_city.id,
								'work_province':assessor_obj.work_province.id,
								'work_zip':assessor_obj.work_zip,
								'work_country':assessor_obj.work_country.id,
								'organisation':assessor_obj.organisation.id,
								'organisation_sdl_no':assessor_obj.organisation_sdl_no,
								'department':assessor_obj.department,
								'job_title':assessor_obj.job_title,
								'manager':assessor_obj.manager,
								'notes':assessor_obj.notes,
								'person_title':assessor_obj.person_title,
								'person_name':assessor_obj.person_name,
								'person_last_name':assessor_obj.person_last_name,
								'initials':assessor_obj.initials,
								'cont_number_home':assessor_obj.cont_number_home,
								'cont_number_office':assessor_obj.cont_number_office,
								'citizen_resident_status_code':assessor_obj.citizen_resident_status_code,
								'country_id':assessor_obj.country_id.id,
								'unknown_type':assessor_obj.unknown_type,
								'unknown_type_document':assessor_obj.unknown_type_document,
								'identification_id':assessor_obj.assessor_moderator_identification_id,
								'alternate_id_type':assessor_obj.alternate_id_type,
								'person_birth_date':assessor_obj.person_birth_date,
								'passport_id':assessor_obj.passport_id,
								'national_id':assessor_obj.national_id,
								'id_document':assessor_obj.id_document.id,
								'home_language_code':assessor_obj.home_language_code.id,
								'certificate_no':assessor_obj.certificate_no,
								'record_last_update':assessor_obj.record_last_update,
								'gender':assessor_obj.gender,
								'marital':assessor_obj.marital,
								'dissability':assessor_obj.dissability,
								'person_home_address_1':assessor_obj.person_home_address_1,
								'person_home_address_2':assessor_obj.person_home_address_2,
								'person_home_address_3':assessor_obj.person_home_address_3,
								'person_home_suburb':assessor_obj.person_home_suburb.id,
								'physical_municipality':assessor_obj.physical_municipality.id,
								'person_home_city':assessor_obj.person_home_city.id,
								'person_home_province_code':assessor_obj.person_home_province_code.id,
								'person_home_zip':assessor_obj.person_home_zip,
								'country_home':assessor_obj.country_home.id,
								'same_as_home':assessor_obj.same_as_home,
								'person_postal_address_1':assessor_obj.person_postal_address_1,
								'person_postal_address_2':assessor_obj.person_postal_address_2,
								'person_postal_address_3':assessor_obj.person_postal_address_3,
								'person_postal_suburb':assessor_obj.person_postal_suburb.id,
								'postal_municipality':assessor_obj.postal_municipality.id,
								'person_postal_city':assessor_obj.person_postal_city.id,
								'person_postal_province_code':assessor_obj.person_postal_province_code.id,
								'person_postal_zip':assessor_obj.person_postal_zip,
								'country_postal':assessor_obj.country_postal.id,
								'professionalbodydoc':assessor_obj.professionalbodydoc.id,
								'sram_doc':assessor_obj.sram_doc.id,
								'cv_document':assessor_obj.cv_document.id,
								'registrationdoc':assessor_obj.registrationdoc.id,
								# Below line is commented because we don't need to fetch master qualifications at the time of extension of scope
								'qualification_ids':q_vals_line,
							  }
				if existing_assessor_moderator == 'ex_assessor':
					res.update({'value':vals})
			elif already_registered:
				ass_mod_obj = self.env['assessors.moderators.register'].search([('existing_assessor_moderator', '=', 'ex_assessor'),('existing_assessor_number', '=', existing_assessor_number),('already_registered', '=', True),('approved', '=', False),('final_state','!=','Rejected')])
				if ass_mod_obj:
					return {'value':{'existing_assessor_moderator':'', 'already_registered': False, 'search_by':'', 'existing_assessor_number':''}, 'warning':{'title':'Duplicate Entry','message':'You have already applied for re-registration.'}}
				assessor_objects = self.env['hr.employee'].search([('assessor_seq_no', '=', existing_assessor_number)])
				if not assessor_objects:
					return {'value':{'existing_assessor_moderator':'', 'already_registered': False, 'search_by':'', 'existing_assessor_number':''}, 'warning':{'title':'Invalid Assessor Number','message':'Please Enter Correct Assessor Number'}}
				elif assessor_objects:
					ase_lst = []
					for ase_obj in assessor_objects:
						ase_lst.append(ase_obj.id)
					assessor_obj = self.env['hr.employee'].search([('id', '=', max(ase_lst))])
					if already_registered and str(datetime.today().date()) < assessor_obj.end_date and existing_assessor_moderator == 'ex_assessor':
						return {'value': {'existing_assessor_moderator':'', 'search_by':'', 'already_registered': False, 'existing_assessor_number':''}, 'warning': {'title': 'Already Registered', 'message': "You are already registered, Your end date is %s" % (assessor_obj.end_date)}}
					q_vals_line = []
					if already_registered:
						if assessor_obj.qualification_ids:
							for q_lines in assessor_obj.qualification_ids:
								if q_lines.qualification_status == 'approved':
										qual_master_obj = self.env['provider.qualification'].search([('id','=',q_lines.qualification_hr_id.id),('seta_branch_id','=','11')])
										if qual_master_obj:
											accreditation_qualification_line = []
											for lines in q_lines.qualification_line_hr:
												for data in lines:
													val = {
														 'name':data.name,
														 'type':data.type,
														 'id_no':data.id_no,
														 'title':data.title,
														 'level1':data.level1,
														 'level2':data.level2,
														 'level3': data.level3,
														 'selection':data.selection,
														}
													accreditation_qualification_line.append((0, 0, val))
											q_vals = {
														'qual_unit_type': q_lines.qual_unit_type,
														'qualification_id':qual_master_obj.id,
														'saqa_qual_id':qual_master_obj.saqa_qual_id,
														'minimum_credits':qual_master_obj.m_credits,
														'qualification_line':accreditation_qualification_line,
														}
											q_vals_line.append((0, 0, q_vals))
					vals = {
							'name':assessor_obj.name,
							'work_email':assessor_obj.work_email,
							'work_phone':assessor_obj.work_phone,
							'person_cell_phone_number':assessor_obj.person_cell_phone_number,
							'work_address':assessor_obj.work_address,
							'work_address2':assessor_obj.work_address2,
							'work_address3':assessor_obj.work_address3,
							'person_suburb':assessor_obj.person_suburb.id,
							'work_municipality':assessor_obj.work_municipality.id,
							'work_city':assessor_obj.work_city.id,
							'work_province':assessor_obj.work_province.id,
							'work_zip':assessor_obj.work_zip,
							'work_country':assessor_obj.work_country.id,
							'organisation':assessor_obj.organisation.id,
							'organisation_sdl_no':assessor_obj.organisation_sdl_no,
							'department':assessor_obj.department,
							'job_title':assessor_obj.job_title,
							'manager':assessor_obj.manager,
							'notes':assessor_obj.notes,
							'person_title':assessor_obj.person_title,
							'person_name':assessor_obj.person_name,
							'person_last_name':assessor_obj.person_last_name,
							'initials':assessor_obj.initials,
							'cont_number_home':assessor_obj.cont_number_home,
							'cont_number_office':assessor_obj.cont_number_office,
							'citizen_resident_status_code':assessor_obj.citizen_resident_status_code,
							'country_id':assessor_obj.country_id.id,
							'unknown_type':assessor_obj.unknown_type,
							'unknown_type_document':assessor_obj.unknown_type_document,
							'identification_id':assessor_obj.assessor_moderator_identification_id,
							'alternate_id_type':assessor_obj.alternate_id_type,
							'person_birth_date':assessor_obj.person_birth_date,
							'passport_id':assessor_obj.passport_id,
							'national_id':assessor_obj.national_id,
							'id_document':assessor_obj.id_document.id,
							'home_language_code':assessor_obj.home_language_code.id,
							'certificate_no':assessor_obj.certificate_no,
							'record_last_update':assessor_obj.record_last_update,
							'gender':assessor_obj.gender,
							'marital':assessor_obj.marital,
							'dissability':assessor_obj.dissability,
							'person_home_address_1':assessor_obj.person_home_address_1,
							'person_home_address_2':assessor_obj.person_home_address_2,
							'person_home_address_3':assessor_obj.person_home_address_3,
							'person_home_suburb':assessor_obj.person_home_suburb.id,
							'physical_municipality':assessor_obj.physical_municipality.id,
							'person_home_city':assessor_obj.person_home_city.id,
							'person_home_province_code':assessor_obj.person_home_province_code.id,
							'person_home_zip':assessor_obj.person_home_zip,
							'country_home':assessor_obj.country_home.id,
							'same_as_home':assessor_obj.same_as_home,
							'person_postal_address_1':assessor_obj.person_postal_address_1,
							'person_postal_address_2':assessor_obj.person_postal_address_2,
							'person_postal_address_3':assessor_obj.person_postal_address_3,
							'person_postal_suburb':assessor_obj.person_postal_suburb.id,
							'postal_municipality':assessor_obj.postal_municipality.id,
							'person_postal_city':assessor_obj.person_postal_city.id,
							'person_postal_province_code':assessor_obj.person_postal_province_code.id,
							'person_postal_zip':assessor_obj.person_postal_zip,
							'country_postal':assessor_obj.country_postal.id,
							'professionalbodydoc':assessor_obj.professionalbodydoc.id,
							'sram_doc':assessor_obj.sram_doc.id,
							'cv_document':assessor_obj.cv_document.id,
							'registrationdoc':assessor_obj.registrationdoc.id,
							'qualification_ids':q_vals_line,
						  }
					if existing_assessor_moderator == 'ex_assessor':
						res.update({'value':vals})
		return res

	@api.multi
	def onchange_existing_moderator_id(self, existing_moderator_id, existing_assessor_id, already_registered,is_extension_of_scope):
		res = {}
		if not existing_moderator_id:
			return res
		if existing_moderator_id:
			if is_extension_of_scope:
				ass_mod_obj = self.env['assessors.moderators.register'].search([('existing_assessor_moderator', '=', 'ex_moderator'),('identification_id', '=', existing_moderator_id),('is_extension_of_scope', '=', True),('approved', '=', False),('final_state','!=','Rejected')])
				if ass_mod_obj:
					return {'value': {'existing_moderator_id':'', 'search_by':'', 'existing_assessor_moderator':'', 'is_extension_of_scope': False}, 'warning':{'title':'Duplicate Entry','message':'You have already applied for moderators extension of scope.'}}
				else:
					moderator_obj = self.env['hr.employee'].search([('is_active_moderator','=',True),('is_moderators','=',True),('assessor_moderator_identification_id', '=', existing_moderator_id)])
					if not moderator_obj:
						return {'value': {'existing_moderator_id':'', 'search_by':'', 'existing_assessor_moderator':'', 'is_extension_of_scope': False}, 'warning':{'title':'Invalid Identification Number','message':'Please Enter Correct/Active Moderator Identification Number'}}
					elif moderator_obj:
						if already_registered and str(datetime.today().date()) < moderator_obj.moderator_end_date:
							return {'value': {'existing_assessor_moderator':'', 'search_by':'', 'already_registered': False, 'existing_moderator_id':''}, 'warning': {'title': 'Already Registered', 'message': "You are already registered, Your end date is %s" % (moderator_obj.moderator_end_date)}}
						q_vals_line = []
						if not already_registered:
							if moderator_obj.moderator_qualification_ids:
								for q_lines in moderator_obj.moderator_qualification_ids:
									if q_lines.qualification_status == 'approved':
										qual_master_obj = self.env['provider.qualification'].search([('id','=',q_lines.qualification_hr_id.id),('seta_branch_id','=','11')])
										if qual_master_obj:
											accreditation_qualification_line = []
											for lines in q_lines.qualification_line_hr:
												for data in lines:
													val = {
														 'name':data.name,
														 'type':data.type,
														 'id_no':data.id_no,
														 'title':data.title,
														 'level1':data.level1,
														 'level2':data.level2,
														 'level3': data.level3,
														 'selection':data.selection,
														}
													accreditation_qualification_line.append((0, 0, val))
											q_vals = {
														'qual_unit_type': q_lines.qual_unit_type,
														'qualification_id':qual_master_obj.id,
														'saqa_qual_id':qual_master_obj.saqa_qual_id,
														'minimum_credits':qual_master_obj.m_credits,
														'qualification_line':accreditation_qualification_line,
														}
											q_vals_line.append((0, 0, q_vals))

						vals = {
								'name':moderator_obj.name,
								'work_email':moderator_obj.work_email,
								'work_phone':moderator_obj.work_phone,
								'work_address':moderator_obj.work_address,
								'person_cell_phone_number':moderator_obj.person_cell_phone_number,
								'work_address2':moderator_obj.work_address2,
								'work_address3':moderator_obj.work_address3,
								'person_suburb':moderator_obj.person_suburb.id,
								'work_municipality':moderator_obj.work_municipality.id,
								'work_city':moderator_obj.work_city.id,
								'work_province':moderator_obj.work_province.id,
								'work_zip':moderator_obj.work_zip,
								'work_country':moderator_obj.work_country.id,
								'organisation':moderator_obj.organisation.id,
								'organisation_sdl_no':moderator_obj.organisation_sdl_no,
								'department':moderator_obj.department,
								'job_title':moderator_obj.job_title,
								'manager':moderator_obj.manager,
								'notes':moderator_obj.notes,
								'person_title':moderator_obj.person_title,
								'person_name':moderator_obj.person_name,
								'person_last_name':moderator_obj.person_last_name,
								'initials':moderator_obj.initials,
								'cont_number_home':moderator_obj.cont_number_home,
								'cont_number_office':moderator_obj.cont_number_office,
								'citizen_resident_status_code':moderator_obj.citizen_resident_status_code,
								'country_id':moderator_obj.country_id.id,
								'unknown_type':moderator_obj.unknown_type,
								'unknown_type_document':moderator_obj.unknown_type_document,
								'identification_id':moderator_obj.assessor_moderator_identification_id,
								'alternate_id_type':moderator_obj.alternate_id_type,
								'person_birth_date':moderator_obj.person_birth_date,
								'passport_id':moderator_obj.passport_id,
								'national_id':moderator_obj.national_id,
								'id_document':moderator_obj.id_document.id,
								'home_language_code':moderator_obj.home_language_code.id,
								'certificate_no':moderator_obj.certificate_no,
								'record_last_update':moderator_obj.record_last_update,
								'gender':moderator_obj.gender,
								'marital':moderator_obj.marital,
								'dissability':moderator_obj.dissability,
								'person_home_address_1':moderator_obj.person_home_address_1,
								'person_home_address_2':moderator_obj.person_home_address_2,
								'person_home_address_3':moderator_obj.person_home_address_3,
								'person_home_suburb':moderator_obj.person_home_suburb.id,
								'physical_municipality':moderator_obj.physical_municipality.id,
								'person_home_city':moderator_obj.person_home_city.id,
								'person_home_province_code':moderator_obj.person_home_province_code.id,
								'person_home_zip':moderator_obj.person_home_zip,
								'country_home':moderator_obj.country_home.id,
								'same_as_home':moderator_obj.same_as_home,
								'person_postal_address_1':moderator_obj.person_postal_address_1,
								'person_postal_address_2':moderator_obj.person_postal_address_2,
								'person_postal_address_3':moderator_obj.person_postal_address_3,
								'person_postal_suburb':moderator_obj.person_postal_suburb.id,
								'postal_municipality':moderator_obj.postal_municipality.id,
								'person_postal_city':moderator_obj.person_postal_city.id,
								'person_postal_province_code':moderator_obj.person_postal_province_code.id,
								'person_postal_zip':moderator_obj.person_postal_zip,
								'country_postal':moderator_obj.country_postal.id,
								'professionalbodydoc':moderator_obj.professionalbodydoc.id,
								'sram_doc':moderator_obj.sram_doc.id,
								'cv_document':moderator_obj.cv_document.id,
								'registrationdoc':moderator_obj.registrationdoc.id,
								# Below line is commented because we don't need to fetch master qualifications at the time of extension of scope
								'qualification_ids':q_vals_line,
							  }
						res.update({'value':vals})
					if existing_assessor_id:
						if existing_assessor_id != existing_moderator_id:
							raise Warning(_("Sorry! existing Assessor id and existing Moderator id should be same"))
#                     else:
#                         raise Warning(_("Please enter Assessor Identification number"))
			if already_registered:
				ass_mod_obj = self.env['assessors.moderators.register'].search([('existing_assessor_moderator', '=', 'ex_moderator'),('identification_id', '=', existing_moderator_id),('already_registered', '=', True),('approved', '=', False),('final_state','!=','Rejected')])
				if ass_mod_obj:
					return {'value':{'existing_assessor_moderator':'', 'search_by':'', 'already_registered': False, 'existing_moderator_id':''},'warning':{'title':'Duplicate Entry','message':'You have already applied for re-registration.'}}
				moderator_obj = self.env['hr.employee'].search([('assessor_moderator_identification_id', '=', existing_moderator_id)])
				if moderator_obj:
					mod_lst = []
					for obj in moderator_obj:
						mod_lst.append(obj.id)
					if mod_lst:
						moderator_obj = self.env['hr.employee'].search([('id', '=', max(mod_lst))])
				if not moderator_obj:
						return {'value':{'existing_assessor_moderator':'','already_registered': False, 'search_by':'', 'existing_moderator_id':''}, 'warning':{'title':'Invalid Identification Number','message':'Please Enter Correct Moderator Identification Number'}}
				elif moderator_obj:
					if already_registered and str(datetime.today().date()) < moderator_obj.moderator_end_date:
						return {'value': {'existing_assessor_moderator':'', 'search_by':'', 'already_registered': False, 'existing_moderator_id':''}, 'warning': {'title': 'Already Registered', 'message': "You are already registered, Your end date is %s" % (moderator_obj.moderator_end_date)}}
					q_vals_line = []
					if already_registered:
						if moderator_obj.moderator_qualification_ids:
							for q_lines in moderator_obj.moderator_qualification_ids:
								if q_lines.qualification_status == 'approved':
										qual_master_obj = self.env['provider.qualification'].search([('id','=',q_lines.qualification_hr_id.id),('seta_branch_id','=','11')])
										if qual_master_obj:
											accreditation_qualification_line = []
											for lines in q_lines.qualification_line_hr:
												for data in lines:
													val = {
														 'name':data.name,
														 'type':data.type,
														 'id_no':data.id_no,
														 'title':data.title,
														 'level1':data.level1,
														 'level2':data.level2,
														 'level3': data.level3,
														 'selection':data.selection,
														}
													accreditation_qualification_line.append((0, 0, val))
											q_vals = {
														'qual_unit_type': q_lines.qual_unit_type,
														'qualification_id':qual_master_obj.id,
														'saqa_qual_id':qual_master_obj.saqa_qual_id,
														'minimum_credits':qual_master_obj.m_credits,
														'qualification_line':accreditation_qualification_line,
														}
											q_vals_line.append((0, 0, q_vals))

					vals = {
							'name':moderator_obj.name,
							'work_email':moderator_obj.work_email,
							'work_phone':moderator_obj.work_phone,
							'work_address':moderator_obj.work_address,
							'person_cell_phone_number':moderator_obj.person_cell_phone_number,
							'work_address2':moderator_obj.work_address2,
							'work_address3':moderator_obj.work_address3,
							'person_suburb':moderator_obj.person_suburb.id,
							'work_municipality':moderator_obj.work_municipality.id,
							'work_city':moderator_obj.work_city.id,
							'work_province':moderator_obj.work_province.id,
							'work_zip':moderator_obj.work_zip,
							'work_country':moderator_obj.work_country.id,
							'organisation':moderator_obj.organisation.id,
							'organisation_sdl_no':moderator_obj.organisation_sdl_no,
							'department':moderator_obj.department,
							'job_title':moderator_obj.job_title,
							'manager':moderator_obj.manager,
							'notes':moderator_obj.notes,
							'person_title':moderator_obj.person_title,
							'person_name':moderator_obj.person_name,
							'person_last_name':moderator_obj.person_last_name,
							'initials':moderator_obj.initials,
							'cont_number_home':moderator_obj.cont_number_home,
							'cont_number_office':moderator_obj.cont_number_office,
							'citizen_resident_status_code':moderator_obj.citizen_resident_status_code,
							'country_id':moderator_obj.country_id.id,
							'unknown_type':moderator_obj.unknown_type,
							'unknown_type_document':moderator_obj.unknown_type_document,
							'identification_id':moderator_obj.assessor_moderator_identification_id,
							'alternate_id_type':moderator_obj.alternate_id_type,
							'person_birth_date':moderator_obj.person_birth_date,
							'passport_id':moderator_obj.passport_id,
							'national_id':moderator_obj.national_id,
							'id_document':moderator_obj.id_document.id,
							'home_language_code':moderator_obj.home_language_code.id,
							'certificate_no':moderator_obj.certificate_no,
							'record_last_update':moderator_obj.record_last_update,
							'gender':moderator_obj.gender,
							'marital':moderator_obj.marital,
							'dissability':moderator_obj.dissability,
							'person_home_address_1':moderator_obj.person_home_address_1,
							'person_home_address_2':moderator_obj.person_home_address_2,
							'person_home_address_3':moderator_obj.person_home_address_3,
							'person_home_suburb':moderator_obj.person_home_suburb.id,
							'physical_municipality':moderator_obj.physical_municipality.id,
							'person_home_city':moderator_obj.person_home_city.id,
							'person_home_province_code':moderator_obj.person_home_province_code.id,
							'person_home_zip':moderator_obj.person_home_zip,
							'country_home':moderator_obj.country_home.id,
							'same_as_home':moderator_obj.same_as_home,
							'person_postal_address_1':moderator_obj.person_postal_address_1,
							'person_postal_address_2':moderator_obj.person_postal_address_2,
							'person_postal_address_3':moderator_obj.person_postal_address_3,
							'person_postal_suburb':moderator_obj.person_postal_suburb.id,
							'postal_municipality':moderator_obj.postal_municipality.id,
							'person_postal_city':moderator_obj.person_postal_city.id,
							'person_postal_province_code':moderator_obj.person_postal_province_code.id,
							'person_postal_zip':moderator_obj.person_postal_zip,
							'country_postal':moderator_obj.country_postal.id,
							'professionalbodydoc':moderator_obj.professionalbodydoc.id,
							'sram_doc':moderator_obj.sram_doc.id,
							'cv_document':moderator_obj.cv_document.id,
							'registrationdoc':moderator_obj.registrationdoc.id,
							'qualification_ids':q_vals_line,
						  }
					res.update({'value':vals})
				if existing_assessor_id:
					if existing_assessor_id != existing_moderator_id:
						raise Warning(_("Sorry! existing Assessor id and existing Moderator id should be same"))
#                 else:
#                     raise Warning(_("Please enter Assessor Identification number"))
		return res


	@api.multi
	def onchange_existing_moderator_number(self, existing_moderator_number, existing_assessor_number, already_registered, is_extension_of_scope):
		res = {}
		if not existing_moderator_number:
			return res
		if existing_moderator_number:
			if is_extension_of_scope:
				ass_mod_obj = self.env['assessors.moderators.register'].search([('existing_assessor_moderator', '=', 'ex_moderator'),('existing_moderator_number', '=', existing_moderator_number),('is_extension_of_scope', '=', True),('approved', '=', False),('final_state','!=','Rejected')])
				if ass_mod_obj:
					return {'value':{'existing_moderator_number':'', 'search_by':'', 'existing_assessor_number':'','is_extension_of_scope': False}, 'warning':{'title':'Duplicate Entry','message':'You have already applied for moderators extension of scope.'}}
				else:
					self._cr.execute("select id from hr_employee where moderator_seq_no = '%s'" % (existing_moderator_number,))
					mod_id = self._cr.fetchone()
					moderator_obj = self.env['hr.employee']
					if mod_id:
						moderator_obj = self.env['hr.employee'].browse(mod_id[0])
					if existing_assessor_number:
						assessor_ob = self.env['hr.employee'].search([('is_active_assessor','=',True),('assessor_seq_no', '=', existing_assessor_number)])
						if not assessor_ob:
							return {'value':{'existing_moderator_number':'', 'search_by':'', 'existing_assessor_number':'','is_extension_of_scope': False}, 'warning':{'title':'Invalid Assessor Number','message':'Please Enter Correct/Active Assessor Number'}}
						asse_lst = []
						for obj in assessor_ob:
							asse_lst.append(obj.id)
						assessor_obj = self.env['hr.employee'].search([('id', '=', max(asse_lst))])
						if assessor_obj.work_email != moderator_obj.work_email:
							raise Warning(_("Sorry!! Assessor Number and Moderator Number should belongs to same user"))
					if not moderator_obj:
						return {'value': {'existing_moderator_number':'', 'search_by':'', 'existing_assessor_moderator':'', 'is_extension_of_scope':''}, 'warning':{'title': 'Invalid Moderator Number','message':'Please Enter Valid Moderator Number'}}
					elif moderator_obj:
						if already_registered and str(datetime.today().date()) < moderator_obj.moderator_end_date:
							return {'value': {'existing_assessor_moderator':'', 'search_by':'', 'already_registered': False, 'existing_moderator_number':''}, 'warning': {'title': 'Already Registered', 'message': "You are already registered, Your end date is %s" % (moderator_obj.moderator_end_date)}}
						q_vals_line = []
						if not already_registered:
							if moderator_obj.moderator_qualification_ids:
								for q_lines in moderator_obj.moderator_qualification_ids:
									if q_lines.qualification_status == 'approved':
										qual_master_obj = self.env['provider.qualification'].search([('id','=',q_lines.qualification_hr_id.id),('seta_branch_id','=','11')])
										if qual_master_obj:
											accreditation_qualification_line = []
											for lines in q_lines.qualification_line_hr:
												for data in lines:
													val = {
														 'name':data.name,
														 'type':data.type,
														 'id_no':data.id_no,
														 'title':data.title,
														 'level1':data.level1,
														 'level2':data.level2,
														 'level3': data.level3,
														 'selection':data.selection,
														}
													accreditation_qualification_line.append((0, 0, val))
											q_vals = {
														'qual_unit_type': q_lines.qual_unit_type,
														'qualification_id':qual_master_obj.id,
														'saqa_qual_id':qual_master_obj.saqa_qual_id,
														'minimum_credits':qual_master_obj.m_credits,
														'qualification_line':accreditation_qualification_line,
														}
											q_vals_line.append((0, 0, q_vals))
						vals = {
								'name':moderator_obj.name,
								'work_email':moderator_obj.work_email,
								'work_phone':moderator_obj.work_phone,
								'person_cell_phone_number':moderator_obj.person_cell_phone_number,
								'work_address':moderator_obj.work_address,
								'work_address2':moderator_obj.work_address2,
								'work_address3':moderator_obj.work_address3,
								'person_suburb':moderator_obj.person_suburb.id,
								'work_municipality':moderator_obj.work_municipality.id,
								'work_city':moderator_obj.work_city.id,
								'work_province':moderator_obj.work_province.id,
								'work_zip':moderator_obj.work_zip,
								'work_country':moderator_obj.work_country.id,
								'organisation':moderator_obj.organisation.id,
								'organisation_sdl_no':moderator_obj.organisation_sdl_no,
								'department':moderator_obj.department,
								'job_title':moderator_obj.job_title,
								'manager':moderator_obj.manager,
								'notes':moderator_obj.notes,
								'person_title':moderator_obj.person_title,
								'person_name':moderator_obj.person_name,
								'person_last_name':moderator_obj.person_last_name,
								'initials':moderator_obj.initials,
								'cont_number_home':moderator_obj.cont_number_home,
								'cont_number_office':moderator_obj.cont_number_office,
								'citizen_resident_status_code':moderator_obj.citizen_resident_status_code,
								'country_id':moderator_obj.country_id.id,
								'unknown_type':moderator_obj.unknown_type,
								'unknown_type_document':moderator_obj.unknown_type_document,
								'identification_id':moderator_obj.assessor_moderator_identification_id,
								'alternate_id_type':moderator_obj.alternate_id_type,
								'person_birth_date':moderator_obj.person_birth_date,
								'passport_id':moderator_obj.passport_id,
								'national_id':moderator_obj.national_id,
								'id_document':moderator_obj.id_document.id,
								'home_language_code':moderator_obj.home_language_code.id,
								'certificate_no':moderator_obj.certificate_no,
								'record_last_update':moderator_obj.record_last_update,
								'gender':moderator_obj.gender,
								'marital':moderator_obj.marital,
								'dissability':moderator_obj.dissability,
								'person_home_address_1':moderator_obj.person_home_address_1,
								'person_home_address_2':moderator_obj.person_home_address_2,
								'person_home_address_3':moderator_obj.person_home_address_3,
								'person_home_suburb':moderator_obj.person_home_suburb.id,
								'physical${line.level2 or ''}_municipality':moderator_obj.physical_municipality.id,
								'person_home_city':moderator_obj.person_home_city.id,
								'person_home_province_code':moderator_obj.person_home_province_code.id,
								'person_home_zip':moderator_obj.person_home_zip,
								'country_home':moderator_obj.country_home.id,
								'same_as_home':moderator_obj.same_as_home,
								'person_postal_address_1':moderator_obj.person_postal_address_1,
								'person_postal_address_2':moderator_obj.person_postal_address_2,
								'person_postal_address_3':moderator_obj.person_postal_address_3,
								'person_postal_suburb':moderator_obj.person_postal_suburb.id,
								'postal_municipality':moderator_obj.postal_municipality.id,
								'person_postal_city':moderator_obj.person_postal_city.id,
								'person_postal_province_code':moderator_obj.person_postal_province_code.id,
								'person_postal_zip':moderator_obj.person_postal_zip,
								'country_postal':moderator_obj.country_postal.id,
								'professionalbodydoc':moderator_obj.professionalbodydoc.id,
								'sram_doc':moderator_obj.sram_doc.id,
								'cv_document':moderator_obj.cv_document.id,
								'registrationdoc':moderator_obj.registrationdoc.id,
								# Below line is commented because we don't need to fetch master qualifications at the time of extension of scope
								'qualification_ids':q_vals_line,
							  }
						res.update({'value':vals})
#                     elif not existing_assessor_number:
#                         raise Warning(_("Please enter Assessor Number"))
			elif already_registered:
				ass_mod_obj = self.env['assessors.moderators.register'].search([('existing_assessor_moderator', '=', 'ex_moderator'),('existing_moderator_number', '=', existing_moderator_number),('already_registered', '=', True),('approved', '=', False),('final_state','!=','Rejected')])
				if ass_mod_obj:
					return {'value': {'existing_moderator_number':'', 'already_registered': False, 'search_by': '', 'existing_assessor_number':''}, 'warning':{'title':'Duplicate Entry','message':'You have already applied re-registration.'}}
				self._cr.execute("select max(id) from hr_employee where moderator_seq_no = '%s'" % (existing_moderator_number,))
				mod_id = self._cr.fetchall()
				moderator_obj = self.env['hr.employee']
				if mod_id:
					moderator_obj = self.env['hr.employee'].browse(mod_id[0])
				if existing_assessor_number:
					assessor_ob = self.env['hr.employee'].search([('assessor_seq_no', '=', existing_assessor_number)])
					if not assessor_ob:
						return {'value': {'existing_moderator_number':'', 'already_registered': False, 'search_by': '', 'existing_assessor_number':''}, 'warning':{'title':'Invalid Assessor Number','message':'Please Enter Correct Assessor Number'}}
					asse_lst = []
					for obj in assessor_ob:
						asse_lst.append(obj.id)
					assessor_obj = self.env['hr.employee'].search([('id', '=', max(asse_lst))])
					if assessor_obj.work_email != moderator_obj.work_email:
						raise Warning(_("Sorry!! Assessor Number and Moderator Number should belongs to same user"))
				if not moderator_obj:
					return {'value': {'already_registered': False, 'existing_moderator_number':'', 'search_by':'', 'existing_assessor_moderator':''}, 'warning':{'title': 'Invalid Moderator Number','message':'Please Enter Valid Moderator Number'}}
				elif moderator_obj:
					if already_registered and str(datetime.today().date()) < moderator_obj.moderator_end_date:
						return {'value': {'existing_assessor_moderator':'', 'search_by':'', 'already_registered': False, 'existing_moderator_number':''}, 'warning': {'title': 'Already Registered', 'message': "You are already registered, Your end date is %s" % (moderator_obj.moderator_end_date)}}
					q_vals_line = []
					if already_registered:
						if moderator_obj.moderator_qualification_ids:
							for q_lines in moderator_obj.moderator_qualification_ids:
								if q_lines.qualification_status == 'approved':
										qual_master_obj = self.env['provider.qualification'].search([('id','=',q_lines.qualification_hr_id.id),('seta_branch_id','=','11')])
										if qual_master_obj:
											accreditation_qualification_line = []
											for lines in q_lines.qualification_line_hr:
												for data in lines:
													val = {
														 'name':data.name,
														 'type':data.type,
														 'id_no':data.id_no,
														 'title':data.title,
														 'level1':data.level1,
														 'level2':data.level2,
														 'level3': data.level3,
														 'selection':data.selection,
														}
													accreditation_qualification_line.append((0, 0, val))
											q_vals = {
														'qual_unit_type': q_lines.qual_unit_type,
														'qualification_id':qual_master_obj.id,
														'saqa_qual_id':qual_master_obj.saqa_qual_id,
														'minimum_credits':qual_master_obj.m_credits,
														'qualification_line':accreditation_qualification_line,
														}
											q_vals_line.append((0, 0, q_vals))
					vals = {
							'name':moderator_obj.name,
							'work_email':moderator_obj.work_email,
							'work_phone':moderator_obj.work_phone,
							'person_cell_phone_number':moderator_obj.person_cell_phone_number,
							'work_address':moderator_obj.work_address,
							'work_address2':moderator_obj.work_address2,
							'work_address3':moderator_obj.work_address3,
							'person_suburb':moderator_obj.person_suburb.id,
							'work_municipality':moderator_obj.work_municipality.id,
							'work_city':moderator_obj.work_city.id,
							'work_province':moderator_obj.work_province.id,
							'work_zip':moderator_obj.work_zip,
							'work_country':moderator_obj.work_country.id,
							'organisation':moderator_obj.organisation.id,
							'organisation_sdl_no':moderator_obj.organisation_sdl_no,
							'department':moderator_obj.department,
							'job_title':moderator_obj.job_title,
							'manager':moderator_obj.manager,
							'notes':moderator_obj.notes,
							'person_title':moderator_obj.person_title,
							'person_name':moderator_obj.person_name,
							'person_last_name':moderator_obj.person_last_name,
							'initials':moderator_obj.initials,
							'cont_number_home':moderator_obj.cont_number_home,
							'cont_number_office':moderator_obj.cont_number_office,
							'citizen_resident_status_code':moderator_obj.citizen_resident_status_code,
							'country_id':moderator_obj.country_id.id,
							'unknown_type':moderator_obj.unknown_type,
							'unknown_type_document':moderator_obj.unknown_type_document,
							'identification_id':moderator_obj.assessor_moderator_identification_id,
							'alternate_id_type':moderator_obj.alternate_id_type,
							'person_birth_date':moderator_obj.person_birth_date,
							'passport_id':moderator_obj.passport_id,
							'national_id':moderator_obj.national_id,
							'id_document':moderator_obj.id_document.id,
							'home_language_code':moderator_obj.home_language_code.id,
							'certificate_no':moderator_obj.certificate_no,
							'record_last_update':moderator_obj.record_last_update,
							'gender':moderator_obj.gender,
							'marital':moderator_obj.marital,
							'dissability':moderator_obj.dissability,
							'person_home_address_1':moderator_obj.person_home_address_1,
							'person_home_address_2':moderator_obj.person_home_address_2,
							'person_home_address_3':moderator_obj.person_home_address_3,
							'person_home_suburb':moderator_obj.person_home_suburb.id,
							'physical${line.level2 or ''}_municipality':moderator_obj.physical_municipality.id,
							'person_home_city':moderator_obj.person_home_city.id,
							'person_home_province_code':moderator_obj.person_home_province_code.id,
							'person_home_zip':moderator_obj.person_home_zip,
							'country_home':moderator_obj.country_home.id,
							'same_as_home':moderator_obj.same_as_home,
							'person_postal_address_1':moderator_obj.person_postal_address_1,
							'person_postal_address_2':moderator_obj.person_postal_address_2,
							'person_postal_address_3':moderator_obj.person_postal_address_3,
							'person_postal_suburb':moderator_obj.person_postal_suburb.id,
							'postal_municipality':moderator_obj.postal_municipality.id,
							'person_postal_city':moderator_obj.person_postal_city.id,
							'person_postal_province_code':moderator_obj.person_postal_province_code.id,
							'person_postal_zip':moderator_obj.person_postal_zip,
							'country_postal':moderator_obj.country_postal.id,
							'professionalbodydoc':moderator_obj.professionalbodydoc.id,
							'sram_doc':moderator_obj.sram_doc.id,
							'cv_document':moderator_obj.cv_document.id,
							'registrationdoc':moderator_obj.registrationdoc.id,
							'qualification_ids':q_vals_line,
						  }
					res.update({'value':vals})
				if not existing_assessor_number:
					return {'value': {'existing_moderator_number':''}, 'warning':{'title':'Invalid Assessor Number','message':'Please enter Assessor Number'}}
		return res

	@api.multi
	def onchange_existing_assessor_moderator(self, existing_assessor_moderator):
		res = {}
		if existing_assessor_moderator == 'ex_assessor':
			res.update({'value':{'assessor_moderator':'assessor','search_by':'id', 'existing_assessor_id':self.env['res.users'].browse(self._uid).assessor_moderator_id.assessor_moderator_identification_id}})
		if existing_assessor_moderator == 'ex_moderator':
			res.update({'value':{'assessor_moderator':'moderator', 'search_by':'id', 'existing_assessor_id':self.env['res.users'].browse(self._uid).assessor_moderator_id.assessor_moderator_identification_id, 'existing_moderator_id':self.env['res.users'].browse(self._uid).assessor_moderator_id.assessor_moderator_identification_id}})
		return res

	@api.multi
	def on_change_search_by(self, search_by, existing_assessor_moderator):
		res = {}
		if not search_by:
			res.update({'value':{'existing_assessor_id':'', 'existing_assessor_number':'', 'existing_moderator_id':'', 'existing_moderator_number':''}})
		elif search_by == 'number' and existing_assessor_moderator=='ex_assessor':
			res.update({'value':{'existing_assessor_number':self.env['res.users'].browse(self._uid).assessor_moderator_id.assessor_seq_no}})
		elif search_by == 'number' and existing_assessor_moderator=='ex_moderator':
			res.update({'value':{'existing_assessor_number':self.env['res.users'].browse(self._uid).assessor_moderator_id.assessor_seq_no,'existing_moderator_number':self.env['res.users'].browse(self._uid).assessor_moderator_id.moderator_seq_no}})
		return res

	@api.multi
	def onchange_crc(self, citizen_resident_status_code):
		res = {}
		if not citizen_resident_status_code:
			return res
		if citizen_resident_status_code == 'sa':
			country_data = self.env['res.country'].search(['|', ('code', '=', 'ZA'), ('name', '=', 'South Africa')], limit=1)
			res.update({'value':{'country_id':country_data and country_data.id}})
		else:
			res.update({'value':{'country_id':None and None}})
		return res

	@api.multi
	def onchange_person_postal_suburb(self, person_postal_suburb):
		res = {}
		if not person_postal_suburb:
			return res
		if person_postal_suburb:
			sub_res = self.env['res.suburb'].browse(person_postal_suburb)
			res.update({'value':{'person_postal_zip':sub_res.postal_code, 'person_postal_city':sub_res.city_id, 'person_postal_province_code':sub_res.province_id}})
		return res

	@api.multi
	def onchange_person_home_suburb(self, person_home_suburb):
		res = {}
		if not person_home_suburb:
			return res
		if person_home_suburb:
			sub_res = self.env['res.suburb'].browse(person_home_suburb)
			res.update({'value':{'person_home_zip':sub_res.postal_code, 'person_home_city':sub_res.city_id, 'physical_municipality':sub_res.municipality_id, 'person_home_province_code':sub_res.province_id}})
		return res


	@api.multi
	def onchange_person_suburb(self, person_suburb):
		res = {}
		if not person_suburb:
			return res
		if person_suburb:
			sub_res = self.env['res.suburb'].browse(person_suburb)
			res.update({'value':{'work_zip':sub_res.postal_code, 'work_city':sub_res.city_id, 'work_province':sub_res.province_id}})
		return res

	@api.multi
	def onchange_id_no(self, identification_id):
		res, val = {}, {}
		if not identification_id:
			return res
		if len(identification_id) == 13 and str(identification_id).isdigit():
			if not self.already_registered and not self.is_extension_of_scope and self.assessor_moderator == 'assessor':
				exist_assr = self.env['hr.employee'].search([('is_assessors','=',True),('assessor_moderator_identification_id','=',identification_id)])
				exist_ass_mod = self.env['assessors.moderators.register'].search([('final_state','!=','Rejected'),('identification_id','=',identification_id)])
				if exist_assr or exist_ass_mod:
					return {'value':{'identification_id':''},'warning':{'title':'Duplicate Entry (Aleady Exist In the Master)','message':'Please enter unique Identification Number!'}}
			gender_digit = str(identification_id)[6:10]
			citizenship = str(identification_id)[10:11]
			if gender_digit:
				if int(gender_digit) <= 4999:
					val.update({'gender':'female'})
				elif int(gender_digit) >= 5000:
					val.update({'gender':'male'})
			if citizenship:
				if int(citizenship) == 0:
					val.update({'citizen_resident_status_code':'sa'})
				elif int(citizenship) == 1:
					val.update({'citizen_resident_status_code':'PR'})
			year = identification_id[:2]
			identification_id = identification_id[2:]
			month = identification_id[:2]
			identification_id = identification_id[2:]
			day = identification_id[:2]
			if int(month) > 12 or int(month) < 1 or int(day) > 31 or int(day) < 1:
				return {'value':{'identification_id':''},'warning':{'title':'Invalid Identification Number','message':'Incorrect Identification Number!'}}
			else:
				# # Calculating last day of month.
				x_year = int(year)
				if x_year == 00:
					x_year = 2000
				last_day = calendar.monthrange(int(x_year),int(month))[1]
				if int(day) > last_day :
					return {'value':{'identification_id':''},'warning':{'title':'Invalid Identification Number','message':'Incorrect Identification Number!'}}
			if int(year) == 00 or int(year) >= 01 and int(year) <= 20:
				birth_date = datetime.strptime('20' + year + '-' + month + '-' + day, '%Y-%m-%d').date()
			else:
				birth_date = datetime.strptime('19' + year + '-' + month + '-' + day, '%Y-%m-%d').date()

			val.update({'person_birth_date':birth_date})
			res.update({'value':val})
			return res
		else:
			return {'value':{'identification_id':''},'warning':{'title':'Invalid Identification Number','message':'Identification Number should be numeric!'}}
	@api.multi
	def onchange_assessor_moderator(self, assessor_moderator):
		res = {}
		if not assessor_moderator:
			return res
		if assessor_moderator == 'assessor':
			res.update({'value':{'is_assessors':True}})
			res.update({'value':{'is_moderators':False}})
		if assessor_moderator == 'moderator':
			res.update({'value':{'is_moderators':True}})
			res.update({'value':{'is_assessors':False}})
		return res

	@api.multi
	def onchange_assessor_id(self, assessor_id):
		res = {}
		if not assessor_id:
			return res
		assessors_objects = self.env['hr.employee'].search([('assessor_seq_no', '=', assessor_id)])
		ase_lst = []
		for ase_obj in assessors_objects:
			ase_lst.append(ase_obj.id)
		assessors_ids = []
		if ase_lst:
			assessors_ids = self.env['hr.employee'].search([('id', '=', max(ase_lst))])
		if assessors_ids:
			for assessor_data in assessors_ids:
				if assessor_data.end_date:
					if assessor_data.end_date < str(datetime.now().date()):
#                         raise Warning(_("Sorry! %s Assessor is currently In-Active") % (assessor_id))
						return {'value': {'assessor_id': ''}, 'warning':{'title':'In-Active Assessor ID','message':'Sorry! Assessor is currently In-Active'}}

				q_vals_line = []
				if assessor_data.qualification_ids:
					for q_lines in assessor_data.qualification_ids:
						if q_lines.qualification_status == 'approved':
							qual_master_obj = self.env['provider.qualification'].search([('id','=',q_lines.qualification_hr_id.id),('seta_branch_id','=','11')])
							if qual_master_obj:
								accreditation_qualification_line = []
								for lines in q_lines.qualification_line_hr:
									for data in lines:
										val = {
											 'name':data.name,
											 'type':data.type,
											 'id_no':data.id_no,
											 'title':data.title,
											 'level1':data.level1,
											 'level2':data.level2,
											 'level3': data.level3,
											 'selection':data.selection,
											}
										accreditation_qualification_line.append((0, 0, val))
								q_vals = {
											'qual_unit_type': q_lines.qual_unit_type,
											'qualification_id':qual_master_obj.id,
											'saqa_qual_id':qual_master_obj.saqa_qual_id,
											'minimum_credits':qual_master_obj.m_credits,
											'qualification_line':accreditation_qualification_line,
											}
								q_vals_line.append((0, 0, q_vals))
				vals = {
					 'name' : assessor_data.name,
					 'seq_no':assessor_data.assessor_seq_no,
					 'type':assessor_data.type,
					 'work_email' : assessor_data.work_email,
					 'work_phone' : assessor_data.work_phone,
					 'work_address' : assessor_data.work_address or False,
					 'work_address2' : assessor_data.work_address2,
					 'work_address3' : assessor_data.work_address3,
					 'work_location' : assessor_data.work_location,
					 'person_suburb' : assessor_data.person_suburb and  assessor_data.person_suburb.id,
					 'work_city' : assessor_data.work_city and assessor_data.work_city.id,
					 'work_province' : assessor_data.work_province and assessor_data.work_province.id,
					 'work_zip' : assessor_data.work_zip,
					 'work_country': assessor_data.work_country and assessor_data.work_country.id,
					 'department' : assessor_data.department or False,
					 'job_title' : assessor_data.job_title or False,
					 'manager' : assessor_data.manager or False,
					 'notes' : assessor_data.notes,
					 'person_title' : assessor_data.person_title,
					 'person_name' : assessor_data.person_name,
					 'dissability' : assessor_data.dissability,
					 'person_last_name' : assessor_data.person_last_name,
					 'cont_number_home' : assessor_data.cont_number_home,
					 'cont_number_office' : assessor_data.cont_number_office,
					 'person_cell_phone_number' : assessor_data.person_cell_phone_number,
					 'citizen_resident_status_code' : assessor_data.citizen_resident_status_code,
					 'country_id' : assessor_data.country_id and assessor_data.country_id.id or False,
					 'identification_id' : assessor_data.assessor_moderator_identification_id,
					 'person_birth_date' : assessor_data.person_birth_date,
					 'passport_id' : assessor_data.passport_id,
					 'national_id' : assessor_data.national_id,
					 'home_language_code' : assessor_data.home_language_code and assessor_data.home_language_code.id,
					 'gender' : assessor_data.gender,
					 'marital' : assessor_data.marital,
					 'id_document':assessor_data.id_document,
					 'registrationdoc':assessor_data.registrationdoc,
					 'professionalbodydoc':assessor_data.professionalbodydoc,
					 'sram_doc':assessor_data.sram_doc,
					 'cv_document':assessor_data.cv_document,
					 'person_home_address_1' : assessor_data.person_home_address_1,
					 'person_home_address_2' : assessor_data.person_home_address_2,
					 'person_home_address_3' : assessor_data.person_home_address_3,
					 'person_home_province_code': assessor_data.person_home_province_code and assessor_data.person_home_province_code.id,
					 'person_home_city' : assessor_data.person_home_city and assessor_data.person_home_city.id,
					 'person_home_suburb' : assessor_data.person_home_suburb and  assessor_data.person_home_suburb.id,
					 'person_home_zip' : assessor_data.person_home_zip,
					 'country_home': assessor_data.country_home and assessor_data.country_home.id,
					 'person_postal_address_1' : assessor_data.person_postal_address_1,
					 'person_postal_address_2' : assessor_data.person_postal_address_2,
					 'person_postal_address_3' : assessor_data.person_postal_address_3,
					 'person_postal_suburb' : assessor_data.person_postal_suburb and assessor_data.person_postal_suburb.id,
					 'person_postal_city' : assessor_data.person_postal_city and assessor_data.person_postal_city.id,
					 'person_postal_province_code': assessor_data.person_postal_province_code and assessor_data.person_postal_province_code.id,
					 'person_postal_zip': assessor_data.person_postal_zip,
					 'country_postal': assessor_data.country_postal and assessor_data.country_postal.id,
					 'dissability' : assessor_data.dissability,
	#                  'is_assessors':assessor_data.is_assessors,
					 'is_moderators':True,
					 'seta_elements':True,
					 'same_as_home':assessor_data.same_as_home,
					 'qualification_ids':q_vals_line,

					 'unknown_type':assessor_data.unknown_type,
					 'unknown_type_document':assessor_data.unknown_type_document and assessor_data.unknown_type_document.id
				}

			res.update({'value':vals,})
		else:
			return {'value': {'assessor_id': ''},\
						'warning': {'title':'Invalid Asssessor ID','message':'Assessor does not exits in the system!'} }
		return res

	@api.multi
	def onchange_sameas_home(self, same_as_home):
		res = {}
		if not same_as_home:
			return res
		result = {
				  'person_postal_address_1' : self.person_home_address_1,
				  'person_postal_address_2' : self.person_home_address_2,
				  'person_postal_address_3' : self.person_home_address_3,
				  'person_postal_suburb' : self.person_home_suburb,
				  'person_postal_city' : self.person_home_city,
				  'person_postal_province_code' : self.person_home_province_code and self.person_home_province_code.id,
				  'person_postal_zip' : self.person_home_zip,
				  'country_postal' : self.country_home and self.country_home.id
				  }
		res.update({'value':result})
		return res

	@api.multi
	def open_map(self, street, city, state, country, zip):
		url = "http://maps.google.com/maps?oi=map&q="
		if street:
			url += street.replace(' ', '+')
		if city:
			url += '+' + city.replace(' ', '+')
		if state:
			url += '+' + state.name.replace(' ', '+')
		if country:
			url += '+' + country.name.replace(' ', '+')
		if zip:
			url += '+' + zip.replace(' ', '+')
		return {
		'type': 'ir.actions.act_url',
		'url':url,
		'target': 'new'
		}

	@api.multi
	def work_addr_map(self):
		return self.open_map(self.work_address, self.work_city, self.work_province, self.work_country, self.work_zip)

	@api.multi
	def home_addr_map(self):
		return self.open_map(self.person_home_address_1, self.person_home_city, self.person_home_province_code, self.country_home, self.person_home_zip)

	@api.multi
	def postal_addr_map(self):
		return self.open_map(self.person_postal_address_1, self.person_postal_city, self.person_postal_province_code, self.country_postal, self.person_postal_zip)

	@api.multi
	def country_for_province(self, province):
		state = self.env['res.country.state'].browse(province)
		return state.country_id.id

	@api.multi
	def onchange_work_province(self, province):
		if province:
			country_id = self.country_for_province(province)
			return {'value': {'work_country': country_id }}
		return {}

	@api.multi
	def onchange_home_province(self, province):
		if province:
			country_id = self.country_for_province(province)
			return {'value': {'country_home': country_id }}
		return {}

	@api.multi
	def onchange_postal_province(self, province):
		if province:
			country_id = self.country_for_province(province)
			return {'value': {'country_postal': country_id }}
		return {}

	@api.multi
	def action_submit_button(self):
		context = self._context
		if context is None:
			context = {}
		self = self.with_context(submit=True)
		if not self.work_address or not self.work_address2 or not self.work_province or not self.work_country:
			raise Warning(_("Please fill work address in Public Information!!"))
		if not self.citizen_resident_status_code:
			raise Warning(_("Please select citizen status in Personal Information!!"))
		if self.identification_id:
			if len(self.identification_id) > 13:
				raise Warning(_("You can enter maximum 13 digits Identification No. only!!"))
		if not self.qualification_ids:
				raise Warning(_("Please add qualification!!"))
		if not self.person_cell_phone_number:
			raise Warning(_('Please enter mobile number in General Information'))
		if not self.cv_document:
			raise Warning(_('Please upload CV Document'))

		if self.qualification_ids:
			for line in self.qualification_ids:
				if line.qual_unit_type == 'qual':
					if line.qualification_id.is_exit_level_outcomes == False:
						if line.minimum_credits > line.total_credits:
							raise Warning(_("Sum of checked unit standards credits point should be greater than or equal to Minimum credits point for Qualification ID: %s !!")%(line.saqa_qual_id))
		q_vals_line = []
		if self.qualification_ids:
			for q_lines in self.qualification_ids:
				accreditation_qualification_line = []
				for lines in q_lines.qualification_line:
					for data in lines:
						val = {
							 'name':data.name,
							 'type':data.type,
							 'id_no':data.id_no,
							 'title':data.title,
							 'level1':data.level1,
							 'level2':data.level2,
							 'level3': data.level3,
							 'selection':data.selection
							}
						accreditation_qualification_line.append((0, 0, val))
				q_vals = {
							'qual_unit_type': q_lines.qual_unit_type,
							'qualification_evaluation_id':q_lines.qualification_id.id,
							'saqa_qual_id':q_lines.saqa_qual_id,
							'minimum_credits':q_lines.minimum_credits,
							'total_credits':q_lines.total_credits,
							'qualification_line_evaluation':accreditation_qualification_line,
							}
				q_vals_line.append((0, 0, q_vals))

		ir_model_data_obj = self.env['ir.model.data']
		mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_assessors_moderator_submit')
		if mail_template_id:
			self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)

		self.write({'assessors_moderators_status_ids':[(0, 0, {'am_name':self.env['res.users'].browse(self._uid).name, 'am_date':datetime.now(), 'am_status':'Submitted', 'am_updation_date':self.write_date, 'am_comment':self.comment_line})]})
		self.write({'comment_line':''})
#        if self.already_registered == False and self.is_extension_of_scope == False and not self.assessor_id:
		return self.write({'state':'verification', 'submitted':True, 'final_state':'Submitted', 'qualification_evaluation_ids':q_vals_line})
		# For Mail Server notification
#         user_pool = self.env['res.users']
#         group_pool = self.env['res.groups']
#         email_to_string=""
#
#         group_obj = group_pool.search([('name', '=', 'ETQE Manager')])
#         for group_data in group_obj:
#             print "group_id====",group_data.id
#             user_obj = user_pool.search([('groups_id', '=', group_data.id)])
#             for user_data in user_obj:
#                 print "user email===",user_data.partner_id.email
#                 if email_to_string:
#                     email_to_string=email_to_string + ',' + user_data.partner_id.email
#                 else:
#                     email_to_string=user_data.partner_id.email
#
#         print "email_to_string===",email_to_string
#         email_template_obj = self.env['email.template']
#         ir_model_data_obj = self.env['ir.model.data']
#         mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_edi_etq11')
#         print "mail_template_id====",mail_template_id
#         if mail_template_id:
#             temp_obj = email_template_obj.browse(mail_template_id[1])
#             current_user_obj = user_pool.browse(self._uid)
#             print "login user =",current_user_obj.partner_id.email
#             if email_to_string:
#                 if temp_obj.write({'email_to' : email_to_string, 'email_from' : current_user_obj.partner_id.email}):
#                     print "done="
#                     self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True,context=self.env.context)
#         return True
	@api.multi
	def action_verify_button(self):
		context = self._context
		qual_verify = False
		if context is None:
			context = {}
		for qual in self.qualification_evaluation_ids:
			if qual.verify == True:
				qual_verify = True
		if qual_verify == False:
			raise Warning(_("Please check/verify at least one Qualification before Evaluate"))
		if not self.comment_line:
			raise Warning(_("Please enter status comment"))
		self = self.with_context(verify=True)
		if(self.registrationdoc.id != False and self.registrationdoc_bool == False):
			raise Warning(_("Please check Documents before Evaluate!"))
		if(self.professionalbodydoc.id != False and self.professionalbodydoc_bool == False):
			raise Warning(_("Please check Professional body before Evaluate!"))
		if(self.sram_doc.id != False and self.sram_doc_bool == False):
			raise Warning(_("Please check Statement before Evaluate"))
		if(self.cv_document.id != False and self.cv_document_bool == False):
			raise Warning(_("Please check CV Document Documents before Evaluate"))
		ir_model_data_obj = self.env['ir.model.data']
		mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_assessors_moderator_verify')
		self.write({'assessors_moderators_status_ids':[(0, 0, {'am_name':self.env['res.users'].browse(self._uid).name, 'am_date':datetime.now(), 'am_status':'Evaluated', 'am_updation_date':self.write_date, 'am_comment':self.comment_line})]})
		self.write({'comment_line':''})
		if mail_template_id:
			self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
		self.write({'state':'evaluation', 'verify':True, 'ass_mod_state':'submit', 'final_state':'Evaluated'})
		return True

	@api.multi
	def action_evaluate_button(self):
		context = self._context
		if context is None:
			context = {}
		if not self.comment_line:
			raise Warning(_("Please enter status comment"))
		self = self.with_context(evaluate=True)
		self.write({'assessors_moderators_status_ids':[(0, 0, {'am_name':self.env['res.users'].browse(self._uid).name, 'am_date':datetime.now(), 'am_status':'Recommended', 'am_updation_date':self.write_date, 'am_comment':self.comment_line})]})
		self.write({'comment_line':''})
		'''Below 4 lines of mail template has been commented as per client request on 23rd Nov.17'''
#         ir_model_data_obj = self.env['ir.model.data']
#         mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_assessors_moderator_evaluated')
#         if mail_template_id:
#             self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
		self.write({'state':'evaluation', 'evaluate':True, 'final_state':'Recommended'})
		return True

	@api.multi
	def action_denied_button(self):
		context = self._context
		if context is None:
			context = {}
		if not self.comment_line:
			raise Warning(_("Please enter status comment"))
		self = self.with_context(submit=True)
		ir_model_data_obj = self.env['ir.model.data']
		mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_assessors_moderator_denied')
		if mail_template_id:
			self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)

		self.write({'assessors_moderators_status_ids':[(0, 0, {'am_name':self.env['res.users'].browse(self._uid).name, 'am_date':datetime.now(), 'am_status':'Rejected', 'am_updation_date':self.write_date, 'am_comment':self.comment_line})]})
		self.write({'state':'denied', 'denied':True, 'final_state':'Rejected', 'comment_line':''})
		return True

	@api.multi
	def action_reevaluate_button(self):
		if not self.comment_line:
			raise Warning(_("Please enter status comment"))
		self.write({'assessors_moderators_status_ids':[(0, 0, {'am_name':self.env['res.users'].browse(self._uid).name, 'am_date':datetime.now(), 'am_status':'Re-Evaluated', 'am_updation_date':self.write_date, 'am_comment':self.comment_line})]})
		self.write({'state':'verification', 'evaluate':False, 'verify':False, 'denied':False, 'comment_line':''})
		return True

	@api.model
	def create(self, vals):
		context = self._context
		if vals.get('is_extension_of_scope') or vals.get('already_registered') or vals.get('is_moderators'):
			vals['related_assessor_moderator'] = self.env['res.users'].browse(self._uid).assessor_moderator_id.id
		vals['final_state'] = 'Draft'
		if not context.get('from_website1', False) :
			vals['assessor_moderator_register_date'] = datetime.today().date()
#             vals['assessors_moderators_ref'] = self.env['ir.sequence'].get('assessors.moderators.reference')
			if vals['assessor_moderator'] == 'assessor':
				vals['assessors_moderators_ref'] = self.env['ir.sequence'].get('assessors.register')
			if vals['assessor_moderator'] == 'moderator':
				vals['assessors_moderators_ref'] = self.env['ir.sequence'].get('moderators.register')
		if vals.get('assessor_moderator') == 'assessor':
			vals['is_assessors'] = True
		if vals.get('assessor_moderator') == 'moderator':
			vals['is_moderators'] = True
		if vals.get('identification_id') and vals.get('existing_assessor_moderator') == 'ex_assessor':
			assessors_obj = self.env['hr.employee'].search([('assessor_moderator_identification_id', '=', vals['identification_id'])])
			ase_lst = []
			for ase_obj in assessors_obj:
				ase_lst.append(ase_obj.id)
			assessor_obj = self.env['hr.employee'].search([('id', '=', max(ase_lst))])
			if assessor_obj:
				vals.update({'existing_assessor_number':assessor_obj.assessor_seq_no})
		if vals.get('identification_id') and vals.get('existing_assessor_moderator') == 'ex_moderator':
			moderators_obj = self.env['hr.employee'].search([('assessor_moderator_identification_id', '=', vals['identification_id'])])
			mod_lst = []
			for mod_obj in moderators_obj:
				mod_lst.append(mod_obj.id)
			moderator_obj = self.env['hr.employee'].search([('id', '=', max(mod_lst))])
			if moderator_obj:
				vals.update({'existing_assessor_number':moderator_obj.assessor_seq_no, 'existing_moderator_number':moderator_obj.moderator_seq_no})
		res = super(assessors_moderators_register, self).create(vals)
		if not context.get('from_website1', False) :
			if '@' not in res.work_email:
				raise Warning(_('Please enter valid email address'))
			if not res.person_cell_phone_number:
				raise Warning(_('Please Enter Mobile Number'))
		ir_model_data_obj = self.env['ir.model.data']
		mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_edi_etq11')
		if mail_template_id:
			self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], res.id, force_send=True, context=self.env.context)
		# For Mail Server notification
#         user_pool = self.env['res.users']
#         group_pool = self.env['res.groups']
#         email_to_string=""
#
#         group_obj = group_pool.search([('name', '=', 'ETQE Manager')])
#         for group_data in group_obj:
#             user_obj = user_pool.search([('groups_id', '=', group_data.id)])
#             for user_data in user_obj:
#                 if email_to_string:
#                     email_to_string=email_to_string + ',' + user_data.partner_id.email
#                 else:
#                     email_to_string=user_data.partner_id.email
#
#         email_template_obj = self.env['email.template']
#         ir_model_data_obj = self.env['ir.model.data']
#         mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_edi_etq11')
#         if mail_template_id:
#             temp_obj = email_template_obj.browse(mail_template_id[1])
#             current_user_obj = user_pool.browse(self._uid)
#             if email_to_string:
#                 if temp_obj.write({'email_to' : email_to_string, 'email_from' : current_user_obj.partner_id.email,'lang':'en_US'}):
#                     self.pool['email.template'].send_mail(self.env.cr, self.env.uid, temp_obj.id,res.id, force_send=True,context=self.env.context)
		return res

	@api.multi
	def action_approve_button(self):
		self.write({'assessors_moderators_status_ids':[(0, 0, {'am_name':self.env['res.users'].browse(self._uid).name, 'am_date':self.create_date, 'am_status':'Approved', 'am_updation_date':self.write_date, 'am_comment':self.comment_line, 'comment_line':''})]})
		context = self._context
		seq_no = ""
		asssesor_seq_no = ''
		moderator_seq_no = ''
		if context is None:
			context = {}
		self = self.with_context(submit=True, from_registration_process=True)
		mainlist = []
		group_obj = self.env['res.groups']
		ir_model_data_obj = self.env['ir.model.data']
		if not self.comment_line:
			raise Warning(_("Please enter status comment"))
		# New Moderator Registration
		if not self.already_registered and not self.is_extension_of_scope :
			if self.is_moderators:
				assessors_objects = self.env['hr.employee'].search([('is_assessors', '=', True), ('assessor_seq_no', '=', self.assessor_id)])
				if not assessors_objects:
					raise Warning('Assessor does not exist in system.')
				ase_lst = []
				for ase_obj in assessors_objects:
					ase_lst.append(ase_obj.id)
				assessors_ids = self.env['hr.employee'].search([('id', '=', max(ase_lst))])
				group_data = group_obj.search(['|', ('name', '=', 'Portal'), ('name', '=', 'Moderators')])
				for data in group_data:
					tup1 = (4, data.id)
					mainlist.append(tup1)
				moderator_seq_no = self.env['ir.sequence'].get('moderators.master.register')
				self.write({'temp_moderator_seq_no':moderator_seq_no})
				q_vals_line = []
				if self.qualification_evaluation_ids:
					for q_lines in self.qualification_evaluation_ids:
						if q_lines.verify == True:
							if q_lines.select:
								accreditation_qualification_line = []
								for lines in q_lines.qualification_line_evaluation:
									for data in lines:
										if data.selection:
											val = {
												 'name':data.name,
												 'type':data.type,
												 'id_no':data.id_no,
												 'title':data.title,
												 'level1':data.level1,
												 'level2':data.level2,
												 'level3': data.level3,
												 'selection':data.selection,
												}
											accreditation_qualification_line.append((0, 0, val))
								q_vals = {
											'qual_unit_type': q_lines.qual_unit_type,
											'qualification_hr_id':q_lines.qualification_evaluation_id.id,
											'saqa_qual_id':q_lines.saqa_qual_id,
											'qualification_line_hr':accreditation_qualification_line,
											'qualification_status':'approved',
											'approval_request':True,
											'request_send':True,
											}
								q_vals_line.append((0, 0, q_vals))
				for assessor_data in assessors_ids:
					group_data = group_obj.search([('name', '=', 'Moderators')])
					for data in group_data:
						tup1 = (4, data.id)
						mainlist.append(tup1)
					self._cr.execute("update res_users set internal_external_users = 'Moderators' where assessor_moderator_id=%s" % (assessor_data.id))
					assessor_data.user_id.write({'groups_id':mainlist, })
					assessor_data.write({'moderator_qualification_ids':[(2, assessor.id) for assessor in assessor_data.qualification_ids]})
					assessor_data.write({'is_moderators':True,
										 'moderator_seq_no':moderator_seq_no,
										 'moderator_qualification_ids':q_vals_line,
										 'moderator_cv_document':self.cv_document and self.cv_document.id,
										 'moderator_unknown_type_document':self.unknown_type_document and self.unknown_type_document.id,
										 'id_document':self.id_document and self.id_document.id,
										 'moderator_registrationdoc':self.registrationdoc and self.registrationdoc.id,
										 'moderator_professionalbodydoc':self.professionalbodydoc and self.registrationdoc.id,
										 'moderator_sram_doc':self.sram_doc and self.sram_doc.id,
										 })
#                     etqe_conf = self.env['etqe.config'].search([])
#                     sdate = datetime.today().date()
#                     new_date = "2018-03-31"
#                     if etqe_conf:
#                         etqe_brw = self.env['etqe.config'].browse(etqe_conf.id)
#                         effdate = datetime.strptime(etqe_brw.from_effective_date, '%Y-%m-%d').date()
#                         if  effdate <= datetime.today().date():
#                             if etqe_brw.etqa_end_date:
#                                 new_date = sdate + relativedelta(years=etqe_brw.etqa_end_date)
					''' As per new configuration '''
					etqe_conf = self.env['etqe.config'].search([])
					sdate = datetime.today().date()
					new_date = "2020-03-31"
					if etqe_conf:
						etqe_brw = self.env['etqe.config'].browse(etqe_conf[0].id)
						if etqe_brw.etqa_end_date and etqe_brw.seta_license_end_date:
							seta_license_date = datetime.strptime(etqe_brw.seta_license_end_date, '%Y-%m-%d').date()
							new_date = sdate + relativedelta(years=etqe_brw.etqa_end_date)
							if new_date > seta_license_date:
								new_date = etqe_brw.seta_license_end_date
					assessor_data.write({'moderator_start_date':sdate, 'moderator_end_date':new_date})
					self.write({'reg_end': new_date})
				self.write({'state':'approved', 'approved':True, 'assessor_moderator_approval_date':datetime.today().date(), 'final_state':'Approved', })
				self.write({'reg_start': self.assessor_moderator_approval_date})

				mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_moderator_approved')
				if mail_template_id:
					self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
		# Existing Moderator Extension of Scope
		elif self.is_extension_of_scope and self.existing_assessor_moderator == 'ex_moderator':
			assessors_ids = ''
			if self.existing_assessor_number:
				assessors_ids = self.env['hr.employee'].search([('is_active_assessor', '=', True),('is_assessors', '=', True),('assessor_seq_no', '=', self.existing_assessor_number)])
			if self.existing_assessor_id:
				assessors_ids = self.env['hr.employee'].search([('is_active_assessor', '=', True),('is_assessors', '=', True),('assessor_moderator_identification_id', '=', self.existing_assessor_id)])
			if self.existing_moderator_id:
				assessors_ids = self.env['hr.employee'].search([('is_active_moderator', '=', True),('is_moderators', '=', True),('assessor_moderator_identification_id', '=', self.existing_moderator_id)])
			if self.existing_moderator_number:
				assessors_ids = self.env['hr.employee'].search([('is_active_moderator', '=', True),('is_moderators', '=', True),('moderator_seq_no', '=', self.existing_moderator_number)])
			if assessors_ids:
				ase_lst = []
				for ase_obj in assessors_ids:
					ase_lst.append(ase_obj.id)
					if ase_lst:
						assessors_ids = self.env['hr.employee'].search([('id', '=', min(ase_lst))])
				group_data = group_obj.search(['|', ('name', '=', 'Portal'), ('name', '=', 'Moderators')])
				for data in group_data:
					tup1 = (4, data.id)
					mainlist.append(tup1)
				q_vals_line = []
				if self.qualification_evaluation_ids:
					for q_lines in self.qualification_evaluation_ids:
						if q_lines.verify == True:
							if q_lines.select:
								accreditation_qualification_line = []
								for lines in q_lines.qualification_line_evaluation:
									for data in lines:
										if data.selection:
											val = {
												 'name':data.name,
												 'type':data.type,
												 'id_no':data.id_no,
												 'title':data.title,
												 'level1':data.level1,
												 'level2':data.level2,
												 'level3': data.level3,
												 'selection':data.selection,
												}
											accreditation_qualification_line.append((0, 0, val))
								q_vals = {
											'qual_unit_type': q_lines.qual_unit_type,
											'qualification_hr_id':q_lines.qualification_evaluation_id.id,
											'saqa_qual_id':q_lines.saqa_qual_id,
											'qualification_line_hr':accreditation_qualification_line,
											'qualification_status':'approved',
											'approval_request':True,
											'request_send':True,
											}
								q_vals_line.append((0, 0, q_vals))
				for assessor_data in assessors_ids:
					group_data = group_obj.search([('name', '=', 'Moderators')])
					for data in group_data:
						tup1 = (4, data.id)
						mainlist.append(tup1)
					assessor_data.user_id.write({'groups_id':mainlist, })
					'''Below code is written to delete qualifications from Moderator master data before appending'''
					unlink_qual_list = []
					for mod_qual in assessor_data.moderator_qualification_ids:
						for qual in self.qualification_evaluation_ids:
							if qual.verify:
								if mod_qual.qualification_hr_id == qual.qualification_evaluation_id:
								   unlink_qual_list.append((2, mod_qual.id))
					assessor_data.write({'moderator_qualification_ids':unlink_qual_list})
					assessor_data.write({
										 'moderator_qualification_ids':q_vals_line,
										 'type':self.type,
										 'work_email' : self.work_email,
										 'work_phone' : self.work_phone,
										 'work_address' : self.work_address or False,
										 'work_address2' : self.work_address2,
										 'work_address3' : self.work_address3,
										 'work_location' : self.work_location,
										 'person_suburb' : self.person_suburb and  self.person_suburb.id,
										 'work_city' : self.work_city and self.work_city.id,
										 'work_province' : self.work_province and self.work_province.id,
										 'work_zip' : self.work_zip,
										 'work_country': self.work_country and self.work_country.id,
										 'department' : self.department or False,
										 'job_title' : self.job_title or False,
										 'manager' : self.manager or False,
										 'notes' : self.notes,
										 'person_title' : self.person_title,
										 'person_name' : self.person_name,
										 'dissability' : self.dissability,
										 'person_last_name' : self.person_last_name,
										 'cont_number_home' : self.cont_number_home,
										 'cont_number_office' : self.cont_number_office,
										 'person_cell_phone_number' : self.person_cell_phone_number,
										 'citizen_resident_status_code' : self.citizen_resident_status_code,
										 'country_id' : self.country_id and self.country_id.id or False,
										 'person_birth_date' : self.person_birth_date,
										 'gender' : self.gender,
										 'marital' : self.marital,
										 'person_home_address_1' : self.person_home_address_1,
										 'person_home_address_2' : self.person_home_address_2,
										 'person_home_address_3' : self.person_home_address_3,
										 'person_home_province_code': self.person_home_province_code and self.person_home_province_code.id,
										 'person_home_city' : self.person_home_city and self.person_home_city.id,
										 'person_home_suburb' : self.person_home_suburb and  self.person_home_suburb.id,
										 'person_home_zip' : self.person_home_zip,
										 'country_home': self.country_home and self.country_home.id,
										 'person_postal_address_1' : self.person_postal_address_1,
										 'person_postal_address_2' : self.person_postal_address_2,
										 'person_postal_address_3' : self.person_postal_address_3,
										 'person_postal_suburb' : self.person_postal_suburb and self.person_postal_suburb.id,
										 'person_postal_city' : self.person_postal_city and self.person_postal_city.id,
										 'person_postal_province_code': self.person_postal_province_code and self.person_postal_province_code.id,
										 'person_postal_zip': self.person_postal_zip,
										 'country_postal': self.country_postal and self.country_postal.id,
										 'dissability' : self.dissability,
										 'seta_elements':True,
										 'same_as_home':self.same_as_home,
										 'organisation':self.organisation.id,
										 'organisation_sdl_no':self.organisation_sdl_no,
										 'cv_document':self.cv_document and self.cv_document.id,
										 'unknown_type_document':self.unknown_type_document and self.unknown_type_document.id,
										 'id_document':self.id_document and self.id_document.id,
										 'registrationdoc':self.registrationdoc and self.registrationdoc.id,
										 'professionalbodydoc':self.professionalbodydoc and self.registrationdoc.id,
										 'sram_doc':self.sram_doc and self.sram_doc.id,
										 })
				moderator_seq_no = assessors_ids.moderator_seq_no
				self.write({'temp_moderator_seq_no':moderator_seq_no})
				self.write({'state':'approved', 'approved':True, 'assessor_moderator_approval_date':datetime.today().date(), 'final_state':'Approved', })
				self.write({'reg_start': assessors_ids.moderator_start_date,
							'reg_end': assessors_ids.moderator_end_date,
							})
				mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_moderator_eos')
				if mail_template_id:
					self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
		#Moderator Re-registration
		elif self.already_registered and self.existing_assessor_moderator == 'ex_moderator':
			assessors_ids = ''
			if self.existing_assessor_number:
				assessors_ids = self.env['hr.employee'].search([('is_assessors', '=', True), ('assessor_seq_no', '=', self.existing_assessor_number)])
			elif self.existing_assessor_id or self.existing_moderator_id:
				assessors_ids = self.env['hr.employee'].search(['','|'('is_assessors', '=', True), ('assessor_moderator_identification_id', '=', self.existing_assessor_id),('assessor_moderator_identification_id', '=', self.existing_moderator_id)])
			if self.already_registered:
				ase_lst = []
				for ase_obj in assessors_ids:
					ase_lst.append(ase_obj.id)
				if ase_lst:
					assessors_ids = self.env['hr.employee'].search([('id', '=', max(ase_lst))])
					if self.existing_moderator_number:
						assessors_ids.write({'moderator_seq_no':self.existing_moderator_number, })
						self.write({'temp_moderator_seq_no':self.existing_moderator_number})
					if self.existing_moderator_id:
						moderator_id = self.env['hr.employee'].search([('is_moderators', '=', True),('assessor_moderator_identification_id','=',self.existing_moderator_id)])
						if moderator_id:
							assessors_ids.write({'moderator_seq_no':moderator_id.moderator_seq_no, })
							self.write({'temp_moderator_seq_no':moderator_id.moderator_seq_no,})
			if assessors_ids:
				group_data = group_obj.search(['|', ('name', '=', 'Portal'), ('name', '=', 'Moderators')])
				for data in group_data:
					tup1 = (4, data.id)
					mainlist.append(tup1)
				# moderator_seq_no = self.env['ir.sequence'].get('moderators.master.register')
				q_vals_line = []
				if self.qualification_evaluation_ids:
					for q_lines in self.qualification_evaluation_ids:
						if q_lines.verify == True:
							if q_lines.select:
								accreditation_qualification_line = []
								for lines in q_lines.qualification_line_evaluation:
									for data in lines:
										if data.selection:
											val = {
												 'name':data.name,
												 'type':data.type,
												 'id_no':data.id_no,
												 'title':data.title,
												 'level1':data.level1,
												 'level2':data.level2,
												 'level3': data.level3,
												 'selection':data.selection,
												}
											accreditation_qualification_line.append((0, 0, val))
								q_vals = {
											'qual_unit_type': q_lines.qual_unit_type,
											'qualification_hr_id':q_lines.qualification_evaluation_id.id,
											'saqa_qual_id':q_lines.saqa_qual_id,
											'qualification_line_hr':accreditation_qualification_line,
											'qualification_status':'approved',
											'approval_request':True,
											'request_send':True,
											}
								q_vals_line.append((0, 0, q_vals))
				for assessor_data in assessors_ids:
					group_data = group_obj.search([('name', '=', 'Moderators')])
					for data in group_data:
						tup1 = (4, data.id)
						mainlist.append(tup1)
					assessor_data.user_id.write({'groups_id':mainlist, })
					'''Below code is written to delete qualifications from Moderator master data before appending'''
					unlink_qual_list = []
					for mod_qual in assessor_data.moderator_qualification_ids:
						for qual in self.qualification_evaluation_ids:
							if qual.verify:
								if mod_qual.qualification_hr_id == qual.qualification_evaluation_id:
								   unlink_qual_list.append((2, mod_qual.id))
					assessor_data.write({'moderator_qualification_ids':unlink_qual_list})
					#Below line is commented
					#assessor_data.write({'moderator_qualification_ids':[(2, assessor.id) for assessor in assessor_data.moderator_qualification_ids]})
					assessor_data.write({'is_moderators':True,
										 'is_moderators':True,
										 'is_active_moderator':True,
										 # 'moderator_seq_no':moderator_seq_no,
										 'moderator_qualification_ids':q_vals_line,
										 })
					if self.already_registered:
#                         etqe_conf = self.env['etqe.config'].search([])
#                         sdate = datetime.today().date()
#                         new_date = "2018-03-31"
#                         if etqe_conf:
#                             etqe_brw = self.env['etqe.config'].browse(etqe_conf.id)
#                             effdate = datetime.strptime(etqe_brw.from_effective_date, '%Y-%m-%d').date()
#                             if  effdate <= datetime.today().date():
#                                 if etqe_brw.etqa_end_date:
#                                     new_date = sdate + relativedelta(years=etqe_brw.etqa_end_date)
						''' As per new configuration '''
						etqe_conf = self.env['etqe.config'].search([])
						sdate = datetime.today().date()
						new_date = "2020-03-31"
						if etqe_conf:
							etqe_brw = self.env['etqe.config'].browse(etqe_conf[0].id)
							if etqe_brw.etqa_end_date and etqe_brw.seta_license_end_date:
								seta_license_date = datetime.strptime(etqe_brw.seta_license_end_date, '%Y-%m-%d').date()
								new_date = sdate + relativedelta(years=etqe_brw.etqa_end_date)
								if new_date > seta_license_date:
									new_date = etqe_brw.seta_license_end_date
						assessor_data.write({'moderator_start_date':sdate, 'moderator_end_date':new_date, 'is_active_assessor':True})
						self.write({'reg_end': new_date})
				self.write({'state':'approved', 'approved':True, 'assessor_moderator_approval_date':datetime.today().date(), 'final_state':'Approved', })
				self.write({'reg_start': self.assessor_moderator_approval_date})
				mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_moderator_reregistration')
				if mail_template_id:
					self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
		# New Assessor Registration  and Assessor Re-registration
		if (self.is_assessors and not self.is_extension_of_scope) or (self.already_registered and self.existing_assessor_moderator == 'ex_assessor'):
			if self.is_assessors:
				group_data = group_obj.search(['|', ('name', '=', 'Portal'), ('name', '=', 'Assessors')])
				for data in group_data:
					tup1 = (4, data.id)
					mainlist.append(tup1)
				if not self.already_registered:
					assessor_seq_no = self.env['ir.sequence'].get('assessors.master.register')
					self.write({'temp_assessor_seq_no':assessor_seq_no})
				elif self.already_registered:
					assessors_obj = self.env['hr.employee'].search([('assessor_seq_no', '=', self.existing_assessor_number)])
					ase_lst = []
					for ase_obj in assessors_obj:
						ase_lst.append(ase_obj.id)
					assessor_obj = self.env['hr.employee'].search([('id', '=', max(ase_lst))])
					if assessor_obj:
						assessor_seq_no = assessor_obj.assessor_seq_no
						self.write({'temp_assessor_seq_no':assessor_seq_no})
			# Remove User from default Group
			contact_creation_group_data = group_obj.search(['|', ('name', '=', 'Contact Creation'), ('name', '=', 'Employee')])
			for data in contact_creation_group_data:
				tup1 = (3, data.id)
				mainlist.append(tup1)
			employee_obj = self.env['hr.employee']
			q_vals_line = []
			if self.qualification_evaluation_ids:
				for q_lines in self.qualification_evaluation_ids:
					if q_lines.verify == True:
						if q_lines.select:
							accreditation_qualification_line = []
							for lines in q_lines.qualification_line_evaluation:
								for data in lines:
									if data.selection:
										val = {
											 'name':data.name,
											 'type':data.type,
											 'id_no':data.id_no,
											 'title':data.title,
											 'level1':data.level1,
											 'level2':data.level2,
											 'level3': data.level3,
											 'selection':data.selection,
											}
										accreditation_qualification_line.append((0, 0, val))
							q_vals = {
										'qual_unit_type': q_lines.qual_unit_type,
										'qualification_hr_id':q_lines.qualification_evaluation_id.id,
										'saqa_qual_id':q_lines.saqa_qual_id,
										'qualification_line_hr':accreditation_qualification_line,
										'qualification_status':'approved',
										'approval_request':True,
										'request_send':True,
										}
							q_vals_line.append((0, 0, q_vals))
			password = ''.join(random.choice('admin') for _ in range(10))
			self.write({'password': password})
			gender_saqa_code = ''
			if self.gender == 'male':
				gender_saqa_code = 'm'
			elif self.gender == 'female':
				gender_saqa_code = 'f'
			citizen_status_saqa_code = ''
			if self.citizen_resident_status_code == 'sa':
				citizen_status_saqa_code = 'sa'
			elif self.citizen_resident_status_code == 'dual':
				citizen_status_saqa_code = 'd'
			elif self.citizen_resident_status_code == 'other':
				citizen_status_saqa_code = 'o'
			elif self.citizen_resident_status_code == 'PR':
				citizen_status_saqa_code = 'pr'
			elif self.citizen_resident_status_code == 'unknown':
				citizen_status_saqa_code = 'u'
			home_lang_saqa_code = ''
			if self.home_language_code == 1:
				home_lang_saqa_code = 'eng'
			elif self.home_language_code == 2:
				home_lang_saqa_code = 'zul'
			elif self.home_language_code == 3:
				home_lang_saqa_code = 'sep'
			elif self.home_language_code == 4:
				home_lang_saqa_code = 'tsh'
			elif self.home_language_code == 5:
				home_lang_saqa_code = 'ses'
			elif self.home_language_code == 6:
				home_lang_saqa_code = 'xit'
			elif self.home_language_code == 7:
				home_lang_saqa_code = 'oth'
			elif self.home_language_code == 8:
				home_lang_saqa_code = 'swa'
			elif self.home_language_code == 9:
				home_lang_saqa_code = 'u'
			elif self.home_language_code == 10:
				home_lang_saqa_code = 'nde'
			elif self.home_language_code == 11:
				home_lang_saqa_code = 'set'
			elif self.home_language_code == 12:
				home_lang_saqa_code = 'afr'
			elif self.home_language_code == 13:
				home_lang_saqa_code = 'xho'
			employee_data = employee_obj.create({
									 'name' : self.name,
									 'assessor_seq_no':assessor_seq_no,
									 'moderator_seq_no':moderator_seq_no,
									 'type':self.type,
									 'work_email' : self.work_email,
									 'work_phone' : self.work_phone,
									 'work_address' : self.work_address or False,
									 'work_address2' : self.work_address2,
									 'work_address3' : self.work_address3,
									 'work_location' : self.work_location,
									 'person_suburb' : self.person_suburb and  self.person_suburb.id,
									 'work_city' : self.work_city and self.work_city.id,
									 'work_province' : self.work_province and self.work_province.id,
									 'work_zip' : self.work_zip,
									 'work_country': self.work_country and self.work_country.id,
									 'department' : self.department or False,
									 'job_title' : self.job_title or False,
									 'manager' : self.manager or False,
									 'notes' : self.notes,
									 'person_title' : self.person_title,
									 'person_name' : self.person_name,
									 'dissability' : self.dissability,
									 'person_last_name' : self.person_last_name,
									 'cont_number_home' : self.cont_number_home,
									 'cont_number_office' : self.cont_number_office,
									 'person_cell_phone_number' : self.person_cell_phone_number,
									 'citizen_resident_status_code' : self.citizen_resident_status_code,
									 'citizen_status_saqa_code': citizen_status_saqa_code,
									 'country_id' : self.country_id and self.country_id.id or False,
									 'assessor_moderator_identification_id' : self.identification_id,
									 'person_birth_date' : self.person_birth_date,
									 'passport_id' : self.passport_id,
									 'national_id' : self.national_id,
									 'home_language_code' : self.home_language_code and self.home_language_code.id,
									 'home_lang_saqa_code':home_lang_saqa_code,
									 'gender' : self.gender,
									 'gender_saqa_code':gender_saqa_code,
									 'marital' : self.marital,
									 'person_home_address_1' : self.person_home_address_1,
									 'person_home_address_2' : self.person_home_address_2,
									 'person_home_address_3' : self.person_home_address_3,
									 'person_home_province_code': self.person_home_province_code and self.person_home_province_code.id,
									 'person_home_city' : self.person_home_city and self.person_home_city.id,
									 'person_home_suburb' : self.person_home_suburb and  self.person_home_suburb.id,
									 'person_home_zip' : self.person_home_zip,
									 'country_home': self.country_home and self.country_home.id,
									 'person_postal_address_1' : self.person_postal_address_1,
									 'person_postal_address_2' : self.person_postal_address_2,
									 'person_postal_address_3' : self.person_postal_address_3,
									 'person_postal_suburb' : self.person_postal_suburb and self.person_postal_suburb.id,
									 'person_postal_city' : self.person_postal_city and self.person_postal_city.id,
									 'person_postal_province_code': self.person_postal_province_code and self.person_postal_province_code.id,
									 'person_postal_zip': self.person_postal_zip,
									 'country_postal': self.country_postal and self.country_postal.id,
									 'dissability' : self.dissability,
									 'is_assessors':self.is_assessors,
									 'is_moderators':self.is_moderators,
									 'seta_elements':True,
									 'same_as_home':self.same_as_home,
									 'qualification_ids':q_vals_line,
									 'organisation':self.organisation.id,
									 'organisation_sdl_no':self.organisation_sdl_no,
									 'unknown_type':self.unknown_type,
									 'cv_document':self.cv_document and self.cv_document.id,
									 'unknown_type_document':self.unknown_type_document and self.unknown_type_document.id,
									 'id_document':self.id_document and self.id_document.id,
									 'registrationdoc':self.registrationdoc and self.registrationdoc.id,
									 'professionalbodydoc':self.professionalbodydoc and self.registrationdoc.id,
									 'sram_doc':self.sram_doc and self.sram_doc.id,
									 'password':self.password ,
									 'already_registered':self.already_registered,
								})
			employee_data.user_id.write({'groups_id':mainlist})
			self.write({'related_assessor_moderator':employee_data.id, 'state':'approved', 'approved':True, 'assessor_moderator_approval_date':datetime.today().date(), 'final_state':'Approved'})
#             etqe_conf = self.env['etqe.config'].search([])
#             new_date = "2018-03-31"
#             sdate = datetime.today().date()
#             if etqe_conf:
#                 etqe_brw = self.env['etqe.config'].browse(etqe_conf.id)
#                 effdate = datetime.strptime(etqe_brw.from_effective_date, '%Y-%m-%d').date()
#                 if  effdate <= datetime.today().date():
# #                     sdate = effdate
#                     if etqe_brw.etqa_end_date:
#                         new_date = sdate + relativedelta(years=etqe_brw.etqa_end_date)
			''' As per new configuration '''
			etqe_conf = self.env['etqe.config'].search([])
			sdate = datetime.today().date()
			new_date = "2020-03-31"
			if etqe_conf:
				etqe_brw = self.env['etqe.config'].browse(etqe_conf[0].id)
				if etqe_brw.etqa_end_date and etqe_brw.seta_license_end_date:
					seta_license_date = datetime.strptime(etqe_brw.seta_license_end_date, '%Y-%m-%d').date()
					new_date = sdate + relativedelta(years=etqe_brw.etqa_end_date)
					if new_date > seta_license_date:
						new_date = etqe_brw.seta_license_end_date

			employee_data.write({'start_date': sdate, 'end_date': new_date})
			self.write({'reg_start': self.assessor_moderator_approval_date})
			self.write({'reg_end': new_date})
			if not self.already_registered:
				mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_assessor_approved')
				if mail_template_id:
					self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
			if self.already_registered:
				mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_assessor_reregistration')
				if mail_template_id:
					self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
		# Assessor Extension of Scope
		elif self.is_extension_of_scope and self.existing_assessor_moderator == 'ex_assessor':
			if self.existing_assessor_number:
				employee_data = self.env['hr.employee'].search([('is_active_assessor','=',True),('is_assessors', '=', True), ('assessor_seq_no', '=', self.existing_assessor_number)])
			elif self.existing_assessor_id:
				employee_data = self.env['hr.employee'].search([('is_active_assessor','=',True),('is_assessors', '=', True), ('assessor_moderator_identification_id', '=', self.existing_assessor_id)])

			if self.is_assessors:
				group_data = group_obj.search(['|', ('name', '=', 'Portal'), ('name', '=', 'Assessors')])
				for data in group_data:
					tup1 = (4, data.id)
					mainlist.append(tup1)
				# assessor_seq_no = self.env['ir.sequence'].get('assessors.master.register')
			# Remove User from default Group
			contact_creation_group_data = group_obj.search(['|', ('name', '=', 'Contact Creation'), ('name', '=', 'Employee')])
			for data in contact_creation_group_data:
				tup1 = (3, data.id)
				mainlist.append(tup1)
			employee_obj = self.env['hr.employee']
			q_vals_line = []
			if self.qualification_evaluation_ids:
				for q_lines in self.qualification_evaluation_ids:
					if q_lines.verify == True:
						if q_lines.select:
							accreditation_qualification_line = []
							for lines in q_lines.qualification_line_evaluation:
								for data in  lines:
									if data.selection:
										val = {
											 'name':data.name,
											 'type':data.type,
											 'id_no':data.id_no,
											 'title':data.title,
											 'level1':data.level1,
											 'level2':data.level2,
											 'level3': data.level3,
											 'selection':data.selection,
											}
										accreditation_qualification_line.append((0, 0, val))
							q_vals = {
										'qual_unit_type': q_lines.qual_unit_type,
										'qualification_hr_id':q_lines.qualification_evaluation_id.id,
										'saqa_qual_id':q_lines.saqa_qual_id,
										'qualification_line_hr':accreditation_qualification_line,
										'qualification_status':'approved',
										'approval_request':True,
										'request_send':True,
										}
							q_vals_line.append((0, 0, q_vals))
			'''Below code is written to delete qualifications from Assessor master data before appending'''
			unlink_qual_list = []
			for ass_qual in employee_data.qualification_ids:
				for qual in self.qualification_evaluation_ids:
					if qual.verify:
						if ass_qual.qualification_hr_id == qual.qualification_evaluation_id:
						   unlink_qual_list.append((2, ass_qual.id))

			employee_data.write({'qualification_ids':unlink_qual_list})
			# Below line is commented
			#employee_data.write({'qualification_ids':[(2, assessor.id) for assessor in employee_data.qualification_ids]})
			employee_data.write({   'qualification_ids':q_vals_line,
									'name' : self.name,
									'type':self.type,
									'work_email' : self.work_email,
									'work_phone' : self.work_phone,
									'work_address' : self.work_address or False,
									'work_address2' : self.work_address2,
									'work_address3' : self.work_address3,
									'work_location' : self.work_location,
									'person_suburb' : self.person_suburb and  self.person_suburb.id,
									'work_city' : self.work_city and self.work_city.id,
									'work_province' : self.work_province and self.work_province.id,
									'work_zip' : self.work_zip,
									'work_country': self.work_country and self.work_country.id,
									'department' : self.department or False,
									'job_title' : self.job_title or False,
									'manager' : self.manager or False,
									'notes' : self.notes,
									'person_title' : self.person_title,
									'person_name' : self.person_name,
									'dissability' : self.dissability,
									'person_last_name' : self.person_last_name,
									'cont_number_home' : self.cont_number_home,
									'cont_number_office' : self.cont_number_office,
									'person_cell_phone_number' : self.person_cell_phone_number,
									'citizen_resident_status_code' : self.citizen_resident_status_code,
									'country_id' : self.country_id and self.country_id.id or False,
									'assessor_moderator_identification_id' : self.identification_id,
									'person_birth_date' : self.person_birth_date,
									'passport_id' : self.passport_id,
									'national_id' : self.national_id,
									'home_language_code' : self.home_language_code and self.home_language_code.id,
									'marital' : self.marital,
									'person_home_address_1' : self.person_home_address_1,
									'person_home_address_2' : self.person_home_address_2,
									'person_home_address_3' : self.person_home_address_3,
									'person_home_province_code': self.person_home_province_code and self.person_home_province_code.id,
									'person_home_city' : self.person_home_city and self.person_home_city.id,
									'person_home_suburb' : self.person_home_suburb and  self.person_home_suburb.id,
									'person_home_zip' : self.person_home_zip,
									'country_home': self.country_home and self.country_home.id,
									'person_postal_address_1' : self.person_postal_address_1,
									'person_postal_address_2' : self.person_postal_address_2,
									'person_postal_address_3' : self.person_postal_address_3,
									'person_postal_suburb' : self.person_postal_suburb and self.person_postal_suburb.id,
									'person_postal_city' : self.person_postal_city and self.person_postal_city.id,
									'person_postal_province_code': self.person_postal_province_code and self.person_postal_province_code.id,
									'person_postal_zip': self.person_postal_zip,
									'country_postal': self.country_postal and self.country_postal.id,
									'dissability' : self.dissability,
									'seta_elements':True,
									'same_as_home':self.same_as_home,
									'organisation':self.organisation.id,
									'organisation_sdl_no':self.organisation_sdl_no,
									'unknown_type':self.unknown_type,
									'cv_document':self.cv_document and self.cv_document.id,
									'unknown_type_document':self.unknown_type_document and self.unknown_type_document.id,
									'id_document':self.id_document and self.id_document.id,
									'registrationdoc':self.registrationdoc and self.registrationdoc.id,
									'professionalbodydoc':self.professionalbodydoc and self.registrationdoc.id,
									'sram_doc':self.sram_doc and self.sram_doc.id,
								 })
			password = ''.join(random.choice('admin') for _ in range(10))
			self.write({'password':password})
			employee_data.user_id.write({'groups_id':mainlist})
			self.write({'state':'approved', 'approved':True, 'assessor_moderator_approval_date':datetime.today().date(), 'final_state':'Approved'})
			assessor_obj = self.env['hr.employee'].search([('is_active_assessor','=',True),('is_assessors', '=', True),('assessor_seq_no', '=', self.existing_assessor_number)])
			assessor_seq_no = assessor_obj.assessor_seq_no
			self.write({'temp_assessor_seq_no':assessor_seq_no})
			self.write({'reg_start': assessor_obj.start_date})
			self.write({'reg_end': assessor_obj.end_date})
			# Sending Mail
			mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_assessor_eos')
			if mail_template_id:
				self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
#             if self.already_registered:
#                 etqe_conf = self.env['etqe.config'].search([])
#                 if etqe_conf:
#                     new_date = "2018-03-31"
#                     etqe_brw = self.env['etqe.config'].browse(etqe_conf.id)
#                     effdate = datetime.strptime(etqe_brw.from_effective_date, '%Y-%m-%d').date()
#                     sdate = datetime.today().date()
#                     if  effdate <= datetime.today().date():
#     #                     sdate = effdate
#                         if etqe_brw.etqa_end_date:
#                             new_date = sdate + relativedelta(years=etqe_brw.etqa_end_date)
#                     employee_data.write({'start_date':sdate, 'end_date':new_date})

#         att_obj = self.env['ir.attachment']
#         attachment_ids = []
#         if self.is_assessors:
#             mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_assessor_approved')
#             if mail_template_id:
#                 self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
#         if self.is_moderators:
#             mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_moderator_approved')
#             if mail_template_id:
#                 self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
		return True

	@api.multi
	def write(self, vals):
		context = self._context
		if context is None:
			context = {}
		res = super(assessors_moderators_register, self).write(vals)
		if vals.get('identification_id'):
			if len(vals.get('identification_id')) < 13:
				raise Warning(_("Please enter 13 digits Identification No.!!"))
		if context.get('submit') == True:
			pass

#         if self.state == "pending" and self.submitted == False:
#             raise Warning(_('Sorry! you can not change status to Pending first submit application.'))
#
#         if self.state == "verification" and self.verify == False:
#             raise Warning(_('Sorry! you can not change status to verification first verify application.'))

		if self.state == "verification" and self.submitted == False:
			raise Warning(_('Sorry! you can not change status to verification first submit application.'))

		if self.state == "evaluation" and self.verify == False:
			raise Warning(_('Sorry! you can not change status to evaluation first verify application.'))

		if self.state == "approved" and self.evaluate == False:
			raise Warning(_('Sorry! you can not change status to approve first evaluate application.'))

#         if self.state == "denied" and self.evaluate == False:
#             raise Warning(_('Sorry! you can not change status to reject first evaluate application.'))

		if self.state == "approved" and self.denied == True:
			raise Warning(_('Sorry! you can not change status to Approved.'))

		if self.state == "approved" and self.approved == False:
			raise Warning(_('Sorry! you can not change status to Approved first Approve application.'))

		if self.state == "denied" and self.approved == True:
			raise Warning(_('Sorry! you can not change status to Rejected.'))

		if self.state == "denied" and self.denied == False:
			raise Warning(_('Sorry! you can not change status to Rejected first Reject application..'))

#        if self.state == "qualification_info" and self.submitted == True:
#            raise Warning(_('Sorry! you can not submit again. '))
#         elif self.submitted and not context.get('state') in ['approved','denied']:
#             raise Warning(_('Sorry! you can not change status once form is submitted.'))
		#This Warning is given on submit button
		# validate minimum credits
#         if not self.assessor_id and not self.already_registered and not self.is_extension_of_scope:
#             for line in self.qualification_ids:
#                 if line.minimum_credits > line.total_credits:
#                     raise Warning(_("Sum of checked unit standards credits point should be greater than or equal to Minimum credits point !!"))
		return res

	@api.model
	def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
		user = self._uid
		user_data = self.env['res.users'].browse(user)
		if user != 1 and user_data.assessor_moderator_id:
			ass_mod_ids = []
			self._cr.execute("select id from assessors_moderators_register where create_uid='%s'" % (user_data.id,))
			ass_mod_ids = map(lambda x:x[0], self._cr.fetchall())
			args.append(('id', 'in', ass_mod_ids))
#             employee_data = self.env['hr.employee'].search([('user_id', '=', user)])
#             args.append(('related_assessor_moderator', '=', user_data.assessor_moderator_id.id))
			return super(assessors_moderators_register, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		return super(assessors_moderators_register, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

	@api.multi
	def copy(self):
		''' Inherited to avoid duplicating records '''
		raise Warning(_('Sorry! You cannot create duplicate record'))
		return super(assessors_moderators_register, self).copy()

	@api.multi
	def unlink(self):
		''' Inherited to restrict deleting records '''
		raise Warning(_('Sorry! You cannot delete record'))
		return super(assessors_moderators_register, self).unlink()
assessors_moderators_register()

class provider_contact(models.Model):
	_name = 'provider.contact'
	_description = 'Provider Contact'

	provider_contact_id = fields.Many2one('res.partner', 'Res Partner', required=True, ondelete='cascade', select=True)
	name = fields.Char(string='Name', required=True)
	street = fields.Char(string='Street')
	street2 = fields.Char(string='Street2')
	zip = fields.Char(string='Zip', size=24, change_default=True)
	city = fields.Char(string='City')
	state_id = fields.Many2one("res.country.state", 'Province', ondelete='restrict')
	country_id = fields.Many2one('res.country', 'Country', ondelete='restrict')
	email = fields.Char(string='Email')
	phone = fields.Char(string='Phone', size=10)
	mobile = fields.Char(string='Mobile', size=10)
	image = fields.Binary(string="Image",
			help="This field holds the image used as avatar for this contact, limited to 1024x1024px")
	status = fields.Char(string='Status')
	fax = fields.Char(string='Fax',size=10)
	designation = fields.Char(string='Designation')
provider_contact()

class provider_qualification_line_partner(models.Model):
	_name = 'provider.qualification.line.partner'
	_description = 'Provider Qalification Line For partner'

	name = fields.Char(string='Name')
#     type = fields.Char(string='Type')
	type = fields.Selection([
	('Core', 'Core'),
	('Fundamental', 'Fundamental'),
	('Elective', 'Elective'),
	('Knowledge Module', 'Knowledge Module'),
	('Practical Skill Module', 'Practical Skill Module'),
	('Work Experience Module', 'Work Experience Module'),
	('Exit Level Outcomes', 'Exit Level Outcomes'),
	], string='Type', track_visibility='onchange')
	id_data = fields.Char(string='ID')
	title = fields.Char(string='UNIT STANDARD TITLE')
	level1 = fields.Char(string='PRE-2009 NQF LEVEL')
	level2 = fields.Char(string='NQF LEVEL')
	level3 = fields.Char(string='CREDITS')
	line_id = fields.Many2one('res.partner', 'Res Partner', ondelete='cascade')
	state = fields.Selection([('new', 'New'), ('done', 'Done')], string="status")
provider_qualification_line_partner()

class provider_master_qualification_line(models.Model):
	_name = 'provider.master.qualification.line'
	_description = 'Provider Master Qualification Line'

	name = fields.Char(string='Name')
#     type = fields.Char(string='Type')
	type = fields.Selection([
	('Core', 'Core'),
	('Fundamental', 'Fundamental'),
	('Elective', 'Elective'),
	('Knowledge Module', 'Knowledge Module'),
	('Practical Skill Module', 'Practical Skill Module'),
	('Work Experience Module', 'Work Experience Module'),
	('Exit Level Outcomes', 'Exit Level Outcomes'),
	], string='Type', track_visibility='onchange')
	id_data = fields.Char(string='ID')
	title = fields.Char(string='UNIT STANDARD TITLE')
	level1 = fields.Char(string='PRE-2009 NQF LEVEL')
	level2 = fields.Char(string='NQF LEVEL')
	level3 = fields.Char(string='CREDITS')
	selection = fields.Boolean(string="SELECTION")
	is_seta_approved = fields.Boolean(
		string='SETA Learning Material', track_visibility='onchange')
	is_provider_approved = fields.Boolean(
		string='PROVIDER Learning Material', track_visibility='onchange')
	line_id = fields.Many2one('provider.master.qualification', 'Provider Master Reference')

	@api.depends('is_provider_approved')
	@api.onchange('selection')
	def onchange_selection(self):
		if self.selection and self.is_provider_approved:
			raise Warning('Note that the Electives choosen must have HWSETA approved report!!!')
provider_master_qualification_line()

class provider_master_qualification(models.Model):
	_name = 'provider.master.qualification'
	_description = 'Master  Qualification'

	qualification_id = fields.Many2one("provider.qualification", 'Qualification')
	qualification_line = fields.One2many('provider.master.qualification.line', 'line_id', 'Qualification Lines')
	accreditation_qualification_id = fields.Many2one('res.partner', 'Provider Accreditation Reference')
	saqa_qual_id = fields.Char(string='ID')
	status = fields.Selection([('draft', 'Draft'), ('waiting_approval', 'Waiting Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], string="Status", default='draft')
	request_send = fields.Boolean(string='Send Request', default=False)
	approval_request = fields.Boolean(string='Approval Request', default=False)
	reject_request = fields.Boolean(string="Reject Request", default=False)
	assessors_id = fields.Many2one("hr.employee", string='Assessor', domain=[('is_active_assessor','=',True),('is_assessors', '=', True)])
	assessor_sla_document = fields.Many2one('ir.attachment', string="SLA Document")
	moderators_id = fields.Many2one("hr.employee", string='Moderator', domain=[('is_active_moderator','=',True),('is_moderators', '=', True)])
	moderator_sla_document = fields.Many2one('ir.attachment', string="SLA Document")
	assessor_no = fields.Char(string = "Assessor ID")
	moderator_no = fields.Char(string = "Moderator ID")

	@api.one
	def unlink(self):
		self.qualification_line.unlink()
		res = super(provider_master_qualification, self).unlink()
		return res

	@api.multi
	def onchange_qualification(self, qualification_id):
#         res = {}
		accreditation_qualification_line = []
		if qualification_id:
			qualification_obj = self.env['provider.qualification'].browse(qualification_id)
			for qualification_lines in qualification_obj.qualification_line:
				if qualification_lines.type == 'Core' or qualification_lines.type == 'Fundamental':
					val = {
							 'name':qualification_lines.name,
							 'type':qualification_lines.type,
							 'id_data':qualification_lines.id_no,
							 'title':qualification_lines.title,
							 'level1':qualification_lines.level1,
							 'level2':qualification_lines.level2,
							 'level3': qualification_lines.level3,
							 'selection':True,
							}
				elif qualification_lines.type == 'Elective':
					val = {
							 'name':qualification_lines.name,
							 'type':qualification_lines.type,
							 'id_data':qualification_lines.id_no,
							 'title':qualification_lines.title,
							 'level1':qualification_lines.level1,
							 'level2':qualification_lines.level2,
							 'level3': qualification_lines.level3,
							 'is_seta_approved':qualification_lines.is_seta_approved,
							 'is_provider_approved':qualification_lines.is_provider_approved,
#                              'selection':True,
							}
					if qualification_lines.is_seta_approved:
							val.update({
										 'selection':True,
										})
				else:
					val = {
							 'name':qualification_lines.name,
							 'type':qualification_lines.type,
							 'id_data':qualification_lines.id_no,
							 'title':qualification_lines.title,
							 'level1':qualification_lines.level1,
							 'level2':qualification_lines.level2,
							 'level3': qualification_lines.level3,
							}
				accreditation_qualification_line.append((0, 0, val))
			return {'value':{'qualification_line':accreditation_qualification_line, 'saqa_qual_id':qualification_obj.saqa_qual_id, 'status':'draft'}}
		return {}

	@api.multi
	def action_send_request(self):
		self.write({'status':'waiting_approval', 'request_send':True})

	@api.multi
	def action_approved_request(self):
		self.write({'status':'approved', 'approval_request':True})

	@api.multi
	def action_rejected_request(self):
		self.write({'status':'rejected', 'reject_request':True})
		# Mail notification Organisation
#         ir_model_data_obj = self.env['ir.model.data']
#         mail_template_id = ir_model_data_obj.get_object_reference('hwseta_sdp', 'email_template_sdf_register_organisation_post_submit')
#         if mail_template_id:
#             self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True,context=self.env.context)

		return True
provider_master_qualification()

class etqe_assessors_provider_campus_rel(models.Model):
	_name = 'etqe.assessors.provider.campus.rel'

	assessors_id = fields.Many2one("hr.employee", 'Assessors', domain=[('is_active_assessor','=',True),('is_assessors', '=', True)] , ondelete='restrict')
	provider_campus_id = fields.Many2one('res.partner', ondelete='cascade')
	awork_phone = fields.Char('Work Phone', readonly=False)
	awork_email = fields.Char('Work Email', size=240)
	campus_assessor_sla_document = fields.Many2one('ir.attachment', string="SLA Document")
	assessor_notification_letter = fields.Many2one('ir.attachment', string="Notification Letter")

	@api.multi
	def onchange_assessrs(self, assessors_id):

		if assessors_id:
			assessors_obj = self.env['hr.employee'].browse(assessors_id)
			return {'value':{'awork_email':assessors_obj.work_email, 'awork_phone':assessors_obj.work_phone}}
		else:
			return {}
etqe_assessors_provider_campus_rel()

class etqe_moderators_provider_campus_rel(models.Model):
	_name = 'etqe.moderators.provider.campus.rel'

	moderators_id = fields.Many2one("hr.employee", 'Moderator', domain=[('is_active_moderator','=',True),('is_moderators', '=', True)], ondelete='restrict')
	provider_campus_id = fields.Many2one('res.partner', ondelete='cascade')
	mwork_phone = fields.Char('Work Phone', readonly=False, size=10)
	mwork_email = fields.Char('Work Email', size=240)
	campus_moderator_sla_document = fields.Many2one('ir.attachment', string="SLA Document")
	moderator_notification_letter = fields.Many2one('ir.attachment', string="Notification Letter")

	@api.multi
	def onchange_moderators(self, moderators_id):

		if moderators_id:
			moderators_obj = self.env['hr.employee'].browse(moderators_id)
			return {'value':{'mwork_email':moderators_obj.work_email, 'mwork_phone':moderators_obj.work_phone}}
		else:
			return {}
etqe_moderators_provider_campus_rel()


class provider_master_campus_qualification_line(models.Model):
	_name = 'provider.master.campus.qualification.line'
	_description = 'Provider Master Campus Qualification Line'

	name = fields.Char(string='Name')
#     type = fields.Char(string='Type')
	type = fields.Selection([
	('Core', 'Core'),
	('Fundamental', 'Fundamental'),
	('Elective', 'Elective'),
	('Knowledge Module', 'Knowledge Module'),
	('Practical Skill Module', 'Practical Skill Module'),
	('Work Experience Module', 'Work Experience Module'),
	('Exit Level Outcomes', 'Exit Level Outcomes'),
	], string='Type', track_visibility='onchange')
	id_data = fields.Char(string='ID')
	title = fields.Char(string='UNIT STANDARD TITLE')
	level1 = fields.Char(string='PRE-2009 NQF LEVEL')
	level2 = fields.Char(string='NQF LEVEL')
	level3 = fields.Char(string='CREDITS')
	selection = fields.Boolean(string="SELECTION")
	is_seta_approved = fields.Boolean(
		string='SETA Learning Material', track_visibility='onchange')
	is_provider_approved = fields.Boolean(
		string='PROVIDER Learning Material', track_visibility='onchange')
	line_id = fields.Many2one('provider.master.campus.qualification', 'Provider Master Reference', required=True)
provider_master_campus_qualification_line()


class provider_master_campus_qualification(models.Model):
	_name = 'provider.master.campus.qualification'
	_description = 'Accreditation  Qualification'

	qualification_id = fields.Many2one("provider.qualification", 'Qualification', ondelete='restrict')
	qualification_line = fields.One2many('provider.master.campus.qualification.line', 'line_id', 'Qualification Lines')
	accreditation_qualification_campus_id = fields.Many2one('res.partner', 'Provider Accreditation Reference')
	saqa_qual_id = fields.Char("SAQA Qualification ID")
	assessors_id = fields.Many2one("hr.employee", string='Assessor', domain=[('is_active_assessor','=',True),('is_assessors', '=', True)])
	assessor_sla_document = fields.Many2one('ir.attachment', string="SLA Document")
	moderators_id = fields.Many2one("hr.employee", string='Moderator', domain=[('is_active_moderator','=',True),('is_moderators', '=', True)])
	moderator_sla_document = fields.Many2one('ir.attachment', string="SLA Document")
	@api.multi
	def onchange_qualification(self, qualification_id):
		accreditation_qualification_line = []
		if qualification_id:
			qualification_obj = self.env['provider.qualification'].browse(qualification_id)
			for qualification_lines in qualification_obj.qualification_line:
				val = {
						 'name':qualification_lines.name,
						 'type':qualification_lines.type,
						 'id_no':qualification_lines.id_no,
						 'title':qualification_lines.title,
						 'level1':qualification_lines.level1,
						 'level2':qualification_lines.level2,
						 'level3': qualification_lines.level3,
						 'is_seta_approved':qualification_lines.is_seta_approved,
						 'is_provider_approved':qualification_lines.is_provider_approved,
						}
				accreditation_qualification_line.append((0, 0, val))

			return {'value':{'qualification_line':accreditation_qualification_line, 'saqa_qual_id':qualification_obj.saqa_qual_id}}
		return {}
provider_master_campus_qualification()


class skills_programme_unit_standards_master_rel(models.Model):
	_name = 'skills.programme.unit.standards.master.rel'
	_description = 'Skills Programme Unit Standards Master Rel'
	_rec_name = 'type'

	name = fields.Char(string='Name')
#     type = fields.Char(string='Type', required=True)
	type = fields.Selection([
	('Core', 'Core'),
	('Fundamental', 'Fundamental'),
	('Elective', 'Elective'),
	('Knowledge Module', 'Knowledge Module'),
	('Practical Skill Module', 'Practical Skill Module'),
	('Work Experience Module', 'Work Experience Module'),
	('Exit Level Outcomes', 'Exit Level Outcomes'),
	], string='Type', track_visibility='onchange')
	id_no = fields.Char(string='ID NO')
	title = fields.Char(string='UNIT STANDARD TITLE', required=True)
	level1 = fields.Char(string='PRE-2009 NQF LEVEL')
	level2 = fields.Char(string='NQF LEVEL')
	level3 = fields.Char(string='CREDITS')
	selection = fields.Boolean(string='SELECT')
	skills_programme_id = fields.Many2one('skills.programme.master.rel', 'Skills Programme Reference', ondelete='cascade')
skills_programme_unit_standards_master_rel()

class skills_programme_master_rel(models.Model):
	_name = 'skills.programme.master.rel'
	_description = 'Skills Programme master Rel'

	skills_programme_id = fields.Many2one("skills.programme", 'Skills Programme')
	unit_standards_line = fields.One2many('skills.programme.unit.standards.master.rel', 'skills_programme_id', 'Unit Standards')
	skills_programme_partner_rel_id = fields.Many2one('res.partner', 'Provider Partner Reference')
	skill_saqa_id = fields.Char("SAQA QUAL ID")
	status = fields.Selection([('draft', 'Draft'), ('waiting_approval', 'Waiting Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], string="Status", default='draft')
	request_send = fields.Boolean(string='Send Request', default=False)
	approval_request = fields.Boolean(string='Approval Request', default=False)
	reject_request = fields.Boolean(string="Reject Request", default=False)
	assessors_id = fields.Many2one("hr.employee", string='Assessor', domain=[('is_active_assessor','=',True),('is_assessors', '=', True)])
	assessor_sla_document = fields.Many2one('ir.attachment', string="SLA Document")
	moderators_id = fields.Many2one("hr.employee", string='Moderator', domain=[('is_active_moderator','=',True),('is_moderators', '=', True)])
	moderator_sla_document = fields.Many2one('ir.attachment', string="SLA Document")
	assessor_no = fields.Char(string = "Assessor ID")
	moderator_no = fields.Char(string = "Moderator ID")

	@api.multi
	def action_send_request(self):
		self.write({'status':'waiting_approval', 'request_send':True})

	@api.multi
	def action_approved_request(self):
		self.write({'status':'approved', 'approval_request':True})

	@api.multi
	def action_rejected_request(self):
		self.write({'status':'rejected', 'reject_request':True})

	@api.multi
	def onchange_skills_programme(self, skills_programme_id):
#         res = {}
		unit_standards = []
		if skills_programme_id:
			skills_programme_obj = self.env['skills.programme'].browse(skills_programme_id)
			for unit_standards_lines in skills_programme_obj.unit_standards_line:
				if unit_standards_lines.selection == True:
					val = {
							 'name':unit_standards_lines.name,
							 'type':unit_standards_lines.type,
							 'id_no':unit_standards_lines.id_no,
							 'title':unit_standards_lines.title,
							 'level1':unit_standards_lines.level1,
							 'level2':unit_standards_lines.level2,
							 'level3': unit_standards_lines.level3,
							 'selection':True,
							}
					unit_standards.append((0, 0, val))
			return {'value':{'unit_standards_line':unit_standards, 'skill_saqa_id':skills_programme_obj.saqa_qual_id}}
		return {}
skills_programme_master_rel()

class skills_programme_unit_standards_master_campus_rel(models.Model):
	_name = 'skills.programme.unit.standards.master.campus.rel'
	_description = 'Skills Programme Unit Standards Master Campus Rel'
	_rec_name = 'type'
	name = fields.Char(string='Name')
	type = fields.Char(string='Type', required=True)
	id_no = fields.Char(string='ID NO')
	title = fields.Char(string='UNIT STANDARD TITLE', required=True)
	level1 = fields.Char(string='PRE-2009 NQF LEVEL')
	level2 = fields.Char(string='NQF LEVEL')
	level3 = fields.Char(string='CREDITS')
	selection = fields.Boolean(string='SELECT')
	skills_programme_id = fields.Many2one('skills.programme.master.campus.rel', 'Skills Programme Reference', ondelete='cascade')
skills_programme_unit_standards_master_campus_rel()

class skills_programme_master_campus_rel(models.Model):
	_name = 'skills.programme.master.campus.rel'
	_description = 'Skills Programme Master Campus Rel'

	skills_programme_id = fields.Many2one("skills.programme", 'Skills Programme')
	unit_standards_line = fields.One2many('skills.programme.unit.standards.master.campus.rel', 'skills_programme_id', 'Unit Standards')
	skills_programme_partner_campus_rel_id = fields.Many2one('res.partner', 'Provider Accreditation Reference')
	skill_saqa_id = fields.Char("SAQA QUAL ID")

	@api.multi
	def onchange_skills_programme(self, skills_programme_id):
		unit_standards = []
		if skills_programme_id:
			skills_programme_obj = self.env['skills.programme'].browse(skills_programme_id)
			for unit_standards_lines in skills_programme_obj.unit_standards_line:
				if unit_standards_lines.selection == True:
					val = {
							 'name':unit_standards_lines.name,
							 'type':unit_standards_lines.type,
							 'id_no':unit_standards_lines.id_no,
							 'title':unit_standards_lines.title,
							 'level1':unit_standards_lines.level1,
							 'level2':unit_standards_lines.level2,
							 'level3': unit_standards_lines.level3,
							 'selection':True,
							}
					unit_standards.append((0, 0, val))
			return {'value':{'unit_standards_line':unit_standards, 'skill_saqa_id':skills_programme_obj.saqa_qual_id}}
		return {}
skills_programme_master_campus_rel()

class provider_master_contact(models.Model):
	_name = 'provider.master.contact'
	_description = 'Provider Master Contact'

	provider_master_contact_id = fields.Many2one('res.partner', 'Provider Contact', required=True, ondelete='cascade', select=True)
	name = fields.Char(string='Name', required=True)
	street = fields.Char(string='Street')
	street2 = fields.Char(string='Street2')
	zip = fields.Char(string='Zip', size=24, change_default=True)
	city = fields.Char(string='City')
	state_id = fields.Many2one("res.country.state", 'Province', ondelete='restrict')
	country_id = fields.Many2one('res.country', 'Country', ondelete='restrict')
	email = fields.Char(string='Email')
	phone = fields.Char(string='Phone', size=10)
	mobile = fields.Char(string='Mobile', size=10)
	image = fields.Binary(string="Image",
			help="This field holds the image used as avatar for this contact, limited to 1024x1024px")
	status = fields.Char(string='Status')
	fax = fields.Char(string='Fax',size=10)
	designation = fields.Char(string='Designation')
	sur_name = fields.Char(string='Surname', required=True)
provider_master_contact()

class res_partner(models.Model):
	_inherit = 'res.partner'

	@api.model
	def default_get(self, fields):
		''' To get Qualifications/Skills/Learning Programme/Assessors/Moderators from Main campus'''
		context = self._context
		if context is None:
			context = {}
		res = super(res_partner, self).default_get(fields)

		qualification_obj_ids = context.get('default_qualification_id', False)
		skills_obj_ids = context.get('default_skills_id', False)
		learning_programme_obj_ids = context.get('default_learning_programme_id', False)
		assessors_obj_ids = context.get('default_assessors_ids', False)
		moderators_obj_ids = context.get('default_moderators_ids', False)

		q_vals_line, s_vals_line,lp_vals_line, a_vals_line, m_vals_line = [], [], [], [], []
		if qualification_obj_ids:
			for qualification_obj in qualification_obj_ids:
				qualification = self.env['provider.master.qualification'].browse(qualification_obj[1])
				accreditation_qualification_line = []
				for qualification_line_data in qualification.qualification_line:
					for data in qualification_line_data:
						if data.selection:
							val = {
								 'name':data.name,
								 'type':data.type,
								 'id_no':data.id_data,
								 'title':data.title,
								 'level1':data.level1,
								 'level2':data.level2,
								 'level3': data.level3,
								 'is_provider_approved': data.is_provider_approved,
								 'is_seta_approved': data.is_seta_approved,
								 'selection':data.selection
								}
							accreditation_qualification_line.append((0, 0, val))
				q_vals = {
							'qualification_id':qualification.qualification_id.id,
							'qualification_line':accreditation_qualification_line,
							'saqa_qual_id':qualification.saqa_qual_id,
							'assessors_id':qualification.assessors_id.id,
							'moderators_id':qualification.moderators_id.id,
							'assessor_sla_document':qualification.assessor_sla_document.id,
							'moderator_sla_document':qualification.moderator_sla_document.id,
							}
				q_vals_line.append((0, 0, q_vals))

				res.update(qualification_campus_ids = q_vals_line)

		if skills_obj_ids:
			for skills_obj in skills_obj_ids:
				skills = self.env['skills.programme.master.rel'].browse(skills_obj[1])
				skills_line = []
				for skills_line_data in skills.unit_standards_line:
					for data in skills_line_data:
						if data.selection:
							val = {
								 'name':data.name,
								 'type':data.type,
								 'id_no':data.id_no,
								 'title':data.title,
								 'level1':data.level1,
								 'level2':data.level2,
								 'level3': data.level3,
								 'selection':data.selection
								}
							skills_line.append((0, 0, val))
				skills_vals = {
							'skills_programme_id':skills.skills_programme_id.id,
							'unit_standards_line':skills_line,
							'skill_saqa_id':skills.skill_saqa_id,
							}
				s_vals_line.append((0, 0, skills_vals))

				res.update(skills_programme_campus_ids = s_vals_line)

		if learning_programme_obj_ids:
			for lp_obj in learning_programme_obj_ids:
				lp = self.env['learning.programme.master.rel'].browse(lp_obj[1])
				lp_line = []
				for lp_line_data in lp.unit_standards_line:
					for data in lp_line_data:
						if data.selection:
							val = {
								 'name':data.name,
								 'type':data.type,
								 'id_no':data.id_no,
								 'title':data.title,
								 'level1':data.level1,
								 'level2':data.level2,
								 'level3': data.level3,
								 'provider_approved_lp': data.provider_approved_lp,
								 'seta_approved_lp': data.seta_approved_lp,
								 'selection':data.selection
								}
							lp_line.append((0, 0, val))
				lp_vals = {
							'learning_programme_id':lp.learning_programme_id.id,
							'unit_standards_line':lp_line,
							'lp_saqa_id':lp.lp_saqa_id,
							}
				lp_vals_line.append((0, 0, lp_vals))
				res.update(learning_programme_campus_ids = lp_vals_line)
		if assessors_obj_ids:
			for assessors_obj in assessors_obj_ids:
				assessor = self.env['etqe.assessors.provider.rel'].browse(assessors_obj[1])
				assessor_vals = {
							'assessors_id':assessor.assessors_id.id,
							'awork_email':assessor.awork_email,
							'awork_phone':assessor.awork_phone,
							'campus_assessor_sla_document':assessor.assessor_sla_document.id,
							'assessor_notification_letter':assessor.assessor_notification_letter.id,
							}
				a_vals_line.append((0, 0, assessor_vals))

				res.update(assessors_campus_ids=a_vals_line)

		if moderators_obj_ids:
			for moderators_obj in moderators_obj_ids:
				moderator = self.env['etqe.moderators.provider.rel'].browse(moderators_obj[1])
				moderator_vals = {
							'moderators_id':moderator.moderators_id.id,
							'mwork_email':moderator.mwork_email,
							'mwork_phone':moderator.mwork_phone,
							'campus_moderator_sla_document':moderator.moderator_sla_document.id,
							'moderator_notification_letter':moderator.moderator_notification_letter.id,
							}
				m_vals_line.append((0, 0, moderator_vals))
				res.update(moderators_campus_ids=m_vals_line)
		return res

	@api.v7
	def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
		res = models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
		if view_type == 'form':
			doc = etree.XML(res['arch'])
			for sheet in doc.xpath("//sheet"):
				parent = sheet.getparent()
				index = parent.index(sheet)
				for child in sheet:
					parent.insert(index, child)
					index += 1
				parent.remove(sheet)
			res['arch'] = etree.tostring(doc)
		return res

	is_active_provider = fields.Boolean("Active", default=True)
	is_existing_provider = fields.Boolean("Existing Provider", default=False)
	is_visible = fields.Boolean("Visible", default=False)
	phone = fields.Char(String="Phone", size=10)
	mobile = fields.Char(String="Mobile", size=10)
	provider_contact_ids = fields.One2many('provider.contact', 'provider_contact_id', 'Provider Contact')
	qualification_line = fields.One2many('provider.qualification.line.partner', 'line_id', 'Qualification Lines', readonly=True)
	qualification_id = fields.Many2one("provider.qualification", 'Qualification')
	assessors_ids = fields.One2many('etqe.assessors.provider.rel', 'provider_id', 'Assessors')
	moderators_ids = fields.One2many('etqe.moderators.provider.rel', 'provider_id', 'Moderators')
	assessors_campus_ids = fields.One2many('etqe.assessors.provider.campus.rel', 'provider_campus_id', 'Assessors')
	moderators_campus_ids = fields.One2many('etqe.moderators.provider.campus.rel', 'provider_campus_id', 'Moderators')
	assess_pro_id = fields.Many2one('hr.employee', string='Assessment')
	state = fields.Selection([('new', 'New'), ('done', 'Done')], string="status", track_visibility='onchange')
	provider_sic_code = fields.Char(string='SIC Code', help="SIC_Code", track_visibility='onchange', size=50)
	#     General Business Information part1
	txtRegName = fields.Char(string='Organisation Registered Name', track_visibility='onchange', size=240)
	txtTradeName = fields.Char(string='Organisation Trading Name', track_visibility='onchange', size=240)
	txtAbbrTradeName = fields.Char(string='Organisation Abbreviated Trading Name', track_visibility='onchange', size=240)
	cboOrgLegalStatus = fields.Many2one("hwseta.organisation.legal.status", string='Organisation Legal Status', track_visibility='onchange', ondelete='restrict')
	txtCompanyRegNo = fields.Char(string='Company Registration Number', track_visibility='onchange', size=240)
	txtVATRegNo = fields.Char(string='VAT Number', track_visibility='onchange', size=240)
	# cboOrgSICCode = fields.Many2one("hwseta.sic.master", string='SIC Code', track_visibility='onchange', ondelete='restrict')
	cboOrgSICCode = fields.Char(string='SIC Code', track_visibility='onchange', ondelete='restrict')
	txtSDLNo = fields.Char(string='SARS / SD Levy Number', track_visibility='onchange', size=240)
	cboTHETAChamberSelect = fields.Many2one("hwseta.chamber.master", string='HWSETA Chamber', track_visibility='onchange', ondelete='restrict')
	cboProviderFocus = fields.Many2one("hwseta.provider.focus.master", string='Provider Focus', track_visibility='onchange', ondelete='restrict')
	txtNumYearsCurrentBusiness = fields.Selection([
		   ('0', '0'),
		   ('1', '1'),
		   ('2', '2'),
		   ('3', '3'),
		   ('4', '4'),
		   ('5', '5'),
		   ('6', '6'),
		   ('7', '7'),
		   ('8', '8'),
		   ('9', '9'),
		   ('10', '10'),
		   ('10+', '10+'),
		], string='Years in Business', track_visibility='onchange', size=240)
	txtNumStaffMembers = fields.Char(string='Number of full time staff members', track_visibility='onchange', size=240)
	#     General Site Information part2
	optYesNo = fields.Boolean('Has the organisation ever applied to another SETA or ETQA for accreditation?')
	cboSETA = fields.Many2one("hwseta.master", string='If yes, please indicate which SETA or ETQA:', track_visibility='onchange', ondelete='restrict')
	txtStateAccNumber = fields.Char(string='State Accreditation number', track_visibility='onchange', size=240)
	optAccStatus = fields.Char(string='D2 Accreditation Status', track_visibility='onchange', size=240)
	StatusReason = fields.Char(string='D3 Status Reason', track_visibility='onchange', size=240)
	txtTags = fields.Char(string='Tags', track_visibility='onchange', size=240)
	txtWorkEmail = fields.Char(string='WorkEmail', track_visibility='onchange', size=240)
	txtWorkPhone = fields.Char(string='WorkPhone', track_visibility='onchange', size=10)
	SICCode = fields.Char(string='Registration Number', track_visibility='onchange', size=240)
	AccreditationStatus = fields.Char(string='AccreditationStatus', track_visibility='onchange', size=240)
	cmdNext = fields.Char(string='cmdNext', track_visibility='onchange', size=240)
	OrgLegalStatus = fields.Char(string='OrgLegalStatus', track_visibility='onchange', size=240)
	AppliedToAnotherSETA = fields.Char(string='AppliedToAnotherSETA', track_visibility='onchange', size=240)
	qualification_ids = fields.One2many('provider.master.qualification', 'accreditation_qualification_id', 'Qualification Lines')
	qualification_campus_ids = fields.One2many('provider.master.campus.qualification', 'accreditation_qualification_campus_id', 'Qualification Lines')
	skills_programme_ids = fields.One2many('skills.programme.master.rel', 'skills_programme_partner_rel_id', 'Skills Programme Lines')
	skills_programme_campus_ids = fields.One2many('skills.programme.master.campus.rel', 'skills_programme_partner_campus_rel_id', 'Skills Programme Lines')
	# Learning Programme Fields
	learning_programme_ids = fields.One2many('learning.programme.master.rel', 'learning_programme_partner_rel_id', 'Learning Programme Lines')
	learning_programme_campus_ids = fields.One2many('learning.programme.master.campus.rel', 'learning_programme_partner_campus_rel_id', 'Learning Programme Lines')

	alternate_acc_number = fields.Char(string='Accreditation Number', track_visibility='onchange', size=240)
	material = fields.Selection([
		   ('own_material', 'Own Material'),
		   ('hwseta_material', 'HWSETA Material'),
		], string='Material', default='own_material',
		track_visibility='onchange')
	# # Document Uploads
#     cipro_documents = fields.Binary(string="Cipro Documents")
#     tax_clearance = fields.Binary(string="Tax Clearance")
#     director_cv = fields.Binary(string="Director C.V")
#     certified_copies_of_qualifications = fields.Binary(string="Certified copies of Qualifications")
	cipro_documents = fields.Many2one('ir.attachment', string='Cipro Documents')
	tax_clearance = fields.Many2one('ir.attachment', string='Tax Clearance')
	director_cv = fields.Many2one('ir.attachment', string='Director C.V')
	certified_copies_of_qualifications = fields.Many2one('ir.attachment', string='Certified copies of Qualifications')
	professional_body_registration = fields.Many2one('ir.attachment', string='Professional Body Registration')
	workplace_agreement = fields.Many2one('ir.attachment', string='Workplace Agreement')
	business_residence_proof = fields.Many2one('ir.attachment', string='Business Visa/Passport/Permanent residence')
	provider_learning_material = fields.Many2one('ir.attachment', string='Learning Programme Approval Report')
	skills_programme_registration_letter = fields.Many2one('ir.attachment', string='Skills Programme Registration Letter')
	company_profile_and_organogram = fields.Many2one('ir.attachment', string='Company Profile  and organogram')
	quality_management_system = fields.Many2one('ir.attachment', string='Quality Management System (QMS)')
	provider_master_contact_ids = fields.One2many('provider.master.contact', 'provider_master_contact_id', string='Provider Contact', track_visibility='onchange')
	acc_multi_doc_upload_master_ids = fields.One2many('acc.multi.doc.upload', 'acc_id', string='Other Documents', help='Upload Document')
	site_visit_image_master_ids = fields.One2many('site.visit.upload', 'acc_id', string='Site Visit Image Upload', help='Image Upload Document')
	lease_agreement_document = fields.Many2one('ir.attachment', string='Lease Document')
	partner_user_rel_ids = fields.One2many('partner.user.rel', 'rel_id', string='Rel')
	provider_batch_ids = fields.One2many('etqe.batch.provider.rel', 'batch_provider_id', string='Provider Batch Rel', track_visibility='onchange')
	provider_master_campus_contact_ids = fields.One2many('provider.master.campus.contact', 'provider_master_campus_contact_id', string='Provider Master Campus', track_visibility='onchange')
#     _sql_constraints = [('sdl_uniq', 'unique(provider_sdl_no)',
#             'SDL Number must be unique per Provider!'),]
#     Added provider group
	provider_hwseta_group = fields.Boolean(string='HWSETA')
	provider_dhet_group = fields.Boolean(string='DHET')
	provider_hpcsa_group = fields.Boolean(string='HPCSA')
	provider_otherseta_group = fields.Boolean(string='Other SETA')
	provider_che_group = fields.Boolean(string='CHE')
	provider_sanc_group = fields.Boolean(string='SANC')
	provider_sapc_group = fields.Boolean(string='SAPC')
	_sql_constraints = [('txtVATRegNo_uniq', 'unique(txtVATRegNo)',
			'VAT Registration Number must be unique per Company!'), ]

	@api.model
	def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
		""" Override read_group to add Label for boolean field status """
		ret_val = super(res_partner, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
		for rt in ret_val:
			if rt.has_key('is_active_provider'):
				if rt.get('is_active_provider', False):
					rt['is_active_provider'] = 'Active'
				else:
					rt['is_active_provider'] = 'In Active'
		return ret_val

	@api.model
	def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
		user = self._uid
		user_data = self.env['res.users'].browse(user)
		user_groups = user_data.groups_id
		sdp_manager = False
		finance_manager = False
		wsp_manager = False
		provincial_manager = False
		wsp_officer = False
		provincial_officer = False
		wsp_administrator = False
		general_access = False
		sdf = False
		provider = False
		for group in user_groups:
			if group.name == "SDP Manager":
				sdp_manager = True
			if group.name == "WSP Manager":
				wsp_manager = True
			if group.name == "Provincial Manager":
				provincial_manager = True
			if group.name == "WSP Officer":
				wsp_officer = True
			if group.name == "Provincial Officer":
				provincial_officer = True
			if group.name == "WSP Administrator":
				wsp_administrator = True
			if group.name == "General Access":
				general_access = True
			if group.name in ['Financial Manager', 'Accountant', 'Invoicing & Payments']:
				finance_manager = True
			if group.name == "SDF":
				sdf = True
			if group.name == "Providers":
				provider = True
#                 return super(res_partner, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
			if group.name == "ETQE Manager":
				if args:
					if args[0][0] == 'provider':
						self._cr.execute("select id from res_partner where is_visible = True and provider = True")
						providers_ids = map(lambda x:x[0], self._cr.fetchall())
						args.append(('id', 'in', providers_ids))
					return super(res_partner, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
			if user == 1:
				if args:
					if args[0][0] == 'provider':
						self._cr.execute("select id from res_partner where is_visible = True and provider = True")
						providers_ids = map(lambda x:x[0], self._cr.fetchall())
						args.append(('id', 'in', providers_ids))
					return super(res_partner, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		# # Very Important : Checking args so that we can diff employer and provider.Do not erase.
		if args and isinstance(args[0], list) and sdp_manager == False and finance_manager == False and wsp_manager == False and provincial_manager == False and wsp_officer == False and provincial_officer == False and wsp_administrator == False and general_access == False:
			if args[0][0] == 'employer' and args[0][2] == True:
				partner = []
				user_data = self.env['res.users'].browse(user)
				if sdf:
					self._cr.execute("select id from resource_resource where user_id=%s" % (user_data.id))
					resource_id = self._cr.fetchone()
					if resource_id:
						self._cr.execute("select id from hr_employee where resource_id=%s" % (resource_id[0]))
						hr_employee_id = self._cr.fetchone()
						self._cr.execute("select employer_id from sdf_employer_rel where sdf_prof_id=%s or sdf_id=%s" % (hr_employee_id[0], hr_employee_id[0]))
						partner.extend(map(lambda x:x[0], self._cr.fetchall()))
					args.append(('id', 'in', partner))
				else:
					self._cr.execute('select partner_id from res_users where id=%s', (user_data.id,))
					partner_id = self._cr.fetchone()
					if partner_id :
						partner_id = partner_id[0]
						partner.append(partner_id)
					else :
						partner_id = None
					args.append(('id', '=', partner_id))
		if provider:
			# providers = [provider_data.id for provider_data in self.env['res.partner'].search([('provider', '=', True)])]
			self._cr.execute("select id from res_partner where provider_accreditation_num='%s'" % (user_data.partner_id.provider_accreditation_num,))
			providers_ids = map(lambda x:x[0], self._cr.fetchall())
			args.append(('id', 'in', providers_ids))
			return super(res_partner, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		return super(res_partner, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

	@api.v7
	def send_re_registration_alert_email(self, cr, uid, context=None):
		today = datetime.today().date()
		provider_obj = self.pool.get('res.partner')
		exp_provider_lst = provider_obj.search(cr, uid, [('provider', '=', True), ('provider_end_date', '<', today)])
		#exp_provider_lst = provider_obj.search(cr, uid, [('provider', '=', True), ('provider_end_date', '<', today), ('provider_status_Id', '=', 'Active')])
		exp_provider_obj = provider_obj.browse(cr, uid, exp_provider_lst)
		if exp_provider_obj:
			for obj in exp_provider_obj:
				obj.provider_status_Id = 'Expired'
				obj.is_active_provider = False
		mail_provider_lst = provider_obj.search(cr, uid, [('is_active_provider','=',True),('active', '=', True), ('provider', '=', True)])
		mail_provider_obj = provider_obj.browse(cr, uid, mail_provider_lst)
		if mail_provider_obj:
			for pro_obj in mail_provider_obj:
				if pro_obj.provider_end_date:
					end_date = datetime.strptime(pro_obj.provider_end_date, "%Y-%m-%d").date()
					today_date = datetime.strptime(str(today), "%Y-%m-%d").date()
					delta = (end_date - today_date).days
					if delta == 42:
						mail_mail = self.pool.get('email.template')
						template = self.pool.get('ir.model.data').get_object(cr, uid, 'hwseta_etqe', 'email_template_provider_re_registration_alert')
						mail_mail.send_mail(cr, uid, template.id, pro_obj.id, force_send=True, raise_exception=True, context=context)
		return True

	@api.multi
	def onchange_qualification(self, qualification_id):
		accreditation_qualification_line = []
		if qualification_id:
			qualification_obj = self.env['provider.qualification'].browse(qualification_id)
			for qualification_lines in qualification_obj.qualification_line:
				val = {
						 'name':qualification_lines.name,
						 'type':qualification_lines.type,
						 'id_data':qualification_lines.id_no,
						 'title':qualification_lines.title,
						 'level1':qualification_lines.level1,
						 'level2':qualification_lines.level2,
						 'level3': qualification_lines.level3,
						}
				accreditation_qualification_line.append((0, 0, val))
			return {'value':{'qualification_line':accreditation_qualification_line}}
		return {'value':{'qualification_line':[]}}

	@api.model
	def create(self, vals):
#         vals.update({'provider_accreditation_num':self.env['ir.sequence'].get('provider.accreditation') or ''})
		provider_data = super(res_partner, self).create(vals)
		if not vals.get('is_existing_provider'):
			mainlist = []
			user_obj = self.env['res.users']
			group_obj = self.env['res.groups']
			# Adding User to Groups
			if provider_data.provider == True:

				group_data = group_obj.search(['|', ('name', '=', 'Portal'), ('name', '=', 'Providers')])
				for data in group_data:
					tup1 = (4, data.id)
					mainlist.append(tup1)
				# Remove User from default Group
				contact_creation_group_data = group_obj.search(['|', ('name', '=', 'Contact Creation'), ('name', '=', 'Employee')])
				for data in contact_creation_group_data:
					tup1 = (3, data.id)
					mainlist.append(tup1)
				values = {
						 'name':provider_data.name,
						 'login':str(provider_data.email).lower(),
						 'partner_id':provider_data.id,
						 'password':'admin',
						 'groups_id':mainlist,
						 'internal_external_users':'Providers',
				}
				user_data = user_obj.create(values)
		if vals.get('is_existing_provider'):
#             This code is written for email & login field mismatch in res_partner and res_user
#             self._cr.execute('select id from res_partner where provider = True and email=%s', (vals.get('email'),))
#             partner_id = self._cr.fetchone()
# #             pro_lst = []
# #             if partner_ids:
# #                 for id in partner_ids:
# #                     pro_lst.append(id)
# #                 provider_obj = self.env['res.partner'].search([('id', '=', max(pro_lst))])
#             self._cr.execute('select id,partner_id from res_users where partner_id=%s' %(partner_id[0]))
#             result = self._cr.fetchall()
			self._cr.execute('select id,partner_id from res_users where login=%s', (vals.get('email'),))
			result = self._cr.fetchall()
			if result:
				self._cr.execute('update learner_registration_qualification set provider_id=%s where provider_id =%s' % (provider_data.id,result[0][1]))
				self._cr.execute('update skills_programme_learner_rel set provider_id=%s where provider_id =%s' % (provider_data.id,result[0][1]))
				self._cr.execute('update learning_programme_learner_rel set provider_id=%s where provider_id =%s' % (provider_data.id,result[0][1]))
				self._cr.execute('update batch_master set provider_id=%s where provider_id =%s' % (provider_data.id,result[0][1]))
				self._cr.execute('update provider_assessment set provider_id=%s where provider_id =%s' % (provider_data.id,result[0][1]))
				self._cr.execute('update res_users set partner_id=%s where id =%s' % (provider_data.id, result[0][0]))
		return provider_data

	@api.multi
	def write(self, vals):
		context = self._context
		if context is None:
			context = {}
		res = super(res_partner, self).write(vals)
#         if self.assessors_ids:
#             for assessor in self.assessors_ids:
#                 if not assessor.assessor_sla_document:
#                     raise Warning(_('Please upload SLA Document in Assessor tab'))
#         if self.moderators_ids:
#             for moderator in self.moderators_ids:
#                 if not moderator.moderator_sla_document:
#                     raise Warning(_('Please upload SLA Document in Moderator tab'))
		return res

	@api.multi
	def onchange_provider_province_code(self, province):
		if province:
			country_id = self.country_for_province(province)
			return {'value': {'country_code_physical': country_id }}
		return {}

	@api.multi
	def onchange_provider_province_postal(self, province):
		if province:
			country_id = self.country_for_province(province)
			return {'value': {'country_code_postal': country_id }}
		return {}

	@api.multi
	def onchange_assessrs(self, assessors_id):
		if assessors_id:
			assessors_obj = self.env['hr.employee'].browse(assessors_id)
			return {'value':{'awork_email':assessors_obj.work_email, 'awork_phone':assessors_obj.work_phone}}
		else:
			return {}

	@api.multi
	def onchange_moderators(self, moderators_id):
		if moderators_id:
			moderators_obj = self.env['hr.employee'].browse(moderators_id)
			return {'value':{'mwork_email':moderators_obj.work_email, 'mwork_phone':moderators_obj.work_phone}}
		else:
			return {}

	@api.multi
	def onchange_comment(self, comment):
		if comment:
			user = []
			if self.partner_user_rel_ids:
				user = [(0, 0, {'update_date':user_history.update_date, 'u_id':user_history.u_id, 'rel_id':user_history.rel_id}) for user_history in self.partner_user_rel_ids]
			user.append((0, 0, {'update_date':datetime.now(), 'u_id':self._uid, 'rel_id':self.id, 'comment':comment}))
			return {'value' :{'partner_user_rel_ids':user}}

	@api.multi
	def unlink(self):
		raise Warning(_("Sorry!! You cannot delete Approved record !"))
		return super(res_partner, self).unlink()

	@api.multi
	def copy(self):
		raise Warning(_("Sorry!! You cannot duplicate Approved record !"))
		return super(res_partner, self).copy()
res_partner()

class partner_user_rel(models.Model):
	_name = 'partner.user.rel'

	u_id = fields.Many2one("res.users", 'User')
	update_date = fields.Date(string='Update Date')
	rel_id = fields.Many2one("res.partner", 'Partner')
	comment = fields.Text("Internal Note")
partner_user_rel()

class etqe_as_provider_rel(models.Model):
	_name = 'etqe.as.provider.rel'

	provider_id = fields.Many2one('res.partner', 'Provider Name', domain=[('provider', '=', True),('is_active_provider','=',True)] , ondelete='restrict')
	assessors_id = fields.Many2one('hr.employee', ondelete='cascade')
	provider_accreditation_num = fields.Char("Accreditation Number")
	employer_sdl_no = fields.Char("SDL Number")

	@api.multi
	def onchange_provider(self, provider_id):
		if provider_id:
			provider_obj = self.env['res.partner'].search([('is_active_provider','=',True),('id', '=', provider_id), ('provider', '=', True)])
			if not provider_obj:
				raise Warning(_('Please select valid Provider!'))
			else:
				return {'value':{'provider_accreditation_num':provider_obj.provider_accreditation_num, 'employer_sdl_no':provider_obj.employer_sdl_no}}
		else:
			return {}

class etqe_mo_provider_rel(models.Model):
	_name = 'etqe.mo.provider.rel'

	provider_id = fields.Many2one('res.partner', 'Provider Name', domain=[('provider', '=', True),('is_active_provider','=',True)] , ondelete='restrict')
	moderators_id = fields.Many2one('hr.employee', ondelete='cascade')
	provider_accreditation_num = fields.Char("Accreditation Number")
	employer_sdl_no = fields.Char("SDL Number")
	@api.multi
	def onchange_provider(self, provider_id):
		if provider_id:
			provider_obj = self.env['res.partner'].search([('is_active_provider','=',True),('id', '=', provider_id), ('provider', '=', True)])
			if not provider_obj:
				raise Warning(_('Please select valid Provider!'))
			else:
				return {'value':{'provider_accreditation_num':provider_obj.provider_accreditation_num, 'employer_sdl_no':provider_obj.employer_sdl_no}}
		else:
			return {}

class etqe_assessors_provider_rel(models.Model):
	_name = 'etqe.assessors.provider.rel'

	assessors_id = fields.Many2one("hr.employee", 'Assessors', domain=[('is_active_assessor','=',True),('is_assessors', '=', True)] , ondelete='restrict')
	provider_id = fields.Many2one('res.partner', ondelete='cascade')
	awork_phone = fields.Char('Mobile Number', readonly=False, size=10)
	awork_email = fields.Char('Work Email', size=240)
	assessor_sla_document = fields.Many2one('ir.attachment', string="SLA Document")
	assessor_notification_letter = fields.Many2one('ir.attachment', string="Notification Letter")
	identification_id = fields.Char("Identification/Assessor Number")
	status = fields.Selection([('draft', 'Draft'), ('waiting_approval', 'Waiting Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], string="Status", default='draft')
	request_send = fields.Boolean(string='Send Request', default=False)
	approval_request = fields.Boolean(string='Approval Request', default=False)
	reject_request = fields.Boolean(string="Reject Request", default=False)
	search_by = fields.Selection([('id', 'Identification No'), ('number', 'Assessor ID')], string="Search by")


	@api.multi
	def onchange_assessrs(self, assessors_id, search_by):
		provider_master_objects = self.env['res.partner'].search([('provider_accreditation_num', '=', self._context.get('provider_accreditation_num'))])
		if provider_master_objects:
			pro_lst = []
			for pro_obj in provider_master_objects:
				pro_lst.append(pro_obj.id)
			provider_obj = self.env['res.partner'].search([('id', '=', max(pro_lst))])
			if provider_obj:
				if provider_obj.assessors_ids:
					for line in provider_obj.assessors_ids:
						if assessors_id:
							if assessors_id == line.assessors_id.id:
								raise Warning(_('Assessor already exist,Please enter unique assessor!'))
		if search_by == 'id':
			if assessors_id:
				assessors_obj = self.env['hr.employee'].search([('is_active_assessor','=',True),('id', '=', assessors_id), ('is_assessors', '=', True)])
				if not assessors_obj:
					raise Warning(_('Please enter valid Identification Number!'))
				else:
					return {'value':{'identification_id':assessors_obj.assessor_moderator_identification_id, 'awork_email':assessors_obj.work_email, 'awork_phone':assessors_obj.person_cell_phone_number}}
		if search_by == 'number':
			if assessors_id:
				assessors_obj = self.env['hr.employee'].search([('is_active_assessor','=',True),('id', '=', assessors_id), ('is_assessors', '=', True)])
				if not assessors_obj:
					raise Warning(_('Please enter valid Assessor Number!'))
				else:
					return {'value':{'identification_id':assessors_obj.assessor_seq_no, 'awork_email':assessors_obj.work_email, 'awork_phone':assessors_obj.person_cell_phone_number}}
		else:
			return {}

	@api.multi
	def onchange_identification_id(self, identification_id, search_by):
		if search_by == 'id':
			if identification_id:
				assessors_obj = self.env['hr.employee'].search([('is_active_assessor','=',True),('assessor_moderator_identification_id', '=', identification_id)])
				if assessors_obj:
					return {'value':{'assessors_id':assessors_obj.id, 'awork_email':assessors_obj.work_email, 'awork_phone':assessors_obj.person_cell_phone_number}}
				else:
					raise Warning(_("Assessor with identification id %s does not exist in the system")%(identification_id))
		elif search_by == 'number':
			if identification_id:
				assessors_obj = self.env['hr.employee'].search([('is_active_assessor','=',True),('assessor_seq_no', '=', identification_id),('is_assessors', '=', True)])
				if assessors_obj:
					return {'value':{'assessors_id':assessors_obj.id, 'awork_email':assessors_obj.work_email, 'awork_phone':assessors_obj.person_cell_phone_number}}
				else:
					raise Warning(_("Assessor with Assessor id %s is not active in the system")%(identification_id))
		else:
			return {}

	@api.multi
	def action_send_request(self):
		self.write({'status':'waiting_approval', 'request_send':True})

	@api.multi
	def action_approved_request(self):
		self.write({'status':'approved', 'approval_request':True})

	@api.multi
	def action_rejected_request(self):
		self.write({'status':'rejected', 'reject_request':True})
etqe_assessors_provider_rel()

class etqe_moderators_provider_rel(models.Model):
	_name = 'etqe.moderators.provider.rel'

	moderators_id = fields.Many2one("hr.employee", 'Moderator', domain=[('is_active_moderator','=',True),('is_moderators', '=', True)], ondelete='restrict')
	provider_id = fields.Many2one('res.partner', ondelete='cascade')
	mwork_phone = fields.Char('Work Phone', readonly=False, size=10)
	mwork_email = fields.Char('Work Email', size=240)
	moderator_sla_document = fields.Many2one('ir.attachment', string="SLA Document")
	moderator_notification_letter = fields.Many2one('ir.attachment', string="Notification Letter")
	identification_id = fields.Char("Identification/Moderator Number")
	status = fields.Selection([('draft', 'Draft'), ('waiting_approval', 'Waiting Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], string="Status", default='draft')
	request_send = fields.Boolean(string='Send Request', default=False)
	approval_request = fields.Boolean(string='Approval Request', default=False)
	reject_request = fields.Boolean(string="Reject Request", default=False)
	search_by = fields.Selection([('id', 'Identification No'), ('number', 'Moderator ID')], string="Search by")

	@api.multi
	def onchange_moderators(self, moderators_id, search_by):
		provider_master_objects = self.env['res.partner'].search([('provider_accreditation_num', '=', self._context.get('provider_accreditation_num'))])
		if provider_master_objects:
			pro_lst = []
			for pro_obj in provider_master_objects:
				pro_lst.append(pro_obj.id)
			provider_obj = self.env['res.partner'].search([('id', '=', max(pro_lst))])
			if provider_obj:
				if provider_obj.moderators_ids:
					for line in provider_obj.moderators_ids:
						if moderators_id:
							if moderators_id == line.moderators_id.id:
								raise Warning(_('Moderator already exist,Please enter unique Moderator!'))
		if search_by == 'id':
			if moderators_id:
				moderators_obj = self.env['hr.employee'].search([('is_active_moderator','=',True),('id', '=', moderators_id), ('is_moderators', '=', True)])
				if not moderators_obj:
					raise Warning(_('Please enter valid Identification Number!'))
				else:
					return {'value':{'identification_id':moderators_obj.assessor_moderator_identification_id, 'mwork_email':moderators_obj.work_email, 'mwork_phone':moderators_obj.person_cell_phone_number}}
		elif search_by == 'number':
			if moderators_id:
				moderators_obj = self.env['hr.employee'].search([('is_active_moderator','=',True),('id', '=', moderators_id), ('is_moderators', '=', True)])
				if not moderators_obj:
					raise Warning(_('Please enter valid Moderator Number!'))
				else:
					return {'value':{'identification_id':moderators_obj.moderator_seq_no, 'mwork_email':moderators_obj.work_email, 'mwork_phone':moderators_obj.person_cell_phone_number}}
		else:
			return {}

	@api.multi
	def onchange_identification_id(self, identification_id, search_by):
		if search_by == 'id':
			if identification_id:
				moderators_obj = self.env['hr.employee'].search([('is_active_moderator','=',True),('assessor_moderator_identification_id', '=', identification_id),('is_moderators', '=', True)])
				if moderators_obj:
					return {'value':{'moderators_id':moderators_obj.id, 'mwork_email':moderators_obj.work_email, 'mwork_phone':moderators_obj.person_cell_phone_number}}
				else:
					raise Warning(_("Moderator with identification id %s does not exist in the system")%(identification_id))
		elif search_by == 'number':
			if identification_id:
				moderators_obj = self.env['hr.employee'].search([('is_active_moderator','=',True),('moderator_seq_no', '=', identification_id),('is_moderators', '=', True)])
				if moderators_obj:
					return {'value':{'moderators_id':moderators_obj.id, 'mwork_email':moderators_obj.work_email, 'mwork_phone':moderators_obj.person_cell_phone_number}}
				else:
					raise Warning(_("Moderator with Moderator id %s is not active in the system")%(identification_id))
		else:
			return {}

	@api.multi
	def action_send_request(self):
		self.write({'status':'waiting_approval', 'request_send':True})

	@api.multi
	def action_approved_request(self):
		self.write({'status':'approved', 'approval_request':True})

	@api.multi
	def action_rejected_request(self):
		self.write({'status':'rejected', 'reject_request':True})
etqe_moderators_provider_rel()

class provider_qualification(models.Model):
	_name = 'provider.qualification'
	_description = 'Provider Qualification'

	@api.model
	def _search(self, args, offset=0, limit=80, order=None, count=False, access_rights_uid=None):
		user = self._uid
		user_obj = self.env['res.users']
		user_data = user_obj.browse(user)
		if self._context.get('model') == 'learner.registration.qualification':
			if user_data.partner_id.provider:
				qual_lst = []
				for line in self.env.user.partner_id.qualification_ids:
					self._cr.execute("select id from provider_qualification where seta_branch_id=1 and id =%s"%(line.qualification_id.id))
					qual_id = self._cr.fetchone()
					if qual_id:
						qual_lst.append(qual_id[0])
				args.append(('id', 'in', qual_lst))
				return super(provider_qualification, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		return super(provider_qualification, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
	@api.multi
	@api.depends('name', 'saqa_qual_id')
	def name_get(self):
		res = []
		for record in self:
			rec_str = ''
			if record.saqa_qual_id:
				rec_str += '[' + record.saqa_qual_id + '] '
			if record.name:
				rec_str += record.name
			res.append((record.id, rec_str))
		return res

	@api.model
	def name_search(self, name='', args=[], operator='ilike', limit=100):
		args += ['|', ('name', operator, name), ('saqa_qual_id', operator, name)]
		cuur_ids = self.search(args, limit=limit)
		return cuur_ids.name_get()

	@api.model
	def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
		""" Override read_group to add Label for boolean field status """
		ret_val = super(provider_qualification, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
		for rt in ret_val:
			if rt.has_key('is_archive'):
				if rt.get('is_archive', True):
					rt['is_archive'] = 'Archive'
			if rt.has_key('is_sdp'):
				if rt.get('is_sdp', True):
					rt['is_sdp'] = 'SDP'
			if rt.has_key('is_qdm'):
				if rt.get('is_qdm', True):
					rt['is_qdm'] = 'QDM'
		return ret_val
	name = fields.Char(string='QUALIFICATION TITLE', required=True)
	saqa_qual_id = fields.Char(string='SAQA QUAL ID')
	originator = fields.Char(string='ORIGINATOR')
	qab = fields.Char(string='QUALITY ASSURING BODY')
	nsf = fields.Char(string='NQF SUB-FRAMEWORK')
	qt = fields.Char(string='QUALIFICATION TYPE')
	filed_name = fields.Char(string='FIELD')
	subfield = fields.Char(string='SUBFIELD')
	a_band = fields.Char(string='ABET BAND')
	m_credits = fields.Integer(string='MINIMUM CREDITS')
	pn_level = fields.Char(string='PRE-2009 NQF LEVEL')
	n_level = fields.Char(string='NQF LEVEL')
	q_class = fields.Char(string='QUAL CLASS')
	r_status = fields.Char(string='REGISTRATION STATUS')
	sb_number = fields.Char(string='SAQA DECISION NUMBER')
	rs_date = fields.Date(string='REGISTRATION START DATE')
	re_date = fields.Date(string='REGISTRATION END DATE')
	l_date_e = fields.Date(string='LAST DATE FOR ENROLMENT')
	l_date_a = fields.Date(string='LAST DATE FOR ACHIEVEMENT')
	seta_branch_id = fields.Many2one('seta.branches', 'SETA BRANCH')
	is_archive = fields.Boolean("ARCHIVE")
	is_sdp = fields.Boolean("SDP")
	is_qdm = fields.Boolean("QDM")
	is_exit_level_outcomes = fields.Boolean("Exit Level Outcomes")
	is_ass_mod_linked = fields.Boolean("Assessor/Moderator Linked")
	qualification_line = fields.One2many('provider.qualification.line', 'line_id', 'Qualification Lines')
	qualification_id = fields.Many2one('learner.assessment.line', string='qualification')
	qualification_verify_id = fields.Many2one('learner.assessment.verify.line', string='Qualification')
	qualification_achieve_id = fields.Many2one('learner.assessment.achieve.line', string='Qualification')
	qualification_achieved_id = fields.Many2one('learner.assessment.achieved.line', string='Qualification')

	@api.multi
	def onchange_archive(self, is_archive):
		res = {}
		if is_archive:
			res.update({'value': {'seta_branch_id': None, 'is_sdp': False, 'is_qdm': False, 'is_exit_level_outcomes': False}})
		return res

	@api.multi
	def onchange_seta_branch_sdp_qdm(self, seta_branch_id, is_sdp, is_qdm, is_exit_level_outcomes):
		res = {}
		if seta_branch_id == 1 or is_sdp == True or is_qdm == True or is_exit_level_outcomes == True:
			res.update({'value': {'is_archive': False,}})
		return res

	@api.multi
	@api.onchange('saqa_qual_id')
	def onchange_saqa_qual_id(self):
		if self.saqa_qual_id:
			is_exist_qual_id = self.env['provider.qualification'].search([('saqa_qual_id','=',str(self.saqa_qual_id).split())])
			if is_exist_qual_id:
				self.saqa_qual_id = ''
				return {'warning':{'title':'Duplicate Record','message':'Please enter unique SAQA QUAL ID'}}
		return {}

	@api.multi
	@api.onchange('name')
	def onchange_name(self):
		if self.name:
			is_exist_name = self.env['provider.qualification'].search([('name','=',str(self.name).strip())])
			if is_exist_name:
				self.name = ''
				return {'warning':{'title':'Duplicate Record','message':'Please enter unique  QUALIFICATION TITLE'}}
		return {}
provider_qualification()

class project_project(models.Model):
	_inherit = 'project.project'

	@api.v7
	def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
		res = models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
		if view_type == 'form':
			doc = etree.XML(res['arch'])
			for sheet in doc.xpath("//sheet"):
				parent = sheet.getparent()
				index = parent.index(sheet)
				for child in sheet:
					parent.insert(index, child)
					index += 1
				parent.remove(sheet)
			res['arch'] = etree.tostring(doc)
		return res

	qualification_id = fields.Many2one('provider.qualification', string='Qualification')
	qualification_ids = fields.One2many('project.qualification', 'project_id', string="Qualifications")
	@api.multi
	def onchange_qualification(self, qualification_id) :
		res = {}
		if qualification_id :
			provider_id = []
			for provider in self.env['provider.master.qualification'].search([('qualification_id', '=', qualification_id)]):
				provider_id.append(provider.accreditation_qualification_id)
			provider_vals = [(0, 0, {'provider_id':provider.id}) for provider in list(set(provider_id))]
			res.update({'value':{ 'pro_ids' : provider_vals }})
		return res

	@api.multi
	def get_provider(self):
		''' Getting provider list for selected qualification '''
		if self.qualification_ids :
			if self.pro_ids :
				self.write({'pro_ids':[(2, provider.id) for provider in self.pro_ids]})
			qualification_ids = [qualification.qualification_id.id for qualification in self.qualification_ids]
			provider_id = []
			for provider in self.env['provider.master.qualification'].search([('qualification_id','in',qualification_ids)]):
				provider_id.append(provider.accreditation_qualification_id)
			provider_vals = [(0, 0, {'provider_id':provider.id, 'provider_accreditation_num':provider.provider_accreditation_num,}) for provider in list(set(provider_id))]
			self.write({'pro_ids':provider_vals})
#             res.update({'value':{ 'pro_ids' : provider_vals }})
		return True
project_project()

class project_qualification(models.Model):
	_name = 'project.qualification'

	qualification_id = fields.Many2one('provider.qualification', string="Qualifications")
	project_id = fields.Many2one('project.project', string="Project")
project_qualification()

class provider_qualification_line(models.Model):
	_name = 'provider.qualification.line'
	_description = 'Provider Qualification Line'

	@api.multi
	@api.depends('id_no', 'name')
	def name_get(self):
		res = []
		for record in self:
			rec_str = ''
			if record.id_no:
				rec_str += record.id_no
			else:
				rec_str += record.name
			res.append((record.id, rec_str))
		return res

	name = fields.Char(string='Name')
#     type = fields.Char(string='Type')
	type = fields.Selection([
		   ('Core', 'Core'),
		   ('Fundamental', 'Fundamental'),
		   ('Elective', 'Elective'),
		   ('Knowledge Module', 'Knowledge Module'),
		   ('Practical Skill Module', 'Practical Skill Module'),
		   ('Work Experience Module', 'Work Experience Module'),
		   ('Exit Level Outcomes', 'Exit Level Outcomes'),
		], string='Type', track_visibility='onchange')
	id_no = fields.Char(string='ID NO')
	title = fields.Char(string='UNIT STANDARD TITLE')
	level1 = fields.Char(string='PRE-2009 NQF LEVEL')
	level2 = fields.Char(string='NQF LEVEL')
	level3 = fields.Char(string='CREDITS')
	selection = fields.Boolean(string="SELECTION")
	type_key = fields.Integer("Type Key")
#     seta_approved_lp = fields.Boolean("SETA APPROVED LP")
	line_id = fields.Many2one('provider.qualification', 'Order Reference', required=True, ondelete='cascade')
	unit_standards_id = fields.Many2one('learner.assessment.line', string='Unit Standards')
	unit_standards_verify_id = fields.Many2one('learner.assessment.verify.line', string='Unit Standards')
	unit_standards_achieve_id = fields.Many2one('learner.assessment.achieve.line', string='Unit Standards')
	unit_standards_achieved_id = fields.Many2one('learner.assessment.achieved.line', string='Unit Standards')
	is_seta_approved = fields.Boolean(
		string='SETA Learning Material', track_visibility='onchange')
	is_provider_approved = fields.Boolean(
		string='PROVIDER Learning Material', track_visibility='onchange')

	@api.multi
	@api.onchange('type')
	def onchange_type(self):
		if self.type == 'Core':
			self.type_key = 1
		elif self.type == 'Fundamental':
			self.type_key = 2
		elif self.type == 'Elective':
			self.type_key = 3
		elif self.type == 'Knowledge Module':
			self.type_key = 4
		elif self.type == 'Practical Skill Module':
			self.type_key = 5
		elif self.type == 'Work Experience Module':
			self.type_key = 6
		elif self.type == 'Exit Level Outcomes':
			self.type_key = 7

	@api.multi
	@api.onchange('is_seta_approved')
	def onchange_is_seta_approved(self):
		if self.is_seta_approved:
			self.is_provider_approved = False

	@api.multi
	@api.onchange('is_provider_approved')
	def onchange_is_provider_approved(self):
		if self.is_provider_approved:
			self.is_seta_approved = False

provider_qualification_line()

class provider_accreditation_contact(models.Model):
	_name = 'provider.accreditation.contact'
	_description = 'Provider Accreditation Contact'

	provider_accreditation_contact_id = fields.Many2one('provider.accreditation', 'Provider Accreditation', required=True, ondelete='cascade', select=True)
	name = fields.Char(string='Name', required=True)
	sur_name = fields.Char(string='Surname', required=True)
	street = fields.Char(string='Street')
	street2 = fields.Char(string='Street2')
	zip = fields.Char(string='Zip', size=24, change_default=True)
	city = fields.Char(string='City')
	state_id = fields.Many2one("res.country.state", 'Province', ondelete='restrict')
	country_id = fields.Many2one('res.country', 'Country', ondelete='restrict')
	email = fields.Char(string='Email')
	phone = fields.Char(string='Phone', size=10)
	mobile = fields.Char(string='Mobile', size=10)
	image = fields.Binary(string="Image", help="This field holds the image used as avatar for this contact, limited to 1024x1024px")
	status = fields.Char(string='Status')
	fax = fields.Char(string='Fax', size=10)
	designation = fields.Char(string='Job Title')

	@api.onchange('email')
	def onchange_validate_email(self):
		if self.email:
			if '@' not in self.email:
				self.email = ''
				return {'warning':{'title':'Invalid input','message':'Please enter valid Contact email address'}}
provider_accreditation_contact()

class provider_accreditation_campus_contact(models.Model):
	_name = 'provider.accreditation.campus.contact'
	_description = 'Provider Accreditation Campus Contact'


	provider_accreditation_campus_contact_id = fields.Many2one('provider.accreditation.campus', 'Provider Accreditation Campus', required=True, ondelete='cascade', select=True)
	name = fields.Char(string='Name', required=True)
	street = fields.Char(string='Street')
	street2 = fields.Char(string='Street2')
	zip = fields.Char(string='Zip', size=24, change_default=True)
	city = fields.Char(string='City')
	state_id = fields.Many2one("res.country.state", 'Province', ondelete='restrict')
	country_id = fields.Many2one('res.country', 'Country', ondelete='restrict')
	email = fields.Char(string='Email')
	phone = fields.Char(string='Phone', size=10)
	mobile = fields.Char(string='Mobile', size=10)
	image = fields.Binary(string="Image",
			help="This field holds the image used as avatar for this contact, limited to 1024x1024px")
	status = fields.Char(string='Status')
	fax = fields.Char(string='Fax',size=10)
	designation = fields.Char(string='Job Title')
	sur_name = fields.Char(string='Surname')
provider_accreditation_campus_contact()

class provider_master_campus_contact(models.Model):
	_name = 'provider.master.campus.contact'
	_description = 'Provider Master Campus Contact'

	provider_master_campus_contact_id = fields.Many2one('res.partner', 'Provider Master Campus', required=True, ondelete='cascade', select=True)
	name = fields.Char(string='Name', required=True)
	street = fields.Char(string='Street')
	street2 = fields.Char(string='Street2')
	zip = fields.Char(string='Zip', size=24, change_default=True)
	city = fields.Char(string='City')
	state_id = fields.Many2one("res.country.state", 'Province', ondelete='restrict')
	country_id = fields.Many2one('res.country', 'Country', ondelete='restrict')
	email = fields.Char(string='Email')
	phone = fields.Char(string='Phone', size=10)
	mobile = fields.Char(string='Mobile', size=10)
	image = fields.Binary(string="Image",
			help="This field holds the image used as avatar for this contact, limited to 1024x1024px")
	status = fields.Char(string='Status')
	fax = fields.Char(string='Fax',size=10)
	designation = fields.Char(string='Job Title')
	sur_name = fields.Char(string='Surname')
provider_accreditation_campus_contact()

class provider_accreditation_qualification_line(models.Model):
	_name = 'provider.accreditation.qualification.line'
	_description = 'Provider Accreditation Qalification Line'

	name = fields.Char(string='Name')
#     type = fields.Char(string='Type')
	type = fields.Selection([
	('Core', 'Core'),
	('Fundamental', 'Fundamental'),
	('Elective', 'Elective'),
	('Knowledge Module', 'Knowledge Module'),
	('Practical Skill Module', 'Practical Skill Module'),
	('Work Experience Module', 'Work Experience Module'),
	('Exit Level Outcomes', 'Exit Level Outcomes'),
	], string='Type', track_visibility='onchange')
	id_data = fields.Char(string='ID')
	title = fields.Char(string='UNIT STANDARD TITLE')
	level1 = fields.Char(string='PRE-2009 NQF LEVEL')
	level2 = fields.Char(string='NQF LEVEL')
	level3 = fields.Char(string='CREDITS')
	selection = fields.Boolean(string="SELECTION")
	is_seta_approved = fields.Boolean(
		string='SETA Learning Material', track_visibility='onchange')
	is_provider_approved = fields.Boolean(
		string='PROVIDER Learning Material', track_visibility='onchange')
	line_id = fields.Many2one('provider.accreditation', 'Provider Accreditation Reference', required=True, ondelete='cascade')

	@api.depends('is_provider_approved')
	@api.onchange('selection')
	def onchange_selection(self):
		if self.selection and self.is_provider_approved:
			raise Warning('Note that the Electives choosen must have HWSETA approved report!!!')

provider_accreditation_qualification_line()

class accreditation_qualification_campus_lines_line(models.Model):
	_name = 'accreditation.qualification.campus.lines.line'
	_description = 'accreditation qualification campus lines line'
	_rec_name = 'type'

	name = fields.Char(string='Name')
#     type = fields.Char(string='Type')
	type = fields.Selection([
	('Core', 'Core'),
	('Fundamental', 'Fundamental'),
	('Elective', 'Elective'),
	('Knowledge Module', 'Knowledge Module'),
	('Practical Skill Module', 'Practical Skill Module'),
	('Work Experience Module', 'Work Experience Module'),
	('Exit Level Outcomes', 'Exit Level Outcomes'),
	], string='Type', track_visibility='onchange')
	id_no = fields.Char(string='ID NO')
	title = fields.Char(string='UNIT STANDARD TITLE')
	level1 = fields.Char(string='PRE-2009 NQF LEVEL')
	level2 = fields.Char(string='NQF LEVEL')
	level3 = fields.Char(string='CREDITS')
	selection = fields.Boolean(string="SELECTION")
	is_seta_approved = fields.Boolean(
		string='SETA Learning Material', track_visibility='onchange')
	is_provider_approved = fields.Boolean(
		string='PROVIDER Learning Material', track_visibility='onchange')
	line_id = fields.Many2one('accreditation.qualification.campus.lines', 'Qualification Reference')

accreditation_qualification_campus_lines_line()

class accreditation_qualification_campus_lines(models.Model):
	_name = 'accreditation.qualification.campus.lines'
	_description = 'Accreditation Qualification Campus Lines'

	qualification_id = fields.Many2one("provider.qualification", 'Qualification', ondelete='restrict')
	saqa_qual_id = fields.Char(string='ID')
	qualification_line = fields.One2many('accreditation.qualification.campus.lines.line', 'line_id', 'Qualification Lines')
	accreditation_campus_qualification_id = fields.Many2one('provider.accreditation.campus', 'Provider Accreditation Campus Reference')
	assessors_id = fields.Many2one("hr.employee", string='Assessor', domain=[('is_active_assessor','=',True),('is_assessors', '=', True)])
	assessor_sla_document = fields.Many2one('ir.attachment', string="SLA Document")
	moderators_id = fields.Many2one("hr.employee", string='Moderator', domain=[('is_active_moderator','=',True),('is_moderators', '=', True)])
	moderator_sla_document = fields.Many2one('ir.attachment', string="SLA Document")

	@api.multi
	def onchange_qualification(self, qualification_id):
		res = {}
		accreditation_qualification_line = []
		if qualification_id:
			qualification_obj = self.env['provider.qualification'].browse(qualification_id)
			for qualification_lines in qualification_obj.qualification_line:
				if qualification_lines.type == 'Core' or qualification_lines.type == 'Fundamental':
					val = {
							'name':qualification_lines.name,
							'type':qualification_lines.type,
							'id_no':qualification_lines.id_no,
							'title':qualification_lines.title,
							'level1':qualification_lines.level1,
							'level2':qualification_lines.level2,
							'level3': qualification_lines.level3,
							'is_seta_approved':qualification_lines.is_seta_approved,
							'is_provider_approved':qualification_lines.is_provider_approved,
							'selection': True
							}
					accreditation_qualification_line.append((0, 0, val))
				elif qualification_lines.type == 'Elective':
					val = {
							'name':qualification_lines.name,
							'type':qualification_lines.type,
							'id_no':qualification_lines.id_no,
							'title':qualification_lines.title,
							'level1':qualification_lines.level1,
							'level2':qualification_lines.level2,
							'level3': qualification_lines.level3,
							'is_seta_approved':qualification_lines.is_seta_approved,
							'is_provider_approved':qualification_lines.is_provider_approved,
						   }
				else:
					val = {
							'name':qualification_lines.name,
							'type':qualification_lines.type,
							'id_no':qualification_lines.id_no,
							'title':qualification_lines.title,
							'level1':qualification_lines.level1,
							'level2':qualification_lines.level2,
							'level3': qualification_lines.level3,
							}
					accreditation_qualification_line.append((0, 0, val))
			return {'value':{'qualification_line':accreditation_qualification_line, 'saqa_qual_id':qualification_obj.saqa_qual_id}}
		return {}
accreditation_qualification_campus_lines()

class etqe_assessors_provider_accreditation_campus_rel(models.Model):
	_name = 'etqe.assessors.provider.accreditation.campus.rel'

	@api.multi
	def _get_qualification_list(self):
		''' Getting qualification via context passed in xml.'''
		context = self._context
		qualification_obj_ids = context.get('qualification_ids_assessors', False)
		main_qualification_list = ""
		if qualification_obj_ids:
			for qualification_obj in qualification_obj_ids:
				if main_qualification_list == "":
					main_qualification_list + str(qualification_obj[1])
				else:
					main_qualification_list + "," + str(qualification_obj[1])
		return main_qualification_list

	@api.multi
	def onchange_qualification_list(self, qualification_str):
		'''Applying domain on assessors. Will show only assessors in which selected qualification
		matches.'''
		res = {}
		if qualification_str:
			qualification_list = qualification_str.split(",")
			main_qualification_list = []
			assessors_list = []
			for qualification_obj in qualification_list:
				qualification = self.env['accreditation.qualification'].browse(qualification_obj)
				for main_qualification in qualification:
					main_qualification_list.append(main_qualification.qualification_id.id)
				assessors_ids = self.env['hr.employee'].search([('is_active_assessor','=',True),('is_assessors', '=', True)])
				for assessors_obj in assessors_ids:
					for qualification_data in assessors_obj.qualification_ids:
						if qualification_data.qualification_hr_id.id in main_qualification_list:
							assessors_list.append(assessors_obj.id)
			res.update({'domain':{'assessors_id':[('id', 'in', assessors_list)]}})
		return res
	assessors_id = fields.Many2one("hr.employee", 'Assessors', domain=[('is_active_assessor','=',True),('is_assessors', '=', True)] , ondelete='restrict')
	ass_campus_id = fields.Many2one('provider.accreditation.campus', ondelete='cascade')
	awork_phone = fields.Char('Work Phone', readonly=False, size=10)
	awork_email = fields.Char('Work Email', size=240)
	qualification_list = fields.Char('Qualification List', size=1000, default=_get_qualification_list)
	campus_assessor_sla_document = fields.Many2one('ir.attachment', string="SLA Document")
	assessor_notification_letter = fields.Many2one('ir.attachment', string="Notification Letter")
	@api.multi
	def onchange_assessrs(self, assessors_id):

		if assessors_id:
			assessors_obj = self.env['hr.employee'].browse(assessors_id)
			return {'value':{'awork_email':assessors_obj.work_email, 'awork_phone':assessors_obj.work_phone}}
		else:
			return {}
etqe_assessors_provider_accreditation_campus_rel()

class etqe_moderators_provider_accreditation_campus_rel(models.Model):
	_name = 'etqe.moderators.provider.accreditation.campus.rel'

	@api.multi
	def _get_qualification_list(self):
		''' Getting qualification via context passed in xml.'''
		context = self._context
		qualification_obj_ids = context.get('qualification_ids_moderators', False)
		main_qualification_list = ""
		if qualification_obj_ids:
			for qualification_obj in qualification_obj_ids:
				if main_qualification_list == "":
					main_qualification_list + str(qualification_obj[1])
				else:
					main_qualification_list + "," + str(qualification_obj[1])
		return main_qualification_list

	@api.multi
	def onchange_qualification_list(self, qualification_str):
		'''Applying domain on moderators. Will show only assessors in which selected qualification
		matches.'''
		res = {}
		if qualification_str:
			qualification_list = qualification_str.split(",")
			main_qualification_list = []
			moderators_list = []
			for qualification_obj in qualification_list:
				qualification = self.env['accreditation.qualification'].browse(qualification_obj)
				for main_qualification in qualification:
					main_qualification_list.append(main_qualification.qualification_id.id)
				moderators_ids = self.env['hr.employee'].search([('is_active_moderator','=',True),('is_moderators', '=', True)])
				for moderators_obj in moderators_ids:
					for qualification_data in moderators_obj.qualification_ids:
						if qualification_data.qualification_hr_id.id in main_qualification_list:
							moderators_list.append(moderators_obj.id)
			res.update({'domain':{'moderators_id':[('id', 'in', moderators_list)]}})
		return res
	moderators_id = fields.Many2one("hr.employee", 'Moderator', domain=[('is_active_moderator','=',True),('is_moderators', '=', True)], ondelete='restrict')
	mo_campus_id = fields.Many2one('provider.accreditation.campus', ondelete='cascade')
	mwork_phone = fields.Char('Work Phone', readonly=False, size=10)
	mwork_email = fields.Char('Work Email', size=240)
	qualification_list = fields.Char('Qualification List', size=1000, default=_get_qualification_list)
	campus_moderator_sla_document = fields.Many2one('ir.attachment', string="SLA Document")
	moderator_notification_letter = fields.Many2one('ir.attachment', string="Notification Letter")

	@api.multi
	def onchange_moderators(self, moderators_id):

		if moderators_id:
			moderators_obj = self.env['hr.employee'].browse(moderators_id)
			return {'value':{'mwork_email':moderators_obj.work_email, 'mwork_phone':moderators_obj.work_phone}}
		else:
			return {}
etqe_moderators_provider_accreditation_campus_rel()

class skills_programme_unit_standards_accreditation_campus_rel(models.Model):
	_name = 'skills.programme.unit.standards.accreditation.campus.rel'
	_description = 'Skills Programme Unit Standards Accreditation Campus Rel'
	_rec_name = 'type'
	name = fields.Char(string='Name')
	type = fields.Char(string='Type', required=True)
	id_no = fields.Char(string='ID NO')
	title = fields.Char(string='UNIT STANDARD TITLE', required=True)
	level1 = fields.Char(string='PRE-2009 NQF LEVEL')
	level2 = fields.Char(string='NQF LEVEL')
	level3 = fields.Char(string='CREDITS')
	selection = fields.Boolean(string='SELECT')
	skills_programme_id = fields.Many2one('skills.programme.accreditation.campus.rel', 'Skills Programme Reference', ondelete='cascade')
skills_programme_unit_standards_accreditation_campus_rel()

class skills_programme_accreditation_campus_rel(models.Model):
	_name = 'skills.programme.accreditation.campus.rel'
	_description = 'Skills Programme Accreditation Campus Rel'

	saqa_skill_id = fields.Char(string='SAQA QUAL ID')
	skills_programme_id = fields.Many2one("skills.programme", 'Skills Programme')
	unit_standards_line = fields.One2many('skills.programme.unit.standards.accreditation.campus.rel', 'skills_programme_id', 'Unit Standards')
	skills_programme_accreditation_rel_id = fields.Many2one('provider.accreditation.campus', 'Provider Accreditation Reference')

	@api.multi
	def onchange_skills_programme(self, skills_programme_id):
		unit_standards = []
		if skills_programme_id:
			skills_programme_obj = self.env['skills.programme'].browse(skills_programme_id)
			for unit_standards_lines in skills_programme_obj.unit_standards_line:
				if unit_standards_lines.selection == True:
					val = {
							 'name':unit_standards_lines.name,
							 'type':unit_standards_lines.type,
							 'id_no':unit_standards_lines.id_no,
							 'title':unit_standards_lines.title,
							 'level1':unit_standards_lines.level1,
							 'level2':unit_standards_lines.level2,
							 'level3': unit_standards_lines.level3,
							 'selection':True,
							}
					unit_standards.append((0, 0, val))
			return {'value':{'unit_standards_line':unit_standards, 'saqa_skill_id':skills_programme_obj.saqa_qual_id}}
		return {}
skills_programme_accreditation_campus_rel()

class provider_accreditation_campus(models.Model):
	_name = 'provider.accreditation.campus'
	_description = 'Provider Accreditation Campus'

	@api.multi
	def country_for_province(self, province):
		state = self.env['res.country.state'].browse(province)
		return state.country_id.id

	@api.multi
	def onchange_header_province_code(self, province):
		if province:
			country_id = self.country_for_province(province)
			return {'value': {'country_id': country_id }}
		return {}

	@api.multi
	def onchange_header_suburb_code(self, suburb):
		res = {}
		if not suburb:
			return res
		if suburb:
			sub_res = self.env['res.suburb'].browse(suburb)
			res.update({'value':{'zip':sub_res.postal_code, 'city':sub_res.city_id, 'state_id':sub_res.province_id}})
		return res

	@api.multi
	def _get_image(self, name, args):
		return dict((p.id, tools.image_get_resized_images(p.image)) for p in self)

	@api.one
	def _set_image(self, name, value, args):
		return self.write({'image': tools.image_resize_image_big(value)})

	@api.multi
	def _has_image(self, name, args):
		return dict((p.id, bool(p.image)) for p in self)

	@api.model
	def default_get(self, fields):
		''' To get Qualifications/Skills/Learning Programme/Assessors/Moderators from Main campus'''
		context = self._context
		if context is None:
			context = {}
		res = super(provider_accreditation_campus, self).default_get(fields)

		qualification_obj_ids = context.get('default_qualification_id', False)
		skills_obj_ids = context.get('default_skills_id', False)
		learning_programme_obj_ids = context.get('default_learning_programme_id', False)
		assessors_obj_ids = context.get('default_assessors_ids', False)
		moderators_obj_ids = context.get('default_moderators_ids', False)

		q_vals_line, s_vals_line,lp_vals_line, a_vals_line, m_vals_line = [], [], [], [], []
		if qualification_obj_ids:
			for qualification_obj in qualification_obj_ids:
				qualification = self.env['accreditation.qualification'].browse(qualification_obj[1])
				accreditation_qualification_line = []
				for qualification_line_data in qualification.qualification_line:
					for data in qualification_line_data:
						if data.selection:
							val = {
								 'name':data.name,
								 'type':data.type,
								 'id_no':data.id_no,
								 'title':data.title,
								 'level1':data.level1,
								 'level2':data.level2,
								 'level3': data.level3,
								 'is_provider_approved': data.is_provider_approved,
								 'is_seta_approved': data.is_seta_approved,
								 'selection':data.selection
								}
							accreditation_qualification_line.append((0, 0, val))
				q_vals = {
							'qualification_id':qualification.qualification_id.id,
							'qualification_line':accreditation_qualification_line,
							'saqa_qual_id':qualification.saqa_qual_id,
							'assessors_id':qualification.assessors_id.id,
							'moderators_id':qualification.moderators_id.id,
							'assessor_sla_document':qualification.assessor_sla_document.id,
							'moderator_sla_document':qualification.moderator_sla_document.id,
							}
				q_vals_line.append((0, 0, q_vals))

				res.update(qualification_ids=q_vals_line)

		if skills_obj_ids:
			for skills_obj in skills_obj_ids:
				skills = self.env['skills.programme.accreditation.rel'].browse(skills_obj[1])
				skills_line = []
				for skills_line_data in skills.unit_standards_line:
					for data in skills_line_data:
						if data.selection:
							val = {
								 'name':data.name,
								 'type':data.type,
								 'id_no':data.id_no,
								 'title':data.title,
								 'level1':data.level1,
								 'level2':data.level2,
								 'level3': data.level3,
								 'selection':data.selection
								}
							skills_line.append((0, 0, val))
				skills_vals = {
							'skills_programme_id':skills.skills_programme_id.id,
							'unit_standards_line':skills_line,
							'saqa_skill_id':skills.saqa_skill_id,
							}
				s_vals_line.append((0, 0, skills_vals))

				res.update(skills_programme_ids=s_vals_line)

		if learning_programme_obj_ids:
			for lp_obj in learning_programme_obj_ids:
				lp = self.env['learning.programme.accreditation.rel'].browse(lp_obj[1])
				lp_line = []
				for lp_line_data in lp.unit_standards_line:
					for data in lp_line_data:
						if data.selection:
							val = {
								 'name':data.name,
								 'type':data.type,
								 'id_no':data.id_no,
								 'title':data.title,
								 'level1':data.level1,
								 'level2':data.level2,
								 'level3': data.level3,
								 'provider_approved_lp': data.provider_approved_lp,
								 'seta_approved_lp': data.seta_approved_lp,
								 'selection':data.selection
								}
							lp_line.append((0, 0, val))
				lp_vals = {
							'learning_programme_id':lp.learning_programme_id.id,
							'unit_standards_line':lp_line,
							'saqa_qual_id':lp.saqa_qual_id,
							}
				lp_vals_line.append((0, 0, lp_vals))
				res.update(learning_programme_ids=lp_vals_line)
		if assessors_obj_ids:
			for assessors_obj in assessors_obj_ids:
				assessor = self.env['etqe.assessors.provider.accreditation.rel'].browse(assessors_obj[1])
				assessor_vals = {
							'assessors_id':assessor.assessors_id.id,
							'awork_email':assessor.awork_email,
							'awork_phone':assessor.awork_phone,
							'campus_assessor_sla_document':assessor.assessor_sla_document.id,
							'assessor_notification_letter':assessor.assessor_notification_letter.id,
							}
				a_vals_line.append((0, 0, assessor_vals))

				res.update(assessors_ids=a_vals_line)

		if moderators_obj_ids:
			for moderators_obj in moderators_obj_ids:
				moderator = self.env['etqe.moderators.provider.accreditation.rel'].browse(moderators_obj[1])
				moderator_vals = {
							'moderators_id':moderator.moderators_id.id,
							'mwork_email':moderator.mwork_email,
							'mwork_phone':moderator.mwork_phone,
							'campus_moderator_sla_document':moderator.moderator_sla_document.id,
							'moderator_notification_letter':moderator.moderator_notification_letter.id,
							}
				m_vals_line.append((0, 0, moderator_vals))
				res.update(moderators_ids=m_vals_line)
		return res

	provider_accreditation_campus_id = fields.Many2one('provider.accreditation', 'Provider Accreditation', required=True, ondelete='cascade', select=True)
	name = fields.Char(string='Name', required=True)
	street = fields.Char(string='Street')
	street2 = fields.Char(string='Street2')
	street3 = fields.Char(string='Street2')
	zip = fields.Char(string='Zip', size=24, change_default=True)
	suburb = fields.Many2one('res.suburb', string='Suburb')
	city = fields.Many2one('res.city', string='City', track_visibility='onchange')
	state_id = fields.Many2one("res.country.state", 'Province', ondelete='restrict')
	country_id = fields.Many2one('res.country', 'Country', ondelete='restrict')
	email = fields.Char(string='Email')
	phone = fields.Char(string='Phone', size=10)
	mobile = fields.Char(string='Mobile', size=10)
	image = fields.Binary(string="Image",
			help="This field holds the image used as avatar for this contact, limited to 1024x1024px")
	status = fields.Char(string='Status')
	fax = fields.Char(string='Fax',size=10)
	designation = fields.Char(string='Designation')
	campus_evaluat = fields.Boolean(string="Evaluate")
	qualification_ids = fields.One2many('accreditation.qualification.campus.lines', 'accreditation_campus_qualification_id', 'Qualification Campus Lines')
	skills_programme_ids = fields.One2many('skills.programme.accreditation.campus.rel', 'skills_programme_accreditation_rel_id', 'Skills Programme Lines')
	learning_programme_ids = fields.One2many('learning.programme.accreditation.campus.rel', 'learning_programme_accreditation_rel_id', 'Learning Programme Lines')
	assessors_ids = fields.One2many('etqe.assessors.provider.accreditation.campus.rel', 'ass_campus_id', 'Assessors')
	moderators_ids = fields.One2many('etqe.moderators.provider.accreditation.campus.rel', 'mo_campus_id', 'Moderators')
	color = fields.Integer('Color Index')
	provider_accreditation_campus_contact_ids = fields.One2many('provider.accreditation.campus.contact', 'provider_accreditation_campus_contact_id', string='Provider Accreditation Campus', track_visibility='onchange')
	state = fields.Selection([
				('draft', 'Draft'),
				('approved', 'Approved'),
				('denied', 'Rejected'),
			], string='Status', index=True, readonly=True, default='draft',
			track_visibility='onchange', copy=False)
	_columns = {
				# image: all image fields are base64 encoded and PIL-supported
				'image': fields2.binary("Image", track_visibility='onchange',
					help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),
				'image_medium': fields2.function(_get_image, fnct_inv=_set_image,
					string="Medium-sized image", track_visibility='onchange', type="binary", multi="_get_image",
					store={
						'provider.accreditation.campus': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
					},
					help="Medium-sized image of this contact. It is automatically "\
						 "resized as a 128x128px image, with aspect ratio preserved. "\
						 "Use this field in form views or some kanban views."),
				'image_small': fields2.function(_get_image, fnct_inv=_set_image,
					string="Small-sized image", track_visibility='onchange', type="binary", multi="_get_image",
					store={
						'provider.accreditation.campus': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
					},
					help="Small-sized image of this contact. It is automatically "\
						 "resized as a 64x64px image, with aspect ratio preserved. "\
						 "Use this field anywhere a small image is required."),
				'has_image': fields2.function(_has_image, type="boolean"),

					}
	@api.multi
	def action_approved_button(self):
		context = self._context
		if context is None:
			context = {}
		self = self.with_context(approved=True)
		self.write({'state':'approved', 'campus_evaluat':True})

	@api.multi
	def action_reject_button(self):
		context = self._context
		if context is None:
			context = {}
		self = self.with_context(denied=True)
		self.write({'state':'denied', 'campus_evaluat':False})
		return True
provider_accreditation_campus()

class accreditation_qualification_line(models.Model):
	_name = 'accreditation.qualification.line'
	_description = 'accreditation qualification line'
	_rec_name = 'type'

	name = fields.Char(string='Name')
#     type = fields.Char(string='Type')
	type = fields.Selection([
	('Core', 'Core'),
	('Fundamental', 'Fundamental'),
	('Elective', 'Elective'),
	('Knowledge Module', 'Knowledge Module'),
	('Practical Skill Module', 'Practical Skill Module'),
	('Work Experience Module', 'Work Experience Module'),
	('Exit Level Outcomes', 'Exit Level Outcomes'),
	], string='Type', track_visibility='onchange')
	id_no = fields.Char(string='ID NO')
	title = fields.Char(string='UNIT STANDARD TITLE')
	level1 = fields.Char(string='PRE-2009 NQF LEVEL')
	level2 = fields.Char(string='NQF LEVEL')
	level3 = fields.Char(string='CREDITS')
	selection = fields.Boolean(string="SELECTION")
	line_id = fields.Many2one('accreditation.qualification', 'Qualification Reference')
	is_seta_approved = fields.Boolean(
		string='SETA Learning Material', track_visibility='onchange')
	is_provider_approved = fields.Boolean(
		string='PROVIDER Learning Material', track_visibility='onchange')

	@api.depends('is_provider_approved')
	@api.onchange('selection')
	def onchange_selection(self):
		if self.selection and self.is_provider_approved:
			raise Warning('Note that the Electives choosen must have HWSETA approved report!!!')

accreditation_qualification_line()

class accreditation_qualification(models.Model):
	_name = 'accreditation.qualification'
	_inherit = 'mail.thread'
	_description = 'Accreditation  Qualification'

	qualification_id = fields.Many2one("provider.qualification", 'NAME', ondelete='restrict', track_visibility="always")
	saqa_qual_id = fields.Char(string='ID')
	originator = fields.Char(string='ORIGINATOR')
	qualification_line = fields.One2many('accreditation.qualification.line', 'line_id', 'Qualification Lines')
	accreditation_qualification_id = fields.Many2one('provider.accreditation', 'Provider Accreditation Reference')
	select = fields.Boolean('Selection', default=True)
	verify = fields.Boolean('Verify', default=False, track_visibility="onchange")
	minimum_credits = fields.Integer(related="qualification_id.m_credits", string="Minimum Credits")
	total_credits = fields.Integer(compute="_cal_limit" , string="Total Credits", store=True)
	assessors_id = fields.Many2one("hr.employee", string='Assessor Name', domain=[('is_active_assessor','=',True),('is_assessors', '=', True)])
	assessor_sla_document = fields.Many2one('ir.attachment', string="Assessor SLA Document")
	moderators_id = fields.Many2one("hr.employee", string='Moderator Name', domain=[('is_active_moderator','=',True),('is_moderators', '=', True)])
	moderator_sla_document = fields.Many2one('ir.attachment', string="Moderator SLA Document")
	assessor_no = fields.Char(string="Assessor ID")
	moderator_no = fields.Char(string="Moderator ID")

	@api.onchange('assessor_sla_document','assessors_id',)
	def onchange_assessors_id(self):
		provider_accreditation_id = self._context.get('provider_acc_id')
		provider_acc_record = self.env['provider.accreditation'].browse(provider_accreditation_id)
		lst_existed = []
		vals, lst = {}, []
		for line in provider_acc_record:
			if self.assessor_sla_document and self.assessor_sla_document:
				provider_acc_record.onchange_assessors_by_onchange(self.assessors_id,self.assessor_sla_document)
		return {'value':{'assessors_id':self.assessors_id.id}}


	@api.depends('qualification_id')
	@api.onchange('assessor_no')
	def onchange_assessor_no(self):
		if self.assessor_no and self.qualification_id:
			assessor = str(self.assessor_no).strip()
			assessor_id = self.env['hr.employee'].search([('is_active_assessor','=', True),('assessor_seq_no','=', assessor)])
			if not assessor_id:
				self.assessor_no = ''
				return {'warning':{'title':'Invalid Assessor Number','message':'Please Enter Valid Assessor Number!!!'}}
			ass_qual_lst =  []
			for qualification in assessor_id.qualification_ids:
				ass_qual_lst.append(qualification.qualification_hr_id.id)
			if ass_qual_lst:
				if self.qualification_id.id in ass_qual_lst:
					self.assessors_id = assessor_id.id
					return {'domain':{'assessors_id':[('id','in', [assessor_id.id])]}}
				else:
					self.assessor_no = ''
					return {'warning':{'title':'Invalid Assessor','message':'This Assessor is not Linked with selected Qualifications!!'}}


	@api.depends('qualification_id')
	@api.onchange('moderator_no')
	def onchange_moderator_no(self):
		if self.moderator_no and self.qualification_id:
			moderator = str(self.moderator_no).strip()
			moderator_id = self.env['hr.employee'].search([('is_active_moderator','=', True),('moderator_seq_no','=', moderator)])
			if not moderator_id:
				self.moderator_no = ''
				return {'warning':{'title':'Invalid Moderator Number','message':'Please Enter Valid Moderator Number!!!'}}
			mod_qual_lst =  []
			for qualification in moderator_id.moderator_qualification_ids:
				mod_qual_lst.append(qualification.qualification_hr_id.id)
			if mod_qual_lst:
				if self.qualification_id.id in mod_qual_lst:
					self.moderators_id = moderator_id.id
					return {'domain':{'moderators_id':[('id','in', [moderator_id.id])]}}
				else:
					self.moderator_no = ''
					return {'value':{'moderators_no':''}, 'warning':{'title':'Invalid Moderator','message':'This Moderator is not Linked with selected Qualifications!!!'}}

	@api.onchange('assessors_id')
	def onchange_assessors_id(self):
		if self.assessors_id:
			assessor_id = self.env['hr.employee'].search([('id', '=', self.assessors_id.id)])
			if assessor_id:
				self.assessor_no = assessor_id.assessor_seq_no

	@api.onchange('moderators_id')
	def onchange_moderators_id(self):
		if self.moderators_id:
			moderator_id = self.env['hr.employee'].search([('id', '=', self.moderators_id.id)])
			if moderator_id:
				self.moderator_no = moderator_id.moderator_seq_no

	@api.model
	def create(self, vals):
		res = super(accreditation_qualification, self).create(vals)
		return res

	@api.one
	@api.depends('qualification_line.selection')
	def _cal_limit(self):
		total_credit_point = 0
		if self.qualification_line:
			for unit_line in self.qualification_line:
				if unit_line.selection:
					if unit_line.level3 != 'None':
						total_credit_point += int(unit_line.level3)
		self.total_credits = total_credit_point

	@api.multi
	def onchange_qualification(self, qualification_id):
		accreditation_qualification_line, core_lst, fundamental_lst, elective_lst, other_lst = [], [], [], [], []
		qualification_obj = self.env['provider.qualification'].search([('seta_branch_id','=','11')])
		provider_obj = self.env['res.partner']
		qual_list, asse_list, mode_list = [], [], []
		if qualification_obj:
			for q in qualification_obj:
				qual_list.append(q.id)
		'''Code to avoid those qualifications which are already exist in provider master in extension of scope provider process'''
		if (self._context.get('extension_of_scope') == True or self._context.get('existing_provider') == True) and not self._context.get('provider_master_id_number'):
			return {'warning':{'title':'Warning','message':'Please Enter Accreditation Number to fetch existing Provider details!!'}}
		if (self._context.get('extension_of_scope') == True or self._context.get('existing_provider') == True) and self._context.get('provider_master_id_number'):
			provider_master_objects = self.env['res.partner'].search([('provider_accreditation_num', '=', self._context.get('provider_master_id_number'))])
			if provider_master_objects:
				pro_lst = []
				for pro_obj in provider_master_objects:
					pro_lst.append(pro_obj.id)
				provider_obj = self.env['res.partner'].search([('id', '=', max(pro_lst))])
				if provider_obj:
					if provider_obj.qualification_ids:
						for master_qual in provider_obj.qualification_ids:
							if master_qual.qualification_id.id in qual_list:
								qual_list.remove(master_qual.qualification_id.id)
		if qualification_id:
			qualification_obj = self.env['provider.qualification'].browse(qualification_id)
			for qualification_lines in qualification_obj.qualification_line:
				if qualification_lines.type == 'Core':
					val = {
							 'name':qualification_lines.name,
							 'type':qualification_lines.type,
							 'id_no':qualification_lines.id_no,
							 'title':qualification_lines.title,
							 'level1':qualification_lines.level1,
							 'level2':qualification_lines.level2,
							 'level3': qualification_lines.level3,
							 'selection':True,
							}
					core_lst.append((0, 0, val))
				elif qualification_lines.type == 'Fundamental':
					val = {
							 'name':qualification_lines.name,
							 'type':qualification_lines.type,
							 'id_no':qualification_lines.id_no,
							 'title':qualification_lines.title,
							 'level1':qualification_lines.level1,
							 'level2':qualification_lines.level2,
							 'level3': qualification_lines.level3,
							 'selection':True,
							}
					fundamental_lst.append((0, 0, val))
				elif qualification_lines.type == 'Elective':
					val = {
							 'name':qualification_lines.name,
							 'type':qualification_lines.type,
							 'id_no':qualification_lines.id_no,
							 'title':qualification_lines.title,
							 'level1':qualification_lines.level1,
							 'level2':qualification_lines.level2,
							 'level3': qualification_lines.level3,
							 'is_seta_approved':qualification_lines.is_seta_approved,
							 'is_provider_approved':qualification_lines.is_provider_approved,
#                              'selection':True,
							}
					if qualification_lines.is_seta_approved:
						val.update({
									 'selection':True,
									})
					elective_lst.append((0, 0, val))
				else:
					val = {
							 'name':qualification_lines.name,
							 'type':qualification_lines.type,
							 'id_no':qualification_lines.id_no,
							 'title':qualification_lines.title,
							 'level1':qualification_lines.level1,
							 'level2':qualification_lines.level2,
							 'level3': qualification_lines.level3,
							 'is_seta_approved':qualification_lines.is_seta_approved,
							 'is_provider_approved':qualification_lines.is_provider_approved,
							}
					other_lst.append((0, 0, val))
			accreditation_qualification_line = core_lst + fundamental_lst + elective_lst + other_lst
			'''if extension of scope then only select those assessors/moderators which are exist in provider master'''
			ass_list, mod_list = [], []
			if provider_obj.assessors_ids:
				for pro_assessor in provider_obj.assessors_ids:
					if pro_assessor.status == 'approved':
						ass_list.append(pro_assessor.assessors_id.id)
			if provider_obj.moderators_ids:
				for pro_moderator in provider_obj.moderators_ids:
					if pro_moderator.status == 'approved':
						mod_list.append(pro_moderator.moderators_id.id)
			if ass_list:
				assessor_ids = self.env['hr.employee'].search([('id', 'in', ass_list)])
				for ass_id in assessor_ids:
					for qualification_data in ass_id.qualification_ids:
						if qualification_data.qualification_hr_id.id == qualification_obj.id:
							asse_list.append(ass_id.id)
			if mod_list:
				moderator_ids = self.env['hr.employee'].search([('id', 'in', mod_list)])
				for mod_id in moderator_ids:
					for qualification_data in mod_id.qualification_ids:
						if qualification_data.qualification_hr_id.id == qualification_obj.id:
							mode_list.append(mod_id.id)
			return {'domain':{'assessors_id':[('id', 'in', asse_list)], 'moderators_id':[('id', 'in', mode_list)]}, 'value':{'qualification_line':accreditation_qualification_line, 'saqa_qual_id':qualification_obj.saqa_qual_id, 'originator':qualification_obj.originator}}
		return {'domain':{'qualification_id':[('id', 'in', qual_list)],'assessors_id':[('id', 'in', asse_list)],'moderators_id':[('id', 'in', mode_list)]}}

accreditation_qualification()

class etqe_assessors_provider_accreditation_rel(models.Model):
	_name = 'etqe.assessors.provider.accreditation.rel'

	@api.multi
	def _get_qualification_list(self):
		''' Getting qualification via context passed in xml.'''
		context = self._context
		qualification_obj_ids = context.get('qualification_ids_assessors', False)
		main_qualification_list = ""
		if qualification_obj_ids:
			for qualification_obj in qualification_obj_ids:
				if main_qualification_list == "":
					main_qualification_list + str(qualification_obj[1])
				else:
					main_qualification_list + "," + str(qualification_obj[1])
		return main_qualification_list

	@api.multi
	def onchange_qualification_list(self, qualification_str):
		'''Applying domain on assessors. Will show only assessors in which selected qualification
		matches.'''
		res = {}
		if qualification_str:
			qualification_list = qualification_str.split(",")
			main_qualification_list = []
			assessors_list = []
			for qualification_obj in qualification_list:
				qualification = self.env['accreditation.qualification'].browse(qualification_obj)
				for main_qualification in qualification:
					main_qualification_list.append(main_qualification.qualification_id.id)
				assessors_ids = self.env['hr.employee'].search([('is_active_assessor','=',True),('is_assessors', '=', True)])
				for assessors_obj in assessors_ids:
					for qualification_data in assessors_obj.qualification_ids:
						if qualification_data.qualification_hr_id.id in main_qualification_list:
							assessors_list.append(assessors_obj.id)
			res.update({'domain':{'assessors_id':[('id', 'in', assessors_list)]}})
		return res

	assessors_id = fields.Many2one("hr.employee", 'Assessors', domain=[('is_active_assessor','=',True),('is_assessors', '=', True)] , ondelete='restrict')
	ass_provider_id = fields.Many2one('provider.accreditation', ondelete='cascade')
	awork_phone = fields.Char('Work Phone', readonly=False, size=10)
	awork_email = fields.Char('Work Email', size=240)
	qualification_list = fields.Char('Qualification List', size=1000, default=_get_qualification_list)
	assessor_sla_document = fields.Many2one('ir.attachment', string="SLA Document")
	assessor_notification_letter = fields.Many2one('ir.attachment', string="Notification Letter")

	@api.multi
	def onchange_assessrs(self, assessors_id):

		if assessors_id:
			assessors_obj = self.env['hr.employee'].browse(assessors_id)
			return {'value':{'awork_email':assessors_obj.work_email, 'awork_phone':assessors_obj.work_phone, 'assessor_no':assessors_obj.assessor_seq_no}}
		else:
			return {}
etqe_assessors_provider_accreditation_rel()

class etqe_moderators_provider_accreditation_rel(models.Model):
	_name = 'etqe.moderators.provider.accreditation.rel'

	@api.multi
	def _get_qualification_list(self):
		''' Getting qualification via context passed in xml.'''
		context = self._context
		qualification_obj_ids = context.get('qualification_ids_moderators', False)
		main_qualification_list = ""
		if qualification_obj_ids:
			for qualification_obj in qualification_obj_ids:
				if main_qualification_list == "":
					main_qualification_list + str(qualification_obj[1])
				else:
					main_qualification_list + "," + str(qualification_obj[1])
		return main_qualification_list

	@api.multi
	def onchange_qualification_list(self, qualification_str):
		'''Applying domain on moderators. Will show only assessors in which selected qualification
		matches.'''
		res = {}
		if qualification_str:
			qualification_list = qualification_str.split(",")
			main_qualification_list = []
			moderators_list = []
			for qualification_obj in qualification_list:
				qualification = self.env['accreditation.qualification'].browse(qualification_obj)
				for main_qualification in qualification:
					main_qualification_list.append(main_qualification.qualification_id.id)
				moderators_ids = self.env['hr.employee'].search([('is_active_moderator','=',True),('is_moderators', '=', True)])
				for moderators_obj in moderators_ids:
					for qualification_data in moderators_obj.qualification_ids:
						if qualification_data.qualification_hr_id.id in main_qualification_list:
							moderators_list.append(moderators_obj.id)
			res.update({'domain':{'moderators_id':[('id', 'in', moderators_list)]}})
		return res

	moderators_id = fields.Many2one("hr.employee", 'Moderator', domain=[('is_active_moderator','=',True),('is_moderators', '=', True)], ondelete='restrict')
	mo_provider_id = fields.Many2one('provider.accreditation', ondelete='cascade')
	mwork_phone = fields.Char('Work Phone', readonly=False, size=10)
	mwork_email = fields.Char('Work Email', size=240)
	qualification_list = fields.Char('Qualification List', size=1000, default=_get_qualification_list)
	moderator_sla_document = fields.Many2one('ir.attachment', string="SLA Document")
	moderator_notification_letter = fields.Many2one('ir.attachment', string="Notifcation Letter")

	@api.multi
	def onchange_moderators(self, moderators_id):

		if moderators_id:
			moderators_obj = self.env['hr.employee'].browse(moderators_id)
			return {'value':{'mwork_email':moderators_obj.work_email, 'mwork_phone':moderators_obj.work_phone}}
		else:
			return {}
etqe_moderators_provider_accreditation_rel()

class skills_programme_unit_standards_accreditation_rel(models.Model):
	_name = 'skills.programme.unit.standards.accreditation.rel'
	_description = 'Skills Programme Unit Standards Accreditation Rel'
	_rec_name = 'type'
	name = fields.Char(string='Name')
#     type = fields.Char(string='Type', required=True)
	type = fields.Selection([
	('Core', 'Core'),
	('Fundamental', 'Fundamental'),
	('Elective', 'Elective'),
	('Knowledge Module', 'Knowledge Module'),
	('Practical Skill Module', 'Practical Skill Module'),
	('Work Experience Module', 'Work Experience Module'),
	('Exit Level Outcomes', 'Exit Level Outcomes'),
	], string='Type', required=True, track_visibility='onchange')
	id_no = fields.Char(string='ID NO')
	title = fields.Char(string='UNIT STANDARD TITLE', required=True)
	level1 = fields.Char(string='PRE-2009 NQF LEVEL')
	level2 = fields.Char(string='NQF LEVEL')
	level3 = fields.Char(string='CREDITS')
	selection = fields.Boolean(string='SELECT')
	skills_programme_id = fields.Many2one('skills.programme.accreditation.rel', 'Skills Programme Reference', ondelete='cascade')
skills_programme_unit_standards_accreditation_rel()

class skills_programme_accreditation_rel(models.Model):
	_name = 'skills.programme.accreditation.rel'
	_inherit = 'mail.thread'
	_description = 'Skills Programme Accreditation Rel'

	saqa_skill_id = fields.Char(string='SAQA QUAL ID')
	skills_programme_id = fields.Many2one("skills.programme", 'NAME', track_visibility="always")
	qualification_id = fields.Many2one("provider.qualification", 'QUALIFICATION', ondelete='restrict')
	unit_standards_line = fields.One2many('skills.programme.unit.standards.accreditation.rel', 'skills_programme_id', 'Unit Standards')
	skills_programme_accreditation_rel_id = fields.Many2one('provider.accreditation', 'Provider Accreditation Reference')
	select = fields.Boolean("Selection", default=True)
	verify = fields.Boolean('Verify', default=False, track_visibility="onchange")
	minimum_credits = fields.Integer(related="skills_programme_id.total_credit", string="Minimum Credits")
	total_credits = fields.Integer(compute="_cal_limit" , string="Total Credits", store=True)
	assessors_id = fields.Many2one("hr.employee", string='Assessor Name', domain=[('is_active_assessor','=',True),('is_assessors', '=', True)])
	assessor_sla_document = fields.Many2one('ir.attachment', string="Assessor SLA Document")
	moderators_id = fields.Many2one("hr.employee", string='Moderator Name', domain=[('is_active_moderator','=',True),('is_moderators', '=', True)])
	moderator_sla_document = fields.Many2one('ir.attachment', string="Moderator SLA Document")
	assessor_no = fields.Char(string="Assessor ID")
	moderator_no = fields.Char(string="Moderator ID")

	@api.depends('skills_programme_id')
	@api.onchange('assessor_no')
	def onchange_assessor_no(self):
		if self.assessor_no and self.skills_programme_id:
			assessor = str(self.assessor_no).strip()
			assessor_id = self.env['hr.employee'].search([('is_active_assessor','=', True),('assessor_seq_no','=', assessor)])
			if not assessor_id:
				self.assessor_no = ''
				return {'warning':{'title':'Invalid Assessor Number','message':'Please Enter Valid Assessor Number!!!'}}
			ass_qual_lst =  []
			for qualification in assessor_id.qualification_ids:
				ass_qual_lst.append(qualification.qualification_hr_id.id)
			if ass_qual_lst:
				print "ass_qual_lst===",ass_qual_lst
				if self.skills_programme_id.qualification_id.id in ass_qual_lst:
					self.assessors_id = assessor_id.id
					return {'domain':{'assessors_id':[('id','in', [assessor_id.id])]}}
				else:
					self.assessor_no = ''
					return {'warning':{'title':'Invalid Assessor','message':'This Assessor is not Linked with selected Skills Programme!!'}}


	@api.depends('skills_programme_id')
	@api.onchange('moderator_no')
	def onchange_moderator_no(self):
		if self.moderator_no and self.skills_programme_id:
			moderator = str(self.moderator_no).strip()
			moderator_id = self.env['hr.employee'].search([('is_active_moderator','=', True),('moderator_seq_no','=', moderator)])
			if not moderator_id:
				self.moderator_no = ''
				return {'warning':{'title':'Invalid Moderator Number','message':'Please Enter Valid Moderator Number!!!'}}
			mod_qual_lst =  []
			for qualification in moderator_id.moderator_qualification_ids:
				mod_qual_lst.append(qualification.qualification_hr_id.id)
			if mod_qual_lst:
				if self.skills_programme_id.qualification_id.id in mod_qual_lst:
					self.moderators_id = moderator_id.id
					return {'domain':{'moderators_id':[('id','in', [moderator_id.id])]}}
				else:
					self.moderator_no = ''
					return {'value':{'moderators_no':''}, 'warning':{'title':'Invalid Moderator','message':'This Moderator is not Linked with selected Skills Programme!!!'}}

	@api.onchange('assessors_id')
	def onchange_assessors_id(self):
		if self.assessors_id:
			assessor_id = self.env['hr.employee'].search([('id', '=', self.assessors_id.id)])
			if assessor_id:
				self.assessor_no = assessor_id.assessor_seq_no

	@api.onchange('moderators_id')
	def onchange_moderators_id(self):
		if self.moderators_id:
			moderator_id = self.env['hr.employee'].search([('id', '=', self.moderators_id.id)])
			if moderator_id:
				self.moderator_no = moderator_id.moderator_seq_no

	@api.one
	@api.depends('unit_standards_line.selection')
	def _cal_limit(self):
		total_credit_point = 0
		if self.unit_standards_line:
			for unit_line in self.unit_standards_line:
				if unit_line.selection:
					if unit_line.level3:
						total_credit_point += int(unit_line.level3)
		self.total_credits = total_credit_point

	@api.multi
	def onchange_skills_programme(self, skills_programme_id):
		unit_standards = []
		skills_obj = self.env['skills.programme'].search([('seta_branch_id','=','11')])
		provider_obj = self.env['res.partner']
		skills_list, asse_list, mode_list = [], [], []
		if skills_obj:
			for s in skills_obj:
				skills_list.append(s.id)
		'''Code to avoid those skills which are already exist in provider master in extension of scope provider process'''
		if (self._context.get('extension_of_scope') == True or self._context.get('existing_provider') == True) and not self._context.get('provider_master_id_number'):
			return {'warning':{'title':'Warning','message':'Please Enter Accreditation Number to fetch existing Provider details!!'}}
		if (self._context.get('extension_of_scope') == True or self._context.get('existing_provider') == True) and self._context.get('provider_master_id_number'):
			provider_master_objects = self.env['res.partner'].search([('provider_accreditation_num', '=', self._context.get('provider_master_id_number'))])
			if provider_master_objects:
				pro_lst = []
				for pro_obj in provider_master_objects:
					pro_lst.append(pro_obj.id)
				provider_obj = self.env['res.partner'].search([('id', '=', max(pro_lst))])
				if provider_obj:
					if provider_obj.skills_programme_ids:
						for master_skills in provider_obj.skills_programme_ids:
							if master_skills.skills_programme_id.id in skills_list:
								skills_list.remove(master_skills.skills_programme_id.id)
		skills_programme_obj = self.env['skills.programme'].browse(skills_programme_id)
		if skills_programme_id:
			for unit_standards_lines in skills_programme_obj.unit_standards_line:
				if unit_standards_lines.selection == True:
					val = {
							 'name':unit_standards_lines.name,
							 'type':unit_standards_lines.type,
							 'id_no':unit_standards_lines.id_no,
							 'title':unit_standards_lines.title,
							 'level1':unit_standards_lines.level1,
							 'level2':unit_standards_lines.level2,
							 'level3': unit_standards_lines.level3,
							 'selection':True,
							}
					unit_standards.append((0, 0, val))
			'''if extension of scope then only select those assessors/moderators which are exist in provider master'''
			ass_list, mod_list = [], []
			if provider_obj.assessors_ids:
				for pro_assessor in provider_obj.assessors_ids:
					if pro_assessor.status == 'approved':
						ass_list.append(pro_assessor.assessors_id.id)
			if provider_obj.moderators_ids:
				for pro_moderator in provider_obj.moderators_ids:
					if pro_moderator.status == 'approved':
						mod_list.append(pro_moderator.moderators_id.id)
			if ass_list:
				print
				assessor_ids = self.env['hr.employee'].search([('id', 'in', ass_list)])
				for ass_id in assessor_ids:
					for qualification_data in ass_id.qualification_ids:
						if qualification_data.qualification_hr_id.id == skills_programme_obj.qualification_id.id:
							asse_list.append(ass_id.id)
			if mod_list:
				moderator_ids = self.env['hr.employee'].search([('id', 'in', mod_list)])
				for mod_id in moderator_ids:
					for qualification_data in mod_id.qualification_ids:
						if qualification_data.qualification_hr_id.id == skills_programme_obj.qualification_id.id:
							mode_list.append(mod_id.id)
			return {'domain':{'assessors_id':[('id', 'in', asse_list)], 'moderators_id':[('id', 'in', mode_list)]}, 'value':{'unit_standards_line':unit_standards, 'saqa_skill_id':skills_programme_obj.saqa_qual_id, 'qualification_id':skills_programme_obj.qualification_id.id}}
		return {'domain':{'skills_programme_id':[('id', 'in', skills_list)],'assessors_id':[('id', 'in', asse_list)],'moderators_id':[('id', 'in', mode_list)]}}

skills_programme_accreditation_rel()

# Newly added class for ETQE Learner's skills programme
class skills_programme_unit_standards_learner_rel(models.Model):
	_name = 'skills.programme.unit.standards.learner.rel'
	_description = 'Skills Programme Unit Standards Learner Rel'
	_rec_name = 'type'
	name = fields.Char(string='Name')
#     type = fields.Char(string='Type', required=True)
	type = fields.Selection([
	('Core', 'Core'),
	('Fundamental', 'Fundamental'),
	('Elective', 'Elective'),
	('Knowledge Module', 'Knowledge Module'),
	('Practical Skill Module', 'Practical Skill Module'),
	('Work Experience Module', 'Work Experience Module'),
	('Exit Level Outcomes', 'Exit Level Outcomes'),
	], string='Type', required=True, track_visibility='onchange')
	id_no = fields.Char(string='ID NO')
	title = fields.Char(string='UNIT STANDARD TITLE', required=True)
	level1 = fields.Char(string='PRE-2009 NQF LEVEL')
	level2 = fields.Char(string='NQF LEVEL')
	level3 = fields.Char(string='CREDITS')
	selection = fields.Boolean(string='SELECT')
	skills_programme_id = fields.Many2one('skills.programme.learner.rel', 'Skills Programme Reference', ondelete='cascade')
	achieve = fields.Boolean("ACHIEVE", default=False)
skills_programme_unit_standards_learner_rel()
# Newly added class for ETQE Learner's skills programme
class skills_programme_learner_rel(models.Model):
	_name = 'skills.programme.learner.rel'
	_description = 'Skills Programme Learner Rel'

	saqa_skill_id = fields.Char(string='SAQA QUAL ID')
	skills_programme_id = fields.Many2one("skills.programme", 'Skills Programme', required=True)
	unit_standards_line = fields.One2many('skills.programme.unit.standards.learner.rel', 'skills_programme_id', 'Unit Standards')
	skills_programme_learner_rel_id = fields.Many2one('learner.registration', 'Learner Registration Reference')
	select = fields.Boolean("Selection", default=True)
	skills_programme_learner_rel_ids = fields.Many2one('hr.employee', 'Learner Master Reference')
	start_date = fields.Date("Start Date" , required=True)
	end_date = fields.Date("End Date" , required=True)
	assessors_id = fields.Many2one("hr.employee", string='Assessors', domain=[('is_active_assessor','=',True),('is_assessors', '=', True)])
	assessor_date = fields.Date("Assessor Date")
	moderators_id = fields.Many2one("hr.employee", string='Moderators', domain=[('is_active_moderator','=',True),('is_moderators', '=', True)])
	moderator_date = fields.Date("Moderator Date")
	minimum_credits = fields.Integer(related="skills_programme_id.total_credit", string="Minimum Credits")
	total_credits = fields.Integer(compute="_cal_limit" , string="Total Credits", store=True)
	#recently added fields
	batch_id = fields.Many2one('batch.master',string = 'Batch')
	provider_id = fields.Many2one('res.partner', string="Provider", track_visibility='onchange', default=lambda self:self.env.user.partner_id)
	approval_date = fields.Date()
	is_learner_achieved = fields.Boolean(string="Competent", default=False)
	is_complete = fields.Boolean("Achieve", default=False)
	certificate_no = fields.Char("Certificate No.")
	certificate_date = fields.Date("Certificate Date")
	skill_status = fields.Char("Status")

	@api.model
	def default_get(self, fields):
		context = self._context
		if context is None:
			context = {}
		res = super(skills_programme_learner_rel, self).default_get(fields)
		return res

	@api.one
	@api.depends('unit_standards_line.selection')
	def _cal_limit(self):
		total_credit_point = 0
		if self.unit_standards_line:
			for unit_line in self.unit_standards_line:
				if unit_line.selection:
					if unit_line.level3:
						total_credit_point += int(unit_line.level3)
		self.total_credits = total_credit_point

	@api.multi
	def onchange_skills_programme(self, skills_programme_id):
		user = self._uid
		user_obj = self.env['res.users']
		user_data = user_obj.browse(user)
		assessors_lst, moderators_lst, batch_lst, unit_standards, skills_id = [], [], [], [], []
		if user_data.partner_id.provider:
			if self.env.user.partner_id.assessors_ids:
				for assessor in self.env.user.partner_id.assessors_ids:
					if assessor.assessors_id.is_active_assessor:
						assessors_lst.append(assessor.assessors_id.id)
			if self.env.user.partner_id.moderators_ids:
				for moderator in self.env.user.partner_id.moderators_ids:
					if moderator.moderators_id.is_active_moderator:
						moderators_lst.append(moderator.moderators_id.id)
			for line in self.env.user.partner_id.skills_programme_ids:
				skill_programming_obj = self.env['skills.programme'].search([('seta_branch_id','=','11'),('id','=',line.skills_programme_id.id)])
				if skill_programming_obj:
					skills_id.append(skill_programming_obj.id)
			if self.env.user.partner_id.provider_batch_ids:
				for batch in self.env.user.partner_id.provider_batch_ids:
					if batch.batch_master_id.qual_skill_batch == 'skill' and batch.batch_status == 'open':
						batch_lst.append(batch.batch_master_id.id)
		if not user_data.partner_id.provider:
			batch_obj = self.env['batch.master'].search([('qual_skill_batch', '=', 'skill'),('batch_status','=','open')])
			if batch_obj:
				for obj in batch_obj:
					batch_lst.append(obj.id)
		 # Commented following code Giving problem when we fetch non-SA learners because context is passed based on identification id
		'''Code to avoid those skills programme which are already exist in learner master in extension of scope learner process'''
#         if self._context.get('existing_learner') == True and not self._context.get('learner_master_id_number'):
#             return {'warning':{'title':'Warning','message':'Please Enter Identification Number to fetch existing learner details!!'}}
		if self._context.get('existing_learner') == True and self._context.get('learner_master_id_number'):
			learner_master_object = self.env['hr.employee'].search([('learner_identification_id', '=', self._context.get('learner_master_id_number'))])
			if learner_master_object:
				learner_master_skills_obj = self.env['skills.programme.learner.rel'].search([('skills_programme_learner_rel_ids', '=',learner_master_object.id)])
				if learner_master_skills_obj:
					for master_skill in learner_master_skills_obj:
						if master_skill.skills_programme_id.id in skills_id:
							skills_id.remove(master_skill.skills_programme_id.id)
		if skills_programme_id:
			skills_programme_obj = self.env['skills.programme'].search([('seta_branch_id','=','11'),('id','=',skills_programme_id)])
			if skills_programme_obj:
				for unit_standards_lines in skills_programme_obj.unit_standards_line:
					if unit_standards_lines.selection == True:
						val = {
								 'name':unit_standards_lines.name,
								 'type':unit_standards_lines.type,
								 'id_no':unit_standards_lines.id_no,
								 'title':unit_standards_lines.title,
								 'level1':unit_standards_lines.level1,
								 'level2':unit_standards_lines.level2,
								 'level3': unit_standards_lines.level3,
								 'selection':True,
								}
						unit_standards.append((0, 0, val))
				return {'value':{'unit_standards_line':unit_standards, 'saqa_skill_id':skills_programme_obj.saqa_qual_id, 'qualification_id':skills_programme_obj.qualification_id.id}}
		elif skills_id:
			return {'domain': {'skills_programme_id': [('id', 'in', skills_id)],'batch_id':[('id','in',batch_lst)],'assessors_id': [('id', 'in', assessors_lst)], 'moderators_id':[('id', 'in', moderators_lst)]}}
		elif not skills_programme_id and not user_data.partner_id.provider:
			skills_lst = []
			skills_obj = self.env['skills.programme'].search([('seta_branch_id','=','11')])
			if skills_obj:
				for obj in skills_obj:
					skills_lst.append(obj.id)
				return {'domain': {'skills_programme_id': [('id', 'in', skills_lst)],'batch_id':[('id','in',batch_lst)]}}
		return {'domain': {'skills_programme_id': [('id', 'in', [])],'batch_id':[('id','in',batch_lst)]}}

	@api.multi
	def onchange_assessors_id(self, assessors_id):
		res = {}
		if not assessors_id:
			return res
		if assessors_id:
			assessor_brw_id = self.env['hr.employee'].search([('id', '=', assessors_id)])
			res.update({'value':{'assessor_date':assessor_brw_id.end_date}})
		return res

	@api.multi
	def onchange_moderators_id(self, moderators_id):
		res = {}
		if not moderators_id:
			return res
		if moderators_id:
			moderator_brw_id = self.env['hr.employee'].search([('id', '=', moderators_id)])
			res.update({'value':{'moderator_date':moderator_brw_id.end_date}})
		return res

	@api.model
	def _search(self, args, offset=0, limit=80, order=None, count=False, access_rights_uid=None):
		user = self._uid
		user_obj = self.env['res.users']
		user_data = user_obj.browse(user)
		user_groups = user_data.groups_id
		for group in user_groups:
			if group.name in ['ETQE Manager', 'ETQE Executive Manager', 'ETQE Provincial Manager', 'ETQE Officer', 'ETQE Provincial Officer', 'ETQE Administrator', 'ETQE Provincial Administrator', 'Applicant Skills Development Provider', 'CEO']:
				return super(skills_programme_learner_rel, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		if user == 1 :
			return super(skills_programme_learner_rel, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		q = self._cr.execute("select id from skills_programme_learner_rel where provider_id=%s or create_uid = %s" % (user_data.partner_id.id,user_data.id))
		learner_ids = self._cr.fetchall()
		args.append(('id', 'in', learner_ids))
		return super(skills_programme_learner_rel, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
skills_programme_learner_rel()

class acc_multi_doc_upload(models.Model):
	_name = 'acc.multi.doc.upload'

	pro_acc_id = fields.Many2one('provider.accreditation', string='Related Accreditation')
	pro_assessement_id = fields.Many2one('provider.assessment', string='Related Assessment')
	learner_reg_id = fields.Many2one('learner.registration', string='Related Learner Registration')
	learner_master_id = fields.Many2one('hr.employee', string='Related Learner master')
	acc_id = fields.Many2one('res.partner', string="Accreditation")
	name = fields.Char(string='Name Of Doc')
	doc_file = fields.Many2one('ir.attachment', string='Document')

	@api.multi
	def onchange_file(self, doc_file):
		res = {}
		if not doc_file :
			return res
		attachment_data = self.env['ir.attachment'].browse(doc_file)
		values = attachment_data.name
		res_val = {
			  'name' : values,
			  }
		res['value'] = res_val
		return res
acc_multi_doc_upload()

class site_visit_upload(models.Model):
	_name = 'site.visit.upload'

	pro_acc_id = fields.Many2one('provider.accreditation', string='Related Accreditation')
	acc_id = fields.Many2one('res.partner', string='Accreditation')
	name = fields.Char(string='Name Of Doc')
	doc_file = fields.Many2one('ir.attachment', string='Document')

	@api.multi
	def onchange_file(self, doc_file):
		res = {}
		if not doc_file :
			return res
		attachment_data = self.env['ir.attachment'].browse(doc_file)
		values = attachment_data.name
		res_val = {
			  'name' : values,
			  }
		res['value'] = res_val
		return res
site_visit_upload()

class provider_accreditation_status(models.Model):
	_name = 'provider.accreditation.status'
	_description = 'Provider Accreditation Status'
	pro_acc_status_ids = fields.Many2one('provider.accreditation', string='Provider Accreditation Status Reference')
	pa_name = fields.Char(string="Name")
	pa_status = fields.Char(string="Status")
	pa_comment = fields.Char(string="Comment")
	pa_date = fields.Datetime(string="Date")
	pa_updation_date = fields.Datetime(string="Update Date")
provider_accreditation_status()

class provider_accreditation(models.Model):
	_name = 'provider.accreditation'
	_inherit = 'mail.thread'
	_description = 'Provider Accreditation'

	@api.one
	def check_us_lib_min_cred(self,qual):
		dbg('check_us_lib_min_cred')
		this_total = 0
		if qual:
			for us in qual.qualification_line:
				this_total += int(us.level3)
				dbg('qual:' + qual.saqa_qual_id + '--us min:'+ str(us.level3) + '--running total:' + str(this_total))
			dbg('total' + str(this_total))
		return this_total

	@api.one
	def check_lp_us_lib_min_cred(self, lp):
		dbg('check_us_lib_min_cred')
		this_total = 0
		if lp:
			for us in lp.unit_standards_line:
				this_total += int(us.level3)
				dbg('qual:' + lp.saqa_qual_id + '--us min:' + str(us.level3) + '--running total:' + str(this_total))
			dbg('total' + str(this_total))
		return this_total

	@api.one
	def check_sp_us_lib_min_cred(self, sp):
		dbg('check_us_lib_min_cred')
		this_total = 0
		if sp:
			for us in sp.unit_standards_line:
				this_total += int(us.level3)
				dbg('qual:' + sp.saqa_skill_id + '--us min:' + str(us.level3) + '--running total:' + str(this_total))
			dbg('total' + str(this_total))
		return this_total

	@api.multi
	def compare_all_us_dicts(self):
		for this in self.env['provider.accreditation'].search([('state','!=','draft')]):
			this.compare_us_dicts(multi=True)


	@api.one
	def compare_us_dicts(self,**kwargs):
		prov_dict = self.build_prov_dict()[0]
		ass_dict = self.build_ass_dict()[0]
		# dbg('ass dict as is ----------------------------------' + str(self.build_ass_dict()))
		# dbg('ass dict as variable ----------------------------------' + str(ass_dict))
		mod_dict = self.build_mod_dict()
		mismatch_dict = {}
		mod_mismatch_dict = {}
		# dbg('prov' + str(type(prov_dict)))
		# dbg('ass' + str(type(ass_dict)))
		# dbg('prov dict' + str(prov_dict))
		# dbg('ass dict' + str(ass_dict))
		text_guy = ''
		text_guy_issues = ''
		for k, v in prov_dict.items():
			dbg('prov_dict' + str(prov_dict.get(k)))
			dbg(k)
			dbg('ass dict' + str(ass_dict.get(k)))
			for k, v in ass_dict.items():
				if k == 'missing_qual':
					text_guy_issues += str(self.id) + 'missing Qual from assessor dict:' + str(k)
				if k == 'assessor':
					if prov_dict.get(k).get('assessor') == self.env['hr.employee'].search([('id', '=', 421344)]):
						text_guy_issues += str(self.id) + 'missing assessor from prov dict:'
						# dbg(str(self.id) + 'missing assessor from prov dict:')
						continue
					if ass_dict.get(k).get('assessor') == self.env['hr.employee'].search([('id', '=', 421344)]):
						text_guy_issues += str(self.id) + 'missing assessor from ass dict:'
						# dbg(str(self.id) + 'missing assessor from ass dict:')
						continue
			# if ass_dict.get(k).get('missing_qual'):
			# 	text_guy_issues += str(self.id) + 'missing Qual from assessor dict:' + str(k)
			# else:
			# 	if prov_dict.get(k).get('assessor') == self.env['hr.employee'].search([('id','=',421344)]):
			# 		text_guy_issues += str(self.id) + 'missing assessor from prov dict:'
			# 		# dbg(str(self.id) + 'missing assessor from prov dict:')
			# 		continue
			# 	if ass_dict.get(k).get('assessor') == self.env['hr.employee'].search([('id','=',421344)]):
			# 		text_guy_issues += str(self.id) + 'missing assessor from ass dict:'
			# 		# dbg(str(self.id) + 'missing assessor from ass dict:')
			# 		continue
			prov_assessor = prov_dict.get(k).get('assessor')
			dbg('ass ass_assessor' + str(ass_dict.get(k)))
			ass_assessor = ass_dict.get(k).get('assessor')
			if k in ass_dict and ass_assessor == prov_assessor:
				dbg('same assessor:' + str(ass_assessor) + '-prov ass:' + str(prov_assessor))
				mismatch_dict.update({k: {'assessor': ass_assessor, 'units': []}})
				for us in prov_dict.get(k).get('units'):
					if us in ass_dict.get(k).get('units'):
						dbg(str(k) + '--us:' + str(us))
					else:
						mismatch_dict.get(k).get('units').append(us)
			else:
				dbg('adding to mistmatch dict' + str(k))
				mismatch_dict.update({k: "not found"})
		for k, v in prov_dict.items():
			if not prov_dict.get(k).get('moderator'):
				text_guy_issues += str(self.id) + 'missing moderator from prov dict:'
				# dbg(str(self.id) + 'missing moderator from prov dict:')
				# continue
			if not ass_dict.get(k).get('moderator'):
				text_guy_issues += str(self.id) + 'missing moderator from ass dict:'
				# dbg(str(self.id) + 'missing moderator from ass dict:')
				continue
			prov_moderator = prov_dict.get(k).get('moderator')
			mod_moderator = mod_dict.get(k).get('moderator')
			if k in mod_dict and mod_moderator == prov_moderator:
				dbg('same moderator:' + str(mod_moderator) + '-prov mod:' + str(prov_moderator))
				mod_mismatch_dict.update({k: {'moderator': mod_moderator, 'units': []}})
				for us in prov_dict.get(k).get('units'):
					if us in mod_dict.get(k).get('units'):
						dbg(str(k) + '--us:' + str(us))
					else:
						mod_mismatch_dict.get(k).get('units').append(us)
			else:
				mod_mismatch_dict.update({k: "not found"})
		dbg(mismatch_dict)
		for k,v in mismatch_dict.items():
			dbg('mismatch dict k' + str(mismatch_dict.get(k)) + 'key:' + str(k))
			if mismatch_dict.get(k) == 'not found':
				text_guy += 'Qualification:' + k + ' no dict found:' + '\n'
			else:
				if mismatch_dict.get(k).get('units'):
					text_guy += 'Qualification:' + k + ' Assessor:' + mismatch_dict.get(k).get('assessor').name + '\n'
					for unit in mismatch_dict.get(k).get('units'):
						text_guy += unit + '\n'
		for k,v in mod_mismatch_dict.items():
			if mod_mismatch_dict.get(k).get('units'):
				text_guy += 'Qualification:' + k + ' Moderator:' + mod_mismatch_dict.get(k).get('moderator').name + '\n'
				for unit in mod_mismatch_dict.get(k).get('units'):
					text_guy += unit + '\n'
		if text_guy_issues == '':
			pass
		else:
			dbg(text_guy_issues)
		if text_guy == '':
			pass
		elif text_guy != '' and kwargs.get('multi'):
			dbg(str(self.id) + text_guy)
		else:
			raise Warning(_(text_guy))

	@api.one
	def compare_unit_standard_dicts(self):
		prov_dict = self.build_prov_dict()[0]
		ass_dict = self.build_ass_dict()[0]
		lib_dict = self.build_lib_dict()[0]
		mismatch_dict = {}
		# dbg('prov' + str(type(prov_dict)))
		# dbg('ass' + str(type(ass_dict)))
		# dbg(prov_dict)
		text_guy = ''
		style = '<style>#lib_units table, #lib_units th, #lib_units td {border: 1px solid black;text-align: center;}</style>'
		start_table = '<table id="lib_units">'
		table_header = '<tr><th>library Q</th><th>library U</th><th>Provider Q</th><th>Provider U</th><th>assessor</th><th>moderator</th></tr>'
		rows = ''
		for key,value in lib_dict.items():
			rows += '<tr>'
			if key in prov_dict:
				prov_qual = key
			else:
				prov_qual = 'x'
			rows += '<td>' + key + '</td><td>lib US</td><td>' + prov_qual + '</td><td>prov US</td><td>assessor US</td><td>moderator US</td>'
			rows += '</tr>'
			for lib_us in lib_dict.get(key).get('units'):
				rows += '<tr><td>'+key+'</td><td>' + lib_us + '</td>'
				# check for lib units in prov dict
				if lib_us in prov_dict.get(key).get('units'):
					rows += '<td>'+key+'</td><td>' + lib_us + '</td>'
				else:
					rows += '<td>'+key+'</td><td>x</td>'
				rows += '</tr>'
			for k,v in prov_dict.items():
				prov_assessor = prov_dict.get(k).get('assessor')
				ass_assessor = ass_dict.get(k).get('assessor')
				if k in lib_dict:
					# rows += '<tr>'
					rows += '<td>' + k + '</td>'
					for us in prov_dict.get(k).get('units'):
						rows += '<tr><td></td><td>' + us + '</td><td></td><td></td><td></td></tr>'
					if k in ass_dict and ass_assessor == prov_assessor:
						dbg('same assessor:' + str(ass_assessor) + '-prov ass:' + str(prov_assessor))
						mismatch_dict.update({k:{'assessor':ass_assessor,'units':[]}})
						for us in prov_dict.get(k).get('units'):
							if us in ass_dict.get(k).get('units'):
								dbg(str(k) + '--us:' + str(us))
							else:
								mismatch_dict.get(k).get('units').append(us)
					else:
						mismatch_dict.update({k: "not found"})
					if k in mismatch_dict:
						rows += '<td>' + k + '</td>'
					else:
						rows += '<td>not found</td>'
					rows += '</tr>'
		table_end = '</table>'
		text_guy += style + start_table + table_header + rows + table_end
		self.unit_standard_report = text_guy
		# raise Warning(_(mismatch_dict))

	@api.one
	def build_prov_dict(self):
		prov_dict = {}
		if self.qualification_ids:
			for prov_quals in self.qualification_ids:
				if prov_quals.saqa_qual_id:
					prov_dict.update({prov_quals.saqa_qual_id:{'assessor':prov_quals.assessors_id,
					                                           'moderator':prov_quals.moderators_id,
					                                           'units':[]}})
					for prov_us in prov_quals.qualification_line:
						if prov_us.selection:
							prov_dict.get(prov_quals.saqa_qual_id).get('units').append(prov_us.id_no)
				else:
					with open("accrediation_issues.txt", "a+") as f:
						f.write(str(self.id) + 'missing qualification:' + str(prov_quals.qualification_id.saqa_qual_id))
						f.close()
		# dbg('build_prov_dict :' + str(prov_dict))
		return prov_dict
		# raise Warning(_(prov_dict))

	@api.one
	def build_ass_dict(self):
		ass_dict = {}
		if self.qualification_ids:
			for prov_quals in self.qualification_ids:
				if prov_quals.assessors_id:
					dbg('found assessor!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!' + str(prov_quals.assessors_id))
					assessor = prov_quals.assessors_id
					for ass_quals in assessor.qualification_ids:
						dbg(ass_quals.saqa_qual_id)
						if ass_quals.saqa_qual_id == prov_quals.saqa_qual_id:
							dbg('matching quals!!!!' + str(ass_quals.saqa_qual_id) + '-vs-' + str(
								prov_quals.saqa_qual_id))
						else:
							dbg('!!!!!!!!!!!!!!!non-matching quals!!!!' + str(ass_quals.saqa_qual_id) + '-vs-' + str(
								prov_quals.saqa_qual_id))
						if ass_quals.saqa_qual_id not in ass_dict and ass_quals.saqa_qual_id == prov_quals.saqa_qual_id:
							dbg('not in ass dict' + str(ass_quals.saqa_qual_id))
							ass_dict.update({ass_quals.saqa_qual_id: {'assessor': assessor, 'units': []}})
							for ass_us in ass_quals.qualification_line_hr:
								ass_dict.get(ass_quals.saqa_qual_id).get('units').append(ass_us.id_no)
						elif ass_quals.saqa_qual_id not in ass_dict and ass_quals.saqa_qual_id != prov_quals.saqa_qual_id:
							ass_dict.update(
								{prov_quals.saqa_qual_id: {'assessor': assessor, 'units': [], 'missing_qual': True}})
				else:
					with open("accrediation_issues.txt", "a+") as f:
						f.write(str(self.id) + 'missing Assessor on Qual:' + str(prov_quals.qualification_id.saqa_qual_id))
		dbg(str(self) + 'build_ass_dict :' + str(ass_dict))
		return ass_dict

	def build_mod_dict(self):
		mod_dict = {}
		if self.qualification_ids:
			for prov_quals in self.qualification_ids:
				if prov_quals.moderators_id:
					moderator = prov_quals.moderators_id
				else:
					moderator = self.env['hr.employee'].search([('id','=',421344)])
				for mod_quals in moderator.moderator_qualification_ids:
					if mod_quals.saqa_qual_id not in mod_dict:
						# dbg('not in mod dict' + str(mod_quals.saqa_qual_id))
						mod_dict.update({mod_quals.saqa_qual_id:{'moderator':moderator,'units':[]}})
						for mod_us in mod_quals.qualification_line_hr:
							mod_dict.get(mod_quals.saqa_qual_id).get('units').append(mod_us.id_no)
		# dbg('build_mod_dict :' + str(mod_dict))
		return mod_dict

	@api.one
	def build_lib_dict(self):
		lib_dict = {}
		if self.qualification_ids:
			for prov_quals in self.qualification_ids:
				for lib_quals in self.env['provider.qualification'].search([('id','=',prov_quals.qualification_id.id)]):
					if lib_quals.saqa_qual_id not in lib_dict:
						dbg('not in ass dict' + str(lib_quals.saqa_qual_id))
						lib_dict.update({lib_quals.saqa_qual_id:{'units':[]}})
						for lib_us in lib_quals.qualification_line:
							lib_dict.get(lib_quals.saqa_qual_id).get('units').append(lib_us.id_no)
		dbg('build_ass_dict :' + str(lib_dict))
		return lib_dict

	@api.one
	def check_min_sp(self):
		dbg('check_min_lp')
		text_guy = ''
		if self.skills_programme_ids:
			text_guy += '------------lp vs lib-------------\n'
			for sp_quals in self.skills_programme_ids:
				text_guy += str(self.check_sp_us_lib_min_cred(sp_quals)) + '--LP: ' + str(
					sp_quals.saqa_skill_id) + 'min creds' + 'no min cred?\n'
		return text_guy

	@api.one
	def check_min_lp(self):
		dbg('check_min_cred')
		text_guy = ''
		if self.learning_programme_ids:
			text_guy += '------------lp vs lib-------------\n'
			for lp_quals in self.learning_programme_ids:
				text_guy += str(self.check_lp_us_lib_min_cred(lp_quals)) + '--LP: ' + str(
					lp_quals.saqa_qual_id) + 'min creds' + 'no min cred?\n'
		return text_guy

	@api.one
	def check_min_cred(self):
		dbg('check_min_cred')
		quals_dict = {}
		text_guy = ''
		if self.qualification_ids:
			text_guy += '------------provider vs lib-------------\n'
			for prov_quals in self.qualification_ids:
				quals_dict.update({prov_quals:[]})
				for prov_us in prov_quals.qualification_line:
					if prov_us.id_no not in quals_dict.get(prov_quals) and prov_us.selection:
						quals_dict.get(prov_quals).append(prov_us.id_no)
			for k,v in quals_dict.items():
				if self.env['provider.qualification'].search([('id','=',k.qualification_id.id)]):
					# dbg('')
					for z in self.env['provider.qualification'].search([('id','=',k.qualification_id.id)]):
						text_guy += str(self.check_us_lib_min_cred(z)) + '--qual: ' + str(z.saqa_qual_id) + 'min creds' + str(z.m_credits) + '\n'
				else:
					text_guy += 'issue on qual:' + str(k.qualification_id) + '--Unit standard:' + str(v)

		if self.learning_programme_ids:
			text_guy += '------------lp vs lib-------------\n'
			text_guy += self.check_min_lp()[0]
		if self.skills_programme_ids:
			text_guy += '------------sp vs lib-------------\n'
			text_guy += self.check_min_sp()[0]
			text_guy += '----------------------------------------\n'
		self.unit_standard_report = text_guy
		# raise Warning(_(text_guy))

	@api.one
	def check_unit_standards_lib(self):
		dbg('check_unit_standards_lib')
		quals_dict = {}
		text_guy = ''
		if self.qualification_ids:
			for prov_quals in self.qualification_ids:
				quals_dict.update({prov_quals:[]})
				for prov_us in prov_quals.qualification_line:
					if prov_us.id_no not in quals_dict.get(prov_quals) and prov_us.selection:
						quals_dict.get(prov_quals).append(prov_us.id_no)
			for k,v in quals_dict.items():
				if self.env['provider.qualification'].search([('id','=',k.qualification_id.id)]):
					for z in self.env['provider.qualification'].search([('id','=',k.qualification_id.id)]):
						for x in z.qualification_line:
							if x.id_no in quals_dict.get(k):
								dbg('big match:::' + str(x.id_no) + '---' + str(quals_dict.get(k)) + 'lib' + str(z))
							else:
								dbg('mismatch on unit standard:' + str(x.id_no) + '-on qualification:' + str(k.id) + 'lib' + str(z.id))
				else:
					text_guy += 'issue on qual:' + str(k.qualification_id) + '--Unit standard:' + str(v)
			self.unit_standard_report = text_guy
			raise Warning(_(text_guy))



	@api.model
	def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
		""" Override read_group to filter record count based on logged provider """
		if self.env.user.id != 1 and self.env.user.partner_id.provider == True:
			acc_ids = []
			self._cr.execute("select id from provider_accreditation where create_uid='%s'" % (self.env.user.id,))
			acc_ids = map(lambda x:x[0], self._cr.fetchall())
			domain.append(('id', 'in', acc_ids))
		return super(provider_accreditation, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

	@api.model
	def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
		user = self._uid
		user_obj = self.env['res.users']
		user_groups = user_obj.browse(user).groups_id
		for group in user_groups:
			if group.name == "ETQE Manager":
				return super(provider_accreditation, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
			if group.name == "ETQE Provincial Manager":
				return super(provider_accreditation, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
			if group.name == "ETQE Officer":
				return super(provider_accreditation, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
			if group.name == "ETQE Provincial Officer":
				return super(provider_accreditation, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
			if group.name == "ETQE Administrator":
				return super(provider_accreditation, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
			if group.name == "ETQE Provincial Administrator":
				return super(provider_accreditation, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
			if group.name == "ETQE Executive Manager":
				return super(provider_accreditation, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
			if group.name == "CEO":
				return super(provider_accreditation, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
			if group.name == "Applicant Skills Development Provider":
				return super(provider_accreditation, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

		if user == 1:
			return super(provider_accreditation, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		else :
			partner_data = self.env['res.users'].browse(user).partner_id
			args.append(('related_provider', '=', partner_data.id))
			return super(provider_accreditation, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)


	@api.multi
	def open_map_addr(self, street, city, state, country, zip):
		url = "http://maps.google.com/maps?oi=map&q="
		if street:
			url += street.replace(' ', '+')
		if city:
			url += '+' + city.name.replace(' ', '+')
		if state:
			url += '+' + state.name.replace(' ', '+')
		if country:
			url += '+' + country.name.replace(' ', '+')
		if zip:
			url += '+' + zip.replace(' ', '+')
		return {
		'type': 'ir.actions.act_url',
		'url':url,
		'target': 'new'
		}

	@api.multi
	@api.onchange('phone','mobile','fax','email')
	def onchange_validate_number(self):
		if self.is_existing_provider == False and self.is_extension_of_scope == False:
			if self.phone:
				if not self.phone.isdigit() or len(self.phone) != 10:
					self.phone = ''
					return {'warning':{'title':'Invalid input','message':'Please enter 10 digits Phone number'}}
			if self.mobile:
				if not self.mobile.isdigit() or len(self.mobile) != 10:
					self.mobile = ''
					return {'warning':{'title':'Invalid input','message':'Please enter 10 digits Mobile number'}}
			if self.fax:
				if not self.fax.isdigit() or len(self.fax) != 10:
					self.fax = ''
					return {'warning':{'title':'Invalid input','message':'Please enter 10 digits Fax number'}}
			if self.email:
				if '@' not in self.email:
					self.email = ''
					return {'warning':{'email':'Invalid input','message':'Please enter valid email address'}}
				unicode_email = self.email
				email = unicode_email.encode("utf-8")
				duplicate_match_user = self.env['res.users'].search(['|',('login','=',email.strip()),('login','=',self.email)])
				duplicate_provider = self.env['provider.accreditation'].search([('final_state','!=','Rejected'),('email','=',email.strip())])
				if duplicate_match_user or duplicate_provider:
					self.email = ''
					return {'warning':{'title':'Invalid input','message':'Sorry!! Provider is already registered with this email Id !'}}

	@api.multi
	def _get_image(self, name, args):
		return dict((p.id, tools.image_get_resized_images(p.image)) for p in self)

	@api.one
	def _set_image(self, name, value, args):
		return self.write({'image': tools.image_resize_image_big(value)})

	@api.multi
	def _has_image(self, name, args):
		return dict((p.id, bool(p.image)) for p in self)

	@api.multi
	def header_addr_map(self):
		return self.open_map_addr(self.street, self.city, self.state_id, self.country_id, self.zip)


	@api.multi
	def physical_addr_map(self):
		return self.open_map_addr(self.txtPhysicalAddressLine1, self.city_physical, self.province_code_physical, self.country_code_physical, self.zip_physical)

	@api.multi
	def postal_addr_map(self):
		return self.open_map_addr(self.txtPostalAddressLine1, self.city_postal, self.province_code_postal, self.country_code_postal, self.zip_postal)

	@api.multi
	def country_for_province(self, province):
		state = self.env['res.country.state'].browse(province)
		return state.country_id.id

	@api.multi
	def onchange_header_province_code(self, province):
		if province:
			country_id = self.country_for_province(province)
			return {'value': {'country_id': country_id }}
		return {}


	## added Assessor ......................
	@api.multi
	def onchange_assessors_by_onchange(self, assessor_id, assessor_sla_document):
		vals, lst = {}, []
		lst_existed = []
		ids_new = False
		for line in self.assessors_ids:
			lst_existed.append(line.assessors_id.id)
		if assessor_id.id not in lst_existed:
			vals.update({
				   'assessors_id':assessor_id.id,
				   'awork_email':assessor_id.work_email,
				   'awork_phone':assessor_id.work_phone,
				   'ass_provider_id':self.id,
					'assessor_sla_document':assessor_sla_document.id,
				})

		if 'assessors_id' in vals and vals['assessors_id']:
			ids_new = self.env['etqe.assessors.provider.accreditation.rel'].create(vals)
		return ids_new

	@api.multi
	def onchange_qualification_ids(self, qualification_ids):
		vals, lst, m_lst = {}, [], []
		existe_lst_id = []
		try:
			if qualification_ids:
				if qualification_ids[1][2].get('assessors_id'):
					if self.assessors_ids:
						for a_line in self.assessors_ids:
							existe_lst_id.append(a_line.assessors_id.id)
							v = {
								   'assessors_id':a_line.assessors_id.id,
								   'awork_email':a_line.awork_email,
								   'awork_phone':a_line.awork_phone,
								   'assessor_sla_document':a_line.assessor_sla_document.id,
								}
							lst.append((0, 0, v))
					for line in qualification_ids:
						if line[0] != 6 :
							asse_obj = self.env['hr.employee'].search([('id', '=', line[2]['assessors_id'])])
							if asse_obj:
								if asse_obj.id not in existe_lst_id:
									val = {
								   'assessors_id': line[2]['assessors_id'],
								   'awork_email':asse_obj.work_email,
								   'awork_phone':asse_obj.work_phone,
								   'assessor_sla_document': line[2]['assessor_sla_document'],
								   }
									lst.append((0, 0, val))
					vals.update({'assessors_ids':lst})
				if qualification_ids[1][2].get('moderators_id'):
					if self.moderators_ids:
						for m_line in self.moderators_ids:
							v = {
								   'moderators_id':m_line.moderators_id.id,
								   'mwork_email':m_line.mwork_email,
								   'mwork_phone':m_line.mwork_phone,
								   'moderator_sla_document':m_line.moderator_sla_document.id,
								}
							m_lst.append((0, 0, v))
					for line in qualification_ids:
						if line[0] != 6 :
							mode_obj = self.env['hr.employee'].search([('id', '=', line[2]['moderators_id'])])
							if mode_obj:
								val = {
								   'moderators_id':line[2]['moderators_id'],
								   'mwork_email':mode_obj.work_email,
								   'mwork_phone':mode_obj.work_phone,
								   'moderator_sla_document':line[2]['moderator_sla_document'],
								   }
								m_lst.append((0, 0, val))
					vals.update({'moderators_ids':m_lst})
		except:
			pass
		return {'value':vals}

	@api.multi
	def onchange_skills_programme_ids(self, skills_programme_ids):
		vals, lst, m_lst = {}, [], []
		try:
			if skills_programme_ids:
				if skills_programme_ids[1][2].get('assessors_id'):
					if self.assessors_ids:
						for a_line in self.assessors_ids:
							v = {
								   'assessors_id':a_line.assessors_id.id,
								   'awork_email':a_line.awork_email,
								   'awork_phone':a_line.awork_phone,
								   'assessor_sla_document':a_line.assessor_sla_document.id,
								}
							lst.append((0, 0, v))
					for line in skills_programme_ids:
						if line[0] != 6 :
							asse_obj = self.env['hr.employee'].search([('id', '=', line[2]['assessors_id'])])
							if asse_obj:
								val = {
							   'assessors_id': line[2]['assessors_id'],
							   'awork_email':asse_obj.work_email,
							   'awork_phone':asse_obj.work_phone,
							   'assessor_sla_document': line[2]['assessor_sla_document'],
							   }
								lst.append((0, 0, val))
					vals.update({'assessors_ids':lst})
				if skills_programme_ids[1][2].get('moderators_id'):
					if self.moderators_ids:
						for m_line in self.moderators_ids:
							v = {
								   'moderators_id':m_line.moderators_id.id,
								   'mwork_email':m_line.mwork_email,
								   'mwork_phone':m_line.mwork_phone,
								   'moderator_sla_document':m_line.moderator_sla_document.id,
								}
							m_lst.append((0, 0, v))
					for line in skills_programme_ids:
						if line[0] != 6 :
							mode_obj = self.env['hr.employee'].search([('id', '=', line[2]['moderators_id'])])
							if mode_obj:
								val = {
								   'moderators_id':line[2]['moderators_id'],
								   'mwork_email':mode_obj.work_email,
								   'mwork_phone':mode_obj.work_phone,
								   'moderator_sla_document':line[2]['moderator_sla_document'],
								   }
								m_lst.append((0, 0, val))
					vals.update({'moderators_ids':m_lst})
		except:
			pass
		return {'value':vals}

	@api.multi
	def onchange_learning_programme_ids(self, learning_programme_ids):
		vals, lst, m_lst = {}, [], []
		try:
			if learning_programme_ids:
				if learning_programme_ids[1][2].get('assessors_id'):
					if self.assessors_ids:
						for a_line in self.assessors_ids:
							v = {
								   'assessors_id':a_line.assessors_id.id,
								   'awork_email':a_line.awork_email,
								   'awork_phone':a_line.awork_phone,
								   'assessor_sla_document':a_line.assessor_sla_document.id,
								}
							lst.append((0, 0, v))
					for line in learning_programme_ids:
						if line[0] != 6 :
							asse_obj = self.env['hr.employee'].search([('id', '=', line[2]['assessors_id'])])
							if asse_obj:
								val = {
							   'assessors_id': line[2]['assessors_id'],
							   'awork_email':asse_obj.work_email,
							   'awork_phone':asse_obj.work_phone,
							   'assessor_sla_document': line[2]['assessor_sla_document'],
							   }
								lst.append((0, 0, val))
					vals.update({'assessors_ids':lst})
				if learning_programme_ids[1][2].get('moderators_id'):
					if self.moderators_ids:
						for m_line in self.moderators_ids:
							v = {
								   'moderators_id':m_line.moderators_id.id,
								   'mwork_email':m_line.mwork_email,
								   'mwork_phone':m_line.mwork_phone,
								   'moderator_sla_document':m_line.moderator_sla_document.id,
								}
							m_lst.append((0, 0, v))
					for line in learning_programme_ids:
						if line[0] != 6 :
							mode_obj = self.env['hr.employee'].search([('id', '=', line[2]['moderators_id'])])
							if mode_obj:
								val = {
								   'moderators_id':line[2]['moderators_id'],
								   'mwork_email':mode_obj.work_email,
								   'mwork_phone':mode_obj.work_phone,
								   'moderator_sla_document':line[2]['moderator_sla_document'],
								   }
								m_lst.append((0, 0, val))
					vals.update({'moderators_ids':m_lst})
		except:
			pass
		return {'value':vals}

	@api.multi
	def onchange_provider_province_code(self, province):
		if province:
			country_id = self.country_for_province(province)
			return {'value': {'country_code_physical': country_id }}
		return {}

	@api.multi
	def onchange_provider_province_postal(self, province):
		if province:
			country_id = self.country_for_province(province)
			return {'value': {'country_code_postal': country_id }}
		return {}


	broken_rec = fields.Boolean(default=False)
	unit_standard_report = fields.Text()
	is_extension_of_scope = fields.Boolean("Extension of Scope", default=False)
	is_existing_provider = fields.Boolean("Re - Accreditation", default=False)
	accreditation_number = fields.Char("Accreditation Number")
	name = fields.Char(string='Name', track_visibility='onchange', required=True)
	date = fields.Date(string='Date', track_visibility='onchange', select=1)
	street = fields.Char(string='Street', track_visibility='onchange')
	street2 = fields.Char(string='Street2', track_visibility='onchange')
	zip = fields.Char(string='Zip', track_visibility='onchange', size=24, change_default=True)
	city = fields.Many2one('res.city', string='City', track_visibility='onchange')
	state_id = fields.Many2one("res.country.state", string='State', track_visibility='onchange', ondelete='restrict')
	country_id = fields.Many2one('res.country', string='Country', track_visibility='onchange', ondelete='restrict')
	email = fields.Char(string='Email', track_visibility='onchange')
	phone = fields.Char(string='Phone', track_visibility='onchange', size=10)
	fax = fields.Char(string='Fax', track_visibility='onchange', size=10)
	mobile = fields.Char(string='Mobile', track_visibility='onchange', size=10)
	website = fields.Char(string='Website', track_visibility='onchange', help="Website of Partner or Company")
	image = fields.Binary(string="Image", track_visibility='onchange',
			help="This field holds the image used as avatar for this contact, limited to 1024x1024px")
	related_provider = fields.Many2one('res.partner', string='Related Provider')
	provider_accreditation_ref = fields.Char(string='Ref No.', help="Accreditation Reference Number", track_visibility='onchange', size=50)
	sequence_num = fields.Char(string='Accreditation No.', track_visibility='onchange', help="Sequence Numberr", size=50)
	street3 = fields.Char(string='street3', track_visibility='onchange', size=240)
	provider_suburb = fields.Many2one('res.suburb', string='Suburb')
	provider_physical_suburb = fields.Many2one('res.suburb', string='Physical Suburb')
	provider_postal_suburb = fields.Many2one('res.suburb', string='Postal Suburb')
	provider = fields.Boolean(string='Provider')
	reg_start_date = fields.Date(string='Registration Start Date')
	reg_end_date = fields.Date(string='Registration End Date')
	_columns = {
				# image: all image fields are base64 encoded and PIL-supported
				'image': fields2.binary("Image", track_visibility='onchange',
					help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),
				'image_medium': fields2.function(_get_image, fnct_inv=_set_image,
					string="Medium-sized image", track_visibility='onchange', type="binary", multi="_get_image",
					store={
						'provider.accreditation': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
					},
					help="Medium-sized image of this contact. It is automatically "\
						 "resized as a 128x128px image, with aspect ratio preserved. "\
						 "Use this field in form views or some kanban views."),
				'image_small': fields2.function(_get_image, fnct_inv=_set_image,
					string="Small-sized image", track_visibility='onchange', type="binary", multi="_get_image",
					store={
						'provider.accreditation': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
					},
					help="Small-sized image of this contact. It is automatically "\
						 "resized as a 64x64px image, with aspect ratio preserved. "\
						 "Use this field anywhere a small image is required."),
				'has_image': fields2.function(_has_image, type="boolean"),

					}
	state = fields.Selection([
			('general_details', 'General Details'),
			('general_business_information', 'Business Information'),
			('address_info', 'Address Information'),
			('qualification', 'Main Campus'),
			('assessor', 'Assessor'),
			('moderator', 'Moderator'),
			('campus', 'Satellite Campus'),
			('verification', 'Verification'),
			('evaluation', 'Evaluation'),
			('recommended1', 'Recommended'),
			('validated', 'Validated'),
			('recommended2', 'Recommended'),
			('approved', 'Approved'),
			('denied', 'Rejected'),
		], string='Status', index=True, readonly=True, default='general_details',
		track_visibility='onchange', copy=False)
	submitted = fields.Boolean(string='Submitted')
	approved = fields.Boolean(string='Approved')
	denied = fields.Boolean(string='Denied')
	verify = fields.Boolean(string='Verify')
	verification_comment = fields.Text(string='Verification Comment')
	evaluate = fields.Boolean(string='Evaluate')
	recommended1 = fields.Boolean(string='Recommended1')
	validate = fields.Boolean(string='Validate')
	recommended2 = fields.Boolean(string='Recommended2')
	qualification_id = fields.Many2one("provider.qualification", string='Qualification', track_visibility='onchange', ondelete='restrict')
	provider_accreditation_campus_ids = fields.One2many('provider.accreditation.campus', 'provider_accreditation_campus_id', string='Provider Accreditation Campus', track_visibility='onchange')
	provider_accreditation_contact_ids = fields.One2many('provider.accreditation.contact', 'provider_accreditation_contact_id', string='Provider Accreditation Campus', track_visibility='onchange')
	accreditation_qualification_line = fields.One2many('provider.accreditation.qualification.line', 'line_id', string='Qualification Lines', track_visibility='onchange')
	assessors_id = fields.Many2one("hr.employee", string='Assessors', track_visibility='onchange', domain=[('is_active_assessor','=',True),('is_assessors', '=', True)] , ondelete='restrict')
	moderators_id = fields.Many2one("hr.employee", string='Moderator', track_visibility='onchange', domain=[('is_active_moderator','=',True),('is_moderators', '=', True)], ondelete='restrict')
	awork_phone = fields.Char(string='Work Phone', track_visibility='onchange', readonly=False, size=10)
	awork_email = fields.Char(string='Work Email', track_visibility='onchange', size=240)
	mwork_phone = fields.Char(string='Work Phone', track_visibility='onchange', readonly=False, size=10)
	mwork_email = fields.Char(string='Work Email', track_visibility='onchange', size=240)
#     General Business Information part1
	txtRegName = fields.Char(string='Organisation Registered Name', track_visibility='onchange', size=240)
	txtTradeName = fields.Char(string='Organisation Trading Name', track_visibility='onchange', size=240)
	txtAbbrTradeName = fields.Char(string='Organisation Abbreviated Trading Name', track_visibility='onchange', size=240)
	cboOrgLegalStatus = fields.Many2one("hwseta.organisation.legal.status", string='Legal Status', track_visibility='onchange', ondelete='restrict')
	txtCompanyRegNo = fields.Char(string='Registration Number', track_visibility='onchange', size=240)
	txtVATRegNo = fields.Char(string='VAT Number', track_visibility='onchange', size=240)
	alternate_acc_number = fields.Char(string='Accreditation Number', track_visibility='onchange', size=240)
	material = fields.Selection([
		   ('own_material', 'Own Material'),
		   ('hwseta_material', 'HWSETA Material'),
		], string='Material', default='own_material',
		track_visibility='onchange')
	cboOrgSICCode = fields.Char(string='SIC Code', track_visibility='onchange', ondelete='restrict')
	txtSDLNo = fields.Char(string='SDL Number', track_visibility='onchange', size=240)
	cboTHETAChamberSelect = fields.Many2one("hwseta.chamber.master", string='HWSETA Chamber', track_visibility='onchange', ondelete='restrict')
	cboProviderFocus = fields.Many2one("hwseta.provider.focus.master", string='Provider Focus', track_visibility='onchange', ondelete='restrict')
	txtNumYearsCurrentBusiness = fields.Selection([
		   ('0', '0'),
		   ('1', '1'),
		   ('2', '2'),
		   ('3', '3'),
		   ('4', '4'),
		   ('5', '5'),
		   ('6', '6'),
		   ('7', '7'),
		   ('8', '8'),
		   ('9', '9'),
		   ('10', '10'),
		   ('10+', '10+'),
		], string='Years in Business', track_visibility='onchange', size=240)
	txtNumStaffMembers = fields.Char(string='Number of full time staff members', track_visibility='onchange', size=240)
#     General Business Information part1
	txtContactNameSurname = fields.Char(string='Contact Person Name & Surname', track_visibility='onchange', size=240)
	txtContactDesignation = fields.Char(string='Contact Person Designation', track_visibility='onchange', size=240)
	txtContactTel = fields.Char(string='Telephone / Cell Phone', track_visibility='onchange', size=10)
	txtContactFax = fields.Char(string='Fax', track_visibility='onchange', size=10)
	txtContactEmail = fields.Char('Email Address', size=240)
	cboContactStatus = fields.Many2one("hwseta.relation.to.provider.status", string='Status in relation to provider', track_visibility='onchange', ondelete='restrict')
	txtAltContactNameSurname = fields.Char(string='Contact Person Name & Surname', track_visibility='onchange', size=240)
	txtAltContactDesignation = fields.Char(string='Contact Person Designation', track_visibility='onchange', size=240)
	txtAltContactTel = fields.Char(string='Telephone / Cell Phone', track_visibility='onchange', size=10)
	txtAltContactFax = fields.Char(string='Fax ', track_visibility='onchange', size=10)
	txtAltContactEmail = fields.Char(string='Email Address', track_visibility='onchange', size=240)
	cboAltContactStatus = fields.Many2one("hwseta.relation.to.provider.status", string='Status in relation to provider', track_visibility='onchange', ondelete='restrict')
#     General Site Information part1
	txtPhysicalAddressLine1 = fields.Char(string='Line1', track_visibility='onchange', size=240)
	txtPhysicalAddressLine2 = fields.Char(string='Line2', track_visibility='onchange', size=240)
	txtPhysicalAddressLine3 = fields.Char(string='Line3', track_visibility='onchange', size=240)
	txtPhysicalCode = fields.Char(string='Code', track_visibility='onchange', size=240)
	txtPostalAddressLine1 = fields.Char(string='Line1', track_visibility='onchange', size=240)
	txtPostalAddressLine2 = fields.Char(string='Line2', track_visibility='onchange', size=240)
	txtPostalAddressLine3 = fields.Char(string='Line3', track_visibility='onchange', size=240)
	txtPostalCode = fields.Char(string='Code', track_visibility='onchange', size=240)
	city_physical = fields.Many2one('res.city', string='City', track_visibility='onchange')
	city_postal = fields.Many2one('res.city', string='City', track_visibility='onchange')
	zip_physical = fields.Char(string='Zip', track_visibility='onchange')
	zip_postal = fields.Char(string='Zip', track_visibility='onchange')
	country_code_physical = fields.Many2one('res.country', string='Physical Country Code', track_visibility='onchange')
	country_code_postal = fields.Many2one('res.country', string='Postal Country Code', track_visibility='onchange')
	province_code_physical = fields.Many2one('res.country.state', string='Physical Province Code', track_visibility='onchange')
	province_code_postal = fields.Many2one('res.country.state', string='Postal Province Code', track_visibility='onchange')
	txtTelNo = fields.Char(string='TelNo', track_visibility='onchange', size=240)
	txtFaxNo = fields.Char(string='FaxNo', track_visibility='onchange', size=10)
	txtEmail = fields.Char(string='Email', track_visibility='onchange', size=240)
	txtWebSite = fields.Char(string='WebSite', track_visibility='onchange', size=240)
#     General Site Information part2
	optYesNo = fields.Boolean('Organisation ever applied to another SETA or ETQA for accreditation?')
	cboSETA = fields.Many2one("hwseta.master", string='Please indicate which SETA or ETQA:', track_visibility='onchange', ondelete='restrict')
	txtStateAccNumber = fields.Char(string='State Accreditation number', track_visibility='onchange', size=240)
	optAccStatus = fields.Char(string='Accreditation Status', track_visibility='onchange', size=240)
	txtTags = fields.Char(string='Tags', track_visibility='onchange', size=240)
	txtWorkEmail = fields.Char(string='WorkEmail', track_visibility='onchange', size=240)
	txtWorkPhone = fields.Char(string='WorkPhone', track_visibility='onchange', size=10)
	SICCode = fields.Char(string='SICCode', track_visibility='onchange', size=240)
	AccreditationStatus = fields.Char(string='AccreditationStatus', track_visibility='onchange', size=240)
	cmdNext = fields.Char(string='cmdNext', track_visibility='onchange', size=240)
	OrgLegalStatus = fields.Char(string='OrgLegalStatus', track_visibility='onchange', size=240)
	AppliedToAnotherSETA = fields.Char(string='AppliedToAnotherSETA', track_visibility='onchange', size=240)
	same_as_home = fields.Boolean(string='Same As Home Address')
	qualification_ids = fields.One2many('accreditation.qualification', 'accreditation_qualification_id', 'Qualification Lines')
	assessors_ids = fields.One2many('etqe.assessors.provider.accreditation.rel', 'ass_provider_id', 'Assessors')
	moderators_ids = fields.One2many('etqe.moderators.provider.accreditation.rel', 'mo_provider_id', 'Moderators')
	# status One2many field in provider.accreditation
	provider_accreditation_status_ids = fields.One2many('provider.accreditation.status', 'pro_acc_status_ids', 'Status')
	comment_box = fields.Text(string="Status Comment")
	# # Document Uploads
	cipro_documents = fields.Many2one('ir.attachment', string='CIPC/DSD Documents')
	tax_clearance = fields.Many2one('ir.attachment', string='Tax Clearance')
	director_cv = fields.Many2one('ir.attachment', string='Director C.V')
	certified_copies_of_qualifications = fields.Many2one('ir.attachment', string='Certified copies of Qualifications')
	lease_agreement_document = fields.Many2one('ir.attachment', string='Ownership or Lease Agreement')
	professional_body_registration = fields.Many2one('ir.attachment', string='Professional Body Registration')
	workplace_agreement = fields.Many2one('ir.attachment', string='Workplace Agreement')
	business_residence_proof = fields.Many2one('ir.attachment', string='Business Visa/Passport/Permanent residence')
	provider_learning_material = fields.Many2one('ir.attachment', string='Learning Programme Approval Report')
	skills_programme_registration_letter = fields.Many2one('ir.attachment', string='Skills Programme Registration Letter')
	company_profile_and_organogram = fields.Many2one('ir.attachment', string='Company Profile  and organogram')
	quality_management_system = fields.Many2one('ir.attachment', string='Quality Management System (QMS)')
	cipro_documents_bool = fields.Boolean(string='Verify')
	tax_clearance_bool = fields.Boolean(string='Verify')
	director_cv_bool = fields.Boolean(string='Verify')
	certified_copies_of_qualifications_bool = fields.Boolean(string='Verify')
	lease_agreement_document_bool = fields.Boolean(string='Verify')
	professional_body_registration_bool = fields.Boolean(string='Verify')
	workplace_agreement_bool = fields.Boolean(string='Verify')
	business_residence_proof_bool = fields.Boolean(string='Verify')
	provider_learning_material_bool = fields.Boolean(string='Verify')
	skills_programme_registration_letter_bool = fields.Boolean(string='Verify')
	company_profile_and_organogram_bool = fields.Boolean(string='Verify')
	quality_management_system_bool = fields.Boolean(string='Verify')
	skills_programme_ids = fields.One2many('skills.programme.accreditation.rel', 'skills_programme_accreditation_rel_id', 'Skills Programme Lines')
	learning_programme_ids = fields.One2many('learning.programme.accreditation.rel', 'learning_programme_accreditation_rel_id', 'Learning Programme Lines')

	accreditation_state = fields.Selection([
		   ('draft', 'Draft'),
		   ('submit', 'Submit'),
		], string='Status', index=True, readonly=True, default='draft',
		track_visibility='onchange', copy=False)
	empl_sic_code_id = fields.Many2one('hwseta.sic.master', string='SIC Code ID')
	acc_multi_doc_upload_ids = fields.One2many('acc.multi.doc.upload', 'pro_acc_id', string='Other Documents', help='Upload Document')
	site_visit_image = fields.One2many('site.visit.upload', 'pro_acc_id', string='Site Visit Image Upload', help='Image Upload Document')
	final_state = fields.Char("Status")
	provider_approval_date = fields.Date(string='Provider Approval Date')
	provider_register_date = fields.Date(string='Provider Accreditation Date')
	provider_expiry_date = fields.Date(string='Provider Accreditation Date')
	_sql_constraints = [('txtVATRegNo_uniq', 'unique(txtVATRegNo)',
			'VAT Registration Number must be unique!'), ]

	@api.multi
	def onchange_is_existing_provider(self, is_existing_provider):
		res = {}
		if is_existing_provider:
			res.update({'value':{ 'is_extension_of_scope' : False, 'accreditation_number':self.env['res.users'].browse(self._uid).partner_id.provider_accreditation_num}})
		return res

	@api.multi
	def onchange_is_extension_of_scope(self, is_extension_of_scope):
		res = {}
		if is_extension_of_scope:
			res.update({'value':{ 'is_existing_provider' : False, 'accreditation_number':self.env['res.users'].browse(self._uid).partner_id.provider_accreditation_num}})
		return res

	@api.multi
	def onchange_accreditation_number(self, accreditation_number, is_existing_provider, is_extension_of_scope):
		res = {}
		if accreditation_number is None:
			return res
		if accreditation_number:
			if is_extension_of_scope:
				provider_acc_obj = self.env['provider.accreditation'].search([('accreditation_number', '=', accreditation_number),('is_extension_of_scope', '=', True),('approved', '=', False),('final_state', '!=', 'Rejected')])
				if provider_acc_obj:
					return {'value': {'accreditation_number': '','is_extension_of_scope': False},'warning':{'title':'Duplicate Entry','message':'You have already applied for extension of scope.'}}
				else:
					provider_objects = self.env['res.partner'].search([('is_active_provider','=',True),('provider_accreditation_num', '=', accreditation_number)])
					if not provider_objects:
						return {'value': {'accreditation_number': '', 'is_extension_of_scope': False }, 'warning':{'title':'Invalid Accreditation Number','message':'Please Enter Correct Accreditation Number of Active Provider!!'}}
					elif provider_objects:
						pro_lst = []
						for pro_obj in provider_objects:
							pro_lst.append(pro_obj.id)
						provider_obj = self.env['res.partner'].search([('id', '=', max(pro_lst))])
						if is_existing_provider and str(datetime.today().date()) < provider_obj.provider_end_date:
							raise Warning(_("You have already accreditated, Your end date is %s.") % (provider_obj.provider_end_date))
						# To fetch qualifications from provider master
						q_vals_line, skills_vals_line, lp_vals_line, assessors_line, moderators_line = [], [], [], [], []
						if provider_obj.qualification_ids:
							for q_lines in provider_obj.qualification_ids:
								if q_lines.status == 'approved':
									qual_master_obj = self.env['provider.qualification'].search([('id','=',q_lines.qualification_id.id),('seta_branch_id','=','11')])
									if qual_master_obj:
										accreditation_qualification_line = []
										for lines in q_lines.qualification_line:
											for data in lines:
												val = {
													 'name':data.name,
													 'type':data.type,
													 'id_data':data.id_data,
													 'title':data.title,
													 'level1':data.level1,
													 'level2':data.level2,
													 'level3': data.level3,
													 'selection':data.selection,
													 'is_seta_approved':data.is_seta_approved,
													 'is_provider_approved':data.is_provider_approved,
													}
												accreditation_qualification_line.append((0, 0, val))
										q_vals = {
													'qualification_id':qual_master_obj.id,
													'saqa_qual_id':qual_master_obj.saqa_qual_id,
													'minimum_credits': qual_master_obj.m_credits,
													'qualification_line':accreditation_qualification_line,
													'assessors_id':q_lines.assessors_id.id,
													'assessor_no': q_lines.assessor_no,
													'moderator_no': q_lines.moderator_no,
													'moderators_id':q_lines.moderators_id.id,
													'assessor_sla_document':q_lines.assessor_sla_document.id,
													'moderator_sla_document':q_lines.moderator_sla_document.id,
													}
										q_vals_line.append((0, 0, q_vals))
						# To fetch skills programme from provider master
						if provider_obj.skills_programme_ids:
							for skills_lines in provider_obj.skills_programme_ids:
								if skills_lines.status == 'approved':
									skill_master_obj = self.env['skills.programme'].search([('id','=',skills_lines.skills_programme_id.id),('seta_branch_id','=','11')])
									if skill_master_obj:
										accreditation_skill_line = []
										for lines in skills_lines.unit_standards_line:
											for data in lines:
												if data.selection:
													val = {
														 'name':data.name,
														 'type':data.type,
														 'id_no':data.id_no,
														 'title':data.title,
														 'level1':data.level1,
														 'level2':data.level2,
														 'level3': data.level3,
														 'selection':data.selection,
														}
													accreditation_skill_line.append((0, 0, val))
										s_vals = {
													'skills_programme_id':skill_master_obj.id,
													'saqa_skill_id':skill_master_obj.saqa_qual_id,
													'unit_standards_line':accreditation_skill_line,
													'assessors_id':skills_lines.assessors_id.id,
													'moderators_id':skills_lines.moderators_id.id,
													'assessor_no': skills_lines.assessor_no,
													'moderator_no': skills_lines.moderator_no,
													'assessor_sla_document':skills_lines.assessor_sla_document.id,
													'moderator_sla_document':skills_lines.moderator_sla_document.id,
													}
										skills_vals_line.append((0, 0, s_vals))
						# To fetch Learning programme from provider master
						if provider_obj.learning_programme_ids:
							for lp_lines in provider_obj.learning_programme_ids:
								if lp_lines.status == 'approved':
									lp_master_obj = self.env['etqe.learning.programme'].search([('id','=',lp_lines.learning_programme_id.id),('seta_branch_id','=','11')])
									if lp_master_obj:
										accreditation_lp_line = []
										for lines in lp_lines.unit_standards_line:
											for data in lines:
												if data.selection:
													val = {
														 'name':data.name,
														 'type':data.type,
														 'id_no':data.id_no,
														 'title':data.title,
														 'level1':data.level1,
														 'level2':data.level2,
														 'level3': data.level3,
														 'selection':data.selection,
														 'seta_approved_lp':data.seta_approved_lp,
														 'provider_approved_lp':data.provider_approved_lp,
														}
													accreditation_lp_line.append((0, 0, val))
										s_vals = {
													'learning_programme_id':lp_master_obj.id,
													'saqa_qual_id':lp_master_obj.saqa_qual_id,
													'unit_standards_line':accreditation_lp_line,
													'assessors_id':lp_lines.assessors_id.id,
													'moderators_id':lp_lines.moderators_id.id,
													'assessor_no': lp_lines.assessor_no,
													'moderator_no': lp_lines.moderator_no,
													'assessor_sla_document':lp_lines.assessor_sla_document.id,
													'moderator_sla_document':lp_lines.moderator_sla_document.id,
													}
										lp_vals_line.append((0, 0, s_vals))
						# To fetch assessors from provider master
						assessors_line = []
						if provider_obj.assessors_ids:
							for as_line in provider_obj.assessors_ids:
								val = {
									   'identification_id':as_line.identification_id,
									   'assessors_id':as_line.assessors_id.id,
									   'awork_email':as_line.awork_email,
									   'awork_phone':as_line.awork_phone,
									   'assessor_sla_document':as_line.assessor_sla_document,
									   'assessor_notification_letter':as_line.assessor_notification_letter,
									   }
								assessors_line.append((0, 0, val))
						print "assessors_line====", assessors_line
						# To fetch moderators from provider master
						if provider_obj.moderators_ids:
							for mo_line in provider_obj.moderators_ids:
								val = {
									   'identification_id':mo_line.identification_id,
									   'moderators_id':mo_line.moderators_id.id,
									   'mwork_email':mo_line.mwork_email,
									   'mwork_phone':mo_line.mwork_phone,
									   'moderator_sla_document':mo_line.moderator_sla_document,
									   'moderator_notification_letter':mo_line.moderator_notification_letter,
									   }
								moderators_line.append((0, 0, val))
						partner_vals = {
								'name':provider_obj.name,
								'txtTradeName':provider_obj.provider_trading_name,
								'street': provider_obj.street,
								'street2': provider_obj.street2,
								'street3': provider_obj.street3,
								'zip':provider_obj.zip,
								'city': provider_obj.city and provider_obj.city.id,
								'state_id':provider_obj.state_id and provider_obj.state_id.id,
								'country_id':provider_obj.country_id and provider_obj.country_id.id,
								'email':provider_obj.email,
								'phone': provider_obj.phone,
								'mobile':provider_obj.mobile,
								'qualification_id':provider_obj.qualification_id and provider_obj.qualification_id.id,
								'txtPhysicalAddressLine1':provider_obj.physical_address_1,
								'txtPhysicalAddressLine2':provider_obj.physical_address_2,
								'txtPhysicalAddressLine3':provider_obj.physical_address_3,
								'image':provider_obj.image,
								'txtRegName':provider_obj.txtRegName,
								'txtTradeName':provider_obj.txtTradeName,
								'txtAbbrTradeName':provider_obj.txtAbbrTradeName,
								'cboOrgLegalStatus':provider_obj.cboOrgLegalStatus and provider_obj.cboOrgLegalStatus.id,
								'txtCompanyRegNo':provider_obj.txtCompanyRegNo,
								'txtVATRegNo':provider_obj.txtVATRegNo,
								'cboOrgSICCode':provider_obj.cboOrgSICCode,
								'txtSDLNo':provider_obj.txtSDLNo,
								'cboTHETAChamberSelect':provider_obj.cboTHETAChamberSelect and provider_obj.cboTHETAChamberSelect.id,
								'cboProviderFocus':provider_obj.cboProviderFocus and provider_obj.cboProviderFocus.id,
								'txtNumYearsCurrentBusiness':provider_obj.txtNumYearsCurrentBusiness,
								'txtNumStaffMembers':provider_obj.txtNumStaffMembers,
								'txtStateAccNumber':provider_obj.txtStateAccNumber,
								'optAccStatus':provider_obj.optAccStatus,
								'StatusReason':provider_obj.StatusReason,
								'SICCode':provider_obj.SICCode,
								'AccreditationStatus':provider_obj.AccreditationStatus,
								'cmdNext':provider_obj.cmdNext,
								'txtWorkEmail':provider_obj.txtWorkEmail,
								'OrgLegalStatus':provider_obj.OrgLegalStatus,
								'txtWorkPhone':provider_obj.txtWorkPhone,
								'AppliedToAnotherSETA':provider_obj.AppliedToAnotherSETA,
								'optYesNo':provider_obj.optYesNo,
								'cboSETA':provider_obj.cboSETA and self.cboSETA.id,
								'SICCode':provider_obj.provider_sic_code,
								'provider_sars_number':provider_obj.txtSDLNo,
								'cboOrgSICCode':provider_obj.provider_sic_code,
								'txtPhysicalAddressLine1': provider_obj.physical_address_1,
								'txtPhysicalAddressLine2': provider_obj.physical_address_2,
								'txtPhysicalAddressLine3': provider_obj.physical_address_3,
								'txtPostalAddressLine1': provider_obj.postal_address_1,
								'txtPostalAddressLine2': provider_obj.postal_address_2,
								'txtPostalAddressLine3': provider_obj.postal_address_3,
								'city_physical' : provider_obj.city_physical and provider_obj.city_physical.id,
								'city_postal' :   provider_obj.city_postal and provider_obj.city_postal.id,
								'zip_physical' : provider_obj.zip_physical,
								'zip_postal' : provider_obj.zip_postal,
								'country_code_physical' : provider_obj.country_code_physical and provider_obj.country_code_physical.id,
								'country_code_postal' : provider_obj.country_code_postal and provider_obj.country_code_postal.id,
								'province_code_physical' : provider_obj.province_code_physical and provider_obj.province_code_physical.id,
								'province_code_postal' : provider_obj.province_code_postal and provider_obj.province_code_postal.id,
								'provider_suburb' : provider_obj.suburb and provider_obj.suburb.id,
								'provider_physical_suburb' : provider_obj.provider_physical_suburb and provider_obj.provider_physical_suburb.id,
								'provider_postal_suburb' : provider_obj.provider_postal_suburb and provider_obj.provider_postal_suburb.id,
								'active' : True,
								'website': provider_obj.website,
								'fax': provider_obj.fax,
								'material':provider_obj.material,
								'alternate_acc_number':provider_obj.alternate_acc_number,
								'qualification_ids':q_vals_line,
								'skills_programme_ids':skills_vals_line,
								'learning_programme_ids':lp_vals_line,
								'assessors_ids': assessors_line,
								'moderators_ids': moderators_line,
								'related_provider':provider_obj.id,
						}
						if not is_existing_provider:
							partner_vals.update({
									'cipro_documents': provider_obj.cipro_documents and provider_obj.cipro_documents.id,
									'tax_clearance': provider_obj.tax_clearance and provider_obj.tax_clearance.id,
									'lease_agreement_document':provider_obj.lease_agreement_document and provider_obj.lease_agreement_document.id,
									'director_cv': provider_obj.director_cv and provider_obj.director_cv.id,
									'certified_copies_of_qualifications': provider_obj.certified_copies_of_qualifications and provider_obj.certified_copies_of_qualifications.id,
									'professional_body_registration': provider_obj.professional_body_registration and provider_obj.professional_body_registration.id,
									'workplace_agreement': provider_obj.workplace_agreement and provider_obj.workplace_agreement.id,
									'business_residence_proof': provider_obj.business_residence_proof and provider_obj.business_residence_proof.id,
									'provider_learning_material': provider_obj.provider_learning_material and provider_obj.provider_learning_material.id,
									'skills_programme_registration_letter': provider_obj.skills_programme_registration_letter and provider_obj.skills_programme_registration_letter.id,
									'company_profile_and_organogram' : provider_obj.company_profile_and_organogram and provider_obj.company_profile_and_organogram.id,
									'quality_management_system' : provider_obj.quality_management_system and provider_obj.quality_management_system.id,
								 })
						res.update({'value': partner_vals})
			elif is_existing_provider:
				provider_acc_obj = self.env['provider.accreditation'].search([('accreditation_number', '=', accreditation_number),('is_existing_provider', '=', True),('approved', '=', False),('final_state', '!=', 'Rejected')])
				if provider_acc_obj:
					return {'value': {'accreditation_number': '', 'is_existing_provider': False},'warning':{'title':'Duplicate Entry','message':'You have already applied for Re-registration.'}}
				provider_objects = self.env['res.partner'].search([('provider_accreditation_num', '=', accreditation_number)])
				if not provider_objects:
					return {'value': {'accreditation_number': '', 'is_existing_provider': False }, 'warning':{'title':'Invalid Accreditation Number','message':'Please Enter Valid Accreditation Number!!'}}
				elif provider_objects:
					pro_lst = []
					for pro_obj in provider_objects:
						pro_lst.append(pro_obj.id)
					provider_obj = self.env['res.partner'].search([('id', '=', max(pro_lst))])
					# commented for now but needs to write logic to get 60 days old date
#                     if is_existing_provider and str(datetime.today().date()) < provider_obj.provider_end_date:
#                         raise Warning(_("You are already accreditated, Your end date is %s.") % (provider_obj.provider_end_date))
					# To fetch qualifications from provider master
					q_vals_line, skills_vals_line, lp_vals_line, assessors_line, moderators_line = [], [], [], [], []
					if provider_obj.qualification_ids:
						for q_lines in provider_obj.qualification_ids:
							if q_lines.status == 'approved':
								qual_master_obj = self.env['provider.qualification'].search([('id','=',q_lines.qualification_id.id),('seta_branch_id','=','11')])
								if qual_master_obj:
									accreditation_qualification_line = []
									for lines in q_lines.qualification_line:
										for data in lines:
											val = {
												 'name':data.name,
												 'type':data.type,
												 'id_no':data.id_data,
												 'title':data.title,
												 'level1':data.level1,
												 'level2':data.level2,
												 'level3': data.level3,
												 'selection':data.selection,
												 'is_seta_approved':data.is_seta_approved,
												 'is_provider_approved':data.is_provider_approved,
												}
											accreditation_qualification_line.append((0, 0, val))
									q_vals = {
												'qualification_id':qual_master_obj.id,
												'saqa_qual_id':qual_master_obj.saqa_qual_id,
												'minimum_credits': qual_master_obj.m_credits,
												'qualification_line':accreditation_qualification_line,
												'assessors_id':q_lines.assessors_id.id,
												'moderators_id':q_lines.moderators_id.id,
												'assessor_no': q_lines.assessor_no,
												'moderator_no': q_lines.moderator_no,
												'assessor_sla_document':q_lines.assessor_sla_document.id,
												'moderator_sla_document':q_lines.moderator_sla_document.id,
												}
									q_vals_line.append((0, 0, q_vals))
					# To fetch skills programme from provider master
					if provider_obj.skills_programme_ids:
						for skills_lines in provider_obj.skills_programme_ids:
							if skills_lines.status == 'approved':
								skill_master_obj = self.env['skills.programme'].search([('id','=',skills_lines.skills_programme_id.id),('seta_branch_id','=','11')])
								if skill_master_obj:
									accreditation_skill_line = []
									for lines in skills_lines.unit_standards_line:
										for data in lines:
											if data.selection:
												val = {
													 'name':data.name,
													 'type':data.type,
													 'id_no':data.id_no,
													 'title':data.title,
													 'level1':data.level1,
													 'level2':data.level2,
													 'level3': data.level3,
													 'selection':data.selection,
													}
												accreditation_skill_line.append((0, 0, val))
									s_vals = {
												'skills_programme_id':skill_master_obj.id,
												'saqa_skill_id':skill_master_obj.saqa_qual_id,
												'unit_standards_line':accreditation_skill_line,
												'assessors_id':skills_lines.assessors_id.id,
												'moderators_id':skills_lines.moderators_id.id,
												'assessor_no': skills_lines.assessor_no,
												'moderator_no': skills_lines.moderator_no,
												'assessor_sla_document':skills_lines.assessor_sla_document.id,
												'moderator_sla_document':skills_lines.moderator_sla_document.id,
												}
									skills_vals_line.append((0, 0, s_vals))
					# To fetch Learning programme from provider master
					if provider_obj.learning_programme_ids:
						for lp_lines in provider_obj.learning_programme_ids:
							if lp_lines.status == 'approved':
								lp_master_obj = self.env['etqe.learning.programme'].search([('id','=',lp_lines.learning_programme_id.id),('seta_branch_id','=','11')])
								if lp_master_obj:
									accreditation_lp_line = []
									for lines in lp_master_obj.unit_standards_line:
										for data in lines:
											if data.selection:
												val = {
													 'name':data.name,
													 'type':data.type,
													 'id_no':data.id_no,
													 'title':data.title,
													 'level1':data.level1,
													 'level2':data.level2,
													 'level3': data.level3,
													 'selection':data.selection,
													 'seta_approved_lp':data.seta_approved_lp,
													 'provider_approved_lp':data.provider_approved_lp,
													}
												accreditation_lp_line.append((0, 0, val))
									s_vals = {
												'learning_programme_id':lp_master_obj.id,
												'saqa_qual_id':lp_master_obj.saqa_qual_id,
												'unit_standards_line':accreditation_lp_line,
												'assessors_id':lp_lines.assessors_id.id,
												'moderators_id':lp_lines.moderators_id.id,
												'assessor_no': lp_lines.assessor_no,
												'moderator_no': lp_lines.moderator_no,
												'assessor_sla_document':lp_lines.assessor_sla_document.id,
												'moderator_sla_document':lp_lines.moderator_sla_document.id,
												}
									lp_vals_line.append((0, 0, s_vals))
					# To fetch assessors from provider master
					assessors_line = []
					if provider_obj.assessors_ids:
						for as_line in provider_obj.assessors_ids:
							val = {
								   'identification_id':as_line.identification_id,
								   'assessors_id':as_line.assessors_id.id,
								   'awork_email':as_line.awork_email,
								   'awork_phone':as_line.awork_phone,
								   'assessor_sla_document':as_line.assessor_sla_document,
								   'assessor_notification_letter':as_line.assessor_notification_letter,
								   }
							assessors_line.append((0, 0, val))
					# To fetch moderators from provider master
					if provider_obj.moderators_ids:
						for mo_line in provider_obj.moderators_ids:
							val = {
								   'identification_id':mo_line.identification_id,
								   'moderators_id':mo_line.moderators_id.id,
								   'mwork_email':mo_line.mwork_email,
								   'mwork_phone':mo_line.mwork_phone,
								   'moderator_sla_document':mo_line.moderator_sla_document,
								   'moderator_notification_letter':mo_line.moderator_notification_letter,
								   }
							moderators_line.append((0, 0, val))
					partner_vals = {
							'name':provider_obj.name,
							'txtTradeName':provider_obj.provider_trading_name,
							'street': provider_obj.street,
							'street2': provider_obj.street2,
							'street3': provider_obj.street3,
							'zip':provider_obj.zip,
							'city': provider_obj.city and provider_obj.city.id,
							'state_id':provider_obj.state_id and provider_obj.state_id.id,
							'country_id':provider_obj.country_id and provider_obj.country_id.id,
							'email':provider_obj.email,
							'phone': provider_obj.phone,
							'mobile':provider_obj.mobile,
							'qualification_id':provider_obj.qualification_id and provider_obj.qualification_id.id,
							'txtPhysicalAddressLine1':provider_obj.physical_address_1,
							'txtPhysicalAddressLine2':provider_obj.physical_address_2,
							'txtPhysicalAddressLine3':provider_obj.physical_address_3,
							'image':provider_obj.image,
							'txtRegName':provider_obj.txtRegName,
							'txtTradeName':provider_obj.txtTradeName,
							'txtAbbrTradeName':provider_obj.txtAbbrTradeName,
							'cboOrgLegalStatus':provider_obj.cboOrgLegalStatus and provider_obj.cboOrgLegalStatus.id,
							'txtCompanyRegNo':provider_obj.txtCompanyRegNo,
							'txtVATRegNo':provider_obj.txtVATRegNo,
							'cboOrgSICCode':provider_obj.cboOrgSICCode,
							'txtSDLNo':provider_obj.txtSDLNo,
							'cboTHETAChamberSelect':provider_obj.cboTHETAChamberSelect and provider_obj.cboTHETAChamberSelect.id,
							'cboProviderFocus':provider_obj.cboProviderFocus and provider_obj.cboProviderFocus.id,
							'txtNumYearsCurrentBusiness':provider_obj.txtNumYearsCurrentBusiness,
							'txtNumStaffMembers':provider_obj.txtNumStaffMembers,
							'txtStateAccNumber':provider_obj.txtStateAccNumber,
							'optAccStatus':provider_obj.optAccStatus,
							'StatusReason':provider_obj.StatusReason,
							'SICCode':provider_obj.SICCode,
							'AccreditationStatus':provider_obj.AccreditationStatus,
							'cmdNext':provider_obj.cmdNext,
							'txtWorkEmail':provider_obj.txtWorkEmail,
							'OrgLegalStatus':provider_obj.OrgLegalStatus,
							'txtWorkPhone':provider_obj.txtWorkPhone,
							'AppliedToAnotherSETA':provider_obj.AppliedToAnotherSETA,
							'optYesNo':provider_obj.optYesNo,
							'cboSETA':provider_obj.cboSETA and self.cboSETA.id,
							'SICCode':provider_obj.provider_sic_code,
							'provider_sars_number':provider_obj.txtSDLNo,
							'cboOrgSICCode':provider_obj.provider_sic_code,
							'txtPhysicalAddressLine1': provider_obj.physical_address_1,
							'txtPhysicalAddressLine2': provider_obj.physical_address_2,
							'txtPhysicalAddressLine3': provider_obj.physical_address_3,
							'txtPostalAddressLine1': provider_obj.postal_address_1,
							'txtPostalAddressLine2': provider_obj.postal_address_2,
							'txtPostalAddressLine3': provider_obj.postal_address_3,
							'city_physical' : provider_obj.city_physical and provider_obj.city_physical.id,
							'city_postal' :   provider_obj.city_postal and provider_obj.city_postal.id,
							'zip_physical' : provider_obj.zip_physical,
							'zip_postal' : provider_obj.zip_postal,
							'country_code_physical' : provider_obj.country_code_physical and provider_obj.country_code_physical.id,
							'country_code_postal' : provider_obj.country_code_postal and provider_obj.country_code_postal.id,
							'province_code_physical' : provider_obj.province_code_physical and provider_obj.province_code_physical.id,
							'province_code_postal' : provider_obj.province_code_postal and provider_obj.province_code_postal.id,
							'provider_suburb' : provider_obj.suburb and provider_obj.suburb.id,
							'provider_physical_suburb' : provider_obj.provider_physical_suburb and provider_obj.provider_physical_suburb.id,
							'provider_postal_suburb' : provider_obj.provider_postal_suburb and provider_obj.provider_postal_suburb.id,
							'active' : True,
							'website': provider_obj.website,
							'fax': provider_obj.fax,
							'material':provider_obj.material,
							'alternate_acc_number':provider_obj.alternate_acc_number,
							'qualification_ids':q_vals_line,
							'skills_programme_ids':skills_vals_line,
							'learning_programme_ids':lp_vals_line,
							'assessors_ids':assessors_line,
							'moderators_ids':moderators_line,
							'related_provider':provider_obj.id,
							'cipro_documents': provider_obj.cipro_documents and provider_obj.cipro_documents.id,
							'tax_clearance': provider_obj.tax_clearance and provider_obj.tax_clearance.id,
							'lease_agreement_document':provider_obj.lease_agreement_document and provider_obj.lease_agreement_document.id,
							'director_cv': provider_obj.director_cv and provider_obj.director_cv.id,
							'certified_copies_of_qualifications': provider_obj.certified_copies_of_qualifications and provider_obj.certified_copies_of_qualifications.id,
							'professional_body_registration': provider_obj.professional_body_registration and provider_obj.professional_body_registration.id,
							'workplace_agreement': provider_obj.workplace_agreement and provider_obj.workplace_agreement.id,
							'business_residence_proof': provider_obj.business_residence_proof and provider_obj.business_residence_proof.id,
							'provider_learning_material': provider_obj.provider_learning_material and provider_obj.provider_learning_material.id,
							'skills_programme_registration_letter': provider_obj.skills_programme_registration_letter and provider_obj.skills_programme_registration_letter.id,
							'company_profile_and_organogram' : provider_obj.company_profile_and_organogram and provider_obj.company_profile_and_organogram.id,
							'quality_management_system' : provider_obj.quality_management_system and provider_obj.quality_management_system.id,
					}
					res.update({'value':partner_vals})
		return res

	@api.multi
	def onchange_sic_code_id(self, empl_sic_code_id):
		res = {}
		if not empl_sic_code_id :
			return res
		sic_code_data = self.env['hwseta.sic.master'].browse(empl_sic_code_id)
		if sic_code_data:
			res.update({'value':{ 'cboOrgSICCode' : sic_code_data[0].code }})
		return res

	@api.multi
	def onchange_sic_code(self,cboOrgSICCode):
		res = {}
		if not cboOrgSICCode:
			return res
		sic_code_data = self.env['hwseta.sic.master'].search([('code','=',cboOrgSICCode)])
		if sic_code_data:
				res.update({'value':{ 'empl_sic_code_id' : sic_code_data[0].id }})
		else:
			return {'value':{'cboOrgSICCode':''},'warning':{'title':'Invalid SIC Code','message':'Please enter valid SIC Code!'}}
		return res

	@api.multi
	def onchange_provider_postal_suburb(self, person_postal_suburb):
		res = {}
		if not person_postal_suburb:
			return res
		if person_postal_suburb:
			sub_res = self.env['res.suburb'].browse(person_postal_suburb)
			res.update({'value':{'zip_postal':sub_res.postal_code, 'city_postal':sub_res.city_id, 'province_code_postal':sub_res.province_id}})
		return res

	@api.multi
	def onchange_provider_physical_suburb(self, provider_physical_suburb):
		res = {}
		if not provider_physical_suburb:
			return res
		if provider_physical_suburb:
			sub_res = self.env['res.suburb'].browse(provider_physical_suburb)
			res.update({'value':{'zip_physical':sub_res.postal_code, 'city_physical':sub_res.city_id, 'province_code_physical':sub_res.province_id}})
		return res

	@api.multi
	def onchange_provider_suburb(self, provider_suburb):
		res = {}
		if not provider_suburb:
			return res
		if provider_suburb:
			sub_res = self.env['res.suburb'].browse(provider_suburb)
			res.update({'value':{'zip':sub_res.postal_code, 'city':sub_res.city_id, 'state_id':sub_res.province_id}})
		return res

	@api.multi
	def get_partner_ids(self, user_ids):
		'''Used to get Assessors Related partner'''
		if user_ids:
			ass_list = []
			for assessor in user_ids:
				if assessor.assessors_id.is_active_assessor:
					ass_list.append(str(assessor.assessors_id.user_id.partner_id.id))
			print "ass_list====", ass_list
			return str(ass_list).replace('[', '').replace(']', '').replace("'",'')

	@api.multi
	def get_mod_partner_ids(self, user_ids):
		'''Used to get Moderators Related partner'''
		if user_ids:
			mod_list = []
			for moderator in user_ids:
				if moderator.moderators_id.is_active_moderator:
					mod_list.append(str(moderator.moderators_id.user_id.partner_id.id))
			print "mod_list=====", mod_list
			return str(mod_list).replace('[', '').replace(']', '').replace("'",'')

	@api.model
	def create(self, vals):
		context = self._context
		if vals.get('is_extension_of_scope') or vals.get('is_existing_provider') :
			vals['related_provider'] = self.env['res.users'].browse(self._uid).partner_id.id
		vals['final_state'] = 'Draft'
		if not context.get('from_website', False) :
			vals['provider_register_date'] = datetime.today().date()
			vals['provider_accreditation_ref'] = self.env['ir.sequence'].get('provider.accreditation.reference')
		res = super(provider_accreditation, self).create(vals)

		if res.email:
			if '@' not in res.email:
				raise Warning(_('Please enter valid email address'))
		if res.phone:
			if not res.phone.isdigit() or len(res.phone) != 10:
				raise Warning(_('Please enter 10 digits Phone number'))
		elif not res.phone:
			raise Warning(_('Please enter Phone number'))

		if res.mobile:
			if not res.mobile.isdigit() or len(res.mobile) != 10:
				raise Warning(_('Please enter 10 digits Mobile number'))
		elif not res.mobile:
			raise Warning(_('Please enter Mobile number'))

		if res.fax:
			if not res.fax.isdigit() or len(res.fax) != 10:
				raise Warning(_('Please enter 10 digits Fax number'))
		return res

	@api.multi
	def action_submit_button(self):
		context = self._context
		qual_count = 0
		skill_count = 0
#         ass_count = 0
#         mod_count = 0
		lp_count = 0
		if context is None:
			context = {}
		if not self.is_extension_of_scope:
			if not self.tax_clearance or not self.director_cv or not self.certified_copies_of_qualifications or not self.lease_agreement_document or not self.company_profile_and_organogram or not self.quality_management_system:
				raise Warning('Please add all mandatory documents from Business Information')

			if self.material == 'own_material':
				if not self.provider_learning_material:
					raise Warning('Please add all mandatory documents from Business Information')

		if self.qualification_ids:
			for qualification in self.qualification_ids:
					if not qualification.assessors_id or not qualification.moderators_id or not qualification.assessor_sla_document or not qualification.moderator_sla_document:
						raise Warning(_("Please enter required fields of Qualifications in Main Campus before submit!"))

		if self.skills_programme_ids:
			for skill in self.skills_programme_ids:
					if not skill.assessors_id or not skill.moderators_id or not skill.assessor_sla_document or not skill.moderator_sla_document:
						raise Warning(_("Please enter required fields of Skills Programme in Main Campus before submit!"))
		if self.learning_programme_ids:
			for lp in self.learning_programme_ids:
					if not lp.assessors_id or not lp.moderators_id or not lp.assessor_sla_document or not lp.moderator_sla_document:
						raise Warning(_("Please enter required fields of Learning Programme in Main Campus before submit!"))
		if not self.is_extension_of_scope and not self.is_existing_provider:
			if self.qualification_ids or self.skills_programme_ids or self.learning_programme_ids:
				for line in self.qualification_ids:
					qual_count += 1
				for line in self.skills_programme_ids:
					skill_count += 1
				for line in self.learning_programme_ids:
					lp_count += 1
				count = qual_count + skill_count + lp_count
				if count > 3:
					raise Warning(_('Sorry! You Can Add Maximum 3 Qualifications or Skills Programme or Learning Programme in Main Campus'))
			else:
				raise Warning(_('Please Add Qualification or Skills Programme or Learning Programme in Main Campus.'))

#             if self.assessors_ids:
#                 for line in self.assessors_ids:
#                     ass_count += 1
#                 if ass_count < count:
#                     raise Warning(_('Please Add Assessors in Main Campus, Number of Assessors Should be Equal to Number of Qualifications in Main Campus. '))
#                 elif ass_count > count:
#                     raise Warning(_('Number of Assessors Should be Equal to Number of Qualifications in Main Campus.'))
#             elif self.qualification_ids:
#                 raise Warning(_('Please Add Assessors In Main Campus, Number of Assessors Should be Equal to Number of Qualifications in Main Campus.'))

#             if self.moderators_ids:
#                 for line in self.moderators_ids:
#                     mod_count += 1
#                 if mod_count < count:
#                     raise Warning(_('Please Add Moderators in Main Campus, Number of Moderators Should be Equal to Number of Qualifications in Main Campus.'))
#                 elif mod_count > count:
#                     raise Warning(_('Number of Moderators Should be Equal to Number of Qualifications in Main Campus.'))
#             elif self.qualification_ids:
#                 raise Warning(_('Please Add Moderators in Main Campus, Number of Moderators Should be Equal to Number of Qualifications in Main Campus.'))
			for line in self.qualification_ids:
				if line.qualification_id.is_exit_level_outcomes == False:
					if line.minimum_credits > line.total_credits:
						raise Warning(_("Sum of checked unit standards credits point should be greater than or equal to Minimum credits point !!"))
		if not self.phone:
			raise Warning(_('Please enter Phone number General Details'))
		if not self.mobile:
			raise Warning(_('Please enter Mobile number General Details'))
		self = self.with_context(submit=True)
		if not self.is_extension_of_scope:
			self.write({ 'submitted':True, 'accreditation_state':'submit', 'final_state':'Submitted'})
		elif self.is_extension_of_scope:
			self.write({ 'submitted':True,'evaluate':True,'validate':True, 'accreditation_state':'submit', 'final_state':'Recommended2'})
		#'state':'verification',
		# Below code is added to send email notification to linked assessors and moderators
		ir_model_data_obj = self.env['ir.model.data']
		if self.assessors_ids:
			mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_accreditation_submit_ass_linking')
			if mail_template_id:
				self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
		if self.moderators_ids:
			mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_accreditation_submit_mod_linking')
			if mail_template_id:
				self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
		mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_accreditation_submit')
		if mail_template_id:
			self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)

		self.write({'provider_accreditation_status_ids':[(0, 0, {'pa_name':self.env['res.users'].browse(self._uid).name, 'pa_date':datetime.now(), 'pa_status':'Submitted', 'pa_updation_date':self.write_date, 'pa_comment':self.comment_box})]})
		self.write({'comment_box':''})
		return True

	@api.multi
	def action_verify_button(self):
		context = self._context
		if context is None:
			context = {}
		qual_skill_lp_verify = False
		for qual in self.qualification_ids:
			if(qual.verify == True):
				qual_skill_lp_verify = True
		for skill in self.skills_programme_ids:
			if(skill.verify == True):
				qual_skill_lp_verify = True
		for lp in self.learning_programme_ids:
			if(lp.verify == True):
				qual_skill_lp_verify = True
		if qual_skill_lp_verify == False:
			raise Warning(_("Please check/verify at least one Qualification or Skills programme or Learning programme before Evaluate"))

		if not self.comment_box:
			raise Warning(_("Please enter status comment"))
		self = self.with_context(verify=True)
		self.write({'state':'evaluation', 'verify':True, 'final_state':'Evaluated'})
		if(self.cipro_documents.id != False and self.cipro_documents_bool == False and self.is_extension_of_scope == True):
			raise Warning(_("Please check CIPC/DSD Documents before Evaluate"))
		if(self.tax_clearance.id != False and self.tax_clearance_bool == False):
			raise Warning(_("Please check Tax Clearance before Evaluate"))
		if(self.director_cv.id != False and self.director_cv_bool == False):
			raise Warning(_("Please check Director C.V  before Evaluate"))
		if(self.certified_copies_of_qualifications.id != False and self.certified_copies_of_qualifications_bool == False):
			raise Warning(_("Please check Certified copies of Qualifications before Evaluate"))
		if(self.lease_agreement_document.id != False and self.lease_agreement_document_bool == False):
			raise Warning(_("Please check Ownership or Lease Agreement before Evaluate"))
		if(self.professional_body_registration.id != False and self.professional_body_registration_bool == False):
			raise Warning(_("Please check Professional Body Registration  before Evaluate"))
		if(self.workplace_agreement.id != False and self.workplace_agreement_bool == False):
			raise Warning(_("Please check Workplace Agreement before Evaluate"))
		if(self.business_residence_proof.id != False and self.business_residence_proof_bool == False):
			raise Warning(_("Please check Business Visa/Passport/Permanent residence  before Evaluate"))
		if(self.provider_learning_material.id != False and self.provider_learning_material_bool == False):
			raise Warning(_("Please check Provider Learning Material before Evaluate"))
		if(self.skills_programme_registration_letter.id != False and self.skills_programme_registration_letter_bool == False):
			raise Warning(_("Please check Skills Programme Registration letter before Evaluate"))
		if(self.company_profile_and_organogram.id != False and self.company_profile_and_organogram_bool == False):
			raise Warning(_("Please check Company Profile  and organogram before Evaluate"))
		if(self.quality_management_system.id != False and self.quality_management_system_bool == False):
			raise Warning(_("Please check Quality Management System before Evaluate"))

		ir_model_data_obj = self.env['ir.model.data']
		mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_accreditation_verify')
		if mail_template_id:
			self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)

		self.write({'provider_accreditation_status_ids':[(0, 0, {'pa_name':self.env['res.users'].browse(self._uid).name, 'pa_date':datetime.now(), 'pa_status':'Evaluated', 'pa_updation_date':self.write_date, 'pa_comment':self.comment_box})]})
		self.write({'comment_box':''})
		return True

	@api.multi
	def action_evaluate_button(self):
		context = self._context
		if context is None:
			context = {}
		if not self.comment_box:
			raise Warning(_("Please enter status comment"))
		self = self.with_context(evaluate=True)
		self.write({'state':'recommended1', 'evaluate':True, 'final_state':'Recommended'})
		'''Below 4 lines of mail template has been commented as per client request on 23rd Nov.17'''
#         ir_model_data_obj = self.env['ir.model.data']
#         mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_accreditation_evaluated')
#         if mail_template_id:
#             self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
		self.write({'provider_accreditation_status_ids':[(0, 0, {'pa_name':self.env['res.users'].browse(self._uid).name, 'pa_date':datetime.now(), 'pa_status':'Recommended', 'pa_updation_date':self.write_date, 'pa_comment':self.comment_box})]})
		self.write({'comment_box':''})
		return True

	@api.multi
	def action_recommended1_button(self):
		context = self._context
		if context is None:
			context = {}
		if not self.comment_box:
			raise Warning(_("Please enter status comment"))
		self = self.with_context(recommended1=True)
		self.write({'state':'validated', 'recommended1':True, 'final_state':'Validated'})

		'''Below 4 lines of mail template has been commented as per client request on 23rd Nov.17'''
#         ir_model_data_obj = self.env['ir.model.data']
#         mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_accreditation_evaluated')
#         if mail_template_id:
#             self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
		self.write({'provider_accreditation_status_ids':[(0, 0, {'pa_name':self.env['res.users'].browse(self._uid).name, 'pa_date':datetime.now(), 'pa_status':'Validated', 'pa_updation_date':self.write_date, 'pa_comment':self.comment_box})]})
		self.write({'comment_box':''})
		return True

	@api.multi
	def action_validate_button(self):
		context = self._context
		if context is None:
			context = {}
		if not self.comment_box:
			raise Warning(_("Please enter status comment"))
		self = self.with_context(validate=True)
		self.write({'state':'recommended2', 'validate':True, 'final_state':'Recommended2'})
		'''Below 4 lines of mail template has been commented as per client request on 23rd Nov.17'''
#         ir_model_data_obj = self.env['ir.model.data']
#         mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_accreditation_evaluated')
#         if mail_template_id:
#             self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
		self.write({'provider_accreditation_status_ids':[(0, 0, {'pa_name':self.env['res.users'].browse(self._uid).name, 'pa_date':datetime.now(), 'pa_status':'Recommended', 'pa_updation_date':self.write_date, 'pa_comment':self.comment_box})]})
		self.write({'comment_box':''})
		return True

	@api.multi
	def action_denied_button(self):
		context = self._context
		if context is None:
			context = {}
		if not self.comment_box:
			raise Warning(_("Please enter status comment"))
		self = self.with_context(submit=True)
		self.write({'state':'denied', 'denied':True, 'final_state':'Rejected'})
		ir_model_data_obj = self.env['ir.model.data']
		mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_accreditation_denied')
		if mail_template_id:
			self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
		self.write({'provider_accreditation_status_ids':[(0, 0, {'pa_name':self.env['res.users'].browse(self._uid).name, 'pa_date':datetime.now(), 'pa_status':'Rejected', 'pa_updation_date':self.write_date, 'pa_comment':self.comment_box})]})
		self.write({'comment_box':''})
		return True

	@api.multi
	def action_reevaluate_button(self):
		if not self.comment_box:
			raise Warning(_("Please enter status comment"))
		self.write({'state':'verification', 'evaluate':False, 'verify':False, 'denied':False, 'recommended1':False, 'validate':False, 'provider_accreditation_status_ids':[(0, 0, {'pa_name':self.env['res.users'].browse(self._uid).name, 'pa_date':datetime.now(), 'pa_status':'Re-Evaluated', 'pa_updation_date':self.write_date, 'pa_comment':self.comment_box})]})
		self.write({'comment_box':''})
		return True

	@api.multi
	def action_approve_button(self):
		ir_model_data_obj = self.env['ir.model.data']
		if not self.comment_box:
			raise Warning(_("Please enter status comment"))
		if (not self.is_existing_provider and not self.is_extension_of_scope) or self.is_existing_provider:
			# code for new provider registration and existing provider
			self.write({'provider_accreditation_status_ids':[(0, 0, {'pa_name':self.env['res.users'].browse(self._uid).name, 'pa_date':datetime.now(), 'pa_status':'Approved', 'pa_updation_date':self.write_date, 'pa_comment':self.comment_box})]})
			self.write({'comment_box':''})
			context = self._context
			if context is None:
				context = {}
			self = self.with_context(submit=True)
			credit_provider_contact_lines = []
			credit_provider_campus_contact_lines = []
			credit_qualification_line_lines = []
			q_vals_line = []
			s_vals_line = []
			assessors_list = []
			moderators_list = []
			lp_vals_line = []
			batch_val_list = []
			if self.qualification_ids:
				for q_lines in self.qualification_ids:
					if q_lines.verify == True:
						if q_lines.select:
							accreditation_qualification_line = []
							for lines in q_lines.qualification_line:
								for data in  lines:
									if data.selection:
										val = {
											 'name':data.name,
											 'type':data.type,
											 'id_data':data.id_no,
											 'title':data.title,
											 'level1':data.level1,
											 'level2':data.level2,
											 'level3': data.level3,
											 'is_provider_approved': data.is_provider_approved,
											 'is_seta_approved': data.is_seta_approved,
											 'selection':data.selection
											}
										accreditation_qualification_line.append((0, 0, val))
							q_vals = {
										'qualification_id':q_lines.qualification_id.id,
										'qualification_line':accreditation_qualification_line,
										'saqa_qual_id':q_lines.saqa_qual_id,
										'status':'approved',
										'approval_request':True,
										'request_send':True,
										'assessor_no': q_lines.assessor_no,
										'assessors_id':q_lines.assessors_id.id,
										'moderator_no': q_lines.moderator_no,
										'moderators_id':q_lines.moderators_id.id,
										'assessor_sla_document':q_lines.assessor_sla_document.id,
										'moderator_sla_document':q_lines.moderator_sla_document.id,
										}
							q_vals_line.append((0, 0, q_vals))
			if self.skills_programme_ids:
				for unit_standards in self.skills_programme_ids:
					if unit_standards.verify == True:
						if unit_standards.select:
							unit_standards_line = []
							for lines in unit_standards.unit_standards_line:
								for data in  lines:
									if data.selection:
										val = {
											 'name':data.name,
											 'type':data.type,
											 'id_no':data.id_no,
											 'title':data.title,
											 'level1':data.level1,
											 'level2':data.level2,
											 'level3': data.level3,
											 'selection':data.selection
											}
										unit_standards_line.append((0, 0, val))
							s_vals = {
										'skills_programme_id':unit_standards.skills_programme_id.id,
										'unit_standards_line':unit_standards_line,
										'skill_saqa_id':unit_standards.saqa_skill_id,
										'status':'approved',
										'approval_request':True,
										'request_send':True,
										'assessors_id':unit_standards.assessors_id.id,
										'assessor_no': unit_standards.assessor_no,
										'moderator_no': unit_standards.moderator_no,
										'moderators_id':unit_standards.moderators_id.id,
										'assessor_sla_document':unit_standards.assessor_sla_document.id,
										'moderator_sla_document':unit_standards.moderator_sla_document.id,
										}
							s_vals_line.append((0, 0, s_vals))
			''' LEARNING PROGRAMME START'''
			if self.learning_programme_ids:
				for unit_standards in self.learning_programme_ids:
					if unit_standards.verify == True:
						if unit_standards.select:
							unit_standards_line = []
							for lines in unit_standards.unit_standards_line:
								for data in  lines:
									if data.selection:
										val = {
											 'name':data.name,
											 'type':data.type,
											 'id_no':data.id_no,
											 'title':data.title,
											 'level1':data.level1,
											 'level2':data.level2,
											 'level3': data.level3,
											 'selection':data.selection,
											 'provider_approved_lp':data.provider_approved_lp,
											 'seta_approved_lp':data.seta_approved_lp,
											}
										unit_standards_line.append((0, 0, val))
							lp_vals = {
										'learning_programme_id':unit_standards.learning_programme_id.id,
										'unit_standards_line':unit_standards_line,
										'lp_saqa_id':unit_standards.saqa_qual_id,
										'status':'approved',
										'approval_request':True,
										'request_send':True,
										'assessors_id':unit_standards.assessors_id.id,
										'moderators_id':unit_standards.moderators_id.id,
										'assessor_no': unit_standards.assessor_no,
										'moderator_no': unit_standards.moderator_no,
										'assessor_sla_document':unit_standards.assessor_sla_document.id,
										'moderator_sla_document':unit_standards.moderator_sla_document.id,
										}
							lp_vals_line.append((0, 0, lp_vals))
			''' LEARNING PROGRAMME END'''
			if self.assessors_ids:
				for line in self.assessors_ids:
					for data in line:
						val = {
								 'search_by':'id',
								 'identification_id':data.assessors_id.assessor_moderator_identification_id,
								 'assessors_id':data.assessors_id.id,
								 'awork_phone':data.awork_phone,
								 'awork_email':data.awork_email,
								 'assessor_sla_document':data.assessor_sla_document.id,
								 'assessor_sla_document':data.assessor_sla_document.id,
								 'assessor_notification_letter':data.assessor_notification_letter.id,
								 'status':'approved',
								 'approval_request':True,
								 'request_send':True,
								}
						assessors_list.append((0, 0, val))
			if self.moderators_ids:
				for line in self.moderators_ids:
					for data in line:
						val = {
								 'search_by':'id',
								 'identification_id':data.moderators_id.assessor_moderator_identification_id,
								 'moderators_id':data.moderators_id.id,
								 'mwork_phone': data.mwork_phone,
								 'mwork_email': data.mwork_email,
								 'moderator_sla_document':data.moderator_sla_document.id,
								 'moderator_notification_letter':data.moderator_notification_letter.id,
								 'status':'approved',
								 'approval_request':True,
								 'request_send':True,
								}
						moderators_list.append((0, 0, val))
			for provider_contact_vals in self.provider_accreditation_contact_ids:
				provider_contact_data = {
									 'name':provider_contact_vals.name,
									 'sur_name':provider_contact_vals.sur_name,
									 'street':provider_contact_vals.street,
									 'street2':provider_contact_vals.street2,
									 'zip':provider_contact_vals.zip,
									 'city':provider_contact_vals.city,
									 'state_id':provider_contact_vals.state_id.id,
									 'country_id': provider_contact_vals.country_id.id,
									 'email': provider_contact_vals.email,
									 'phone':provider_contact_vals.phone,
									 'mobile': provider_contact_vals.mobile,
									 'image': provider_contact_vals.image,
									 'fax':provider_contact_vals.phone,
									 'designation': provider_contact_vals.designation,
									 'status': provider_contact_vals.image,
									}
				credit_provider_contact_lines.append((0, 0, provider_contact_data))
			for provider_contact_vals_lines in self.provider_accreditation_campus_ids:
				for provider_contact_vals in provider_contact_vals_lines.provider_accreditation_campus_contact_ids:
					provider_campus_contact_data = {
										 'name':provider_contact_vals.name,
										 'sur_name':provider_contact_vals.sur_name,
										 'street':provider_contact_vals.street,
										 'street2':provider_contact_vals.street2,
										 'zip':provider_contact_vals.zip,
										 'city':provider_contact_vals.city,
										 'state_id':provider_contact_vals.state_id.id,
										 'country_id': provider_contact_vals.country_id.id,
										 'email': provider_contact_vals.email,
										 'phone':provider_contact_vals.phone,
										 'mobile': provider_contact_vals.mobile,
										 'image': provider_contact_vals.image,
										 'fax':provider_contact_vals.phone,
										 'designation': provider_contact_vals.designation,
										 'status': provider_contact_vals.image,
										}
					credit_provider_campus_contact_lines.append((0, 0, provider_campus_contact_data))
			# For physical address, longitude and lattitude
	#
	#         gmapString=""
	#         physical_lat_d=""
	#         physical_lat_m=""
	#         physical_lat_s=""
	#         physical_lng_d=""
	#         physical_lng_m=""
	#         physical_lng_s=""
	#
	#         postal_lat_d=""
	#         postal_lat_m=""
	#         postal_lat_s=""
	#         postal_lng_d=""
	#         postal_lng_m=""
	#         postal_lng_s=""
	#
	#         if  self.txtPhysicalAddressLine1:
	#             gmapString=gmapString+self.txtPhysicalAddressLine1;
	#
	#         if self.txtPhysicalAddressLine2:
	#             if self.txtPhysicalAddressLine1:
	#                 gmapString=gmapString+","+self.txtPhysicalAddressLine2
	#             else:
	#                 gmapString=gmapString+self.txtPhysicalAddressLine2
	#         if self.txtPhysicalAddressLine3:
	#             if self.txtPhysicalAddressLine1 or self.txtPhysicalAddressLine2:
	#                 gmapString=gmapString+","+self.txtPhysicalAddressLine3
	#             else:
	#                 gmapString=gmapString+self.txtPhysicalAddressLine3
	#
	#         if self.provider_physical_suburb and self.provider_physical_suburb.id:
	#             if self.txtPhysicalAddressLine1 or self.txtPhysicalAddressLine2 or self.txtPhysicalAddressLine3:
	#                 gmapString=gmapString+","+str(self.provider_physical_suburb and self.provider_physical_suburb.name)
	#             else:
	#                 gmapString=gmapString+str(self.provider_physical_suburb and self.provider_physical_suburb.name)
	#
	#         if self.city_physical and self.city_physical.id:
	#             if self.txtPhysicalAddressLine1 or self.txtPhysicalAddressLine2 or self.txtPhysicalAddressLine3 or self.provider_physical_suburb:
	#                 gmapString=gmapString+","+str(self.city_physical and self.city_physical.name)
	#             else:
	#                 gmapString=gmapString+str(self.city_physical and self.city_physical.name)
	#
	#
	#         if self.province_code_physical and self.province_code_physical.id:
	#             if self.txtPhysicalAddressLine1 or self.txtPhysicalAddressLine2 or self.txtPhysicalAddressLine3 or self.provider_physical_suburb or self.city_physical:
	#                 gmapString=gmapString+","+str(self.province_code_physical and self.province_code_physical.name)
	#             else:
	#                 gmapString=gmapString+str(self.province_code_physical and self.province_code_physical.name)
	#
	#         if self.country_code_physical and self.country_code_physical.id:
	#             if self.txtPhysicalAddressLine1 or self.txtPhysicalAddressLine2 or self.txtPhysicalAddressLine3 or self.provider_physical_suburb or self.city_physical or self.province_code_physical and self.province_code_physical.id:
	#                 gmapString=gmapString+","+str(self.country_code_physical and self.country_code_physical.name)
	#             else:
	#                 gmapString=gmapString+str(self.country_code_physical and self.country_code_physical.name)
	#
	#         print gmapString
	#
	#         g=geocoder.google(gmapString)
	#
	#         print "g.latlng",g.latlng
	#         if g.latlng:
	#             if g.latlng[0]:
	#                 d = int(g.latlng[0])
	#                 md = abs(g.latlng[0] - d) * 60
	#                 m = int(md)
	#                 sd = (md - m) * 60
	#
	#                 physical_lat_d=str(d)
	#                 physical_lat_m=str(md)
	#                 physical_lat_s=str(sd)
	#
	#
	#             if g.latlng[1]:
	#                 d = int(g.latlng[1])
	#                 md = abs(g.latlng[1] - d) * 60
	#                 m = int(md)
	#                 sd = (md - m) * 60
	#                 physical_lng_d=str(d)
	#                 physical_lng_m=str(md)
	#                 physical_lng_s=str(sd)
	#
	#         # For postal address, longitude and lattitude
	#
	#         gmapString=""
	#
	#         if  self.txtPostalAddressLine1:
	#             gmapString=gmapString+self.txtPostalAddressLine1;
	#
	#         if self.txtPostalAddressLine2:
	#             if self.txtPostalAddressLine1:
	#                 gmapString=gmapString+","+self.txtPostalAddressLine2
	#             else:
	#                 gmapString=gmapString+self.txtPostalAddressLine2
	#         if self.txtPostalAddressLine3:
	#             if self.txtPostalAddressLine1 or self.txtPostalAddressLine2:
	#                 gmapString=gmapString+","+self.txtPostalAddressLine3
	#             else:
	#                 gmapString=gmapString+self.txtPostalAddressLine3
	#
	#         if self.provider_postal_suburb and self.provider_postal_suburb.id:
	#             if self.txtPostalAddressLine1 or self.txtPostalAddressLine2 or self.txtPostalAddressLine3:
	#                 gmapString=gmapString+","+str(self.provider_postal_suburb and self.provider_postal_suburb.name)
	#             else:
	#                 gmapString=gmapString+str(self.provider_postal_suburb and self.provider_postal_suburb.name)
	#
	#         if self.city_postal and self.city_postal.id:
	#             if self.txtPostalAddressLine1 or self.txtPostalAddressLine2 or self.txtPostalAddressLine3 or self.provider_postal_suburb:
	#                 gmapString=gmapString+","+str(self.city_postal and self.city_postal.name)
	#             else:
	#                 gmapString=gmapString+str(self.city_postal and self.city_postal.name)
	#
	#         if self.province_code_postal and self.province_code_postal.id:
	#             if self.txtPostalAddressLine1 or self.txtPostalAddressLine2 or self.txtPostalAddressLine3 or self.provider_postal_suburb or self.city_postal:
	#                 gmapString=gmapString+","+str(self.province_code_postal and self.province_code_postal.name)
	#             else:
	#                 gmapString=gmapString+str(self.province_code_postal and self.province_code_postal.name)
	#
	#         if self.country_code_postal and self.country_code_postal.id:
	#             if self.txtPostalAddressLine1 or self.txtPostalAddressLine2 or self.txtPostalAddressLine3 or self.provider_postal_suburb or self.city_postal or self.province_code_postal and self.province_code_postal.id:
	#                 gmapString=gmapString+","+str(self.country_code_postal and self.country_code_postal.name)
	#             else:
	#                 gmapString=gmapString+str(self.country_code_postal and self.country_code_postal.name)
	#
	#         print gmapString
	#
	#         g=geocoder.google(gmapString)
	#
	#         if g.latlng:
	#             if g.latlng[0]:
	#                 d = int(g.latlng[0])
	#                 md = abs(g.latlng[0] - d) * 60
	#                 m = int(md)
	#                 sd = (md - m) * 60
	#
	#                 postal_lat_d=str(d)
	#                 postal_lat_m=str(md)
	#                 postal_lat_s=str(sd)
	#
	#
	#             if g.latlng[1]:
	#                 d = int(g.latlng[1])
	#                 md = abs(g.latlng[1] - d) * 60
	#                 m = int(md)
	#                 sd = (md - m) * 60
	#                 postal_lng_d=str(d)
	#                 postal_lng_m=str(md)
	#                 postal_lng_s=str(sd)
			if not self.is_existing_provider:
				provider_accreditation_num = self.env['ir.sequence'].get('provider.accreditation')
				self.write({'sequence_num': provider_accreditation_num})
			elif self.is_existing_provider:
				provider_obj = self.env['res.partner'].search([('provider_accreditation_num', '=', self.accreditation_number)])
				pro_lst = []
				for pro_obj in provider_obj:
					pro_lst.append(pro_obj.id)
				if pro_lst:
					provider_obj = self.env['res.partner'].search([('id', '=', max(pro_lst))])
					provider_accreditation_num = provider_obj.provider_accreditation_num
					self.write({'sequence_num': provider_accreditation_num})
				'''For getting old batches for re-accreditation'''
				provider_obj.write({'is_visible': False})
				batch_master_obj = self.env['batch.master'].search([('provider_id','=',provider_obj.id)])
				for batch in batch_master_obj:
					provider_batch_data = {
										  'batch_master_id':batch.id,
										  'batch_status':batch.batch_status,
										  }
					batch_val_list.append((0, 0, provider_batch_data))

			credit_provider_campus_lines = []
			if self.provider_accreditation_campus_ids:
				credit_provider_campus_lines = []
				for provider_campus_vals in self.provider_accreditation_campus_ids:
					if provider_campus_vals.campus_evaluat:
						campus_assessors_list = []
						campus_moderators_list = []
						campus_q_vals_line = []
						campus_s_vals_line = []
						campus_lp_vals_line = []
						if provider_campus_vals.assessors_ids:
							for line in provider_campus_vals.assessors_ids:
								for data in line:
									val = {
											 'assessors_id':data.assessors_id.id,
											 'awork_phone':data.awork_phone,
											 'awork_email':data.awork_email,
											 'campus_assessor_sla_document':data.campus_assessor_sla_document.id,
											 'assessor_notification_letter':data.assessor_notification_letter.id,
											}
									campus_assessors_list.append((0, 0, val))

						if provider_campus_vals.moderators_ids:
							for line in provider_campus_vals.moderators_ids:
								for data in line:
									val = {
											 'moderators_id':data.moderators_id.id,
											 'mwork_phone': data.mwork_phone,
											 'mwork_email': data.mwork_email,
											 'campus_moderator_sla_document':data.campus_moderator_sla_document.id,
											 'moderator_notification_letter':data.moderator_notification_letter.id,
											}
									campus_moderators_list.append((0, 0, val))
						if provider_campus_vals.qualification_ids:
							for q_lines in provider_campus_vals.qualification_ids:
								accreditation_qualification_line = []
								for lines in q_lines.qualification_line:
									for data in lines:
										if data.selection:
											val = {
												 'name':data.name,
												 'type':data.type,
												 'id_data':data.id_no,
												 'title':data.title,
												 'level1':data.level1,
												 'level2':data.level2,
												 'level3': data.level3,
												 'selection':data.selection,
												 'is_provider_approved':data.is_provider_approved,
												 'is_seta_approved':data.is_seta_approved,
												}
											accreditation_qualification_line.append((0, 0, val))
								q_vals = {
											'qualification_id':q_lines.qualification_id.id,
											'qualification_line':accreditation_qualification_line,
											'saqa_qual_id':q_lines.saqa_qual_id,
											'assessors_id':q_lines.assessors_id.id,
											'moderators_id':q_lines.moderators_id.id,
											'assessor_sla_document':q_lines.assessor_sla_document.id,
											'moderator_sla_document':q_lines.moderator_sla_document.id,
											}
								campus_q_vals_line.append((0, 0, q_vals))
						if provider_campus_vals.skills_programme_ids:
							for unit_standards in provider_campus_vals.skills_programme_ids:
								unit_standards_line = []
								for lines in unit_standards.unit_standards_line:
									for data in lines:
										if data.selection:
											val = {
												 'name':data.name,
												 'type':data.type,
												 'id_no':data.id_no,
												 'title':data.title,
												 'level1':data.level1,
												 'level2':data.level2,
												 'level3': data.level3,
												 'selection':data.selection
												}
											unit_standards_line.append((0, 0, val))
								s_vals = {
											'skills_programme_id':unit_standards.skills_programme_id.id,
											'unit_standards_line':unit_standards_line,
											'skill_saqa_id':unit_standards.saqa_skill_id,
											}
								campus_s_vals_line.append((0, 0, s_vals))
						'''LEARNING PROGRAMME CODE START'''
						if provider_campus_vals.learning_programme_ids:
							for unit_standards in provider_campus_vals.learning_programme_ids:
								unit_standards_line = []
								for lines in unit_standards.unit_standards_line:
									for data in  lines:
										if data.selection:
											val = {
												 'name':data.name,
												 'type':data.type,
												 'id_no':data.id_no,
												 'title':data.title,
												 'level1':data.level1,
												 'level2':data.level2,
												 'level3': data.level3,
												 'selection':data.selection,
												 'seta_approved_lp':data.seta_approved_lp,
												 'provider_approved_lp':data.provider_approved_lp,
												}
											unit_standards_line.append((0, 0, val))
								lp_vals = {
											'learning_programme_id':unit_standards.learning_programme_id.id,
											'unit_standards_line':unit_standards_line,
											'lp_saqa_id':unit_standards.saqa_qual_id,
											}
								campus_lp_vals_line.append((0, 0, lp_vals))
						'''LEARNING PROGRAMME CODE END'''
						provider_campus_data = {
											 'name':provider_campus_vals.name,
											 'street':provider_campus_vals.street,
											 'street2':provider_campus_vals.street2,
											 'zip':provider_campus_vals.zip,
											 'city':provider_campus_vals.city and provider_campus_vals.city.id,
											 'suburb':provider_campus_vals.suburb and provider_campus_vals.suburb.id,
											 'state_id':provider_campus_vals.state_id.id,
											 'country_id': provider_campus_vals.country_id.id,
											 'email': provider_campus_vals.email,
											 'phone':provider_campus_vals.phone,
											 'mobile': provider_campus_vals.mobile,
											 'image': provider_campus_vals.image,
											 'fax':provider_campus_vals.fax,
											 'use_parent_address':False,
											 'type' : "contact",
											 'active' : True,
	#                                         'parent_id':partner_id,
											 'qualification_campus_ids':campus_q_vals_line,
											 'skills_programme_campus_ids':campus_s_vals_line,
											 'learning_programme_campus_ids':campus_lp_vals_line,
											'assessors_campus_ids':campus_assessors_list,
											'moderators_campus_ids':campus_moderators_list,
											 'is_company':True,
											 'provider':True,
		#                                      'designation': provider_campus_vals.designation,
		#                                      'status': provider_campus_vals.status,
											'provider_master_campus_contact_ids':credit_provider_campus_contact_lines,
											}

						credit_provider_campus_lines.append((0, 0, provider_campus_data))
			partner_vals = {
							'name':self.name,
							'street': self.street,
							'street2': self.street2,
							'street3': self.street3,
							'zip':self.zip,
							'city': self.city and self.city.id,
							'state_id':self.state_id and self.state_id.id,
							'country_id':self.country_id and self.country_id.id,
							'email':self.email,
							'phone': self.phone,
							'mobile':self.mobile,
							'provider_contact_ids': credit_provider_contact_lines,
							'provider_master_contact_ids' : credit_provider_contact_lines,
							'qualification_line': credit_qualification_line_lines,
							'qualification_id':self.qualification_id and self.qualification_id.id,
							'physical_address_1':self.txtPhysicalAddressLine1,
							'physical_address_2':self.txtPhysicalAddressLine2,
							'physical_address_3':self.txtPhysicalAddressLine3,
							'provider':True,
							'provider_accreditation_num':provider_accreditation_num,
							'image':self.image,
							'txtRegName':self.txtRegName,
							'txtTradeName':self.txtTradeName,
							'txtAbbrTradeName':self.txtAbbrTradeName,
							'cboOrgLegalStatus':self.cboOrgLegalStatus and self.cboOrgLegalStatus.id,
							'txtCompanyRegNo':self.txtCompanyRegNo,
							'txtVATRegNo':self.txtVATRegNo,
							'cboOrgSICCode':self.cboOrgSICCode,
							'txtSDLNo':self.txtSDLNo,
							'cboTHETAChamberSelect':self.cboTHETAChamberSelect and self.cboTHETAChamberSelect.id,
							'cboProviderFocus':self.cboProviderFocus and self.cboProviderFocus.id,
							'txtNumYearsCurrentBusiness':self.txtNumYearsCurrentBusiness,
							'txtNumStaffMembers':self.txtNumStaffMembers,
							'txtStateAccNumber':self.txtStateAccNumber,
							'optAccStatus':self.optAccStatus,
							#'StatusReason':self.StatusReason,
							'SICCode':self.SICCode,
							'AccreditationStatus':self.AccreditationStatus,
							'cmdNext':self.cmdNext,
							'txtWorkEmail':self.txtWorkEmail,
							'OrgLegalStatus':self.OrgLegalStatus,
							'txtWorkPhone':self.txtWorkPhone,
							'txtTags':self.txtTags,
							'AppliedToAnotherSETA':self.AppliedToAnotherSETA,
							'optYesNo':self.optYesNo,
							'cboSETA':self.cboSETA and self.cboSETA.id,
							'provider_sars_number':self.txtSDLNo,
							'provider_sic_code':self.cboOrgSICCode,
							'physical_address_1': self.txtPhysicalAddressLine1,
							'physical_address_2': self.txtPhysicalAddressLine2,
							'physical_address_3': self.txtPhysicalAddressLine3,
							'postal_address_1': self.txtPostalAddressLine1,
							'postal_address_2': self.txtPostalAddressLine2,
							'postal_address_3': self.txtPostalAddressLine3,
							'city_physical' : self.city_physical and self.city_physical.id,
							'city_postal' :   self.city_postal and self.city_postal.id,
							'zip_physical' : self.zip_physical,
							'zip_postal' : self.zip_postal,
							'country_code_physical' : self.country_code_physical and self.country_code_physical.id,
							'country_code_postal' : self.country_code_postal and self.country_code_postal.id,
							'province_code_physical' : self.province_code_physical and self.province_code_physical.id,
							'province_code_postal' : self.province_code_postal and self.province_code_postal.id,
							'provider_suburb' : self.provider_suburb and self.provider_suburb.id,
							'provider_physical_suburb' : self.provider_physical_suburb and self.provider_physical_suburb.id,
							'provider_postal_suburb' : self.provider_postal_suburb and self.provider_postal_suburb.id,
							'qualification_ids': q_vals_line,
							'skills_programme_ids':s_vals_line,
							'learning_programme_ids':lp_vals_line,
							'provider_batch_ids': batch_val_list,
							'assessors_ids':assessors_list,
							'moderators_ids':moderators_list,
							'is_company':True,
							'active' : True,
							'is_visible' : True,
							'provider_status_Id': 'Accredited',

	#                         'provider_latitude_degree' : physical_lat_d,
	#                         'provider_latitude_minutes' : physical_lat_m,
	#                         'provider_latitude_seconds' : physical_lat_s,
	#                         'provider_longitude_degree' : physical_lng_d,
	#                         'provider_longitude_minutes' : physical_lng_m,
	#                         'provider_longitude_seconds' : physical_lng_s,
	#
	#                         'provider_latitude_degree_p' : postal_lat_d,
	#                         'provider_latitude_minutes_p' : postal_lat_m,
	#                         'provider_latitude_seconds_p' : postal_lat_s,
	#                         'provider_longitude_degree_p' : postal_lng_d,
	#                         'provider_longitude_minutes_p' : postal_lng_m,
	#                         'provider_longitude_seconds_p' : postal_lng_s,
							'same_as_home':self.same_as_home,
							'website': self.website,
							'fax': self.fax,
							'material':self.material,
							'cipro_documents': self.cipro_documents and self.cipro_documents.id,
							'tax_clearance': self.tax_clearance and self.tax_clearance.id,
							'lease_agreement_document':self.lease_agreement_document and self.lease_agreement_document.id,
							'director_cv': self.director_cv and self.director_cv.id,
							'certified_copies_of_qualifications': self.certified_copies_of_qualifications and self.certified_copies_of_qualifications.id,
							'professional_body_registration': self.professional_body_registration and self.professional_body_registration.id,
							'workplace_agreement': self.workplace_agreement and self.workplace_agreement.id,
							'business_residence_proof': self.business_residence_proof and self.business_residence_proof.id,
							'provider_learning_material': self.provider_learning_material and self.provider_learning_material.id,
							'skills_programme_registration_letter': self.skills_programme_registration_letter and self.skills_programme_registration_letter.id,
							'company_profile_and_organogram' : self.company_profile_and_organogram and self.company_profile_and_organogram.id,
							'quality_management_system' : self.quality_management_system and self.quality_management_system.id,
							'alternate_acc_number':self.alternate_acc_number,
							'SDL_No':self.txtSDLNo,
							'child_ids':credit_provider_campus_lines,
							'is_existing_provider':self.is_existing_provider,
						}
			partner_id = self.env['res.partner'].create(partner_vals)
			''' As per new configuration '''
			etqe_conf = self.env['etqe.config'].search([])
			sdate = datetime.today().date()
			new_date = "2020-03-31"
			if etqe_conf:
				etqe_brw = self.env['etqe.config'].browse(etqe_conf[0].id)
				if etqe_brw.etqa_end_date and etqe_brw.seta_license_end_date:
					seta_license_date = datetime.strptime(etqe_brw.seta_license_end_date, '%Y-%m-%d').date()
					new_date = sdate + relativedelta(years=etqe_brw.etqa_end_date)
					if new_date > seta_license_date:
						new_date = etqe_brw.seta_license_end_date
			partner_id.write({'provider_start_date':sdate, 'provider_end_date':new_date})
			if self.is_existing_provider:
				partner_id.write({'provider_status_Id': 'Reaccredited'})
			self.write({'reg_start_date':sdate,
						'reg_end_date':new_date,
						})
			self.write({'provider_expiry_date':new_date})
			for self_obj in self:
				for rec in self_obj.acc_multi_doc_upload_ids:
					rec.write({'acc_id':partner_id.id})
				for rec in self_obj.site_visit_image:
					rec.write({'acc_id':partner_id.id})
	#                     partner_id.write({'child_ids':credit_provider_campus_lines})
			# # TODO : For Mail Server notification
	#         email_template_obj = self.env['email.template']
	#         ir_model_data_obj = self.env['ir.model.data']
	#         mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_edi_etq')
	#         if mail_template_id:
			self.write({'state':'approved', 'approved':True, 'related_provider':partner_id.id, 'provider_accreditation_num':provider_accreditation_num, 'final_state':'Approved', 'provider_approval_date':datetime.today().date()})
#             Commented because Attachement problem in email template
#             att_obj = self.env['ir.attachment']
#             attachment_ids = []
#             report_xml_letter = self.env['report']._get_report_from_name('hwseta_etqe.report_letter_of_approval')
#             letter_of_approval, format1 = self.pool['report'].get_pdf(self._cr, self._uid, [report_xml_letter.id], 'hwseta_etqe.report_letter_of_approval', data={}), 'pdf'
#             letter_attachment_data = {
#                     'name': "Letter of Approval.pdf",
#                     'datas_fname':'Letter of Approval.pdf',  # your object File Name
#                     'datas':base64.encodestring(letter_of_approval),  # your object Data
#                      'type': 'binary',
#                     'res_name': 'provider_accreditation',
#                     'res_id': self.id,
#                 }
#             attachment_ids.append(att_obj.create(letter_attachment_data)[0].id)
	#         report_xml_certificate = self.env['report']._get_report_from_name('hwseta_etqe.report_accreditation_certificate')
	#         accreditation_certificate,format2= self.pool['report'].get_pdf(self._cr, self._uid, [report_xml_certificate.id], 'hwseta_etqe.report_accreditation_certificate', data={}),'pdf'
	#         certificate_attachment_data = {
	#                 'name': "Certificate of Accreditation.pdf",
	#                 'datas_fname':'Certificate of Accreditation.pdf', # your object File Name
	#                 'datas':base64.encodestring(accreditation_certificate),  # your object Data
	#                  'type': 'binary',
	#                 'res_name': 'provider_accreditation',
	#                 'res_id': self.id,
	#             }
	#         attachment_ids.append(att_obj.create(certificate_attachment_data)[0].id)
#             Commented because Attachement problem in email template
#             ir_model_data_obj = self.env['ir.model.data']
#             mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_accreditation_approved')
#             email_template_obj = self.env['email.template']
#             temp_obj = email_template_obj.browse(mail_template_id[1])
#             if mail_template_id:
#                 temp_obj.write({'attachment_ids':[(6, 0, attachment_ids)]})
#                 self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
			mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_accreditation_approved')
			if mail_template_id:
				self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
			# Below code is written to link provider with given assessors and moderators
			pro_ass_vals = {
							'provider_id':partner_id.id,
							'employer_sdl_no':self.txtSDLNo,
							'provider_accreditation_num':provider_accreditation_num,
							}
			for line in self.assessors_ids:
				assessors_obj = self.env['hr.employee'].browse([line.assessors_id.id])
				assessors_obj.write({'as_provider_rel_id':[(0, 0, pro_ass_vals)]})

			for line in self.moderators_ids:
				moderators_obj = self.env['hr.employee'].browse([line.moderators_id.id])
				moderators_obj.write({'mo_provider_rel_id':[(0, 0, pro_ass_vals)]})
		elif self.is_extension_of_scope:
			q_vals_line = []
			s_vals_line = []
			lp_vals_line = []
			assessors_list = []
			moderators_list = []
			qual_skill_lp_verify = False
			for qual in self.qualification_ids:
				if(qual.verify == True):
					qual_skill_lp_verify = True
			for skill in self.skills_programme_ids:
				if(skill.verify == True):
					qual_skill_lp_verify = True
			for lp in self.learning_programme_ids:
				if(lp.verify == True):
					qual_skill_lp_verify = True
			if qual_skill_lp_verify == False:
				raise Warning(_("Please check/verify at least one Qualification or Skills programme or Learning programme before Approve"))

			if self.qualification_ids:
				for q_lines in self.qualification_ids:
					if q_lines.verify == True:
						if q_lines.select:
							accreditation_qualification_line = []
							for lines in q_lines.qualification_line:
								for data in lines:
									if data.selection:
										val = {
											 'name':data.name,
											 'type':data.type,
											 'id_data':data.id_no,
											 'title':data.title,
											 'level1':data.level1,
											 'level2':data.level2,
											 'level3': data.level3,
											 'selection':data.selection,
											 'is_provider_approved': data.is_provider_approved,
											 'is_seta_approved': data.is_seta_approved,
											}
										accreditation_qualification_line.append((0, 0, val))
							q_vals = {
										'qualification_id':q_lines.qualification_id.id,
										'qualification_line':accreditation_qualification_line,
										'saqa_qual_id':q_lines.saqa_qual_id,
										'status':'approved',
										'approval_request':True,
										'request_send':True,
										'assessors_id':q_lines.assessors_id.id,
										'moderators_id':q_lines.moderators_id.id,
										'assessor_sla_document':q_lines.assessor_sla_document.id,
										'moderator_sla_document':q_lines.moderator_sla_document.id,
										}
							q_vals_line.append((0, 0, q_vals))
			if self.skills_programme_ids:
				for unit_standards in self.skills_programme_ids:
					if unit_standards.verify == True:
						if unit_standards.select:
							unit_standards_line = []
							for lines in unit_standards.unit_standards_line:
								for data in  lines:
									if data.selection:
										val = {
											 'name':data.name,
											 'type':data.type,
											 'id_no':data.id_no,
											 'title':data.title,
											 'level1':data.level1,
											 'level2':data.level2,
											 'level3': data.level3,
											 'selection':data.selection
											}
										unit_standards_line.append((0, 0, val))
							s_vals = {
										'skills_programme_id':unit_standards.skills_programme_id.id,
										'unit_standards_line':unit_standards_line,
										'skill_saqa_id':unit_standards.saqa_skill_id,
										'status':'approved',
										'approval_request':True,
										'request_send':True,
										'assessors_id':unit_standards.assessors_id.id,
										'moderators_id':unit_standards.moderators_id.id,
										'assessor_sla_document':unit_standards.assessor_sla_document.id,
										'moderator_sla_document':unit_standards.moderator_sla_document.id,
										}
							s_vals_line.append((0, 0, s_vals))
			'''LEARNING PROGRAMME START'''
			if self.learning_programme_ids:
				for unit_standards in self.learning_programme_ids:
					if unit_standards.verify == True:
						if unit_standards.select:
							unit_standards_line = []
							for lines in unit_standards.unit_standards_line:
								for data in  lines:
									if data.selection:
										val = {
											 'name':data.name,
											 'type':data.type,
											 'id_no':data.id_no,
											 'title':data.title,
											 'level1':data.level1,
											 'level2':data.level2,
											 'level3': data.level3,
											 'selection':data.selection,
											 'seta_approved_lp': data.seta_approved_lp,
											 'provider_approved_lp':data.provider_approved_lp,
											}
										unit_standards_line.append((0, 0, val))
							lp_vals = {
										'learning_programme_id':unit_standards.learning_programme_id.id,
										'unit_standards_line':unit_standards_line,
										'lp_saqa_id':unit_standards.saqa_qual_id,
										'status':'approved',
										'approval_request':True,
										'request_send':True,
										'assessors_id':unit_standards.assessors_id.id,
										'moderators_id':unit_standards.moderators_id.id,
										'assessor_sla_document':unit_standards.assessor_sla_document.id,
										'moderator_sla_document':unit_standards.moderator_sla_document.id,
										}
							lp_vals_line.append((0, 0, lp_vals))
			'''LEARNING PROGRAMME END'''
			if self.assessors_ids:
				for line in self.assessors_ids:
					for data in line:
						val = {  'search_by':'id',
								 'identification_id':data.assessors_id.assessor_moderator_identification_id,
								 'assessors_id':data.assessors_id.id,
								 'awork_phone':data.awork_phone,
								 'awork_email':data.awork_email,
								 'assessor_sla_document':data.assessor_sla_document.id,
								 'assessor_notification_letter':data.assessor_notification_letter.id,
								 'status':'approved',
								 'approval_request':True,
								 'request_send':True,
								}
						assessors_list.append((0, 0, val))
			if self.moderators_ids:
				for line in self.moderators_ids:
					for data in line:
						val = {
								 'search_by':'id',
								 'identification_id':data.moderators_id.assessor_moderator_identification_id,
								 'moderators_id':data.moderators_id.id,
								 'mwork_phone': data.mwork_phone,
								 'mwork_email': data.mwork_email,
								 'moderator_sla_document':data.moderator_sla_document.id,
								 'moderator_notification_letter':data.moderator_notification_letter.id,
								 'status':'approved',
								 'approval_request':True,
								 'request_send':True,
								}
						moderators_list.append((0, 0, val))
			credit_provider_campus_lines = []
			if self.provider_accreditation_campus_ids:
				credit_provider_campus_lines = []
				for provider_campus_vals in self.provider_accreditation_campus_ids:
					if provider_campus_vals.campus_evaluat:
						campus_assessors_list = []
						campus_moderators_list = []
						campus_q_vals_line = []
						campus_s_vals_line = []
						campus_lp_vals_line = []
						if provider_campus_vals.assessors_ids:
							for line in provider_campus_vals.assessors_ids:
								for data in line:
									val = {
											 'assessors_id':data.assessors_id.id,
											 'awork_phone':data.awork_phone,
											 'awork_email':data.awork_email,
											 'campus_assessor_sla_document':data.campus_assessor_sla_document.id,
											 'assessor_notification_letter':data.assessor_notification_letter.id,
											}
									campus_assessors_list.append((0, 0, val))
						if provider_campus_vals.moderators_ids:
							for line in provider_campus_vals.moderators_ids:
								for data in line:
									val = {
											 'moderators_id':data.moderators_id.id,
											 'mwork_phone': data.mwork_phone,
											 'mwork_email': data.mwork_email,
											 'campus_moderator_sla_document':data.campus_moderator_sla_document.id,
											 'moderator_notification_letter':data.moderator_notification_letter.id,
											}
									campus_moderators_list.append((0, 0, val))
						if provider_campus_vals.qualification_ids:
							for q_lines in provider_campus_vals.qualification_ids:
								accreditation_qualification_line = []
								for lines in q_lines.qualification_line:
									for data in lines:
										if data.selection:
											val = {
												 'name':data.name,
												 'type':data.type,
												 'id_no':data.id_no,
												 'title':data.title,
												 'level1':data.level1,
												 'level2':data.level2,
												 'level3': data.level3,
												 'selection':data.selection,
												 'is_provider_approved': data.is_provider_approved,
												 'is_seta_approved': data.is_seta_approved,
												}
											accreditation_qualification_line.append((0, 0, val))
								q_vals = {
											'qualification_id':q_lines.qualification_id.id,
											'qualification_line':accreditation_qualification_line,
											'saqa_qual_id':q_lines.saqa_qual_id,
											}
								campus_q_vals_line.append((0, 0, q_vals))
						if provider_campus_vals.skills_programme_ids:
							for unit_standards in provider_campus_vals.skills_programme_ids:
								unit_standards_line = []
								for lines in unit_standards.unit_standards_line:
									for data in  lines:
										if data.selection:
											val = {
												 'name':data.name,
												 'type':data.type,
												 'id_no':data.id_no,
												 'title':data.title,
												 'level1':data.level1,
												 'level2':data.level2,
												 'level3': data.level3,
												 'selection':data.selection
												}
											unit_standards_line.append((0, 0, val))
								s_vals = {
											'skills_programme_id':unit_standards.skills_programme_id.id,
											'unit_standards_line':unit_standards_line,
											'skill_saqa_id':unit_standards.saqa_skill_id,
											}
								campus_s_vals_line.append((0, 0, s_vals))
						'''LEARNING PROGRAMME START'''
						if provider_campus_vals.learning_programme_ids:
							for unit_standards in provider_campus_vals.learning_programme_ids:
								unit_standards_line = []
								for lines in unit_standards.unit_standards_line:
									for data in  lines:
										if data.selection:
											val = {
												 'name':data.name,
												 'type':data.type,
												 'id_no':data.id_no,
												 'title':data.title,
												 'level1':data.level1,
												 'level2':data.level2,
												 'level3': data.level3,
												 'selection':data.selection,
												 'seta_approved_lp': data.seta_approved_lp,
												 'provider_approved_lp':data.provider_approved_lp
												}
											unit_standards_line.append((0, 0, val))
								lp_vals = {
											'learning_programme_id':unit_standards.learning_programme_id.id,
											'unit_standards_line':unit_standards_line,
											'lp_saqa_id':unit_standards.saqa_qual_id,
											}
								campus_lp_vals_line.append((0, 0, lp_vals))
						'''LEARNING PROGRAMME END'''
						provider_campus_data = {
											 'name':provider_campus_vals.name,
											 'street':provider_campus_vals.street,
											 'street2':provider_campus_vals.street2,
											 'zip':provider_campus_vals.zip,
											 'city':provider_campus_vals.city and provider_campus_vals.city.id,
											 'suburb':provider_campus_vals.suburb and provider_campus_vals.suburb.id,
											 'state_id':provider_campus_vals.state_id.id,
											 'country_id': provider_campus_vals.country_id.id,
											 'email': provider_campus_vals.email,
											 'phone':provider_campus_vals.phone,
											 'mobile': provider_campus_vals.mobile,
											 'image': provider_campus_vals.image,
											 'fax':provider_campus_vals.fax,
											 'use_parent_address':False,
											 'type' : "contact",
											 'active' : True,
	#                                         'parent_id':partner_id,
											 'qualification_campus_ids':campus_q_vals_line,
											 'skills_programme_campus_ids':campus_s_vals_line,
											 'learning_programme_campus_ids':campus_lp_vals_line,
											'assessors_campus_ids':campus_assessors_list,
											'moderators_campus_ids':campus_moderators_list,
											 'is_company':True,
											 'provider':True,
		#                                      'designation': provider_campus_vals.designation,
		#                                      'status': provider_campus_vals.status,
											}
						credit_provider_campus_lines.append((0, 0, provider_campus_data))
			provider_obj = self.env['res.partner'].search([('provider_accreditation_num', '=', self.accreditation_number)])
			pro_lst = []
			for pro_obj in provider_obj:
				pro_lst.append(pro_obj.id)
			provider_obj = self.env['res.partner'].search([('id', '=', max(pro_lst))])

			'''Below code is written to delete provider master data before appending'''
			unlink_qual_list, unlink_skill_list, unlink_lp_list, unlink_ass_list, unlink_mod_list = [], [], [], [], []
			for pro_qual in provider_obj.qualification_ids:
				for qual in self.qualification_ids:
					if qual.verify:
						if pro_qual.qualification_id == qual.qualification_id:
						   unlink_qual_list.append((2, pro_qual.id))
			for pro_skill in provider_obj.skills_programme_ids:
				for skill in self.skills_programme_ids:
					if skill.verify:
						if pro_skill.skills_programme_id == skill.skills_programme_id:
						   unlink_skill_list.append((2, pro_skill.id))
			for pro_lp in provider_obj.learning_programme_ids:
				for lp in self.learning_programme_ids:
					if lp.verify:
						if pro_lp.learning_programme_id == lp.learning_programme_id:
						   unlink_lp_list.append((2, pro_lp.id))
			for pro_assessor in provider_obj.assessors_ids:
				for assessor in self.assessors_ids:
					if pro_assessor.assessors_id == assessor.assessors_id:
						unlink_ass_list.append((2, pro_assessor.id))
			for pro_moderator in provider_obj.moderators_ids:
				for moderator in self.moderators_ids:
					if pro_moderator.moderators_id == moderator.moderators_id:
						unlink_mod_list.append((2, pro_moderator.id))

			provider_obj.write({'qualification_ids':unlink_qual_list})
			provider_obj.write({'skills_programme_ids':unlink_skill_list})
			provider_obj.write({'learning_programme_ids':unlink_lp_list})
			provider_obj.write({'assessors_ids':unlink_ass_list})
			provider_obj.write({'moderators_ids':unlink_mod_list})

			'''commented below 4 lines, that was written to delete master data before appending'''
#             provider_obj.write({'qualification_ids':[(2, qual.id) for qual in provider_obj.qualification_ids]})
#             provider_obj.write({'skills_programme_ids':[(2, skills.id) for skills in provider_obj.skills_programme_ids]})
#             provider_obj.write({'learning_programme_ids':[(2, lp.id) for lp in provider_obj.learning_programme_ids]})
#             provider_obj.write({'assessors_ids':[(2, assessor.id) for assessor in provider_obj.assessors_ids]})
#             provider_obj.write({'moderators_ids':[(2, moderator.id) for moderator in provider_obj.moderators_ids]})
			provider_obj.write({
						'name':self.name,
						'street': self.street,
						'street2': self.street2,
						'street3': self.street3,
						'zip':self.zip,
						'city': self.city and self.city.id,
						'state_id':self.state_id and self.state_id.id,
						'country_id':self.country_id and self.country_id.id,
						'email':self.email,
						'phone': self.phone,
						'mobile':self.mobile,
						'qualification_ids': q_vals_line,
						'skills_programme_ids':s_vals_line,
						'learning_programme_ids':lp_vals_line,
						'assessors_ids':assessors_list,
						'moderators_ids':moderators_list,
						'child_ids':credit_provider_campus_lines,
					})
#             if self.is_existing_provider:
#                 etqe_conf = self.env['etqe.config'].search([])
#                 sdate =  datetime.today().date()
#                 new_date  = "2018-03-31"
#                 if etqe_conf:
#                     etqe_brw = self.env['etqe.config'].browse(etqe_conf.id)
#                     effdate = datetime.strptime(etqe_brw.from_effective_date, '%Y-%m-%d').date()
#                     sdate =datetime.today().date()
#                     if  effdate <=  datetime.today().date():
#                         if etqe_brw.etqa_end_date:
#                             new_date =sdate + relativedelta(years=etqe_brw.etqa_end_date)
#                 provider_obj.write({'provider_start_date':sdate,'provider_end_date':new_date})
			provider_accreditation_num = provider_obj.provider_accreditation_num
			self.write({'sequence_num': provider_accreditation_num})
			# Below code is written to link provider with given assessors and moderators
			pro_ass_vals = {
							'provider_id':provider_obj.id,
							'employer_sdl_no':self.txtSDLNo,
							'provider_accreditation_num':provider_accreditation_num,
							}
			for line in self.assessors_ids:
				assessors_obj = self.env['hr.employee'].browse([line.assessors_id.id])
				assessors_obj.write({'as_provider_rel_id':[(0, 0, pro_ass_vals)]})

			for line in self.moderators_ids:
				moderators_obj = self.env['hr.employee'].browse([line.moderators_id.id])
				moderators_obj.write({'mo_provider_rel_id':[(0, 0, pro_ass_vals)]})

			self.write({'reg_start_date':provider_obj.provider_start_date,
						'reg_end_date':provider_obj.provider_end_date,
						})
			self.write({'provider_accreditation_status_ids':[(0, 0, {'pa_name':self.env['res.users'].browse(self._uid).name, 'pa_date':datetime.now(), 'pa_status':'Approved', 'pa_updation_date':self.write_date, 'pa_comment':self.comment_box})]})
			self.write({'comment_box':''})
			self.write({'state':'approved', 'approved':True, 'final_state':'Approved', 'provider_approval_date':datetime.today().date()})

			mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_provider_extension_of_scope')
			if mail_template_id:
				self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
		return True

	@api.multi
	def write(self, vals):
		context = self._context
#         qual_count = 0
#         skill_count = 0
#         ass_count = 0
#         mod_count = 0
		if context is None:
			context = {}
		res = super(provider_accreditation, self).write(vals)
#         provider_accreditation_data = self.browse(cr, uid, ids)
#         if self.qualification_ids or self.skills_programme_ids:
#             for line in self.qualification_ids:
#                 qual_count += 1
#             for line in self.skills_programme_ids:
#                 skill_count += 1
#             count = qual_count + skill_count
#             if count > 3:
#                 raise Warning(_('Sorry! You Can Add Maximum 3 Qualifications or Skills Programme.'))
#
#         if self.assessors_ids:
#             for line in self.assessors_ids:
#                 ass_count += 1
#             if ass_count < count:
#                 raise Warning(_('Please Add Assessor.'))
#             elif ass_count > count:
#                 raise Warning(_('Please Remove Assessor.'))
#
#         if self.moderators_ids:
#             for line in self.moderators_ids:
#                 mod_count += 1
#             if mod_count < count:
#                 raise Warning(_('Please Add Moderator.'))
#             elif mod_count > count:
#                 raise Warning(_('Please Remove Moderator.'))
		if context.get('submit') == True:
			pass
		if self.phone:
			if not self.phone.isdigit() or len(self.phone) != 10:
				raise Warning(_('Please enter 10 digits Phone number'))
		if self.mobile:
			if not self.mobile.isdigit() or len(self.mobile) != 10:
				raise Warning(_('Please enter 10 digits Mobile number'))
		if self.fax:
			if not self.fax.isdigit() or len(self.fax) != 10:
				raise Warning(_('Please enter 10 digits Fax number'))
		if self.qualification_ids:
			context = self._context
			if context is None:
				context = {}
			self = self.with_context(qualification_ids=self.qualification_ids)
		if self.state in ['verification','evaluation','recommended1','recommended2','validated','approved','denied'] and self.env.user.partner_id.provider == True:
			raise Warning(_('Sorry! you are not authorized to view evaluation process'))
		if self.state == "verification" and self.submitted == False:
			raise Warning(_('Sorry! you can not change status to verification first submit application.'))
		if self.state == "evaluation" and self.verify == False:
			raise Warning(_('Sorry! you can not change status to evaluation first verify application.'))
		if self.state == "approved" and self.evaluate == False:
			raise Warning(_('Sorry! you can not change status to approve first evaluate application.'))
		if self.state == "approved" and self.denied == True:
			raise Warning(_('Sorry! you can not change status to Approved.'))
		if self.state == "approved" and self.approved == False:
			raise Warning(_('Sorry! you can not change status to Approved first Approve application.'))
		if self.state == "denied" and self.approved == True:
			raise Warning(_('Sorry! you can not change status to Rejected.'))
		if self.state == "denied" and self.denied == False:
			raise Warning(_('Sorry! you can not change status to Rejected first Reject application..'))
		if self.state == "recommended1" and self.evaluate == False:
			raise Warning(_('Sorry! you can not change status to Recommended first Recommended application..'))
		if self.state == "validated" and self.recommended1 == False:
			raise Warning(_('Sorry! you can not change status to Validated first Validate application..'))
		if self.state == "recommended2" and self.validate == False:
			raise Warning(_('Sorry! you can not change status to Recommended first Recommended application..'))
		if not self.env.user.has_group('hwseta_etqe.group_seta_administrator'):
			if not self.is_extension_of_scope and not self.is_existing_provider:
				for line in self.qualification_ids:
					if line.qualification_id.is_exit_level_outcomes == False:
						if line.minimum_credits > line.total_credits:
							raise Warning(_("Sum of checked unit standards credits point should be greater than or equal to Minimum credits point !!"))
	#         for line in self.skills_programme_ids:
	#             if int(line.minimum_credits) > line.total_credits:
	#                 raise Warning(_("Sum of checked unit standards credits point should be greater than or equal to Minimum credits point in Skills Programme!!"))
		return res

	@api.model
	def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False, context=None):
		ctx = dict(self._context or {})
		user_obj = self.env['res.users'].search([('id', '=', self._uid)])
		provider_obj = self.env['res.partner'].search([('id', '=', user_obj.partner_id.id)])
		today = datetime.today().date()
		if provider_obj:
			#code to show re-accreditation option before expiry date ,as per mentioned days in ETQE configuration
			etqe_conf = self.env['etqe.config'].search([])
			if etqe_conf:
				etqe_brw = self.env['etqe.config'].browse(etqe_conf[0].id)
				if provider_obj.provider_end_date and etqe_brw.before_expiry_visible_days:
					d1 = datetime.strptime(str(provider_obj.provider_end_date), "%Y-%m-%d")
					d2 = datetime.strptime(str(today), "%Y-%m-%d")
					if abs((d1 - d2).days) <= etqe_brw.before_expiry_visible_days:
						return super(provider_accreditation, self.with_context(active=False)).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
			if str(provider_obj.provider_end_date) >= str(today):
			#if provider_obj.provider_status_Id == 'Active':
				return super(provider_accreditation, self.with_context(active=True)).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
			elif str(provider_obj.provider_end_date) < str(today):
			#elif provider_obj.provider_status_Id == 'Expired':
				return super(provider_accreditation, self.with_context(active=False)).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		return super(provider_accreditation, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu, context=ctx)

	@api.multi
	def unlink(self):
		''' Inherited to restrict deleting records '''
		raise Warning(_('Sorry! You cannot delete record'))
		return super(provider_accreditation, self).unlink()

	@api.multi
	def copy(self):
		''' Inherited to avoid duplicating records '''
		raise Warning(_('Sorry! You cannot create duplicate record'))
		return super(provider_accreditation, self).copy()
provider_accreditation()

class learner_assessment_line(models.Model):
	_name = 'learner.assessment.line'

	@api.multi
	def _get_provider(self):
		''' Getting provider from Assessment via context passed in xml.'''
		context = self._context
		provider_id = context.get('provider', False)
		return provider_id
#     name = fields.Char(string='Name')
	provider_assessment_ref_id = fields.Many2one('provider.assessment', string='provider_assessment_ref')
#     learner_id = fields.Many2one('etqe.learner', string='Learner', required=True)
	learner_id = fields.Many2one('hr.employee', string='Learners', required=True)
	assessors_id = fields.Many2one("hr.employee", string='Assessors', domain=[('is_active_assessor','=',True),('is_assessors', '=', True)])
	moderators_id = fields.Many2one("hr.employee", string='Moderator', domain=[('is_active_moderator','=',True),('is_moderators', '=', True)])
	learner_identity_number = fields.Char(string='Learner Number', track_visibility='onchange')
	timetable_id = fields.Many2one("learner.timetable", 'TimeTable')
	verify = fields.Boolean(string="Verification")
	provider_id = fields.Many2one('res.partner', string="Provider", track_visibility='onchange', default=_get_provider)
	identification_id = fields.Char(string="National Id",)

	qual_learner_assessment_line_id = fields.Many2many('provider.qualification', 'qualification_id', 'qual_learner_assessment_line_id', string='Qualification')
#     skill_learner_assessment_line_id = fields.Many2many('skills.programme', 'skills_id', 'skill_learner_assessment_line_id', string='Skills')
	unit_standards_learner_assessment_line_id = fields.Many2many('provider.qualification.line', 'unit_standards_id', 'unit_standards_learner_assessment_line_id', string='Unit Standards')

	@api.multi
	def onchange_assessors_id(self, assessors_id, moderators_id):
		res = {}
		if not assessors_id and moderators_id:
			return res
		if assessors_id and moderators_id:
			if assessors_id == moderators_id:
				res.update({
					'value':{
								'assessors_id' : '',
								'moderators_id':'',

							 },
					 'warning': {'title': 'Error!', 'message': 'Assessor  And Moderator Cant be same in a row'},
					})

		return res

	@api.model
	def default_get(self, fields):
		context = self._context
		if context is None:
			context = {}
		res = super(learner_assessment_line, self).default_get(fields)
		provider_id = context.get('provider', False)
		if provider_id:
			res.update(provider_id=provider_id)
		return res

	@api.multi
	def onchange_provider(self, provider_id):
#         provider_list=[]
#         learner_obj = self.env['learning.programme'].search([])
#         for learner in learner_obj:
#             for learner_line in learner.learner_ids:
#                 for load_learner in learner_line:
#                     for line in load_learner.proj_enrolled_ids:
#                         for l in line:
#                             if l.provider_id.id==provider_id:
#                                 provider_list.append(load_learner.id)
#         return {'domain': {'learner_id': [('id', 'in', provider_list)]}}
#         return True

#         learner_obj = self.env['hr.employee'].search([('is_learner', '=', True)])
#         for learner in learner_obj:
#             provider_list.append(learner.id)
#         return {'domain': {'learner_id': [('id', 'in', provider_list)]}}

		# This code is used to filter and show only logged user's learner on 06/10/2016
		learner_list = []
		if self._uid == 1:
			etqe_learner_obj = self.env['hr.employee'].search([('is_learner', '=', True), ('provider_learner', '=', True), ('state', 'in', ['active', 'replacement'])])
			for learner in etqe_learner_obj:
				learner_list.append(learner.id)
		else:
			etqe_learner_obj = self.env['hr.employee'].search([('is_learner', '=', True), ('provider_learner', '=', True), ('state', 'in', ['active', 'replacement'])])  # ,('logged_provider_id','=',user.partner_id.id)
			for learner in etqe_learner_obj:
				for qual_line in learner.learner_qualification_ids:
					provider = qual_line.provider_id.id
					if provider:
						if provider == self.env.user.partner_id.id:
							learner_list.append(learner.id)
#         load qualification as per provider
		qualification = []
		if self._uid == 1:
			qualification_obj = self.env['provider.qualification'].search([])
			for quali_id in qualification_obj:
					qualification.append(quali_id.id)
		else:
			provider_obj = self.env['res.partner'].search([('provider', '=', True), ('id', '=', provider_id)])
			if provider_obj.qualification_ids:
				for qualification_id in provider_obj.qualification_ids:
					for quali_id in qualification_id.qualification_id:
						qualification.append(quali_id.id)
			elif provider_obj.qualification_campus_ids:
				for qualification_campus_id in provider_obj.qualification_campus_ids:
					for quali_id in qualification_campus_id.qualification_id:
						qualification.append(quali_id.id)
#         load skill programme as per provider
		skill_programme = []
		if self._uid == 1:
			skill_obj = self.env['skills.programme'].search([])
			for quali_id in skill_obj:
					skill_programme.append(quali_id.id)
		else:
			provider_obj = self.env['res.partner'].search([('provider', '=', True), ('id', '=', provider_id)])
			if provider_obj.skills_programme_ids:
				for skill_ids in provider_obj.skills_programme_ids:
					for skill_id in skill_ids.skills_programme_id:
						skill_programme.append(skill_id.id)
			elif provider_obj.skills_programme_campus_ids:
				for skill_ids in provider_obj.skills_programme_campus_ids:
					for skill_id in skill_ids.skills_programme_id:
						skill_programme.append(skill_id.id)
#         load Assessor as per provider
		assessors_list = []
		if self._uid == 1:
			assessor_obj = self.env['hr.employee'].search([('is_active_assessor','=',True),('is_assessors', '=', True)])
			for assessor in assessor_obj:
					assessors_list.append(assessor.id)
		else:
			provider_obj = self.env['res.partner'].search([('provider', '=', True), ('id', '=', provider_id)])
			if provider_obj.assessors_ids:
				for assessor_id in provider_obj.assessors_ids:
					for assessor in assessor_id.assessors_id:
						assessors_list.append(assessor.id)
			elif provider_obj.assessors_campus_ids:
				for assessors_campus_id in provider_obj.assessors_campus_ids:
					for assessor in assessors_campus_id.assessors_id:
						assessors_list.append(assessor.id)
		#   load Moderator as per provider
		moderator_list = []
		if self._uid == 1:
			moderator_obj = self.env['hr.employee'].search([('is_active_moderator','=',True),('is_moderators', '=', True)])
			for moderator in moderator_obj:
					moderator_list.append(moderator.id)
		else:
			provider_obj = self.env['res.partner'].search([('provider', '=', True), ('id', '=', provider_id)])
			if provider_obj.moderators_ids:
				for moderator_id in provider_obj.moderators_ids:
					for moderator in moderator_id.moderators_id:
						moderator_list.append(moderator.id)
			elif provider_obj.moderators_campus_ids:
				for moderators_campus_id in provider_obj.moderators_campus_ids:
					for moderator in moderators_campus_id.moderators_id:
						moderator_list.append(moderator.id)
		return {'domain': {'learner_id': [('id', 'in', list(set(learner_list)))],
						   'qual_learner_assessment_line_id':[('id', 'in', qualification)],
						   'skill_learner_assessment_line_id':[('id', 'in', skill_programme)],
						   'assessors_id':[('id', 'in', assessors_list)],
						   'moderators_id':[('id', 'in', moderator_list)]
						   }}
#     @api.multi
#     def onchange_learner_id(self, learner_id,):
#         res = {}
#         if not learner_id :
#             return res
#         learner_data = self.env['hr.employee'].browse(learner_id)
#         l1 =[]
#         unit_lst=[]
#         for l in learner_data.learner_qualification_ids:
#             ulst = self.env['learner.registration.qualification.line'].search([('learner_reg_id','=',l.id)])
#             if ulst:
#                 if l.learner_qualification_parent_id.qualification_line:
#                     for ul in l.learner_qualification_parent_id.qualification_line:
#                         if ul.id not in unit_lst:
#                             unit_lst.append(ul.id)
#             l1.append(l.learner_qualification_parent_id.id)
#         if learner_data.learner_qualification_ids:
#             for l in learner_data.learner_qualification_ids:
#                 ulst = self.env['learner.registration.qualification.line'].search([('learner_reg_id','=',l.id)])
#                 if ulst:
#                     if l.learner_qualification_parent_id.qualification_line :
#                         for ul in l.learner_qualification_parent_id.qualification_line:
#                             if ul.id not in unit_lst:
#                                 unit_lst.append(ul.id)
#                 l1.append(l.learner_qualification_parent_id.id)
#
#
#         res.update({
#                     'value':{
#                                 'learner_identity_number' : learner_data.learner_reg_no,
#                                 'identification_id':learner_data.identification_id,
#                             'qual_learner_assessment_line_id':[(6,0,l1)],
# #                             'unit_standards_learner_assessment_line_id':[(6,0,[])],
#                              },
# #                    'domain':{'unit_standards_learner_assessment_line_id':[('id','in',unit_lst)]}
#                     })
#         return res
	@api.multi
	def onchange_learner_reg_no(self, learner_identity_number):
		res = {}
		if not learner_identity_number:
			return res

		learner_obj = self.env['hr.employee'].search([('learner_reg_no', '=', learner_identity_number)])
		res.update({
					'value':{
							 'learner_id':learner_obj.id,
#                              'qual_learner_assessment_line_id':learner_obj.learner_qualification_ids.learner_qualification_parent_id,
							 }
					})
		return res

#     @api.multi
#     def onchange_identification_id(self,identification_id):
#         res = {}
#         if not identification_id:
#             return res
#
#         learner_obj = self.env['hr.employee'].search([('identification_id','=',identification_id)])
#         l1 =[]
#         unit_lst=[]
#         for l in learner_obj.learner_qualification_ids:
#             ulst = self.env['learner.registration.qualification.line'].search([('learner_reg_id','=',l.id)])
#             if ulst:
#                 if l.learner_qualification_parent_id.qualification_line :
#                     for ul in l.learner_qualification_parent_id.qualification_line:
#                         if ul.id not in unit_lst:
#                             unit_lst.append(ul.id)
#             l1.append(l.learner_qualification_parent_id.id)
#
#         res.update({
#                     'value':{
#                              'learner_id':learner_obj.id,
# #                             'qual_learner_assessment_line_id':[(6,0,l1)],
# #                             'unit_standards_learner_assessment_line_id':[(6,0,unit_lst)]
#                              }
#                     })
#         return res

	@api.multi
	def onchange_qualification_ids(self, qualification_id):
		res = {}
		unit_standards_list = []
		if not qualification_id[0][2] :
			return res
		for qual_id in qualification_id[0][2]:
			qualification_master = self.env['provider.qualification'].browse(qual_id)
			for unit_standards in qualification_master.qualification_line:
				unit_standards_list.append(unit_standards.id)
		return {'domain': {'unit_standards_learner_assessment_line_id': [('id', 'in', unit_standards_list)]}}
learner_assessment_line()

class learner_assessment_achieve_line(models.Model):
	_name = 'learner.assessment.achieve.line'
#     name = fields.Char(string='Name')
	provider_assessment_achieve_ref_id = fields.Many2one('provider.assessment', string='provider_assessment_achieve_ref')
#     learner_id = fields.Many2one('etqe.learner', string='Learner', required=True)
	learner_id = fields.Many2one('hr.employee', string='Learner', required=True)

	assessors_id = fields.Many2one("hr.employee", string='Assessors', domain=[('is_assessors', '=', True)])
	moderators_id = fields.Many2one("hr.employee", string='Moderator', domain=[('is_moderators', '=', True)])
	learner_identity_number = fields.Char(string='Learner Number', track_visibility='onchange')
	timetable_id = fields.Many2one("learner.timetable", 'TimeTable')
	achieve = fields.Boolean(string="Achieved")
	identification_id = fields.Char(string="National Id", track_visibility='onchange')
	qual_learner_assessment_achieve_line_id = fields.Many2many('provider.qualification', 'achieve_asse_qual_rel', 'qualification_achieve_id', 'qual_achieve_learner_assessment_line_id', string='Qualification')
	#skill_learner_assessment_achieve_line_id = fields.Many2many('skills.programme', 'achieve_asse_skills_rel', 'skills_achieve_id', 'skill_learner_assessment_achieve_line_id', string='Skills')
	unit_standards_learner_assessment_achieve_line_id = fields.Many2many('provider.qualification.line', 'achieve_asse_unit_rel', 'unit_standards_achieve_id', 'unit_standards_learner_assessment_achieve_line_id', string='Unit Standards')

#     sdl_number = fields.Char(string='SDL Number')
#     seta_id = fields.Many2one('seta.branches', string='SETA Id')
#     sic_code = fields.Many2one('hwseta.sic.master')
#     email = fields.Char(string='Email')
#     phone = fields.Char(string='Phone')
#     mobile = fields.Char(string='Mobile')
learner_assessment_achieve_line()

class learner_assessment_verify_line(models.Model):
	_name = 'learner.assessment.verify.line'

	provider_assessment_verify_ref_id = fields.Many2one('provider.assessment', string='provider_assessment_verify_ref')
	learner_id = fields.Many2one('hr.employee', string='Learner', required=True)
	assessors_id = fields.Many2one("hr.employee", string='Assessors', domain=[('is_assessors', '=', True)])
	moderators_id = fields.Many2one("hr.employee", string='Moderator', domain=[('is_moderators', '=', True)])
	learner_identity_number = fields.Char(string='Learner Number', track_visibility='onchange')
	identification_id = fields.Char(string="National Id", track_visibility='onchange')
	timetable_id = fields.Many2one("learner.timetable", 'TimeTable')
	verify = fields.Boolean(string="Verified")
	qual_learner_assessment_verify_line_id = fields.Many2many('provider.qualification', 'verify_asse_qual_rel', 'qualification_verify_id', 'qual_learner_assessment_verify_line_id', string='Qualification')
	skill_learner_assessment_verify_line_id = fields.Many2many('skills.programme', 'verify_asse_skills_rel', 'skills_verify_id', 'skill_learner_assessment_verify_line_id', string='Skills')
	unit_standards_learner_assessment_verify_line_id = fields.Many2many('provider.qualification.line', 'verify_asse_unit_rel', 'unit_standards_verify_id', 'unit_standards_learner_assessment_verify_line_id', string='Unit Standards')
	comment = fields.Char(string="Comment")
learner_assessment_verify_line()

class learner_assessment_evaluate_line(models.Model):
	_name = 'learner.assessment.evaluate.line'

	provider_assessment_evaluate_ref_id = fields.Many2one('provider.assessment', string='provider_assessment_Evaluate_ref')
	learner_id = fields.Many2one('hr.employee', string='Learner', required=True)
	assessors_id = fields.Many2one("hr.employee", string='Assessors', domain=[('is_assessors', '=', True)])
	moderators_id = fields.Many2one("hr.employee", string='Moderator', domain=[('is_moderators', '=', True)])
	learner_identity_number = fields.Char(string='Learner Number', track_visibility='onchange')
	identification_id = fields.Char(string="National Id", track_visibility='onchange')
	timetable_id = fields.Many2one("learner.timetable", 'TimeTable')
	evaluate = fields.Boolean(string="Evaluated")
	qual_learner_assessment_evaluate_line_id = fields.Many2many('provider.qualification', 'evaluate_asse_qual_rel', 'qualification_verify_id', 'qual_learner_assessment_verify_line_id', string='Qualification')
	skill_learner_assessment_evaluate_line_id = fields.Many2many('skills.programme', 'evaluate_asse_skills_rel', 'skills_verify_id', 'skill_learner_assessment_verify_line_id', string='Skills')
	unit_standards_learner_assessment_evaluate_line_id = fields.Many2many('provider.qualification.line', 'evaluate_asse_unit_rel', 'unit_standards_verify_id', 'unit_standards_learner_assessment_verify_line_id', string='Unit Standards')
	comment = fields.Char(string="Comment")
learner_assessment_evaluate_line()

class learner_assessment_achieved_line(models.Model):
	_name = 'learner.assessment.achieved.line'

	provider_assessment_achieved_ref_id = fields.Many2one('provider.assessment', string='provider_assessment_achieved_ref')
	learner_id = fields.Many2one('hr.employee', string='Learner', required=True)
	assessors_id = fields.Many2one("hr.employee", string='Assessors', domain=[('is_assessors', '=', True)])
	moderators_id = fields.Many2one("hr.employee", string='Moderator', domain=[('is_moderators', '=', True)])
	learner_identity_number = fields.Char(string='Learner Number', track_visibility='onchange')
	identification_id = fields.Char(string="National Id", track_visibility='onchange')
	timetable_id = fields.Many2one("learner.timetable", 'TimeTable')
	is_learner_achieved = fields.Boolean('Achieved')
	qual_learner_assessment_achieved_line_id = fields.Many2many('provider.qualification', 'achieved_asse_qual_rel', 'qualification_achieved_id', 'qual_achieve_learner_assessment_line_id', string='Qualification')
	skill_learner_assessment_achieved_line_id = fields.Many2many('skills.programme', 'achieved_asse_skills_rel', 'skills_achieved_id', 'skill_learner_assessment_achieve_line_id', string='Skills')
	unit_standards_learner_assessment_achieved_line_id = fields.Many2many('provider.qualification.line', 'achieved_asse_unit_rel', 'unit_standards_achieved_id', 'unit_standards_learner_assessment_achieve_line_id', string='Unit Standards')
learner_assessment_achieved_line()

class assessment_status(models.Model):
	_name = 'assessment.status'

	name = fields.Many2one('res.users', string='Name')
	state = fields.Selection([
			('draft', 'Draft'),
			('submitted', 'Submitted'),
			('verify', 'Verified'),
			('evaluate', 'Evaluated'),
			('achieved', 'Achievement'),

		], string='State', index=True, readonly=True, default='draft',
		track_visibility='onchange', copy=False)
	state_title = fields.Char("Status")
	s_date = fields.Datetime(string='Date', default=datetime.now())
	update_date = fields.Datetime(string='Update Date', default=datetime.now())
	comment = fields.Char(string='Comment')
	pro_id = fields.Many2one('provider.assessment', string='assessment', track_visibility='onchange')
assessment_status()

class provider_assessment(models.Model):
	_inherit = 'provider.assessment'

	@api.model
	def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
		""" Override read_group to filter provider assessment status count based on logged provider """
		if self.env.user.id != 1 and self.env.user.partner_id.provider == True:
			assessment_list = []
			self._cr.execute("select id from provider_assessment where provider_id='%s'" % (self.env.user.partner_id.id,))
			assessment_ids = map(lambda x:x[0], self._cr.fetchall())
			assessment_list.extend(assessment_ids)
			self._cr.execute("select id from provider_assessment where create_uid='%s'" % (self.env.user.id,))
			assessment_uids = map(lambda x:x[0], self._cr.fetchall())
			assessment_list.extend(assessment_uids)
			domain.append(('id', 'in', assessment_list))
		return super(provider_assessment, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

	@api.model
	def default_get(self, fields_list):
		res = super(provider_assessment, self).default_get(fields_list)
		current_date = datetime.now()
		todays_date = current_date.strftime('%Y-%m-%d')
		for fiscal_year in self.env['account.fiscalyear'].search([]):
			start_fiscal = str(datetime.strptime(fiscal_year.date_start, '%Y-%m-%d'))
			end_fiscal = str(datetime.strptime(fiscal_year.date_stop, '%Y-%m-%d'))
			todays_year = todays_date.split('-')[0]
			start_fiscal_year = start_fiscal.split('-')[0]
			end_fiscal_year = end_fiscal.split('-')[0]
			if todays_year:
				if int(start_fiscal_year) <= int(todays_year):
					if int(end_fiscal_year) >= int(todays_year):
						res.update({'fiscal_year':fiscal_year.id})
#         learner_obj = self.env['hr.employee'].search([('logged_provider_id', '=', self.env.user.partner_id.id)])
#         assessment_line_list = []
#         for learner in learner_obj:
#             for learner_qual in learner.learner_qualification_ids:
#                 if learner_qual.is_learner_achieved == False and learner_qual.provider_id.id == self.env.user.partner_id.id:
#                     qual_list, unit_line_list = [], []
#                     qual_list.append(learner_qual.learner_qualification_parent_id.id)
#                     learners_assessor_id = learner_qual.assessors_id.id
#                     learners_moderator_id = learner_qual.moderators_id.id
#                     for unit_line in learner_qual.learner_registration_line_ids:
#                         if unit_line.achieve == False and unit_line.selection:
#                             # pro_qual_id = self.env['provider.qualification.line'].search([('title', '=', unit_line.title)]).id
#                             pro_qual_id = self.env['provider.qualification.line'].search([('title', '=', unit_line.title)]).id
#                             if pro_qual_id:
#                                 unit_line_list.append(pro_qual_id)
#                     if qual_list and unit_line_list:
#                         assessment_line_list.append((0, 0, {'identification_id':learner.learner_identification_id or '', 'learner_id':learner.id, 'qual_learner_assessment_line_id': [[6, 0, list(set(qual_list))]], 'unit_standards_learner_assessment_line_id':[[6, 0, list(set(unit_line_list))]], 'skill_learner_assessment_line_id':'', 'assessors_id':learners_assessor_id, 'moderators_id':learners_moderator_id}))
#         res.update({'learner_ids':assessment_line_list})
		return res

	@api.one
	def _get_login_user(self):
		current_login= self.env.user
		if current_login.partner_id.provider and self.state == 'submitted':
			self.is_provider = True

	@api.multi
	def onchange_qdm_provider(self, is_qdm_provider):
		if is_qdm_provider:
			partner_obj = self.env['res.partner'].search([('id', '=', self.env.user.partner_id.id), ('is_qdm_provider','=',True)])
			if not partner_obj:
				return {'value': {'is_qdm_provider': False},\
						'warning': {'title':'Invalid QDM Provider','message':'Sorry! You are not QDM Provider!'} }

	@api.depends('learner_achieved_ids',  'learner_achieved_ids_for_skills', 'learner_achieved_ids_for_lp')
	def _get_total_learner_count(self):
		''' This method is used to get total learner count '''
		count = 0
		if self.learner_achieved_ids:
			for line in self.learner_achieve_ids:
				count += 1
			self.total_learner_count = count
		if self.learner_achieved_ids_for_skills:
			for line in self.learner_achieved_ids_for_skills:
				count += 1
			self.total_learner_count = count
		if self.learner_achieved_ids_for_lp:
			for line in self.learner_achieved_ids_for_lp:
				count += 1
			self.total_learner_count = count

	@api.depends('learner_achieved_ids',  'learner_achieved_ids_for_skills', 'learner_achieved_ids_for_lp')
	def _get_achieved_learner_count(self):
		'''This method is used to get achieved learner count based on Learner master status'''
		count = 0
		if self.learner_achieved_ids:
			for line in self.learner_achieve_ids:
				for q_line in line.learner_id.learner_qualification_ids:
					if q_line.is_learner_achieved and q_line.qual_status == 'Achieved':
						count += 1
			self.achieved_learner_count = count
		if self.learner_achieved_ids_for_skills:
			for line in self.learner_achieved_ids_for_skills:
				for s_line in line.learner_id.skills_programme_ids:
					if s_line.is_learner_achieved and s_line.skill_status == 'Achieved':
						count += 1
			self.achieved_learner_count = count
		if self.learner_achieved_ids_for_lp:
			for line in self.learner_achieved_ids_for_lp:
				for l_line in line.learner_id.learning_programme_ids:
					if l_line.is_learner_achieved and l_line.lp_status == 'Achieved':
						count += 1
			self.achieved_learner_count = count

	@api.depends('learner_achieved_ids', 'learner_achieved_ids_for_skills', 'learner_achieved_ids_for_lp')
	def _get_partially_achieved_learner_count(self):
		'''This method is used to get partially achieved learner count based on learner master status'''
		count = 0
		if self.learner_achieved_ids:
			for line in self.learner_achieve_ids:
				for q_line in line.learner_id.learner_qualification_ids:
					if q_line.is_complete and not q_line.is_learner_achieved and q_line.qual_status != 'Achieved':
						count += 1
			self.partially_achieved_learner_count = count
		if self.learner_achieved_ids_for_skills:
			for line in self.learner_achieved_ids_for_skills:
				for s_line in line.learner_id.skills_programme_ids:
					if s_line.is_complete and not s_line.is_learner_achieved and s_line.skill_status != 'Achieved':
						count += 1
			self.partially_achieved_learner_count = count
		if self.learner_achieved_ids_for_lp:
			for line in self.learner_achieved_ids_for_lp:
				for l_line in line.learner_id.learning_programme_ids:
					if l_line.is_complete and not l_line.is_learner_achieved and l_line.lp_status != 'Achieved':
						count += 1
			self.partially_achieved_learner_count = count

	@api.multi
	def onchange_batch_id(self, batch_id, qual_skill_assessment):
		assessment_line_list, batch_lst = [], []
		user = self._uid
		user_obj = self.env['res.users']
		user_data = user_obj.browse(user)
		if qual_skill_assessment:
			if not user_data.partner_id.provider:
				if qual_skill_assessment == 'qual':
					all_batch_ids = self.env['batch.master'].search([('qual_skill_batch','=','qual'),('batch_status','=','open')])
					if all_batch_ids:
						for b_id in all_batch_ids:
							batch_lst.append(b_id.id)
				elif qual_skill_assessment == 'skill':
					all_batch_ids = self.env['batch.master'].search([('qual_skill_batch','=','skill'),('batch_status','=','open')])
					if all_batch_ids:
						for b_id in all_batch_ids:
							batch_lst.append(b_id.id)
				# Changes Added by Ganesh
				elif qual_skill_assessment == 'lp':
					all_batch_ids = self.env['batch.master'].search([('qual_skill_batch','=','lp'),('batch_status','=','open')])
					if all_batch_ids:
						for b_id in all_batch_ids:
							batch_lst.append(b_id.id)
			elif user_data.partner_id.provider:
				for batch in self.env.user.partner_id.provider_batch_ids:
					if qual_skill_assessment == 'qual':
						if batch.batch_master_id.qual_skill_batch == 'qual' and batch.batch_status == 'open':
							batch_lst.append(batch.batch_master_id.id)
					elif qual_skill_assessment == 'skill':
						if batch.batch_master_id.qual_skill_batch == 'skill' and batch.batch_status == 'open':
							batch_lst.append(batch.batch_master_id.id)
					# Changes Added by Ganesh
					elif qual_skill_assessment == 'lp':
						if batch.batch_master_id.qual_skill_batch == 'lp' and batch.batch_status == 'open':
							batch_lst.append(batch.batch_master_id.id)
		if batch_id and qual_skill_assessment == 'qual':
			learner_obj = self.env['hr.employee'].search([('logged_provider_id', '=', self.env.user.partner_id.id)])
			if learner_obj:
				for learner in learner_obj:
					for learner_qual in learner.learner_qualification_ids:
						if learner_qual.batch_id.id == batch_id and  learner_qual.is_learner_achieved == False and learner_qual.provider_id.id == self.env.user.partner_id.id:
							qual_list, unit_line_list = [], []
							qual_list.append(learner_qual.learner_qualification_parent_id.id)
							learners_assessor_id = learner_qual.assessors_id.id
							learners_moderator_id = learner_qual.moderators_id.id
							for unit_line in learner_qual.learner_registration_line_ids:
								if unit_line.achieve == False and unit_line.selection:
									pro_qual_id = self.env['provider.qualification.line'].search(['|',('id_no', '=', 'unit_line.id_data'),('title', '=', unit_line.title),('line_id','=',learner_qual.learner_qualification_parent_id.id)]).id
									if pro_qual_id:
										unit_line_list.append(pro_qual_id)
							if qual_list and unit_line_list:
								if learner.citizen_resident_status_code in ['dual','PR', 'sa']:
									assessment_line_list.append((0, 0, {'identification_id':learner.learner_identification_id or '', 'learner_id':learner.id, 'qual_learner_assessment_line_id': [[6, 0, list(set(qual_list))]], 'unit_standards_learner_assessment_line_id':[[6, 0, list(set(unit_line_list))]], 'skill_learner_assessment_line_id':'', 'assessors_id':learners_assessor_id, 'moderators_id':learners_moderator_id}))
								elif learner.citizen_resident_status_code in ['other','unknown']:
									assessment_line_list.append((0, 0, {'identification_id':learner.national_id or '', 'learner_id':learner.id, 'qual_learner_assessment_line_id': [[6, 0, list(set(qual_list))]], 'unit_standards_learner_assessment_line_id':[[6, 0, list(set(unit_line_list))]], 'skill_learner_assessment_line_id':'', 'assessors_id':learners_assessor_id, 'moderators_id':learners_moderator_id}))

		#changes by pradip
		elif batch_id and qual_skill_assessment == 'skill':
			learner_obj = self.env['hr.employee'].search([('logged_provider_id_for_skills', '=', self.env.user.partner_id.id)])
			if learner_obj:
				for learner in learner_obj:
					for learner_skill in learner.skills_programme_ids:
						if  learner_skill.batch_id.id == batch_id and  learner_skill.is_learner_achieved == False and learner_skill.provider_id.id == self.env.user.partner_id.id:
							skill_list, unit_line_list = [], []
							skill_list.append(learner_skill.skills_programme_id.id)
							learners_assessor_id = learner_skill.assessors_id.id
							learners_moderator_id = learner_skill.moderators_id.id
							for unit_line in learner_skill.unit_standards_line:
								if unit_line.achieve == False and unit_line.selection:
									pro_skill_id = self.env['skills.programme.unit.standards'].search([('title', '=', unit_line.title),('skills_programme_id','=',learner_skill.skills_programme_id.id)]).id
									if pro_skill_id:
										unit_line_list.append(pro_skill_id)
							if skill_list and unit_line_list:
								if learner.citizen_resident_status_code in ['dual','PR', 'sa']:
									assessment_line_list.append((0, 0, {'identification_id':learner.learner_identification_id or '', 'learner_id':learner.id, 'skill_learner_assessment_line_id': [[6, 0, list(set(skill_list))]], 'skill_unit_standards_learner_assessment_line_id':[[6, 0, list(set(unit_line_list))]], 'assessors_id':learners_assessor_id, 'moderators_id':learners_moderator_id}))
								elif learner.citizen_resident_status_code in ['other','unknown']:
									 assessment_line_list.append((0, 0, {'identification_id':learner.national_id or '', 'learner_id':learner.id, 'skill_learner_assessment_line_id': [[6, 0, list(set(skill_list))]], 'skill_unit_standards_learner_assessment_line_id':[[6, 0, list(set(unit_line_list))]], 'assessors_id':learners_assessor_id, 'moderators_id':learners_moderator_id}))
		# Changes Added by Ganesh
		elif batch_id and qual_skill_assessment == 'lp':
			learner_obj = self.env['hr.employee'].search([('logged_provider_id_for_lp', '=', self.env.user.partner_id.id)])
			if learner_obj:
				for learner in learner_obj:
					for learner_lp in learner.learning_programme_ids:
						if learner_lp.batch_id.id == batch_id and  learner_lp.is_learner_achieved == False and learner_lp.provider_id.id == self.env.user.partner_id.id:
							lp_list, unit_line_list = [], []
							lp_list.append(learner_lp.learning_programme_id.id)
							learners_assessor_id = learner_lp.assessors_id.id
							learners_moderator_id = learner_lp.moderators_id.id
							for unit_line in learner_lp.unit_standards_line:
								if unit_line.achieve == False and unit_line.selection:
									pro_lp_id = self.env['etqe.learning.programme.unit.standards'].search([('title', '=', unit_line.title),('learning_programme_id','=',learner_lp.learning_programme_id.id)]).id
									if pro_lp_id:
										unit_line_list.append(pro_lp_id)
							if lp_list and unit_line_list:
								if learner.citizen_resident_status_code in ['dual','PR', 'sa']:
									assessment_line_list.append((0, 0, {'identification_id':learner.learner_identification_id or '', 'learner_id':learner.id, 'lp_learner_assessment_line_id': [[6, 0, list(set(lp_list))]], 'lp_unit_standards_learner_assessment_line_id':[[6, 0, list(set(unit_line_list))]], 'assessors_id':learners_assessor_id, 'moderators_id':learners_moderator_id}))
								elif learner.citizen_resident_status_code in ['other','unknown']:
									assessment_line_list.append((0, 0, {'identification_id':learner.national_id or '', 'learner_id':learner.id, 'lp_learner_assessment_line_id': [[6, 0, list(set(lp_list))]], 'lp_unit_standards_learner_assessment_line_id':[[6, 0, list(set(unit_line_list))]], 'assessors_id':learners_assessor_id, 'moderators_id':learners_moderator_id}))
		if batch_id and qual_skill_assessment == 'qual':
			return {'value':{'learner_ids':assessment_line_list}}
		elif batch_id and qual_skill_assessment == 'skill':
			return {'value':{'learner_ids_for_skills':assessment_line_list}}
		elif batch_id and qual_skill_assessment == 'lp':
			return {'value':{'learner_ids_for_lp':assessment_line_list}}
		return {'domain':{'batch_id':[('id','in',batch_lst)]}}

	@api.model
	def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
		user = self._uid
		if user != 1:
			partner_data = self.env['res.users'].browse(user).partner_id
			user_obj = self.env['res.users']
			user_data = user_obj.browse(user)
			user_groups = user_data.groups_id
			for group in user_groups:
				if group.name in ['ETQE Manager', 'ETQE Executive Manager', 'ETQE Provincial Manager', 'ETQE Officer', 'ETQE Provincial Officer', 'ETQE Administrator', 'ETQE Provincial Administrator', 'Applicant Skills Development Provider']:
#                     args.append(('provider_id', '=', partner_data.id))
					return super(provider_assessment, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
			if partner_data.provider:
				args.append(('provider_id', '=', partner_data.id))
#                 employee_data = self.env['hr.employee'].search([('user_id', '=', user)])
#                 if employee_data.is_assessors :
#                     args.append(('assessors_id', '=', employee_data.id))
#                 if employee_data.is_moderators :
#                     args.append(('moderators_id', '=', employee_data.id))
#             else :
#                 employee_data = self.env['hr.employee'].search([('user_id', '=', user)])
#                 if employee_data.is_assessors :
#                     args.append(('assessors_id', '=', employee_data.id))
#                 if employee_data.is_moderators :
#                     args.append(('moderators_id', '=', employee_data.id))
		return super(provider_assessment, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

	@api.multi
	def action_print_certificate_button(self):
		data1 = self.read()
		data = data1[0]
		if self._context is None:
			self._context = {}
		datas = {
			'ids': self._context.get('active_ids', []),
			'model': 'provider.assessment',
			'form': data,
		}
		return self.pool['report'].get_action(self._cr, self._uid, [], 'hwseta_etqe.report_achievement_certificate', data=datas, context=self._context)

	@api.multi
	def action_print_qualification_sor_button(self):
		data1 = self.read()
		data = data1[0]
		if self._context is None:
			self._context = {}
		datas = {
			'ids': self._context.get('active_ids', []),
			'model': 'provider.assessment',
			'form': data,
		}
		return self.pool['report'].get_action(self._cr, self._uid, [], 'hwseta_etqe.qualification_stmt_of_result_report', data=datas, context=self._context)

	@api.multi
	def action_print_statement_of_achievement(self):
		data1 = self.read()
		data = data1[0]
		if self._context is None:
			self._context = {}
		datas = {
			'ids': self._context.get('active_ids', []),
			'model': 'provider.assessment',
			'form': data,
		}
		return self.pool['report'].get_action(self._cr, self._uid, [], 'hwseta_etqe.report_qdm_achievement_certificate', data=datas, context=self._context)


	@api.multi
	def action_print_skills_statement_of_results_button(self):
		data1 = self.read()
		data = data1[0]
		if self._context is None:
			self._context = {}
		datas = {
			'ids': self._context.get('active_ids', []),
			'model': 'provider.assessment',
			 'form': data,
		}
		return self.pool['report'].get_action(self._cr, self._uid, [], 'hwseta_etqe.report_skills_programme_statement_of_results', data=datas, context=self._context)

	# Changes Added by Ganesh For Learning Programme
	@api.multi
	def action_print_lp_certificate_button(self):
		data1 = self.read()
		data = data1[0]
		if self._context is None:
			self._context = {}
		datas = {
			'ids': self._context.get('active_ids', []),
			'model': 'provider.assessment',
			'form': data,
		}
		return self.pool['report'].get_action(self._cr, self._uid, [], 'hwseta_etqe.report_learning_programme_achievement_certificate', data=datas, context=self._context)

	@api.multi
	def action_print_lp_statement_of_result_button(self):
		data1 = self.read()
		data = data1[0]
		if self._context is None:
			self._context = {}
		datas = {
			'ids': self._context.get('active_ids', []),
			'model': 'provider.assessment',
			'form': data,
		}
		return self.pool['report'].get_action(self._cr, self._uid, [], 'hwseta_etqe.report_learning_programme_statement_of_result', data=datas, context=self._context)

	@api.multi
	def action_learner_status_button(self):
		data1 = self.read()
		data = data1[0]
		if self._context is None:
			self._context = {}

		datas = {
			'ids': self._context.get('active_ids', []),
			'model': 'provider.assessment',
			'form': data,
		}
		return self.pool['report'].get_action(self._cr, self._uid, [], 'hwseta_etqe.report_learner_status_report', data=datas, context=self._context)

	name = fields.Char(string='Name')
	state = fields.Selection([
			('draft', 'Draft'),
			('submitted', 'Submitted'),
			('learners', 'Learners'),
			('verify', 'Verified'),
			('evaluate', 'Evaluated'),
			('achieved', 'Achievement'),

		], string='Status', index=True, readonly=True, default='draft',
		track_visibility='onchange', copy=False)

	provider_accreditation_num = fields.Char(string='Identity Number', track_visibility='onchange', help="Provider Identity Number", size=50)
	qualification_id = fields.Many2one("provider.qualification", string='Qualification', track_visibility='onchange', readonly=True, ondelete='restrict')
	employer_id = fields.Many2one('res.partner', string="Employer", track_visibility='onchange')
	provider_id = fields.Many2one('res.partner', string="Provider", track_visibility='onchange', default=lambda self:self.env.user.partner_id.id)
#     learner_ids = fields.One2many('hr.employee', 'assessment_id', string='Learners', track_visibility='onchange')
	learner_ids = fields.One2many('learner.assessment.line', 'provider_assessment_ref_id', string='Learners', track_visibility='onchange')
	learner_achieve_ids = fields.One2many('learner.assessment.achieve.line', 'provider_assessment_achieve_ref_id', string='Learners', track_visibility='onchange')
	learner_verify_ids = fields.One2many('learner.assessment.verify.line', 'provider_assessment_verify_ref_id', string='learner verify ids', track_visibility='onchange')
	learner_evaluate_ids = fields.One2many('learner.assessment.evaluate.line', 'provider_assessment_evaluate_ref_id', string='Learners', track_visibility='onchange')
	learner_achieved_ids = fields.One2many('learner.assessment.achieved.line', 'provider_assessment_achieved_ref_id', string='Learners', track_visibility='onchange')
	fiscal_year = fields.Many2one('account.fiscalyear', string='Financial Year')
	learner_timetables = fields.One2many('hr.employee', 'assessment_timetables_id', string='Learners', track_visibility='onchange')
	learner_verification_ids = fields.One2many('hr.employee', 'assessment_verify_id', string='Learners', track_visibility='onchange')
	learner_verified_ids = fields.One2many('hr.employee', 'assessment_verified_id', string='Learners', track_visibility='onchange')
	assessors_id = fields.Many2one("hr.employee", string='Assessors', domain=[('is_assessors', '=', True)] , ondelete='restrict')
	moderators_id = fields.Many2one("hr.employee", string='Moderator', track_visibility='onchange', domain=[('is_moderators', '=', True)], ondelete='restrict')
	submited = fields.Boolean(string="Submited", track_visibility='onchange', default=False)
	verified = fields.Boolean(string="Verified", track_visibility='onchange', default=False)
	evaluated = fields.Boolean(string="Verified", track_visibility='onchange', default=False)
	assessed = fields.Boolean(string="Assessed", track_visibility='onchange', default=False)
	pro_learner_id = fields.Many2one('hr.employee', string='Learner', track_visibility='onchange')
	status = fields.Selection([('new', 'New'), ('done', 'Done')], string="status", track_visibility='onchange')
	start_date = fields.Date(string='Creation Date', default=datetime.now())
	# end_date = fields.Date(string='End Date')
	assessment_status = fields.One2many('assessment.status', 'pro_id', string='Assessment Status', track_visibility='onchange', readonly=True)
	comment = fields.Char(string='Comment')
	training_intent_form_doc = fields.Many2one('ir.attachment', string='Training Implementation Intent Form', help='Upload Document')
	verification_application_form_doc = fields.Many2one('ir.attachment', string='Verification Application Form', help='Upload Document')
	learner_matrix_doc = fields.Many2one('ir.attachment', string='Learner Matrix', help='Upload Document')
	learner_endorsement_and_certified_id_copies_doc = fields.Many2one('ir.attachment', string='Learner Endorsement Forms & Certified ID copies (attached)', help='Upload Document')
	assessor_documents = fields.Many2one('ir.attachment', string='Assessor Documents (SLA/Contract, Notification of Registration Letter, Assessor Report)', help='Upload Document')
	moderator_documents = fields.Many2one('ir.attachment', string='Moderator Documents (SLA/Contract, Notification of Registration Letter, Moderator Report)', help='Upload Document')
	accreditation_and_programme_approval_doc = fields.Many2one('ir.attachment', string='Accreditation & Programme Approval Documents', help='Upload Document')
	satelite_doc = fields.Many2one('ir.attachment', string='Satellite Documents (Where Applicable)', help='Upload Document')
	endorsement_letter_doc = fields.Many2one('ir.attachment', string='Endorsement Letter (for previous verification, where applicable)', help='Upload Document')
	batch_id = fields.Many2one('batch.master',string = 'Batch',required = True)
	other_docs_ids = fields.One2many('acc.multi.doc.upload', 'pro_assessement_id', string='Other Documents', track_visibility='onchange')
	qual_skill_assessment = fields.Selection([('qual', 'Qualifications'),
							   ('skill', 'Skills Programme'),
							   ('lp', 'Learning Programme'),],
							  string="Assessment Type")
	is_qdm_provider = fields.Boolean('QDM Provider')
	# Skills Fields
	learner_ids_for_skills = fields.One2many('learner.assessment.line.for.skills', 'provider_assessment_ref_id_for_skills', string='Learners for Skills', track_visibility='onchange')
	learner_achieve_ids_for_skills = fields.One2many('learner.assessment.achieve.line.for.skills', 'provider_assessment_achieve_ref_id_for_skills', string='Learners Achieve for Skills', track_visibility='onchange')
	learner_verify_ids_for_skills = fields.One2many('learner.assessment.verify.line.for.skills', 'provider_assessment_verify_ref_id_for_skills', string='learner verify ids for Skills', track_visibility='onchange')
	learner_evaluate_ids_for_skills = fields.One2many('learner.assessment.evaluate.line.for.skills', 'provider_assessment_evaluate_ref_id_for_skills', string='Learners evaluate for Skills', track_visibility='onchange')
	learner_achieved_ids_for_skills = fields.One2many('learner.assessment.achieved.line.for.skills', 'provider_assessment_achieved_ref_id_for_skills', string='Learners achieved for Skills', track_visibility='onchange')
	# Learning Programme Fields
	learner_ids_for_lp = fields.One2many('learner.assessment.line.for.lp', 'provider_assessment_ref_id_for_lp', string='Learners for Learning Programme', track_visibility='onchange')
	learner_achieve_ids_for_lp = fields.One2many('learner.assessment.achieve.line.for.lp', 'provider_assessment_achieve_ref_id_for_lp', string='Learners Achieve for Learning Programme', track_visibility='onchange')
	learner_verify_ids_for_lp = fields.One2many('learner.assessment.verify.line.for.lp', 'provider_assessment_verify_ref_id_for_lp', string='learner verify ids for Learning Programme', track_visibility='onchange')
	learner_evaluate_ids_for_lp = fields.One2many('learner.assessment.evaluate.line.for.lp', 'provider_assessment_evaluate_ref_id_for_lp', string='Learners evaluate for Learning Programme', track_visibility='onchange')
	learner_achieved_ids_for_lp = fields.One2many('learner.assessment.achieved.line.for.lp', 'provider_assessment_achieved_ref_id_for_lp', string='Learners achieved for Learning Programme', track_visibility='onchange')

	select_all = fields.Boolean("Select All", default= False)
	total_learner_count = fields.Integer('Total Learners Count', compute='_get_total_learner_count')
	achieved_learner_count = fields.Integer('Achieved Learners', compute='_get_achieved_learner_count')
	partially_achieved_learner_count = fields.Integer('Partially Achieved Learners', compute='_get_partially_achieved_learner_count')
	is_provider = fields.Boolean("Is Provider", compute='_get_login_user', store = False)
	unit_standard_variance = fields.Text("Unit Standard Variance")
	unit_standard_library_variance = fields.Text("Unit Standard Variance")

	# @api.one
	# def check_unit_standard_library(self):
	# 	dbg("check_unit_standard_library")
	# 	this_us_list = []
	# 	text_guy = ""
	# 	list_of_dict = []
	# 	this_mod_us_list = []
	# 	this_prov_us_list = []
	# 	this_ass_us_list = []
	# 	for x in self.env['provider.qualification'].search([]):
	# 		dbg(x.saqa_qual_id)
	# 		dbg(str(x.name) + str(x.saqa_qual_id) + str([z.id_no for z in x.qualification_line]))
	# 		list_of_dict.append({'name':x.name,
	# 							'code':x.saqa_qual_id,
	# 							'list_of_us':[z.id_no for z in x.qualification_line]
	# 							})
	# 	lib_us_list = [x.id_no for x in self.env['provider.qualification.line'].search([])]
	# 	if self.learner_achieved_ids:
	# 		for prov_quals in self.provider_id.qualification_ids:
	# 			for prov_us in prov_quals.qualification_line:
	# 				if prov_us.id_data not in this_prov_us_list and prov_us.selection:
	# 					dbg(prov_us.id_data)
	# 					# this_prov_us_list.append([x.id_data for x in prov_us])
	# 					this_prov_us_list.append(prov_us.id_data)
	# 		for achieved_ids in self.learner_achieved_ids:
	# 			for us in achieved_ids.unit_standards_learner_assessment_achieved_line_id:
	# 				if us.id_no not in this_us_list:
	# 					this_us_list.append(us.id_no)
	# 		lib_diff = [x for x in this_us_list if x not in lib_us_list]
	# 		for achieved_ids in self.learner_achieved_ids:
	# 			for us in achieved_ids.unit_standards_learner_assessment_achieved_line_id:
	# 				if us.id_no not in this_us_list:
	# 					this_us_list.append(us.id_no)
	# 			if achieved_ids.moderators_id:
	# 				for mod_qualifications in achieved_ids.moderators_id.moderator_qualification_ids:
	# 					for mod_us in mod_qualifications.qualification_line_hr:
	# 						if mod_us.id_no not in this_mod_us_list:
	# 							this_mod_us_list.append(mod_us.id_no)
	# 			if achieved_ids.assessors_id:
	# 				for ass_qualifications in achieved_ids.assessors_id.qualification_ids:
	# 					for ass_us in ass_qualifications.qualification_line_hr:
	# 						if ass_us.id_no not in this_ass_us_list:
	# 							this_ass_us_list.append(ass_us.id_no)
	# 		for libz in list_of_dict:
	# 			text_guy += "<div>-----------Qualification:" + str(libz.get('code')) + "-name:" + str(libz.get('name')) + "</div>"
	# 			for us in libz.get('list_of_us'):
	# 				string_thing = "<div>Qualification:" + str(libz.get('code')) + "--Code:" + str(us)
	# 				if us not in this_mod_us_list:
	# 					string_thing += "-Moderator:" + str(us)
	# 				if us not in this_ass_us_list:
	# 					string_thing += "-Assessor:" + str(us)
	# 				if us not in this_prov_us_list:
	# 					string_thing += "-Provider:" + str(us)
	# 				text_guy += string_thing + "</div>"
	#
	# 		# text_guy += "<h1>Library:</h1>"
	# 		# text_guy += "<h3>In assessment, not in Library:</h3>"
	# 		# for x in lib_diff:
	# 		# 	text_guy += "<div>" + str(x) + "</div>"
	# 	self.unit_standard_library_variance = text_guy

	@api.one
	def check_unit_standard_library(self):
		dbg("check_unit_standard_library")
		this_us_id_list = []
		this_mod_us_id_list = []
		this_prov_us_id_list = []
		this_ass_us_id_list = []
		list_of_dict = []
		quals_list = []
		lib_quals = []
		big_dic = {}
		text_guy = ""
		moderator_name = ""
		assessor_name = ""
		provider_name = self.provider_id.name
		for x in self.env['provider.qualification'].search([]):
			lib_quals.append(x.saqa_qual_id)
		lib_us_list = [x.id_no for x in self.env['provider.qualification.line'].search([])]
		lib_us_id_list = [x for x in self.env['provider.qualification.line'].search([])]
		if self.learner_achieved_ids:
			for prov_quals in self.provider_id.qualification_ids:
				for prov_us in prov_quals.qualification_line:
					if prov_us not in this_prov_us_id_list and prov_us.selection:
						# this_prov_us_list.append([x.id_data for x in prov_us])
						this_prov_us_id_list.append(prov_us)
			for achieved_ids in self.learner_achieved_ids:
				# build qualifications list from assessment
				for qualz in achieved_ids.qual_learner_assessment_achieved_line_id:
					if qualz.saqa_qual_id not in quals_list:
						quals_list.append(qualz.saqa_qual_id)
				# build assessment US list
				for us in achieved_ids.unit_standards_learner_assessment_achieved_line_id:
					# build list of US db ids to compare US in specific qualification
					if us not in this_us_id_list:
						this_us_id_list.append(us)
				if achieved_ids.moderators_id:
					moderator_name = achieved_ids.moderators_id.name
					# build moderator US list
					for mod_qualifications in achieved_ids.moderators_id.moderator_qualification_ids:
						for mod_us in mod_qualifications.qualification_line_hr:
							if mod_us not in this_mod_us_id_list:
								this_mod_us_id_list.append(mod_us)
				if achieved_ids.assessors_id:
					assessor_name = achieved_ids.assessors_id.name
					for ass_qualifications in achieved_ids.assessors_id.qualification_ids:
						for ass_us in ass_qualifications.qualification_line_hr:
							if ass_us not in this_ass_us_id_list:
								this_ass_us_id_list.append(ass_us)
			rows = ''
			style = '<style>#lib_units table, #lib_units th, #lib_units td {border: 1px solid black;text-align: center;}</style>'
			start_table = '<table id="lib_units">'
			header = '<tr><th>Assessment</th><th>library</th><th>provider</th><th>moderator</th><th>assessor</th></tr>'
			header2 = '<tr><th>Assessment</th><th>library</th><th>' + provider_name + '</th><th>' + moderator_name + '</th><th>' + assessor_name + '</th></tr>'
			for x in this_us_id_list:
				dbg(x)
				if x in this_prov_us_id_list:
					prov_x = 'x'
				else:
					prov_x = x.id_no
				if x in this_ass_us_id_list:
					ass_x = 'x'
				else:
					ass_x = x.id_no
				if x in this_mod_us_id_list:
					mod_x = 'x'
				else:
					mod_x = x.id_no
				if x in lib_us_id_list:
					lib_x = 'x'
				else:
					lib_x = x.id_no
				# dbg(prov_x)
				# dbg(mod_x)
				rows += '<tr><td>' + x.id_no + '</td><td>' + lib_x + '</td><td>' + prov_x + '</td><td>' + mod_x + '</td><td>' + ass_x + '</td></tr>'
				dbg('<tr><td>' + x.id_no + '</td><td>' + lib_x + '</td><td>' + prov_x + '</td><td>' + mod_x + '</td><td>' + ass_x + '</td></tr>')
			# dbg(rows)
			end_table = '</table>'
			whole_table = style + start_table + header + header2 + rows + end_table
			dbg(whole_table)
			self.unit_standard_library_variance = whole_table

	@api.one
	def check_unit_standard_upline(self):
		dbg("check_unit_standard_upline")
		# for this in self:
		this_us_list = []
		this_us_id_list = []
		this_mod_us_list = []
		this_mod_us_id_list = []
		this_prov_us_list = []
		this_ass_us_list = []
		list_of_dict = []
		quals_list = []
		lib_quals = []
		big_dic = {}
		text_guy = ""
		moderator_name = ""
		assessor_name = ""
		provider_name = self.provider_id.name
		for x in self.env['provider.qualification'].search([]):
			list_of_dict.append({'name':x.name,
								'code':x.saqa_qual_id,
								'list_of_us':[z.id_no for z in x.qualification_line]
								})
			lib_quals.append(x.saqa_qual_id)
		lib_us_list = [x.id_no for x in self.env['provider.qualification.line'].search([])]
		big_dic.update({'lib_quals':lib_quals,'lib_us':lib_us_list})
		if self.learner_achieved_ids:
			for prov_quals in self.provider_id.qualification_ids:
				for prov_us in prov_quals.qualification_line:
					if prov_us.id_data not in this_prov_us_list and prov_us.selection:
						# this_prov_us_list.append([x.id_data for x in prov_us])
						this_prov_us_list.append(prov_us.id_data)
			big_dic.update({'provider_unit_standards':this_prov_us_list,'provider_name':provider_name})
			for achieved_ids in self.learner_achieved_ids:
				# build qualifications list from assessment
				for qualz in achieved_ids.qual_learner_assessment_achieved_line_id:
					if qualz.saqa_qual_id not in quals_list:
						quals_list.append(qualz.saqa_qual_id)
				# build assessment US list
				for us in achieved_ids.unit_standards_learner_assessment_achieved_line_id:
					# build list of US db ids to compare US in specific qualification
					if us not in this_us_id_list:
						this_us_id_list.append(us)
					if us.id_no not in this_us_list:
						this_us_list.append(us.id_no)
				if achieved_ids.moderators_id:
					moderator_name = achieved_ids.moderators_id.name
					# build moderator US list
					for mod_qualifications in achieved_ids.moderators_id.moderator_qualification_ids:
						for mod_us in mod_qualifications.qualification_line_hr:
							if mod_us not in this_mod_us_id_list:
								this_mod_us_id_list.append(mod_us)
							if mod_us.id_no not in this_mod_us_list:
								this_mod_us_list.append(mod_us.id_no)
				if achieved_ids.assessors_id:
					assessor_name = achieved_ids.assessors_id.name
					for ass_qualifications in achieved_ids.assessors_id.qualification_ids:
						for ass_us in ass_qualifications.qualification_line_hr:
							if ass_us.id_no not in this_ass_us_list:
								this_ass_us_list.append(ass_us.id_no)
			big_dic.update({'assessment_quals': quals_list,
			                'assessment_unit_standards':this_us_list,
			                'moderator_unit_standards':this_mod_us_list,
			                'assessor_unit_standards':this_ass_us_list,
			                'assessor_name':assessor_name,
			                'moderator_name':moderator_name,
			                })
			mod_diff = [x for x in this_us_list if x not in this_mod_us_list]
			ass_diff = [x for x in this_us_list if x not in this_ass_us_list]
			prov_diff = [x for x in this_us_list if x not in this_prov_us_list]
			rows = ''
			style = '<style>#lib_units table, #lib_units th, #lib_units td {border: 1px solid black;text-align: center;}</style>'
			start_table = '<table id="lib_units">'
			header = '<tr><th>Assessment</th><th>library</th><th>provider</th><th>moderator</th><th>assessor</th></tr>'
			for x in this_us_list:
				if x in this_prov_us_list: prov_x = 'x'
				else:prov_x = x
				if x in this_ass_us_list: ass_x = 'x'
				else: ass_x = x
				if x in this_mod_us_list: mod_x = 'x'
				else: mod_x = x
				if x in lib_us_list: lib_x = 'x'
				else: lib_x = x
				# dbg(prov_x)
				# dbg(mod_x)
				rows += '<tr><td>' + x + '</td><td>' + lib_x + '</td><td>' + prov_x + '</td><td>' + mod_x + '</td><td>' + ass_x + '</td></tr>'
				# dbg(rows)
			end_table = '</table>'
			whole_table = style + start_table + header + rows + end_table
			dbg(whole_table)
			self.unit_standard_library_variance = whole_table
			text_guy += "<h1>Provider:" + provider_name + "</h1>"
			text_guy += "<h3>In assessment, not in Provider:</h3>"
			for x in prov_diff:
				text_guy += "<div>" + str(x) + "</div>"
			text_guy += "<h1>Moderator:" + moderator_name + "</h1>"
			text_guy += "<h3>In assessment, not in Moderator:</h3>"
			for x in mod_diff:
				text_guy += "<div>" + str(x) + "</div>"
			text_guy += "<h1>Assessor:" + assessor_name + "</h1>"
			text_guy += "<h3>In assessment, not in Assessor:</h3>"
			for x in ass_diff:
				text_guy += "<div>" + str(x) + "</div>"
			self.unit_standard_variance = text_guy

	@api.onchange('select_all')
	def onchange_select_all(self):
		if not self.qual_skill_assessment and self.select_all:
			self.select_all = False
			return {'warning':{'title':'Warning','message':'Please select Assessment Type first!'}}
		#QUALS
		elif self.qual_skill_assessment == 'qual' and self.select_all:
			if self.state == 'submitted'  and self.learner_verify_ids:
				for q_line in self.learner_verify_ids:
					q_line.verify = True
			elif self.state == 'verify' and self.learner_evaluate_ids:
				for q_line in self.learner_evaluate_ids:
					q_line.evaluate = True
			elif self.state == 'evaluate' and self.learner_achieve_ids:
				for q_line in self.learner_achieve_ids:
					q_line.achieve = True
		elif self.qual_skill_assessment == 'qual' and not self.select_all:
			if self.state == 'submitted' and self.learner_verify_ids:
				for q_line in self.learner_verify_ids:
					q_line.verify = False
			elif self.state == 'verify' and self.learner_evaluate_ids:
				for q_line in self.learner_evaluate_ids:
					q_line.evaluate = False
			elif self.state == 'evaluate' and self.learner_achieve_ids:
				for q_line in self.learner_achieve_ids:
					q_line.achieve = False
		#SKILLS
		elif self.qual_skill_assessment == 'skill' and self.select_all:
			if self.state == 'submitted' and self.learner_verify_ids_for_skills:
				for s_line in self.learner_verify_ids_for_skills:
					s_line.verify = True
			elif self.state == 'verify' and self.learner_evaluate_ids_for_skills:
				for s_line in self.learner_evaluate_ids_for_skills:
					s_line.evaluate = True
			elif self.state == 'evaluate' and self.learner_achieve_ids_for_skills:
				for s_line in self.learner_achieve_ids_for_skills:
					s_line.achieve = True
		elif self.qual_skill_assessment == 'skill' and not self.select_all:
			if self.state == 'submitted' and self.learner_verify_ids_for_skills:
				for s_line in self.learner_verify_ids_for_skills:
					s_line.verify = False
			elif self.state == 'verify' and self.learner_evaluate_ids_for_skills:
				for s_line in self.learner_evaluate_ids_for_skills:
					s_line.evaluate = False
			elif self.state == 'evaluate' and self.learner_achieve_ids_for_skills:
				for s_line in self.learner_achieve_ids_for_skills:
					s_line.achieve = False
		#Learning Programme
		elif self.qual_skill_assessment == 'lp' and self.select_all:
			if self.state == 'submitted' and self.learner_verify_ids_for_lp:
				for s_line in self.learner_verify_ids_for_lp:
					s_line.verify = True
			elif self.state == 'verify' and self.learner_evaluate_ids_for_lp:
				for s_line in self.learner_evaluate_ids_for_lp:
					s_line.evaluate = True
			elif self.state == 'evaluate' and self.learner_achieve_ids_for_lp:
				for s_line in self.learner_achieve_ids_for_lp:
					s_line.achieve = True
		elif self.qual_skill_assessment == 'lp' and not self.select_all:
			if self.state == 'submitted' and self.learner_verify_ids_for_lp:
				for s_line in self.learner_verify_ids_for_lp:
					s_line.verify = False
			elif self.state == 'verify' and self.learner_evaluate_ids_for_lp:
				for s_line in self.learner_evaluate_ids_for_lp:
					s_line.evaluate = False
			elif self.state == 'evaluate' and self.learner_achieve_ids_for_lp:
				for s_line in self.learner_achieve_ids_for_lp:
					s_line.achieve = False

	@api.multi
	def action_fetch_learners_button(self):
		''' This method is used to fetch approved learners from learner master to provider assessment based on assessment type and selected batch '''
		learners_list = []
		assessment_line_list = []
		if self.batch_id and self.qual_skill_assessment == 'qual':
			for record in self.learner_ids:
				learners_list.append(record.learner_id.id)
			learner_obj = self.env['hr.employee'].search([('logged_provider_id', '=', self.env.user.partner_id.id)])
			new_learner_list = [learner.id for learner in learner_obj]
			if learner_obj:
				for learner in learner_obj:
					if learner.id not in learners_list:
						for learner_qual in learner.learner_qualification_ids:
							if learner_qual.batch_id.id == self.batch_id.id and learner_qual.is_learner_achieved == False and learner_qual.provider_id.id == self.env.user.partner_id.id:
								qual_list, unit_line_list = [], []
								qual_list.append(learner_qual.learner_qualification_parent_id.id)
								learners_assessor_id = learner_qual.assessors_id.id
								learners_moderator_id = learner_qual.moderators_id.id
								for unit_line in learner_qual.learner_registration_line_ids:
									if unit_line.achieve == False and unit_line.selection:
										# print "unit_line.id_data====", unit_line.id_data
										# print "unit_line.Title====", unit_line.title
										pro_qual_id = self.env['provider.qualification.line'].search(['|',('id_no', '=', 'unit_line.id_data'),('title', '=', unit_line.title),('line_id','=',learner_qual.learner_qualification_parent_id.id)]).id
										print "pro_qual_id==", pro_qual_id
										if pro_qual_id:
											unit_line_list.append(pro_qual_id)
										# print "Unit line list:==========", unit_line_list
								if qual_list and unit_line_list:
									if learner.citizen_resident_status_code in ['dual','PR', 'sa']:
										assessment_line_list.append((0, 0, {'identification_id':learner.learner_identification_id or '', 'learner_id':learner.id, 'qual_learner_assessment_line_id': [[6, 0, list(set(qual_list))]], 'unit_standards_learner_assessment_line_id':[[6, 0, list(set(unit_line_list))]], 'assessors_id':learners_assessor_id, 'moderators_id':learners_moderator_id}))
									elif learner.citizen_resident_status_code in ['other','unknown']:
										assessment_line_list.append((0, 0, {'identification_id':learner.national_id or '', 'learner_id':learner.id, 'qual_learner_assessment_line_id': [[6, 0, list(set(qual_list))]], 'unit_standards_learner_assessment_line_id':[[6, 0, list(set(unit_line_list))]], 'assessors_id':learners_assessor_id, 'moderators_id':learners_moderator_id}))
			self.write({'learner_ids':assessment_line_list})
			return True
		elif self.batch_id and self.qual_skill_assessment == 'skill':
			for record in self.learner_ids_for_skills:
				learners_list.append(record.learner_id.id)
			learner_obj = self.env['hr.employee'].search([('logged_provider_id_for_skills', '=', self.env.user.partner_id.id)])
			new_learner_list = [learner.id for learner in learner_obj]
			if learner_obj:
				for learner in learner_obj:
					if learner.id not in learners_list:
						for learner_skill in learner.skills_programme_ids:
							if learner_skill.batch_id.id == self.batch_id.id and  learner_skill.is_learner_achieved == False and learner_skill.provider_id.id == self.env.user.partner_id.id:
								skill_list, unit_line_list = [], []
								skill_list.append(learner_skill.skills_programme_id.id)
								learners_assessor_id = learner_skill.assessors_id.id
								learners_moderator_id = learner_skill.moderators_id.id
								for unit_line in learner_skill.unit_standards_line:
									if unit_line.achieve == False and unit_line.selection:
										pro_skill_id = self.env['skills.programme.unit.standards'].search([('title', '=', unit_line.title),('skills_programme_id','=',learner_skill.skills_programme_id.id)]).id
										if pro_skill_id:
											unit_line_list.append(pro_skill_id)
								if skill_list and unit_line_list:
									if learner.citizen_resident_status_code in ['dual','PR', 'sa']:
										assessment_line_list.append((0, 0, {'identification_id':learner.learner_identification_id or '', 'learner_id':learner.id, 'skill_learner_assessment_line_id': [[6, 0, list(set(skill_list))]], 'skill_unit_standards_learner_assessment_line_id':[[6, 0, list(set(unit_line_list))]], 'assessors_id':learners_assessor_id, 'moderators_id':learners_moderator_id}))
									elif learner.citizen_resident_status_code in ['other','unknown']:
										assessment_line_list.append((0, 0, {'identification_id':learner.national_id or '', 'learner_id':learner.id, 'skill_learner_assessment_line_id': [[6, 0, list(set(skill_list))]], 'skill_unit_standards_learner_assessment_line_id':[[6, 0, list(set(unit_line_list))]], 'assessors_id':learners_assessor_id, 'moderators_id':learners_moderator_id}))

			self.write({'learner_ids_for_skills':assessment_line_list})
			return True
		elif self.batch_id and self.qual_skill_assessment == 'lp':
			for record in self.learner_ids_for_lp:
				learners_list.append(record.learner_id.id)
			learner_obj = self.env['hr.employee'].search([('logged_provider_id_for_lp', '=', self.env.user.partner_id.id)])
			new_learner_list = [learner.id for learner in learner_obj]
			if learner_obj:
				for learner in learner_obj:
					if learner.id not in learners_list:
						for learner_lp in learner.learning_programme_ids:
							if learner_lp.batch_id.id == self.batch_id.id and learner_lp.is_learner_achieved == False and learner_lp.provider_id.id == self.env.user.partner_id.id:
								lp_list, unit_line_list = [], []
								lp_list.append(learner_lp.learning_programme_id.id)
								learners_assessor_id = learner_lp.assessors_id.id
								learners_moderator_id = learner_lp.moderators_id.id
								for unit_line in learner_lp.unit_standards_line:
									if unit_line.achieve == False and unit_line.selection:
										pro_lp_id = self.env['etqe.learning.programme.unit.standards'].search([('title', '=', unit_line.title),('learning_programme_id','=',learner_lp.learning_programme_id.id)]).id
										if pro_lp_id:
											unit_line_list.append(pro_lp_id)
								if lp_list and unit_line_list:
									if learner.citizen_resident_status_code in ['dual','PR', 'sa']:
										assessment_line_list.append((0, 0, {'identification_id':learner.learner_identification_id or '', 'learner_id':learner.id, 'lp_learner_assessment_line_id': [[6, 0, list(set(lp_list))]], 'lp_unit_standards_learner_assessment_line_id':[[6, 0, list(set(unit_line_list))]], 'assessors_id':learners_assessor_id, 'moderators_id':learners_moderator_id}))
									elif learner.citizen_resident_status_code in ['other','unknown']:
										assessment_line_list.append((0, 0, {'identification_id':learner.national_id or '', 'learner_id':learner.id, 'lp_learner_assessment_line_id': [[6, 0, list(set(lp_list))]], 'lp_unit_standards_learner_assessment_line_id':[[6, 0, list(set(unit_line_list))]], 'assessors_id':learners_assessor_id, 'moderators_id':learners_moderator_id}))
			self.write({'learner_ids_for_lp':assessment_line_list})
			return True

	@api.multi
	def action_submit_button(self):
		context = self._context
		if context is None:
			context = {}
		self = self.with_context(submited=True)
		if self.qual_skill_assessment == 'qual':
			for learner in self.learner_ids:
				if learner.assessors_id.id is False:
					raise Warning(_("Please select Assessor before submit"))
				elif learner.moderators_id.id is False:
					raise Warning(_("Please select Moderator before submit"))
			learner_submitted = []
			learner_dict = {}
			if not self.learner_verify_ids:
				for learner_data in self.learner_ids:
					qual_ids = []
					unit_ids = []
					for qual in learner_data.qual_learner_assessment_line_id:
						qual_ids.append(qual.id)
					for unit in learner_data.unit_standards_learner_assessment_line_id:
						unit_ids.append(unit.id)
					learner_dict = {
									'learner_id':learner_data.learner_id and learner_data.learner_id.id,
									'learner_identity_number' : learner_data.learner_identity_number,
									'identification_id' : learner_data.identification_id,
									'qual_learner_assessment_verify_line_id': [(6, 0, qual_ids)],
									'unit_standards_learner_assessment_verify_line_id': [(6, 0, unit_ids)],
									'assessors_id':learner_data.assessors_id and learner_data.assessors_id.id,
									'moderators_id':learner_data.moderators_id and learner_data.moderators_id.id,
									'timetable_id':learner_data.timetable_id and learner_data.timetable_id.id,
									}
					learner_submitted.append((0, 0, learner_dict))
			assessment_status_obj = self.env['assessment.status'].create({'name': self._uid,
																		  'state':'submitted',
																		  'pro_id':self.id,
																		  'comment':self.comment,
																		  'state_title':'Submitted'
																		  })
			ir_model_data_obj = self.env['ir.model.data']
			mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_provider_assessment_submit')
			if mail_template_id:
				self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
			if self.learner_ids:
				self.write({'state':'submitted', 'submited':True, 'learner_verify_ids':learner_submitted,'select_all':False})
			else:
				raise Warning(_("Please add learner record first!!"))
			return True
		elif self.qual_skill_assessment == 'skill':
			for learner in self.learner_ids_for_skills:
				if learner.assessors_id.id is False:
					raise Warning(_("Please select Assessor before submit"))
				elif learner.moderators_id.id is False:
					raise Warning(_("Please select Moderator before submit"))
			learner_submitted = []
			learner_dict = {}
			if not self.learner_verify_ids_for_skills:
				for learner_data in self.learner_ids_for_skills:
					skill_ids = []
					unit_ids = []
					for skill in learner_data.skill_learner_assessment_line_id:
						skill_ids.append(skill.id)
					for unit in learner_data.skill_unit_standards_learner_assessment_line_id:
						unit_ids.append(unit.id)
					learner_dict = {
							'learner_id':learner_data.learner_id and learner_data.learner_id.id,
							'learner_identity_number' : learner_data.learner_identity_number,
							'identification_id' : learner_data.identification_id,
							'skill_learner_assessment_verify_line_id': [(6, 0, skill_ids)],
							'skill_unit_standards_learner_assessment_verify_line_id': [(6, 0, unit_ids)],
							 'assessors_id':learner_data.assessors_id and learner_data.assessors_id.id,
							 'moderators_id':learner_data.moderators_id and learner_data.moderators_id.id,
							 'timetable_id':learner_data.timetable_id and learner_data.timetable_id.id,
							}
					learner_submitted.append((0, 0, learner_dict))
			assessment_status_obj = self.env['assessment.status'].create({'name': self._uid,
																		  'state':'submitted',
																		  'pro_id':self.id,
																		  'comment':self.comment,
																		  'state_title':'Submitted'
																		  })
			ir_model_data_obj = self.env['ir.model.data']
			mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_provider_assessment_submit')
			if mail_template_id:
				self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
			if self.learner_ids_for_skills:
				self.write({'state':'submitted', 'submited':True, 'learner_verify_ids_for_skills':learner_submitted,'select_all':False})
			else:
				raise Warning(_("Please add learner record first!!"))
			return True
		# Changes Added by Ganesh For Learning Programme
		elif self.qual_skill_assessment == 'lp':
			for learner in self.learner_ids_for_lp:
				if learner.assessors_id.id is False:
					raise Warning(_("Please select Assessor before submit"))
				elif learner.moderators_id.id is False:
					raise Warning(_("Please select Moderator before submit"))
			learner_submitted = []
			learner_dict = {}
			if not self.learner_verify_ids_for_lp:
				for learner_data in self.learner_ids_for_lp:
					lp_ids = []
					unit_ids = []
					for lp in learner_data.lp_learner_assessment_line_id:
						lp_ids.append(lp.id)
					for unit in learner_data.lp_unit_standards_learner_assessment_line_id:
						unit_ids.append(unit.id)
					learner_dict = {
							'learner_id':learner_data.learner_id and learner_data.learner_id.id,
							'learner_identity_number' : learner_data.learner_identity_number,
							'identification_id' : learner_data.identification_id,
							'lp_learner_assessment_verify_line_id': [(6, 0, lp_ids)],
							'lp_unit_standards_learner_assessment_verify_line_id': [(6, 0, unit_ids)],
							 'assessors_id':learner_data.assessors_id and learner_data.assessors_id.id,
							 'moderators_id':learner_data.moderators_id and learner_data.moderators_id.id,
							 'timetable_id':learner_data.timetable_id and learner_data.timetable_id.id,
							}
					learner_submitted.append((0, 0, learner_dict))
			assessment_status_obj = self.env['assessment.status'].create({'name': self._uid,
																		  'state':'submitted',
																		  'pro_id':self.id,
																		  'comment':self.comment,
																		  'state_title':'Submitted'
																		  })
			ir_model_data_obj = self.env['ir.model.data']
			mail_template_id = ir_model_data_obj.get_object_reference('hwseta_etqe', 'email_template_provider_assessment_submit')
			if mail_template_id:
				self.pool['email.template'].send_mail(self.env.cr, self.env.uid, mail_template_id[1], self.id, force_send=True, context=self.env.context)
			if self.learner_ids_for_lp:
				self.write({'state':'submitted', 'submited':True, 'learner_verify_ids_for_lp':learner_submitted,'select_all':False})
			else:
				raise Warning(_("Please add learner record first!!"))

			return True

	@api.multi
	def action_set_to_draft(self):
		assessment_status_obj = self.env['assessment.status'].create({'name': self._uid,
															  'state':'draft',
															  'pro_id':self.id,
															  'comment':self.comment,
															  'state_title':'Not Recommended'
															  })
		self.write({'state':'draft', 'submited':False, 'verified':False})
		return True

	@api.multi
	def action_verify_button(self):
		context = self._context
		if context is None:
			context = {}
		self = self.with_context(verified=True)
		if self.qual_skill_assessment == 'qual':
			learner_verified = []
			if not self.learner_evaluate_ids:
				for learner_data in self.learner_verify_ids:
					if learner_data.verify:
						qual_ids = []
						skill_ids = []
						unit_ids = []
						for qual in learner_data.qual_learner_assessment_verify_line_id:
							qual_ids.append(qual.id)
						for unit in learner_data.unit_standards_learner_assessment_verify_line_id:
							unit_ids.append(unit.id)
						learner_dict = {
								'learner_id':learner_data.learner_id and learner_data.learner_id.id,
								'learner_identity_number' : learner_data.learner_identity_number,
								'identification_id' : learner_data.identification_id,
								'qual_learner_assessment_evaluate_line_id': [(6, 0, qual_ids)],
								'unit_standards_learner_assessment_evaluate_line_id': [(6, 0, unit_ids)],
								 'assessors_id':learner_data.assessors_id and learner_data.assessors_id.id,
								 'moderators_id':learner_data.moderators_id and learner_data.moderators_id.id,
								 'timetable_id':learner_data.timetable_id and learner_data.timetable_id.id,
								}
						learner_verified.append((0, 0, learner_dict))
			assessment_status_obj = self.env['assessment.status'].create({'name': self._uid,
																  'state':'verify',
																  'pro_id':self.id,
																  'comment':self.comment,
																  'state_title':'Recommended'
																  })
			self.write({'state':'verify', 'verified':True, 'learner_evaluate_ids':learner_verified,'select_all':False})
			# code to check whether any1 learner verify field checked or not by pradip 5/10/2016
			verify_false = 0
			learner_line = 0
			for learner in self.learner_verify_ids:
				if learner.verify == False:
					verify_false += 1
				learner_line += 1
			if verify_false == learner_line:
				raise Warning(_("You haven't verified any learner! Please verify atleast one learner to continue.."))
			return True
		elif self.qual_skill_assessment == 'skill':
			learner_verified = []
			if not self.learner_evaluate_ids_for_skills:
				for learner_data in self.learner_verify_ids_for_skills:
					if learner_data.verify:
						skill_ids = []
						unit_ids = []
						for skill in learner_data.skill_learner_assessment_verify_line_id:
							skill_ids.append(skill.id)
						for unit in learner_data.skill_unit_standards_learner_assessment_verify_line_id:
							unit_ids.append(unit.id)
						learner_dict = {
								'learner_id':learner_data.learner_id and learner_data.learner_id.id,
								'learner_identity_number' : learner_data.learner_identity_number,
								'identification_id' : learner_data.identification_id,
								'skill_learner_assessment_evaluate_line_id': [(6, 0, skill_ids)],
								'skill_unit_standards_learner_assessment_evaluate_line_id': [(6, 0, unit_ids)],
								 'assessors_id':learner_data.assessors_id and learner_data.assessors_id.id,
								 'moderators_id':learner_data.moderators_id and learner_data.moderators_id.id,
								 'timetable_id':learner_data.timetable_id and learner_data.timetable_id.id,
								}
						learner_verified.append((0, 0, learner_dict))
			assessment_status_obj = self.env['assessment.status'].create({'name': self._uid,
																  'state':'verify',
																  'pro_id':self.id,
																  'comment':self.comment,
																  'state_title':'Recommended'
																  })
			self.write({'state':'verify', 'verified':True, 'learner_evaluate_ids_for_skills':learner_verified,'select_all':False})
			# code to check whether any1 learner verify field checked or not by pradip 5/10/2016
			verify_false = 0
			learner_line = 0
			for learner in self.learner_verify_ids_for_skills:
				if learner.verify == False:
					verify_false += 1
				learner_line += 1
			if verify_false == learner_line:
				raise Warning(_("You haven't verified any learner! Please verify atleast one learner to continue.."))
			return True
		# Changes Added by Ganesh For Learning Programme
		elif self.qual_skill_assessment == 'lp':
			learner_verified = []
			if not self.learner_evaluate_ids_for_lp:
				for learner_data in self.learner_verify_ids_for_lp:
					if learner_data.verify:
						lp_ids = []
						unit_ids = []
						for lp in learner_data.lp_learner_assessment_verify_line_id:
							lp_ids.append(lp.id)
						for unit in learner_data.lp_unit_standards_learner_assessment_verify_line_id:
							unit_ids.append(unit.id)
						learner_dict = {
								'learner_id':learner_data.learner_id and learner_data.learner_id.id,
								'learner_identity_number' : learner_data.learner_identity_number,
								'identification_id' : learner_data.identification_id,
								'lp_learner_assessment_evaluate_line_id': [(6, 0, lp_ids)],
								'lp_unit_standards_learner_assessment_evaluate_line_id': [(6, 0, unit_ids)],
								 'assessors_id':learner_data.assessors_id and learner_data.assessors_id.id,
								 'moderators_id':learner_data.moderators_id and learner_data.moderators_id.id,
								 'timetable_id':learner_data.timetable_id and learner_data.timetable_id.id,
								}
						learner_verified.append((0, 0, learner_dict))
			assessment_status_obj = self.env['assessment.status'].create({'name': self._uid,
																  'state':'verify',
																  'pro_id':self.id,
																  'comment':self.comment,
																  'state_title':'Recommended'
																  })
			self.write({'state':'verify', 'verified':True, 'learner_evaluate_ids_for_lp':learner_verified,'select_all':False})
			verify_false = 0
			learner_line = 0
			for learner in self.learner_verify_ids_for_lp:
				if learner.verify == False:
					verify_false += 1
				learner_line += 1
			if verify_false == learner_line:
				raise Warning(_("You haven't verified any learner! Please verify atleast one learner to continue.."))
			return True

	@api.multi
	def action_set_to_submit(self):
		assessment_status_obj = self.env['assessment.status'].create({'name': self._uid,
															  'state':'submitted',
															  'pro_id':self.id,
															  'comment':self.comment,
															  'state_title':'Not Recommended'
															  })
		self.write({'state':'submitted', 'submited':True, 'verified':False,'select_all':False})
		return True


	@api.multi
	def action_evaluate_button(self):
		context = self._context
		if context is None:
			context = {}
		self = self.with_context(evaluated=True)
		learner_evaluate = []
		if self.qual_skill_assessment == 'qual':
			if not self.learner_achieve_ids:
				for learner_data in self.learner_evaluate_ids:
					if learner_data.evaluate:
						qual_ids = []
						unit_ids = []
						for qual in learner_data.qual_learner_assessment_evaluate_line_id:
							qual_ids.append(qual.id)
						for unit in learner_data.unit_standards_learner_assessment_evaluate_line_id:
							unit_ids.append(unit.id)
						learner_dict = {
								 'learner_id':learner_data.learner_id and learner_data.learner_id.id,
								 'learner_identity_number' : learner_data.learner_identity_number,
								 'identification_id' : learner_data.identification_id,
								 'qual_learner_assessment_achieve_line_id': [(6, 0, qual_ids)],
								 'unit_standards_learner_assessment_achieve_line_id': [(6, 0, unit_ids)],
								 'assessors_id':learner_data.assessors_id and learner_data.assessors_id.id,
								 'moderators_id':learner_data.moderators_id and learner_data.moderators_id.id,
								 'timetable_id':learner_data.timetable_id and learner_data.timetable_id.id,
								}
						learner_evaluate.append((0, 0, learner_dict))
			assessment_status_obj = self.env['assessment.status'].create({'name': self._uid,
																  'state':'evaluate',
																  'pro_id':self.id,
																  'comment':self.comment,
																  'state_title':'Recommended'
																  })
			self.write({'state':'evaluate', 'evaluated':True, 'learner_achieve_ids':learner_evaluate,'select_all':False})
			# code to check whether any1 learner evaluate field checked or not by pradip 5/10/2016
			evaluate_false = 0
			learner_line = 0
			for learner in self.learner_evaluate_ids:
				if learner.evaluate == False:
					evaluate_false += 1
				learner_line += 1
			if evaluate_false == learner_line:
				raise Warning(_("You haven't evaluated any learner! Please evaluate atleast one learner to continue.."))
			return True
		elif self.qual_skill_assessment == 'skill':
			learner_evaluate = []
			if not self.learner_achieve_ids_for_skills:
				for learner_data in self.learner_evaluate_ids_for_skills:
					if learner_data.evaluate:
						skill_ids = []
						unit_ids = []
						for skill in learner_data.skill_learner_assessment_evaluate_line_id:
							skill_ids.append(skill.id)
						for unit in learner_data.skill_unit_standards_learner_assessment_evaluate_line_id:
							unit_ids.append(unit.id)
						learner_dict = {
								 'learner_id':learner_data.learner_id and learner_data.learner_id.id,
								 'learner_identity_number' : learner_data.learner_identity_number,
								 'identification_id' : learner_data.identification_id,
								 'skill_learner_assessment_achieve_line_id': [(6, 0, skill_ids)],
								 'skill_unit_standards_learner_assessment_achieve_line_id': [(6, 0, unit_ids)],
								 'assessors_id':learner_data.assessors_id and learner_data.assessors_id.id,
								 'moderators_id':learner_data.moderators_id and learner_data.moderators_id.id,
								 'timetable_id':learner_data.timetable_id and learner_data.timetable_id.id,
								}
						learner_evaluate.append((0, 0, learner_dict))
			assessment_status_obj = self.env['assessment.status'].create({'name': self._uid,
																  'state':'evaluate',
																  'pro_id':self.id,
																  'comment':self.comment,
																  'state_title':'Recommended'
																  })
			self.write({'state':'evaluate', 'evaluated':True, 'learner_achieve_ids_for_skills':learner_evaluate,'select_all':False})
			# code to check whether any1 learner evaluate field checked or not by pradip 5/10/2016
			evaluate_false = 0
			learner_line = 0
			for learner in self.learner_evaluate_ids_for_skills:
				if learner.evaluate == False:
					evaluate_false += 1
				learner_line += 1
			if evaluate_false == learner_line:
				raise Warning(_("You haven't evaluated any learner! Please evaluate atleast one learner to continue.."))
			return True
		# Changes Added by Ganesh For Learning Programme
		elif self.qual_skill_assessment == 'lp':
			learner_evaluate = []
			if not self.learner_achieve_ids_for_lp:
				for learner_data in self.learner_evaluate_ids_for_lp:
					if learner_data.evaluate:
						lp_ids = []
						unit_ids = []
						for lp in learner_data.lp_learner_assessment_evaluate_line_id:
							lp_ids.append(lp.id)
						for unit in learner_data.lp_unit_standards_learner_assessment_evaluate_line_id:
							unit_ids.append(unit.id)
						learner_dict = {
								 'learner_id':learner_data.learner_id and learner_data.learner_id.id,
								 'learner_identity_number' : learner_data.learner_identity_number,
								 'identification_id' : learner_data.identification_id,
								 'lp_learner_assessment_achieve_line_id': [(6, 0, lp_ids)],
								 'lp_unit_standards_learner_assessment_achieve_line_id': [(6, 0, unit_ids)],
								 'assessors_id':learner_data.assessors_id and learner_data.assessors_id.id,
								 'moderators_id':learner_data.moderators_id and learner_data.moderators_id.id,
								 'timetable_id':learner_data.timetable_id and learner_data.timetable_id.id,
								}
						learner_evaluate.append((0, 0, learner_dict))
			assessment_status_obj = self.env['assessment.status'].create({'name': self._uid,
																  'state':'evaluate',
																  'pro_id':self.id,
																  'comment':self.comment,
																  'state_title':'Recommended'
																  })
			self.write({'state':'evaluate', 'evaluated':True, 'learner_achieve_ids_for_lp':learner_evaluate,'select_all':False})
			evaluate_false = 0
			learner_line = 0
			for learner in self.learner_evaluate_ids_for_lp:
				if learner.evaluate == False:
					evaluate_false += 1
				learner_line += 1
			if evaluate_false == learner_line:
				raise Warning(_("You haven't evaluated any learner! Please evaluate atleast one learner to continue.."))
			return True

	@api.multi
	def action_achieved_button(self):
		context = self._context
		if context is None:
			context = {}
		self = self.with_context(assessed=True)
		if self.qual_skill_assessment == 'qual':
			learner_achieved = []
			if not self.learner_achieved_ids:
				for learner_data in self.learner_achieve_ids:
					min_qual_creds = learner_data.qual_learner_assessment_achieve_line_id.m_credits
					min_creds_found = 0
					if learner_data.achieve:
						req_units_found = []
						for us_min in learner_data.unit_standards_learner_assessment_achieve_line_id:
							dbg(us_min.level3)
							min_creds_found += int(us_min.level3)
							dbg('unit--' + str(us_min) + 'type found' + str(us_min.type))
							if us_min.type in ['Core','Fundamental']:
								req_units_found.append(us_min.id_no)
						# raise Warning(
						# 	_('min_qual_creds:' + str(min_qual_creds) + '-min_creds_found:' + str(min_creds_found)))
						dbg('min_qual_creds:' + str(min_qual_creds) + '-min_creds_found:' + str(min_creds_found))
						qual_ids = []
						unit_ids = []
						for qual in learner_data.qual_learner_assessment_achieve_line_id:
							qual_ids.append(qual.id)
						for unit in learner_data.unit_standards_learner_assessment_achieve_line_id:
							unit_ids.append(unit.id)
						learner_dict = {
								 'learner_id':learner_data.learner_id and learner_data.learner_id.id,
								 'learner_identity_number' : learner_data.learner_identity_number,
								 'identification_id' : learner_data.identification_id,
								 'qual_learner_assessment_achieved_line_id': [(6, 0, qual_ids)],
								 'unit_standards_learner_assessment_achieved_line_id': [(6, 0, unit_ids)],
								 'assessors_id':learner_data.assessors_id and learner_data.assessors_id.id,
								 'moderators_id':learner_data.moderators_id and learner_data.moderators_id.id,
								 'timetable_id':learner_data.timetable_id and learner_data.timetable_id.id,
								}
						# This code is used to assign True value to achieve field of etqe learner qualification line
						qual_line_obj = self.env['hr.employee'].search([('id', '=', learner_dict['learner_id'])])
						for line in qual_line_obj.learner_qualification_ids:
							min_expected_creds = line.learner_qualification_parent_id.m_credits
							dbg(line)
							selected_line, achieved_line = 0, 0
							if line.learner_qualification_parent_id.id in qual_ids and line.provider_id.id == self.provider_id.id:
								dbg('match prov and quals for id:' + str(line))
								registration_min_creds = 0
								req_units = []
								for u_line in line.learner_registration_line_ids:
									dbg('units:' + str(u_line) + '-qual:' + str(line) + 'learner:' + str(qual_line_obj))
									if u_line.selection:
										dbg('reg unit expected' + str(u_line) + 'type---' + str(u_line.type))
										if u_line.type in ['Core', 'Fundamental']:
											req_units.append(u_line.id_data)
										selected_line += 1
										for assessment_unit in learner_data.unit_standards_learner_assessment_achieve_line_id:
											if u_line.title == assessment_unit.title:
												u_line.achieve = True
												line.is_complete = True
									if u_line.achieve:
										achieved_line += 1
								missing_req_units = []
								for x in req_units:
									if x not in req_units_found:
										missing_req_units.append(x)
								# raise Warning(_(missing_req_units))
								missing_required = False
								if missing_req_units == []:
									missing_required = False
								else:
									missing_required = True
								# check if the counts are same or if min creds requirement are met
								# if selected_line > 0 and achieved_line > 0 and min_qual_creds <= min_creds_found and not missing_required:
								# 	dbg('minimun creds met:' + str(min_creds_found) + 'found---' + str(min_qual_creds) + 'required-------missing required units:' + str(missing_req_units))
									# raise Warning(_('minimun creds met:' + str(min_creds_found) + 'found---' + str(min_qual_creds) + 'required-------missing required units:' + str(missing_req_units) + 'required' + str(missing_required)))
								if selected_line > 0 and achieved_line > 0 and selected_line == achieved_line or\
										selected_line > 0 and achieved_line > 0 and min_qual_creds <= min_creds_found and not missing_required:
									line.is_learner_achieved = True
									line.certificate_no = self.env['ir.sequence'].get('learner.certificate.no')
									line.certificate_date = str(datetime.today().date())
									line.approval_date = str(datetime.today().date())
									line.qual_status = 'Achieved'
									qual_line_obj.learner_status= 'Achieved'
									qual_line_obj.state= 'achieved'
									qual_line_obj.learners_status= 'achieved'
									learner_dict.update({'is_learner_achieved': True})
								# else:
								# 	dbg(str(line) + 'selected line' + str(selected_line) + 'achieved line:' + str(achieved_line))
						learner_achieved.append((0, 0, learner_dict))
			assessment_status_obj = self.env['assessment.status'].create({'name': self._uid,
																  'state':'achieved',
																  'pro_id':self.id,
																  'comment':self.comment,
																  'state_title':'Achieved'
																  })
			self.write({'state':'achieved', 'assessed':True, 'learner_achieved_ids':learner_achieved,'select_all':False})
			# code to check whether any1 learner achieve field checked or not by pradip 5/10/2016
			achieve_false = 0
			learner_line = 0
			for learner in self.learner_achieve_ids:
				if learner.achieve == False:
					achieve_false += 1
				learner_line += 1
			if achieve_false == learner_line:
				raise Warning(_("You haven't achieved any learner! Please achieve atleast one learner to continue.."))
			return True
		elif self.qual_skill_assessment == 'skill':
			learner_achieved = []
			if not self.learner_achieved_ids_for_skills:
				for learner_data in self.learner_achieve_ids_for_skills:
					if learner_data.achieve:
						skill_ids = []
						unit_ids = []
						for skill in learner_data.skill_learner_assessment_achieve_line_id:
							skill_ids.append(skill.id)
						for unit in learner_data.skill_unit_standards_learner_assessment_achieve_line_id:
							unit_ids.append(unit.id)
						learner_dict = {
								 'learner_id':learner_data.learner_id and learner_data.learner_id.id,
								 'learner_identity_number' : learner_data.learner_identity_number,
								 'identification_id' : learner_data.identification_id,
								 'skill_learner_assessment_achieved_line_id': [(6, 0, skill_ids)],
								 'skill_unit_standards_learner_assessment_achieved_line_id': [(6, 0, unit_ids)],
								 'assessors_id':learner_data.assessors_id and learner_data.assessors_id.id,
								 'moderators_id':learner_data.moderators_id and learner_data.moderators_id.id,
								 'timetable_id':learner_data.timetable_id and learner_data.timetable_id.id,
								}
						# This code is used to assign True value to achieve field of Skills Programme learner rel
						qual_line_obj = self.env['hr.employee'].search([('id', '=', learner_dict['learner_id'])])
						for line in qual_line_obj.skills_programme_ids:
							selected_line, achieved_line = 0, 0
							if line.skills_programme_id.id in skill_ids and line.provider_id.id == self.provider_id.id:
								for u_line in line.unit_standards_line:
									if u_line.selection:
										selected_line += 1
										for assessment_unit in learner_data.skill_unit_standards_learner_assessment_achieve_line_id:
											if u_line.title == assessment_unit.title:
												u_line.achieve = True
												line.is_complete = True
									if u_line.achieve:
										achieved_line += 1
								if selected_line > 0 and achieved_line > 0 and selected_line == achieved_line:
									line.is_learner_achieved = True
									line.certificate_no = self.env['ir.sequence'].get('learner.certificate.no')
									line.certificate_date = str(datetime.today().date())
									line.approval_date = str(datetime.today().date())
									line.skill_status = 'Achieved'
									qual_line_obj.learner_status= 'Achieved'
									qual_line_obj.state= 'achieved'
									qual_line_obj.learners_status= 'achieved'
									learner_dict.update({'is_learner_achieved': True})
						learner_achieved.append((0, 0, learner_dict))
			assessment_status_obj = self.env['assessment.status'].create({'name': self._uid,
																  'state':'achieved',
																  'pro_id':self.id,
																  'comment':self.comment,
																  'state_title':'Achieved'
																  })
			self.write({'state':'achieved', 'assessed':True, 'learner_achieved_ids_for_skills':learner_achieved,'select_all':False})
			# code to check whether any1 learner achieve field checked or not by pradip 5/10/2016
			achieve_false = 0
			learner_line = 0
			for learner in self.learner_achieve_ids_for_skills:
				if learner.achieve == False:
					achieve_false += 1
				learner_line += 1
			if achieve_false == learner_line:
				raise Warning(_("You haven't achieved any learner! Please achieve atleast one learner to continue.."))
			return True
		# Changes Added by Ganesh For Learning Programme
		elif self.qual_skill_assessment == 'lp':
			learner_achieved = []
			if not self.learner_achieved_ids_for_lp:
				for learner_data in self.learner_achieve_ids_for_lp:
					if learner_data.achieve:
						lp_ids = []
						unit_ids = []
						for lp in learner_data.lp_learner_assessment_achieve_line_id:
							lp_ids.append(lp.id)
						for unit in learner_data.lp_unit_standards_learner_assessment_achieve_line_id:
							unit_ids.append(unit.id)
						learner_dict = {
								 'learner_id':learner_data.learner_id and learner_data.learner_id.id,
								 'learner_identity_number' : learner_data.learner_identity_number,
								 'identification_id' : learner_data.identification_id,
								 'lp_learner_assessment_achieved_line_id': [(6, 0, lp_ids)],
								 'lp_unit_standards_learner_assessment_achieved_line_id': [(6, 0, unit_ids)],
								 'assessors_id':learner_data.assessors_id and learner_data.assessors_id.id,
								 'moderators_id':learner_data.moderators_id and learner_data.moderators_id.id,
								 'timetable_id':learner_data.timetable_id and learner_data.timetable_id.id,
								}
						# This code is used to assign True value to achieve field of learning programme learner rel
						learner_obj = self.env['hr.employee'].search([('id', '=', learner_dict['learner_id'])])
						for line in learner_obj.learning_programme_ids:
							selected_line, achieved_line = 0, 0
							if line.learning_programme_id.id in lp_ids and line.provider_id.id == self.provider_id.id:
								for u_line in line.unit_standards_line:
									if u_line.selection:
										selected_line += 1
										for assessment_unit in learner_data.lp_unit_standards_learner_assessment_achieve_line_id:
											if u_line.title == assessment_unit.title:
												u_line.achieve = True
												line.is_complete = True
									if u_line.achieve:
										achieved_line += 1
								if selected_line > 0 and achieved_line > 0 and selected_line == achieved_line:
									line.is_learner_achieved = True
									line.certificate_no = self.env['ir.sequence'].get('learner.certificate.no')
									line.certificate_date = str(datetime.today().date())
									line.approval_date = str(datetime.today().date())
									line.lp_status = 'Achieved'
									learner_obj.learner_status= 'Achieved'
									learner_obj.state= 'achieved'
									learner_obj.learners_status= 'achieved'
									learner_dict.update({'is_learner_achieved': True})
						learner_achieved.append((0, 0, learner_dict))
			assessment_status_obj = self.env['assessment.status'].create({'name': self._uid,
																  'state':'achieved',
																  'pro_id':self.id,
																  'comment':self.comment,
																  'state_title':'Achieved'
																  })
			self.write({'state':'achieved', 'assessed':True, 'learner_achieved_ids_for_lp':learner_achieved,'select_all':False})
			achieve_false = 0
			learner_line = 0
			for learner in self.learner_achieve_ids_for_lp:
				if learner.achieve == False:
					achieve_false += 1
				learner_line += 1
			if achieve_false == learner_line:
				raise Warning(_("You haven't achieved any learner! Please achieve atleast one learner to continue.."))

			return True

	@api.multi
	def onchange_provider(self, provider_id):
#         learner_line = []
#         provider_accreditation_num = ''
#         employee_pool = self.env['hr.employee']
#         if provider_id:
#             learning_programme_pool = self.env['learning.programme']
#             learning_programme_search_obj = learning_programme_pool.search([('provider_id', '=', provider_id)])
#             for learning_programme in learning_programme_search_obj:
#                 for learner in learning_programme.learner_ids:
#                     learner_search_obj = employee_pool.search([('provider_id', '=', provider_id), ('latest_employer', '=', learning_programme.employer_id.id), ('is_learner', '=', True)])
#                     for learner in learner_search_obj:
#                         val = {
#                                  'name':learner.name,
#                                  'person_last_name':learner.person_last_name,
#                                  'learner_reg_no':learner.learner_reg_no,
#                                  'timetable_id':learner.timetable_id,
#                                  'assessment_verify_id':self.id,
#                                  'assessment_timetables_id':self.id,
#                                  'assessment_id':self.id,
#                                 }
#                         learner_line.append((1, learner.id , val))
#                         provider_accreditation_num = learner.provider_accreditation_num
#             provider_data = self.env['res.partner'].browse(provider_id)
#             assessors_list = [assessors_rel.assessors_id and assessors_rel.assessors_id.id for assessors_rel in provider_data.assessors_ids]
#             moderators_list = [moderators_rel.moderators_id and moderators_rel.moderators_id.id for moderators_rel in provider_data.moderators_ids]
#             return {'domain': {'assessors_id': [('id', 'in', assessors_list)], 'moderators_id': [('id', 'in', moderators_list)] } , 'value':{'provider_accreditation_num': provider_accreditation_num, 'qualification_id':provider_data.qualification_id and provider_data.qualification_id.id, 'learner_ids':learner_line, 'learner_timetables':learner_line, 'learner_verification_ids':learner_line}}


#         if provider_id and employer_id:
#             employee_pool=self.env['hr.employee']
#             learner_search_obj=employee_pool.search([('provider_id', '=', provider_id), ('latest_employer','=',employer_id),('is_learner', '=', True)])
#             for learner in learner_search_obj:
#                 val = {
#                          'name':learner.name,
#                          'person_last_name':learner.person_last_name,
#                          'learner_reg_no':learner.learner_reg_no,
#                          'timetable_id':learner.timetable_id,
#                          'assessment_verify_id':self.id,
#                          'assessment_timetables_id':self.id,
#                          'assessment_id':self.id,
#                         }
#                 learner_line.append((1, learner.id , val))
#                 provider_accreditation_num=learner.provider_accreditation_num
#             provider_data = self.env['res.partner'].browse(provider_id)
#             assessors_list = [assessors_rel.assessors_id and assessors_rel.assessors_id.id for assessors_rel in provider_data.assessors_ids]
#             moderators_list = [moderators_rel.moderators_id and moderators_rel.moderators_id.id for moderators_rel in provider_data.moderators_ids]
#             return {'domain': {'assessors_id': [('id', 'in', assessors_list)], 'moderators_id': [('id', 'in', moderators_list)] } ,'value':{'provider_accreditation_num': provider_accreditation_num, 'qualification_id':provider_data.qualification_id and provider_data.qualification_id.id, 'learner_ids':learner_line, 'learner_timetables':learner_line, 'learner_verification_ids':learner_line}}


		return {}

	# #  Added  Sequence for Provider Assessment.
	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].get('provider.assessment')
		return super(provider_assessment, self).create(vals)

	@api.multi
	def write(self, vals):
		context = self._context
		if context is None:
			context = {}
		res = super(provider_assessment, self).write(vals)

		if self.state == "submitted" and self.submited == False:
			raise Warning(_('Sorry! you can not change state to submit'))

		if self.state == "verify" and self.verified == False:
			raise Warning(_('Sorry! you can not change state to Verified'))

		if self.state == "evaluate" and self.verified == False:
			raise Warning(_('Sorry! you can not change state to Evaluated'))

		if self.state == "achieved" and self.assessed == False:
			raise Warning(_('Sorry! you can not change state to Achievement'))

		if self.state == "draft" and self.submited == True:
			raise Warning(_('Sorry! you can not submit again'))

		if self.state == "submitted" and self.verified == True:
			raise Warning(_('Sorry! you can not verify again'))

		if self.state == "verify" and self.evaluated == True:
			raise Warning(_('Sorry! you can not evaluate again'))

		if self.state == "evaluate" and self.assessed == True:
			raise Warning(_('Sorry! you can not achieve again'))
		return res

	@api.multi
	def copy(self):
		''' Inherited to avoid duplicating records '''
		raise Warning(_('Sorry! You cannot create duplicate Assessment'))
		return super(provider_assessment, self).copy()

	@api.multi
	def unlink(self):
		''' Inherited to avoid duplicating records '''
		raise Warning(_('Sorry! You cannot delete the Assessment'))
		return super(provider_assessment, self).unlink()
provider_assessment()
# This class is created to add One2many field in hr.employee
class learner_master_status(models.Model):
	_name = 'learner.master.status'
	_description = 'Learner Master Status'

	learner_master_status_id = fields.Many2one('hr.employee', string='Learner Master Status Reference')
	learner_master_uid = fields.Char(string="Name")
	learner_master_status = fields.Char(string="Status")
	learner_master_comment = fields.Char(string="Comment")
	learner_master_date = fields.Datetime(string="Date")
learner_master_status()
# This class is created to add One2many field of history in learner.registration
class learner_status(models.Model):
	_name = 'learner.status'
	_description = 'Learner Status'

	learner_status_id = fields.Many2one('learner.registration', string='Learner Status Reference')
	learner_uid = fields.Char(string="Name")
	learner_status = fields.Char(string="Status")
	learner_comment = fields.Char(string="Comment")
	learner_date = fields.Datetime(string="Date")
	learner_updation_date = fields.Datetime(string="Update Date")
learner_status()

class learner_registration(models.Model):
	_name = 'learner.registration'
	_inherit = 'mail.thread'
	_description = 'Learner Registration'

	@api.v7
	def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
		res = models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
		if view_type == 'form':
			doc = etree.XML(res['arch'])
			for sheet in doc.xpath("//sheet"):
				parent = sheet.getparent()
				index = parent.index(sheet)
				for child in sheet:
					parent.insert(index, child)
					index += 1
				parent.remove(sheet)
			res['arch'] = etree.tostring(doc)
		return res

	@api.model
	def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
		""" Override read_group to filter learner registration's status count based on logged provider """
		if self.env.user.id != 1 and self.env.user.partner_id.provider == True:
#             domain.append(['logged_provider_id','=',self.env.user.partner_id.id])
			learner_ids = []
			self._cr.execute("select id from learner_registration where provider_id='%s'" % (self.env.user.partner_id.id,))
			learner_ids = map(lambda x:x[0], self._cr.fetchall())
			self._cr.execute("select id from learner_registration where create_uid='%s'" % (self.env.user.id,))
			learner_uids = map(lambda x:x[0], self._cr.fetchall())
			learner_ids.extend(learner_uids)
			self._cr.execute("select learner_qualification_id from learner_registration_qualification where learner_id is null and provider_id='%s'" % (self.env.user.partner_id.id,))
			learner_qids = map(lambda x:x[0], self._cr.fetchall())
			learner_ids.extend(learner_qids)
			domain.append(('id', 'in', learner_ids))
			self._cr.execute("select skills_programme_learner_rel_id from skills_programme_learner_rel where skills_programme_learner_rel_id is null and provider_id='%s'" % (self.env.user.partner_id.id,))
			learner_sids = map(lambda x:x[0], self._cr.fetchall())
			learner_ids.extend(learner_sids)
			self._cr.execute("select learning_programme_learner_rel_id from learning_programme_learner_rel where learning_programme_learner_rel_id is null and provider_id='%s'" % (self.env.user.partner_id.id,))
			learner_lids = map(lambda x:x[0], self._cr.fetchall())
			learner_ids.extend(learner_lids)
			domain.append(('id', 'in', learner_ids))
		return super(learner_registration, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

	@api.model
	def default_get(self, fields):
		context = self._context
		if context is None:
			context = {}
		res = super(learner_registration, self).default_get(fields)
		p_id = self.env.user.partner_id.id
		res.update({'provider_id' : p_id,'seeing_rating_id':'1', 'hearing_rating_id':'1', 'walking_rating_id':'1', 'remembering_rating_id':'1', 'communicating_rating_id':'1', 'self_care_rating_id':'1'})
		return res

	@api.depends('compute_field')
	def get_user(self):
		res_user = self.env['res.users'].search([('id', '=', self._uid)])
		if res_user.has_group('hwseta_etqe.group_seta_administrator'):
			self.compute_field = True
		else:
			self.compute_field = False

	@api.model
	def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
		user = self._uid
		user_obj = self.env['res.users']
		user_data = user_obj.browse(user)
		user_groups = user_data.groups_id
		for group in user_groups:
			if group.name in ['ETQE Manager', 'ETQE Executive Manager', 'ETQE Provincial Manager', 'ETQE Officer', 'ETQE Provincial Officer', 'ETQE Administrator', 'ETQE Provincial Administrator', 'Applicant Skills Development Provider', 'CEO']:
				return super(learner_registration, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		if user == 1:
			return super(learner_registration, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		if user_data.partner_id.provider:
			learner_ids = []
			self._cr.execute("select id from learner_registration where provider_id='%s'" % (user_data.partner_id.id,))
			learner_ids = map(lambda x:x[0], self._cr.fetchall())
			self._cr.execute("select id from learner_registration where create_uid='%s'" % (user_data.id,))
			learner_uids = map(lambda x:x[0], self._cr.fetchall())
			learner_ids.extend(learner_uids)
			self._cr.execute("select learner_qualification_id from learner_registration_qualification where learner_id is null and provider_id='%s'" % (user_data.partner_id.id,))
			learner_qids = map(lambda x:x[0], self._cr.fetchall())
			learner_ids.extend(learner_qids)
			self._cr.execute("select skills_programme_learner_rel_id from skills_programme_learner_rel where skills_programme_learner_rel_id is null and provider_id='%s'" % (self.env.user.partner_id.id,))
			learner_sids = map(lambda x:x[0], self._cr.fetchall())
			learner_ids.extend(learner_sids)
			self._cr.execute("select learning_programme_learner_rel_id from learning_programme_learner_rel where learning_programme_learner_rel_id is null and provider_id='%s'" % (self.env.user.partner_id.id,))
			learner_lids = map(lambda x:x[0], self._cr.fetchall())
			learner_ids.extend(learner_lids)
			args.append(('id', 'in', learner_ids))
			return super(learner_registration, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		return super(learner_registration, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

	provider_id = fields.Many2one('res.partner', string="Provider", track_visibility='onchange')
	image_medium = fields.Binary(string='Medium Photo')
	is_existing_learner = fields.Boolean(string='Existing Learner', track_visibility='onchange')
	citizen_status = fields.Selection([('dual', 'Dual (SA plus other)'), ('other', 'Other'), ('PR', 'Permanent Resident'), ('sa', 'South Africa'), ('unknown', 'Unknown')], string='Citizen Status')
	onchange_identification_number = fields.Char(string='Identification Number', size=13)
	existing_national_id = fields.Char(string='National ID', track_visibility='onchange')
	# learner_reg_no = fields.Char(string='Learner Reg No')
	name = fields.Char(string="First Name", track_visibility='onchange', required=True)
	work_email = fields.Char(string='Email', track_visibility='onchange')
	work_phone = fields.Char(string='Phone', track_visibility='onchange', size=10)
	financial_year = fields.Datetime(string='Enrollment Year',track_visibility='onchange')
	work_address = fields.Char(string='Work Address', track_visibility='onchange')
	work_address2 = fields.Char(string='Work Address 2', track_visibility='onchange')
	work_address3 = fields.Char(string='Work Address 3', track_visibility='onchange')
	person_suburb = fields.Many2one('res.suburb', string='Suburb')
	work_municipality = fields.Many2one('res.municipality', string='Working Municipality')
	work_city = fields.Many2one('res.city', string='Work City', track_visibility='onchange')
	work_province = fields.Many2one('res.country.state', string='Work Place Province', track_visibility='onchange')
	work_zip = fields.Char(string='Place Zip', track_visibility='onchange')
	work_country = fields.Many2one('res.country', string='Place Country', track_visibility='onchange')
	department = fields.Char(string='Department', track_visibility='onchange')
	job_title = fields.Char(string='Job Title', track_visibility='onchange')
	manager = fields.Char(string='Manager', track_visibility='onchange')
	user_id = fields.Many2one('res.users', string='Related User', track_visibility='onchange')
	notes = fields.Text(string='Notes', track_visibility='onchange')
	# contact information
	person_title = fields.Selection([('adv', 'Adv.'), ('dr', 'Dr.'), ('mr', 'Mr.'), ('mrs', 'Mrs.'), ('ms', 'Ms.'), ('prof', 'Prof.')], string='Person Title', track_visibility='onchange')
	person_name = fields.Char(string='Name', track_visibility='onchange', size=50)
	person_last_name = fields.Char(string='Last Name', track_visibility='onchange', size=45)
	initials = fields.Char(string='Initials', track_visibility='onchange', size=50)
	maiden_name = fields.Char(string='Maiden Name')
	middle_name = fields.Char(string='Middle Name')
	cell = fields.Char(string='Mobile Number', size=10)
	person_fax_number = fields.Char(string='Tele Fax Number', size=10)
	socio_economic_status = fields.Selection([('employed', 'Employed'), ('unemployed', 'Unemployed, seeking work'),
											('Not working, not looking', 'Not working, not looking'),
											('Home-maker (not working)', 'Home-maker (not working)'),
											('Scholar/student (not w.)', 'Scholar/student (not w.)'),
											('Pensioner/retired (not w.)', 'Pensioner/retired (not w.)'),
											('Not working - disabled', 'Not working - disabled'),
											('Not working - no wish to w', 'Not working - no wish to w'),
											('Not working - N.E.C.', 'Not working - N.E.C.'),
											('N/A: aged <15', 'N/A: aged <15'),
											('N/A: Institution', 'N/A: Institution'),
											('Unspecified', 'Unspecified'), ], string='Socio Economic Status')
	current_occupation = fields.Char(string='Current Occupation', track_visibility='onchange', size=50)
	years_in_occupation = fields.Char(string='Years in Occupation')
	method_of_communication = fields.Selection([('cell_phone', 'Cell Phone'), ('email', 'Email')], string='Method of Communication')
	status_effective_date = fields.Date(string='Status Effective Date')
	last_updated_operator = fields.Char(string='Last Updated Operator')
	# Citizenship & Other Info
	african = fields.Boolean(string='African')
	citizen_resident_status_code = fields.Selection([('dual', 'Dual (SA plus other)'), ('other', 'Other'), ('PR', 'Permanent Resident'), ('sa', 'South Africa'), ('unknown', 'Unknown')], string='Citizen Status')
	country_id = fields.Many2one('res.country', string='Nationality', track_visibility='onchange')
	identification_id = fields.Char(string='Identification No', track_visibility='onchange', size=13)
	alternate_id_type = fields.Selection([('saqa_member', '521 - SAQA Member ID'), ('passport_number', '527 - Passport Number'), ('drivers_license','529 - Drivers License'), ('temporary_id_number','531 - Temporary ID number'), ('none', '533 - None'), ('unknown','535 - Unknown'), ('student_number', '537 - Student number'), ('work_permit_number', '538 - Work Permit Number'),('employee_number','539 - Employee Number'),('birth_certificate_number','540 - Birth Certificate Number'),('hsrc_register_number',' 541 - HSRC Register Number'),('etqe_record_number','561 - ETQA Record Number'),('refugee_number','565 - Refugee Number')], string='Alternate ID Type')
	person_birth_date = fields.Date(string='Birth Date', track_visibility='onchange')
	passport_id = fields.Char(string='Passport No', track_visibility='onchange')
	national_id = fields.Char(string='National Id', track_visibility='onchange', size=13)
	id_document = fields.Many2one('ir.attachment', string='ID Document', help='Upload Document')
	home_language_code = fields.Many2one('res.lang', string='Home Language Code', track_visibility='onchange', size=6)
	learner_status = fields.Char('Learner Status')
	certificate_no = fields.Char(string='Qualification & Certificate No')
	record_last_update = fields.Date(string='Record Last Updated', track_visibility='onchange')
	status_comments = fields.Char(string='Status Comment', track_visibility='onchange')
	highest_education = fields.Char(string='Highest Education', size=20)
	wsp_year = fields.Selection([('2015', '2015'), ('2016', '2016')], 'WSP Year', track_visibility='onchange')
	# status
	gender = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Gender', track_visibility='onchange')
	marital = fields.Selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('widow', 'Widow'), ('divorced', 'Divorced')], 'Marital Status', track_visibility='onchange')
	dissability = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Disability")
	status_reason = fields.Selection([('workplace_learning', '500 - Workplace learning')], 'Learner Status Reason')
	is_sdf = fields.Boolean(string='SDF', track_visibility='onchange')
	is_learner = fields.Boolean(string='Learner', track_visibility='onchange')
	seta_elements = fields.Boolean(string='Seta Elements', track_visibility='onchange')
	socio_economic_saqa_code = fields.Selection([('1', '01'), ('2', '02'), ('3', '03'), ('4', '04'), ('6', '06'), ('7', '07'), ('8', '08'), ('9', '09'), ('10', '10'), ('97', '97'), ('98', '98'), ('U', 'U')], string='Socio Economic Status SAQA Code')
	enrollment_date = fields.Date("Enrollment Date", readonly=True)
	# .
	gender_saqa_code = fields.Selection([('m', 'M'), ('f', 'F')], string='Gender SAQA Code')
	equity = fields.Selection([('black_african', 'Black: African'), ('black_indian', 'Black: Indian / Asian'), ('black_coloured', 'Black: Coloured'), ('other', 'Other'), ('unknown', 'Unknown'), ('white', 'White')], string='Equity')
	equity_saqa_code = fields.Selection([('ba', 'BA'), ('bi', 'BI'), ('bc', 'BC'), ('oth', 'Oth'), ('u', 'U'), ('wh', 'Wh')], string='Equity SAQA Code')
	disability_status = fields.Selection([
													('sight', 'Sight ( even with glasses )'),
													('hearing', 'Hearing ( even with h.aid )'),
													('communication', 'Communication ( talk/listen)'),
													('physical', 'Physical ( move/stand, etc)'),
													('intellectual', 'Intellectual ( learn,etc)'),
													('emotional', 'Emotional ( behav/psych)'),
													('multiple', 'Multiple'),
													('disabled', 'Disabled but unspecified'),
													('none', 'None'), ], string='Disability Status')
	disability_status_saqa = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('9', '9'), ('n', 'N')], string='Disability SAQA Code')
	# Banking Details
	bank_name = fields.Char(string='Bank Name')
	branch_code = fields.Char(string='Branch Code')
	bank_account_number = fields.Char(string='Bank Account Number', track_visibility='onchange')
	# Address
	same_as_home = fields.Boolean(string='Same As Home Address')
	person_home_address_1 = fields.Char(string='Home Address 1', track_visibility='onchange', size=50)
	person_home_address_2 = fields.Char(string='Home Address 2', track_visibility='onchange', size=50)
	person_home_address_3 = fields.Char(string='Home Address 3', track_visibility='onchange', size=50)
	person_home_suburb = fields.Many2one('res.suburb', string='Home Suburb')
	person_postal_suburb = fields.Many2one('res.suburb', string='Postal Suburb')
	postal_municipality = fields.Many2one('res.municipality', string='Postal Municipality')
	person_postal_city = fields.Many2one('res.city', string='Postal City', track_visibility='onchange')
	person_home_city = fields.Many2one('res.city', string='Home City', track_visibility='onchange')
	person_home_province_code = fields.Many2one('res.country.state', string='Home Province Code', track_visibility='onchange')
	person_postal_province_code = fields.Many2one('res.country.state', string='Postal Province Code', track_visibility='onchange')
	person_home_zip = fields.Char(string='Postal Zip', track_visibility='onchange')
	person_postal_zip = fields.Char(string='Postal Zip', track_visibility='onchange')
	country_postal = fields.Many2one('res.country', string='Postal Country', track_visibility='onchange')
	provider_code = fields.Char(string='Provider Code', size=20)
	person_home_addr_postal_code = fields.Char(string='Home Address Postal Code', track_visibility='onchange', size=4)
	physical_municipality = fields.Many2one('res.municipality', string='Physical Municipality')
	country_home = fields.Many2one('res.country', string='Home Country', track_visibility='onchange')
	person_cell_phone_number = fields.Char(string='Cell Phone Number', track_visibility='onchange', size=10)
	person_postal_address_1 = fields.Char(string='Postal Address 1', track_visibility='onchange', size=50)
	person_postal_address_2 = fields.Char(string='Postal Address 2', track_visibility='onchange', size=50)
	person_postal_address_3 = fields.Char(string='Postal Address 3', track_visibility='onchange', size=50)
	country_postal = fields.Many2one('res.country', string='Postal Country', track_visibility='onchange')
	# Rating
	seeing_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')], string='Seeing Rating Id', track_visibility='onchange')
	hearing_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')], string='Hearing Rating Id', track_visibility='onchange')
	walking_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')], string='Walking Rating Id', track_visibility='onchange')
	remembering_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')], string='Remembering Rating Id', track_visibility='onchange')
	statssa_area_code = fields.Integer(string='STATSSA Area Code', track_visibility='onchange', size=20)
	popi_act_status_date = fields.Date(string='POPI Act Status Date', track_visibility='onchange')
	communicating_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')], string='Communicating Rating Id', track_visibility='onchange')
	self_care_rating_id = fields.Selection([('1', 'No difficulty'), ('2', 'Some difficulty'), ('3', 'A lot of difficulty'), ('4', 'Cannot do at all'), ('6', 'Cannot yet be determined'), ('60', 'May be part of multiple difficulties (TBC)'), ('70', 'May have difficulty (TBC)'), ('80', 'Former difficulty - none now')], string='Self Care Rating Id', track_visibility='onchange')
	last_school_emis_no = fields.Char(string='Last School EMIS No', track_visibility='onchange', size=20)
	last_school_year = fields.Integer(string='Last School Year', track_visibility='onchange', size=4)
	popi_act_status_id = fields.Integer(string='POPI Act Status Id', track_visibility='onchange', size=2)
	date_stamp = fields.Date(string='Date Stamp', track_visibility='onchange')
	# state
	state = fields.Selection([
			('draft', 'Draft'),
			('approved', 'Approved'),
			('rejected', 'Rejected'),
		], string='Status', index=True, readonly=True, default='draft',
		track_visibility='onchange', copy=False)
#     submited = fields.Boolean(string="Submited", track_visibility='onchange', default=False)
#     verified = fields.Boolean(string="Verified", track_visibility='onchange', default=False)
#     evaluated = fields.Boolean(string="Verified", track_visibility='onchange', default=False)
	approved = fields.Boolean(string="Approved", track_visibility='onchange', default=False)
	rejected = fields.Boolean(string="Rejected", track_visibility='onchange', default=False)
	learner_qualification_ids = fields.One2many('learner.registration.qualification', 'learner_qualification_id')
	# One2many field to maintain history of learner status
	learner_status_ids = fields.One2many('learner.status', 'learner_status_id', 'Status Line')
	comment = fields.Text("Comment")
	logged_provider_id = fields.Many2one(related="learner_qualification_ids.provider_id")
	skills_programme_ids = fields.One2many('skills.programme.learner.rel', 'skills_programme_learner_rel_id', 'Skills Programme Lines')
	learner_other_docs_ids = fields.One2many('acc.multi.doc.upload', 'learner_reg_id', string='Learner Other Documents', track_visibility='onchange')
	logged_provider_id_for_skills = fields.Many2one(related="skills_programme_ids.provider_id")
	# New Fields For Learning Programme
	learning_programme_ids = fields.One2many('learning.programme.learner.rel', 'learning_programme_learner_rel_id', 'Learning Programme Lines')
	logged_provider_id_for_lp = fields.Many2one(related="learning_programme_ids.provider_id")
	compute_field = fields.Boolean(string="check field", compute='get_user')

	@api.multi
	def onchange_details(self, identification_id):
		if identification_id:
			learner_obj = self.env['hr.employee'].search([('learner_identification_id', '=', identification_id)])
			if not learner_obj:
				return {'value': {'is_existing_learner': False, 'citizen_status':'', 'onchange_identification_number': ''},\
						'warning':{'title':'Invalid Identification Number','message':'Learner does not exist in the learner master with this Identification Number!'}}
			if learner_obj:
				for learner in learner_obj:
					val = {
							'seta_elements':True,
							'is_learner':True,
							'name':learner.name,
							'work_email':learner.work_email,
							'work_phone':learner.work_phone,
							'work_address':learner.work_address,
							'work_address2':learner.work_address2,
							'work_address3':learner.work_address3,
							'person_suburb':learner.person_suburb.id,
							'work_municipality':learner.work_municipality.id,
							'work_city':learner.work_city.id,
							'work_province':learner.work_province.id,
							'work_zip':learner.work_zip,
							'work_country':learner.work_country.id,
							'department':learner.department,
							'job_title':learner.job_title,
							'manager':learner.manager,
							'user_id':learner.user_id,
							'notes':learner.notes,
							'person_title':learner.person_title,
							'person_name':learner.person_name,
							'person_last_name':learner.person_last_name,
							'initials':learner.initials,
							'maiden_name':learner.maiden_name,
							'middle_name':learner.person_middle_name,
							'cell':learner.cell,
							'person_fax_number':learner.person_fax_number,
							'highest_education':learner.highest_education,
							'current_occupation':learner.current_occupation,
							'years_in_occupation':learner.years_in_occupation,
							'method_of_communication':learner.method_of_communication,
							'last_updated_operator':learner.last_updated_operator,
							'status_effective_date':learner.status_effective_date,
							'citizen_resident_status_code':learner.citizen_resident_status_code,
							'country_id':learner.country_id.id,
							'identification_id':learner.learner_identification_id,
							'alternate_id_type':learner.alternate_id_type,
							'person_birth_date':learner.person_birth_date,
							'passport_id':learner.passport_id,
							'national_id':learner.national_id,
							'id_document':learner.id_document.id,
							'home_language_code':learner.home_language_code.id,
							'learner_status':'Re-Enrolled',
							'certificate_no':learner.certificate_no,
							'record_last_update':learner.record_last_update,
							'status_comments':learner.status_comments,
							'highest_education':learner.highest_education,
							'wsp_year':learner.wsp_year,
							'gender':learner.gender,
							'marital':learner.marital,
							'dissability':learner.dissability,
							'status_reason':learner.status_reason,
							'socio_economic_saqa_code':learner.socio_economic_saqa_code,
							'is_sdf':learner.is_sdf,
							'gender_saqa_code':learner.gender_saqa_code,
							'equity':learner.equity,
							'equity_saqa_code':learner.equity_saqa_code,
							'socio_economic_status':learner.socio_economic_status,
							'disability_status':learner.disability_status,
							'disability_status_saqa':learner.disability_status_saqa,
							'person_home_address_1':learner.person_home_address_1,
							'person_home_address_2':learner.person_home_address_2,
							'person_home_address_3':learner.person_home_address_3,
							'person_home_suburb':learner.person_home_suburb.id,
							'physical_municipality':learner.physical_municipality.id,
							'person_home_city':learner.person_home_city.id,
							'person_home_province_code':learner.person_home_province_code.id,
							'person_home_zip':learner.person_home_zip,
							'country_home':learner.country_home.id,
							'same_as_home':learner.same_as_home,
							'person_postal_address_1':learner.person_postal_address_1,
							'person_postal_address_2':learner.person_postal_address_2,
							'person_postal_address_3':learner.person_postal_address_3,
							'person_postal_suburb':learner.person_postal_suburb.id,
							'postal_municipality':learner.postal_municipality.id,
							'person_postal_city':learner.person_postal_city.id,
							'person_postal_province_code':learner.person_postal_province_code.id,
							'person_postal_zip':learner.person_postal_zip,
							'country_postal':learner.country_postal.id,
							'seeing_rating_id':learner.seeing_rating_id,
							'hearing_rating_id':learner.hearing_rating_id,
							'walking_rating_id':learner.walking_rating_id,
							'remembering_rating_id':learner.remembering_rating_id,
							'statssa_area_code':learner.statssa_area_code,
							'popi_act_status_date':learner.popi_act_status_date,
							'communicating_rating_id':learner.communicating_rating_id,
							'self_care_rating_id':learner.self_care_rating_id,
							'last_school_emis_no':learner.last_school_emis_no,
							'last_school_year':learner.last_school_year,
							'popi_act_status_id':learner.popi_act_status_id,
							'date_stamp':learner.date_stamp,
							'enrollment_date':learner.enrollment_date,
						  }
					return {'value':val}
	@api.multi
	def onchange_existing_national_id(self, existing_national_id):
		if existing_national_id:
			learner_obj = self.env['hr.employee'].search([('national_id', '=', existing_national_id)])
			if not learner_obj:
				return {'value': {'is_existing_learner': False, 'citizen_status':'', 'existing_national_id': ''},\
						'warning':{'title':'Invalid Identification Number','message':'Learner does not exist in the learner master with this Identification Number!'}}
			if learner_obj:
				for learner in learner_obj:
					val = {
							'seta_elements':True,
							'is_learner':True,
							'name':learner.name,
							'work_email':learner.work_email,
							'work_phone':learner.work_phone,
							'work_address':learner.work_address,
							'work_address2':learner.work_address2,
							'work_address3':learner.work_address3,
							'person_suburb':learner.person_suburb.id,
							'work_municipality':learner.work_municipality.id,
							'work_city':learner.work_city.id,
							'work_province':learner.work_province.id,
							'work_zip':learner.work_zip,
							'work_country':learner.work_country.id,
							'department':learner.department,
							'job_title':learner.job_title,
							'manager':learner.manager,
							'user_id':learner.user_id,
							'notes':learner.notes,
							'person_title':learner.person_title,
							'person_name':learner.person_name,
							'person_last_name':learner.person_last_name,
							'initials':learner.initials,
							'maiden_name':learner.maiden_name,
							'middle_name':learner.person_middle_name,
							'cell':learner.cell,
							'person_fax_number':learner.person_fax_number,
							'highest_education':learner.highest_education,
							'current_occupation':learner.current_occupation,
							'years_in_occupation':learner.years_in_occupation,
							'method_of_communication':learner.method_of_communication,
							'last_updated_operator':learner.last_updated_operator,
							'status_effective_date':learner.status_effective_date,
							'citizen_resident_status_code':learner.citizen_resident_status_code,
							'country_id':learner.country_id.id,
							'identification_id':learner.learner_identification_id,
							'alternate_id_type':learner.alternate_id_type,
							'person_birth_date':learner.person_birth_date,
							'passport_id':learner.passport_id,
							'national_id':learner.national_id,
							'id_document':learner.id_document.id,
							'home_language_code':learner.home_language_code.id,
							'learner_status':'Re-Enrolled',
							'certificate_no':learner.certificate_no,
							'record_last_update':learner.record_last_update,
							'status_comments':learner.status_comments,
							'highest_education':learner.highest_education,
							'wsp_year':learner.wsp_year,
							'gender':learner.gender,
							'marital':learner.marital,
							'dissability':learner.dissability,
							'status_reason':learner.status_reason,
							'socio_economic_saqa_code':learner.socio_economic_saqa_code,
							'is_sdf':learner.is_sdf,
							'gender_saqa_code':learner.gender_saqa_code,
							'equity':learner.equity,
							'equity_saqa_code':learner.equity_saqa_code,
							'socio_economic_status':learner.socio_economic_status,
							'disability_status':learner.disability_status,
							'disability_status_saqa':learner.disability_status_saqa,
							'person_home_address_1':learner.person_home_address_1,
							'person_home_address_2':learner.person_home_address_2,
							'person_home_address_3':learner.person_home_address_3,
							'person_home_suburb':learner.person_home_suburb.id,
							'physical_municipality':learner.physical_municipality.id,
							'person_home_city':learner.person_home_city.id,
							'person_home_province_code':learner.person_home_province_code.id,
							'person_home_zip':learner.person_home_zip,
							'country_home':learner.country_home.id,
							'same_as_home':learner.same_as_home,
							'person_postal_address_1':learner.person_postal_address_1,
							'person_postal_address_2':learner.person_postal_address_2,
							'person_postal_address_3':learner.person_postal_address_3,
							'person_postal_suburb':learner.person_postal_suburb.id,
							'postal_municipality':learner.postal_municipality.id,
							'person_postal_city':learner.person_postal_city.id,
							'person_postal_province_code':learner.person_postal_province_code.id,
							'person_postal_zip':learner.person_postal_zip,
							'country_postal':learner.country_postal.id,
							'seeing_rating_id':learner.seeing_rating_id,
							'hearing_rating_id':learner.hearing_rating_id,
							'walking_rating_id':learner.walking_rating_id,
							'remembering_rating_id':learner.remembering_rating_id,
							'statssa_area_code':learner.statssa_area_code,
							'popi_act_status_date':learner.popi_act_status_date,
							'communicating_rating_id':learner.communicating_rating_id,
							'self_care_rating_id':learner.self_care_rating_id,
							'last_school_emis_no':learner.last_school_emis_no,
							'last_school_year':learner.last_school_year,
							'popi_act_status_id':learner.popi_act_status_id,
							'date_stamp':learner.date_stamp,
							'enrollment_date':learner.enrollment_date,
						  }
					return {'value':val}

	@api.multi
	@api.onchange('work_phone','cell','person_fax_number','years_in_occupation','is_existing_learner','work_email')
	def onchange_validate_number(self):
		if self.is_existing_learner == False:
			if self.work_email:
				if '@' not in self.work_email:
					self.work_email = ''
					return {'warning':{'title':'Invalid input','message':'Please enter valid email address'}}
			if self.work_phone:
				learner_obj = self.env['hr.employee'].search([('work_phone','=',self.work_phone)])
				if learner_obj:
					self.work_phone = ''
					return {'warning':{'title':'Duplicate Entry','message':'Please enter unique Phone number'}}
				if not self.work_phone.isdigit() or len(self.work_phone) != 10:
					self.work_phone = ''
					return {'warning':{'title':'Invalid input','message':'Please enter 10 digits Phone number'}}
			if self.cell:
				learner_obj = self.env['hr.employee'].search([('cell','=',self.cell)])
				if learner_obj:
					self.cell = ''
					return {'warning':{'title':'Duplicate Entry','message':'Please enter unique Mobile number'}}
				if not self.cell.isdigit() or len(self.cell) != 10:
					self.cell = ''
					return {'warning':{'title':'Invalid input','message':'Please enter 10 digits Mobile number'}}
			if self.person_fax_number:
				if not self.person_fax_number.isdigit() or len(self.person_fax_number) != 10:
					self.person_fax_number = ''
					return {'warning':{'title':'Invalid input','message':'Please enter 10 digits Fax number'}}
			if self.years_in_occupation:
				if not self.years_in_occupation.isdigit() or len(self.years_in_occupation) > 2:
					self.years_in_occupation = ''
					return {'warning':{'title':'Invalid input','message':'Please enter valid years in occupation'}}

	@api.multi
	def onchange_gender(self, gender):
		res = {}
		if not gender:
			res.update({'value':{'gender_saqa_code':''}})
			return res
		if gender == 'male':
			res.update({'value':{'gender_saqa_code':'m'}})
		elif gender == 'female':
			res.update({'value':{'gender_saqa_code':'f'}})
		return res

	@api.multi
	def onchange_gender_saqa_code(self, gender_saqa_code):
		res = {}
		if not gender_saqa_code:
			res.update({'value':{'gender':''}})
			return res
		if gender_saqa_code == 'm':
			res.update({'value':{'gender':'male'}})
		elif gender_saqa_code == 'f':
			res.update({'value':{'gender':'female'}})
		return res

	@api.multi
	def onchange_person_postal_suburb(self, person_postal_suburb):
		res = {}
		if not person_postal_suburb:
			return res
		if person_postal_suburb:
			sub_res = self.env['res.suburb'].browse(person_postal_suburb)
			res.update({'value':{'person_postal_zip':sub_res.postal_code, 'postal_municipality':sub_res.municipality_id, 'person_postal_city':sub_res.city_id, 'person_postal_province_code':sub_res.province_id}})
		return res

	@api.multi
	def onchange_person_home_suburb(self, person_home_suburb):
		res = {}
		if not person_home_suburb:
			return res
		if person_home_suburb:
			sub_res = self.env['res.suburb'].browse(person_home_suburb)
			res.update({'value':{'person_home_zip':sub_res.postal_code, 'person_home_city':sub_res.city_id, 'physical_municipality':sub_res.municipality_id, 'person_home_province_code':sub_res.province_id}})
		return res

	@api.multi
	def onchange_person_suburb(self, person_suburb):
		res = {}
		if not person_suburb:
			return res
		if person_suburb:
			sub_res = self.env['res.suburb'].browse(person_suburb)
			res.update({'value':{'work_zip':sub_res.postal_code, 'work_city':sub_res.city_id, 'work_province':sub_res.province_id, 'work_municipality':sub_res.municipality_id}})
		return res

	@api.multi
	def onchange_id_no(self, identification_id, is_existing_learner):
		res, val = {}, {}
		if not identification_id:
			return res
		if len(identification_id) == 13 and str(identification_id).isdigit():
			if not is_existing_learner:
				duplicate_id = self.env['hr.employee'].search([('learner_identification_id','=',identification_id)])
				duplicate_learner_id = self.env['learner.registration'].search([('identification_id','=',identification_id),('state','=','draft'),('create_uid','=',self._uid)])
				if duplicate_id:
					return {'value':{'is_existing_learner':True, 'onchange_identification_number': identification_id}}
				if duplicate_learner_id:
					return {'value':{'identification_id':''},'warning':{'title':'Duplicate Entry','message':'Learner Identification Number must be unique per Learner!'}}
			if is_existing_learner:
				duplicate_learner_id = self.env['learner.registration'].search([('identification_id','=',identification_id),('state','=','draft'),('create_uid','=',self._uid)])
				if duplicate_learner_id:
					return {'value':{'identification_id':''},'warning':{'title':'Duplicate Entry','message':'Learner record already exists with same Identification Number in draft state!'}}
			gender_digit = str(identification_id)[6:10]
			citizenship = str(identification_id)[10:11]
			if gender_digit:
				if int(gender_digit) <= 4999:
					val.update({'gender':'female'})
				elif int(gender_digit) >= 5000:
					val.update({'gender':'male'})
			if citizenship:
				if int(citizenship) == 0:
					val.update({'citizen_resident_status_code':'sa'})
				elif int(citizenship) == 1:
					val.update({'citizen_resident_status_code':'PR'})
			year = identification_id[:2]
			identification_id = identification_id[2:]
			month = identification_id[:2]
			identification_id = identification_id[2:]
			day = identification_id[:2]
			if int(month) > 12 or int(month) < 1 or int(day) > 31 or int(day) < 1:
				return {'value':{'identification_id':''},'warning':{'title':'Invalid Identification Number','message':'Incorrect Identification Number!'}}
			else:
				# # Calculating last day of month.
				x_year = int(year)
				if x_year == 00:
					x_year = 2000
				last_day = calendar.monthrange(int(x_year),int(month))[1]
				if int(day) > last_day :
					return {'value':{'identification_id':''},'warning':{'title':'Invalid Identification Number','message':'Incorrect Identification Number!'}}
			if int(year) == 00 or int(year) >= 01 and int(year) <= 20:
				birth_date = datetime.strptime('20' + year + '-' + month + '-' + day, '%Y-%m-%d').date()
			else:
				birth_date = datetime.strptime('19' + year + '-' + month + '-' + day, '%Y-%m-%d').date()

			val.update({'person_birth_date':birth_date})
			res.update({'value':val})
			return res
		else:
			return {'value':{'identification_id':''},'warning':{'title':'Invalid Identification Number','message':'Identification Number should be numeric!'}}

	@api.multi
	def onchange_socio(self, socio_economic_status):
		res = {}
		if not socio_economic_status:
			return res
		if socio_economic_status == 'unemployed':
			res.update({'value':{'current_occupation':'', 'years_in_occupation':''}})
		return res

	@api.multi
	def open_map(self, street, city, state, country, zip):
		url = "http://maps.google.com/maps?oi=map&q="
		if street:
			url += street.replace(' ', '+')
		if state:
			url += '+' + state.name.replace(' ', '+')
		if country:
			url += '+' + country.name.replace(' ', '+')
		if zip:
			url += '+' + zip.replace(' ', '+')
		return {
		'type': 'ir.actions.act_url',
		'url':url,
		'target': 'new'
		}

	@api.multi
	def work_addr_map(self):
		return self.open_map(self.work_address, self.work_city, self.work_province, self.work_country, self.work_zip)

	@api.multi
	def home_addr_map(self):
		return self.open_map(self.person_home_address_1, self.person_home_city, self.person_home_province_code, self.country_home, self.person_home_zip)

	@api.multi
	def postal_addr_map(self):
		return self.open_map(self.person_postal_address_1, self.person_postal_city, self.person_postal_province_code, self.country_postal, self.person_postal_zip)

	@api.multi
	def check_all_required_fields(self):
		'''This method is used to check all the required fields are filled or not'''
		if not self.person_title and not self.name and not self.person_last_name and not self.work_email and not self.work_phone and not self.gender and not self.marital and not self.disability and not self.disability_status and not self.socio_economic_status and not self.person_home_address_1 and not self.cell and not self.method_of_communication and not self.citizen_resident_status_code and not self.id_document:
			return {'warning':{'title':'Warning','message':'Please fill all the required fields!!'}}
		if self.socio_economic_status:
			if not self.current_occupation and not self.years_in_occupation:
				return {'warning':{'title':'Warning','message':'Please fill all the required fields!!'}}
		if self.citizen_resident_status_code in ['dual', 'PR', 'sa']:
			if not self.identification_id:
				return {'warning':{'title':'Warning','message':'Please fill all the required fields!!'}}
		if self.citizen_resident_status_code in ['other','unknown']:
			if not self.national_id:
			   return {'warning':{'title':'Warning','message':'Please fill all the required fields!!'}}

	@api.multi
	def action_approved_button(self):
		try:
			context = self._context
			if context is None:
				context = {}
			context = self._context

			self.check_all_required_fields()
			if self.identification_id:
				if len(self.identification_id) < 13:
					raise Warning(_("Please enter 13 digits Identification No."))
			if not self.learner_qualification_ids and not self.skills_programme_ids and not self.learning_programme_ids:
				raise Warning(_("Sorry! Please add Learner's Qualification or Skills Programme or Learning Programme before approve"))
			if self.work_phone:
				if not self.work_phone.isdigit() or len(self.work_phone) != 10:
					raise Warning(_('Please enter 10 digits Phone number'))
			if self.cell:
				if not self.cell.isdigit() or len(self.cell) != 10:
					raise Warning(_('Please enter 10 digits Mobile number'))
			if self.person_fax_number:
				if not self.person_fax_number.isdigit() or len(self.person_fax_number) != 10:
					raise Warning(_('Please enter 10 digits Fax number'))
			if self.years_in_occupation:
				if not self.years_in_occupation.isdigit() or len(self.years_in_occupation) > 2:
					raise Warning(_('Please enter valid years in occupation'))
			if self.is_existing_learner == False:
				for line in self.learner_qualification_ids:
					if line.learner_qualification_parent_id.is_exit_level_outcomes == False:
						if line.minimum_credits > line.total_credits:
							raise Warning(_("Sum of checked unit standards credits point should be greater than or equal to Minimum credits point !!"))

			if self.learning_programme_ids:
				date_list = []
				for lp_line in self.learning_programme_ids:
					if lp_line.start_date > lp_line.end_date:
						raise Warning(_("Sorry! Learning Programme Start Date should not be greater than Learning Programme End Date"))
					date_list.append(lp_line.start_date)
					date_list.append(lp_line.end_date)
				for c, value in enumerate(date_list, 1):
					if c < len(date_list):
						if value < date_list[c]:
							continue
						else:
							raise Warning('Sorry! Learning Programme start date should be greater than previous Learning programme end date.')

			if self.skills_programme_ids:
				date_list = []
				for skill_line in self.skills_programme_ids:
					if skill_line.start_date > skill_line.end_date:
						raise Warning(_("Sorry! Skills Programme Start Date should not be greater than Skills Programme End Date"))
					date_list.append(skill_line.start_date)
					date_list.append(skill_line.end_date)
				for c, value in enumerate(date_list, 1):
					if c < len(date_list):
						if value < date_list[c]:
							continue
						else:
							raise Warning('Sorry! Skills Programme start date should be greater than previous skills programme end date.')

			if self.learner_qualification_ids:
				date_list = []
				for qual_line in self.learner_qualification_ids:
					if qual_line.start_date > qual_line.end_date:
						raise Warning(_("Sorry! Qualification Start Date should not be greater than Qualification End Date"))
					date_list.append(qual_line.start_date)
					date_list.append(qual_line.end_date)
				for c, value in enumerate(date_list, 1):
					if c < len(date_list):
						if value < date_list[c]:
							continue
						else:
							raise Warning('Sorry! Qualifications start date should be greater than previous qualification end date')

			if self.learner_qualification_ids and self.skills_programme_ids:
				for qual_line in self.learner_qualification_ids:
					for skill_line in self.skills_programme_ids:
						if qual_line.start_date >= skill_line.start_date and qual_line.start_date <= skill_line.end_date:
							raise Warning(_("Sorry! Qualification start date should not be in the range of Skills Program start date and Skills Program end date"))
						if qual_line.end_date >= skill_line.start_date and qual_line.end_date <= skill_line.end_date:
							raise Warning(_("Sorry! Qualification end date should not be in the range of Skills Program start date and Skills Program end date"))
						if skill_line.start_date >= qual_line.start_date and skill_line.start_date <= qual_line.end_date:
							raise Warning(_("Sorry! Skills Program start date should not be in the range of Qualification start date and Qualification end date"))
						if skill_line.end_date >= qual_line.start_date and skill_line.end_date <= qual_line.end_date:
							raise Warning(_("Sorry! Skills Program end date should not be in the range of Qualification start date and Qualification end date"))

			if self.learner_qualification_ids and self.learning_programme_ids:
				for qual_line in self.learner_qualification_ids:
					for lp_line in self.learning_programme_ids:
						if qual_line.start_date >= lp_line.start_date and qual_line.start_date <= lp_line.end_date:
							raise Warning(_("Sorry! Qualification start date should not be in the range of Learning Program start date and Learning Program end date"))
						if qual_line.end_date >= lp_line.start_date and qual_line.end_date <= lp_line.end_date:
							raise Warning(_("Sorry! Qualification end date should not be in the range of Learning Program start date and Learning Program end date"))
						if lp_line.start_date >= qual_line.start_date and lp_line.start_date <= qual_line.end_date:
							raise Warning(_("Sorry! Learning Program start date should not be in the range of Qualification start date and Qualification end date"))
						if lp_line.end_date >= qual_line.start_date and lp_line.end_date <= qual_line.end_date:
							raise Warning(_("Sorry! Learning Program end date should not be in the range of Qualification start date and Qualification end date"))

			if self.skills_programme_ids and self.learning_programme_ids:
				for skill_line in self.skills_programme_ids:
					for lp_line in self.learning_programme_ids:
						if skill_line.start_date >= lp_line.start_date and skill_line.start_date <= lp_line.end_date:
							raise Warning(_("Sorry! Skills Programme start date should not be in the range of Learning Program start date and Learning Program end date"))
						if skill_line.end_date >= lp_line.start_date and skill_line.end_date <= lp_line.end_date:
							raise Warning(_("Sorry! Skills Programme end date should not be in the range of Learning Program start date and Learning Program end date"))
						if lp_line.start_date >= skill_line.start_date and lp_line.start_date <= skill_line.end_date:
							raise Warning(_("Sorry! Learning Program start date should not be in the range of Skills Programme start date and Learning Programme end date"))
						if lp_line.end_date >= skill_line.start_date and lp_line.end_date <= skill_line.end_date:
							raise Warning(_("Sorry! Learning Program end date should not be in the range of Skills Programme start date and Learning Programme end date"))

			self = self.with_context(submit=True)
			self.write({'financial_year':datetime.now()})
			self.write({'state':'approved', 'approved':True, 'final_state':'Approved'})
			self.write({'learner_status_ids':[(0, 0, {'learner_uid':self.env['res.users'].browse(self._uid).name, 'learner_date':datetime.now(), 'learner_status':'Approved', 'learner_comment':self.comment, 'learner_updation_date':self.write_date})]})
			self.write({'comment':'', 'enrollment_date':self.write_date})
			# code for approve entry in master
			employee_obj = self.env['hr.employee']
			if self.is_existing_learner == False:
				employee_id = employee_obj.create({
											  'name' : self.name,
											  # 'learner_reg_no':self.learner_reg_no,
											  'work_email' : self.work_email,
											  'work_phone' : self.work_phone,
											  'seta_elements':True,
											  'is_learner':True,
											  'work_address':self.work_address,
											  'work_address2':self.work_address2,
											  'work_address3':self.work_address3,
											  'person_suburb':self.person_suburb.id,
											  'work_municipality':self.work_municipality.id,
											  'work_city':self.work_city.id,
											  'work_province':self.work_province.id,
											  'work_zip':self.work_zip,
											  'work_country':self.work_country.id,
											  'department':self.department,
											  'job_title':self.job_title,
											  'manager':self.manager,
											  'user_id':self.user_id,
											  'notes':self.notes,
											  'person_title':self.person_title,
											  'person_name':self.person_name,
											  'person_last_name':self.person_last_name,
											  'initials':self.initials,
											  'maiden_name':self.maiden_name,
											  'person_middle_name':self.middle_name,
											  'cell':self.cell,
											  'gender_saqa_code':self.gender_saqa_code,
											  'person_fax_number':self.person_fax_number,
											  'highest_education':self.highest_education,
											  'current_occupation':self.current_occupation,
											  'years_in_occupation':self.years_in_occupation,
											  'method_of_communication':self.method_of_communication,
											  'last_updated_operator':self.last_updated_operator,
											  'status_effective_date':self.status_effective_date,
											  'citizen_resident_status_code':self.citizen_resident_status_code,
											  'country_id':self.country_id.id,
											  'learner_identification_id':self.identification_id,
											  'alternate_id_type':self.alternate_id_type,
											  'person_birth_date':self.person_birth_date,
											  'passport_id':self.passport_id,
											  'national_id':self.national_id,
											  'id_document':self.id_document.id,
											  'home_language_code':self.home_language_code.id,
											  'learner_status':'Enrolled',  # self.learner_status,
											  'certificate_no':self.certificate_no,
											  'record_last_update':self.record_last_update,
											  'status_comments':self.status_comments,
											  'highest_education':self.highest_education,
											  'wsp_year':self.wsp_year,
											  'gender':self.gender,
											  'marital':self.marital,
											  'dissability':self.dissability,
											  'status_reason':self.status_reason,
											  'socio_economic_saqa_code':self.socio_economic_saqa_code,
											  'is_sdf':self.is_sdf,
											  'equity':self.equity,
											  'equity_saqa_code':self.equity_saqa_code,
											  'socio_economic_status':self.socio_economic_status,
											  'disability_status':self.disability_status,
											  'disability_status_saqa':self.disability_status_saqa,
											  'person_home_address_1':self.person_home_address_1,
											  'person_home_address_2':self.person_home_address_2,
											  'person_home_address_3':self.person_home_address_3,
											  'person_home_suburb':self.person_home_suburb.id,
											  'physical_municipality':self.physical_municipality.id,
											  'person_home_city':self.person_home_city.id,
											  'person_home_province_code':self.person_home_province_code.id,
											  'person_home_zip':self.person_home_zip,
											  'country_home':self.country_home.id,
											  'same_as_home':self.same_as_home,
											  'person_postal_address_1':self.person_postal_address_1,
											  'person_postal_address_2':self.person_postal_address_2,
											  'person_postal_address_3':self.person_postal_address_3,
											  'person_postal_suburb':self.person_postal_suburb.id,
											  'postal_municipality':self.postal_municipality.id,
											  'person_postal_city':self.person_postal_city.id,
											  'person_postal_province_code':self.person_postal_province_code.id,
											  'person_postal_zip':self.person_postal_zip,
											  'country_postal':self.country_postal.id,
											  'seeing_rating_id':self.seeing_rating_id,
											  'hearing_rating_id':self.hearing_rating_id,
											  'walking_rating_id':self.walking_rating_id,
											  'remembering_rating_id':self.remembering_rating_id,
											  'statssa_area_code':self.statssa_area_code,
											  'popi_act_status_date':self.popi_act_status_date,
											  'communicating_rating_id':self.communicating_rating_id,
											  'self_care_rating_id':self.self_care_rating_id,
											  'last_school_emis_no':self.last_school_emis_no,
											  'last_school_year':self.last_school_year,
											  'popi_act_status_id':self.popi_act_status_id,
											  'date_stamp':self.date_stamp,
											  'provider_learner':True,
											  'enrollment_date':self.enrollment_date,
										 })
				for learner_qualification in self.learner_qualification_ids:
					learner_qualification.write({'learner_id':employee_id.id,'qual_status':'Enrolled'})

				for skill_line in self.skills_programme_ids:
					skill_line.write({'skills_programme_learner_rel_ids':employee_id.id,'skill_status':'Enrolled'})

				for lp_line in self.learning_programme_ids:
					lp_line.write({'learning_programme_learner_rel_ids':employee_id.id,'lp_status':'Enrolled'})

				for other_docs in self.learner_other_docs_ids:
					other_docs.write({'learner_master_id':employee_id.id})

			elif self.is_existing_learner == True:
				learner_data = ''
				if self.citizen_resident_status_code in ['dual', 'PR', 'sa']:
					learner_data = employee_obj.search([('learner_identification_id', '=', self.identification_id)])
				elif self.citizen_resident_status_code in ['other','unknown']:
					learner_data = employee_obj.search(['|',('national_id', '=', self.national_id),('passport_id','=',self.passport_id)])
				if not learner_data:
					raise Warning(_("This Learner does not exists in Learner Master, Please uncheck Existing Learner!"))
				max_end_date, max_skill_end_date, max_lp_end_date = None, None, None
				if learner_data.learner_qualification_ids:
					latest_end_date = []
					for qual_date_line in learner_data.learner_qualification_ids:
						latest_end_date.append(qual_date_line.end_date)
					max_end_date = max(latest_end_date)
					for qual_line in self.learner_qualification_ids:
						if qual_line.start_date <= max_end_date:
							raise Warning(_("This Learner is already enrolled for the same periods"))
				if learner_data.skills_programme_ids:
					latest_skill_end_date = []
					for skill_date_line in learner_data.skills_programme_ids:
						latest_skill_end_date.append(skill_date_line.end_date)
					max_skill_end_date = max(latest_skill_end_date)
					for skill_line in self.skills_programme_ids:
						if skill_line.start_date <= max_skill_end_date:
							raise Warning(_("This Learner is already enrolled for the same periods"))
				if learner_data.learning_programme_ids:
					latest_lp_end_date = []
					for lp_date_line in learner_data.learning_programme_ids:
						latest_lp_end_date.append(lp_date_line.end_date)
					max_lp_end_date = max(latest_lp_end_date)
					for lp_line in self.learning_programme_ids:
						if lp_line.start_date <= max_lp_end_date:
							raise Warning(_("This Learner is already enrolled for the same periods"))
				if max_end_date and max_skill_end_date and max_lp_end_date:
					if max_end_date < max_skill_end_date < max_lp_end_date:
						max_end_date = max_lp_end_date
					if max_end_date < max_lp_end_date < max_skill_end_date:
						max_end_date = max_skill_end_date
					for qual_line in self.learner_qualification_ids:
						if max_end_date > qual_line.start_date:
							raise Warning(_("This Learner is already enrolled for the same periods"))
					for skill_line in self.skills_programme_ids:
						if max_end_date > skill_line.start_date:
							raise Warning(_("This Learner is already enrolled for the same periods"))
					for lp_line in self.learning_programme_ids:
						if max_end_date > lp_line.start_date:
							raise Warning(_("This Learner is already enrolled for the same periods"))
				for learner_qualification in self.learner_qualification_ids:
					if not learner_qualification.start_date or not learner_qualification.end_date or not learner_qualification.batch_id:
						raise Warning(_("Please enter required fields of Qualifications before approve"))
					learner_qualification.write({'learner_id':learner_data.id,'qual_status':'Re-Enrolled'})
				for skill_line in self.skills_programme_ids:
					skill_line.write({'skills_programme_learner_rel_ids':learner_data.id,'skill_status':'Re-Enrolled'})
				for lp_line in self.learning_programme_ids:
					lp_line.write({'learning_programme_learner_rel_ids':learner_data.id,'lp_status':'Re-Enrolled'})
				learner_data.write({
											  'name' : self.name,
											  'work_email' : self.work_email,
											  'work_phone' : self.work_phone,
											  'seta_elements':True,
											  'is_learner':True,
											  'work_address':self.work_address,
											  'work_address2':self.work_address2,
											  'work_address3':self.work_address3,
											  'person_suburb':self.person_suburb.id,
											  'work_municipality':self.work_municipality.id,
											  'work_city':self.work_city.id,
											  'work_province':self.work_province.id,
											  'work_zip':self.work_zip,
											  'work_country':self.work_country.id,
											  'department':self.department,
											  'job_title':self.job_title,
											  'manager':self.manager,
											  'user_id':self.user_id,
											  'notes':self.notes,
											  'person_title':self.person_title,
											  'person_name':self.person_name,
											  'person_last_name':self.person_last_name,
											  'initials':self.initials,
											  'maiden_name':self.maiden_name,
											  'person_middle_name':self.middle_name,
											  'cell':self.cell,
											  'gender_saqa_code':self.gender_saqa_code,
											  'person_fax_number':self.person_fax_number,
											  'highest_education':self.highest_education,
											  'current_occupation':self.current_occupation,
											  'years_in_occupation':self.years_in_occupation,
											  'method_of_communication':self.method_of_communication,
											  'last_updated_operator':self.last_updated_operator,
											  'status_effective_date':self.status_effective_date,
											  'citizen_resident_status_code':self.citizen_resident_status_code,
											  'country_id':self.country_id.id,
											  'alternate_id_type':self.alternate_id_type,
											  'person_birth_date':self.person_birth_date,
											  'passport_id':self.passport_id,
											  'national_id':self.national_id,
											  'id_document':self.id_document.id,
											  'home_language_code':self.home_language_code.id,
											  'status_comments':self.status_comments,
											  'highest_education':self.highest_education,
											  'wsp_year':self.wsp_year,
											  'gender':self.gender,
											  'marital':self.marital,
											  'dissability':self.dissability,
											  'status_reason':self.status_reason,
											  'socio_economic_saqa_code':self.socio_economic_saqa_code,
											  'is_sdf':self.is_sdf,
											  'equity':self.equity,
											  'equity_saqa_code':self.equity_saqa_code,
											  'socio_economic_status':self.socio_economic_status,
											  'disability_status':self.disability_status,
											  'disability_status_saqa':self.disability_status_saqa,
											  'person_home_address_1':self.person_home_address_1,
											  'person_home_address_2':self.person_home_address_2,
											  'person_home_address_3':self.person_home_address_3,
											  'person_home_suburb':self.person_home_suburb.id,
											  'physical_municipality':self.physical_municipality.id,
											  'person_home_city':self.person_home_city.id,
											  'person_home_province_code':self.person_home_province_code.id,
											  'person_home_zip':self.person_home_zip,
											  'country_home':self.country_home.id,
											  'same_as_home':self.same_as_home,
											  'person_postal_address_1':self.person_postal_address_1,
											  'person_postal_address_2':self.person_postal_address_2,
											  'person_postal_address_3':self.person_postal_address_3,
											  'person_postal_suburb':self.person_postal_suburb.id,
											  'postal_municipality':self.postal_municipality.id,
											  'person_postal_city':self.person_postal_city.id,
											  'person_postal_province_code':self.person_postal_province_code.id,
											  'person_postal_zip':self.person_postal_zip,
											  'country_postal':self.country_postal.id,
											  'seeing_rating_id':self.seeing_rating_id,
											  'hearing_rating_id':self.hearing_rating_id,
											  'walking_rating_id':self.walking_rating_id,
											  'remembering_rating_id':self.remembering_rating_id,
											  'statssa_area_code':self.statssa_area_code,
											  'popi_act_status_date':self.popi_act_status_date,
											  'communicating_rating_id':self.communicating_rating_id,
											  'self_care_rating_id':self.self_care_rating_id,
											  'last_school_emis_no':self.last_school_emis_no,
											  'last_school_year':self.last_school_year,
											  'popi_act_status_id':self.popi_act_status_id,
											  'date_stamp':self.date_stamp,
											  'enrollment_date':self.enrollment_date,
										 })
				learner_data.write({'enrollment_date':self.enrollment_date,'learner_status':'Re-Enrolled','learners_status':'re-enrolled','state':'re-enrolled'})
			return self.write({'state':'approved', 'approved':True})
		except Exception, e:
			if self._context.get('by_multi'):
				return self.identification_id
			else:
				raise Warning(_(e))
		return True

	@api.multi
	def action_update_button(self):
		learner_data = ''
		employee_obj = self.env['hr.employee']
		if self.citizen_resident_status_code in ['dual', 'PR', 'sa']:
			learner_data = employee_obj.search([('learner_identification_id', '=', self.identification_id),('provider_learner', '=', True)])
		elif self.citizen_resident_status_code in ['other','unknown']:
			learner_data = employee_obj.search(['|',('national_id', '=', self.national_id),('passport_id','=',self.passport_id),('provider_learner', '=', True)])
		if not learner_data:
			raise Warning(_("This Learner does not exists in Learner Master!"))
		learner_data.write({
							  'name' : self.name,
							  'work_email' : self.work_email,
							  'work_phone' : self.work_phone,
							  'seta_elements':True,
							  'is_learner':True,
							  'work_address':self.work_address,
							  'work_address2':self.work_address2,
							  'work_address3':self.work_address3,
							  'person_suburb':self.person_suburb.id,
							  'work_municipality':self.work_municipality.id,
							  'work_city':self.work_city.id,
							  'work_province':self.work_province.id,
							  'work_zip':self.work_zip,
							  'work_country':self.work_country.id,
							  'department':self.department,
							  'job_title':self.job_title,
							  'manager':self.manager,
							  'user_id':self.user_id,
							  'notes':self.notes,
							  'person_title':self.person_title,
							  'person_name':self.person_name,
							  'person_last_name':self.person_last_name,
							  'initials':self.initials,
							  'maiden_name':self.maiden_name,
							  'person_middle_name':self.middle_name,
							  'cell':self.cell,
							  'gender_saqa_code':self.gender_saqa_code,
							  'person_fax_number':self.person_fax_number,
							  'highest_education':self.highest_education,
							  'current_occupation':self.current_occupation,
							  'years_in_occupation':self.years_in_occupation,
							  'method_of_communication':self.method_of_communication,
							  'last_updated_operator':self.last_updated_operator,
							  'status_effective_date':self.status_effective_date,
							  'citizen_resident_status_code':self.citizen_resident_status_code,
							  'country_id':self.country_id.id,
							  'alternate_id_type':self.alternate_id_type,
							  'person_birth_date':self.person_birth_date,
							  'passport_id':self.passport_id,
							  'national_id':self.national_id,
							  'id_document':self.id_document.id,
							  'home_language_code':self.home_language_code.id,
							  'status_comments':self.status_comments,
							  'highest_education':self.highest_education,
							  'wsp_year':self.wsp_year,
							  'gender':self.gender,
							  'marital':self.marital,
							  'dissability':self.dissability,
							  'status_reason':self.status_reason,
							  'socio_economic_saqa_code':self.socio_economic_saqa_code,
							  'is_sdf':self.is_sdf,
							  'equity':self.equity,
							  'equity_saqa_code':self.equity_saqa_code,
							  'socio_economic_status':self.socio_economic_status,
							  'disability_status':self.disability_status,
							  'disability_status_saqa':self.disability_status_saqa,
							  'person_home_address_1':self.person_home_address_1,
							  'person_home_address_2':self.person_home_address_2,
							  'person_home_address_3':self.person_home_address_3,
							  'person_home_suburb':self.person_home_suburb.id,
							  'physical_municipality':self.physical_municipality.id,
							  'person_home_city':self.person_home_city.id,
							  'person_home_province_code':self.person_home_province_code.id,
							  'person_home_zip':self.person_home_zip,
							  'country_home':self.country_home.id,
							  'same_as_home':self.same_as_home,
							  'person_postal_address_1':self.person_postal_address_1,
							  'person_postal_address_2':self.person_postal_address_2,
							  'person_postal_address_3':self.person_postal_address_3,
							  'person_postal_suburb':self.person_postal_suburb.id,
							  'postal_municipality':self.postal_municipality.id,
							  'person_postal_city':self.person_postal_city.id,
							  'person_postal_province_code':self.person_postal_province_code.id,
							  'person_postal_zip':self.person_postal_zip,
							  'country_postal':self.country_postal.id,
							  'seeing_rating_id':self.seeing_rating_id,
							  'hearing_rating_id':self.hearing_rating_id,
							  'walking_rating_id':self.walking_rating_id,
							  'remembering_rating_id':self.remembering_rating_id,
							  'statssa_area_code':self.statssa_area_code,
							  'popi_act_status_date':self.popi_act_status_date,
							  'communicating_rating_id':self.communicating_rating_id,
							  'self_care_rating_id':self.self_care_rating_id,
							  'last_school_emis_no':self.last_school_emis_no,
							  'last_school_year':self.last_school_year,
							  'popi_act_status_id':self.popi_act_status_id,
							  'date_stamp':self.date_stamp,
							  'enrollment_date':self.enrollment_date,
						})
		for other_docs in self.learner_other_docs_ids:
			other_docs.write({'learner_master_id':learner_data.id})
		return True


	@api.model
	def approve_learners(self):
		str_name = ''
		lst_approve = []
		non_approve = []
		context = dict(self.env.context or {})
		search_id = self.search([('id', 'in', self._context.get('active_ids')),('state','=','draft')])
		for record in search_id:
			ids = record.with_context({'by_multi':True}).action_approved_button()
			if ids != True:
				non_approve.append(record.identification_id)
				str_name = str_name + ids + '\n'
			else:
				lst_approve.append(record.identification_id)
		context['approve_ids'] = lst_approve
		context['non_apr_ids'] = non_approve
		if lst_approve or non_approve:
			str_name = str_name + 'Please check all the validations one by one!!!'
			context['error_log'] = '**********Not Approved Learners SA Identification Numbers**********' + '\n' + str_name

			return {
				'name': _('Learners Approval Log'),
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'approve.learner.wizard',
				'view_id': self.env.ref('hwseta_etqe.approve_learner_wizard_id').id,
				'type': 'ir.actions.act_window',
				'res_id': self.env.context.get('id'),
				'context': context,
				'target': 'new'
			}


	@api.multi
	def action_rejected_button(self):
		self = self.with_context(submit=True)
		self.write({'state':'rejected', 'rejected':True, 'final_state':'Rejected'})
		self.write({'learner_status_ids':[(0, 0, {'learner_uid':self.env['res.users'].browse(self._uid).name, 'learner_date':datetime.now(), 'learner_status':'Rejected', 'learner_comment':self.comment, 'learner_updation_date':self.write_date})]})
		self.write({'comment':''})
		return True

	@api.multi
	def action_set_to_draft_button(self):
#       self.write({'state':'draft', 'evaluated':False, 'rejected':False})
		self.write({'state':'draft', 'rejected':False})
		self.write({'learner_status_ids':[(0, 0, {'learner_uid':self.env['res.users'].browse(self._uid).name, 'learner_date':datetime.now(), 'learner_status':'Set To Draft', 'learner_comment':self.comment, 'learner_updation_date':self.write_date})]})
		self.write({'comment':''})
		return True

	@api.multi
	def onchange_work_province(self, province):
		if province:
			country_id = self.country_for_province(province)
			return {'value': {'work_country': country_id }}
		return {}

	@api.multi
	def onchange_postal_province(self, province):
		if province:
			country_id = self.country_for_province(province)
			return {'value': {'country_postal': country_id }}
		return {}

	@api.multi
	def onchange_home_province(self, province):
		if province:
			country_id = self.country_for_province(province)
			return {'value': {'country_home': country_id }}
		return {}

	@api.multi
	def country_for_province(self, province):
		state = self.env['res.country.state'].browse(province)
		return state.country_id.id

	@api.multi
	def onchange_crc(self, citizen_resident_status_code):
		res = {}
		if not citizen_resident_status_code:
			return res
		if citizen_resident_status_code == 'sa':
			country_data = self.env['res.country'].search(['|', ('code', '=', 'ZA'), ('name', '=', 'South Africa')], limit=1)
			res.update({'value':{'country_id':country_data and country_data.id}})
		else:
			res.update({'value':{'country_id':None and None}})
		return res

	@api.model
	def create(self, vals):
		res = super(learner_registration, self).create(vals)
#         if not res.learner_qualification_ids and not res.skills_programme_ids :
#             raise Warning(_('Please add at least one Qualification or Skills Program'))
		if res.work_email:
			if '@' not in res.work_email:
				raise Warning(_('Please enter valid email address'))
		if res.work_phone:
			if not res.work_phone.isdigit() or len(res.work_phone) != 10:
				raise Warning(_('Please enter 10 digits Phone number'))
		if res.cell:
			if not res.cell.isdigit() or len(res.cell) != 10:
				raise Warning(_('Please enter 10 digits Mobile number'))
		if res.person_fax_number:
			if not res.person_fax_number.isdigit() or len(res.person_fax_number) != 10:
				raise Warning(_('Please enter 10 digits Fax number'))
		if res.years_in_occupation:
			if not res.years_in_occupation.isdigit() or len(res.years_in_occupation) > 2:
				raise Warning(_('Please enter valid years in occupation'))
		if res.is_existing_learner == True:
			for line in res.learner_qualification_ids:
				if not line.learner_registration_line_ids:
					raise Warning(_("Each Qualification should have at least one unit standard!!"))
		if res.is_existing_learner == False:
			for line in res.learner_qualification_ids:
				if line.learner_qualification_parent_id.is_exit_level_outcomes == False:
					if line.minimum_credits > line.total_credits:
						raise Warning(_("Sum of checked unit standards credits point should be greater than or equal to Minimum credits point !!"))

		if res.learning_programme_ids:
			date_list = []
			for lp_line in res.learning_programme_ids:
				if lp_line.start_date > lp_line.end_date:
					raise Warning(_("Sorry! Learning Programme Start Date should not be greater than Learning Programme End Date"))
				date_list.append(lp_line.start_date)
				date_list.append(lp_line.end_date)
			for c, value in enumerate(date_list, 1):
				if c < len(date_list):
					if value < date_list[c]:
						continue
					else:
						raise Warning('Sorry! Learning Programme start date should be greater than previous learning programme end date.')

		if res.skills_programme_ids:
			date_list = []
			for skill_line in res.skills_programme_ids:
				if skill_line.start_date > skill_line.end_date:
					raise Warning(_("Sorry! Skills Programme Start Date should not be greater than Skills Programme End Date"))
				date_list.append(skill_line.start_date)
				date_list.append(skill_line.end_date)
			for c, value in enumerate(date_list, 1):
				if c < len(date_list):
					if value < date_list[c]:
						continue
					else:
						raise Warning('Sorry! Skills Programme start date should be greater than previous skills programme end date.')

		if res.learner_qualification_ids:
			date_list = []
			for qual_line in res.learner_qualification_ids:
				if qual_line.start_date > qual_line.end_date:
					raise Warning(_("Sorry! Qualification Start Date should not be greater than Qualification End Date"))
				date_list.append(qual_line.start_date)
				date_list.append(qual_line.end_date)
			for c, value in enumerate(date_list, 1):
				if c < len(date_list):
					if value < date_list[c]:
						continue
					else:
						raise Warning('Sorry! Qualifications start date should be greater than previous qualification end date')

		if res.learner_qualification_ids and res.skills_programme_ids:
			for quali_line in res.learner_qualification_ids:
				for skill_line in res.skills_programme_ids:
					if quali_line.start_date >= skill_line.start_date and quali_line.start_date <= skill_line.end_date:
						raise Warning(_("Sorry! Qualification start date should not be in the range of Skills Program start date and Skills Program end date"))
					if quali_line.end_date >= skill_line.start_date and quali_line.end_date <= skill_line.end_date:
						raise Warning(_("Sorry! Qualification end date should not be in the range of Skills Program start date and Skills Program end date"))
					if skill_line.start_date >= quali_line.start_date and skill_line.start_date <= quali_line.end_date:
						raise Warning(_("Sorry! Skills Program start date should not be in the range of Qualification start date and Qualification end date"))
					if skill_line.end_date >= quali_line.start_date and skill_line.end_date <= quali_line.end_date:
						raise Warning(_("Sorry! Skills Program end date should not be in the range of Qualification start date and Qualification end date"))

		if res.learner_qualification_ids and res.learning_programme_ids:
			for qual_line in res.learner_qualification_ids:
				for lp_line in res.learning_programme_ids:
					if qual_line.start_date >= lp_line.start_date and qual_line.start_date <= lp_line.end_date:
						raise Warning(_("Sorry! Qualification start date should not be in the range of Learning Program start date and Learning Program end date"))
					if qual_line.end_date >= lp_line.start_date and qual_line.end_date <= lp_line.end_date:
						raise Warning(_("Sorry! Qualification end date should not be in the range of Learning Program start date and Learning Program end date"))
					if lp_line.start_date >= qual_line.start_date and lp_line.start_date <= qual_line.end_date:
						raise Warning(_("Sorry! Learning Program start date should not be in the range of Qualification start date and Qualification end date"))
					if lp_line.end_date >= qual_line.start_date and lp_line.end_date <= qual_line.end_date:
						raise Warning(_("Sorry! Learning Program end date should not be in the range of Qualification start date and Qualification end date"))

		if res.skills_programme_ids and res.learning_programme_ids:
			for skill_line in res.skills_programme_ids:
				for lp_line in res.learning_programme_ids:
					if skill_line.start_date >= lp_line.start_date and skill_line.start_date <= lp_line.end_date:
						raise Warning(_("Sorry! Skills Programme start date should not be in the range of Learning Program start date and Learning Program end date"))
					if skill_line.end_date >= lp_line.start_date and skill_line.end_date <= lp_line.end_date:
						raise Warning(_("Sorry! Skills Programme end date should not be in the range of Learning Program start date and Learning Program end date"))
					if lp_line.start_date >= skill_line.start_date and lp_line.start_date <= skill_line.end_date:
						raise Warning(_("Sorry! Learning Program start date should not be in the range of Skills Programme start date and Learning Programme end date"))
					if lp_line.end_date >= skill_line.start_date and lp_line.end_date <= skill_line.end_date:
						raise Warning(_("Sorry! Learning Program end date should not be in the range of Skills Programme start date and Learning Programme end date"))
		return res

	@api.multi
	def write(self, vals):

		context = self._context
		if context is None:
			context = {}
		res = super(learner_registration, self).write(vals)
#         if not self.learner_qualification_ids and not self.skills_programme_ids :
#             raise Warning(_('Please add at least one Qualification or Skills Program'))
		if self.work_phone:
			if not self.work_phone.isdigit() or len(self.work_phone) != 10:
				raise Warning(_('Please enter 10 digits Phone number'))
		if self.cell:
			if not self.cell.isdigit() or len(self.cell) != 10:
				raise Warning(_('Please enter 10 digits Mobile number'))
		if self.person_fax_number:
			if not self.person_fax_number.isdigit() or len(self.person_fax_number) != 10:
				raise Warning(_('Please enter 10 digits Fax number'))
		if self.years_in_occupation:
			if not self.years_in_occupation.isdigit() or len(self.years_in_occupation) > 2:
				raise Warning(_('Please enter valid years in occupation'))
		if self.is_existing_learner == True:
			for line in self.learner_qualification_ids:
				if not line.learner_registration_line_ids:
					raise Warning(_("Each Qualification should have at least one unit standard!!"))
		if self.state == "approved" and self.approved == False:
			raise Warning(_('Sorry! you can not change state to Approved'))

		if self.state == "rejected" and self.rejected == False:
			raise Warning(_('Sorry! you can not change state to Rejected'))

		if self.state == "draft" and self.approved == True:
			raise Warning(_('Sorry! you can not approve again'))
		if self.is_existing_learner == False:
			for line in self.learner_qualification_ids:
				if line.learner_qualification_parent_id.is_exit_level_outcomes == False:
					if line.minimum_credits > line.total_credits:
						raise Warning(_("Sum of checked unit standards credits point should be greater than or equal to Minimum credits point !!"))

		if self.learning_programme_ids:
			date_list = []
			for lp_line in self.learning_programme_ids:
				if lp_line.start_date > lp_line.end_date:
					raise Warning(_("Sorry! Learning Programme Start Date should not be greater than Learning Programme End Date"))
				date_list.append(lp_line.start_date)
				date_list.append(lp_line.end_date)
			for c, value in enumerate(date_list, 1):
				if c < len(date_list):
					if value < date_list[c]:
						continue
					else:
						raise Warning('Sorry! Learning Programme start date should be greater than previous Learning programme end date.')

		if self.skills_programme_ids:
			date_list = []
			for skill_line in self.skills_programme_ids:
				if skill_line.start_date > skill_line.end_date:
					raise Warning(_("Sorry! Skills Programme Start Date should not be greater than Skills Programme End Date"))
				date_list.append(skill_line.start_date)
				date_list.append(skill_line.end_date)
			for c, value in enumerate(date_list, 1):
				if c < len(date_list):
					if value < date_list[c]:
						continue
					else:
						raise Warning('Sorry! Skills Programme start date should be greater than previous skills programme end date.')

		if self.learner_qualification_ids:
			date_list = []
			for qual_line in self.learner_qualification_ids:
				if qual_line.start_date > qual_line.end_date:
					raise Warning(_("Sorry! Qualification Start Date should not be greater than Qualification End Date"))
				date_list.append(qual_line.start_date)
				date_list.append(qual_line.end_date)
			for c, value in enumerate(date_list, 1):
				if c < len(date_list):
					if value < date_list[c]:
						continue
					else:
						raise Warning('Sorry! Qualifications start date should be greater than previous qualification end date')

		if self.learner_qualification_ids and self.skills_programme_ids:
			for qual_line in self.learner_qualification_ids:
				for skill_line in self.skills_programme_ids:
					if qual_line.start_date >= skill_line.start_date and qual_line.start_date <= skill_line.end_date:
						raise Warning(_("Sorry! Qualification start date should not be in the range of Skills Program start date and Skills Program end date"))
					if qual_line.end_date >= skill_line.start_date and qual_line.end_date <= skill_line.end_date:
						raise Warning(_("Sorry! Qualification end date should not be in the range of Skills Program start date and Skills Program end date"))
					if skill_line.start_date >= qual_line.start_date and skill_line.start_date <= qual_line.end_date:
						raise Warning(_("Sorry! Skills Program start date should not be in the range of Qualification start date and Qualification end date"))
					if skill_line.end_date >= qual_line.start_date and skill_line.end_date <= qual_line.end_date:
						raise Warning(_("Sorry! Skills Program end date should not be in the range of Qualification start date and Qualification end date"))

		if self.learner_qualification_ids and self.learning_programme_ids:
			for qual_line in self.learner_qualification_ids:
				for lp_line in self.learning_programme_ids:
					if qual_line.start_date >= lp_line.start_date and qual_line.start_date <= lp_line.end_date:
						raise Warning(_("Sorry! Qualification start date should not be in the range of Learning Program start date and Learning Program end date"))
					if qual_line.end_date >= lp_line.start_date and qual_line.end_date <= lp_line.end_date:
						raise Warning(_("Sorry! Qualification end date should not be in the range of Learning Program start date and Learning Program end date"))
					if lp_line.start_date >= qual_line.start_date and lp_line.start_date <= qual_line.end_date:
						raise Warning(_("Sorry! Learning Program start date should not be in the range of Qualification start date and Qualification end date"))
					if lp_line.end_date >= qual_line.start_date and lp_line.end_date <= qual_line.end_date:
						raise Warning(_("Sorry! Learning Program end date should not be in the range of Qualification start date and Qualification end date"))

		if self.skills_programme_ids and self.learning_programme_ids:
			for skill_line in self.skills_programme_ids:
				for lp_line in self.learning_programme_ids:
					if skill_line.start_date >= lp_line.start_date and skill_line.start_date <= lp_line.end_date:
						raise Warning(_("Sorry! Skills Programme start date should not be in the range of Learning Program start date and Learning Program end date"))
					if skill_line.end_date >= lp_line.start_date and skill_line.end_date <= lp_line.end_date:
						raise Warning(_("Sorry! Skills Programme end date should not be in the range of Learning Program start date and Learning Program end date"))
					if lp_line.start_date >= skill_line.start_date and lp_line.start_date <= skill_line.end_date:
						raise Warning(_("Sorry! Learning Program start date should not be in the range of Skills Programme start date and Learning Programme end date"))
					if lp_line.end_date >= skill_line.start_date and lp_line.end_date <= skill_line.end_date:
						raise Warning(_("Sorry! Learning Program end date should not be in the range of Skills Programme start date and Learning Programme end date"))
		return res

	@api.multi
	def unlink(self):
		raise Warning(_("Sorry!! You cannot delete record !"))
		return super(learner_registration, self).unlink()

	@api.multi
	def copy(self):
		''' Inherited to avoid duplicating records '''
		raise Warning(_('Sorry! You cannot create duplicate record'))
		return super(learner_registration, self).copy()
learner_registration()

class learner_timetable_period (models.Model):
	_name = 'learner.timetable.period'
	_description = 'Learner Timetable Period'
#     name = fields.Char(string='Name', required=True)
	standard = fields.Many2one("provider.qualification", 'Standard', ondelete='restrict' , required=True)
	subject = fields.Many2one("provider.qualification.line", 'Subject', ondelete='restrict', required=True)
	hours = fields.Selection([('1', '1'),
							   ('2', '2'),
							   ('3', '3'),
							   ('4', '4'),
							   ('5', '5'),
							   ('6', '6'),
							   ('7', '7'),
							   ('8', '8'),
							   ('9', '9'),
							   ('10', '10'),
							   ('11', '11'),
							   ('12', '12')],
							  string='Hours', required=True)
	minute = fields.Selection([('00', '00'),
							   ('01', '01'),
							   ('02', '02'),
							   ('03', '03'),
							   ('04', '04'),
							   ('05', '05'),
							   ('06', '06'),
							   ('07', '07'),
							   ('08', '08'),
							   ('09', '09'),
							   ('10', '10'),
							   ('11', '11'),
							   ('12', '12'),
							   ('13', '13'),
							   ('14', '14'),
							   ('15', '15'),
							   ('16', '16'),
							   ('17', '17'),
							   ('18', '18'),
							   ('19', '19'),
							   ('20', '20'),
							   ('21', '21'),
							   ('22', '22'),
							   ('23', '23'),
							   ('24', '24'),
							   ('25', '25'),
							   ('26', '26'),
							   ('27', '27'),
							   ('28', '28'),
							   ('29', '29'),
							   ('30', '30'),
							   ('31', '31'),
							   ('32', '32'),
							   ('33', '33'),
							   ('34', '34'),
							   ('35', '35'),
							   ('36', '36'),
							   ('37', '37'),
							   ('38', '38'),
							   ('39', '39'),
							   ('40', '40'),
							   ('41', '41'),
							   ('42', '42'),
							   ('43', '43'),
							   ('44', '44'),
							   ('45', '45'),
							   ('46', '46'),
							   ('47', '47'),
							   ('48', '48'),
							   ('49', '49'),
							   ('50', '50'),
							   ('51', '51'),
							   ('52', '52'),
							   ('53', '53'),
							   ('54', '54'),
							   ('55', '55'),
							   ('56', '56'),
							   ('57', '57'),
							   ('58', '58'),
							   ('59', '59'),
							   ('60', '60')],
							  string='Minute', required=True)
	am_pm = fields.Selection([('am', 'AM'),
							   ('pm', 'PM')],
							  string='AM/PM', required=True)
	duration = fields.Float(string='Duration')
	sequence = fields.Integer(string='Sequence')
	learner_timetable_id = fields.Many2one("learner.timetable", 'TimeTable', ondelete='restrict')
learner_timetable_period()

class learner_timetable(models.Model):
	_name = 'learner.timetable'
	_description = 'Learner Timetable'

	name = fields.Char(string='Name', required=True)
	faculty = fields.Char(string='Faculty')
#     standard = fields.Many2one("provider.qualification", 'Standard', ondelete='restrict' , required=True)
	division = fields.Char(string='Division')
#     period = fields.Many2one("lerner.timetable.period", 'Period',  ondelete='restrict' , required=True)
#     subject = fields.Many2one("provider.qualification.line", 'Subject',  ondelete='restrict', required=True)
	start = fields.Date(string='Start', required=True)
	end = fields.Date(string='End', required=True)
	days = fields.Selection([('monday', 'Monday'),
							   ('tuesday', 'Tuesday'),
							   ('wednesday', 'Wednesday'),
							   ('thursday', 'Thursday'),
							   ('friday', 'Friday'),
							   ('saturday', 'Saturday')],
							  string='Days',)
	peroid_ids = fields.One2many('learner.timetable.period', 'learner_timetable_id', string='Period')
#     provider_id = fields.Many2one('res.partner', string="Provider", track_visibility='onchange', default=lambda self:self.env.user.partner_id.id)
learner_timetable()

class learner_qualification(models.Model):
	_name = 'learner.qualification'

	name = fields.Char(string='Name')
	originator = fields.Char(string='Originator')
	qab = fields.Char(string='Quality Assurance Body')
	rs_date = fields.Date(string='Registration Start Date')
	re_date = fields.Date(string='Registration End Date')
	learner_id = fields.Many2one('hr.employee', string='Learner')
	state = fields.Selection([('new', 'New'), ('done', 'Done')], string="Status")
learner_qualification()

class learner_qualification_line(models.Model):
	_name = 'learner.qualification.line'

	name = fields.Char(string='Name', required=True)
	id_no = fields.Char(string='ID NO')
	title = fields.Char(string='UNIT STANDARD TITLE')
	level3 = fields.Char(string='CREDITS')
#     line_id = fields.Many2one('provider.qualification', 'Order Reference', required=True, ondelete='cascade')
#     qual_line_id = fields.Many2one('learner.qualification', 'Qualification', required=True, ondelete='cascade')
	learner_id = fields.Many2one('hr.employee', string='Learner')
	state = fields.Selection([('new', 'New'), ('done', 'Done')], string="status")
learner_qualification_line()

class learner_assessment(models.Model):
	_name = 'learner.assessment'

	name = fields.Char(string='Name')
	assessors_id = fields.Many2one("hr.employee", 'Assessors', domain=[('is_assessors', '=', True)])
	moderators_id = fields.Many2one("hr.employee", 'Moderator', domain=[('is_moderators', '=', True)])
	pro_learner_id = fields.Many2one('hr.employee', string='Learner')
	status = fields.Selection([('new', 'New'), ('done', 'Done')], string='Status')
learner_assessment()

class learner_provider_rel(models.Model):
	_name = 'learner.provider.rel'

	name = fields.Char(string='Name')
	provider_id = fields.Many2one('res.partner', string='Provider', domain=[('provider', '=', True)])
	provider_accreditation_num = fields.Char(string='Provider Accreditation Number')
	provider_etqe_id = fields.Char(string='Provider ETQE ID')
	assess_pro_id = fields.Many2one('hr.employee', string='Assessment')
	state = fields.Selection([('new', 'New'), ('done', 'Done')], string="status")
learner_provider_rel()

class hr_employee(models.Model):
	_inherit = 'hr.employee'

	@api.v7
	def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
		res = models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
		if view_type == 'form':
			doc = etree.XML(res['arch'])
			for sheet in doc.xpath("//sheet"):
				parent = sheet.getparent()
				index = parent.index(sheet)
				for child in sheet:
					parent.insert(index, child)
					index += 1
				parent.remove(sheet)
			res['arch'] = etree.tostring(doc)
		return res

	@api.v7
	def deactivate_assessors(self, cr, uid, context=None):
		'''Method to deactivate assessors if it's end date is expired'''
		today = datetime.today().date()
		assessors_obj = self.pool.get('hr.employee')
		exp_assessor_lst = assessors_obj.search(cr, uid, [('is_active_assessor', '=', True),('is_assessors', '=', True), ('end_date', '<', today)])
		exp_assessor_obj = assessors_obj.browse(cr, uid, exp_assessor_lst)
		if exp_assessor_obj:
			for obj in exp_assessor_obj:
				obj.is_active_assessor = False
		return True

	@api.v7
	def deactivate_moderators(self, cr, uid, context=None):
		'''Method to deactivate moderators if it's end date is expired'''
		today = datetime.today().date()
		moderators_obj = self.pool.get('hr.employee')
		exp_moderator_lst = moderators_obj.search(cr, uid, [('is_active_moderator', '=', True),('is_moderators', '=', True), ('moderator_end_date', '<', today)])
		exp_moderator_obj = moderators_obj.browse(cr, uid, exp_moderator_lst)
		if exp_moderator_obj:
			for obj in exp_moderator_obj:
				obj.is_active_moderator = False
		return True

	@api.multi
	@api.depends('name', 'person_last_name')
	def name_get(self):
		res = []
		if self._context.get('is_learner_from_assessment', False):
			for record in self:
				rec_str = ''
				if record.name:
					rec_str += record.name + ' '
				if record.person_last_name:
					rec_str += record.person_last_name
				res.append((record.id, rec_str))
		else:
			for record in self:
				res.append((record.id, record.name))
		return res

	@api.model
	def name_search(self, name='', args=[], operator='ilike', limit=1000):
		args += ['|', ('name', operator, name), ('person_last_name', operator, name)]
		cuur_ids = self.search(args, limit=limit)
		return cuur_ids.name_get()

	@api.model
	def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
		""" Override read_group to filter learner master's status count based on logged provider """
		if self.env.user.id != 1 and self.env.user.partner_id.provider == True:
#             domain.append(['logged_provider_id','=',self.env.user.partner_id.id])
			learners = self.env['learner.registration.qualification'].search([('provider_id', '=', self.env.user.partner_id.id)])
			learner_ids = [learner.learner_id.id for learner in learners]
			skill_learners = self.env['skills.programme.learner.rel'].search(['|',('provider_id', '=', self.env.user.partner_id.id),('create_uid', '=', self.env.user.id)])
			skills_learner_ids = [s_learner.skills_programme_learner_rel_ids.id for s_learner in skill_learners]
			learner_ids.extend(skills_learner_ids)
			lp_learners = self.env['learning.programme.learner.rel'].search(['|',('provider_id', '=', self.env.user.partner_id.id),('create_uid', '=', self.env.user.id)])
			lp_learner_ids = [l_learner.learning_programme_learner_rel_ids.id for l_learner in lp_learners]
			learner_ids.extend(lp_learner_ids)
			domain.append(['id', 'in', learner_ids])

		""" Override read_group to add Label for boolean field status """
		ret_val = super(hr_employee, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
		for rt in ret_val:
			if rt.has_key('is_active_assessor') :
				if rt.get('is_active_assessor', False):
					rt['is_active_assessor'] = 'Active'
				else:
					rt['is_active_assessor'] = 'In Active'
			if rt.has_key('is_active_moderator'):
				if rt.get('is_active_moderator', False):
					rt['is_active_moderator'] = 'Active'
				else:
					rt['is_active_moderator'] = 'In Active'
		return ret_val

	@api.model
	def _search(self, args, offset=0, limit=80, order=None, count=False, access_rights_uid=None):
		user = self._uid
		context = self._context
		user_obj = self.env['res.users']
		user_data = user_obj.browse(user)
		user_groups = user_data.groups_id
		for group in user_groups:
			if group.name in ['ETQE Manager', 'ETQE Executive Manager', 'ETQE Provincial Manager', 'ETQE Officer', 'ETQE Provincial Officer', 'ETQE Administrator', 'ETQE Provincial Administrator', 'Applicant Skills Development Provider', 'CEO']:
				return super(hr_employee, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
			if group.name == "SDP Manager":
				return super(hr_employee, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
			if group.name in ['Financial Manager', 'Accountant', 'Invoicing & Payments']:
				return super(hr_employee, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		if user == 1 :
			return super(hr_employee, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		if user_data.partner_id.employer:
			sdf_employers = self.env['sdf.employer.rel'].search([('employer_id', '=', user_data.partner_id.id)])
			sdf_empl_ids = [sdf_empl_data.id for sdf_empl_data in sdf_employers]
			args.append(('employer_ids', 'in', sdf_empl_ids))
			return super(hr_employee, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		if 'default_provider_learner' in context :
			learner_ids = []
			learners = self.env['learner.registration.qualification'].search([('provider_id', '=', user_data.partner_id.id)])
			learner_ids = [learner.learner_id.id for learner in learners]
			skill_learners = self.env['skills.programme.learner.rel'].search(['|',('provider_id', '=', user_data.partner_id.id),('create_uid', '=', user_data.id)])
			skills_learner_ids = [s_learner.skills_programme_learner_rel_ids.id for s_learner in skill_learners]
			learner_ids.extend(skills_learner_ids)
			lp_learners = self.env['learning.programme.learner.rel'].search(['|',('provider_id', '=', user_data.partner_id.id),('create_uid', '=', user_data.id)])
			lp_learner_ids = [l_learner.learning_programme_learner_rel_ids.id for l_learner in lp_learners]
			learner_ids.extend(lp_learner_ids)
			args.append(('id', 'in', learner_ids))
			return super(hr_employee, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
#         if user_data.partner_id.provider:
#             learners = self.env['learner.registration.qualification'].search([('provider_id','=',user_data.partner_id.id)])
#             learner_ids = [learner.learner_id.id for learner in learners]
#             args.append(('id','in',learner_ids))
#             return super(hr_employee, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		if 'default_is_sdf' in context:
			args.append(('id', '=', user_data.sdf_id.id))
			return super(hr_employee, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		if 'default_is_assessment' in context:
			return super(hr_employee, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		if 'default_is_moderators' in context:
#             self._cr.execute("select id from hr_employee where moderator_seq_no='%s'"%(user_data.assessor_moderator_id.moderator_seq_no,))
#             moderator_ids = map(lambda x:x[0], self._cr.fetchall())
#             print "--------moderator_ids--------",moderator_ids
#             args.append(('id', 'in', moderator_ids))
#             args.append(('user_id', '=', user))
			self._cr.execute("select id from hr_employee where assessor_seq_no='%s'" % (user_data.assessor_moderator_id.assessor_seq_no,))
			assessor_ids = map(lambda x:x[0], self._cr.fetchall())
			args.append(('id', 'in', assessor_ids))
			return super(hr_employee, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		if 'default_is_assessors' in context:
			self._cr.execute("select id from hr_employee where assessor_seq_no='%s'" % (user_data.assessor_moderator_id.assessor_seq_no,))
			assessor_ids = map(lambda x:x[0], self._cr.fetchall())
			if assessor_ids:
				args.append(('id', '=', max(assessor_ids)))
			return super(hr_employee, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		if 'default_is_learner' in context :
			return super(hr_employee, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		if self._context.get('model') == 'learner.registration.qualification' or self._context.get('model') == 'skills.programme.learner.rel' or self._context.get('model') == 'learning.programme.learner.rel':
			if user_data.partner_id.provider:
				ass_mod_lst = []
				for line in self.env.user.partner_id.assessors_ids:
					self._cr.execute("select id from hr_employee where is_active_assessor = True and id =%s"%(line.assessors_id.id))
					ass_id = self._cr.fetchone()
					if ass_id:
						ass_mod_lst.append(ass_id[0])
				for line in self.env.user.partner_id.moderators_ids:
					self._cr.execute("select id from hr_employee where is_active_moderator = True and id =%s"%(line.moderators_id.id))
					mod_id = self._cr.fetchone()
					if mod_id:
						ass_mod_lst.append(mod_id[0])
				args.append(('id', 'in', ass_mod_lst))
				return super(hr_employee, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
		return super(hr_employee, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

	learner_identification_id = fields.Char("R.S.A.Identification No", size=13)
	assessor_moderator_identification_id = fields.Char("R.S.A.Identification No.", size=13)
	moderator_start_date = fields.Date("Moderator Start Date")
	moderator_end_date = fields.Date("Moderator End Date")
	already_registered = fields.Boolean("Re-registration", default=False)
	as_provider_rel_id = fields.One2many('etqe.as.provider.rel', 'assessors_id', string="Provider Assessor Relation")
	mo_provider_rel_id = fields.One2many('etqe.mo.provider.rel', 'moderators_id', string="Provider Moderator Relation")
	qualification_id = fields.Many2one("provider.qualification", 'Provider Qualification', readonly=True, ondelete='restrict')
	etqe_assessors_tracking_ids = fields.One2many('etqe.assessors.tracking', 'employee_id', string='Etqe Assessors tracking', readonly=True)
	etqe_moderators_tracking_ids = fields.One2many('etqe.moderators.tracking', 'employee_id', string='Etqe Moderators tracking', readonly=True)
	timetable_id = fields.Many2one("learner.timetable", 'TimeTable', ondelete='restrict')
	verify = fields.Boolean(string="Verification")
	assessment_id = fields.Many2one("provider.assessment", 'Assessment')
	assessment_timetables_id = fields.Many2one("provider.assessment", 'Assessment')
	assessment_verify_id = fields.Many2one("provider.assessment", "Assessment")
	assessment_verified_id = fields.Many2one("provider.assessment", "Assessment")
	pro_assess_ids = fields.One2many('learner.assessment', 'pro_learner_id', string='Provider Assessment')
#     pro_assessment_ids = fields.One2many('provider.assessment','pro_learner_id', string='Provider Assessment')
	learner_pro_ids = fields.One2many('learner.provider.rel', 'assess_pro_id', string='Providers')
	qual_ids = fields.One2many('learner.qualification', 'learner_id', string='Qualifications')
	qual_line_ids = fields.One2many('learner.qualification.line', 'learner_id', string='Qualification Lines')
#     provider_ids = fields.One2many('res.partner', 'assess_pro_id', string='Providers')
#     qualification_ids = fields.One2many('provider.qualification', 'learner_id', string='Qualifications')
#     qualification_line_ids = fields.One2many('provider.qualification.line', 'learner_id', string='Qualification Lines')
	attached_report = fields.Binary(string="Certificate No")
	type = fields.Selection([('permanent', 'Permanent'), ('consultant', 'Consultant')], string="Type")
	qualification_ids = fields.One2many('assessors.moderators.qualification.hr', 'assessors_moderators_qualification_hr_id', 'Qualification Hr Lines')
	moderator_qualification_ids = fields.One2many('moderators.qualification.hr', 'moderators_qualification_hr_id', 'Qualification Hr Lines')
	organisation_sdl_no = fields.Char("Organisation SDL No")
	organisation = fields.Many2one('res.partner', string='Organisation', track_visibility='onchange')
	learner_qualification_ids = fields.One2many('learner.registration.qualification', 'learner_id')
#     qualification_extensions_ids = fields.One2many('assessors.moderators.qualification.extensions', 'assessors_moderators_qualification_extensions_id', 'Qualification extensions Lines')
	learners_status = fields.Selection([('active', 'Enrolled'),
								('re-enrolled','Re-Enrolled'),
							   ('in_active', 'In Active'),
							   ('drop_out', 'Drop Out'),
							   ('replacement', 'Replacement'),
							   ('suspend', 'Suspended'),
							   ('achieved','Achieved'),
							   ('unknown','Unknown') ],
							  string='Status', default='active')

	enrollment_date = fields.Date("Enrollment Date")
	learner_status_reason = fields.Text("Status Reason")
	learner_master_status_ids = fields.One2many('learner.master.status', 'learner_master_status_id', 'Status Line')
	state = fields.Selection([
			('active', 'Enrolled'),
			('re-enrolled','Re-Enrolled'),
			('dropout', 'Drop Out'),
			('replacement', 'Replacement'),
			('suspended', ' Suspended'),
			('inactive', 'In Active'),
			('achieved','Achieved'),
			('unknown','Unknown'),
		], string='Status', index=True, readonly=True, default='active',
		track_visibility='onchange', copy=False)
	# bool values for state changing buttons of etqe learners in hr.empolyee
	is_active = fields.Boolean(string="Active", track_visibility='onchange', default=False)
	is_drop_out = fields.Boolean(string="Drop Out", track_visibility='onchange', default=False)
	is_replacement = fields.Boolean(string="Replacement", track_visibility='onchange', default=False)
	is_suspend = fields.Boolean(string="Suspended", track_visibility='onchange', default=False)
	# bool value to show data for only provider learner
	provider_learner = fields.Boolean(string="provider learner", track_visibility='onchange', default=False)
	# field to know looged provider name
	logged_provider_id = fields.Many2one(related="learner_qualification_ids.provider_id")
	skills_programme_ids = fields.One2many('skills.programme.learner.rel', 'skills_programme_learner_rel_ids', 'Skills Programme Lines')
	learner_master_other_docs_ids = fields.One2many('acc.multi.doc.upload', 'learner_master_id', string='Learner Master Other Documents', track_visibility='onchange')
	logged_provider_id_for_skills = fields.Many2one(related="skills_programme_ids.provider_id")
	is_active_assessor = fields.Boolean("Active", default=True)
	is_active_moderator = fields.Boolean("Active", default=True)
	# Newly added fields for learning programme
	learning_programme_ids = fields.One2many('learning.programme.learner.rel', 'learning_programme_learner_rel_ids', 'Learning Programme Lines')
	logged_provider_id_for_lp = fields.Many2one(related="learning_programme_ids.provider_id")
#     _sql_constraints = [('am_idno_uniq', 'unique(assessor_moderator_identification_id)',
#         'R.S.A.Identification No must be unique per Assessor/Moderator!'),]
#
#     _sql_constraints = [('learner_idno_uniq', 'unique(learner_identification_id)',
#             'Learner Identification Number must be unique per Learner!'), ]
	# method of Set As Active Button to change state
	@api.multi
	def action_active_button(self):
		qual_obj = self.env['learner.registration.qualification'].search([('learner_id','=',self.id)])
		if qual_obj:
			end_date_lst = [qual.end_date for qual in qual_obj if qual.end_date]
			if end_date_lst:
				latest_qual_obj = self.env['learner.registration.qualification'].search([('end_date','=',max(end_date_lst))])
				if latest_qual_obj:
					latest_qual_obj.write({'qual_status':'Enrolled'})
		self.write({'learner_status':'Enrolled','state':'active', 'is_active':True, 'learners_status':'active', 'learner_master_status_ids':[(0, 0, {'learner_master_uid':self.env['res.users'].browse(self._uid).name, 'learner_master_status':'Enrolled', 'learner_master_date':datetime.now(), 'learner_master_comment':self.learner_status_reason})], 'learner_status_reason':''})
		return True

#     @api.multi
#     def action_dropout_button(self):
#         if self.state == 'suspended':
#             self.write({'learner_status':'Reinstated'})
#         if not self.learner_status_reason:
#             raise Warning(_("please add reason for Drop out in comment"))
#         self.write({'state':'dropout', 'is_drop_out':True, 'learners_status':'drop_out', 'learner_master_status_ids':[(0, 0, {'learner_master_uid':self.env['res.users'].browse(self._uid).name, 'learner_master_status':'Drop Out', 'learner_master_date':datetime.now(), 'learner_master_comment':self.learner_status_reason})], 'learner_status_reason':''})
#         return True

	@api.multi
	def action_replacement_button(self):
		qual_obj = self.env['learner.registration.qualification'].search([('learner_id','=',self.id)])
		if qual_obj:
			end_date_lst = [qual.end_date for qual in qual_obj if qual.end_date]
			if end_date_lst:
				latest_qual_obj = self.env['learner.registration.qualification'].search([('end_date','=',max(end_date_lst))])
				if latest_qual_obj:
					latest_qual_obj.write({'qual_status':'Replacement'})

		self.write({'learner_status':'Replacement','state':'replacement', 'is_replacement':True, 'learners_status':'replacement', 'learner_master_status_ids':[(0, 0, {'learner_master_uid':self.env['res.users'].browse(self._uid).name, 'learner_master_status':'Replacement', 'learner_master_date':datetime.now(), 'learner_master_comment':self.learner_status_reason})], 'learner_status_reason':''})
		return True

	@api.multi
	def action_suspend_button(self):
		qual_obj = self.env['learner.registration.qualification'].search([('learner_id','=',self.id)])
		if qual_obj:
			end_date_lst = [qual.end_date for qual in qual_obj if qual.end_date]
			if end_date_lst:
				latest_qual_obj = self.env['learner.registration.qualification'].search([('end_date','=',max(end_date_lst))])
				if latest_qual_obj:
					latest_qual_obj.write({'qual_status':'Suspended'})
		self.write({'learner_status':'Replacement','state':'suspended', 'is_suspend':True, 'learners_status':'suspend', 'learner_master_status_ids':[(0, 0, {'learner_master_uid':self.env['res.users'].browse(self._uid).name, 'learner_master_status':'Suspended', 'learner_master_date':datetime.now(), 'learner_master_comment':self.learner_status_reason})], 'learner_status_reason':''})
		return True

#     @api.multi
#     def action_inactive_button(self):
#         if self.state == 'suspended':
#             self.write({'learner_status':'Reinstated'})
#         self.write({'state':'inactive', 'is_active':False, 'learners_status':'in_active', 'learner_master_status_ids':[(0, 0, {'learner_master_uid':self.env['res.users'].browse(self._uid).name, 'learner_master_status':'In Active', 'learner_master_date':datetime.now(), 'learner_master_comment':self.learner_status_reason})], 'learner_status_reason':''})
#         return True

	@api.multi
	def action_achieved_button(self):
		self.write({'state':'achieved', 'learners_status':'achieved', 'learner_master_status_ids':[(0, 0, {'learner_master_uid':self.env['res.users'].browse(self._uid).name, 'learner_master_status':'Achieved', 'learner_master_date':datetime.now(), 'learner_master_comment':self.learner_status_reason})], 'learner_status_reason':''})
		return True

	@api.multi
	def country_for_province(self, province):
		state = self.env['res.country.state'].browse(province)
		return state.country_id.id

	@api.multi
	def onchange_work_province(self, province):
		if province:
			country_id = self.country_for_province(province)
			return {'value': {'work_country': country_id }}
		return {}

	@api.multi
	def onchange_home_province(self, province):
		if province:
			country_id = self.country_for_province(province)
			return {'value': {'country_home': country_id }}
		return {}

	@api.multi
	def onchange_postal_province(self, province):
		if province:
			country_id = self.country_for_province(province)
			return {'value': {'country_postal': country_id }}
		return {}

	@api.multi
	def onchange_employer_id(self, employer_id):
		if not employer_id:
			return False
		else:
			result = {}
			employer_data = self.env['res.partner'].browse(employer_id)
			result = {'value':{
							   'organisation_sdl_no': employer_data.employer_sdl_no,
							   }}
		return result

	@api.multi
	def work_addr_map(self):
		return self.open_map(self.work_address, self.work_city, self.work_province, self.work_country, self.work_zip)

	@api.multi
	def home_addr_map(self):
		return self.open_map(self.person_home_address_1, self.person_home_city, self.person_home_province_code, self.country_home, self.person_home_zip)

	@api.multi
	def postal_addr_map(self):
		return self.open_map(self.person_postal_address_1, self.person_postal_city, self.person_postal_province_code, self.country_postal, self.person_postal_zip)

	@api.model
	def create(self, vals):
		res = super(hr_employee, self).create(vals)
		if self._context.get('from_registration_process'):
			pass
		else:
			if self._context.get('default_is_assessors'):
				res['assessor_seq_no'] = self.env['ir.sequence'].get('assessors.master.register')
			if self._context.get('default_is_moderators'):
				res['moderator_seq_no'] = self.env['ir.sequence'].get('moderators.master.register')
		return res

	@api.multi
	def onchange_gender(self, gender):
		res = {}
		if not gender:
			res.update({'value':{'gender_saqa_code':''}})
			return res
		if gender == 'male':
			res.update({'value':{'gender_saqa_code':'m'}})
		elif gender == 'female':
			res.update({'value':{'gender_saqa_code':'f'}})
		return res

	@api.multi
	def onchange_gender_saqa_code(self, gender_saqa_code):
		res = {}
		if not gender_saqa_code:
			res.update({'value':{'gender':''}})
			return res
		if gender_saqa_code == 'm':
			res.update({'value':{'gender':'male'}})
		elif gender_saqa_code == 'f':
			res.update({'value':{'gender':'female'}})
		return res

	@api.multi
	def onchange_equity(self, equity):
		res = {}
		if not equity:
			res.update({'value':{'equity_saqa_code':''}})
			return res
		if equity == 'black_african':
			res.update({'value':{'equity_saqa_code':'ba'}})
		elif equity == 'black_indian':
			res.update({'value':{'equity_saqa_code':'bi'}})
		elif equity == 'black_coloured':
			res.update({'value':{'equity_saqa_code':'bc'}})
		elif equity == 'other':
			res.update({'value':{'equity_saqa_code':'oth'}})
		elif equity == 'unknown':
			res.update({'value':{'equity_saqa_code':'u'}})
		elif equity == 'white':
			res.update({'value':{'equity_saqa_code':'wh'}})
		return res

	@api.multi
	def onchange_equity_saqa_code(self, equity_saqa_code):
		res = {}
		if not equity_saqa_code:
			res.update({'value':{'equity':''}})
			return res
		if equity_saqa_code == 'ba':
			res.update({'value':{'equity':'black_african'}})
		elif equity_saqa_code == 'bi':
			res.update({'value':{'equity':'black_indian'}})
		elif equity_saqa_code == 'bc':
			res.update({'value':{'equity':'black_coloured'}})
		elif equity_saqa_code == 'oth':
			res.update({'value':{'equity':'other'}})
		elif equity_saqa_code == 'u':
			res.update({'value':{'equity':'unknown'}})
		elif equity_saqa_code == 'wh':
			res.update({'value':{'equity':'white'}})
		return res

	@api.multi
	def onchange_socio(self, socio_economic_status):
		res = {}
		if not socio_economic_status:
			res.update({'value':{'socio_economic_saqa_code':''}})
			return res
		if socio_economic_status == 'employed':
			res.update({'value':{'socio_economic_saqa_code':'1'}})
		if socio_economic_status == 'unemployed':
			res.update({'value':{'socio_economic_saqa_code':'2'}})
		if socio_economic_status == 'Not working, not looking':
			res.update({'value':{'socio_economic_saqa_code':'3'}})
		if socio_economic_status == 'Home-maker (not working)':
			res.update({'value':{'socio_economic_saqa_code':'4'}})
		if socio_economic_status == 'Scholar/student (not w.)':
			res.update({'value':{'socio_economic_saqa_code':'6'}})
		if socio_economic_status == 'Pensioner/retired (not w.)':
			res.update({'value':{'socio_economic_saqa_code':'7'}})
		if socio_economic_status == 'Not working - disabled':
			res.update({'value':{'socio_economic_saqa_code':'8'}})
		if socio_economic_status == 'Not working - no wish to w':
			res.update({'value':{'socio_economic_saqa_code':'9'}})
		if socio_economic_status == 'Not working - N.E.C.':
			res.update({'value':{'socio_economic_saqa_code':'10'}})
		if socio_economic_status == 'N/A: aged <15':
			res.update({'value':{'socio_economic_saqa_code':'97'}})
		if socio_economic_status == 'N/A: Institution':
			res.update({'value':{'socio_economic_saqa_code':'98'}})
		if socio_economic_status == 'Unspecified':
			res.update({'value':{'socio_economic_saqa_code':'U'}})
		return res

	@api.multi
	def onchange_socio_code(self, socio_economic_saqa_code):
		res = {}
		if not socio_economic_saqa_code:
			res.update({'value':{'socio_economic_status':''}})
			return res
		if socio_economic_saqa_code == '1':
			res.update({'value':{'socio_economic_status':'employed'}})
		if socio_economic_saqa_code == '2':
			res.update({'value':{'socio_economic_status':'unemployed'}})
		if socio_economic_saqa_code == '3':
			res.update({'value':{'socio_economic_status':'Not working, not looking'}})
		if socio_economic_saqa_code == '4':
			res.update({'value':{'socio_economic_status':'Home-maker (not working)'}})
		if socio_economic_saqa_code == '6':
			res.update({'value':{'socio_economic_status':'Scholar/student (not w.)'}})
		if socio_economic_saqa_code == '7':
			res.update({'value':{'socio_economic_status':'Pensioner/retired (not w.)'}})
		if socio_economic_saqa_code == '8':
			res.update({'value':{'socio_economic_status':'Not working - disabled'}})
		if socio_economic_saqa_code == '9':
			res.update({'value':{'socio_economic_status':'Not working - no wish to w'}})
		if socio_economic_saqa_code == '10':
			res.update({'value':{'socio_economic_status':'Not working - N.E.C.'}})
		if socio_economic_saqa_code == '97':
			res.update({'value':{'socio_economic_status':'N/A: aged <15'}})
		if socio_economic_saqa_code == '98':
			res.update({'value':{'socio_economic_status':'N/A: Institution'}})
		if socio_economic_saqa_code == 'U':
			res.update({'value':{'socio_economic_status':'Unspecified'}})
		return res

	@api.multi
	def onchange_disability(self, disability_status):
		res = {}
		if not disability_status:
			res.update({'value':{'disability_status_saqa':''}})
			return res
		if disability_status == 'sight':
			res.update({'value':{'disability_status_saqa':'1'}})
		elif disability_status == 'hearing':
			res.update({'value':{'disability_status_saqa':'2'}})
		elif disability_status == 'communication':
			res.update({'value':{'disability_status_saqa':'3'}})
		elif disability_status == 'physical':
			res.update({'value':{'disability_status_saqa':'4'}})
		elif disability_status == 'intellectual':
			res.update({'value':{'disability_status_saqa':'5'}})
		elif disability_status == 'emotional':
			res.update({'value':{'disability_status_saqa':'6'}})
		elif disability_status == 'multiple':
			res.update({'value':{'disability_status_saqa':'7'}})
		elif disability_status == 'disabled':
			res.update({'value':{'disability_status_saqa':'9'}})
		elif disability_status == 'none':
			res.update({'value':{'disability_status_saqa':'n'}})
		return res

	@api.multi
	def onchange_disability_status_saqa(self, disability_status_saqa):
		res = {}
		if not disability_status_saqa:
			res.update({'value':{'disability_status':''}})
			return res
		if disability_status_saqa == '1':
			res.update({'value':{'disability_status':'sight'}})
		elif disability_status_saqa == '2':
			res.update({'value':{'disability_status':'hearing'}})
		elif disability_status_saqa == '3':
			res.update({'value':{'disability_status':'communication'}})
		elif disability_status_saqa == '4':
			res.update({'value':{'disability_status':'physical'}})
		elif disability_status_saqa == '5':
			res.update({'value':{'disability_status':'intellectual'}})
		elif disability_status_saqa == '6':
			res.update({'value':{'disability_status':'emotional'}})
		elif disability_status_saqa == '7':
			res.update({'value':{'disability_status':'multiple'}})
		elif disability_status_saqa == '9':
			res.update({'value':{'disability_status':'disabled'}})
		elif disability_status_saqa == 'n':
			res.update({'value':{'disability_status':'none'}})

		return res

	@api.multi
	def onchange_language(self, home_language_code):
		res = {}
		if not home_language_code:
			res.update({'value':{'home_lang_saqa_code':''}})
			return res
		if home_language_code == 1:
			res.update({'value':{'home_lang_saqa_code':'eng'}})
		elif home_language_code == 2:
			res.update({'value':{'home_lang_saqa_code':'zul'}})
		elif home_language_code == 3:
			res.update({'value':{'home_lang_saqa_code':'sep'}})
		elif home_language_code == 4:
			res.update({'value':{'home_lang_saqa_code':'tsh'}})
		elif home_language_code == 5:
			res.update({'value':{'home_lang_saqa_code':'ses'}})
		elif home_language_code == 6:
			res.update({'value':{'home_lang_saqa_code':'xit'}})
		elif home_language_code == 7:
			res.update({'value':{'home_lang_saqa_code':'oth'}})
		elif home_language_code == 8:
			res.update({'value':{'home_lang_saqa_code':'swa'}})
		elif home_language_code == 9:
			res.update({'value':{'home_lang_saqa_code':'u'}})
		elif home_language_code == 10:
			res.update({'value':{'home_lang_saqa_code':'nde'}})
		elif home_language_code == 11:
			res.update({'value':{'home_lang_saqa_code':'set'}})
		elif home_language_code == 12:
			res.update({'value':{'home_lang_saqa_code':'afr'}})
		elif home_language_code == 13:
			res.update({'value':{'home_lang_saqa_code':'xho'}})
		return res

	@api.multi
	def onchange_home_lang_saqa_code(self, home_lang_saqa_code):
		res = {}
		if not home_lang_saqa_code:
			res.update({'value':{'home_language_code':''}})
			return res
		if home_lang_saqa_code == 'eng':
			res.update({'value':{'home_language_code':1}})
		elif home_lang_saqa_code == 'zul':
			res.update({'value':{'home_language_code':2}})
		elif home_lang_saqa_code == 'sep':
			res.update({'value':{'home_language_code':3}})
		elif home_lang_saqa_code == 'tsh':
			res.update({'value':{'home_language_code':4}})
		elif home_lang_saqa_code == 'ses':
			res.update({'value':{'home_language_code':5}})
		elif home_lang_saqa_code == 'xit':
			res.update({'value':{'home_language_code':6}})
		elif home_lang_saqa_code == 'oth':
			res.update({'value':{'home_language_code':7}})
		elif home_lang_saqa_code == 'swa':
			res.update({'value':{'home_language_code':8}})
		elif home_lang_saqa_code == 'u':
			res.update({'value':{'home_language_code':9}})
		elif home_lang_saqa_code == 'nde':
			res.update({'value':{'home_language_code':10}})
		elif home_lang_saqa_code == 'set':
			res.update({'value':{'home_language_code':11}})
		elif home_lang_saqa_code == 'afr':
			res.update({'value':{'home_language_code':12}})
		elif home_lang_saqa_code == 'xho':
			res.update({'value':{'home_language_code':13}})
		return res

	@api.multi
	def unlink(self):
		if self.env.user.has_group('hwseta_etqe.group_seta_administrator'):
			for achieve in self.env['learner.assessment.achieve.line'].search([('learner_id','=',self.id)]):
				dbg(achieve)
				achieve.unlink()
			for achieved in self.env['learner.assessment.achieved.line'].search([('learner_id','=',self.id)]):
				dbg(achieved)
				achieved.unlink()
			for evaluate in self.env['learner.assessment.evaluate.line'].search([('learner_id','=',self.id)]):
				dbg(evaluate)
				evaluate.unlink()
			for line in self.env['learner.assessment.line'].search([('learner_id','=',self.id)]):
				dbg(line)
				line.unlink()
			for verify in self.env['learner.assessment.verify.line'].search([('learner_id','=',self.id)]):
				dbg(verify)
				verify.unlink()
			return super(hr_employee, self).unlink()
		else:
			raise Warning(_("Sorry!! You cannot delete Approved record !"))


	@api.multi
	def copy(self):
		raise Warning(_("Sorry!! You cannot duplicate Approved record !"))
		return super(hr_employee, self).copy()
hr_employee()

class etqe_assessors_tracking(models.Model):
	_name = 'etqe.assessors.tracking'

	provider_accreditation_id = fields.Many2one("provider.accreditation", string="Provider Accreditation")
	status = fields.Selection([('requested_approval', 'Requested Approval'),
							   ('approved', 'Approved'),
							   ('denied', 'Denied')],
							  string='State', readonly=True)
	employee_id = fields.Many2one("hr.employee", string="Employee")
	etqe_approved_denied = fields.Boolean(string='ETQE Approved Denied')

	_defaults = {
		'etqe_approved_denied': False,
	}
	@api.multi
	def action_approve_sdf(self):
		self.write({'etqe_approved_denied':True, 'status':'approved'})
		# TODO: Creation of SDF Master from SDF Registration Information Object.
		return True

	@api.multi
	def action_deny_sdf(self):
		self.write({'etqe_approved_denied':False, 'status':'denied'})
		# TODO: Creation of SDF Master from SDF Registration Information Object.
		return True
etqe_assessors_tracking()

class etqe_moderators_tracking(models.Model):
	_name = 'etqe.moderators.tracking'

	provider_accreditation_id = fields.Many2one("provider.accreditation", string="Provider Accreditation")
	status = fields.Selection([('requested_approval', 'Requested Approval'),
							   ('approved', 'Approved'),
							   ('denied', 'Denied')],
							  string='State', readonly=True)
	employee_id = fields.Many2one("hr.employee", string="Employee")
	etqe_approved_denied = fields.Boolean(string='ETQE Approved Denied')

	_defaults = {
		'etqe_approved_denied': False,
	}

	@api.multi
	def action_approve_sdf(self):
		self.write({'etqe_approved_denied':True, 'status':'approved'})
		# TODO: Creation of SDF Master from SDF Registration Information Object.
		return True

	@api.multi
	def action_deny_sdf(self):
		self.write({'etqe_approved_denied':False, 'status':'denied'})
		# TODO: Creation of SDF Master from SDF Registration Information Object.
		return True
etqe_moderators_tracking()

class etqe_learner_attachment(models.Model):
	"""
	Form for Attachment details
	"""
	_name = "etqe.learner.attachment"

	name = fields.Char('Document Name', required=True)
	data = fields.Binary('File', required=True)
	learner_attach_id = fields.Many2one('etqe.learner', 'Document Upload', ondelete='cascade')
etqe_learner_attachment()

class etqe_learner(models.Model):
	_name = 'etqe.learner'
	_description = 'Etqe Learner'

	seq_no = fields.Char(string='Agreement No')
	surname = fields.Char(string='Surname')
	identity_number = fields.Char(string='Identity Number')
	alternate_identity_no = fields.Char(string='Alternate identity No')
	certificate_no = fields.Char(string='Certificate No')

	title = fields.Char(string='Title')
	name = fields.Char(string='Name')
	detials_surname = fields.Char(string='Surname')
	maiden_name = fields.Char(string='Maiden Name')
	gender = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Gender')
	business_tel_no = fields.Char(string='Business Tel No')
	fax_no = fields.Char(string='Fax No', size=10)
	email = fields.Char(string='Email')
	cell = fields.Char(string='Cell')
	dissability = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Dissability')
	citizen_residential_status = fields.Selection([('dual', 'D - Dual (SA plus other)'), ('other', 'O - Other'), ('sa', 'SA - South Africa'), ('unknown', 'U - Unknown')], string='Citizen Status')
	nationality_id = fields.Many2one('res.country', string='Nationality')
	rsa_identity_no = fields.Char(string='RSA Identity No')
	date_of_birth = fields.Date(string='Date of Birth')
	method_of_communication = fields.Char(string='Method of Communication')
	sponsorship = fields.Selection([('non_sponsored', 'Non-sponsored')], 'Sponsorship')
	home_language = fields.Many2one('res.lang', string='Home Language Code', track_visibility='onchange', size=6)
	highest_education = fields.Selection([('abet_level_1', 'Abet Level 1'), ('abet_level_2', 'Abet Level 2'), ('abet_level_3', 'Abet Level 3'), ('abet_level_4', 'Abet Level 4'), ('nqf123', 'NQF 1,2,3'), ('nqf45', 'NQF 4,5'), ('nqf67', 'NQF 6,7'), ('nqf8910', 'NQF 8,9,10')], string='Highest Education')
	record_last_updated = fields.Datetime('Record Last Updated')
	last_updated_operator = fields.Char(string='Last Updated Operator')
	learner_status = fields.Selection([('achieved', 'Achieved')], 'Learner Status')
	status_reason = fields.Selection([('workplace_learning', '500 - Workplace learning')], 'Learner Status Reason')
	status_comments = fields.Text('Status Comments')
	status_effective_date = fields.Date(string='Status Effective Date')
	learner_attachment_ids = fields.One2many('etqe.learner.attachment', 'learner_attach_id', 'Document Upload')
	# # Learner Address ##
	learner_home_address_1 = fields.Char(string='Home Address 1', track_visibility='onchange', size=50)
	learner_home_address_2 = fields.Char(string='Home Address 2', track_visibility='onchange', size=50)
	learner_home_address_3 = fields.Char(string='Home Address 3', track_visibility='onchange', size=50)
	learner_postal_address_1 = fields.Char(string='Postal Address 1', track_visibility='onchange', size=50)
	learner_postal_address_2 = fields.Char(string='Postal Address 2', track_visibility='onchange', size=50)
	learner_postal_address_3 = fields.Char(string='Postal Address 3', track_visibility='onchange', size=50)
	learner_home_suburb = fields.Many2one('res.suburb', string='Home Suburb')
	learner_postal_suburb = fields.Many2one('res.suburb', string='Postal Suburb')
	learner_home_city = fields.Many2one('res.city', string='Home City', track_visibility='onchange')
	learner_postal_city = fields.Many2one('res.city', string='Postal City', track_visibility='onchange')
	learner_home_zip = fields.Char(string='Home Zip', track_visibility='onchange')
	learner_postal_zip = fields.Char(string='Postal Zip', track_visibility='onchange')
	learner_country_home = fields.Many2one('res.country', string='Home Country', track_visibility='onchange')
	learner_country_postal = fields.Many2one('res.country', string='Postal Country', track_visibility='onchange')
	learner_home_province_code = fields.Many2one('res.country.state', string='Home Province Code', track_visibility='onchange')
	learner_postal_province_code = fields.Many2one('res.country.state', string='Postal Province Code', track_visibility='onchange')
	same_as_home = fields.Boolean(string='Same As Home Address')
	user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
	african = fields.Boolean(string='African')
	person_title = fields.Selection([('adv', 'Adv.'), ('dr', 'Dr.'), ('mr', 'Mr.'), ('mrs', 'Mrs.'), ('ms', 'Ms.'), ('prof', 'Prof.')], string='Title', track_visibility='onchange')
	learner_reg_no = fields.Char(string='Learner Reg No')
#     equity = fields.Char(string='Equity')
#     disability_status = fields.Char(string='Disability Status')
#     status_effective_date = fields.Date(string='Status Effective Date')
#     status_reason = fields.Selection([('workplace_learning', '500 - Workplace learning')],'Learner Status Reason')
#     wsp_year = fields.Selection([('2015', '2015'),('2016', '2016')],'WSP Year')
#     attached_report = fields.Binary(string="Agreement No")
#     created = fields.Boolean(string='Created', default=True)
#     loaded = fields.Boolean(string='Loaded')

	@api.multi
	def onchange_crc(self, citizen_residential_status):
		res = {}
		if not citizen_residential_status:
			return res
		if citizen_residential_status == 'sa':
			country_data = self.env['res.country'].search(['|', ('code', '=', 'ZA'), ('name', '=', 'South Africa')], limit=1)
			res.update({'value':{'nationality_id':country_data and country_data.id}})
		return res

	@api.multi
	def onchange_id_no(self, identification_id):
		res, val = {}, {}
		if not identification_id:
			return res
		if len(identification_id) == 13 and str(identification_id).isdigit():
			year = identification_id[:2]
			identification_id = identification_id[2:]
			month = identification_id[:2]
			identification_id = identification_id[2:]
			day = identification_id[:2]
			if int(month) > 12 or int(month) < 1 or int(day) > 31 or int(day) < 1:
				return {'value':{'identity_number':''},'warning':{'title':'Invalid Identification Number','message':'Incorrect Identification Number!'}}
			else:
				# # Calculating last day of month.
				x_year = int(year)
				if x_year == 00:
					x_year = 2000
				last_day = calendar.monthrange(int(x_year),int(month))[1]
				if int(day) > last_day :
					return {'value':{'identity_number':''},'warning':{'title':'Invalid Identification Number','message':'Incorrect Identification Number!'}}
			if int(year) == 00 or int(year) >= 01 and int(year) <= 20:
				birth_date = datetime.strptime('20' + year + '-' + month + '-' + day, '%Y-%m-%d').date()
			else:
				birth_date = datetime.strptime('19' + year + '-' + month + '-' + day, '%Y-%m-%d').date()

			val.update({'date_of_birth':birth_date})
			res.update({'value':val})
			return res
		else:
			return {'value':{'identity_number':''},'warning':{'title':'Invalid Identification Number','message':'Identification Number should be numeric!'}}

	@api.multi
	def onchange_identity_number(self, identification_id):
		res = {}
		if not identification_id:
			return res
		for identification_ids in self.search([('identity_number', '=', str(identification_id))]):
			if identification_ids:
				raise Warning(_('Duplicate Identification Number!'))
		return res
	# #  Added  Sequence for Learner Agreement
	@api.model
	def create(self, vals):
		vals['seq_no'] = self.env['ir.sequence'].get('sdp.learner')
		return super(etqe_learner, self).create(vals)

	@api.multi
	def country_for_province(self, province):
		state = self.env['res.country.state'].browse(province)
		return state.country_id.id

	@api.multi
	def onchange_postal_province(self, province):
		if province:
			country_id = self.country_for_province(province)
			return {'value': {'learner_country_postal': country_id }}
		return {}

	@api.multi
	def onchange_home_province(self, province):
		if province:
			country_id = self.country_for_province(province)
			return {'value': {'learner_country_home': country_id }}
		return {}

	@api.multi
	def onchange_country_id(self, country_id):
		res = {}
		if not country_id:
			return res
		country_data = self.env['res.country'].browse(country_id)
		if country_data.code == 'ZA':
			res.update({'value':{'african':True}})
		else:
			res.update({'value':{'african':False}})
		return res
etqe_learner()

#Assessment classes for skills programme
class learner_assessment_line_for_skills(models.Model):
	_name = 'learner.assessment.line.for.skills'

	@api.multi
	def _get_provider(self):
		''' Getting provider from Assessment via context passed in xml.'''
		context = self._context
		provider_id = context.get('provider', False)
		return provider_id
#     name = fields.Char(string='Name')
	provider_assessment_ref_id_for_skills = fields.Many2one('provider.assessment', string='provider_assessment_ref')
#     learner_id = fields.Many2one('etqe.learner', string='Learner', required=True)
	learner_id = fields.Many2one('hr.employee', string='Learners', required=True)
	assessors_id = fields.Many2one("hr.employee", string='Assessors', domain=[('is_assessors', '=', True)])
	moderators_id = fields.Many2one("hr.employee", string='Moderator', domain=[('is_moderators', '=', True)])
	learner_identity_number = fields.Char(string='Learner Number', track_visibility='onchange')
	timetable_id = fields.Many2one("learner.timetable", 'TimeTable')
	verify = fields.Boolean(string="Verification")
	provider_id = fields.Many2one('res.partner', string="Provider", track_visibility='onchange', default=_get_provider)
	identification_id = fields.Char(string="National Id",)
	skill_learner_assessment_line_id = fields.Many2many('skills.programme', 'skills_assessment_line_rel','skills_id', 'skill_learner_assessment_line_id', string='Skills')
	skill_unit_standards_learner_assessment_line_id = fields.Many2many('skills.programme.unit.standards', 'skills_unit_assessment_line_rel', 'skills_unit_standards_id', 'skill_unit_standards_learner_assessment_line_id', string='Skills Unit Standards')

	@api.multi
	def onchange_assessors_id(self, assessors_id, moderators_id):
		res = {}
		if not assessors_id and moderators_id:
			return res
		if assessors_id and moderators_id:
			if assessors_id == moderators_id:
				res.update({
					'value':{
								'assessors_id' : '',
								'moderators_id':'',

							 },
					 'warning': {'title': 'Error!', 'message': 'Assessor  And Moderator Cant be same in a row'},
					})

		return res

	@api.model
	def default_get(self, fields):
		context = self._context
		if context is None:
			context = {}
		res = super(learner_assessment_line_for_skills, self).default_get(fields)
		provider_id = context.get('provider', False)
		if provider_id:
			res.update(provider_id=provider_id)
		return res

	@api.multi
	def onchange_provider(self, provider_id):
#         provider_list=[]
#         learner_obj = self.env['learning.programme'].search([])
#         for learner in learner_obj:
#             for learner_line in learner.learner_ids:
#                 for load_learner in learner_line:
#                     for line in load_learner.proj_enrolled_ids:
#                         for l in line:
#                             if l.provider_id.id==provider_id:
#                                 provider_list.append(load_learner.id)
#         return {'domain': {'learner_id': [('id', 'in', provider_list)]}}
#         return True

#         learner_obj = self.env['hr.employee'].search([('is_learner', '=', True)])
#         for learner in learner_obj:
#             provider_list.append(learner.id)
#         return {'domain': {'learner_id': [('id', 'in', provider_list)]}}

		# This code is used to filter and show only logged user's learner on 06/10/2016
		learner_list = []
		if self._uid == 1:
			etqe_learner_obj = self.env['hr.employee'].search([('is_learner', '=', True), ('provider_learner', '=', True), ('state', 'in', ['active', 'replacement'])])
			for learner in etqe_learner_obj:
				learner_list.append(learner.id)
		else:
			etqe_learner_obj = self.env['hr.employee'].search([('is_learner', '=', True), ('provider_learner', '=', True), ('state', 'in', ['active', 'replacement'])])  # ,('logged_provider_id','=',user.partner_id.id)
			for learner in etqe_learner_obj:
				for qual_line in learner.learner_qualification_ids:
					provider = qual_line.provider_id.id
					if provider:
						if provider == self.env.user.partner_id.id:
							learner_list.append(learner.id)
#         load qualification as per provider
		qualification = []
		if self._uid == 1:
			qualification_obj = self.env['provider.qualification'].search([])
			for quali_id in qualification_obj:
					qualification.append(quali_id.id)
		else:
			provider_obj = self.env['res.partner'].search([('provider', '=', True), ('id', '=', provider_id)])
			if provider_obj.qualification_ids:
				for qualification_id in provider_obj.qualification_ids:
					for quali_id in qualification_id.qualification_id:
						qualification.append(quali_id.id)
			elif provider_obj.qualification_campus_ids:
				for qualification_campus_id in provider_obj.qualification_campus_ids:
					for quali_id in qualification_campus_id.qualification_id:
						qualification.append(quali_id.id)
#         load skill programme as per provider
		skill_programme = []
		if self._uid == 1:
			skill_obj = self.env['skills.programme'].search([])
			for quali_id in skill_obj:
					skill_programme.append(quali_id.id)
		else:
			provider_obj = self.env['res.partner'].search([('provider', '=', True), ('id', '=', provider_id)])
			if provider_obj.skills_programme_ids:
				for skill_ids in provider_obj.skills_programme_ids:
					for skill_id in skill_ids.skills_programme_id:
						skill_programme.append(skill_id.id)
			elif provider_obj.skills_programme_campus_ids:
				for skill_ids in provider_obj.skills_programme_campus_ids:
					for skill_id in skill_ids.skills_programme_id:
						skill_programme.append(skill_id.id)
#         load Assessor as per provider
		assessors_list = []
		if self._uid == 1:
			assessor_obj = self.env['hr.employee'].search([('is_assessors', '=', True)])
			for assessor in assessor_obj:
					assessors_list.append(assessor.id)
		else:
			provider_obj = self.env['res.partner'].search([('provider', '=', True), ('id', '=', provider_id)])
			if provider_obj.assessors_ids:
				for assessor_id in provider_obj.assessors_ids:
					for assessor in assessor_id.assessors_id:
						assessors_list.append(assessor.id)
			elif provider_obj.assessors_campus_ids:
				for assessors_campus_id in provider_obj.assessors_campus_ids:
					for assessor in assessors_campus_id.assessors_id:
						assessors_list.append(assessor.id)
		#   load Moderator as per provider
		moderator_list = []
		if self._uid == 1:
			moderator_obj = self.env['hr.employee'].search([('is_moderators', '=', True)])
			for moderator in moderator_obj:
					moderator_list.append(moderator.id)
		else:
			provider_obj = self.env['res.partner'].search([('provider', '=', True), ('id', '=', provider_id)])
			if provider_obj.moderators_ids:
				for moderator_id in provider_obj.moderators_ids:
					for moderator in moderator_id.moderators_id:
						moderator_list.append(moderator.id)
			elif provider_obj.moderators_campus_ids:
				for moderators_campus_id in provider_obj.moderators_campus_ids:
					for moderator in moderators_campus_id.moderators_id:
						moderator_list.append(moderator.id)
		return {'domain': {'learner_id': [('id', 'in', list(set(learner_list)))],
						   'qual_learner_assessment_line_id':[('id', 'in', qualification)],
						   'skill_learner_assessment_line_id':[('id', 'in', skill_programme)],
						   'assessors_id':[('id', 'in', assessors_list)],
						   'moderators_id':[('id', 'in', moderator_list)]
						   }}
#     @api.multi
#     def onchange_learner_id(self, learner_id,):
#         res = {}
#         if not learner_id :
#             return res
#         learner_data = self.env['hr.employee'].browse(learner_id)
#         l1 =[]
#         unit_lst=[]
#         for l in learner_data.learner_qualification_ids:
#             ulst = self.env['learner.registration.qualification.line'].search([('learner_reg_id','=',l.id)])
#             if ulst:
#                 if l.learner_qualification_parent_id.qualification_line:
#                     for ul in l.learner_qualification_parent_id.qualification_line:
#                         if ul.id not in unit_lst:
#                             unit_lst.append(ul.id)
#             l1.append(l.learner_qualification_parent_id.id)
#         if learner_data.learner_qualification_ids:
#             for l in learner_data.learner_qualification_ids:
#                 ulst = self.env['learner.registration.qualification.line'].search([('learner_reg_id','=',l.id)])
#                 if ulst:
#                     if l.learner_qualification_parent_id.qualification_line :
#                         for ul in l.learner_qualification_parent_id.qualification_line:
#                             if ul.id not in unit_lst:
#                                 unit_lst.append(ul.id)
#                 l1.append(l.learner_qualification_parent_id.id)
#
#
#         res.update({
#                     'value':{
#                                 'learner_identity_number' : learner_data.learner_reg_no,
#                                 'identification_id':learner_data.identification_id,
#                             'qual_learner_assessment_line_id':[(6,0,l1)],
# #                             'unit_standards_learner_assessment_line_id':[(6,0,[])],
#                              },
# #                    'domain':{'unit_standards_learner_assessment_line_id':[('id','in',unit_lst)]}
#                     })
#         return res
	@api.multi
	def onchange_learner_reg_no(self, learner_identity_number):
		res = {}
		if not learner_identity_number:
			return res

		learner_obj = self.env['hr.employee'].search([('learner_reg_no', '=', learner_identity_number)])
		res.update({
					'value':{
							 'learner_id':learner_obj.id,
#                              'qual_learner_assessment_line_id':learner_obj.learner_qualification_ids.learner_qualification_parent_id,
							 }
					})
		return res

#     @api.multi
#     def onchange_identification_id(self,identification_id):
#         res = {}
#         if not identification_id:
#             return res
#
#         learner_obj = self.env['hr.employee'].search([('identification_id','=',identification_id)])
#         l1 =[]
#         unit_lst=[]
#         for l in learner_obj.learner_qualification_ids:
#             ulst = self.env['learner.registration.qualification.line'].search([('learner_reg_id','=',l.id)])
#             if ulst:
#                 if l.learner_qualification_parent_id.qualification_line :
#                     for ul in l.learner_qualification_parent_id.qualification_line:
#                         if ul.id not in unit_lst:
#                             unit_lst.append(ul.id)
#             l1.append(l.learner_qualification_parent_id.id)
#
#         res.update({
#                     'value':{
#                              'learner_id':learner_obj.id,
# #                             'qual_learner_assessment_line_id':[(6,0,l1)],
# #                             'unit_standards_learner_assessment_line_id':[(6,0,unit_lst)]
#                              }
#                     })
#         return res

	@api.multi
	def onchange_qualification_ids(self, qualification_id):
		res = {}
		unit_standards_list = []
		if not qualification_id[0][2] :
			return res
		for qual_id in qualification_id[0][2]:
			qualification_master = self.env['provider.qualification'].browse(qual_id)
			for unit_standards in qualification_master.qualification_line:
				unit_standards_list.append(unit_standards.id)
		return {'domain': {'unit_standards_learner_assessment_line_id': [('id', 'in', unit_standards_list)]}}
learner_assessment_line_for_skills()

class learner_assessment_achieve_line_for_skills(models.Model):
	_name = 'learner.assessment.achieve.line.for.skills'
#     name = fields.Char(string='Name')
	provider_assessment_achieve_ref_id_for_skills = fields.Many2one('provider.assessment', string='provider_assessment_achieve_ref')
#     learner_id = fields.Many2one('etqe.learner', string='Learner', required=True)
	learner_id = fields.Many2one('hr.employee', string='Learner', required=True)

	assessors_id = fields.Many2one("hr.employee", string='Assessors', domain=[('is_assessors', '=', True)])
	moderators_id = fields.Many2one("hr.employee", string='Moderator', domain=[('is_moderators', '=', True)])
	learner_identity_number = fields.Char(string='Learner Number', track_visibility='onchange')
	timetable_id = fields.Many2one("learner.timetable", 'TimeTable')
	achieve = fields.Boolean(string="Achieved")
	identification_id = fields.Char(string="National Id", track_visibility='onchange')
#    qual_learner_assessment_achieve_line_id = fields.Many2many('provider.qualification', 'achieve_asse_qual_rel', 'qualification_achieve_id', 'qual_achieve_learner_assessment_line_id', string='Qualification')
#    skill_learner_assessment_achieve_line_id = fields.Many2many('skills.programme', 'achieve_asse_skills_rel', 'skills_achieve_id', 'skill_learner_assessment_achieve_line_id', string='Skills')
#    unit_standards_learner_assessment_achieve_line_id = fields.Many2many('provider.qualification.line', 'achieve_asse_unit_rel', 'unit_standards_achieve_id', 'unit_standards_learner_assessment_achieve_line_id', string='Unit Standards')
	skill_learner_assessment_achieve_line_id = fields.Many2many('skills.programme', 'achieve_asse_skills_rel_new','skills_achieve_id', 'skill_learner_assessment_achieve_line_id', string='Skills')
	skill_unit_standards_learner_assessment_achieve_line_id = fields.Many2many('skills.programme.unit.standards', 'achieve_asse_skills_unit_rel_new', 'skills_unit_standards_achieve_id', 'skill_unit_standards_learner_assessment_achieve_line_id', string='Skills Unit Standards')

#     sdl_number = fields.Char(string='SDL Number')
#     seta_id = fields.Many2one('seta.branches', string='SETA Id')
#     sic_code = fields.Many2one('hwseta.sic.master')
#     email = fields.Char(string='Email')
#     phone = fields.Char(string='Phone')
#     mobile = fields.Char(string='Mobile')
learner_assessment_achieve_line_for_skills()

class learner_assessment_verify_line_for_skills(models.Model):
	_name = 'learner.assessment.verify.line.for.skills'


	provider_assessment_verify_ref_id_for_skills = fields.Many2one('provider.assessment', string='provider_assessment_verify_ref')
	learner_id = fields.Many2one('hr.employee', string='Learner', required=True)
	assessors_id = fields.Many2one("hr.employee", string='Assessors', domain=[('is_assessors', '=', True)])
	moderators_id = fields.Many2one("hr.employee", string='Moderator', domain=[('is_moderators', '=', True)])
	learner_identity_number = fields.Char(string='Learner Number', track_visibility='onchange')
	identification_id = fields.Char(string="National Id", track_visibility='onchange')
	timetable_id = fields.Many2one("learner.timetable", 'TimeTable')
	verify = fields.Boolean(string="Verified")
#    qual_learner_assessment_verify_line_id = fields.Many2many('provider.qualification', 'verify_asse_qual_rel', 'qualification_verify_id', 'qual_learner_assessment_verify_line_id', string='Qualification')
#    skill_learner_assessment_verify_line_id = fields.Many2many('skills.programme', 'verify_asse_skills_rel', 'skills_verify_id', 'skill_learner_assessment_verify_line_id', string='Skills')
#    unit_standards_learner_assessment_verify_line_id = fields.Many2many('provider.qualification.line', 'verify_asse_unit_rel', 'unit_standards_verify_id', 'unit_standards_learner_assessment_verify_line_id', string='Unit Standards')
	comment = fields.Char(string="Comment")

	skill_learner_assessment_verify_line_id = fields.Many2many('skills.programme', 'skills_assessment_verified_rel', 'skills_verify_id', 'skill_learner_assessment_verify_line_id', string='Skills')
	skill_unit_standards_learner_assessment_verify_line_id = fields.Many2many('skills.programme.unit.standards', 'skills_unit_assessment_verified_rel', 'skills_unit_standards_verify_id', 'skill_unit_standards_learner_assessment_verify_line_id', string='Skills Unit Standards')


learner_assessment_verify_line_for_skills()

class learner_assessment_evaluate_line_for_skills(models.Model):
	_name = 'learner.assessment.evaluate.line.for.skills'

	provider_assessment_evaluate_ref_id_for_skills = fields.Many2one('provider.assessment', string='provider_assessment_Evaluate_ref')
	learner_id = fields.Many2one('hr.employee', string='Learner', required=True)
	assessors_id = fields.Many2one("hr.employee", string='Assessors', domain=[('is_assessors', '=', True)])
	moderators_id = fields.Many2one("hr.employee", string='Moderator', domain=[('is_moderators', '=', True)])
	learner_identity_number = fields.Char(string='Learner Number', track_visibility='onchange')
	identification_id = fields.Char(string="National Id", track_visibility='onchange')
	timetable_id = fields.Many2one("learner.timetable", 'TimeTable')
	evaluate = fields.Boolean(string="Evaluated")
#    qual_learner_assessment_evaluate_line_id = fields.Many2many('provider.qualification', 'evaluate_asse_qual_rel', 'qualification_verify_id', 'qual_learner_assessment_verify_line_id', string='Qualification')
#    skill_learner_assessment_evaluate_line_id = fields.Many2many('skills.programme', 'evaluate_asse_skills_rel', 'skills_verify_id', 'skill_learner_assessment_verify_line_id', string='Skills')
#    unit_standards_learner_assessment_evaluate_line_id = fields.Many2many('provider.qualification.line', 'evaluate_asse_unit_rel', 'unit_standards_verify_id', 'unit_standards_learner_assessment_verify_line_id', string='Unit Standards')
	comment = fields.Char(string="Comment")

	skill_learner_assessment_evaluate_line_id = fields.Many2many('skills.programme', 'skills_assessment_evaluate_rel', 'skills_verify_id', 'skill_learner_assessment_verify_line_id', string='Skills')
	skill_unit_standards_learner_assessment_evaluate_line_id = fields.Many2many('skills.programme.unit.standards', 'skills_unit_assessment_evaluate_rel', 'skills_unit_standards_verify_id', 'skill_unit_standards_learner_assessment_verify_line_id', string='Skills Unit Standards')

learner_assessment_evaluate_line_for_skills()

class learner_assessment_achieved_line_for_skills(models.Model):
	_name = 'learner.assessment.achieved.line.for.skills'

	provider_assessment_achieved_ref_id_for_skills = fields.Many2one('provider.assessment', string='provider_assessment_achieved_ref')
	learner_id = fields.Many2one('hr.employee', string='Learner', required=True)
	assessors_id = fields.Many2one("hr.employee", string='Assessors', domain=[('is_assessors', '=', True)])
	moderators_id = fields.Many2one("hr.employee", string='Moderator', domain=[('is_moderators', '=', True)])
	learner_identity_number = fields.Char(string='Learner Number', track_visibility='onchange')
	identification_id = fields.Char(string="National Id", track_visibility='onchange')
	timetable_id = fields.Many2one("learner.timetable", 'TimeTable')
	is_learner_achieved = fields.Boolean('Achieved')
#     qual_learner_assessment_achieved_line_id = fields.Many2many('provider.qualification', 'achieved_asse_qual_rel', 'qualification_achieved_id', 'qual_achieve_learner_assessment_line_id', string='Qualification')
#     skill_learner_assessment_achieved_line_id = fields.Many2many('skills.programme', 'achieved_asse_skills_rel', 'skills_achieved_id', 'skill_learner_assessment_achieve_line_id', string='Skills')
#     unit_standards_learner_assessment_achieved_line_id = fields.Many2many('provider.qualification.line', 'achieved_asse_unit_rel', 'unit_standards_achieved_id', 'unit_standards_learner_assessment_achieve_line_id', string='Unit Standards')

	skill_learner_assessment_achieved_line_id = fields.Many2many('skills.programme','skills_assessment_achieved_rel', 'skills_achieved_id', 'skill_learner_assessment_achieved_line_id', string='Skills')
	skill_unit_standards_learner_assessment_achieved_line_id = fields.Many2many('skills.programme.unit.standards','skills_unit_assessment_achieved_rel', 'skills_unit_standards_achieved_id', 'skill_unit_standards_learner_assessment_achieved_line_id', string='Skills Unit Standards')

learner_assessment_achieved_line_for_skills()
