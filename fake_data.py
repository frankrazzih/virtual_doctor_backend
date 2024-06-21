from faker import Faker
import uuid
import random
from datetime import datetime, timedelta

# Initialize Faker to generate fake data
fake = Faker()

# Services list
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

# Generate services data
def generate_services(num_services, num_hospitals):
    services = []
    for _ in range(num_services):
        service = random.choice(services_list)
        cost = round(random.uniform(100, 1000), 2)  # Generate a random cost
        hosp_id = random.randint(1, num_hospitals)  # Assign service to a random hospital
        services.append((service, cost, hosp_id))
    return services

# Number of services and hospitals to generate
num_services = 50
num_hospitals = 20

services_data = generate_services(num_services, num_hospitals)

# Generate SQL insert statements for services
def generate_sql_inserts_services(data):
    sql_statements = []
    for service in data:
        sql = f"INSERT INTO services (service, cost, hosp_id) VALUES ('{service[0]}', {service[1]}, {service[2]});"
        sql_statements.append(sql)
    return sql_statements

# Generate SQL statements
services_sql = generate_sql_inserts_services(services_data)

# Write SQL statements to a file
with open('fake_services_data.sql', 'w') as f:
    f.write('-- SQL statements for inserting services\n\n')
    for sql in services_sql:
        f.write(sql + '\n')

print("SQL file for services generated successfully.")
