from sqlalchemy import create_engine, text
import os

database_connection_string = os.environ['DB_CONNECTION_STRING']
engine = create_engine(database_connection_string,
          connect_args = {
            "ssl": {
              "ssl_ca": "/etc/ssl/cert.pem"
            }
          }
                      )

def load_jobs_from_db():
  with engine.connect() as conn:
    result = conn.execute(text("select * from jobs"))
    column_names = result.keys()
    jobs_list = [dict(zip(column_names, row)) for row in result.fetchall()]
    return jobs_list

def load_job_from_db(job_id):
    with engine.connect() as conn:
        query = text("SELECT * FROM jobs WHERE job_id = :val")
        result = conn.execute(query, {"val": job_id})
        row = result.fetchone()

    if row is None:
        return None
    else:
        column_names = result.keys()
        return dict(zip(column_names, row))

def add_application_to_db(job_id, data):
  with engine.connect() as conn:
    query=text("INSERT INTO applications(job_id, full_name, email, linkedin_url, education, work_experience, resume_url) VALUES (:job_id, :full_name, :email, :linkedin_url, :education, :work_experience, :resume_url)")
    conn.execute (query, {"job_id":job_id, "full_name":data['full_name'], "email":data['email'], "linkedin_url":data['linkedin_url'], "education":data['education'], "work_experience":data['work_experience'], "resume_url":data['resume_url']})

def add_user_details_to_db(data):
  with engine.connect() as conn:
    query=text("INSERT INTO users(name, email, password) VALUES (:name, :email, :password)")
    conn.execute (query, {"name":data['name'], "email":data["email"], "password":data["password"]})


def db_login_validation(name, email, password):
  with engine.connect() as conn:
    query=text("SELECT * FROM users WHERE name = :name AND email= :email AND password= :password")
    result=conn.execute(query, {"name":name, "email":email, "password":password})
    row=result.fetchone()
    if row is None:
      return None
    else:
      column_name=result.keys()
      return dict(zip(column_name, row))

def status_validation(full_name, email):
  with engine.connect() as conn:
    query=text("SELECT * FROM applications WHERE full_name= :full_name AND email= :email")
    result=conn.execute(query, {"full_name":full_name, "email":email})
    row=result.fetchone()
    if row is None:
      return None
    else:
      column_name=result.keys()
      return dict(zip(column_name, row))
      
def status_results(id):
  with engine.connect() as conn:
    query=text("SELECT * FROM applications WHERE id= :val")
    results=conn.execute(query, {"val":id})
    row=results.fetchone()
    if row is None:
      return None
    else:
      column_name=results.keys()
      return dict(zip(column_name, row))
