from openerp.osv import fields, osv
from openerp.report import report_sxw


class learner_status_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(learner_status_report, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'get_learner_status': self.get_learner_status,
        })

    def get_learner_status(self, data):
        learner_lst = []
        learner_ser = self.pool.get('learner.registration.qualification').search(
            self.cr, self.uid, [('learner_id', '!=', False)])
        if learner_ser:
            learner_brw = self.pool.get('learner.registration.qualification').browse(
                self.cr, self.uid, learner_ser)
            if learner_brw:
                for learner in learner_brw:
                    pro_id = self.pool.get('res.users').search(
                        self.cr, self.uid, [('id', '=', self.uid)])
                    if pro_id:
                        pro_obj = self.pool.get('res.users').browse(
                            self.cr, self.uid, pro_id)
                    if pro_obj:
                        if pro_obj.partner_id.id == learner.provider_id.id:
                            data_dict = {}
                            data_dict['provider_id'] = learner.provider_id.name
                            data_dict[
                                'id'] = learner.learner_id.identification_id
                            data_dict['name'] = learner.learner_id.name
                            data_dict[
                                'title'] = learner.learner_qualification_parent_id.name
                            data_dict[
                                'achieve'] = 'Yes' if learner.is_learner_achieved == True else 'No'
                            data_dict[
                                'complete'] = 'Yes' if learner.is_complete == True else 'No'
                            learner_lst.append(data_dict)
        return learner_lst


class status_report_view(osv.AbstractModel):
    _name = 'report.hwseta_etqe.report_learner_status_report'
    _inherit = 'report.abstract_report'
    _template = 'hwseta_etqe.report_learner_status_report'
    _wrapped_report_class = learner_status_report
