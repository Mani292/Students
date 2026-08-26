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
    allowed_latitude = Column(Float, nullable=True) # e.g. 12.9716
    allowed_longitude = Column(Float, nullable=True) # e.g. 77.5946
    radius_meters = Column(Float, default=150.0) # Geofence tolerance

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
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
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
    resolution_notes = Column(String, nullable=True)

    record = relationship("AttendanceRecord", back_populates="anomalies")

class PermissionStatus(str, enum.Enum):
    PENDING = "PENDING"
    FACULTY_REVIEW = "FACULTY_REVIEW"
    HOD_REVIEW = "HOD_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class PermissionRequest(Base):
    __tablename__ = "permission_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    reason = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    proof_url = Column(String, nullable=True)
    comments = Column(Text, nullable=True)
    faculty_comment = Column(Text, nullable=True)
    hod_comment = Column(Text, nullable=True)
    status = Column(SQLEnum(PermissionStatus), default=PermissionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="permissions")

class ServiceType(str, enum.Enum):
    BONAFIDE = "BONAFIDE"
    ID_CARD = "ID_CARD"
    TRANSCRIPT = "TRANSCRIPT"
    STUDY_CERTIFICATE = "STUDY_CERTIFICATE"
    HOSTEL = "HOSTEL"
    TRANSPORT = "TRANSPORT"
    LIBRARY_CARD = "LIBRARY_CARD"
    FEE_CONCESSION = "FEE_CONCESSION"
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
    verification_token = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="service_requests")

class DigitalStudentIdCard(Base):
    __tablename__ = "digital_id_cards"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True, nullable=False)
    card_number = Column(String, unique=True, nullable=False)
    verification_token = Column(String, unique=True, nullable=False)
    qr_signature = Column(String, nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    due_date = Column(DateTime, nullable=False)
    max_marks = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)

class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    submission_text = Column(Text, nullable=True)
    attachment_url = Column(String, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    marks_obtained = Column(Float, nullable=True)
    faculty_feedback = Column(Text, nullable=True)

class LibraryBook(Base):
    __tablename__ = "library_books"

    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    category = Column(String, nullable=False)
    total_copies = Column(Integer, default=5)
    available_copies = Column(Integer, default=5)

class LibraryBorrowRecord(Base):
    __tablename__ = "library_borrows"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("library_books.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    borrowed_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    returned_at = Column(DateTime, nullable=True)
    fine_amount = Column(Float, default=0.0)
    status = Column(String, default="BORROWED") # BORROWED, RETURNED, OVERDUE

class HostelRoom(Base):
    __tablename__ = "hostel_rooms"

    id = Column(Integer, primary_key=True, index=True)
    hostel_name = Column(String, nullable=False)
    room_number = Column(String, nullable=False)
    capacity = Column(Integer, default=2)
    occupied_count = Column(Integer, default=0)

class HostelComplaint(Base):
    __tablename__ = "hostel_complaints"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    category = Column(String, nullable=False) # e.g. "PLUMBING", "ELECTRICAL", "MESS"
    description = Column(Text, nullable=False)
    status = Column(String, default="OPEN") # OPEN, IN_PROGRESS, RESOLVED
    created_at = Column(DateTime, default=datetime.utcnow)

class TransportRoute(Base):
    __tablename__ = "transport_routes"

    id = Column(Integer, primary_key=True, index=True)
    route_name = Column(String, nullable=False)
    bus_number = Column(String, nullable=False)
    stops = Column(JSON, default=list) # e.g. ["Central Station", "Tech Park", "Campus Gate"]
    schedule_time = Column(String, nullable=False)

class BusPass(Base):
    __tablename__ = "bus_passes"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("transport_routes.id"), nullable=False)
    pass_number = Column(String, unique=True, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

class CampusEvent(Base):
    __tablename__ = "campus_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False) # HACKATHON, WORKSHOP, SEMINAR, CLUB
    description = Column(Text, nullable=False)
    event_date = Column(DateTime, nullable=False)
    venue = Column(String, nullable=False)
    registration_open = Column(Boolean, default=True)

class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("campus_events.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    attended = Column(Boolean, default=False)

class StudentSkillPassport(Base):
    __tablename__ = "student_skill_passports"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    skill_name = Column(String, nullable=False)
    proficiency = Column(String, default="INTERMEDIATE") # BEGINNER, INTERMEDIATE, ADVANCED, EXPERT
    verified_by_faculty = Column(Boolean, default=True)
    badge_title = Column(String, nullable=True)
    details = Column(JSON, default=dict) # Certifications, project links, hackathon awards

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
    category = Column(String, nullable=False) # e.g. "REGULATIONS", "COURSES", "FAQS", "LIBRARY", "HOSTEL"
    content = Column(Text, nullable=False)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="New Consultation")
    created_at = Column(DateTime, default=datetime.utcnow)

class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id"), nullable=False)
    sender = Column(String, nullable=False) # "USER" or "ASSISTANT"
    content = Column(Text, nullable=False)
    tools_used = Column(JSON, default=list)
    sources = Column(JSON, default=list)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False) # e.g. "ATTENDANCE_CREATED", "PERMISSION_APPROVED"
    resource = Column(String, nullable=False)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)

    actor = relationship("User", back_populates="audit_logs")
