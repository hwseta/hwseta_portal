import psycopg2
import calendar
import csv
from datetime import datetime

'''Python script to update DOB from Identification Number in SDF Registration'''

conn_string = "host='localhost' dbname='HWSETA' user='odoo' password='odoo'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()
count = 0

output_myfile = open('Invalid DOB in SDF Registration.csv', 'wb')
wr = csv.writer(output_myfile, delimiter='\t', quoting=csv.QUOTE_ALL)
wr.writerow(['Identification Number','System Birth Date', 'Date of Birth Should be'])

cursor.execute(
    "select id, identification_id, person_birth_date from sdf_register where citizen_resident_status_code in ('sa', 'dual')")
sdf_ids = cursor.fetchall()

for sdf_id in sdf_ids:
    if sdf_id[1] is not None:
        year = '19' + sdf_id[1][0:2]
        month = sdf_id[1][2:4]
        identification_id = sdf_id[1][4:6]
        day = sdf_id[1][4:6]
        if int(month) > 12 or int(month) < 1 or int(day) > 31 or int(day) < 1:
            pass
        else:
            #Calculating last day of month.
            last_day = calendar.monthrange(int(year),int(month))[1]
            if int(day) > last_day :
                pass
            else:
                birth_date = datetime.strptime(year + '-' + month + '-' + day, '%Y-%m-%d').date()
            if birth_date != sdf_id[2]:
                count += 1
                wr.writerow([str(sdf_id[1]), str(sdf_id[2]), str(birth_date)])
                print "====Identification Number====", sdf_id[1]
                print "1. System Birth Date:", sdf_id[2]
                print "2. Birth Date Should be:", birth_date
                cursor.execute(
                    "update sdf_register set person_birth_date = %s where id = %s", ([birth_date, sdf_id[0]]))
#Remove following comment to update DOB in the database
#conn.commit()
print "===Total DOB update Count===", count
