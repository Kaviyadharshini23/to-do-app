from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'secretkey123'  # Needed for sessions

# MongoDB Local Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["todo_app"]
users = db["users"]
tasks = db["tasks"]

# Home
@app.route('/')
def home():
    return redirect('/login')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users.insert_one({
            'username': request.form['username'],
            'password': request.form['password']
        })
        return redirect('/login')
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = users.find_one({
            'username': request.form['username'],
            'password': request.form['password']
        })
        if user:
            session['username'] = user['username']
            return redirect('/todo')
    return render_template('login.html')

# To-Do Page
@app.route('/todo', methods=['GET', 'POST'])
def todo():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        tasks.insert_one({
            'user': session['username'],
            'task': request.form['task'],
            'status': 'pending'
        })
    user_tasks = list(tasks.find({'user': session['username']}))
    return render_template('todo.html', tasks=user_tasks)

# Mark as done
@app.route('/complete/<task_id>')
def complete(task_id):
    from bson.objectid import ObjectId
    tasks.update_one({'_id': ObjectId(task_id)}, {'$set': {'status': 'completed'}})
    return redirect('/todo')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    all_tasks = list(tasks.find({'user': session['username']}))
    return render_template('dashboard.html', tasks=all_tasks)

if __name__ == '__main__':
    app.run(debug=True)
