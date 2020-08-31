import os
import json

from timeit import default_timer as timer

from flask_migrate import Migrate
from werkzeug.utils import secure_filename

from acronyms import find_acronyms
from asl import avg_sentence_len
from confused_word import get_confused_word
from database.models import db
from database.setupdatabase import fill_database
from get_sentence_structure import get_sentence_structure
from hypernyms import find_hypernyms
from hyponyms import find_hyponyms
from synonym import find_synonyms
from uncountable_nouns import find_uncountable_nouns
from utils import UploadForm
from wordiness import find_wordiness
from toptenwords import find_top_ten_words
from verbs import find_verbs, find_verbs_per_char
from nouns import find_nouns, find_noun_compound
from google_translate import google_translate
from flask import Flask, render_template, request, jsonify, url_for, flash, redirect, send_from_directory, abort, \
    send_file

BASEDIR = os.path.abspath(os.path.dirname(__file__))
SERVER_PATH = os.path.join(BASEDIR, 'db.sqlite')
UPLOAD_FOLDER = r'C:/englishtips/englishtips_web_api/version/'
ALLOWED_EXTENSIONS = {'txt', 'zip'}

app = Flask(__name__, template_folder='templates')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
MAX_UPLOAD_SIZE_MB = 1
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE_MB * 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + SERVER_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ba86103dafb9ec379d26c7bd92206424'

db.init_app(app)

with app.app_context():
    db.create_all()
    # fill_database()

Migrate(app, db)

from project.admin.views import confused_word_blueprints
app.register_blueprint(confused_word_blueprints, url_prefix='/admin')


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
    name = "EnglishTips_v_0.1.zip"
    response = send_file(os.path.join(UPLOAD_FOLDER, "publish.zip"), as_attachment=True, mimetype="application/zip",
                         attachment_filename=name)
    response.headers["x-filename"] = name
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
        return str("Error: " + str(e))


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
        return str("Error: " + str(e))


@app.route('/api/uncountable', methods=['POST'])
def uncountable():
    try:
        content = request.get_json()
        print(content)
        result = find_uncountable_nouns(content['text'])
        return json.dumps(result)
    except Exception as e:
        return str("Error: " + str(e))


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
        return str("Error: " + str(e))


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
        return str("Error: " + str(e))


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
        return str("Error: " + str(e))


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
        return str("Error: " + str(e))


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
        return str("Error: " + str(e))


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
        return str("Error: " + str(e))


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
        return str("Error: " + str(e))


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
        return str("Error: " + str(e))


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
        return str("Error: " + str(e))


@app.route('/api/translate', methods=['POST'])
def translate():
    try:
        content = request.get_json()
        print(content)
        result = google_translate(content['text'], content['language'])

        return json.dumps(result)
    except Exception as e:
        return str("Error: " + str(e))


if __name__ == '__main__':
    import ssl

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain('avrl_cs_technion_ac_il.crt', 'AVRL_cs_technion_ac_il.key')
    app.run(host="0.0.0.0", port=80, ssl_context=context, threaded=True, debug=False)
    # app.run(debug=True)
