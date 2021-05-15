import sqlite3
import logging
import sys
from datetime import datetime
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


def logInfo(message):
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    app.logger.info(timestampStr + " " + message)


def logError(message):
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    app.logger.error(timestampStr + " " + message)

# Function to get a database connection.
# This function connects to database with the name `database.db`


def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID


def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application


@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logError("Failed article access: " + str(post_id))
        return render_template('404.html'), 404
    else:
        logInfo("Article acccessed: " + str(post_id))
        return render_template('post.html', post=post)

# Define the About Us page


@app.route('/about')
def about():
    logInfo("About page accessed")
    return render_template('about.html')

# Degine the Health Checker


@app.route('/healthz')
def healthz():
    return app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )

# Define metric route


@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    numberOfPosts = len(posts)
    connection.close()
    return app.response_class(
        response=json.dumps(
            {"db_connection_count": 5, "post_count": numberOfPosts}),
        status=200,
        mimetype='application/json'
    )


# Define the post creation functionality


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()
            logInfo("Article created")
            return redirect(url_for('index'))

    return render_template('create.html')


# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    app.run(host='0.0.0.0', port='3111')
