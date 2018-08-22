from openerp import models, fields, api, _
import xlsxwriter
import cStringIO
import base64
class ApproveLearner(models.TransientModel):
    _name = "approve.learner.wizard"
    
    war_label = fields.Text("Not Approve Records")
    @api.model
    def default_get(self, fields):
        res = super(ApproveLearner, self).default_get(fields)
        err_log = self._context.get('error_log')
        if err_log:
            res.update({
                            'war_label':err_log,
                })
        
        return res
    
    @api.multi
    def learner_error_log(self):
        
        buffered = cStringIO.StringIO()
        workbook = xlsxwriter.Workbook(buffered)
        worksheet1 = workbook.add_worksheet('Approval Status')
        worksheet1.set_column(0, 2, 14)
        merge_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        })
        worksheet1.write('A1', 'Approved Learners',merge_format)
        worksheet1.write('B1', 'Non-Approved Learners',merge_format)
        row = 1
        for l in self._context.get('non_apr_ids'):
            col = 1
            if l:
                worksheet1.write(row, col, l)
            col+=1
            row+=1
        row = 1
        for l in self._context.get('approve_ids'):
            col = 0
            if l:
                worksheet1.write(row, col, l)
            col+=1
            row+=1
        
        workbook.close()
        xlsx_data = buffered.getvalue()
        out_data = base64.encodestring(xlsx_data)
        attachment_obj = self.env['ir.attachment']
        new_attach = attachment_obj.create({
            'name':'Learners_Approval_Non-Approval_Log.xlsx',
            'res_name': 'learner_registration',
            'type': 'binary',
            'res_model': 'learner.registration',
            'datas': out_data,
        })
        return {
                'type' : 'ir.actions.act_url',
                'url': '/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=%s' % (new_attach.id),
                'target': 'self',                
                }
ApproveLearner()