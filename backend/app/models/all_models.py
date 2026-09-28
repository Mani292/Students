import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, Float, JSON
)
from sqlalchemy.orm import relationship
from app.db.session import Base

class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    FACULTY = "FACULTY"
    HOD = "HOD"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student_profile = relationship("Student", back_populates="user", uselist=False)
    faculty_profile = relationship("Faculty", back_populates="user", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="actor")

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)

    students = relationship("Student", back_populates="department")
    faculty = relationship("Faculty", back_populates="department")
    courses = relationship("Course", back_populates="department")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    roll_number = Column(String, unique=True, index=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    year = Column(Integer, default=1)
    semester = Column(Integer, default=1)
    cgpa = Column(Float, default=0.0)
    skills = Column(JSON, default=list) # e.g. ["Python", "FastAPI"]
    career_interests = Column(JSON, default=list)

    user = relationship("User", back_populates="student_profile")
    department = relationship("Department", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student")
    attendance_records = relationship("AttendanceRecord", back_populates="student")
    permissions = relationship("PermissionRequest", back_populates="student")
    service_requests = relationship("ServiceRequest", back_populates="student")

class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    designation = Column(String, nullable=False)

    user = relationship("User", back_populates="faculty_profile")
    department = relationship("Department", back_populates="faculty")
    classes = relationship("ClassSession", back_populates="faculty")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    credits = Column(Integer, default=3)

    department = relationship("Department", back_populates="courses")
    classes = relationship("ClassSession", back_populates="course")

class ClassSession(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.id"), nullable=False)
    academic_year = Column(String, nullable=False)
    semester = Column(Integer, nullable=False)
    room_number = Column(String, nullable=False)

    course = relationship("Course", back_populates="classes")
    faculty = relationship("Faculty", back_populates="classes")
    enrollments = relationship("Enrollment", back_populates="class_session")
    attendance_sessions = relationship("AttendanceSession", back_populates="class_session")

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="enrollments")
    class_session = relationship("ClassSession", back_populates="enrollments")

class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.id"), nullable=False)
    session_token = Column(String, unique=True, nullable=False)
    totp_secret = Column(String, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    class_session = relationship("ClassSession", back_populates="attendance_sessions")
    records = relationship("AttendanceRecord", back_populates="session")

class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    FLAGGED = "FLAGGED"

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    device_fingerprint = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    status = Column(SQLEnum(AttendanceStatus), default=AttendanceStatus.PRESENT)

    session = relationship("AttendanceSession", back_populates="records")
    student = relationship("Student", back_populates="attendance_records")
    anomalies = relationship("AttendanceAnomaly", back_populates="record")

class AttendanceAnomaly(Base):
    __tablename__ = "attendance_anomalies"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("attendance_records.id"), nullable=False)
    reason = Column(String, nullable=False) # e.g. "Duplicate device fingerprint", "Time window mismatch"
    severity = Column(String, default="WARNING") # WARNING, HIGH
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    record = relationship("AttendanceRecord", back_populates="anomalies")

class PermissionStatus(str, enum.Enum):
    PENDING = "PENDING"
    FACULTY_REVIEW = "FACULTY_REVIEW"
    HOD_REVIEW = "HOD_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class PermissionRequest(Base):
    __tablename__ = "permission_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    reason = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    proof_url = Column(String, nullable=True)
    comments = Column(Text, nullable=True)
    status = Column(SQLEnum(PermissionStatus), default=PermissionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="permissions")

class ServiceType(str, enum.Enum):
    BONAFIDE = "BONAFIDE"
    ID_CARD = "ID_CARD"
    HOSTEL = "HOSTEL"
    TRANSPORT = "TRANSPORT"
    OTHER = "OTHER"

class ServiceRequestStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    IN_PROGRESS = "IN_PROGRESS"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    service_type = Column(SQLEnum(ServiceType), nullable=False)
    details = Column(JSON, default=dict)
    status = Column(SQLEnum(ServiceRequestStatus), default=ServiceRequestStatus.SUBMITTED)
    issued_document_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="service_requests")

class NotificationPriority(str, enum.Enum):
    CRITICAL = "CRITICAL"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    INFORMATIONAL = "INFORMATIONAL"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String, default="SYSTEM")
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.INFORMATIONAL)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False) # e.g. "REGULATIONS", "COURSES", "FAQS"
    content = Column(Text, nullable=False)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False) # e.g. "ATTENDANCE_CREATED", "PERMISSION_APPROVED"
    resource = Column(String, nullable=False)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)

    actor = relationship("User", back_populates="audit_logs")

# --- Extended Campus & AI Ecosystem Models ---

class LibraryBook(Base):
    __tablename__ = "library_books"

    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    category = Column(String, nullable=False)
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)

class LibraryBorrowRecord(Base):
    __tablename__ = "library_borrow_records"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("library_books.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    borrowed_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    returned_at = Column(DateTime, nullable=True)
    fine_amount = Column(Float, default=0.0)

class HostelRoom(Base):
    __tablename__ = "hostel_rooms"

    id = Column(Integer, primary_key=True, index=True)
    block_name = Column(String, nullable=False)
    room_number = Column(String, nullable=False)
    capacity = Column(Integer, default=2)
    occupied_beds = Column(Integer, default=0)

class HostelComplaint(Base):
    __tablename__ = "hostel_complaints"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    room_number = Column(String, nullable=False)
    issue_type = Column(String, nullable=False) # e.g. "Plumbing", "Electrical", "Cleaning"
    description = Column(Text, nullable=False)
    status = Column(String, default="OPEN") # OPEN, IN_PROGRESS, RESOLVED
    created_at = Column(DateTime, default=datetime.utcnow)

class TransportRoute(Base):
    __tablename__ = "transport_routes"

    id = Column(Integer, primary_key=True, index=True)
    route_name = Column(String, nullable=False)
    bus_number = Column(String, nullable=False)
    driver_contact = Column(String, nullable=True)
    pickup_points = Column(JSON, default=list)
    departure_time = Column(String, nullable=False)

class CampusEvent(Base):
    __tablename__ = "campus_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False) # e.g. "Hackathon", "Seminar", "Workshop"
    event_date = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    organizer = Column(String, nullable=False)

class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("campus_events.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)

class StudentSkillPassport(Base):
    __tablename__ = "student_skill_passports"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True, nullable=False)
    verified_skills = Column(JSON, default=list)
    certifications = Column(JSON, default=list)
    achievements = Column(JSON, default=list)
    projects_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)

class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)

class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id"), nullable=False)
    sender = Column(String, nullable=False) # "user" or "assistant"
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# --- Additional Core Data Entities for Sections 1-13 ---

class AcademicActivity(Base):
    __tablename__ = "academic_activities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    due_date = Column(DateTime, nullable=True)
    activity_type = Column(String, default="ANNOUNCEMENT") # ANNOUNCEMENT, ASSIGNMENT, TASK, NOTICE
    created_at = Column(DateTime, default=datetime.utcnow)

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    unit_number = Column(Integer, default=1)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="PLANNED") # PLANNED, IN_PROGRESS, COMPLETED
    completed_at = Column(DateTime, nullable=True)

class LearningTrack(Base):
    __tablename__ = "learning_tracks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False) # e.g. "Full-Stack", "AI/ML", "Cloud"
    target_role = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

class LearningResource(Base):
    __tablename__ = "learning_resources"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("learning_tracks.id"), nullable=False)
    title = Column(String, nullable=False)
    resource_type = Column(String, default="ARTICLE") # ARTICLE, VIDEO, DOCUMENT, QUIZ
    url_or_content = Column(Text, nullable=False)
    sequence_order = Column(Integer, default=1)

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("learning_tracks.id"), nullable=True)
    title = Column(String, nullable=False)
    questions = Column(JSON, default=list) # [{question, options, correct_answer_idx}]

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    score = Column(Float, default=0.0)
    passed = Column(Boolean, default=False)
    attempted_at = Column(DateTime, default=datetime.utcnow)

class StudentProgress(Base):
    __tablename__ = "student_progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("learning_tracks.id"), nullable=False)
    completed_resources = Column(JSON, default=list) # [resource_ids]
    progress_percentage = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    resume_text = Column(Text, nullable=False)
    file_name = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class ATSAnalysis(Base):
    __tablename__ = "ats_analyses"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_description = Column(Text, nullable=False)
    ats_score = Column(Float, default=0.0)
    missing_keywords = Column(JSON, default=list)
    improvements = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    website = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    industry = Column(String, nullable=True)
    location = Column(String, nullable=True)

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    min_cgpa = Column(Float, default=6.0)
    allowed_departments = Column(JSON, default=list)
    package_ctc = Column(String, nullable=False) # e.g. "12 LPA"
    application_deadline = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

class PlacementDrive(Base):
    __tablename__ = "placement_drives"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    drive_date = Column(DateTime, nullable=False)
    venue = Column(String, nullable=False)
    status = Column(String, default="SCHEDULED") # SCHEDULED, ONGOING, COMPLETED

class JobApplicationStatus(str, enum.Enum):
    APPLIED = "APPLIED"
    ASSESSMENT = "ASSESSMENT"
    INTERVIEW = "INTERVIEW"
    OFFERED = "OFFERED"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"

class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    status = Column(SQLEnum(JobApplicationStatus), default=JobApplicationStatus.APPLIED)
    applied_at = Column(DateTime, default=datetime.utcnow)

class InterviewStage(Base):
    __tablename__ = "interview_stages"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False)
    stage_name = Column(String, nullable=False) # e.g. "Technical Round 1"
    scheduled_at = Column(DateTime, nullable=False)
    feedback = Column(Text, nullable=True)
    status = Column(String, default="PENDING") # PENDING, PASSED, FAILED

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False)
    ctc_offered = Column(String, nullable=False)
    joining_date = Column(DateTime, nullable=True)
    offer_letter_url = Column(String, nullable=True)
    is_accepted = Column(Boolean, default=False)
