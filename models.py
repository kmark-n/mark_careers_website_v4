from app import db
from datetime import datetime

class Users(db.Model):
  __tablename__ = 'users'
  user_id=db.Column(db.Integer, primary_key=True)
  name=db.Column(db.String(256))
  email=db.Column(db.String(256))
  password=db.Column(db.String(256))

class Jobs(db.Model):
  __tablename__ = 'jobs'
  job_id=db.Column(db.Integer, primary_key=True)
  title=db.Column(db.String(256))
  location=db.Column(db.String(256))
  REQUIREMENTS=db.Column(db.String(2000))
  RESPONSIBILITIES=db.Column(db.String(2000))
  SALARY=db.Column(db.Numeric(precision=10, scale=2))

class Applications(db.Model):
  __tablename__ = 'applications'
  id=db.Column(db.Integer, primary_key=True)
  job_id=db.Column(db.Integer)
  full_name=db.Column(db.String(250))
  email=db.Column(db.String(250))
  linkedin_url=db.Column(db.String(500))
  education=db.Column(db.String(2000))
  work_experience=db.Column(db.String(2000))
  resume_url=db.Column(db.String(500))
  created_at=db.Column(db.DateTime, default=datetime.utcnow)
  updated_at=db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  status=db.Column(db.String(2000))