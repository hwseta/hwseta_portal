from openerp import models, fields, api, _
from openerp.osv.orm import except_orm
from datetime import datetime
DEBUG = True

if DEBUG:
    import logging

    logger = logging.getLogger(__name__)


    def dbg(msg):
        logger.info(msg)
else:
    def dbg(msg):
        pass

class wss_draft(models.Model):
    _name = 'wss.draft'
    _inherit = 'mail.thread'
    _description = 'WSS'

    def chatter(self,author,msg):
        self.message_post(body=_(msg), subtype='mail.mt_comment', author_id=author.partner_id.id)

    @api.depends('extendable')
    @api.one
    def _get_extendable(self):
        nw = datetime.today().date()
        # todo: fix the dates to select from config instead of hard code dates
        wss_conf = self.env['wss.upload.config.settings'].search([])
        # wss_settings = self.env['wss.upload.config.settings'].browse(wss_conf[0].id)
        if not self.extendable:
            show_submit = datetime.strptime('2019/08/04', '%Y/%m/%d').date()
            # show_submit = datetime.strptime(wss_settings.show_submit, '%Y-%m-%d').date()
            if nw >= show_submit:
                self.extendable = True

    @api.depends('financial_year_id')
    @api.one
    def get_default_year(self):
        dbg('get_default_year')
        nw = datetime.today().date()
        if not self.financial_year_id:
            dbg('no year')
            this_fin_year = self.env['account.fiscalyear'].search([('date_stop','>',nw),('date_start','<',nw)], limit=1)
            dbg(this_fin_year)
            self.financial_year_id = this_fin_year

    @api.depends('staff_database_ids')
    @api.one
    def _get_staff_counts(self):
        dbg('get_staff_counts')
        vols = 0
        perms = 0
        temps = 0
        if self.staff_database_ids:
            for emp in self.staff_database_ids:
                if emp.employment_status == 'temp':
                    temps += 1
                elif emp.employment_status == 'perm':
                    perms += 1
                elif emp.employment_status == 'volunteer':
                    vols += 1
            self.temporary = temps
            self.permanent = perms
            self.volunteer = vols
            self.number_of_employees = temps + perms + vols

    # @api.depends('text_full')
    # @api.one
    # def consolidate_wss_data(self):
    #     text_full = """"""
    #     if not self.text_full:
    #         field_dict = self.read()[0]
    #         field_list = list(field_dict)
    #         for field in field_list:
    #             # dbg('type field:' + type(field))
    #             text_full += str(field) + ':' + str(field_dict.get(field)) + '\r'
    #     self.text_full = text_full

    # @api.onchange('permanent','temporary')
    # @api.one
    # def get_emp_count(self):
    #     if self.permanent and self.temporary:
    #         self.number_of_employees = self.permanent + self.temporary
    #         return

    # section A--DETAILS OF THE ORGANISATION
    status = fields.Selection([('draft', 'Draft'),
                               ('submitted', 'Submitted'),
                               ('assessed', 'Assessed'),
                               ('evaluated', 'Evaluated'),
                               ('approved', 'Accepted'),
                               # ('query', 'Query'),
                               ('rejected', 'Rejected')],
                              string="State", default='draft')
    extension_status = fields.Selection([('standard','Standard'),
                                         ('requested','Ext Requested'),
                                         ('approved','Ext Approved'),
                                         ('rejected','Ext Rejected'),
                                         ('open','Open Ended')],default='standard', track_visibility='always')
    assessed_check = fields.Boolean()
    submitted_check = fields.Boolean()
    evaluated_check = fields.Boolean()
    approved_check = fields.Boolean()
    rejected_check = fields.Boolean()
    chatterbox = fields.Text()
    extension_reason = fields.Text()
    # text_full = fields.Text(compute=consolidate_wss_data)
    page = fields.Selection([('no_sdl','no sdl'),
                             ('contact','Contact'),
                             ('exists_page','SDL Exists'),
                             ('org','Org'),
                             ('staff_db','Staff DB'),
                             ('training','Training'),
                             ('signatories','Signatories')
                             ],default='no_sdl')
    org_name = fields.Char()
    org_contact_name = fields.Char()
    sdl_number = fields.Char()
    org_type = fields.Selection([('ngo', 'NGO'),
                                 ('npo', 'NPO'),
                                 ('npc', 'NPC'),
                                 ('cc', 'CC'),
                                 ('pty', 'PTY'),
                                 ('trust', 'Trust'),
                                 ('other', 'Other'),
                                 ],
                                string="Organisation Type")
    main_bus_act = fields.Text(string="Main Business Activity")
    # physical addr
    street = fields.Char()
    street2 = fields.Char()
    city_id = fields.Many2one(comodel_name="res.city", string="City")
    state_id = fields.Many2one(comodel_name="res.country.state", string="Province")
    zip_code = fields.Char()
    country_id = fields.Many2one('res.country')
    municipality_id = fields.Many2one('res.municipality')
    # postal addr
    postal_street = fields.Char()
    postal_street2 = fields.Char()
    postal_state_id = fields.Many2one(comodel_name="res.country.state", string="Province")
    postal_zip_code = fields.Char()
    postal_country_id = fields.Many2one('res.country')
    urban_or_rural = fields.Selection([('urban', 'Urban'), ('rural', 'Rural')])
    phone = fields.Char(string="Tel. No")
    email = fields.Char()
    mobile = fields.Char()
    # section B-ORGANISATION PERSON CONTACT OR SKILLS DEVELOPMENT FACILITATOR DETAILS
    first_name = fields.Char()
    last_name = fields.Char()
    job_title = fields.Char()
    facilitator_phone = fields.Char()
    facilitator_email = fields.Char()
    facilitator_cell = fields.Char()
    facilitator_id_number = fields.Char()
    proof_attachment = fields.Binary()
    citizenship_status = fields.Selection([('sa','South African'),
                                           ('dual','Dual (SA plus other)'),
                                           ('perm','Permanent Resident'),
                                           ('unknown','Unknown'),
                                           ('other','Other')])
    # section C - STAFF DATABASE
    number_of_employees = fields.Integer(compute='_get_staff_counts')
    permanent = fields.Integer(compute='_get_staff_counts')
    temporary = fields.Integer(compute='_get_staff_counts')
    volunteer = fields.Integer(compute='_get_staff_counts')
    staff_database_ids = fields.One2many('staff.database', 'wss_id')
    # section D - training need identification
    financial_year_id = fields.Many2one('account.fiscalyear',default=get_default_year)
    training_needs_ids = fields.One2many('training.needs','wss_id')
    # end section
    designated_signatory = fields.Many2one('res.partner')
    authorised_signatory = fields.Many2one('res.partner')
    # helper fields
    extendable = fields.Boolean(compute='_get_extendable')

    @api.model
    def create(self, vals):
        nw = datetime.today().date()
        vals['last_name'] = self.env.user.partner_id.ext_partner_surname
        vals['first_name'] = self.env.user.partner_id.name
        vals['facilitator_email'] = self.env.user.partner_id.email
        vals['facilitator_id_number'] = self.env.user.partner_id.ext_identity_number
        vals['phone'] = self.env.user.partner_id.phone
        vals['designated_signatory'] = self.env.user.partner_id.id
        vals['financial_year_id'] = self.env['account.fiscalyear'].search([('date_stop', '>', nw), ('date_start', '<', nw)],
                                                                  limit=1).id
        res = super(wss_draft,self).create(vals)
        return res



    @api.one
    def assessed(self):
        if self.status == 'submitted' and self.assessed_check:
            self.chatter(self.env.user, "wss was set to assessed and disclaimer was checked")
            self.status = 'assessed'
            self.assessed_check = False
        else:
            raise except_orm(_('Missing values!'), _('Please check the disclaimer box before setting to assessed'))

    @api.one
    def evaluated(self):
        if self.status == 'assessed' and self.evaluated_check:
            self.chatter(self.env.user, "wss was set to evaluated and disclaimer was checked")
            self.status = 'evaluated'
            self.evaluated_check = False
        else:
            raise except_orm(_('Missing values!'), _('Please check the disclaimer box before setting to evaluated'))


    @api.one
    def approved(self):
        if self.status == 'evaluated' and self.approved_check:
            self.chatter(self.env.user, "wss was set to approved and disclaimer was checked")
            self.status = 'approved'
            self.approved_check = False
        else:
            raise except_orm(_('Missing values!'), _('Please check the disclaimer box before approving'))

    @api.one
    def rejected(self):
        if self.rejected_check and self.chatterbox:
            self.chatter(self.env.user,"wss was set back to rejected with reasoning:" + self.chatterbox)
            self.status = 'rejected'
            self.chatterbox = ''
            self.rejected_check = False
        else:
            raise except_orm(_('Missing values!'), _('Please fill in chatterbox with a reason for setting to rejected and check the disclaimer box'))


    @api.one
    def set_to_draft(self):
        if self.status and self.status != 'draft' and self.chatterbox:
            self.chatter(self.env.user, "wss was set back to draft with reasoning:" + self.chatterbox)
            self.status = 'draft'
            self.chatterbox = ''
        else:
            raise except_orm(_('Missing values!'), _('Please fill in chatterbox with a reason for setting to draft'))

    @api.one
    def check_extension(self):
        dbg('check_extension')
        wss_conf = self.env['wss.upload.config.settings'].search([])
        # wss_settings = self.env['wss.upload.config.settings'].browse(wss_conf[0].id)
        ext_state = self.extension_status
        nw = datetime.today().date()
        # start = datetime.strptime(wss_settings.submission_start, '%Y-%m-%d').date()
        # end = datetime.strptime(wss_settings.submission_end, '%Y-%m-%d').date()
        # ext = datetime.strptime(wss_settings.submission_ext, '%Y-%m-%d').date()
        start = datetime.strptime('2019/07/14','%Y/%m/%d').date()
        end = datetime.strptime('2019/08/14','%Y/%m/%d').date()
        ext = datetime.strptime('2019/09/14','%Y/%m/%d').date()
        # if wss_settings.submission_start and wss_settings.submission_end and wss_settings.submission_ext and ext_state:
        if start and end and ext and ext_state:
            dbg('found all extension dates')
            dbg('start:' + str(start))
            dbg('end:' + str(end))
            dbg('ext:' + str(ext))
            dbg('ext:' + str(ext_state))
            if ext_state == 'standard' and nw < start:
                raise except_orm(_('Too Early!'), _('The submission date has not started yet'))
            if ext_state == 'standard' and nw > end:
                raise except_orm(_('Date Exceeded!'), _('The submission date has been surpassed'))
            if ext_state == 'approved' and nw > ext:
                raise except_orm(_('Date Exceeded!'), _('The submission date has been surpassed'))
            if ext_state == 'requested':
                raise except_orm(_('Extension Pending!'), _('The submission extension is still pending. please contact your system administrator.'))
            if ext_state == 'rejected':
                raise except_orm(_('Extension Rejected!'), _('The submission Extension was not granted, please check the logs below to see reasoning behind extension rejection.'))
            if ext_state == 'open':
                dbg('submission is open ended')
        else:
            raise except_orm(_('Missing Configuration!'), _('PLease check with system administrator about WSS submission date configuration'))

    @api.one
    def open_extension(self):
        if self.extension_status == 'approved' and self.extension_reason:
            self.chatter(self.env.user, "Submission date extension opened with reasoning:" + self.extension_reason)
            self.extension_status = 'open'
            self.extension_reason = ''
        else:
            raise except_orm(_('Missing values!'), _('Please fill in open extension reasoning'))

    @api.one
    def approve_extension(self):
        if self.extension_status == 'requested' and self.extension_reason:
            self.chatter(self.env.user, "Submission date extension approved with reasoning:" + self.extension_reason)
            self.extension_status = 'approved'
            self.extension_reason = ''
        else:
            raise except_orm(_('Missing values!'), _('Please fill in approval reasoning'))

    @api.one
    def request_extension(self):
        if self.extension_status == 'standard' and self.extension_reason:
            self.chatter(self.env.user, "Submission date extension resquested with reasoning:" + self.extension_reason)
            self.extension_status = 'requested'
            self.extension_reason = ''
        else:
            raise except_orm(_('Missing values!'), _('Please fill in extension reasoning'))

    @api.one
    def submit_wss(self):
        field_dict = self.read()[0]
        field_list = list(field_dict)
        empty = []
        ommitted = ['message_follower_ids',
                    'rejected_check',
                    'message_ids',
                    'message_is_follower',
                    'evaluated_check',
                    'message_last_post',
                    'chatterbox',
                    'message_unread',
                    'website_message_ids',
                    'approved_check',
                    'permanent',
                    'temporary',
                    'volunteer',
                    'number_of_employees',
                    'extension_reason',
                    'extension_status',
                    'street',
                    'street2',
                    'postal_street',
                    'postal_street2',
                    'zip_code',
                    'postal_zip_code',
                    'assessed_check']
        for field in field_list:
            if not field_dict.get(field) and not field == 'authorised_signatory' and field not in ommitted:
                dbg(field)
                empty.append(field)
            else:
                dbg(str(field) + str(field_dict.get(field)))
        dbg(empty)
        if not empty:
            self.check_extension()
            self.status = 'submitted'
            self.submitted_check = False
        else:
            raise except_orm(_('Missing values!'), _('Please fill in these fields:' + str(empty)))

        # dbg(field_list)

    @api.one
    def check_sdl(self):
        match = False
        if self.sdl_number:
            if self.sdl_number in [wss.sdl_number for wss in self.env['wss.draft'].search([('sdl_number','=',self.sdl_number),('id','!=',self.id)])]:
                selfie = self.env['wss.draft'].browse(self.id)
                me = selfie.unlink()
                self._cr.commit()
                # raise except_orm(_('WSS already exists!'), _('There is already a WSS in the system with this organisation\'s SDL number.\n If the record was rejected please request for it to be set back to draft'))
                raise except_orm(_('WSS already exists!'), _('There is already a WSS in the system with this organisation\'s SDL number.\n If you would like to re-submit the WSS for this organsation, please request for it to be set back to draft by logging a call on the helpdesk.\n \n Refresh your page to continue'))
            elif self.sdl_number in [sdl.employer_sdl_no for sdl in self.env['res.partner'].search([('employer_sdl_no','=',self.sdl_number)])]:
                self.page = 'exists_page'
            else:
                self.page = 'contact'

    @api.one
    def authorise_wss(self):
        if not self.authorised_signatory:
            user = self.env.user
            self.authorised_signatory = user.partner_id.id

    @api.one
    def next_page(self):
        if self.page:
            if self.page == 'contact':
                self.page = 'org'
            elif self.page == 'org':
                self.page = 'staff_db'
            elif self.page == 'staff_db':
                self.page = 'training'
            elif self.page == 'training':
                self.page = 'signatories'

    @api.one
    def back_page(self):
        if self.page:
            if self.page == 'org':
                self.page = 'contact'
            elif self.page == 'staff_db':
                self.page = 'org'
            elif self.page == 'training':
                self.page = 'staff_db'
            elif self.page == 'signatories':
                self.page = 'training'


    @api.one
    def approve_wss_and_commit(self):
        wsp_obj = self.env['wsp.plan']
        if self.sdl_number:
            matching_employer = self.env['res.partner'].search([('employer_sdl_no','=',self.sdl_number)])
            if matching_employer:
                wsp_obj.create({'sdl_no':self.sdl_number,
                                'employer_id':matching_employer.id})
            matching_emp_rel = self.env['sdf.employer.rel'].search([('employer_sdl_no','=',self.sdl_number)])
            matching_sdf = self.env['hr.employee'].search([('sdf_id','in',matching_emp_rel)])
            # if matching_sdf:



wss_draft()


class staff_database(models.Model):
    _name = 'staff.database'


    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].get('staff.db.reference')
        res = super(staff_database,self).create(vals)
        return res

    # @api.one
    # def get_seq(self):
    #     if not self.number:
    #         self.number = self.env['ir.sequence'].get('staff.db.reference')

    wss_id = fields.Many2one('wss.draft')
    number = fields.Char()
    first_name = fields.Char()
    last_name = fields.Char()
    id_number = fields.Char()
    country = fields.Many2one(comodel_name="res.country", string="Country")
    state = fields.Many2one(comodel_name="res.country.state", string="Province")
    race = fields.Selection([('white','White'),
                             ('coloured','Coloured'),
                             ('indian','Indian'),
                             ('african','African')])
    gender = fields.Selection([('male','Male'),('female','Female')])
    disabled = fields.Boolean(default=False)
    job_title = fields.Char()
    highest_qual = fields.Char(string="Highest Qualification")
    employment_status = fields.Selection([('perm','Permanent'),
                                          ('temp','Temporary'),
                                          ('volunteer','Volunteer')])

staff_database()


class training_needs(models.Model):
    _name = 'training.needs'

    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].get('training.needs.reference')
        res = super(training_needs, self).create(vals)
        return res

    # @api.one
    # def get_seq(self):
    #     if not self.number:
    #         self.number = self.env['ir.sequence'].get('training.needs.reference')

    wss_id = fields.Many2one('wss.draft')
    number = fields.Char()
    first_name = fields.Char()
    last_name = fields.Char()
    id_number = fields.Char()
    country = fields.Many2one(comodel_name="res.country", string="Country")
    state = fields.Many2one(comodel_name="res.country.state", string="Province")
    name_of_training = fields.Char()
    training_type = fields.Selection([('short','Short Course'),
                                      ('certificate','Certificate'),
                                      ('renewal','Renewal'),
                                      ('certificate6','Certificate longer than 6 months'),
                                      ('degree','Degree'),
                                      ('cpd','CPD training'),
                                      ('noncred','Noncredit bearing training'),
                                      ('cred','Credit bearing training'),
                                      ('other','Other'),
                                      ('workshop','Workshop')])
    start_date = fields.Date()
    end_date = fields.Date()
    cost_of_training = fields.Float()

training_needs()
