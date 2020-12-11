import os
import json

from nltk.corpus import wordnet
from timeit import default_timer as timer

from flask_migrate import Migrate
from werkzeug.utils import secure_filename

from NLP import predict_class, init
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
from flask import Flask, render_template, request, url_for, flash, redirect, send_file
from flask_login import login_required

BASEDIR = os.path.abspath(os.path.dirname(__file__))
SERVER_PATH = os.path.join(BASEDIR, 'db.sqlite')
UPLOAD_FOLDER = r'C:/englishtips/englishtips_web_api/version/'
ALLOWED_EXTENSIONS = {'txt', 'zip'}

app = Flask(__name__, template_folder='templates')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
MAX_UPLOAD_SIZE_MB = 2.5
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE_MB * 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + SERVER_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ba86103dafb9ec379d26c7bd92206424'
app.config['MODEL'] = None
app.config['DEVICE'] = None

db.init_app(app)
app.config['MODEL'], app.config['DEVICE'] = init()

#
# with app.app_context():
# #     db.create_all()
#       fill_database()

Migrate(app, db)

login_manager.init_app(app)
login_manager.login_view = 'login'

from app.project.admin.views import confused_word_blueprints
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
            # f = open('version.txt', 'r+')
            # old_version = (f.read())
            # old_version = int(old_version)
            # version = old_version + 1
            # f.truncate(0)  # need '0' when using r+
            # f.write(str(version))
            # f.close()
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
        return str("Error: " + str(e))


@app.route('/api/summ', methods=['POST'])
def text_summary():
    try:
        start = timer()
        content = request.get_json()
        print(content)
        result = text_summarization(content['text'])

        result = {
            "result": result,
            "ServerExecutionTime": timer() - start
        }
        return json.dumps(result)
    except Exception as e:
        return str("Error: " + str(e))


@app.route('/api/predict/<path:sentence>', methods=['POST'])
def predict(sentence):
    start = timer()
    if not sentence:
        result = {
            "result": "Error: Sentence is empty",
            "ServerExecutionTime": timer() - start
        }
    else:
        prediction = predict_class(sentence=sentence, model=app.config['MODEL'], device=app.config['DEVICE'])
        # not_wordy_0 = ("Among pathological hallmarks of AD are the senile plaques, which are formed by the copper induced aggregation of the amyloid beta peptides.", "Clear")
        # not_wordy_1 = ("Unmixing results is highly affected from imaging geometry: camera/view zenithal and azimuth angles and light source direction.", "Clear")
        # not_wordy_2 = ("The main idea of the DIP paper is using the network itself as the regularization for the corrupted image, without the need for training on thousandths of examples.", "Clear")
        # not_wordy_3 = ("Imaging is taking a big part of our lives, sciences use imagery for discovering from which particles are moon or Mars made of, agricultures know to irrigate or fertilize their field according to imagery of their field..", "Clear")
        # not_wordy_4 = ("Indeed, if parasites and pathogens follow the patterns predicted for other taxa, it is reasonable to expect that some diseases will adapt to changing environmental conditions and potentially increase in prevalence, whereas others will suffer negative consequences leading to range contractions and even local extinctions.", "Clear")
        # not_wordy_5 = ("In my opinion torture is always wrong.", "Clear")
        # not_wordy_6 = ("A few inches of snow is necessary to go sledding.", "Clear")
        # not_wordy_7 = ("New students are required to attend a meeting on Friday, September 22.", "Clear")
        # not_wordy_8 = ("I bought a dog for companionship.", "Clear")
        # wordy_1 = ("In my research I'm following the long quest for cognitive system.", "Wordy")
        # wordy_2 = ("This technique was proved to be efficient and accurate one, however, it still needneeds a primary expert analysis and not fully automatic.", "Wordy")
        # wordy_3 = ("At first, it is rather surprising that it is an abstract thing.", "Wordy")
        # wordy_4 = ("A few inches of snow on the ground is all that is necessary in order for a person to be able to go sledding.", "Wordy")
        # wordy_5 = ("The subjects that are considered most important by students are those that have been shown to be useful to them after graduation.", "Wordy")
        # wordy_6 = ("There are many students who like reading.", "Wordy")
        # wordy_7 = ("As part of the Paris agreement which was  signed in 2015, the world’s nations have agreed to pursue efforts to limit global warming to 1.5oC above the pre-industrial levels, in light of the  risks of the climate crisis.", "Wordy")
        # wordy_8 = ("The theory of lattices is a well developed one and has been used  to define the  real world objects known as crystals.", "Wordy")
        # wordy_9 = ("I bought a dog for the purpose of providing me with companionship.", "Wordy")
        #
        # result_labels = []
        # sentences = [not_wordy_0, not_wordy_1, not_wordy_2, not_wordy_3, not_wordy_4, not_wordy_5, not_wordy_6, not_wordy_7,
        #              not_wordy_8, wordy_1, wordy_2, wordy_3, wordy_4, wordy_5, wordy_6, wordy_7, wordy_8, wordy_9]
        #
        # for sen in sentences:
        #     result_labels.append(predict_class(sentence=sen[0], model=app.config['MODEL'], device=app.config['DEVICE']))
        #
        # i = 0
        # correct = 0
        # for label in result_labels:
        #     # print("\n" + sentences[i][0] + "\nPrediction: (" + label + ") -- " + "Correct" if sentences[i][1] == label else "Wrong")
        #     correct = correct + (1 if sentences[i][1] == label else 0)
        #     i = i + 1

        result = {
            "result": prediction,
            "ServerExecutionTime": timer() - start
        }
    return json.dumps(result)
