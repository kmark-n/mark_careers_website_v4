from flask import Flask, render_template, jsonify, request, redirect, session, url_for, flash
from database import load_jobs_from_db, load_job_from_db, add_application_to_db, status_validation, status_results
import os
import pymysql
from models import db, Users, Jobs, Applications, bcrypt
from admin_setup import admin
from middleware import auth, guest
from itsdangerous.serializer import Serializer
from flask_mail import Message, Mail
from werkzeug.utils import secure_filename
import secrets as secrets

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
  app.config['UPLOAD_FOLDER']='static/profile_pic'

  app.config['MAIL_SERVER'] = 'smtp.gmail.com'
  app.config['MAIL_PORT'] = 465
  app.config['MAIL_USE_SSL'] = True
  app.config['MAIL_USERNAME'] = 'markcareerswebsite@gmail.com'
  app.config['MAIL_PASSWORD'] = 'beoc lmja mqpf qezv'

  
  mail=Mail(app)

  db.init_app(app)

  with app.app_context():
    db.create_all() 

  admin.init_app(app)
  

   
  @app.route('/')
  @guest
  def login():
    return render_template('login.html')
  
  @app.route('/register_form')
  @guest
  def register_form():
    return render_template('register_form.html')
  
  
  @app.route("/register_form/registered", methods=['POST', 'GET'])
  def register_complete():
    if request.method == 'POST':
      name=request.form['name']
      email=request.form['email']
      password=request.form['password']
      profile_pic=request.files['profile_pic']
      if profile_pic:
        filename=secure_filename(profile_pic.filename)
        random_hex=secrets.token_hex(8)
        pic_name=random_hex + filename
        profile_pic.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], pic_name))
        profile_pic=pic_name
      else:
        profile_pic='default.jpeg'
      existing_user=Users.query.filter_by(email=email).first()
      if existing_user:
        flash('Email is already in use. Please choose a different email.', 'error')
        return redirect(url_for('register_form'))
      else:
        new_user=Users(name=name, email=email, password=password, profile_pic=profile_pic)
        db.session.add(new_user)
        db.session.commit()
        flash('Registeration success!', 'success')
        return render_template('registered.html', name=name, email=email)

  @app.route("/login_validation", methods=['POST'])
  def login_validation():
    if request.method == 'POST':
      name=request.form['name']
      email=request.form['email']
      password=request.form['password']
      user=Users.query.filter_by(name=name, email=email).first()
      if user and user.check_password(password):
        session['user_id']=user.user_id
        return redirect(url_for('mark_careers'))
      else:
        error_message="Invalid user"
        return render_template('login.html', error=error_message)
      
  @app.route('/pwd_reset_req', methods=['GET', 'POST'])
  def pwd_reset_request():
    if request.method == 'POST':
      email=request.form['email']
      user=Users.query.filter_by(email=email).first()
      if user:
        send_mail(user)
        flash('Your password reset request has been received. Check your mail.', 'success')
      else:
        flash('Unrecognized email.', 'error')
    return render_template('pwd_reset_request.html')
  
  def send_mail(user):
    token=gen_token(user.user_id, user.email)
    msg=Message('Password reset request', recipients=[user.email], sender='noreply@kmark.com')
    msg.body=f"If you sent a password reset request, please follow the link:{url_for('pwd_reset', token=token,  _external=True)} If you didn\'t send a password reset request please ignore this message."
    mail.send(msg)
  

  def gen_token(user_id, email):
    serial=Serializer(app.config['SECRET_KEY'])
    return serial.dumps({'user_id':user_id, 'email':email})
  
  @staticmethod
  def verify_token(token):
    serial=Serializer(app.config['SECRET_KEY'])
    try:
      data=serial.loads(token)
      user_id=data['user_id']
      email=data['email']
    except:
      return None
    return Users.query.filter_by(user_id=user_id, email=email).first()
  
  @app.route('/reset_password/<token>', methods=['POST', 'GET'])
  def pwd_reset(token):
    user=verify_token(token)
    if user is None:
      flash('The token is invalid')
      return redirect(url_for('pwd_reset_request'))
    if user:
        if request.method == 'POST':
          new_password=request.form['new_password']
          confirm_password=request.form['confirm_password']
          if new_password != confirm_password:
            flash('The passwords do not match. Please try again', 'error')
          else:
            hashed_password=bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user.password=hashed_password
            db.session.commit()
            flash('Password changed successfully.', 'success')
    return render_template('change_password.html', token=token)

  @app.route('/logout')
  @auth
  def logout():
    session.pop('user_id', None)
    return redirect('/')
  
  @app.route("/home")
  @auth
  def mark_careers():
      user=Users.query.get(session['user_id'])
      name=user.name
      profile_pic=url_for('static', filename='profile_pic/' + user.profile_pic)
      jobs_list = load_jobs_from_db()
      return render_template('home.html', jobs = jobs_list, user=user, profile_pic=profile_pic, name=name)
  
  @app.route("/profile_update", methods=['POST', 'GET'])
  def update_profile():
    user=Users.query.get(session['user_id'])
    if user:
      if request.method == 'POST':
        new_name=request.form['new_name']
        new_profile_pic=request.files['new_profile_pic']
        if new_name:
          user.name=new_name
        if new_profile_pic:
          filename=secure_filename(new_profile_pic.filename)
          random_hex=secrets.token_hex(8)
          new_pic=random_hex + filename
          new_profile_pic.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], new_pic))
          user.profile_pic=new_pic
        if new_name or new_profile_pic:
          db.session.commit()
          flash('Account  updated successfully.', 'success')
    return render_template('profile_update.html')
  
  @app.route("/api/jobs")
  def list_jobs():
    jobs_list = load_jobs_from_db()
    return jsonify(jobs=jobs_list)
  
  @app.route("/status_form")
  def status_form():
    user=Users.query.get(session['user_id'])
    profile_pic=url_for('static', filename='profile_pic/' + user.profile_pic)
    return render_template('status_form.html', profile_pic=profile_pic)
  
  @app.route("/job_status", methods=['POST'])
  def status_check():
    firstname=request.form.get('firstname')
    lastname=request.form.get('lastname')
    email=request.form.get('email')
    row=status_validation(firstname, lastname, email)
    if row is not None:
      session['id']=row['id']                     
      return redirect(f'/status_results/{row["id"]}')
    else:
      error_message="wrong name or email"
      return render_template('status_form.html', error=error_message)
  
  @app.route("/status_results/<id>")
  def application_status(id):
    user=Users.query.get(session['user_id'])
    profile_pic=url_for('static', filename='profile_pic/' + user.profile_pic)
    application=status_results(id)
    if application:
      job_id=application['job_id']
      job=load_job_from_db(job_id)
      if application['status']:
        return render_template('status_results.html', application=application, job=job, profile_pic=profile_pic)
      else:
        status_message="Your status has not yet been updated"
        return render_template('status_results.html', status=status_message, profile_pic=profile_pic)
    else:
      error_message="wrong name or email"
      return render_template('status_form.html', error=error_message)
  
  @app.route("/job/<job_id>")
  def show_job(job_id):
    user=Users.query.get(session['user_id'])
    profile_pic=url_for('static', filename='profile_pic/' + user.profile_pic)
    job = load_job_from_db(job_id)
    if not job:
      return "Not found", 404
    return render_template('jobpage.html', job = job, profile_pic=profile_pic)
  
  @app.route("/job/<job_id>/apply", methods=['post'])
  def apply_to_job(job_id):
    user=Users.query.get(session['user_id'])
    profile_pic=url_for('static', filename='profile_pic/' + user.profile_pic)
    data = request.form
    job = load_job_from_db(job_id)
    add_application_to_db(job_id, data)
    return render_template('application_submitted.html', application=data, job=job, profile_pic=profile_pic)
    
  return app

if __name__ == "__main__":
  app=create_app()
  app.run(host='0.0.0.0', debug=True)
