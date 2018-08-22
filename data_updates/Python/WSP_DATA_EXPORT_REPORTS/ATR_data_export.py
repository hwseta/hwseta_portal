import csv
import psycopg2

'''Python Script to extract ATR Data for financial year 2018-2019'''

output_myfile = open('ATR_data_2018-2019.csv', 'wb')
wr = csv.writer(output_myfile, delimiter='\t', quoting=csv.QUOTE_ALL)
print "**********Script Started*************"
try:
    conn_string = "host='localhost' dbname='HWSETA' user='odoo' password='odoo'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    wr.writerow(["First Name", "Surname", "Employee ID", "Type Of Training Intervention", "Training Type", "Start Date", "End Date", "OFO Code", "Occupation", "NQF level",
                 "Qualification", "Name of Training Intervention", "Pivotal Programme Qualification", "Pivotal Programme Institution", "Employer Name",
                 "SDL No.", "Contact", "Provider Name", "Provider Accreditation No.", "Provider Contacts", "Province", "City", "Urban-Rural", "Cost",
                 "Race", "Gender", "Age", "Disability", "Youth", "Non-RSA citizen", 'Employment Status'])

    # Getting WSP's which are in current year.
    cursor.execute('select id from wsp_plan where fiscal_year = 30')
    wsp_ids = cursor.fetchall()

    for wsp_id in wsp_ids:
        cursor.execute(
            'select employer_id from wsp_plan where id = %s', (wsp_id,))
        wsp_plan_id = cursor.fetchone()

        cursor.execute(
            'select employer_sdl_no, name from res_partner where employer = True and id = %s' % (wsp_plan_id[0],))
        res_partner_id = cursor.fetchone()
        cursor.execute("select training_type, name, surname, employee_id, code, occupation, specialization,\
                learner_province, city_id, urban, socio_economic_status, type_training, other_type_of_intervention,\
                name_training, pivotal_programme_institution, pivotal_programme_qualification, training_cost,\
                start_date, end_date, nqf_aligned, nqf_level, population_group, gender, dissability from actual_training_fields where actual_wsp_id = %s", (wsp_id,))
        actual_training_ids = cursor.fetchall()
        if actual_training_ids:
            for actual_training in actual_training_ids:
                # Province
                cursor.execute(
                    "select name from res_country_state where id = %s", (actual_training[7],))
                province_name = cursor.fetchone()
                if province_name is None:
                    pass
                else:
                    province_name = province_name[0]

                # City
                cursor.execute(
                    "select name from res_city where id = %s", (actual_training[8],))
                city_name = cursor.fetchone()
                if city_name is None:
                    pass
                else:
                    city_name = city_name[0]

                # Getting well formated data for printing OFO Code
                cursor.execute(
                    "select name from ofo_code where id = %s", (actual_training[4],))
                ofo_code = cursor.fetchone()
                if ofo_code is None:
                    pass
                else:
                    ofo_code = ofo_code[0]

                # occupation
                cursor.execute(
                    'select name from occupation_ofo where id = %s', (actual_training[5],))
                occupation_name = cursor.fetchone()
                if occupation_name is None:
                    pass
                else:
                    occupation_name = occupation_name[0]

                # Population Group
                race = ''
                is_non_RSA_citizen = False
                if actual_training[21] == 'african':
                    race = 'African'
                    is_non_RSA_citizen = 'False'
                elif actual_training[21] == 'coloured':
                    race = 'Coloured'
                    is_non_RSA_citizen = 'True'
                elif actual_training[21] == 'indian':
                    race = 'Indian'
                    is_non_RSA_citizen = 'True'
                elif actual_training[21] == 'white':
                    race = 'White'
                    is_non_RSA_citizen = 'True'

                # Gender
                gender = ''
                if actual_training[22] == 'male':
                    gender = 'M-Male'
                elif actual_training[22] == 'female':
                    gender = 'F-female'

                # Type Of Training Intervention
                type_training = ''
                cursor.execute(
                    "select name from training_intervention where id = %s", (actual_training[11],))
                type_training = cursor.fetchone()
                if type_training is None:
                    pass
                else:
                    type_training = type_training[0]

                wr.writerow([actual_training[1], actual_training[2], actual_training[3], type_training,
                             actual_training[0], actual_training[17], actual_training[
                                 18], ofo_code, occupation_name, actual_training[20],
                             '', actual_training[13], actual_training[15], actual_training[
                                 14], res_partner_id[1], res_partner_id[0],
                             '', '', '', '', province_name, city_name, actual_training[
                                 9], actual_training[16],
                             race, gender, '', actual_training[23], '', is_non_RSA_citizen, actual_training[10]])
finally:
    pass

print "**********Script Ended*************"
