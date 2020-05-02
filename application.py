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
    response = {"Text": "Hello " + content['name'] + ", I know that you are " + str(content['age']) + " years old."}
    return jsonify(response)


if __name__ == '__main__':
    app.run()
