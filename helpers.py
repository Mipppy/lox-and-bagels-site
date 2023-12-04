from flask import Flask, flash, redirect, render_template, request, session, g
from cs50 import SQL
from flask_session import Session
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def usd(value):
    value = value/100
    return f"${value:,.2f}"