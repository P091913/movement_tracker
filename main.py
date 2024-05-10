from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import *
from flask_sqlalchemy import SQLAlchemy
from models import *
from val_creat import *

app=Flask(__name__)
app.secret_key = "dfdf23hh34"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/movement'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method=="POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('social'))
        else:
            flash("Invalid Username and Password")
    return redirect(url_for("index"))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/social")
@login_required
# @relog_required
def social():
    return render_template("social.html")


@app.route("/create", methods=['POST', 'GET'])
def create():
    print(request.method)
    if request.method=="POST":
        print("in")
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if len(check_empty_fields(username, password, email)) == 0:
            print("in2")
            user = User()
            user.username = username
            user.password = password
            user.email = email
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            flash("Invalid Username and Password or email")
    return render_template("create.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

