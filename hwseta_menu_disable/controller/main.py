from openerp.addons.web import http
from openerp.http import request
from datetime import datetime


class ActionClass(http.Controller):

    @http.route('/check_expired_menus', type="http", website=True, auth="public", csrf=False)
    def return_actionids(self, **kwargs):
        user = http.request.env['res.users'].sudo()
        user_brw = user.search([('id', '=', http.request.uid)])
        partner_obj = user_brw.partner_id
        provider_end_date = partner_obj.provider_end_date
        today = datetime.now().date()
        todays_date = today.strftime('%Y-%m-%d')
        print "Todays Date======", todays_date
        action_list = []
        if provider_end_date < todays_date and partner_obj.provider == True:
            action_ids1 = request.env.ref(
                'hwseta_etqe.action_providers_form').id
            if action_ids1:
                action_list.append(action_ids1)
            action_ids2 = request.env.ref(
                'hwseta_etqe.action_provider_learner_view').id
            if action_ids2:
                action_list.append(action_ids2)
            action_ids3 = request.env.ref(
                'hwseta_etqe.open_view_assessment_list_my').id
            if action_ids3:
                action_list.append(action_ids3)
            action_ids4 = request.env.ref(
                'hwseta_etqe.learner_registration_action').id
            if action_ids4:
                action_list.append(action_ids4)
        print "Action List=====", action_list
        return str(action_list)
