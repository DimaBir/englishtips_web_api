import json

from verbs import find_verbs, find_verbs_per_char
from nouns import find_nouns
from google_translate import google_translate
from flask import Flask, render_template, request, jsonify
app = Flask(__name__, template_folder='templates')


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Gary'}
    posts = [
        {
            'author': {'username': 'Dima'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Netanel'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='EnglishTips', user=user, posts=posts)


@app.route('/api/test', methods=['POST'])
def test():
    content = request.get_json()
    print(content)

    response_json = {
        "Text": "Hello " + content['name'] + ", I know that you are " + str(content['age']) + " years old.",
        "indexes": [1, 10, 16, 17, 201]
    }

    return jsonify(response_json)


@app.route('/api/verbs', methods=['POST'])
def verbs():
    try:
        content = request.get_json()
        print(content)
        result_dic = find_verbs(content['text'])

        return json.dumps(result_dic)

    except Exception as e:
        return (str("Error: " + e))


@app.route('/api/verbs2', methods=['POST'])
def verbs2():
    try:
        content = request.get_json()
        print(content)
        result_dic = find_verbs_per_char(content['text'])

        return json.dumps(result_dic)

    except Exception as e:
        return (str("Error: " + e))


@app.route('/api/noun-compound', methods=['POST'])
def noun_compound():
    try:
        content = request.get_json()
        print(content)
        result_dic = find_nouns(content['text'])

        return json.dumps(result_dic)
    except Exception as e:
        return (str("Error: " + e))


@app.route('/api/translate', methods=['POST'])
def translate():
    try:
        content = request.get_json()
        print(content)
        result = google_translate(content['text'], content['language'])

        return json.dumps(result)
    except Exception as e:
        return (str("Error: " + e))


if __name__ == '__main__':
    app.run()
