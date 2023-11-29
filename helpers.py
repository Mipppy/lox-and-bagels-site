from flask import Flask, flash, redirect, render_template, request, session, g
from cs50 import SQL
from flask_session import Session

db = SQL("sqlite:///sql.db")

def get_products():
    products = db.execute("SELECT * FROM products")
    return products
