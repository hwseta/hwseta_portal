import psycopg2
'''Python script to insert Skills Programme in Satellite Campus For Provider: The Order Of St John For Sa (HW592A0600149)'''

conn_string = "host='localhost' dbname='HWSETA' user='odoo' password='odoo'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
print "=============Script Started================="
cursor.execute(
    "select id, skills_programme_id, skill_saqa_id from skills_programme_master_rel where skills_programme_partner_rel_id = 78309")
skill_ids = cursor.fetchall()

for skill_id in skill_ids:
    cursor.execute("select id from res_partner where parent_id = 78309")
    child_ids = cursor.fetchall()
    for child_id in child_ids:
        print "-----Skill SAQA ID-------", skill_id[2]

        cursor.execute(
            "insert into skills_programme_master_campus_rel (skills_programme_id, skill_saqa_id, skills_programme_partner_campus_rel_id) values (%s, %s, %s)", ([skill_id[1], skill_id[2], child_id[0]]))

        cursor.execute(
            'select max(id) from skills_programme_master_campus_rel')
        master_campus_skill_id = cursor.fetchone()

        cursor.execute(
            "select name,type,id_no,title,level1,level2,level3,selection from skills_programme_unit_standards_master_rel where skills_programme_id ='%s'" % (skill_id[0]))
        skills_unit_ids = cursor.fetchall()

        for skills_unit_id in skills_unit_ids:
            cursor.execute("insert into skills_programme_unit_standards_master_campus_rel (name, type, id_no, title, level1, level2, level3, selection, skills_programme_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)", ([
                           str(skills_unit_id[3]), str(skills_unit_id[1]), str(skills_unit_id[2]), str(skills_unit_id[3]), str(skills_unit_id[4]), str(skills_unit_id[5]), str(skills_unit_id[6]), 'True', master_campus_skill_id[0]]))
conn.commit()
print "=================Script Ended==================="
