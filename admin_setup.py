from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, Users, Jobs, Applications
from flask import abort, session



admin=Admin()

class SecureModelView(ModelView):
    def is_accessible(self):
        if 'user_id' in session: 
            user=Users.query.get(session['user_id'])
            if user and user.is_admin:
                return True
            else:
                return abort(404)
        else:
            return abort(404)
            

admin.add_view(SecureModelView(Users, db.session))
admin.add_view(SecureModelView(Jobs, db.session))
admin.add_view(SecureModelView(Applications, db.session))