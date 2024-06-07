from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
from flask_login import *
from flask_sqlalchemy import SQLAlchemy
from models import *
from val_creat import *
from email_validator import validate_email, EmailNotValidError
from jinja2 import Environment

app = Flask(__name__)
app.secret_key = "dfdf23hh34"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/movement'
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://movement_ulas_user:9Kh8ZtfvYtMzICBvWcpJRwlZhUSUkGMJ@dpg-cpa93dm3e1ms739m73fg-a.oregon-postgres.render.com/movement_ulas'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


# Define the slugify function
def slugify(value):
    return value.lower().replace(' ', '-')


# Register the slugify function as a custom Jinja2 filter
app.jinja_env.filters['slugify'] = slugify


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template("index.html", page='index')


@app.route('/training')
@login_required
def training():
    user = current_user
    session_details = user.user_session_details
    combos = user.combos
    moves = Moves.query.all()
    user_moves = db.session.query(Moves.move_id, Moves.move_name, UserMoves.status). \
        join(Moves, UserMoves.move_id == Moves.move_id). \
        filter(UserMoves.user_id == current_user.id).all()

    # Fetch all previous session details for the current user, ordered by date
    previous_sessions = db.session.query(SessionDetails). \
        filter_by(user_id=current_user.id). \
        order_by(SessionDetails.date.desc()).all()

    # Group sessions by date
    from collections import defaultdict
    sessions_by_date = defaultdict(list)
    for session in previous_sessions:
        sessions_by_date[session.date.date()].append(session)

    combos_by_date = defaultdict(list)
    for combo in combos:
        for combo_progress in combo.combo_progress_details:
            # Query the Combo table to get the combo name based on the combo_id
            combo_name = db.session.query(Combo.title).filter(Combo.id == combo_progress.combo_id).scalar()
            # Add the combo name to the ComboProgress object
            combo_progress.combo_name = combo_name
            # Append the ComboProgress object to the list corresponding to the date
            combos_by_date[combo_progress.date.date()].append(combo_progress)

    combined_dates = set(sessions_by_date.keys()).union(set(combos_by_date.keys()))

    custom_moves = CustomTrick.query.filter(CustomTrick.user_id == current_user.id).all()

    #print(custom_moves)
    #print(combined_dates)

    return render_template("training.html", moves=moves, user_moves=user_moves,
                           sessions_by_date=sessions_by_date, combos_by_date=combos_by_date,
                           custom_moves=custom_moves, combined_dates=combined_dates
                           )


@app.route('/get_combo_details')
@login_required
def get_combo_details():
    combo_id = request.args.get('combo_id')
    combo = Combo.query.get(combo_id)
    if combo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    combo_details = {
        'id': combo.id,
        'title': combo.title,
        'description': combo.description,
        'tricks': [{'id': trick.trick_id, 'name': trick.trick_name} for trick in combo.combo_tricks]
        # Adjust this to match your data structure
    }
    return jsonify(combo_details)


@app.route('/save_combo_edit', methods=['POST'])
@login_required
def update_combo():
    combo_id = request.form.get('combo_id')
    title = request.form.get('combo-title')
    description = request.form.get('combo-description')
    tricks = request.form.getlist('tricks[]')

    combo = Combo.query.get(combo_id)
    if combo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    combo.title = title
    combo.description = description
    # Handle updating tricks here

    db.session.commit()
    return jsonify({'success': True})


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('training'))
        else:
            flash("Invalid Username and Password")
    return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/add_custom_trick', methods=['POST'])
def add_custom_trick():
    data = request.json
    trick_name = data.get('trickName')

    existing_trick = CustomTrick.query.filter_by(user_id=current_user.id, trick_name=trick_name).first()
    if existing_trick:
        return jsonify({'error': 'Trick already exists for this user'})
    else:
        # Create and store the custom trick in the database
        custom_trick = CustomTrick(trick_name=trick_name, user_id=current_user.id)
        # combo_trick = ComboTricks(combo_id=combo_id, trick_id=trick_id, trick_type=trick_type, position=position)
        db.session.add(custom_trick)
        db.session.commit()
        return jsonify({'message': 'Custom trick added successfully'})


@app.route('/fetch_custom_tricks')
def fetch_custom_tricks():
    # Fetch custom tricks for the current user
    custom_tricks = CustomTrick.query.filter_by(user_id=current_user.id).all()

    # Serialize custom tricks to JSON format
    custom_tricks_json = [{
        'id': trick.id,
        'name': trick.trick_name
    } for trick in custom_tricks]

    return jsonify(custom_tricks_json)


@app.route('/fetch_official_tricks')
def fetch_official_tricks():
    # Fetch all official tricks from the Moves table
    official_tricks = Moves.query.all()

    # Serialize the official tricks to JSON format
    serialized_tricks = [{'id': trick.move_id, 'name': trick.move_name} for trick in official_tricks]

    # Return the serialized tricks as JSON response
    return jsonify(serialized_tricks)


@app.route('/add_progress_entry', methods=['POST'])
@login_required
def add_progress_entry():
    data = request.json
    # Here, you can access the form data using the keys of the JSON object
    date = data.get('date')
    trick = data.get('trick')
    trick_id = data.get('trick_id')
    attempts = data.get('attempts')
    successes = data.get('successes')
    notes = data.get('notes')
    #print(data)

    new_entry = SessionDetails(date=date, trick_name=trick, attempts=attempts,
                               successful_landings=successes, notes=notes, user_id=current_user.id,
                               move_id=trick_id)
    db.session.add(new_entry)
    db.session.commit()

    # Redirect to the appropriate page after adding the entry
    return jsonify(success=True, redirect_url=url_for('training'))


@app.route('/add_combo_progress', methods=['POST'])
@login_required
def add_combo_progress():
    data = request.json
    date = data.get('date')
    combo_id = data.get('combo')
    attempts = data.get('attempts')
    successes = data.get('successes')
    notes = data.get('notes')

    new_combo_progress = ComboProgress(date=date, combo_id=combo_id, attempts=attempts,
                                       successes=successes, notes=notes, user_id=current_user.id)
    db.session.add(new_combo_progress)
    db.session.commit()

    return jsonify({'success': True})


@app.route("/create", methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        try:
            # Check that the email address is valid. Turn on check_deliverability
            # for first-time validations like on account creation pages (but not
            # login pages).
            emailinfo = validate_email(email, check_deliverability=False)

            # After this point, use only the normalized form of the email address,
            # especially before going to a database query.
            email = emailinfo.normalized

            if len(check_empty_fields(username, password, email)) == 0:
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    flash("Email address already exists. Please use a different email.")
                else:
                    existing_username = User.query.filter_by(username=username).first()
                    if existing_username:
                        flash("Username already exists.")
                    else:
                        # Create a new user if the email doesn't exist
                        user = User()
                        user.username = username
                        user.password = password
                        user.email = email
                        db.session.add(user)
                        db.session.commit()
                        return redirect(url_for('login'))
            else:
                flash("Invalid Username and Password or email")
        except EmailNotValidError as e:
            # The exception message is human-readable explanation of why it's
            # not a valid (or deliverable) email address.
            flash("You Must use a valid email address")
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

    return redirect(url_for('training'))


@app.route('/update_exist', methods=['POST'])
@login_required
def update_exist():
    data = request.json
    skill = data.get('skill')
    percentage = data.get('percentage')
    id = data.get('move_id')

    try:
        user_move = UserMoves.query.filter_by(move_id=id, user_id=current_user.id).first()

        if user_move:
            user_move.status = percentage

            db.session.commit()
    except Exception:
        flash('Percentage needs a number', 'error')
        return redirect(url_for('training'))  # Adjust the redirect to your appropriate view function

    return redirect(url_for('training'))


@app.route('/add_combo', methods=['POST'])
@login_required
def add_combo():
    combo_title = request.form.get('combo-title')
    combo_description = request.form.get('combo-description')

    # Create a new Combo object
    new_combo = Combo(title=combo_title, description=combo_description, user_id=current_user.id)

    # Add the new combo to the database session and commit to get the combo ID
    db.session.add(new_combo)
    db.session.commit()

    return jsonify({'combo_id': new_combo.id})


@app.route('/add_combo_tricks', methods=['POST'])
@login_required
def add_combo_tricks():
    combo_id = request.form.get('combo_id')

    # Get all selected tricks from form data
    selected_tricks = request.form.getlist('tricks[]')

    # Add the selected tricks to the ComboTricks table in the order they were selected
    for position, trick in enumerate(selected_tricks, start=1):
        trick_parts = trick.split('-')
        if len(trick_parts) != 2:
            #print("Error: Trick does not contain expected format:", trick)
            continue
        trick_type, trick_id = trick_parts
        #print("Trick Type:", trick_type)
        #print("Trick ID:", trick_id)
        trick_id = int(trick_id)

        # Create a new ComboTricks object
        combo_trick = ComboTricks(combo_id=combo_id, trick_id=trick_id, trick_type=trick_type, position=position)

        # Add the combo trick to the database session
        db.session.add(combo_trick)

    # Commit all changes to the database
    db.session.commit()

    return redirect(url_for('training'))


@app.route('/custom_add_combo', methods=['POST'])
def custom_add_combo():
    combo_id = request.form.get('combo-id')
    combo_title = request.form['combo-title']
    combo_description = request.form['combo-description']
    selected_tricks = request.form.getlist('tricks[]')
    #print(combo_title, combo_description, selected_tricks)

    # Create a new Combo object
    new_combo = Combo(title=combo_title, description=combo_description, user_id=current_user.id)

    # Add the new combo to the database session and commit to get the combo ID
    db.session.add(new_combo)
    db.session.commit()

    for position, trick in enumerate(selected_tricks, start=1):
        trick_parts = trick.split('-')
        if len(trick_parts) != 2:
            #print("Error: Trick does not contain expected format:", trick)
            continue
        trick_type, trick_id = trick_parts
        #print("Trick Type:", trick_type)
        #print("Trick ID:", trick_id)
        trick_id = int(trick_id)

        # Create a new ComboTricks object
        if trick_type == 'custom':
            combo_trick = ComboTricks(combo_id=new_combo.id, trick_id=trick_id, trick_type=trick_type,
                                      position=position,
                                      custom_trick_id=trick_id)
        else:
            combo_trick = ComboTricks(combo_id=new_combo.id, trick_id=trick_id, trick_type=trick_type,
                                      position=position,
                                      move_id=trick_id)

        # Add the combo trick to the database session
        db.session.add(combo_trick)

    # Commit all changes to the database
    db.session.commit()

    return redirect(url_for('training'))

    # return "Success"  # You can return a response as needed



@app.route('/custom_edit_combo', methods=['POST'])
def custom_edit_combo():
    combo_id = request.form['combo-id']
    combo_title = request.form['combo-title']
    combo_description = request.form['combo-description']
    selected_tricks = request.form.getlist('tricks[]')
    #print(combo_title, combo_description, selected_tricks)
    #print(f'combo_id: {combo_id}')

    existing_combo = Combo.query.get(combo_id)

    if existing_combo:
        existing_combo.title = combo_title
        existing_combo.description = combo_description

        ComboTricks.query.filter_by(combo_id=combo_id).delete()

        for position, trick in enumerate(selected_tricks, start=1):
            trick_parts = trick.split('-')
            if len(trick_parts) != 2:
                #print("Error: Trick does not contain expected format:", trick)
                continue
            trick_type, trick_id = trick_parts
            #print("Trick Type:", trick_type)
            #print("Trick ID:", trick_id)
            trick_id = int(trick_id)

            # Create a new ComboTricks object
            if trick_type == 'custom':
                combo_trick = ComboTricks(combo_id=existing_combo.id, trick_id=trick_id, trick_type=trick_type,
                                          position=position,
                                          custom_trick_id=trick_id)
            else:
                combo_trick = ComboTricks(combo_id=existing_combo.id, trick_id=trick_id, trick_type=trick_type,
                                          position=position,
                                          move_id=trick_id)

            # Add the combo trick to the database session
            db.session.add(combo_trick)

        # Commit all changes to the database
        db.session.commit()

        return redirect(url_for('training'))


@app.route('/remove_combo', methods=['POST'])
@login_required
def remove_combo():
    combo_id = request.form.get('combo_id')

    # Retrieve the combo from the database
    combo = Combo.query.get(combo_id)

    if not combo:
        flash('Combo not found!', 'error')
        return redirect(url_for('training'))  # Adjust the redirect to your appropriate view function

    # Check if the current user is allowed to delete this combo
    if combo.user_id != current_user.id:
        flash('You do not have permission to delete this combo.', 'error')
        return redirect(url_for('training'))  # Adjust the redirect to your appropriate view function

    # Manually delete related records in combo_tricks
    ComboTricks.query.filter_by(combo_id=combo_id).delete()
    # Manually delete related records in combo_moves and combo_custom_tricks if necessary
    db.session.execute(combo_moves.delete().where(combo_moves.c.combo_id == combo_id))
    db.session.execute(combo_custom_tricks.delete().where(combo_custom_tricks.c.combo_id == combo_id))

    # Delete related combo progress records
    ComboProgress.query.filter_by(combo_id=combo_id).delete()

    # Delete the combo from the database
    db.session.delete(combo)
    db.session.commit()

    flash('Combo removed successfully!', 'success')
    return redirect(url_for('training'))  # Adjust the redirect to your appropriate view function


@app.route('/add_skill', methods=['POST'])
@login_required
def add_skill():
    skill_name = request.form.get('new_skill')

    if not skill_name:
        flash('No skill selected!', 'error')
        return redirect(url_for('training'))  # Adjust the redirect to your appropriate view function

    # Find the move in the database
    move = Moves.query.filter_by(move_name=skill_name).with_entities(Moves.move_id).first()

    # Check if the skill already exists in the user's skills
    #print(current_user.id)
    #print(move)
    existing_skill = UserMoves.query.filter_by(user_id=current_user.id, move_id=move[0]).first()
    if existing_skill:
        flash('You already have this skill!', 'error')
        return redirect(url_for('training'))  # Adjust the redirect to your appropriate view function

    # Add the skill to the user's acquired skills
    new_user_move = UserMoves(user_id=current_user.id, move_id=move[0], status=0)
    db.session.add(new_user_move)
    db.session.commit()

    flash('Skill added successfully!', 'success')
    return redirect(url_for('training'))  # Adjust the redirect to your appropriate view function


@app.route('/remove_skill', methods=['POST'])
@login_required
def remove_skill():
    move_id = request.form.get('move_id')

    # Retrieve the user's skill entry from the database
    user_skill = UserMoves.query.filter_by(move_id=move_id, user_id=current_user.id).first()

    if not user_skill:
        flash('Skill not found!', 'error')
        return redirect(url_for('training'))  # Adjust the redirect to your appropriate view function

    try:
        # Delete the skill from the userMoves table
        db.session.delete(user_skill)
        db.session.commit()

        flash('Skill removed successfully!', 'success')
    except Exception as e:
        flash('An error occurred while removing the skill.', 'error')
        db.session.rollback()
        #print(str(e))  # Print the error for debugging purposes

    return redirect(url_for('training'))  # Adjust the redirect to your appropriate view function


@app.route('/activity')
@login_required
def activity():
    other_users_posts = Post.query.filter(Post.author != current_user).all()
    return render_template('activity.html', posts=other_users_posts)


@app.route('/create_post', methods=['POST'])
@login_required
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


def create_app():
    with app.app_context():
        db.create_all()
    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
