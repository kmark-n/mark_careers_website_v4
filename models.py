from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
from flask_login import UserMixin


db=SQLAlchemy()

class Users(db.Model, UserMixin):
  __tablename__ = 'users'
  user_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  name=db.Column(db.String(256), nullable=False)
  email=db.Column(db.String(256), unique=True)
  password=db.Column(db.String(256))
  is_admin=db.Column(db.Boolean, default=False)
  profile_pic=db.Column(db.String(256), nullable=False, default='default.jpeg')
  def __init__(self, name, email, password, user_id=None, is_admin=False, profile_pic=None):
    self.user_id=user_id
    self.name=name
    self.email=email
    self.password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    self.is_admin=is_admin
    self.profile_pic=profile_pic

  def check_password(self, password):
    return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
  
  def get_id(self):
    return str(self.user_id)
  
  
  @property
  def is_active(self):
    return True
  
class Jobs(db.Model):
  __tablename__ = 'jobs'
  job_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
  title=db.Column(db.String(256))
  location=db.Column(db.String(256))
  REQUIREMENTS=db.Column(db.String(2000))
  RESPONSIBILITIES=db.Column(db.String(2000))
  CURRENCY=db.Column(db.String(50))
  SALARY=db.Column(db.Numeric(precision=10, scale=2))

class Applications(db.Model):
  __tablename__ = 'applications'
  id=db.Column(db.Integer, primary_key=True, autoincrement=True)
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
