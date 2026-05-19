import json
import random
from datetime import datetime, timedelta

# ==========================================
# SAMPLE DATA
# ==========================================

names = [
    "Ramu", "Krishna", "Raghu", "Hari", "Raju",
    "Suresh", "Mahesh", "Kiran", "Naresh", "Lokesh",
    "Vijay", "Ajay", "Praveen", "Manoj", "Charan"
]

cities = [
    "Hyderabad",
    "Vijayawada",
    "Visakhapatnam",
    "Rajahmundry",
    "Warangal",
    "Guntur",
    "Kakinada",
    "Nellore"
]

marks1 = [
    "A MOLE NEAR THE NOSE.",
    "A MOLE ON THE LEFT HAND.",
    "A SCAR ON THE RIGHT CHEEK.",
    "A MOLE ON THE LEFT RING FINGER."
]

marks2 = [
    "A MOLE ON THE LEFT WRIST.",
    "A MOLE ON THE RIGHT TOE.",
    "A SCAR ON THE FOREHEAD.",
    "A MOLE ON THE RIGHT HAND."
]

# ==========================================
# GENERATE 1000 USERS
# ==========================================

generated = {}

for i in range(1, 1001):

    name = random.choice(names)
    father = random.choice(names)

    dob = datetime(
        random.randint(1965, 2002),
        random.randint(1, 12),
        random.randint(1, 28)
    )

    city = random.choice(cities)

    generated[str(i)] = {
        "sl_no": i,
        "application_id": i,
        "name": name,
        "father_name": father,
        "date_of_birth": dob.strftime("%Y-%m-%d"),
        "age": str(random.randint(18, 65)),
        "place_of_birth": city,
        "present_residing_at": city,
        "address_part_1": city,
        "address_part_2": city,
        "nationality": "INDIAN",
        "work_in_state": "ANDHRA PRADESH",
        "height": random.randint(150, 185),
        "identification_mark_1": random.choice(marks1),
        "identification_mark_2": random.choice(marks2),
        "mobile_no": str(random.randint(6000000000, 9999999999)),
        "class_of_certificate": "I",
        "challan_no": str(random.randint(10000000000000, 99999999999999)),
        "challan_date": (
            datetime.now() - timedelta(days=random.randint(1, 1000))
        ).strftime("%Y-%m-%d"),
        "amount": 500,
        "payment_status": "SUCCESS",
        "file_no": f"B3/{4000+i}/2021",
        "status": "ADMITTED",
        "reason": None,
        "date_of_exam": "18.06.2024",
        "result": random.choice(["PASS", "FAIL", None])
    }

# ==========================================
# SAVE FILE
# ==========================================

with open("Applicants.json", "w") as f:
    json.dump(generated, f, indent=4)

print("✅ 1000 Users Generated Successfully")