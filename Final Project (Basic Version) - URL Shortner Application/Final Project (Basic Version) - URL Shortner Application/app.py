from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import random
import string
import validators

app = Flask(__name__)

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Database Model
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(20), nullable=False)


# Create Database
with app.app_context():
    db.create_all()


# Generate Short URL (Custom Length)
def generate_short_url(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


# Home Route
@app.route('/', methods=['GET', 'POST'])
def home():

    short_url = ""
    error = ""

    if request.method == 'POST':

        long_url = request.form['url']
        length = int(request.form['length'])

        # URL Validation
        if not validators.url(long_url):
            error = "Invalid URL! Please enter a valid URL."

        else:
            code = generate_short_url(length)

            new_entry = URL(original_url=long_url, short_url=code)
            db.session.add(new_entry)
            db.session.commit()

            short_url = request.host_url + code

    return render_template('index.html',
                           short_url=short_url,
                           error=error)


# Redirect Route
@app.route('/<short_code>')
def redirect_url(short_code):

    data = URL.query.filter_by(short_url=short_code).first()

    if data:
        return redirect(data.original_url)

    return "Short URL Not Found!"


# History Page
@app.route('/history')
def history():

    all_urls = URL.query.all()
    return render_template('history.html', urls=all_urls)


if __name__ == '__main__':
    app.run(debug=True)