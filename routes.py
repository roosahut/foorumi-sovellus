from crypt import methods
from app import app
from flask import render_template, request, redirect
import users
import forums as fr


@app.route('/')
def index():
    forums = fr.get_forums_info()
    return render_template('index.html', forums=forums)


@app.route('/register', methods=['get', 'post'])
def reqister():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        username = request.form['username']
        if len(username) > 25:
            return render_template('error.html', message='The username is too long')
        if len(username) < 8:
            return render_template('error.html', message='Username is too short')

        password1 = request.form['password1']
        password2 = request.form['password2']
        if password1 != password2:
            return render_template('error.html', message='The passwords are not the same')
        if len(password1) < 8:
            return render_template('error.html', message='Password is too short')

        role = request.form['role']
        if role not in ['1', '2']:
            return render_template('error.html', message='Unknown user')

        if not users.register(username, password1, role):
            return render_template('error.html', message='The registration was unsuccesful, try a different username')

        return redirect('/')


@app.route('/login', methods=['get', 'post'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not users.login(username, password):
            return render_template('error.html', message='Wrong username or password')
        return redirect('/')


@app.post('/logout')
def logout():
    users.logout()
    return redirect('/')


@app.route('/forum/<int:forum_id>')
def show_forum(forum_id):
    chains = fr.get_chains_info_in_forum(forum_id)
    name = fr.get_forum_name(forum_id)[0]
    return render_template('forum.html', id=forum_id, chains=chains, name=name)


@app.route('/forum/<int:forum_id>/<int:chain_id>')
def show_chain(forum_id, chain_id):
    messages = fr.get_messages_info(chain_id)
    chain_info = fr.get_chains_info(chain_id)[0]
    return render_template('chain.html', id=chain_id, forum_id=forum_id, messages=messages, chain_info=chain_info)


@app.route('/forum/<int:forum_id>/new_chain', methods=['get', 'post'])
def add_new_chain(forum_id):
    if request.method == 'GET':
        return render_template('new_chain.html', forum_id=forum_id)

    if request.method == 'POST':
        users.check_csrf()

        headline = request.form['headline']
        if headline == "":
            return render_template("error.html", message="You have to write a headline")
        if 2 > len(headline) > 20:
            return render_template("error.html", message="Headline must be between 2-15 characters")

        message = request.form['message']
        if message == "":
            return render_template("error.html", message="You have to write a message to start the chain")
        if len(message) > 10000:
            return render_template("error.html", message="The message is too long")

        chain_id = fr.add_new_chain(
            headline, message, users.user_id(), forum_id)

        return redirect(f'/forum/{forum_id}/{chain_id}')


@app.post('/new_message')
def new_message():
    users.check_csrf()

    chain_id = request.form['chain_id']
    writer_id = users.user_id()

    message = request.form['message']
    if message == "":
        return render_template("error.html", message="You have to write a message to submit")
    if len(message) > 10000:
        return render_template("error.html", message="The message is too long")

    fr.add_new_message(message, writer_id, chain_id)

    forum_id = request.form['forum_id']
    return redirect(f'/forum/{forum_id}/{chain_id}')


@app.post('/new_forum')
def new_forum():
    users.check_csrf()
    users.require_role(2)

    name = request.form['name']
    if name == "":
        return render_template("error.html", message="You have to give the forum a name")
    if len(name) > 20:
        return render_template("error.html", message="The forum-name is too long")

    creator_id = users.user_id()
    forum_id = fr.add_new_forum(name, creator_id)
    return redirect(f'/forum/{forum_id}')


@app.post('/delete_message')
def delete_message():
    users.check_csrf()

    message_id = request.form['message_id']
    writer_id = users.user_id()
    fr.delete_message(message_id, writer_id)

    forum_id = request.form['forum_id']
    chain_id = request.form['chain_id']
    return redirect(f'/forum/{forum_id}/{chain_id}')


@app.route('/forum/<int:forum_id>/<int:chain_id>/<int:message_id>', methods=['get', 'post'])
def edit_message(forum_id, chain_id, message_id):
    if request.method == 'GET':
        return render_template('edit_message.html', forum_id=forum_id, chain_id=chain_id, message_id=message_id)

    if request.method == 'POST':
        users.check_csrf()

        message = request.form['message']
        if message == "":
            return render_template("error.html", message="You have to write a message")
        if len(message) > 10000:
            return render_template("error.html", message="The message is too long")
        writer_id = users.user_id()

        fr.edit_message(message_id, message, writer_id)

        return redirect(f'/forum/{forum_id}/{chain_id}')

@app.route('/forum/<int:forum_id>/<int:chain_id>/edit_headline', methods=['get', 'post'])
def edit_headline(forum_id, chain_id):
    if request.method == 'GET':
        return render_template('edit_headline.html', forum_id=forum_id, chain_id=chain_id)

    if request.method == 'POST':
        users.check_csrf()

        headline = request.form['headline']
        if headline == "":
            return render_template("error.html", message="You have to write something to be the headline")
        if 2 > len(headline) > 20:
            return render_template("error.html", message="Headline must be between 2-15 characters")
        writer_id = users.user_id()

        fr.edit_chain_headline(chain_id, headline, writer_id)

        return redirect(f'/forum/{forum_id}/{chain_id}')

@app.post('/delete_chain')
def delete_chain():
    users.check_csrf()

    chain_id = request.form['chain_id']
    creator_id = users.user_id()
    fr.delete_chain(chain_id, creator_id)

    forum_id = request.form['forum_id']
    return redirect(f'/forum/{forum_id}')

@app.post('/delete_forum')
def delete_forum():
    users.check_csrf()
    users.require_role(2)

    forum_id = request.form['forum_id']
    fr.delete_forum(forum_id)

    forum_id = request.form['forum_id']
    return redirect(f'/')

@app.route('/search', methods=['get', 'post'])
def search_messages():
    if request.method == 'GET':
        is_words = False
        return render_template('search.html', is_words=is_words)

    if request.method == 'POST':
        users.check_csrf()

        word = request.form['word']
        if word == "":
            return render_template("error.html", message="You have to input a word or letter")
        words = fr.find_messages_with_word(word)
        is_words = True

        return render_template('search.html', words=words, is_words=is_words)