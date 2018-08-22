from openerp.exceptions import Warning
from openerp import models, fields, tools, api, _


class skills_programme_unit_standards(models.Model):
    _name = 'skills.programme.unit.standards'
    _description = 'Skills Programme Unit Standards'
    _rec_name = 'id_no'
    name = fields.Char(string='Name', required=True)
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
    type_key = fields.Integer("Type Key");
    id_no = fields.Char(string='ID NO')
    title = fields.Char(string='UNIT STANDARD TITLE', required=True)
    level1 = fields.Char(string='PRE-2009 NQF LEVEL')
    level2 = fields.Char(string='NQF LEVEL')
    level3 = fields.Char(string='CREDITS')
    selection = fields.Boolean(string='SELECT', track_visibility='onchange')
    skills_programme_id = fields.Many2one(
        'skills.programme', 'Skills Programme Reference', ondelete='cascade')
    # Newly added fields
    skills_unit_standards_id = fields.Many2one(
        'learner.assessment.line.for.skills', string='Skills Unit Standards')
    skills_unit_standards_verify_id = fields.Many2one(
        'learner.assessment.verify.line.for.skills', string='Skills Unit Standards')
    skills_unit_standards_achieve_id = fields.Many2one(
        'learner.assessment.achieve.line.for.skills', string='Skills Unit Standards')
    skills_unit_standards_achieved_id = fields.Many2one(
        'learner.assessment.achieved.line.for.skills', string='Skills Unit Standards')
    
#     @api.multi
#     @api.onchange('type')
#     def onchange_type(self):
#         if self.type == 'Core':
#             self.type_key = 1
#         elif self.type == 'Fundamental':
#             self.type_key = 2
#         elif self.type == 'Elective':
#             self.type_key = 3
#         elif self.type == 'Knowledge Module':
#             self.type_key = 4
#         elif self.type == 'Practical Skill Module':
#             self.type_key = 5
#         elif self.type == 'Work Experience Module':
#             self.type_key = 6
#         elif self.type == 'Exit Level Outcomes':
#             self.type_key = 7

skills_programme_unit_standards()


class skills_programme(models.Model):
    _name = 'skills.programme'
    _description = 'Skills Programme'
    
    @api.model
    def _search(self, args, offset=0, limit=80, order=None, count=False, access_rights_uid=None):
        user = self._uid
        user_obj = self.env['res.users']
        user_data = user_obj.browse(user)
        if self._context.get('model') == 'skills.programme.learner.rel':
            if user_data.partner_id.provider:
                skill_lst = []
                for line in self.env.user.partner_id.skills_programme_ids:
                    self._cr.execute("select id from skills_programme where seta_branch_id=1 and id =%s"%(line.skills_programme_id.id))
                    skill_id = self._cr.fetchone()
                    if skill_id:
                        skill_lst.append(skill_id[0])
                args.append(('id', 'in', skill_lst))
                return super(skills_programme, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
        return super(skills_programme, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
    
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
        ret_val = super(skills_programme, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for rt in ret_val:
            if rt.has_key('is_archive'):
                if rt.get('is_archive', True):
                    rt['is_archive'] = 'Archive'
        return ret_val

    @api.one
    @api.depends('unit_standards_line.selection')
    def _compute_total_credit(self):
        total_credit = 0
        for skill in self:
            for skill_line in skill.unit_standards_line:
                if skill_line.selection == True:
                    if skill_line.level3:
                        total_credit += int(skill_line.level3)
            skill.total_credit = total_credit

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    qualification_id = fields.Many2one(
        'provider.qualification', 'Qualification', required=True)
    saqa_qual_id = fields.Char(string='SAQA QUAL ID ')
    applicant = fields.Char(string='Applicant')
    notes = fields.Text(string='Comment')
    if_us = fields.Boolean(string='US')
    total_credit = fields.Integer(
        string="Total Credit", compute="_compute_total_credit")
    unit_standards_line = fields.One2many(
        'skills.programme.unit.standards', 'skills_programme_id', 'Unit Standards')
    seta_branch_id = fields.Many2one('seta.branches', 'Seta Branch')
    is_archive = fields.Boolean('Archive')
    skills_id = fields.Many2one(
        'learner.assessment.line.for.skills', string='Skills Programme')
    skills_verify_id = fields.Many2one(
        'learner.assessment.verify.line.for.skills', string='Skills Programme')
    skills_achieve_id = fields.Many2one(
        'learner.assessment.achieve.line.for.skills', string='Skills Programme')
    skills_achieved_id = fields.Many2one(
        'learner.assessment.achieved.line.for.skills', string='Skills Programme')

    @api.multi
    def onchange_qualification(self, qualification_id):
        res = {}
        unit_standards = []
        qual_list = []
        qualification_obj = self.env['provider.qualification'].search([('seta_branch_id','=','11')])
        if qualification_obj:
            for q in qualification_obj:  
                qual_list.append(q.id)
        if qualification_id:
            qualification_obj = self.env[
                'provider.qualification'].browse(qualification_id)
            for qualification_lines in qualification_obj.qualification_line:
                val = {
                    'name': qualification_lines.title,
                    'type': qualification_lines.type,
                    'id_no': qualification_lines.id_no,
                    'title': qualification_lines.title,
                    'level1': qualification_lines.level1,
                    'level2': qualification_lines.level2,
                    'level3': qualification_lines.level3,
                    'selection': False,
                }
                unit_standards.append((0, 0, val))

            return {'value': {'unit_standards_line': unit_standards, 'saqa_qual_id': qualification_obj.saqa_qual_id}}
        return {'domain': {'qualification_id': [('id', 'in',qual_list)]}}

    @api.multi
    def onchange_archive(self, is_archive):
        print "Inside onchange----", is_archive
        res = {}
        if is_archive:
            res.update({'value':{'seta_branch_id': None,}})
        return res

    @api.multi
    def onchange_seta_branch_id(self, seta_branch_id):
        print "Inside onchange----", seta_branch_id
        res = {}
        if seta_branch_id == 1:
            res.update({'value':{'is_archive': False,}})
        return res

    @api.multi
    @api.onchange('code')
    def onchange_code(self):
        if self.code:
            is_exist_code = self.env['skills.programme'].search([('code','=',str(self.code).strip())])
            if is_exist_code:
                self.code = ''
                print "111111"
                return {'warning':{'title':'Duplicate Record','message':'Please enter unique Skills Programme Code'}}
        return {}

    @api.multi
    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            is_exist_name = self.env['skills.programme'].search([('name','=',str(self.name).strip())])
            if is_exist_name:
                self.name = ''
                print "222222"
                return {'warning':{'title':'Duplicate Record','message':'Please enter unique  Skills Programme Name'}}
        return {}    
skills_programme()
