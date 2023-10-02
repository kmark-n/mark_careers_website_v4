from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, Users, Jobs, Applications

admin=Admin()

admin.add_view(ModelView(Users, db.session))
admin.add_view(ModelView(Jobs, db.session))
admin.add_view(ModelView(Applications, db.session))