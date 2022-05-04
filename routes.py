from app import app
from flask import render_template, request, redirect
import users
import forums as fr


@app.route('/')
def index():
    forums = fr.get_all_forums()
    counts = []
    for i in forums:
        messages = fr.get_message_count_in_forum(i[0])
        chains = fr.get_chain_count_in_forum(i[0])
        add = (messages, chains)
        counts.append(add)
    return render_template('index.html', forums=forums, counts=counts)


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
    chains = fr.get_chains_in_forum(forum_id)
    name = fr.get_forum_name(forum_id)[0]
    messages = []
    for chain in chains:
        message = fr.get_message_count_in_chain(chain[0])
        messages.append(message)
    return render_template('forum.html', id=forum_id, chains=chains, name=name, messages=messages)

@app.route('/chain/<int:chain_id>')
def show_chain(chain_id):
    messages = fr.get_messages_in_chain(chain_id)
    chain_info = fr.get_chain_info(chain_id)[0]
    return render_template('chain.html', id=chain_id, messages=messages, chain_info=chain_info)
