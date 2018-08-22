import psycopg2
'''Python script to insert Assessors in Satellite Campus For Provider: The Order Of St John For Sa (HW592A0600149)'''

conn_string = "host='localhost' dbname='HWSETA' user='odoo' password='odoo'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
print "=============Script Started================="
count = 0
cursor.execute(
    "select assessors_id, awork_phone, awork_email, assessor_sla_document, assessor_notification_letter from etqe_assessors_provider_rel where provider_id = 78309")
assessor_ids = cursor.fetchall()
for assessor_id in assessor_ids:
    cursor.execute("select id from res_partner where parent_id = 78309")
    child_ids = cursor.fetchall()
    for child_id in child_ids:
        count += 1
        print "Assessor Insert Count=====", count
        cursor.execute(
            "insert into etqe_assessors_provider_campus_rel (assessors_id, awork_phone, awork_email, campus_assessor_sla_document, assessor_notification_letter, provider_campus_id) values (%s, %s, %s, %s, %s, %s)", ([assessor_id[0], assessor_id[1], assessor_id[2], assessor_id[3], assessor_id[4], child_id[0]]))

conn.commit()
print "=================Script Ended==================="