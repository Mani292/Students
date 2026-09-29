import sys
import os
import csv
import json
import urllib.parse
from pymongo import MongoClient

# Get MONGODB_URL strictly from environment variables or safe local default
MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb://localhost:27017/smart_university"
)

def import_students_to_mongodb(csv_filepath: str):
    """
    Imports student records from a CSV file into MongoDB Atlas under the 'students' collection.
    Supported headers:
    Roll.No, Student Name, Branch, Semester, Gender, Mobile.No, Whatsapp.No, E-mail, Password
    """
    if not os.path.exists(csv_filepath):
        print(f"Error: CSV file '{csv_filepath}' not found.")
        return

    print(f"Connecting to MongoDB...")
    client = MongoClient(MONGODB_URL)
    db = client["smart_university"]
    students_collection = db["students"]

    imported_count = 0
    updated_count = 0

    try:
        with open(csv_filepath, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normalize column headers
                norm_row = {k.strip(): v.strip() for k, v in row.items() if k}

                email = norm_row.get("E-mail") or norm_row.get("email") or norm_row.get("Email")
                full_name = norm_row.get("Student Name") or norm_row.get("full_name") or norm_row.get("Name")
                roll_number = norm_row.get("Roll.No") or norm_row.get("roll_number") or norm_row.get("Roll No")
                branch = norm_row.get("Branch") or norm_row.get("department_code") or "CSE"
                semester = norm_row.get("Semester") or norm_row.get("semester") or "1"
                gender = norm_row.get("Gender") or norm_row.get("gender")
                mobile_number = norm_row.get("Mobile.No") or norm_row.get("mobile_number")
                whatsapp_number = norm_row.get("Whatsapp.No") or norm_row.get("whatsapp_number")
                password = norm_row.get("Password") or norm_row.get("password") or "Student@123"

                if not email or not full_name or not roll_number:
                    print(f"Skipping incomplete row: {row}")
                    continue

                student_document = {
                    "roll_number": roll_number,
                    "full_name": full_name,
                    "email": email,
                    "branch": branch.upper(),
                    "semester": int(semester) if semester.isdigit() else 1,
                    "gender": gender,
                    "mobile_number": mobile_number,
                    "whatsapp_number": whatsapp_number,
                    "password_initial": password,
                    "role": "STUDENT",
                    "status": "ACTIVE"
                }

                # Upsert into MongoDB by roll_number or email
                result = students_collection.update_one(
                    {"$or": [{"roll_number": roll_number}, {"email": email}]},
                    {"$set": student_document},
                    upsert=True
                )

                if result.upserted_id:
                    imported_count += 1
                else:
                    updated_count += 1

        print(f"\n✅ MongoDB Import Complete!")
        print(f"   - Imported new records: {imported_count}")
        print(f"   - Updated existing records: {updated_count}")
        print(f"   - Total records in MongoDB 'students' collection: {students_collection.count_documents({})}")

    except Exception as e:
        print(f"❌ Error during MongoDB import: {e}")

if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "students.csv"
    import_students_to_mongodb(filepath)
