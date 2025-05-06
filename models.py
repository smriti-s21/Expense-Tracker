from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and access control"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')  # admin, customer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Employee(db.Model):
    """Employee model for storing staff information"""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    position = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    join_date = db.Column(db.Date, nullable=False)
    contact_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    hourly_rate = db.Column(db.Float, nullable=False)
    is_blue_card = db.Column(db.Boolean, default=False)  # Special category for extra pay on weekoffs
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    attendances = db.relationship('Attendance', backref='employee', lazy=True)
    leaves = db.relationship('Leave', backref='employee', lazy=True)
    payrolls = db.relationship('Payroll', backref='employee', lazy=True)
    
    def __repr__(self):
        return f'<Employee {self.first_name} {self.last_name}>'


class Attendance(db.Model):
    """Attendance model for tracking daily attendance with split shifts"""
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Morning shift (10-3)
    morning_present = db.Column(db.Boolean, default=False)
    morning_in_time = db.Column(db.Time)
    morning_out_time = db.Column(db.Time)
    
    # Evening shift (6-10)
    evening_present = db.Column(db.Boolean, default=False)
    evening_in_time = db.Column(db.Time)
    evening_out_time = db.Column(db.Time)
    
    # Calculated fields
    status = db.Column(db.String(20))  # 'present', 'half-day', 'absent'
    notes = db.Column(db.Text)
    
    def calculate_status(self):
        """Calculate attendance status based on morning and evening shifts"""
        if self.morning_present and self.evening_present:
            self.status = 'present'
        elif self.morning_present or self.evening_present:
            self.status = 'half-day'
        else:
            self.status = 'absent'
        return self.status
    
    def __repr__(self):
        return f'<Attendance {self.employee_id} on {self.date}: {self.status}>'


class Leave(db.Model):
    """Leave model for tracking employee leaves"""
    __tablename__ = 'leaves'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    leave_type = db.Column(db.String(20), nullable=False)  # sick, vacation, personal
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, approved, rejected
    reason = db.Column(db.Text)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Leave {self.employee_id} from {self.start_date} to {self.end_date}>'


class Payroll(db.Model):
    """Payroll model for employee salary processing"""
    __tablename__ = 'payrolls'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    total_days = db.Column(db.Integer, nullable=False)
    present_days = db.Column(db.Integer, nullable=False)
    half_days = db.Column(db.Integer, nullable=False)
    absent_days = db.Column(db.Integer, nullable=False)
    weekoff_days = db.Column(db.Integer, nullable=False)
    weekoff_worked = db.Column(db.Integer, nullable=False)  # For extra pay calculation
    base_salary = db.Column(db.Float, nullable=False)
    overtime_hours = db.Column(db.Float, default=0.0)
    overtime_pay = db.Column(db.Float, default=0.0)
    bonus = db.Column(db.Float, default=0.0)
    deductions = db.Column(db.Float, default=0.0)
    net_salary = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid
    payment_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<Payroll {self.employee_id} for {self.period_start} to {self.period_end}>'


class Expenditure(db.Model):
    """Expenditure model for tracking hotel expenses"""
    __tablename__ = 'expenditures'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # groceries, gas, utilities, maintenance, etc.
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    vendor = db.Column(db.String(100))
    receipt_number = db.Column(db.String(50))
    payment_method = db.Column(db.String(50))
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<Expenditure {self.category} {self.amount} on {self.date}>'


class DailyBalance(db.Model):
    """Daily Balance model for tracking opening and closing balances"""
    __tablename__ = 'daily_balances'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    opening_balance = db.Column(db.Float, nullable=False)
    closing_balance = db.Column(db.Float, nullable=False)
    total_income = db.Column(db.Float, nullable=False)
    total_expenditure = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DailyBalance {self.date}: {self.opening_balance} to {self.closing_balance}>'