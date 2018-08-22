import psycopg2
import csv

'''Python script to extract data for approved learners but not present in learner master'''

conn_string = "host='localhost' dbname='HWSETA' user='odoo' password='odoo'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
output_myfile = open('Learners.csv', 'wb')
wr = csv.writer(output_myfile, delimiter='\t', quoting=csv.QUOTE_ALL)

wr.writerow(
    ['First Name', 'Last Name', 'RSA Identification No.', 'Provider Name'])

#################Qualification's Learners##################
cursor.execute(
    "select name, person_last_name, identification_id, provider_id from learner_registration where id in (select learner_qualification_id from learner_registration_qualification where learner_id is null and learner_qualification_id in (select id from learner_registration where state = 'approved' and is_existing_learner = True))")
learner_ids = cursor.fetchall()

#################Skill Programme Learners###################
# cursor.execute(
#     "select name, person_last_name, identification_id, provider_id from learner_registration where id in (select skills_programme_learner_rel_id from skills_programme_learner_rel where skills_programme_learner_rel_ids is null and skills_programme_learner_rel_id in (select id from learner_registration where state = 'approved' and is_existing_learner = True))")
# learner_ids = cursor.fetchall()

#################Learning Programme Learners#################
# cursor.execute(
#     "select name, person_last_name, identification_id, provider_id from learner_registration where id in (select learning_programme_learner_rel_id from learning_programme_learner_rel where learning_programme_learner_rel_ids is null and learning_programme_learner_rel_id in (select id from learner_registration where state = 'approved' and is_existing_learner = True))")
# learner_ids = cursor.fetchall()

for learner_id in learner_ids:
    print learner_id[3]
    if learner_id[3] is not None:
        cursor.execute(
            "select name from res_partner where id = %s" % (learner_id[3]))
        provider_id = cursor.fetchone()
        wr.writerow(
            [str(learner_id[0]), str(learner_id[1]), str(learner_id[2]), str(provider_id[0])])
    else:
        wr.writerow(
            [str(learner_id[0]), str(learner_id[1]), str(learner_id[2])])
