import psycopg2
import datetime

'''Python script to update existing Assessments which are associated with SAQA Qual ID: 23993'''
from datetime import datetime

conn_string = "host='localhost' dbname='HWSETA' user='odoo' password='odoo'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

print("*****************Script Started*******************")

cursor.execute('select id from provider_qualification_line where line_id = 203')
unit_standards_ids_list = map(lambda x:x[0], cursor.fetchall())

#Draft
cursor.execute('select qual_learner_assessment_line_id from qualification_id where provider_qualification_id = 203')
assessment_line_ids_list = map(lambda x:x[0], cursor.fetchall())

for assessment_id in assessment_line_ids_list:
    for unit_id in unit_standards_ids_list:
        cursor.execute('select * from unit_standards_id where unit_standards_learner_assessment_line_id = %s and provider_qualification_line_id = %s', ([assessment_id, unit_id]))
        record_exists = cursor.fetchall()
        if not record_exists:
            print "==Inside 1=="
            cursor.execute('insert into unit_standards_id (unit_standards_learner_assessment_line_id, provider_qualification_line_id) values (%s, %s)', ([assessment_id, unit_id]))

#Submit
cursor.execute('select qualification_verify_id from verify_asse_qual_rel where qual_learner_assessment_verify_line_id = 203')
assessment_verify_line_ids_list = map(lambda x:x[0], cursor.fetchall())

for assessment_verify_id in assessment_verify_line_ids_list:
    for unit_id in unit_standards_ids_list:
        cursor.execute('select * from verify_asse_unit_rel where unit_standards_verify_id = %s and unit_standards_learner_assessment_verify_line_id = %s', ([assessment_verify_id, unit_id]))
        record_exists = cursor.fetchall()
        if not record_exists:
            print "==Inside 2=="
            cursor.execute('insert into verify_asse_unit_rel (unit_standards_verify_id, unit_standards_learner_assessment_verify_line_id) values (%s, %s)', ([assessment_verify_id, unit_id]))

#Verified
cursor.execute('select qualification_verify_id from evaluate_asse_qual_rel where qual_learner_assessment_verify_line_id = 203')
assessment_evaluate_line_ids_list = map(lambda x:x[0], cursor.fetchall())
for assessment_evaluate_id in assessment_evaluate_line_ids_list:
    for unit_id in unit_standards_ids_list:
        cursor.execute('select * from evaluate_asse_unit_rel where unit_standards_verify_id = %s and unit_standards_learner_assessment_verify_line_id = %s', ([assessment_evaluate_id, unit_id]))
        record_exists = cursor.fetchall()
        if not record_exists:
            print "==Inside 3=="
            cursor.execute('insert into evaluate_asse_unit_rel (unit_standards_verify_id, unit_standards_learner_assessment_verify_line_id) values (%s, %s)', ([assessment_evaluate_id, unit_id]))

#Evaluated
cursor.execute('select qualification_achieve_id from achieve_asse_qual_rel where qual_achieve_learner_assessment_line_id = 203')
assessment_achieve_line_ids_list = map(lambda x:x[0], cursor.fetchall())
for assessment_achieve_line_id in assessment_achieve_line_ids_list:
    for unit_id in unit_standards_ids_list:
        cursor.execute('select * from achieve_asse_unit_rel where unit_standards_achieve_id = %s and unit_standards_learner_assessment_achieve_line_id = %s', ([assessment_achieve_line_id, unit_id]))
        record_exists = cursor.fetchall()
        if not record_exists:
            print "==Inside 4=="
            cursor.execute('insert into achieve_asse_unit_rel (unit_standards_achieve_id, unit_standards_learner_assessment_achieve_line_id) values (%s, %s)', ([assessment_achieve_line_id, unit_id]))

#Achieve
cursor.execute('select qualification_achieved_id from achieved_asse_qual_rel where qual_achieve_learner_assessment_line_id = 203')
assessment_achieved_line_ids_list = map(lambda x:x[0], cursor.fetchall())
for assessment_achieved_line_id in assessment_achieved_line_ids_list:
    for unit_id in unit_standards_ids_list:
        cursor.execute('select * from achieved_asse_unit_rel where unit_standards_achieved_id = %s and unit_standards_learner_assessment_achieve_line_id = %s', ([assessment_achieved_line_id, unit_id]))
        record_exists = cursor.fetchall()
        if not record_exists:
            print "==Inside 5=="
            cursor.execute('insert into achieved_asse_unit_rel (unit_standards_achieved_id, unit_standards_learner_assessment_achieve_line_id) values (%s, %s)', ([assessment_achieved_line_id, unit_id]))
    cursor.execute("update learner_assessment_achieved_line set is_learner_achieved = True where id = %s", ([assessment_achieved_line_id]))
    
    cursor.execute("select learner_id from learner_assessment_achieved_line where id = %s",([assessment_achieved_line_id]))
    learner_id = map(lambda x:x[0], cursor.fetchall())
    cursor.execute("select id, learner_qualification_parent_id from learner_registration_qualification where learner_id = %s",([learner_id[0]]))
    learner_registration_qual_ids = cursor.fetchall()
    for learner_registration_qual_id in learner_registration_qual_ids:
        if learner_registration_qual_id[1] == 203:
            print "==Inside 6=="
            certificate_date = datetime.now()
            cursor.execute("update learner_registration_qualification set is_learner_achieved = True, is_complete = True, certificate_date = %s where id = %s",([certificate_date, learner_registration_qual_id[0]]))

conn.commit()
print("****************Script Ended********************")
   