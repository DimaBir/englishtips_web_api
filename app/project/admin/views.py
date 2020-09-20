from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, logout_user, login_user

from app.project import db
from database.models import ConfusedWord, User
from app.project.admin.forms import AddForm, LoginForm

confused_word_blueprints = Blueprint('admin', __name__, template_folder='templates/admin')


@confused_word_blueprints.route('/welcome')
@login_required
def welcome_user():
    return render_template('welcome_user.html')


@confused_word_blueprints.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You logged out!")
    return redirect(url_for('index'))


@confused_word_blueprints.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user.check_password(form.password.data) and user is not None:
            login_user(user)
            flash('Logged in successfully!')

            next = request.args.get('next')  # saves previous page user has attempted to login and
                                             # after login redirects there

            if next == None or not next[0]=='/':
                next = url_for('index')

            return redirect(next)
    return render_template('login.html', form=form)


# @confused_word_blueprints.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#
#     if form.validate_on_submit():
#         user = User(email=form.email.data, username=form.username.data, password=form.password.data)
#
#         db.session.add(user)
#         db.session.commit()
#         flash('Thanks for the registration')
#         return redirect(url_for('index'))
#     return render_template('register.html', form=form)


@confused_word_blueprints.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddForm()
    if form.validate_on_submit():
        word = form.word.data
        definition = form.definition.data

        # Add new confused word to database
        new_word = ConfusedWord(word, definition)
        db.session.add(new_word)
        db.session.commit()

        flash(f"'{word}' - has been added to the database", "success")
        return redirect(url_for('admin.list'))
    return render_template('add.html', form=form)


@confused_word_blueprints.route('/list')
@login_required
def list():
    confused_words = ConfusedWord.query.all()
    result = []
    for word in confused_words:
        result.append((word.word, word.note))
    return render_template('list.html', confused_words=result)


@confused_word_blueprints.route('/delete/<word_id>', methods=['GET', 'POST'])
@login_required
def delete(word_id):
    confused_word = ConfusedWord.query.get(word_id)

    local_object = db.session.merge(confused_word)
    db.session.delete(local_object)
    db.session.commit()
    flash(f"'{word_id}' - has been deleted from the database", "error")
    return redirect(url_for('admin.list'))
