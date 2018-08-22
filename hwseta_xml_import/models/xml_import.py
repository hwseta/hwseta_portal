from openerp import models, fields, tools, api, _
import base64
import xml.etree.ElementTree as ET
from openerp.exceptions import Warning, ValidationError
from openerp.osv import fields as fields2, osv

class ProviderQualification(models.Model):
    _inherit = "provider.qualification"
       
    x_is_imported = fields.Boolean("Is Imported from XML Import ?", default=False)
    x_xml_file_id = fields.Integer("XML File ID")
    
class ProviderQualificationLine(models.Model):
    _inherit = "provider.qualification.line"
       
    x_is_imported = fields.Boolean("Is Imported from XML Import ?", default=False)
    x_xml_file_id = fields.Integer("XML File ID")


class Xmlimport(models.TransientModel):
    _name="xml.import.seta"
    _description = "Class for importing XML Files"
    xml_file = fields.Binary("File")
    status = fields.Char(readonly=True)
    import_cnt = 0
    import_exists_cnt = 0
    import_qual_ids = []
    import_qual_line_ids = []
    
    
    @api.multi
    def create_provider_qualification(self, dict_seq):
        if dict_seq:
            provider_qualification_obj = self.env['provider.qualification']
            provider_qual_exists = provider_qualification_obj.search([('saqa_qual_id','=',int(dict_seq.get('saqa_qual_id')))])
#             print "PRIVIDER QUAL EXISTS :::",provider_qual_exists
            
            if provider_qual_exists:
                ''' Try Updating the Qualification Object '''
#                 dict_seq['id'] = provider_qual_exists.id
                del dict_seq['x_is_imported']
                
                written = provider_qual_exists.write(dict_seq)
                if written:
                    self.import_exists_cnt +=1
#                     print "Provider Qualification Object was written successfully",provider_qual_exists.id
                    self.status = ""
                    self.status = 'Imported {} Qualifications and {} Qualifications Existed In System.'.format(self.import_cnt,self.import_exists_cnt)
                    return provider_qual_exists.id
                else:
                    print "Provider Qualification Object was not written"
                    return False
            
            if not provider_qual_exists:
                created_id = provider_qualification_obj.create(dict_seq)
                if created_id:
                    self.import_qual_ids.append(int(dict_seq.get('saqa_qual_id')))
                    self.import_cnt += 1
                    self.status = ""
                    self.status = 'Imported {} Records and {} Records Existed In System.'.format(self.import_cnt,self.import_exists_cnt)
                    return created_id.id
                else:
                    return False
        

    @api.multi
    def import_xml_file(self):
        self.import_qual_ids = []
        self.import_qual_line_ids = []
        log_dict = {}
        import_qual_lines_cnt = 0
        import_qual_lines_exists_cnt = 0
        
        print "INSIDE import_xml_file @@@@@@"
        if self.xml_file:
            dict_seq = {}
            dict_lines = {}
            lst_lines = []
            file_decode = base64.b64decode(self.xml_file)
            if file_decode:
                cnt = 0
#                 print file_decode,type(file_decode)
                try:
                    root = ET.fromstring(file_decode)
                except:
                    raise Warning("Invalid File, Please Select Valid XML File")
                    return { 
                            'context': self.env.context, 
                            'view_type': 'form', 
                            'view_mode': 'form', 
                            'res_model': 'xml.import.seta', 
                            'res_id': self.id, 
                            'type': 'ir.actions.act_window', 
                            'target': 'new'
                            }
                    
                
                for n in root.findall('QUALIFICATION'):
                    if n.find('QUALIFICATION_ID') is not None:
                        dict_seq['saqa_qual_id'] = n.find('QUALIFICATION_ID').text
                    if n.find('QUALIFICATION_TITLE') is not None:
                        dict_seq['name'] = n.find('QUALIFICATION_TITLE').text
                    if n.find('QUALIFICATION_MINIMUM_CREDITS') is not None:
                        dict_seq['m_credits'] = n.find('QUALIFICATION_MINIMUM_CREDITS').text
                    if n.find('QUAL_REGISTRATION_START_DATE') is not None:
                        dict_seq['rs_date'] = n.find('QUAL_REGISTRATION_START_DATE').text
                    if n.find('QUAL_REGISTRATION_END_DATE') is not None:
                        dict_seq['re_date'] = n.find('QUAL_REGISTRATION_END_DATE').text
                    if n.find('NQF_LEVEL_DESCRIPTION') is not None:
                        dict_seq['n_level'] = n.find('NQF_LEVEL_DESCRIPTION').text
                    if n.find('LAST_DATE_FOR_ENROLMENT') is not None:
                        dict_seq['l_date_e'] = n.find('LAST_DATE_FOR_ENROLMENT').text
                    if n.find('LAST_DATE_FOR_ACHIEVEMENT') is not None:
                        dict_seq['l_date_a'] = n.find('LAST_DATE_FOR_ACHIEVEMENT').text
                        
                    ''' FIND CHILD RECS FOR PROVIDER.QUALIFICATION.LINE '''
                        
#                     print "PREPARED DICT IS :",dict_seq
                    
                    if n.find('US_QUALIFICATION_LINK') == None:
                        print "DONT HAVE CHILD IDS "
                        
                    if n.find('US_QUALIFICATION_LINK') is not None:
                        
                        lst_lines = []
                        for child in n.findall('US_QUALIFICATION_LINK'):
                            dict_lines = {}
                            if child.find('UNIT_STD_TITLE') is not None:
#                                 print child.find('UNIT_STD_TITLE').get('UNIT_STANDARD_ID')
                                dict_lines['id_no'] = child.find('UNIT_STD_TITLE').get('UNIT_STANDARD_ID')
                                
                            if child.find('US_QUAL_TYPE_DESCRIPTION') is not None:
#                                 print child.find('US_QUAL_TYPE_DESCRIPTION').text
                                dict_lines['type'] = child.find('US_QUAL_TYPE_DESCRIPTION').text
                                dict_lines['name'] = child.find('US_QUAL_TYPE_DESCRIPTION').text
                            
                            if child.find('UNIT_STD_TITLE') is not None :
#                                 print child.find('UNIT_STD_TITLE').text
                                dict_lines['title'] = child.find('UNIT_STD_TITLE').text
                            
                            if child.find('NQF_LEVEL_DESCRIPTION') is not None :
#                                 print child.find('NQF_LEVEL_DESCRIPTION').text
                                dict_lines['level1'] = child.find('NQF_LEVEL_DESCRIPTION').text
                                
                            if child.find('NQF_LEVEL_ID') is not None :
#                                 print child.find('NQF_LEVEL_ID').text
                                dict_lines['level2'] = child.find('NQF_LEVEL_ID').text
                                
                            if child.find('UNIT_STD_NUMBER_OF_CREDITS') is not None :
#                                 print child.find('UNIT_STD_NUMBER_OF_CREDITS').text
                                dict_lines['level3'] = child.find('UNIT_STD_NUMBER_OF_CREDITS').text
                                
                            lst_lines.append(dict_lines)
                                
#                         print "CHILD DICT :",lst_lines
#                         print "----------------------------------------------------------------------------\n"
                    
                    if dict_seq:
                        ''' Check if provider.qualification does not exists '''
                        
                        dict_seq['x_is_imported'] = True
                        dict_seq['x_xml_file_id'] = dict_seq['saqa_qual_id']
                        dict_seq['seta_branch_id'] = 1
                        parent_id = self.create_provider_qualification(dict_seq)
                        if parent_id:
                            
#                             print "GOT PARENT ID AS {}".format(parent_id)
                            
                            for child_lines in lst_lines:
                                child_lines['line_id'] = parent_id
                                child_lines['x_is_imported'] = True
                                child_lines['x_xml_file_id'] = child_lines['id_no']
                                 
                                ''' Create Child lines '''
                                provider_qual_line_exists = self.env['provider.qualification.line'].search([('id_no','=',int(child_lines['id_no'])),('line_id','=',parent_id)])
#                                 print "PROVIDER QUAL LINE ",provider_qual_line_exists
                                
                                
                                ''' If Provider Qualification Line Exists, Try Updating it '''
                                if provider_qual_line_exists:
                                    import_qual_lines_exists_cnt += 1
                                    for p in provider_qual_line_exists:
#                                         print p.id_no, p.name
#                                         child_lines['id'] = p.id
                                        if child_lines.get('x_is_imported'):
                                            child_lines.pop('x_is_imported')
                                        written_id = p.write(child_lines)
#                                         if written_id:
#                                             print "Child Line Was update with parent id as {}".format(parent_id)
#                                         else:
#                                             print "Child line was not updated"
                                
                                if not provider_qual_line_exists:
                                    provider_qual_line = self.env['provider.qualification.line'].create(child_lines)
                                    if provider_qual_line:
                                        self.import_qual_line_ids.append(int(child_lines['id_no']))
                                        import_qual_lines_cnt += 1
#                                         print "CREATED CHILD ID WITH {}".format(provider_qual_line)
                                    else:
                                        print "CHILD ID NOT CREATED"
                        else:
                            print "DIDNT CREATED RECORD"
                            
                    else:
                        print "DICT WAS NOT PREPARED"
                
                if self.import_qual_ids:
                    log_dict['import_qualification_ids'] = str(self.import_qual_ids)
                    
                if self.import_qual_line_ids:
                    log_dict['import_qualification_lines'] = str(self.import_qual_line_ids)
                    
                    
                ''' Create Log '''
                if self.import_qual_ids or self.import_qual_line_ids:
                    log_dict['import_datetime'] = fields.Datetime().now()
                    user = self.env['res.users'].browse(self._uid)
                    log_dict['import_exec_by'] = user.name
                    log_create = self.env['xml.import.logs'].create(log_dict)
                    if log_create:
                        print "LOG WAS CREATED",log_create
                    else:
                        print "LOG WAS NOT CREATED"
                    
                self.status+=" Imported {} Unit Standards. {} Unit Standards Existed".format(import_qual_lines_cnt,import_qual_lines_exists_cnt)
            
        else:
            raise Warning("Please Select XML File to import.")
        
        
        return { 
            'context': self.env.context, 
            'view_type': 'form', 
            'view_mode': 'form', 
            'res_model': 'xml.import.seta', 
            'res_id': self.id, 
            'type': 'ir.actions.act_window', 
            'target': 'new'
            }
