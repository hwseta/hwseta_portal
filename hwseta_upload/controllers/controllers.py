from openerp import http
import openerp.addons.website.controllers.main
from openerp.http import request
from openerp import SUPERUSER_ID
import json
DEBUG = True

if DEBUG:
    import logging

    logger = logging.getLogger(__name__)


    def dbg(msg):
        logger.info(msg)
else:
    def dbg(msg):
        pass


# class League(http.Controller):
class Website(openerp.addons.website.controllers.main.Website):

    @http.route('/hwseta/wssdraftupload/', auth='public', website=True,context=None)
    def index(self, **kw):
        values = {}
        dbg(kw)
        dbg('index')
        group_obj = http.request.env['res.groups']
        perms = http.request.env.ref('hwseta_upload.group_wss_user')
        if kw:
            values['first_name'] = kw.get('first_name')
            values['last_name'] = kw.get('last_name')
            values['email'] = kw.get('user_email_id')

            sdf = http.request.env['hr.employee'].sudo().search([('is_sdf','=',True),('work_email','=',values['email'])])
            user = http.request.env['res.users'].sudo().search([('login','=',values['email'])])
            if len(sdf) > 0 or len(user) > 0:
                dbg('matched')
                user.sudo().write({'groups_id':[(4,perms.id)]
                })
                if not user.partner_id.email:
                    user.partner_id.write({'email':user.login,
                                           'ext_partner_surname':values['last_name']})
                return http.request.render('hwseta_upload.WSSDuplicateEmailMessage', {'email': values['email']})
            else:

                dbg(perms)
                user_id = http.request.env['res.users'].sudo().create({'login':values['email'],
                                                      'name':values['first_name'],
                                                      'groups_id':[(4,perms.id)],
                                                      'internal_external_users':'SDF'
                                                      })
                user_id.partner_id.write({'email':user_id.login,
                                          'ext_partner_surname':values['last_name'],
                                          'name':values['first_name'],
                                          })
                dbg(user_id)
                new_wss = http.request.env['wss.draft'].sudo().create({'designated_signatory':user_id.partner_id.id,
                                                                       'facilitator_email':values['email'],
                                                                       'first_name':values['first_name'],
                                                                       'last_name':values['last_name'],
                                                      })
                return http.request.render('hwseta_upload.WSSConfirmationMessage', {})
        else:
            return http.request.render('hwseta_upload.wss_upload', {
                # 'leagues': ["Spider Pigs", "Jody Caroll", "Buccaneers"],
                # 'games': Games.search([]),
                # 'leagues': Leagues.search([])
            })
