from flask import Blueprint, render_template, redirect, url_for, flash
from project import db
from database.models import ConfusedWord
from project.admin.forms import AddForm, DelForm

confused_word_blueprints = Blueprint('admin', __name__, template_folder='templates/admin')


@confused_word_blueprints.route('/add', methods=['GET', 'POST'])
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
def list():
    confused_words = ConfusedWord.query.all()
    result = []
    for word in confused_words:
        result.append((word.word, word.note))
    return render_template('list.html', confused_words=result)


@confused_word_blueprints.route('/delete/<word_id>', methods=['GET', 'POST'])
def delete(word_id):
    confused_word = ConfusedWord.query.get(word_id)

    local_object = db.session.merge(confused_word)
    db.session.delete(local_object)
    db.session.commit()
    flash(f"'{word_id}' - has been deleted from the database", "error")
    return redirect(url_for('admin.list'))
