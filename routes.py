from app import app
from flask import render_template, request, redirect
import users


@app.route('/')
def index():
    return render_template('index.html')


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
        if role not in ['1','2']:
            return render_template('error.html', message='Unknown user')

        if users.register(username, password1, role) is False:
            return render_template('error.html', message='The registration was unsuccesful, try a different username')

        return redirect('/')

@app.route('/login', methods=['get', 'post'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not users.login(username,password):
            return render_template('error.html', message='Wrong username or password')
        return redirect('/')

@app.post('/logout')
def logout():
    users.logout()
    return redirect('/')