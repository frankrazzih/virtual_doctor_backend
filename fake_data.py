from faker import Faker
import uuid
import random
from datetime import datetime, timedelta

# Initialize Faker to generate fake data
fake = Faker()

# Generate hospitals data
def generate_hospitals(num_hospitals):
    hospitals = []
    for _ in range(num_hospitals):
        hosp_uuid = str(uuid.uuid4())  # Generate a unique UUID
        hosp_name = fake.
        hosp_location = fake.address()
        contact = fake.phone_number()
        email = fake.email()
        password = fake.password()
        reg_date = fake.date_between(start_date='-10y', end_date='today')
        hospitals.append((hosp_uuid, hosp_name, hosp_location, contact, email, password, reg_date))
    return hospitals

# Generate staff data
services_list = [
    "Emergency Care",
    "Cardiology",
    "Neurology",
    "Orthopedics",
    "Gastroenterology",
    "Radiology",
    "Pathology",
    "Pediatrics",
    "Psychiatry",
    "Dermatology",
    "Obstetrics",
    "Gynecology"
]

def generate_staff(num_staff, num_hospitals):
    staff = []
    for _ in range(num_staff):
        staff_uuid = str(uuid.uuid4())  # Generate a unique UUID
        staff_name = fake.name()
        service = random.choice(services_list)
        availability = random.choice([True, False])
        hosp_id = random.randint(1, num_hospitals)  # Assign staff to a random hospital
        staff.append((staff_uuid, staff_name, service, availability, hosp_id))
    return staff

# Number of hospitals and staff to generate
num_hospitals = 20
num_staff = 100

hospitals_data = generate_hospitals(num_hospitals)
staff_data = generate_staff(num_staff, num_hospitals)

# Generate SQL insert statements
def generate_sql_inserts_hospitals(data):
    sql_statements = []
    for hosp in data:
        sql = f"INSERT INTO hospitals (hosp_uuid, hosp_name, hosp_location, contact, email, password, reg_date) VALUES ('{hosp[0]}', '{hosp[1]}', '{hosp[2]}', '{hosp[3]}', '{hosp[4]}', '{hosp[5]}', '{hosp[6]}');"
        sql_statements.append(sql)
    return sql_statements

def generate_sql_inserts_staff(data):
    sql_statements = []
    for staff in data:
        sql = f"INSERT INTO staff (staff_uuid, staff_name, service, availability, hosp_id) VALUES ('{staff[0]}', '{staff[1]}', '{staff[2]}', {staff[3]}, {staff[4]});"
        sql_statements.append(sql)
    return sql_statements

# Generate SQL statements
hospitals_sql = generate_sql_inserts_hospitals(hospitals_data)
staff_sql = generate_sql_inserts_staff(staff_data)

# Write SQL statements to a file
with open('fake_data.sql', 'w') as f:
    f.write('-- SQL statements for inserting hospitals\n\n')
    for sql in hospitals_sql:
        f.write(sql + '\n')
    f.write('\n-- SQL statements for inserting staff\n\n')
    for sql in staff_sql:
        f.write(sql + '\n')

print("SQL file generated successfully.")
