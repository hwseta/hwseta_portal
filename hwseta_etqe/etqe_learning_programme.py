from openerp.exceptions import Warning
from openerp import models, fields, tools, api, _

###############################
## LEARNING PROGRAMME MASTER ##
###############################


class etqe_learning_programme(models.Model):
    _name = 'etqe.learning.programme'
    _description = 'Learning Programme'

    @api.model
    def _search(self, args, offset=0, limit=80, order=None, count=False, access_rights_uid=None):
        user = self._uid
        user_obj = self.env['res.users']
        user_data = user_obj.browse(user)
        if self._context.get('model') == 'learning.programme.learner.rel':
            if user_data.partner_id.provider:
                lp_lst = []
                for line in self.env.user.partner_id.learning_programme_ids:
                    self._cr.execute("select id from etqe_learning_programme where seta_branch_id=1 and id =%s"%(line.learning_programme_id.id))
                    lp_id = self._cr.fetchone()
                    if lp_id:
                        lp_lst.append(lp_id[0])
                args.append(('id', 'in', lp_lst))
                return super(etqe_learning_programme, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
        return super(etqe_learning_programme, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
    
    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        res = []
        for record in self:
            rec_str = ''
            if record.code:
                rec_str += '[' + record.code + '] '
            if record.name:
                rec_str += record.name
            res.append((record.id, rec_str))
        return res

    @api.model
    def name_search(self, name='', args=[], operator='ilike', limit=1000):
        args += ['|', ('name', operator, name), ('code', operator, name)]
        cuur_ids = self.search(args, limit=limit)
        return cuur_ids.name_get()

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ Override read_group to add Label for boolean field status """
        ret_val = super(etqe_learning_programme, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for rt in ret_val:
            if rt.has_key('is_archive'):
                if rt.get('is_archive', True):
                    rt['is_archive'] = 'Archive'
        return ret_val

    @api.one
    @api.depends('unit_standards_line.selection')
    def _compute_total_credit(self):
        total_credit = 0
        for lp in self:
            for lp_line in lp.unit_standards_line:
                if lp_line.selection == True:
                    if lp_line.level3:
                        total_credit += int(lp_line.level3)
            lp.total_credit = total_credit

    _sql_constraints = [('lp_code_uniq', 'unique(code)',
                         'Learning Programme Code must be unique!')]

    name = fields.Char(string='Learning Programme Title', required=True)
    code = fields.Char(string='Learning Programme ID', required=True)
    qualification_id = fields.Many2one(
        'provider.qualification', 'Qualification', required=True)
    saqa_qual_id = fields.Char(string='SAQA QUAL ID ')
    applicant = fields.Char(string='Applicant')
    notes = fields.Text(string='Comment')
    if_us = fields.Boolean(string='US')
    pn_level = fields.Char(string='PRE-2009 NQF LEVEL')
    n_level = fields.Char(string='NQF LEVEL')
    total_credit = fields.Integer(
        string="Total Credit", compute="_compute_total_credit", store=True)
    unit_standards_line = fields.One2many(
        'etqe.learning.programme.unit.standards', 'learning_programme_id', 'Unit Standards')
    seta_branch_id = fields.Many2one('seta.branches', 'Seta Branch')
    is_archive = fields.Boolean('Archive')
    '''FIELDS FOR ASSESSMENT '''
    lp_id = fields.Many2one(
        'learner.assessment.line.for.lp', string='Learning Programme')
    lp_verify_id = fields.Many2one(
        'learner.assessment.verify.line.for.lp', string='Learning Programme')
    lp_achieve_id = fields.Many2one(
        'learner.assessment.achieve.line.for.lp', string='Learning Programme')
    lp_achieved_id = fields.Many2one(
        'learner.assessment.achieved.line.for.lp', string='Learning Programme')

    @api.multi
    def onchange_qualification(self, qualification_id):
        unit_standards = []
        qual_list = []
        qualification_obj = self.env['provider.qualification'].search(
            [('seta_branch_id', '=', '11')])
        if qualification_obj:
            for q in qualification_obj:
                qual_list.append(q.id)
        if qualification_id:
            qualification_obj = self.env[
                'provider.qualification'].browse(qualification_id)
            core_lst, funda_lst, elect_lst = [], [], []
            for qualification_lines in qualification_obj.qualification_line:
                if qualification_lines.type == 'Core':
                    val = {
                        'name': qualification_lines.title,
                        'type': qualification_lines.type,
                        'id_no': qualification_lines.id_no,
                        'title': qualification_lines.title,
                        'level1': qualification_lines.level1,
                        'level2': qualification_lines.level2,
                        'level3': qualification_lines.level3,
                        'selection': True,
                        'type_key': 2,
                    }
                    core_lst.append((0, 0, val))
                if qualification_lines.type == 'Fundamental':
                    val = {
                        'name': qualification_lines.title,
                        'type': qualification_lines.type,
                        'id_no': qualification_lines.id_no,
                        'title': qualification_lines.title,
                        'level1': qualification_lines.level1,
                        'level2': qualification_lines.level2,
                        'level3': qualification_lines.level3,
                        'selection': True,
                        'type_key': 1,
                    }
                    funda_lst.append((0, 0, val))
                if qualification_lines.type == 'Elective':
                    val = {
                        'name': qualification_lines.title,
                        'type': qualification_lines.type,
                        'id_no': qualification_lines.id_no,
                        'title': qualification_lines.title,
                        'level1': qualification_lines.level1,
                        'level2': qualification_lines.level2,
                        'level3': qualification_lines.level3,
                        'selection': False,
                        'type_key': 3,
                    }
                    elect_lst.append((0, 0, val))
            unit_standards = core_lst + funda_lst + elect_lst
            return {'value': {'unit_standards_line': unit_standards, 'saqa_qual_id': qualification_obj.saqa_qual_id}}
        return {'domain': {'qualification_id': [('id', 'in', qual_list)]}}

    @api.multi
    def onchange_archive(self, is_archive):
        res = {}
        if is_archive:
            res.update({'value': {'seta_branch_id': None, }})
        return res

    @api.multi
    def onchange_seta_branch_id(self, seta_branch_id):
        res = {}
        if seta_branch_id == 1:
            res.update({'value': {'is_archive': False, }})
        return res

    @api.multi
    @api.onchange('code')
    def onchange_saqa_qual_id(self):
        if self.code:
            is_exist_code = self.env['etqe.learning.programme'].search(
                [('code', '=', str(self.code).split())])
            if is_exist_code:
                self.code = ''
                return {'warning': {'title': 'Duplicate Record', 'message': 'Please enter unique Learning Programme ID'}}
        return {}

    @api.multi
    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            is_exist_name = self.env['etqe.learning.programme'].search(
                [('name', '=', str(self.name).strip())])
            if is_exist_name:
                self.name = ''
                return {'warning': {'title': 'Duplicate Record', 'message': 'Please enter unique Learning Programme Name'}}
        return {}
etqe_learning_programme()


class etqe_learning_programme_unit_standards(models.Model):
    _name = 'etqe.learning.programme.unit.standards'
    _description = 'Etqe Learning Programme Unit Standards'
    _rec_name = 'id_no'
    name = fields.Char(string='Name', required=True)
#     type = fields.Char(string='Type', required=True)
    type = fields.Selection([
        ('Core', 'Core'),
        ('Fundamental', 'Fundamental'),
        ('Elective', 'Elective'),
    ], string='Type', required=True, track_visibility='onchange')
    id_no = fields.Char(string='ID NO')
    title = fields.Char(string='UNIT STANDARD TITLE', required=True)
    level1 = fields.Char(string='PRE-2009 NQF LEVEL')
    level2 = fields.Char(string='NQF LEVEL')
    level3 = fields.Char(string='CREDITS')
    selection = fields.Boolean(string='SELECT', track_visibility='onchange')
    type_key = fields.Integer("Type Key")
    learning_programme_id = fields.Many2one(
        'etqe.learning.programme', 'ETQE Learning Programme Reference', ondelete='cascade')
    seta_approved_lp = fields.Boolean(
        string='SETA Learning Material', track_visibility='onchange')
    provider_approved_lp = fields.Boolean(
        string='PROVIDER Learning Material', track_visibility='onchange')

    '''FIELDS FOR ASSESSMENT '''
    lp_unit_standards_id = fields.Many2one(
        'learner.assessment.line.for.lp', string='Learning Programme Unit Standards')
    lp_unit_standards_verify_id = fields.Many2one(
        'learner.assessment.verify.line.for.lp', string='Learning Programme Unit Standards')
    lp_unit_standards_achieve_id = fields.Many2one(
        'learner.assessment.achieve.line.for.lp', string='Learning Programme Unit Standards')
    lp_unit_standards_achieved_id = fields.Many2one(
        'learner.assessment.achieved.line.for.lp', string='Learning Programme Unit Standards')

    @api.multi
    @api.onchange('seta_approved_lp')
    def onchange_seta_approved_lp(self):
        if self.seta_approved_lp:
            self.provider_approved_lp = False
    
    @api.multi
    @api.onchange('provider_approved_lp')
    def onchange_provider_approved_lp(self):
        if self.provider_approved_lp:
            self.seta_approved_lp = False

    @api.multi
    @api.onchange('type')
    def onchange_type(self):
        if self.type == 'Core':
            self.type_key = 1
        elif self.type == 'Fundamental':
            self.type_key = 2
        elif self.type == 'Elective':
            self.type_key = 3


etqe_learning_programme_unit_standards()

################################################################
# PROVIDER MASTER LEARNING PROGRAMME
################################################################

# FOR LEARNING PROGRAMME UNIT STANDARDS


class learning_programme_unit_standards_master_rel(models.Model):
    _name = 'learning.programme.unit.standards.master.rel'
    _description = 'Learning Programme Unit Standards Master Rel'
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
    learning_programme_id = fields.Many2one(
        'learning.programme.master.rel', 'Learning Programme Reference', ondelete='cascade')
    seta_approved_lp = fields.Boolean(
        string='SETA Learning Material', track_visibility='onchange')
    provider_approved_lp = fields.Boolean(
        string='PROVIDER Learning Material', track_visibility='onchange')

learning_programme_unit_standards_master_rel()

# FOR LEARNING PROGRAMME


class learning_programme_master_rel(models.Model):
    _name = 'learning.programme.master.rel'
    _description = 'Learning Programme master Rel'

    learning_programme_id = fields.Many2one(
        "etqe.learning.programme", 'Learning Programme')
    unit_standards_line = fields.One2many(
        'learning.programme.unit.standards.master.rel', 'learning_programme_id', 'Unit Standards')
    learning_programme_partner_rel_id = fields.Many2one(
        'res.partner', 'Provider Partner Reference')
    lp_saqa_id = fields.Char("SAQA QUAL ID")
    status = fields.Selection([('draft', 'Draft'), ('waiting_approval', 'Waiting Approval'), (
        'approved', 'Approved'), ('rejected', 'Rejected')], string="Status", default='draft')
    request_send = fields.Boolean(string='Send Request', default=False)
    approval_request = fields.Boolean(string='Approval Request', default=False)
    reject_request = fields.Boolean(string="Reject Request", default=False)
    assessors_id = fields.Many2one("hr.employee", string='Assessor', domain=[
                                   ('is_active_assessor', '=', True), ('is_assessors', '=', True)])
    assessor_sla_document = fields.Many2one(
        'ir.attachment', string="SLA Document")
    moderators_id = fields.Many2one("hr.employee", string='Moderator', domain=[
                                    ('is_active_moderator', '=', True), ('is_moderators', '=', True)])
    moderator_sla_document = fields.Many2one(
        'ir.attachment', string="SLA Document")
    assessor_no = fields.Char(string = "Assessor ID")
    moderator_no = fields.Char(string = "Moderator ID")

    @api.multi
    def action_send_request(self):
        self.write({'status': 'waiting_approval', 'request_send': True})

    @api.multi
    def action_approved_request(self):
        self.write({'status': 'approved', 'approval_request': True})

    @api.multi
    def action_rejected_request(self):
        self.write({'status': 'rejected', 'reject_request': True})

    @api.multi
    def onchange_learning_programme(self, learning_programme_id):
        #         res = {}
        unit_standards = []
        if learning_programme_id:
            learning_programme_obj = self.env[
                'etqe.learning.programme'].browse(learning_programme_id)
            for unit_standards_lines in learning_programme_obj.unit_standards_line:
                if unit_standards_lines.selection == True:
                    val = {
                        'name': unit_standards_lines.name,
                        'type': unit_standards_lines.type,
                        'id_no': unit_standards_lines.id_no,
                        'title': unit_standards_lines.title,
                        'level1': unit_standards_lines.level1,
                        'level2': unit_standards_lines.level2,
                        'level3': unit_standards_lines.level3,
                        'selection': True,
                        'seta_approved_lp': unit_standards_lines.seta_approved_lp,
                        'provider_approved_lp': unit_standards_lines.provider_approved_lp,
                    }
                    unit_standards.append((0, 0, val))
            return {'value': {'unit_standards_line': unit_standards, 'lp_saqa_id': learning_programme_obj.saqa_qual_id}}
        return {}
learning_programme_master_rel()

################################################################
# PROVIDER MASTER CAMPUS LEARNING PROGRAMME                    #
################################################################
# FOR LEARNING PROGRAMME UNITS STANDARDS


class learning_programme_unit_standards_master_campus_rel(models.Model):
    _name = 'learning.programme.unit.standards.master.campus.rel'
    _description = 'Learning Programme Unit Standards Master Campus Rel'
    _rec_name = 'type'
    name = fields.Char(string='Name')
    type = fields.Char(string='Type', required=True)
    id_no = fields.Char(string='ID NO')
    title = fields.Char(string='UNIT STANDARD TITLE', required=True)
    level1 = fields.Char(string='PRE-2009 NQF LEVEL')
    level2 = fields.Char(string='NQF LEVEL')
    level3 = fields.Char(string='CREDITS')
    selection = fields.Boolean(string='SELECT')
    learning_programme_id = fields.Many2one(
        'learning.programme.master.campus.rel', 'Learning Programme Reference', ondelete='cascade')
    seta_approved_lp = fields.Boolean(
        string='SETA Learning Material', track_visibility='onchange')
    provider_approved_lp = fields.Boolean(
        string='PROVIDER Learning Material', track_visibility='onchange')

learning_programme_unit_standards_master_campus_rel()

# FOR LEARNING PROGRAMME


class learning_programme_master_campus_rel(models.Model):
    _name = 'learning.programme.master.campus.rel'
    _description = 'Learning Programme Master Campus Rel'

    learning_programme_id = fields.Many2one(
        "etqe.learning.programme", 'Learning Programme')
    unit_standards_line = fields.One2many(
        'learning.programme.unit.standards.master.campus.rel', 'learning_programme_id', 'Unit Standards')
    learning_programme_partner_campus_rel_id = fields.Many2one(
        'res.partner', 'Provider Accreditation Reference')
    lp_saqa_id = fields.Char("SAQA QUAL ID")

    @api.multi
    def onchange_learning_programme(self, learning_programme_id):
        unit_standards = []
        if learning_programme_id:
            learning_programme_obj = self.env[
                'etqe.learning.programme'].browse(learning_programme_id)
            for unit_standards_lines in learning_programme_obj.unit_standards_line:
                if unit_standards_lines.selection == True:
                    val = {
                        'name': unit_standards_lines.name,
                        'type': unit_standards_lines.type,
                        'id_no': unit_standards_lines.id_no,
                        'title': unit_standards_lines.title,
                        'level1': unit_standards_lines.level1,
                        'level2': unit_standards_lines.level2,
                        'level3': unit_standards_lines.level3,
                        'selection': True,
                        'seta_approved_lp': unit_standards_lines.seta_approved_lp,
                        'provider_approved_lp': unit_standards_lines.provider_approved_lp,
                    }
                    unit_standards.append((0, 0, val))
            return {'value': {'unit_standards_line': unit_standards, 'lp_saqa_id': learning_programme_obj.saqa_qual_id}}
        return {}
learning_programme_master_campus_rel()

################################################################
# LEARNER REGISTRATION AND MASTER LEARNING PROGRAMME           #
################################################################

# FOR LEARNING PROGRAMME UNIT STANDARDS


class learning_programme_unit_standards_learner_rel(models.Model):
    _name = 'learning.programme.unit.standards.learner.rel'
    _description = 'Learning Programme Unit Standards Learner Rel'
    _rec_name = 'type'
    name = fields.Char(string='Name')
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
    learning_programme_id = fields.Many2one(
        'learning.programme.learner.rel', 'Learning Programme Reference', ondelete='cascade')
    seta_approved_lp = fields.Boolean(
        string='SETA Learning Material', track_visibility='onchange')
    provider_approved_lp = fields.Boolean(
        string='PROVIDER Learning Material', track_visibility='onchange')
    achieve = fields.Boolean("ACHIEVE", default=False)
learning_programme_unit_standards_learner_rel()

# FOR LEARNING PROGRAMME


class learning_programme_learner_rel(models.Model):
    _name = 'learning.programme.learner.rel'
    _description = 'Learning Programme Learner Rel'

    lp_saqa_id = fields.Char(string='SAQA QUAL ID')
    learning_programme_id = fields.Many2one(
        "etqe.learning.programme", 'Learning Programme', required=True)
    unit_standards_line = fields.One2many(
        'learning.programme.unit.standards.learner.rel', 'learning_programme_id', 'Unit Standards')
    learning_programme_learner_rel_id = fields.Many2one(
        'learner.registration', 'Learner Registration Reference')
    select = fields.Boolean("Selection", default=True)
    learning_programme_learner_rel_ids = fields.Many2one(
        'hr.employee', 'Learner Master Reference')
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    assessors_id = fields.Many2one("hr.employee", string='Assessors', domain=[
                                   ('is_active_assessor', '=', True), ('is_assessors', '=', True)])
    assessor_date = fields.Date("Assessor Date")
    moderators_id = fields.Many2one("hr.employee", string='Moderators', domain=[
                                    ('is_active_moderator', '=', True), ('is_moderators', '=', True)])
    moderator_date = fields.Date("Moderator Date")
    minimum_credits = fields.Integer(
        related="learning_programme_id.total_credit", string="Minimum Credits")
    total_credits = fields.Integer(
        compute="_cal_limit", string="Total Credits", store=True)
    batch_id = fields.Many2one('batch.master', string='Batch')
    provider_id = fields.Many2one(
        'res.partner', string="Provider", track_visibility='onchange', default=lambda self: self.env.user.partner_id)
    approval_date = fields.Date()
    is_learner_achieved = fields.Boolean(string="Competent", default=False)
    is_complete = fields.Boolean("Achieve", default=False)
    certificate_no = fields.Char("Certificate No.")
    certificate_date = fields.Date("Certificate Date")
    lp_status = fields.Char("Status")

    @api.model
    def default_get(self, fields):
        context = self._context
        if context is None:
            context = {}
        res = super(learning_programme_learner_rel, self).default_get(fields)
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
    def onchange_learning_programme(self, learning_programme_id):
        user = self._uid
        user_obj = self.env['res.users']
        user_data = user_obj.browse(user)
        assessors_lst, moderators_lst, batch_lst, unit_standards, lp_id = [], [], [], [], []
        if user_data.partner_id.provider:
            if self.env.user.partner_id.assessors_ids:
                for assessor in self.env.user.partner_id.assessors_ids:
                    if assessor.assessors_id.is_active_assessor:
                        assessors_lst.append(assessor.assessors_id.id)
            if self.env.user.partner_id.moderators_ids:
                for moderator in self.env.user.partner_id.moderators_ids:
                    if moderator.moderators_id.is_active_moderator:
                        moderators_lst.append(moderator.moderators_id.id)
            for line in self.env.user.partner_id.learning_programme_ids:
                learning_programming_obj = self.env['etqe.learning.programme'].search(
                    [('seta_branch_id', '=', '11'), ('id', '=', line.learning_programme_id.id)])
                if learning_programming_obj:
                    lp_id.append(learning_programming_obj.id)
            if self.env.user.partner_id.provider_batch_ids:
                for batch in self.env.user.partner_id.provider_batch_ids:
                    if batch.batch_master_id.qual_skill_batch == 'lp' and batch.batch_status == 'open':
                        batch_lst.append(batch.batch_master_id.id)
        if not user_data.partner_id.provider:
            batch_obj = self.sudo().env['batch.master'].search([('qual_skill_batch', '=', 'lp')])
            if batch_obj:
                for obj in batch_obj:
                    batch_lst.append(obj.id)
         # Commented following code Giving problem when we fetch non-SA learners because context is passed based on identification id
        '''Code to avoid those learning programme which are already exist in learner master in extension of scope learner process'''
#         if self._context.get('existing_learner') == True and not self._context.get('learner_master_id_number'):
#             return {'warning': {'title': 'Warning', 'message': 'Please Enter Identification Number to fetch existing learner details!!'}}
        if self._context.get('existing_learner') == True and self._context.get('learner_master_id_number'):
            learner_master_object = self.env['hr.employee'].search(
                [('learner_identification_id', '=', self._context.get('learner_master_id_number'))])
            if learner_master_object:
                learner_master_lp_obj = self.env['learning.programme.learner.rel'].search(
                    [('learning_programme_learner_rel_ids', '=', learner_master_object.id)])
                if learner_master_lp_obj:
                    for master_lp in learner_master_lp_obj:
                        if master_lp.learning_programme_id.id in lp_id:
                            lp_id.remove(master_lp.learning_programme_id.id)
        if learning_programme_id:
            learning_programme_obj = self.env['etqe.learning.programme'].search(
                [('seta_branch_id', '=', '11'), ('id', '=', learning_programme_id)])
            if learning_programme_obj:
                for unit_standards_lines in learning_programme_obj.unit_standards_line:
                    if unit_standards_lines.selection == True:
                        val = {
                            'name': unit_standards_lines.name,
                            'type': unit_standards_lines.type,
                            'id_no': unit_standards_lines.id_no,
                            'title': unit_standards_lines.title,
                            'level1': unit_standards_lines.level1,
                            'level2': unit_standards_lines.level2,
                            'level3': unit_standards_lines.level3,
                            'selection': True,
                            'seta_approved_lp': unit_standards_lines.seta_approved_lp,
                            'provider_approved_lp': unit_standards_lines.provider_approved_lp,
                        }
                        unit_standards.append((0, 0, val))
                return {'value': {'unit_standards_line': unit_standards, 'lp_saqa_id': learning_programme_obj.saqa_qual_id, 'qualification_id': learning_programme_obj.qualification_id.id}}
        elif lp_id:
            return {'domain': {'learning_programme_id': [('id', 'in', lp_id)], 'batch_id': [('id', 'in', batch_lst)], 'assessors_id': [('id', 'in', assessors_lst)], 'moderators_id': [('id', 'in', moderators_lst)]}}
        elif not learning_programme_id and not user_data.partner_id.provider:
            lp_lst = []
            lp_obj = self.env['etqe.learning.programme'].search(
                [('seta_branch_id', '=', '11')])
            if lp_obj:
                for obj in lp_obj:
                    lp_lst.append(obj.id)
                return {'domain': {'learning_programme_id': [('id', 'in', lp_lst)], 'batch_id': [('id', 'in', batch_lst)]}}
        return {'domain': {'learning_programme_id': [('id', 'in', [])], 'batch_id': [('id', 'in', batch_lst)]}}

    @api.multi
    def onchange_assessors_id(self, assessors_id):
        res = {}
        if not assessors_id:
            return res
        if assessors_id:
            assessor_brw_id = self.env['hr.employee'].search(
                [('id', '=', assessors_id)])
            res.update({'value': {'assessor_date': assessor_brw_id.end_date}})
        return res

    @api.multi
    def onchange_moderators_id(self, moderators_id):
        res = {}
        if not moderators_id:
            return res
        if moderators_id:
            moderator_brw_id = self.env['hr.employee'].search(
                [('id', '=', moderators_id)])
            res.update(
                {'value': {'moderator_date': moderator_brw_id.end_date}})
        return res

    @api.model
    def _search(self, args, offset=0, limit=80, order=None, count=False, access_rights_uid=None):
        user = self._uid
        user_obj = self.env['res.users']
        user_data = user_obj.browse(user)
        user_groups = user_data.groups_id
        for group in user_groups:
            if group.name in ['ETQE Manager', 'ETQE Executive Manager', 'ETQE Provincial Manager', 'ETQE Officer', 'ETQE Provincial Officer', 'ETQE Administrator', 'ETQE Provincial Administrator', 'Applicant Skills Development Provider', 'CEO']:
                return super(learning_programme_learner_rel, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
        if user == 1:
            return super(learning_programme_learner_rel, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
        self._cr.execute("select id from learning_programme_learner_rel where provider_id=%s or create_uid = %s" % (
            user_data.partner_id.id, user_data.id))
        learner_ids = self._cr.fetchall()
        args.append(('id', 'in', learner_ids))
        return super(learning_programme_learner_rel, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

learning_programme_learner_rel()

################################################################
# LEARNER ASSESSMENT FOR LEARNING PROGRAMME                    #
################################################################


class learner_assessment_line_for_lp(models.Model):
    _name = 'learner.assessment.line.for.lp'

    @api.multi
    def _get_provider(self):
        ''' Getting provider from Assessment via context passed in xml.'''
        context = self._context
        provider_id = context.get('provider', False)
        return provider_id
#     name = fields.Char(string='Name')
    provider_assessment_ref_id_for_lp = fields.Many2one(
        'provider.assessment', string='provider_assessment_ref')
#     learner_id = fields.Many2one('etqe.learner', string='Learner', required=True)
    learner_id = fields.Many2one(
        'hr.employee', string='Learners', required=True)
    assessors_id = fields.Many2one(
        "hr.employee", string='Assessors', domain=[('is_assessors', '=', True)])
    moderators_id = fields.Many2one(
        "hr.employee", string='Moderator', domain=[('is_moderators', '=', True)])
    learner_identity_number = fields.Char(
        string='Learner Number', track_visibility='onchange')
    timetable_id = fields.Many2one("learner.timetable", 'TimeTable')
    verify = fields.Boolean(string="Verification")
    provider_id = fields.Many2one(
        'res.partner', string="Provider", track_visibility='onchange', default=_get_provider)
    identification_id = fields.Char(string="National Id",)
    lp_learner_assessment_line_id = fields.Many2many(
        'etqe.learning.programme', 'lp_assessment_line_rel','lp_id', 'lp_learner_assessment_line_id', string='Learning Programme')
    lp_unit_standards_learner_assessment_line_id = fields.Many2many(
        'etqe.learning.programme.unit.standards', 'lp_unit_assessment_line_rel', 'lp_unit_standards_id', 'lp_unit_standards_learner_assessment_line_id', string='Learning Programme Unit Standards')

    @api.multi
    def onchange_assessors_id(self, assessors_id, moderators_id):
        res = {}
        if not assessors_id and moderators_id:
            return res
        if assessors_id and moderators_id:
            if assessors_id == moderators_id:
                res.update({
                    'value': {
                        'assessors_id': '',
                        'moderators_id': '',
                    },
                    'warning': {'title': 'Error!', 'message': 'Assessor  And Moderator Cant be same in a row'},
                })
        return res

    @api.model
    def default_get(self, fields):
        context = self._context
        if context is None:
            context = {}
        res = super(learner_assessment_line_for_lp, self).default_get(fields)
        provider_id = context.get('provider', False)
        if provider_id:
            res.update(provider_id=provider_id)
        return res

    @api.multi
    def onchange_provider(self, provider_id):
        learner_list = []
        if self._uid == 1:
            etqe_learner_obj = self.env['hr.employee'].search(
                [('is_learner', '=', True), ('provider_learner', '=', True), ('state', 'in', ['active', 'replacement'])])
            for learner in etqe_learner_obj:
                learner_list.append(learner.id)
        else:
            etqe_learner_obj = self.env['hr.employee'].search([('is_learner', '=', True), ('provider_learner', '=', True), (
                'state', 'in', ['active', 'replacement'])])  # ,('logged_provider_id','=',user.partner_id.id)
            for learner in etqe_learner_obj:
                for qual_line in learner.learner_qualification_ids:
                    provider = qual_line.provider_id.id
                    if provider:
                        if provider == self.env.user.partner_id.id:
                            learner_list.append(learner.id)
        # Load qualification as per provider
        qualification = []
        if self._uid == 1:
            qualification_obj = self.env['provider.qualification'].search([])
            for quali_id in qualification_obj:
                qualification.append(quali_id.id)
        else:
            provider_obj = self.env['res.partner'].search(
                [('provider', '=', True), ('id', '=', provider_id)])
            if provider_obj.qualification_ids:
                for qualification_id in provider_obj.qualification_ids:
                    for quali_id in qualification_id.qualification_id:
                        qualification.append(quali_id.id)
            elif provider_obj.qualification_campus_ids:
                for qualification_campus_id in provider_obj.qualification_campus_ids:
                    for quali_id in qualification_campus_id.qualification_id:
                        qualification.append(quali_id.id)
        # Load skill programme as per provider
        skill_programme = []
        if self._uid == 1:
            skill_obj = self.env['skills.programme'].search([])
            for quali_id in skill_obj:
                skill_programme.append(quali_id.id)
        else:
            provider_obj = self.env['res.partner'].search(
                [('provider', '=', True), ('id', '=', provider_id)])
            if provider_obj.skills_programme_ids:
                for skill_ids in provider_obj.skills_programme_ids:
                    for skill_id in skill_ids.skills_programme_id:
                        skill_programme.append(skill_id.id)
            elif provider_obj.skills_programme_campus_ids:
                for skill_ids in provider_obj.skills_programme_campus_ids:
                    for skill_id in skill_ids.skills_programme_id:
                        skill_programme.append(skill_id.id)
        # Load Learning programme as per provider changes added by Ganesh
        learning_programme = []
        if self._uid == 1:
            lp_obj = self.env['etqe.learning.programme'].search([])
            for lp_id in lp_obj:
                learning_programme.append(lp_id.id)
        else:
            provider_obj = self.env['res.partner'].search(
                [('provider', '=', True), ('id', '=', provider_id)])
            if provider_obj.learning_programme_ids:
                for lp_ids in provider_obj.learning_programme_ids:
                    for lp_id in lp_ids.learning_programme_id:
                        learning_programme.append(lp_id.id)
            elif provider_obj.learning_programme_campus_ids:
                for lp_ids in provider_obj.learning_programme_campus_ids:
                    for lp_id in lp_ids.learning_programme_id:
                        learning_programme.append(lp_id.id)
#         load Assessor as per provider
        assessors_list = []
        if self._uid == 1:
            assessor_obj = self.env['hr.employee'].search(
                [('is_assessors', '=', True)])
            for assessor in assessor_obj:
                assessors_list.append(assessor.id)
        else:
            provider_obj = self.env['res.partner'].search(
                [('provider', '=', True), ('id', '=', provider_id)])
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
            moderator_obj = self.env['hr.employee'].search(
                [('is_moderators', '=', True)])
            for moderator in moderator_obj:
                moderator_list.append(moderator.id)
        else:
            provider_obj = self.env['res.partner'].search(
                [('provider', '=', True), ('id', '=', provider_id)])
            if provider_obj.moderators_ids:
                for moderator_id in provider_obj.moderators_ids:
                    for moderator in moderator_id.moderators_id:
                        moderator_list.append(moderator.id)
            elif provider_obj.moderators_campus_ids:
                for moderators_campus_id in provider_obj.moderators_campus_ids:
                    for moderator in moderators_campus_id.moderators_id:
                        moderator_list.append(moderator.id)
        return {'domain': {'learner_id': [('id', 'in', list(set(learner_list)))],
                           'qual_learner_assessment_line_id': [('id', 'in', qualification)],
                           'skill_learner_assessment_line_id': [('id', 'in', skill_programme)],
                           'lp_learner_assessment_line_id': [('id', 'in', learning_programme)],
                           'assessors_id': [('id', 'in', assessors_list)],
                           'moderators_id': [('id', 'in', moderator_list)]
                           }}

    @api.multi
    def onchange_learner_reg_no(self, learner_identity_number):
        res = {}
        if not learner_identity_number:
            return res

        learner_obj = self.env['hr.employee'].search(
            [('learner_reg_no', '=', learner_identity_number)])
        res.update({
            'value': {
                'learner_id': learner_obj.id,
            }
        })
        return res

    @api.multi
    def onchange_qualification_ids(self, qualification_id):
        res = {}
        unit_standards_list = []
        if not qualification_id[0][2]:
            return res
        for qual_id in qualification_id[0][2]:
            qualification_master = self.env[
                'provider.qualification'].browse(qual_id)
            for unit_standards in qualification_master.qualification_line:
                unit_standards_list.append(unit_standards.id)
        return {'domain': {'unit_standards_learner_assessment_line_id': [('id', 'in', unit_standards_list)]}}

learner_assessment_line_for_lp()


class learner_assessment_achieve_line_for_lp(models.Model):
    _name = 'learner.assessment.achieve.line.for.lp'

    provider_assessment_achieve_ref_id_for_lp = fields.Many2one(
        'provider.assessment', string='provider_assessment_achieve_ref')
    learner_id = fields.Many2one(
        'hr.employee', string='Learner', required=True)

    assessors_id = fields.Many2one(
        "hr.employee", string='Assessors', domain=[('is_assessors', '=', True)])
    moderators_id = fields.Many2one(
        "hr.employee", string='Moderator', domain=[('is_moderators', '=', True)])
    learner_identity_number = fields.Char(
        string='Learner Number', track_visibility='onchange')
    timetable_id = fields.Many2one("learner.timetable", 'TimeTable')
    achieve = fields.Boolean(string="Achieved")
    identification_id = fields.Char(
        string="National Id", track_visibility='onchange')
    lp_learner_assessment_achieve_line_id = fields.Many2many(
        'etqe.learning.programme', 'lp_assessment_achieve_line_rel', 'lp_achieve_id', 'lp_learner_assessment_achieve_line_id', string='Learning Programme')
    lp_unit_standards_learner_assessment_achieve_line_id = fields.Many2many(
        'etqe.learning.programme.unit.standards', 'lp_unit_assessment_achieve_line_rel', 'lp_unit_standards_achieve_id', 'lp_unit_standards_learner_assessment_achieve_line_id', string='Learning Programme Unit Standards')

learner_assessment_achieve_line_for_lp()


class learner_assessment_verify_line_for_lp(models.Model):
    _name = 'learner.assessment.verify.line.for.lp'

    provider_assessment_verify_ref_id_for_lp = fields.Many2one(
        'provider.assessment', string='provider_assessment_verify_ref')
    learner_id = fields.Many2one(
        'hr.employee', string='Learner', required=True)
    assessors_id = fields.Many2one(
        "hr.employee", string='Assessors', domain=[('is_assessors', '=', True)])
    moderators_id = fields.Many2one(
        "hr.employee", string='Moderator', domain=[('is_moderators', '=', True)])
    learner_identity_number = fields.Char(
        string='Learner Number', track_visibility='onchange')
    identification_id = fields.Char(
        string="National Id", track_visibility='onchange')
    timetable_id = fields.Many2one("learner.timetable", 'TimeTable')
    verify = fields.Boolean(string="Verified")
    comment = fields.Char(string="Comment")
    lp_learner_assessment_verify_line_id = fields.Many2many(
        'etqe.learning.programme', 'lp_assessment_verified_rel', 'lp_verify_id', 'lp_learner_assessment_verify_line_id', string='Learning Programme')
    lp_unit_standards_learner_assessment_verify_line_id = fields.Many2many(
        'etqe.learning.programme.unit.standards', 'lp_unit_assessment_verified_rel', 'lp_unit_standards_verify_id', 'lp_unit_standards_learner_assessment_verify_line_id', string='Learning Programme Unit Standards')

learner_assessment_verify_line_for_lp()


class learner_assessment_evaluate_line_for_lp(models.Model):
    _name = 'learner.assessment.evaluate.line.for.lp'

    provider_assessment_evaluate_ref_id_for_lp = fields.Many2one(
        'provider.assessment', string='provider_assessment_Evaluate_ref')
    learner_id = fields.Many2one(
        'hr.employee', string='Learner', required=True)
    assessors_id = fields.Many2one(
        "hr.employee", string='Assessors', domain=[('is_assessors', '=', True)])
    moderators_id = fields.Many2one(
        "hr.employee", string='Moderator', domain=[('is_moderators', '=', True)])
    learner_identity_number = fields.Char(
        string='Learner Number', track_visibility='onchange')
    identification_id = fields.Char(
        string="National Id", track_visibility='onchange')
    timetable_id = fields.Many2one("learner.timetable", 'TimeTable')
    evaluate = fields.Boolean(string="Evaluated")
    comment = fields.Char(string="Comment")
    lp_learner_assessment_evaluate_line_id = fields.Many2many(
        'etqe.learning.programme', 'lp_assessment_evaluate_rel', 'lp_verify_id', 'lp_learner_assessment_verify_line_id', string='Learning Programme')
    lp_unit_standards_learner_assessment_evaluate_line_id = fields.Many2many(
        'etqe.learning.programme.unit.standards', 'lp_unit_assessment_evaluate_rel', 'lp_unit_standards_verify_id', 'lp_unit_standards_learner_assessment_verify_line_id', string='Learning Programme Unit Standards')

learner_assessment_evaluate_line_for_lp()


class learner_assessment_achieved_line_for_lp(models.Model):
    _name = 'learner.assessment.achieved.line.for.lp'

    provider_assessment_achieved_ref_id_for_lp = fields.Many2one(
        'provider.assessment', string='provider_assessment_achieved_ref')
    learner_id = fields.Many2one(
        'hr.employee', string='Learner', required=True)
    assessors_id = fields.Many2one(
        "hr.employee", string='Assessors', domain=[('is_assessors', '=', True)])
    moderators_id = fields.Many2one(
        "hr.employee", string='Moderator', domain=[('is_moderators', '=', True)])
    learner_identity_number = fields.Char(
        string='Learner Number', track_visibility='onchange')
    identification_id = fields.Char(
        string="National Id", track_visibility='onchange')
    is_learner_achieved = fields.Boolean('Achieved') 
    timetable_id = fields.Many2one("learner.timetable", 'TimeTable')
    lp_learner_assessment_achieved_line_id = fields.Many2many(
        'etqe.learning.programme', 'lp_assessment_achieved_rel', 'lp_achieved_id', 'lp_learner_assessment_achieved_line_id', string='Learning Programme')
    lp_unit_standards_learner_assessment_achieved_line_id = fields.Many2many(
        'etqe.learning.programme.unit.standards', 'lp_unit_assessment_achieved_rel', 'lp_unit_standards_achieved_id', 'lp_unit_standards_learner_assessment_achieved_line_id', string='Learning Programme Unit Standards')


learner_assessment_achieved_line_for_lp()

###########################################
## LEARNING PROGRAMME ACCREDITATION REL  ##
###########################################


class learning_programme_accreditation_rel(models.Model):
    _name = 'learning.programme.accreditation.rel'
    _inherit = 'mail.thread'
    _description = 'Learning Programme Accreditation Rel'

    saqa_qual_id = fields.Char(string='SAQA QUAL ID')
    learning_programme_id = fields.Many2one("etqe.learning.programme", 'NAME', track_visibility="always")
    qualification_id = fields.Many2one(
        "provider.qualification", 'QUALIFICATION', ondelete='restrict')
    unit_standards_line = fields.One2many(
        'learning.programme.unit.standards.accreditation.rel', 'learning_programme_id', 'Unit Standards')
    learning_programme_accreditation_rel_id = fields.Many2one(
        'provider.accreditation', 'Provider Accreditation Reference')
    select = fields.Boolean("Selection", default=True)
    verify = fields.Boolean('Verify', default=False, track_visibility="onchange")
    minimum_credits = fields.Integer(
        related="learning_programme_id.total_credit", string="Minimum Credits")
    total_credits = fields.Integer(
        compute="_cal_limit", string="Total Credits", store=True)
    assessors_id = fields.Many2one("hr.employee", string='Assessor Name', domain=[
                                   ('is_active_assessor', '=', True), ('is_assessors', '=', True)])
    assessor_sla_document = fields.Many2one(
        'ir.attachment', string="Assessor SLA Document")
    moderators_id = fields.Many2one("hr.employee", string='Moderator Name', domain=[
                                    ('is_active_moderator', '=', True), ('is_moderators', '=', True)])
    moderator_sla_document = fields.Many2one(
        'ir.attachment', string="Moderator SLA Document")
    assessor_no = fields.Char(string = "Assessor ID")
    moderator_no = fields.Char(string = "Moderator ID")
    
    @api.depends('learning_programme_id')
    @api.onchange('assessor_no')
    def onchange_assessor_no(self):
        if self.assessor_no and self.learning_programme_id:
            assessor = str(self.assessor_no).strip()
            assessor_id = self.env['hr.employee'].search([('is_active_assessor','=', True),('assessor_seq_no','=', assessor)])
            if not assessor_id:
                self.assessor_no = ''
                return {'warning':{'title':'Invalid Assessor Number','message':'Please Enter Valid Assessor Number!!!'}}
            ass_qual_lst =  []
            for qualification in assessor_id.qualification_ids:
                ass_qual_lst.append(qualification.qualification_hr_id.id)
            if ass_qual_lst:
                if self.learning_programme_id.qualification_id.id in ass_qual_lst:
                    self.assessors_id = assessor_id.id
                    return {'domain':{'assessors_id':[('id','in', [assessor_id.id])]}}
                else:
                    self.assessor_no = ''
                    return {'warning':{'title':'Invalid Assessor','message':'This Assessor is not Linked with selected Learning Programme!!'}}
        
    
    @api.depends('learning_programme_id')
    @api.onchange('moderator_no')
    def onchange_moderator_no(self):
        if self.moderator_no and self.learning_programme_id:
            moderator = str(self.moderator_no).strip()
            moderator_id = self.env['hr.employee'].search([('is_active_moderator','=', True),('moderator_seq_no','=', moderator)])
            if not moderator_id:
                self.moderator_no = ''
                return {'warning':{'title':'Invalid Moderator Number','message':'Please Enter Valid Moderator Number!!!'}}
            mod_qual_lst =  []
            for qualification in moderator_id.moderator_qualification_ids:
                mod_qual_lst.append(qualification.qualification_hr_id.id)
            if mod_qual_lst:
                if self.learning_programme_id.qualification_id.id in mod_qual_lst:
                    self.moderators_id = moderator_id.id
                    return {'domain':{'moderators_id':[('id','in', [moderator_id.id])]}}
                else:
                    self.moderator_no = ''
                    return {'value':{'moderators_no':''}, 'warning':{'title':'Invalid Moderator','message':'This Moderator is not Linked with selected Learning Programme!!!'}}
    
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
    def onchange_learning_programme(self, learning_programme_id):
        unit_standards = []
        learning_programme_obj = self.env['etqe.learning.programme'].search(
            [('seta_branch_id', '=', '11')])
        provider_obj = self.env['res.partner']
        learning_programme_list, asse_list, mode_list = [], [], []
        if learning_programme_obj:
            for s in learning_programme_obj:
                learning_programme_list.append(s.id)
        '''Code to avoid those Learning Programme which are already exist in provider master in extension of scope provider process'''
        if (self._context.get('extension_of_scope') == True or self._context.get('existing_provider') == True) and not self._context.get('provider_master_id_number'):
            return {'warning': {'title': 'Warning', 'message': 'Please Enter Accreditation Number to fetch existing Provider details!!'}}
        if (self._context.get('extension_of_scope') == True or self._context.get('existing_provider') == True) and self._context.get('provider_master_id_number'):
            provider_master_objects = self.env['res.partner'].search(
                [('provider_accreditation_num', '=', self._context.get('provider_master_id_number'))])
            if provider_master_objects:
                pro_lst = []
                for pro_obj in provider_master_objects:
                    pro_lst.append(pro_obj.id)
                provider_obj = self.env['res.partner'].search(
                    [('id', '=', max(pro_lst))])
                if provider_obj:
                    if provider_obj.learning_programme_ids:
                        for master_lp in provider_obj.learning_programme_ids:
                            if master_lp.learning_programme_id.id in learning_programme_list:
                                learning_programme_list.remove(
                                    master_lp.learning_programme_id.id)
        if learning_programme_id:
            learning_programme_obj = self.env['etqe.learning.programme'].browse(learning_programme_id)
            for unit_standards_lines in learning_programme_obj.unit_standards_line:
                if unit_standards_lines.selection == True:
                    val = {
                        'name': unit_standards_lines.name,
                        'type': unit_standards_lines.type,
                        'id_no': unit_standards_lines.id_no,
                        'title': unit_standards_lines.title,
                        'level1': unit_standards_lines.level1,
                        'level2': unit_standards_lines.level2,
                        'level3': unit_standards_lines.level3,
                        'selection': True,
                        'seta_approved_lp': unit_standards_lines.seta_approved_lp,
                        'provider_approved_lp': unit_standards_lines.provider_approved_lp,
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
                assessor_ids = self.env['hr.employee'].search([('id', 'in', ass_list)])
                for ass_id in assessor_ids:
                    for qualification_data in ass_id.qualification_ids:
                        if qualification_data.qualification_hr_id.id == learning_programme_obj.qualification_id.id:
                            asse_list.append(ass_id.id)
            if mod_list:
                moderator_ids = self.env['hr.employee'].search([('id', 'in', mod_list)])
                for mod_id in moderator_ids:
                    for qualification_data in mod_id.qualification_ids:
                        if qualification_data.qualification_hr_id.id == learning_programme_obj.qualification_id.id:
                            mode_list.append(mod_id.id)
            return {'domain':{'assessors_id':[('id', 'in', asse_list)], 'moderators_id':[('id', 'in', mode_list)]}, 'value': {'unit_standards_line': unit_standards, 'saqa_qual_id': learning_programme_obj.saqa_qual_id, 'qualification_id': learning_programme_obj.qualification_id.id}}
        return {'domain': {'learning_programme_id': [('id', 'in', learning_programme_list)], 'assessors_id': [('id', 'in', asse_list)], 'moderators_id': [('id', 'in', mode_list)]}}
learning_programme_accreditation_rel()


class learning_programme_unit_standards_accreditation_rel(models.Model):
    _name = 'learning.programme.unit.standards.accreditation.rel'
    _description = 'Learning Programme Unit Standards Accreditation Rel'
    _rec_name = 'type'
    name = fields.Char(string='Name')
#     type = fields.Char(string='Type', required=True)
    type = fields.Selection([
        ('Core', 'Core'),
        ('Fundamental', 'Fundamental'),
        ('Elective', 'Elective'),
    ], string='Type', required=True, track_visibility='onchange')
    id_no = fields.Char(string='ID NO')
    title = fields.Char(string='UNIT STANDARD TITLE', required=True)
    level1 = fields.Char(string='PRE-2009 NQF LEVEL')
    level2 = fields.Char(string='NQF LEVEL')
    level3 = fields.Char(string='CREDITS')
    selection = fields.Boolean(string='SELECT')
    learning_programme_id = fields.Many2one(
        'learning.programme.accreditation.rel', 'Learning Programme Reference', ondelete='cascade')
    seta_approved_lp = fields.Boolean(
        string='SETA Learning Material', track_visibility='onchange')
    provider_approved_lp = fields.Boolean(
        string='PROVIDER Learning Material', track_visibility='onchange')
learning_programme_unit_standards_accreditation_rel()

#################################################
## LEARNING PROGRAMME ACCREDITATION CAMPUS REL ##
#################################################


class learning_programme_accreditation_campus_rel(models.Model):
    _name = 'learning.programme.accreditation.campus.rel'
    _description = 'Learning Programme Accreditation Campus Rel'

    saqa_qual_id = fields.Char(string='SAQA QUAL ID')
    learning_programme_id = fields.Many2one(
        "etqe.learning.programme", 'Learning Programme')
    unit_standards_line = fields.One2many(
        'lp.unit.standards.ac.rel', 'learning_programme_id', 'Unit Standards')
    learning_programme_accreditation_rel_id = fields.Many2one(
        'provider.accreditation.campus', 'Provider Accreditation Reference')
    seta_approved_lp = fields.Boolean(
        string='SETA Learning Material', track_visibility='onchange')
    provider_approved_lp = fields.Boolean(
        string='PROVIDER Learning Material', track_visibility='onchange')
    @api.multi
    def onchange_learning_programme(self, learning_programme_id):
        unit_standards = []
        if learning_programme_id:
            learning_programme_obj = self.env[
                'etqe.learning.programme'].browse(learning_programme_id)
            for unit_standards_lines in learning_programme_obj.unit_standards_line:
                if unit_standards_lines.selection == True:
                    val = {
                        'name': unit_standards_lines.name,
                        'type': unit_standards_lines.type,
                        'id_no': unit_standards_lines.id_no,
                        'title': unit_standards_lines.title,
                        'level1': unit_standards_lines.level1,
                        'level2': unit_standards_lines.level2,
                        'level3': unit_standards_lines.level3,
                        'selection': True,
                        'seta_approved_lp': unit_standards_lines.seta_approved_lp,
                        'provider_approved_lp': unit_standards_lines.provider_approved_lp,
                    }
                    unit_standards.append((0, 0, val))
            return {'value': {'unit_standards_line': unit_standards, 'saqa_qual_id': learning_programme_obj.saqa_qual_id}}
        return {}
learning_programme_accreditation_campus_rel()


class lp_unit_standards_ac_rel(models.Model):
    _name = 'lp.unit.standards.ac.rel'
    _description = 'Learning Programme Unit Standards Accreditation Campus Rel'
    _rec_name = 'type'
    name = fields.Char(string='Name')
    type = fields.Selection([
        ('Core', 'Core'),
        ('Fundamental', 'Fundamental'),
        ('Elective', 'Elective'),
    ], string='Type', required=True, track_visibility='onchange')
    id_no = fields.Char(string='ID NO')
    title = fields.Char(string='UNIT STANDARD TITLE', required=True)
    level1 = fields.Char(string='PRE-2009 NQF LEVEL')
    level2 = fields.Char(string='NQF LEVEL')
    level3 = fields.Char(string='CREDITS')
    selection = fields.Boolean(string='SELECT')
    learning_programme_id = fields.Many2one(
        'learning.programme.accreditation.campus.rel', 'Learning Programme Reference')
    seta_approved_lp = fields.Boolean(
        string='SETA Learning Material', track_visibility='onchange')
    provider_approved_lp = fields.Boolean(
        string='PROVIDER Learning Material', track_visibility='onchange')
lp_unit_standards_ac_rel()
