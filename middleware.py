from flask import session, redirect, url_for
import functools as ft

def auth(view_func):
    @ft.wraps(view_func)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/')
        return view_func(*args, **kwargs)
    return decorated

def guest(view_func):
    @ft.wraps(view_func)
    def decorated(*args, **kwargs):
        if 'user_id' in session:
            return redirect('/home')
        return view_func(*args, **kwargs)
    return decorated
