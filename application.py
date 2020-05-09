import json

from verbs import find_verbs
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
    content = request.get_json()
    print(content)
    result_dic = find_verbs(content['text'])

    return json.dumps(result_dic)


@app.route('/api/translate', methods=['POST'])
def translate():
    content = request.get_json()
    print(content)
    result_dic = google_translate(content['text'], content['language'])

    return json.dumps(result_dic)


if __name__ == '__main__':
    app.run()
