from models import User, GameResult, GameSession, Click, Prize, db

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import login_required, logout_user, LoginManager, login_user, current_user
from flask_bcrypt import Bcrypt

from datetime import datetime, timedelta

import secrets
secret_key = secrets.token_hex(16)


SQLALCHEMY_DATABASE_URI = 'sqlite:///couples_clicking_game.db'
SECRET_KEY = secret_key


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = SECRET_KEY
db.init_app(app)

migrate = Migrate(app, db)


login_manager = LoginManager(app)  # Initialize LoginManager
login_manager.login_view = 'login'  # Set the login view endpoint


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


bcrypt = Bcrypt(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=list(['GET', 'POST']))
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(
            password).decode('utf-8')

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


bcrypt = Bcrypt(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')


@app.route('/profile')
@login_required
def profile():
    user = current_user

    # Get the user's game history
    user_game_sessions = GameSession.query.filter(
        GameSession.clicks.any(user_id=current_user.id)
    ).order_by(GameSession.id.desc()).all()

    history = []

    for session in user_game_sessions:
        user_results = determine_winner(
            game_session=session, user_id=current_user.id)

        game_result = GameResult.query.filter_by(
            user_id=current_user.id, date=session.start_time.date()).first()

        if game_result:
            prizes = [prize.description for prize in game_result.prizes]
            satisfied_prizes = [
                {'description': prize.description, 'satisfied': prize.satisfied}
                for prize in game_result.prizes
            ]
        else:
            prizes = []
            satisfied_prizes = []

        history.append({
            'start_time': session.start_time,
            'end_time': session.end_time,
            'clicks': len(session.clicks),
            'user_results': user_results,
            'prizes': prizes,
            'satisfied_prizes': satisfied_prizes,
        })

    return render_template('home.html', user=user, history=history)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/start_game', methods=['POST'])
@login_required
def start_game():
    # Logic to start a new game session and set up initial values
    new_game_session = GameSession(
        start_time=datetime.now(), end_time=datetime.now() + timedelta(days=1))
    db.session.add(new_game_session)
    db.session.commit()
    flash('New game session started!', 'success')
    return redirect(url_for('game_interface'))


@app.route('/click_button', methods=['POST'])
@login_required
def click_button():
    # Logic to handle a user's button click
    current_game_session = GameSession.query.filter(
        GameSession.end_time >= datetime.now()
    ).first()
    if current_game_session:
        new_click = Click(
            user_id=current_user.id,
            game_session_id=current_game_session.id,
            timestamp=datetime.now()
        )
        db.session.add(new_click)
        db.session.commit()
        click_count = len(current_game_session.clicks)
        flash('Button clicked!', 'success')
        return {'success': True, 'clicks': click_count}
    return {'success': False}


# compare game results
def determine_winner(game_session, user_id):
    user_clicks = len(
        [click for click in game_session.clicks if click.user_id == user_id])
    significant_other_clicks = len(
        [click for click in game_session.clicks if click.user_id == current_user.significant_other_id])

    if user_clicks > significant_other_clicks:
        return 'Winner'
    elif user_clicks < significant_other_clicks:
        return 'Loser'
    else:
        return 'Tie'


@app.route('/game_results')
@login_required
def game_results():
    # Logic to display the results of the most recent game
    most_recent_game_session = GameSession.query.order_by(
        GameSession.id.desc()).first()

    if most_recent_game_session:
        user_results = determine_winner(
            game_session=most_recent_game_session, user_id=current_user.id)

        significant_other_id = current_user.significant_other_id
        significant_other_clicks = len(
            [click for click in most_recent_game_session.clicks if click.user_id == significant_other_id])

        results = {
            'start_time': most_recent_game_session.start_time,
            'end_time': most_recent_game_session.end_time,
            'clicks': len(most_recent_game_session.clicks),
            'significant_other_clicks': significant_other_clicks,
            'user_results': user_results,
            'game_result_id': most_recent_game_session.game_results[-1].id if most_recent_game_session.game_results else None,
        }
    else:
        results = None

    return render_template('game_results.html', results=results)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        search_username = request.form.get('username')
        user = User.query.filter_by(username=search_username).first()
        if user:
            current_user.significant_other_id = user.id
            db.session.commit()
            flash('Significant other added!', 'success')
        else:
            flash('User not found', 'error')
    return render_template('search.html')


@app.route('/available_prizes')
@login_required
def get_available_prizes():
    available_prizes = Prize.query.all()
    return render_template('available_prizes.html', available_prizes=available_prizes)


@app.route('/select_prize/<int:game_result_id>/<int:prize_id>', methods=['POST'])
@login_required
def select_prize(game_result_id, prize_id):
    game_result = GameResult.query.get(game_result_id)
    prize = Prize.query.get(prize_id)

    if game_result.user_id == current_user.id and game_result.won:
        game_result.prizes.append(prize)
        db.session.commit()
        flash('Prize selected!', 'success')
    else:
        flash('Invalid selection.', 'error')

    return redirect(url_for('game_results'))


if __name__ == '__main__':
    # Create the database tables
    with app.app_context():
        db.create_all()

    app.run(debug=True)
