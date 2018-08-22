import psycopg2
'''Python script to insert Moderators in Satellite Campus For Provider: The Order Of St John For Sa (HW592A0600149)'''

conn_string = "host='localhost' dbname='HWSETA' user='odoo' password='odoo'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
print "=============Script Started================="
count = 0
cursor.execute(
    "select moderators_id, mwork_phone, mwork_email, moderator_sla_document, moderator_notification_letter from etqe_moderators_provider_rel where provider_id = 78309")
moderator_ids = cursor.fetchall()
for moderator_id in moderator_ids:
    cursor.execute("select id from res_partner where parent_id = 78309")
    child_ids = cursor.fetchall()
    for child_id in child_ids:
        count += 1
        print "Moderator Insert Count=====", count
        cursor.execute(
            "insert into etqe_moderators_provider_campus_rel (moderators_id, mwork_phone, mwork_email, campus_moderator_sla_document, moderator_notification_letter, provider_campus_id) values (%s, %s, %s, %s, %s, %s)", ([moderator_id[0], moderator_id[1], moderator_id[2], moderator_id[3], moderator_id[4], child_id[0]]))

conn.commit()
print "=================Script Ended==================="