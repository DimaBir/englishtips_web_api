import os
import json
import logging
import traceback

from logging.handlers import RotatingFileHandler
from nltk.corpus import wordnet
from timeit import default_timer as timer

from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from sqlalchemy_utils import database_exists

from NLP import predict_class, init
from app.forms import PredictForm
from database.setupdatabase import fill_database
from logic.coloring.acronyms import find_acronyms
from logic.analytics.asl import avg_sentence_len
from logic.tips.confused_word import get_confused_word
from database.models import db, login_manager
from logic.tips.get_sentence_structure import get_sentence_structure
from logic.coloring.hypernyms import find_hypernyms
from logic.coloring.hyponyms import find_hyponyms
from logic.summarizer import text_summarization
from logic.coloring.synonym import find_synonyms
from logic.coloring.uncountable_nouns import find_uncountable_nouns
from logic.tips.useful_phrases import get_useful_phrase
from logic.coloring.wordiness import find_wordiness
from logic.analytics.toptenwords import find_top_ten_words
from logic.coloring.verbs import find_verbs, find_verbs_per_char
from logic.coloring.nouns import find_noun_compound
from logic.google_translate import google_translate
from flask import Flask, render_template, request, url_for, flash, redirect, send_file, jsonify
from flask_login import login_required

BASEDIR = os.path.abspath(os.path.dirname(__file__))
SERVER_PATH = os.path.join(BASEDIR, 'db.sqlite')
UPLOAD_FOLDER = r'C:/englishtips/englishtips_web_api/version/'
ALLOWED_EXTENSIONS = {'txt', 'zip'}

app = Flask(__name__, template_folder='templates')

# Initialize the log handler
logHandler = RotatingFileHandler(os.path.join(BASEDIR, 'siteLog.log'), maxBytes=1000000, backupCount=5, encoding='utf8')
logHandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
# Set the log handler level
logHandler.setLevel(logging.INFO)
# Set the app logger level
app.logger.setLevel(logging.INFO)
app.logger.addHandler(logHandler)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
MAX_UPLOAD_SIZE_MB = 2.5
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE_MB * 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + SERVER_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ba86103dafb9ec379d26c7bd92206424'
app.config['MODEL'] = None
app.config['DEVICE'] = None

# Recaptcha Config Section
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LcGrAQaAAAAANJDop7yTR9u8zsMe6A6PGM7TJex'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LcGrAQaAAAAAMkUUvOv8aUanK-3paIgYX1JYg7h'
app.config['RECAPTCHA_DATA_ATTRS'] = {'theme': 'light'}

db.init_app(app)
app.config['MODEL'], app.config['DEVICE'] = init()

Migrate(app, db)

login_manager.init_app(app)
login_manager.login_view = 'login'

from app.project.admin.views import confused_word_blueprints
app.register_blueprint(confused_word_blueprints, url_prefix='/admin')


if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
    try:
        with app.app_context():
            db.create_all()
            fill_database()
    except Exception as e:
        app.logger.error('{}\n{}'.format(e, traceback.format_exc()))


####################################### VIEWS ###############################################


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='EnglishTips')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(413)
def request_entity_too_large(error):
    return 'File Too Large', 413


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'warning')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('File must be ZIP.', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            flash(f'{file.filename} uploaded successfully', 'success')
            return redirect(url_for('upload_file'))

    return render_template('upload.html')


@app.route('/download', methods=['GET'])
def download_file():
    # TODO: Change to relative
    f = open('../version.txt', 'r')
    version = (f.read())
    f.close()
    name = f"EnglishTips_v.{version}.zip"
    response = send_file(os.path.join(UPLOAD_FOLDER, "publish.zip"), as_attachment=True, mimetype="application/zip",
                         attachment_filename=name, cache_timeout=0)
    response.headers["x-filename"] = name
    response.headers['Cache-Control'] = 'no-cache, no-store'
    response.headers['Pragma'] = 'no-cache'
    response.headers["Access-Control-Expose-Headers"] = 'x-filename'
    return response


@app.route('/api/verbs', methods=['POST'])
def verbs():
    try:
        content = request.get_json()
        print(content)
        result_dic = find_verbs(content['text'])

        return json.dumps(result_dic)

    except Exception as e:
        return str("Error: " + str(e))


@app.route('/api/verbs2', methods=['POST'])
def verbs2():
    try:
        start = timer()
        content = request.get_json()
        print(content)
        result_dic = find_verbs_per_char(content['text'])
        print(timer() - start)

        return json.dumps(result_dic)

    except Exception as e:
        app.logger.error('In verbs2, error is: {}\n{}'.format(e, traceback.format_exc()))
        return jsonify(result="failed")


@app.route('/api/noun-compound', methods=['POST'])
def noun_compound():
    try:
        start = timer()
        content = request.get_json()
        print(content)
        result = find_noun_compound(content['text'])

        result = {
            "result": result,
            "ServerExecutionTime": timer() - start
        }
        return json.dumps(result)
    except Exception as e:
        app.logger.error('In noun_compound, error is: {}\n{}'.format(e, traceback.format_exc()))
        return jsonify(result="failed")


@app.route('/api/uncountable', methods=['POST'])
def uncountable():
    try:
        content = request.get_json()
        print(content)
        result = find_uncountable_nouns(content['text'])
        return json.dumps(result)
    except Exception as e:
        app.logger.error('In uncountable, error is: {}\n{}'.format(e, traceback.format_exc()))
        return jsonify(result="failed")


@app.route('/api/wordiness', methods=['POST'])
def wordiness():
    try:
        start = timer()
        content = request.get_json()
        print(content)
        result = find_wordiness(content['text'])

        result = {
            "Result": result,
            "ServerExecutionTime": timer() - start
        }
        return json.dumps(result)
    except Exception as e:
        app.logger.error('In wordiness, error is: {}\n{}'.format(e, traceback.format_exc()))
        return jsonify(result="failed")


@app.route('/api/topwords', methods=['POST'])
def top_words():
    try:
        start = timer()
        content = request.get_json()
        print(content)
        result = find_top_ten_words(content['text'])

        result = {
            "Result": result,
            "ServerExecutionTime": timer() - start
        }
        return json.dumps(result)
    except Exception as e:
        app.logger.error('In top_words, error is: {}\n{}'.format(e, traceback.format_exc()))
        return jsonify(result="failed")


@app.route('/api/syn', methods=['POST'])
def synonym():
    try:
        start = timer()
        content = request.get_json()
        if len(content['word'].split()) != 1:
            return json.dumps({
                "result": None,
                "ServerExecutionTime": timer() - start,
                "Error": "Error: Please, choose one word and try again."
            })
        content['word'] = content['word'].strip()
        print(content)
        synonyms, antonyms = find_synonyms(content['word'])

        result = {
            "result": synonyms,
            "ServerExecutionTime": timer() - start,
            "Error": None
        }

        return json.dumps(result)
    except Exception as e:
        app.logger.error('In synonym, error is: {}\n{}'.format(e, traceback.format_exc()))
        return jsonify(result="failed")


@app.route('/api/acr', methods=['POST'])
def acronyms():
    try:
        start = timer()
        content = request.get_json()
        if len(content['word'].split()) != 1:
            return json.dumps({
                "result": None,
                "ServerExecutionTime": timer() - start,
                "Error": "Error: Please, choose one word and try again."
            })
        content['word'] = content['word'].strip()
        print(content)
        acronym_result, definition = find_acronyms(content['word'])

        result = {
            "result": acronym_result,
            "definition": definition,
            "ServerExecutionTime": timer() - start,
            "Error": None
        }

        return json.dumps(result)
    except Exception as e:
        app.logger.error('In acronyms, error is: {}\n{}'.format(e, traceback.format_exc()))
        return jsonify(result="failed")


@app.route('/api/hyper', methods=['POST'])
def hypernyms():
    try:
        start = timer()
        content = request.get_json()
        if len(content['word'].split()) != 1:
            return json.dumps({
                "result": None,
                "ServerExecutionTime": timer() - start,
                "Error": "Error: Please, choose one word and try again."
            })
        content['word'] = content['word'].strip()
        print(content)
        hypernyms = find_hypernyms(content['word'])

        result = {
            "result": hypernyms,
            "ServerExecutionTime": timer() - start,
            "Error": None
        }

        return json.dumps(result)
    except Exception as e:
        app.logger.error('In hypernyms, error is: {}\n{}'.format(e, traceback.format_exc()))
        return jsonify(result="failed")


@app.route('/api/hypon', methods=['POST'])
def hyponyms():
    try:
        start = timer()
        content = request.get_json()
        if len(content['word'].split()) != 1:
            return json.dumps({
                "result": None,
                "ServerExecutionTime": timer() - start,
                "Error": "Error: Please, choose one word and try again."
            })
        content['word'] = content['word'].strip()
        print(content)
        hyponyms = find_hyponyms(content['word'])

        result = {
            "result": hyponyms,
            "ServerExecutionTime": timer() - start,
            "Error": None
        }

        return json.dumps(result)
    except Exception as e:
        app.logger.error('In hyponyms, error is: {}\n{}'.format(e, traceback.format_exc()))
        return jsonify(result="failed")


@app.route('/api/confused_word', methods=['POST'])
def confused_word():
    try:
        start = timer()
        content = request.get_json()
        if len(content['word'].split()) != 1:
            return json.dumps({
                "result": None,
                "ServerExecutionTime": timer() - start,
                "Error": "Error: Please, choose one word and try again."
            })
        content['word'] = content['word'].strip()
        print(content)
        confused_word = get_confused_word(content['word'])

        result = {
            "result": None if confused_word is None else confused_word.note,
            "ServerExecutionTime": timer() - start,
            "Error": None if confused_word is not None else f"Error: The {content['word']} "
                                                            f"is not in the confused words list"
        }

        return json.dumps(result)
    except Exception as e:
        app.logger.error('In confused_word, error is: {}\n{}'.format(e, traceback.format_exc()))
        return jsonify(result="failed")


@app.route('/api/sentence_structure', methods=['POST'])
def sentence_structure():
    try:
        start = timer()
        content = request.get_json()
        if len(content['word'].split()) != 1:
            return json.dumps({
                "result": None,
                "ServerExecutionTime": timer() - start,
                "Error": "Error: Please, choose one word and try again."
            })
        content['word'] = content['word'].strip()
        print(content)
        sentence_structure = get_sentence_structure(content['word'])

        result = {
            "result": None if sentence_structure is None else sentence_structure.structure,
            "ServerExecutionTime": timer() - start,
            "Error": None if sentence_structure is not None else f"Error: The {content['word']} "
                                                            f"is not in the sentence structure list"
        }

        return json.dumps(result)
    except Exception as e:
        app.logger.error('In sentence_structure, error is: {}\n{}'.format(e, traceback.format_exc()))
        return jsonify(result="failed")


@app.route('/api/asl', methods=['POST'])
def avg_sent_len():
    try:
        start = timer()
        content = request.get_json()
        if len(content['text'].split()) < 1:
            return json.dumps({
                "result": None,
                "ServerExecutionTime": timer() - start,
                "Error": "Error: Please, choose at least one word and try again."
            })
        asl = avg_sentence_len(content['text'])

        result = {
            "result": None if asl is None else asl,
            "ServerExecutionTime": timer() - start,
            "Error": None if asl is not None else "Error: There was some error"
        }

        return json.dumps(result)
    except Exception as e:
        app.logger.error('In avg_sent_len, error is: {}\n{}'.format(e, traceback.format_exc()))
        return jsonify(result="failed")


@app.route('/api/useful', methods=['GET'])
def useful_phrases():
    try:
        useful_phrases_dictionary = get_useful_phrase()
        result = {
            "keys": list(useful_phrases_dictionary.keys()),
            "examples": list(useful_phrases_dictionary.values())
        }

        return json.dumps(result)
    except Exception as e:
        app.logger.error('In useful_phrases, error is: {}\n{}'.format(e, traceback.format_exc()))
        return jsonify(result="failed")


@app.route('/api/translate', methods=['POST'])
def translate():
    try:
        content = request.get_json()
        print(content)
        result = google_translate(content['text'], content['language'])

        return json.dumps(result)
    except Exception as e:
        app.logger.error('In translate, error is: {}\n{}'.format(e, traceback.format_exc()))
        return jsonify(result="failed")


# WordNet
@app.route('/api/dictionary', methods=['POST'])
def dictionary():
    try:
        start = timer()
        content = request.get_json()
        if len(content['word'].split()) != 1:
            return json.dumps({
                "result": None,
                "ServerExecutionTime": timer() - start,
                "Error": "Error: Please, choose one word and try again."
            })
        content['word'] = content['word'].strip()
        syns = wordnet.synsets(content['word'])
        response = syns[0].definition()

        result = {
            "result": None if response is None else response,
            "ServerExecutionTime": timer() - start,
            "Error": None if response is not None else "Error: There was some error"
        }

        return json.dumps(result)
    except Exception as e:
        app.logger.error('In dictionary, error is: {}\n{}'.format(e, traceback.format_exc()))
        return jsonify(result="failed")


@app.route('/api/summ', methods=['POST'])
def text_summary():
    try:
        start = timer()
        content = request.get_json()
        if len(content['text'].split()) < 1:
            return json.dumps({
                "result": "Error: Selection is empty.",
                "ServerExecutionTime": timer() - start
            })
        result = text_summarization(content['text'])

        result = {
            "result": result,
            "ServerExecutionTime": timer() - start
        }
        return json.dumps(result)
    except Exception as e:
        app.logger.error('In text_summary, error is: {}\n{}'.format(e, traceback.format_exc()))
        return jsonify(result="failed")

        return str("Error: " + str(e))


@app.route('/NLP', methods=['GET', 'POST'])
def nlp():
    sentence = ""
    form = PredictForm()
    prediction = None
    if form.validate_on_submit():
        sentence = form.sentence.data
        form.sentence.data = ''
        if sentence == "":
            flash(f'Sentence is empty!', 'error')
            return render_template('predict.html', form=form, sentence=sentence, prediction=prediction)
        prediction = predict_class(sentence=sentence, model=app.config['MODEL'], device=app.config['DEVICE'])
        if prediction == "Clear":
            flash(f'\'{sentence}\' - Clear', 'success')
        elif prediction == "Wordy":
            flash(f'\'{sentence}\' - Wordy', 'error')
    return render_template('predict.html', form=form, sentence=sentence, prediction=prediction)


@app.route('/api/predict/<path:sentence>', methods=['POST'])
def predict(sentence):
    pass
    # start = timer()
    # if not sentence:
    #     result = {
    #         "result": "Error: Sentence is empty",
    #         "ServerExecutionTime": timer() - start
    #     }
    # else:
    #     prediction = predict_class(sentence=sentence, model=app.config['MODEL'], device=app.config['DEVICE'])
    #
    #     result = {
    #         "result": prediction,
    #         "ServerExecutionTime": timer() - start
    #     }
    # return json.dumps(result)
