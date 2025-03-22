from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Event
from forms import LoginForm, EventForm
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_pyfile('config.py')

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('view_events'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def view_events():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
            time=form.time.data,
            location=form.location.data,
            due_date=form.due_date.data
        )
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('view_events'))
    
    events = Event.query.order_by(Event.order).all()
    today = datetime.now().date()
    return render_template('events.html', form=form, events=events, today=today)

@app.route('/edit_event/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = Event.query.get_or_404(id)
    form = EventForm()
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.date = form.date.data
        event.time = form.time.data
        event.location = form.location.data
        event.due_date = form.due_date.data
        db.session.commit()
        return redirect(url_for('view_events'))
    elif request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
        form.date.data = event.date
        form.time.data = event.time
        form.location.data = event.location
        form.due_date.data = event.due_date
    return render_template('edit_event.html', form=form, event=event)

@app.route('/delete_event/<int:id>')
@login_required
def delete_event(id):
    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('view_events'))

@app.route('/update_order', methods=['POST'])
@login_required
def update_order():
    data = request.get_json()
    event = Event.query.get(data['id'])
    if event:
        event.order = data['order']
        db.session.commit()
    return '', 204

@app.route('/sort_by_due_date')
@login_required
def sort_by_due_date():
    events = Event.query.order_by(Event.due_date).all()
    form = EventForm()
    today = datetime.now().date()
    return render_template('events.html', form=form, events=events, today=today)

@app.route('/filter_overdue')
@login_required
def filter_overdue():
    today = datetime.now().date()
    events = Event.query.filter(Event.due_date < today).all()
    form = EventForm()
    return render_template('events.html', form=form, events=events, today=today)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)