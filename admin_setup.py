from flask_admin import Admin
from models import Users, Jobs, Applications
from flask_admin.contrib.sqla import ModelView


def configure_admin(app, db):
  admin=Admin(app, name='Admin Panel', template_mode='Bootstrap3')
  admin.add_view(ModelView(Users, db.session))
  admin.add_view(ModelView(Jobs, db.session))
  admin.add_view(ModelView(Applications, db.session))
