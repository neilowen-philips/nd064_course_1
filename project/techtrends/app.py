import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import sys


# Function to get a database connection.
def get_db_connection():
    # increment the number of connections
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM db_connections')
    num_con = cur.fetchone()
    num_db_con = int(num_con[0])
    num_db_con += 1
    cmd = ("UPDATE db_connections SET num_db_connections = " + str(num_db_con))
    cur.execute(cmd)
    con.commit()
    con.close()

    # get and return the connection
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

# Function to get a post title using its ID
def get_post_title(post_id):
    connection = get_db_connection()
    post_title = connection.execute('SELECT title FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    title_element = post_title[0]
    return title_element

def init_logger():
    # set logger to handle STDOUT and STDERR 
    logger = logging.getLogger('appLogger')
    logger.setLevel(logging.DEBUG)
    # handlers
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.DEBUG)
    # formatter
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s:%(message)s')
    stdout_handler.setFormatter(formatter)
    stderr_handler.setFormatter(formatter)
    # add handlers
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
 
# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

init_logger()
app.logger = logging.getLogger('appLogger')

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
      app.logger.debug('File not found. html.404 returned')
      return render_template('404.html'), 404
    else:
      
      app.logger.debug('Article "%s" retrieved!',get_post_title(post_id))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.debug('About Us page was visited')
    return render_template('about.html')

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

            return redirect(url_for('index'))

    app.logger.debug('Article "%s" created!')
    return render_template('create.html')

@app.route('/metrics')
def metrics():
    # get number of posts
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT COUNT(ALL ID) FROM posts')
    post_data = cur.fetchall()
    numPostsStr = str(post_data[0])
    numPosts = int(numPostsStr[1])

    # increment the number of connections
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM db_connections')
    num_con = cur.fetchone()
    num_db_con = int(num_con[0])
    num_db_con += 1
    cmd = ("UPDATE db_connections SET num_db_connections = " + str(num_db_con))
    cur.execute(cmd)
    con.commit()
    con.close()

    response = app.response_class(
            response=json.dumps({"db_connection_count":num_db_con,"Post count":numPosts}),
            status=200,
            mimetype='application/json'
    )
    app.logger.debug('Metrics request successful')
    return response

@app.route('/healthz')
def healthz():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.debug('Status request successful')
    app.logger.debug('DEBUG message')
    return response



# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
