from crypt import methods
from app import app
from flask import render_template, request, redirect
import users
import forums as fr


@app.route('/')
def index():
    forums = fr.get_forums_info()
    users_list = users.get_all_users()
    return render_template('index.html', forums=forums, users=users_list)


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
    if fr.has_user_forum_access(forum_id, users.user_id()):
        chains = fr.get_chains_info_in_forum(forum_id)
        name = fr.get_forum_name(forum_id)[0]
        return render_template('forum.html', id=forum_id, chains=chains, name=name)
    else:
        return render_template("error.html", message="No access to this forum")


@app.route('/forum/<int:forum_id>/<int:chain_id>')
def show_chain(forum_id, chain_id):
    if fr.has_user_forum_access(forum_id, users.user_id()):
        messages = fr.get_messages_info(chain_id)
        chain_info = fr.get_chains_info(chain_id)[0]
        return render_template('chain.html', id=chain_id, forum_id=forum_id, messages=messages, chain_info=chain_info)

    else:
        return render_template("error.html", message="No access to this forum")


@app.route('/forum/<int:forum_id>/new_chain', methods=['get', 'post'])
def add_new_chain(forum_id):
    if request.method == 'GET':
        if fr.has_user_forum_access(forum_id, users.user_id()) and users.user_id() > 0:
            return render_template('new_chain.html', forum_id=forum_id)

        else:
            return render_template("error.html", message="No access")

    if request.method == 'POST':
        users.check_csrf()

        if fr.has_user_forum_access(forum_id, users.user_id()) and users.user_id() > 0:
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

        else:
            return render_template("error.html", message="No access")


@app.post('/new_message')
def new_message():
    users.check_csrf()

    forum_id = request.form['forum_id']
    if fr.has_user_forum_access(forum_id, users.user_id()) and users.user_id() > 0:
        chain_id = request.form['chain_id']
        writer_id = users.user_id()

        message = request.form['message']
        if message == "":
            return render_template("error.html", message="You have to write a message to submit")
        if len(message) > 10000:
            return render_template("error.html", message="The message is too long")

        fr.add_new_message(message, writer_id, chain_id)

        return redirect(f'/forum/{forum_id}/{chain_id}')

    else:
        return render_template("error.html", message="No access")


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

    access_choice = request.form['access_choice']
    if access_choice not in ['public', 'private']:
        return render_template("error.html", message="Unknown access choice")

    if access_choice == 'public':
        forum_id = fr.add_new_forum(name, creator_id, False)

    elif access_choice == 'private':
        forum_id = fr.add_new_forum(name, creator_id, True)
        allowed_users = request.form.getlist('allowed_user')
        for user_id in allowed_users:
            fr.add_access_to_secret_forum(forum_id, user_id)

    return redirect(f'/')


@app.post('/delete_message')
def delete_message():
    users.check_csrf()

    forum_id = request.form['forum_id']
    message_id = request.form['message_id']
    if fr.has_user_forum_access(forum_id, users.user_id()) and fr.is_user_message_writer(message_id, users.user_id()):
        fr.delete_message(message_id, users.user_id())

        chain_id = request.form['chain_id']
        return redirect(f'/forum/{forum_id}/{chain_id}')

    else:
        return render_template("error.html", message="No access")


@app.route('/forum/<int:forum_id>/<int:chain_id>/<int:message_id>', methods=['get', 'post'])
def edit_message(forum_id, chain_id, message_id):
    if request.method == 'GET':
        if fr.has_user_forum_access(forum_id, users.user_id()) and fr.is_user_message_writer(message_id, users.user_id()):
            return render_template('edit_message.html', forum_id=forum_id, chain_id=chain_id, message_id=message_id)
        else:
            return render_template("error.html", message="No access")

    if request.method == 'POST':
        users.check_csrf()

        if fr.has_user_forum_access(forum_id, users.user_id()) and fr.is_user_message_writer(message_id, users.user_id()):
            message = request.form['message']
            if message == "":
                return render_template("error.html", message="You have to write a message")
            if len(message) > 10000:
                return render_template("error.html", message="The message is too long")
            writer_id = users.user_id()

            fr.edit_message(message_id, message, writer_id)

            return redirect(f'/forum/{forum_id}/{chain_id}')

        else:
            return render_template("error.html", message="No access")


@app.route('/forum/<int:forum_id>/<int:chain_id>/edit_headline', methods=['get', 'post'])
def edit_headline(forum_id, chain_id):
    if request.method == 'GET':
        if fr.has_user_forum_access(forum_id, users.user_id()) and fr.is_user_chain_creator(chain_id, users.user_id()):
            return render_template('edit_headline.html', forum_id=forum_id, chain_id=chain_id)

        else:
            return render_template("error.html", message="No access")

    if request.method == 'POST':
        users.check_csrf()

        if fr.has_user_forum_access(forum_id, users.user_id()) and fr.is_user_chain_creator(chain_id, users.user_id()):
            headline = request.form['headline']
            if headline == "":
                return render_template("error.html", message="You have to write something to be the headline")
            if 2 > len(headline) > 20:
                return render_template("error.html", message="Headline must be between 2-15 characters")
            writer_id = users.user_id()

            fr.edit_chain_headline(chain_id, headline, writer_id)

            return redirect(f'/forum/{forum_id}/{chain_id}')

        else:
            return render_template("error.html", message="No access")


@app.post('/delete_chain')
def delete_chain():
    users.check_csrf()

    forum_id = request.form['forum_id']
    chain_id = request.form['chain_id']
    if fr.has_user_forum_access(forum_id, users.user_id()) and fr.is_user_chain_creator(chain_id, users.user_id()):

        fr.delete_chain(chain_id, users.user_id())

        return redirect(f'/forum/{forum_id}')

    else:
        return render_template("error.html", message="No access to this forum")


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
        messages = fr.search_messages_with_word(word, users.user_id())
        is_words = True

        return render_template('search.html', messages=messages, is_words=is_words)


@app.post('/like_message')
def like_message():
    users.check_csrf()

    forum_id = request.form['forum_id']
    if fr.has_user_forum_access(forum_id, users.user_id()) and users.user_id() > 0:
        liker_id = users.user_id()
        message_id = request.form['message_id']
        if not fr.has_user_liked_message(message_id, liker_id):
            return render_template("error.html", message="You can't like the same message twice")
        else:
            fr.like_message(message_id, liker_id)

            chain_id = request.form['chain_id']
            return redirect(f'/forum/{forum_id}/{chain_id}')

    else:
        return render_template("error.html", message="No access")


@app.post('/unlike_message')
def unlike_message():
    users.check_csrf()

    forum_id = request.form['forum_id']
    if fr.has_user_forum_access(forum_id, users.user_id()) and users.user_id() > 0:
        liker_id = users.user_id()
        message_id = request.form['message_id']
        if not fr.has_user_unliked_message(message_id, liker_id):
            return render_template("error.html", message="You can't unlike the same message twice")
        else:
            fr.unlike_message(message_id, liker_id)

            chain_id = request.form['chain_id']
            return redirect(f'/forum/{forum_id}/{chain_id}')

    else:
        return render_template("error.html", message="No access")
