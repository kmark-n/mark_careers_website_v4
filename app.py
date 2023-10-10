from flask import Flask, render_template, jsonify, request, redirect, session, url_for, flash
from database import db_login_validation, load_jobs_from_db, load_job_from_db, add_application_to_db, add_user_details_to_db, db_login_validation, status_validation, status_results
import os
import pymysql
from models import db, Users, Jobs, Applications
from admin_setup import admin
from sqlalchemy.exc import IntegrityError

def create_app(): 
  app = Flask(__name__)
  app.secret_key = ['SECRET_KEY']

  app.config['SQLALCHEMY_DATABASE_URI']=os.environ['DB_CONNECTION_STRING']
  app.config['SQLALCHEMY_ENGINE_OPTIONS']={ "connect_args": {
        "ssl": {
            "ssl_ca": "/etc/ssl/cert.pem"
        }
    }
  }

  db.init_app(app)

  with app.app_context():
    db.create_all() 

  admin.init_app(app)

   
  @app.route('/')
  def login():
    return render_template('login.html')
  
  @app.route('/register_form')
  def register_form():
    return render_template('register_form.html')
  
  
  @app.route("/register_form/registered", methods=['POST', 'GET'])
  def register_complete():
    if request.method == 'POST':
      name=request.form['name']
      email=request.form['email']
      password=request.form['password']
      existing_user=Users.query.filter_by(email=email).first()
      if existing_user:
        flash('Email is already in use. Please choose a different email.', 'error')
        return redirect(url_for('register_form'))
      else:
        new_user=Users(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registeration success!', 'success')
        return render_template('registered.html', name=name, email=email)

  @app.route("/login_validation", methods=['POST'])
  def login_validation():
    name=request.form.get('name')
    email=request.form.get('email')
    password=request.form.get('password')
    row = db_login_validation(name, email, password)
    if row is not None:
      session['user_id']=row['user_id']
      return redirect('home')
    else:
      error_message="wrong user name, password or email"
      return render_template('login.html', error=error_message)
    
  
  
  @app.route("/home")
  def mark_careers():
    jobs_list = load_jobs_from_db()
    return render_template('home.html', jobs = jobs_list)
  
  @app.route("/api/jobs")
  def list_jobs():
    jobs_list = load_jobs_from_db()
    return jsonify(jobs=jobs_list)
  
  @app.route("/status_form")
  def status_form():
    return render_template('status_form.html')
  
  @app.route("/job_status", methods=['POST'])
  def status_check():
    full_name=request.form.get('full_name')
    email=request.form.get('email')
    row=status_validation(full_name, email)
    if row is not None:
      session['id']=row['id']                     
      return redirect(f'/status_results/{row["id"]}')
    else:
      error_message="wrong name or email"
      return render_template('status_form.html', error=error_message)
  
  @app.route("/status_results/<id>")
  def application_status(id):
    application=status_results(id)
    if application:
      job_id=application['job_id']
      job=load_job_from_db(job_id)
      if application['status']:
        return render_template('status_results.html', application=application, job=job)
      else:
        status_message="Your status has not yet been updated"
        return render_template('status_results.html', status=status_message)
    else:
      error_message="wrong name or email"
      return render_template('status_form.html', error=error_message)
  
  @app.route("/job/<job_id>")
  def show_job(job_id):
    job = load_job_from_db(job_id)
    if not job:
      return "Not found", 404
    return render_template('jobpage.html', job = job)
  
  @app.route("/job/<job_id>/apply", methods=['post'])
  def apply_to_job(job_id):
    data = request.form
    job = load_job_from_db(job_id)
    add_application_to_db(job_id, data)
    return render_template('application_submitted.html', application=data, job = job)
    
  return app

if __name__ == "__main__":
  app=create_app()
  app.run(host='0.0.0.0', debug=True)
