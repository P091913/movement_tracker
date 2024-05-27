from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
from flask_login import *
from flask_sqlalchemy import SQLAlchemy
from models import *
from val_creat import *

app = Flask(__name__)
app.secret_key = "dfdf23hh34"
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/movement'
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://movement_ulas_user:9Kh8ZtfvYtMzICBvWcpJRwlZhUSUkGMJ@dpg-cpa93dm3e1ms739m73fg-a.oregon-postgres.render.com/movement_ulas'
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
    if request.method == "POST":
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
    moves = Moves.query.all()
    user_moves = db.session.query(Moves.move_id, Moves.move_name, UserMoves.status). \
        join(Moves, UserMoves.move_id == Moves.move_id). \
        filter(UserMoves.user_id == current_user.id).all()
    return render_template("social.html", moves=moves,
                           user_moves=user_moves)


@app.route("/create", methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if len(check_empty_fields(username, password, email)) == 0:
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


@app.route('/update_progress', methods=['POST', 'GET'])
@login_required
def update_progress():
    trick_id = request.form['trick_id']
    percentage = 100

    user_move = UserMoves()
    user_move.user_id = current_user.id
    user_move.move_id = trick_id
    user_move.status = percentage
    db.session.add(user_move)
    db.session.commit()

    return redirect(url_for('social'))


@app.route('/update_exist', methods=['POST'])
@login_required
def update_exist():
    data = request.json
    skill = data.get('skill')
    percentage = data.get('percentage')
    id = data.get('move_id')

    user_move = UserMoves.query.filter_by(move_id=id, user_id=current_user.id).first()

    if user_move:
        user_move.status = percentage

        db.session.commit()

    return redirect(url_for('social'))


@app.route('/add_combo', methods=['POST'])
def add_combo():
    combo_title = request.form.get('combo-title')
    combo_description = request.form.get('combo-description')

    # Get all selected tricks from form data
    selected_tricks = []
    for key, value in request.form.items():
        if key.startswith('trick-') and value:  # Check if the key starts with 'trick-' and has a non-empty value
            selected_tricks.append(value)

    # Create a new Combo object
    new_combo = Combo(title=combo_title, description=combo_description)

    # Retrieve the Move objects corresponding to the selected move names
    selected_moves = Moves.query.filter(Moves.move_name.in_(selected_tricks)).all()

    # Add the selected moves to the new combo
    new_combo.moves.extend(selected_moves)

    # Set the user_id attribute of the new combo to the ID of the logged-in user
    new_combo.user_id = current_user.id

    # Add the new combo to the database session and commit
    db.session.add(new_combo)
    db.session.commit()

    return redirect(url_for('social'))


@app.route('/activity')
def activity():
    other_users_posts = Post.query.filter(Post.author != current_user).all()
    return render_template('activity.html', posts=other_users_posts)


@app.route('/create_post', methods=['POST'])
def create_post():
    if request.method == 'POST':
        post_content = request.form['postContent']
        if not post_content:
            flash('Post content cannot be empty', 'danger')
            return redirect(url_for('activity'))  # Redirect to your activity feed or the appropriate page

        new_post = Post(content=post_content, author=current_user)
        db.session.add(new_post)
        db.session.commit()

        flash('Post created successfully!', 'success')
        return redirect(url_for('activity'))  # Redirect to your activity feed or the appropriate page


@app.route('/add_friend', methods=['POST'])
@login_required
def add_friend():
    friend_username = request.form.get('friendUsername')
    friend = User.query.filter_by(username=friend_username).first()

    if friend and friend != current_user:
        if friend not in current_user.friends:
            current_user.friends.append(friend)
            db.session.commit()
            flash('Friend added successfully!', 'success')
        else:
            flash('This user is already your friend!', 'warning')
    else:
        flash('User not found or you cannot add yourself!', 'danger')

    return redirect(url_for('activity'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='192.168.86.23', port=5000, debug=True, threaded=False)
