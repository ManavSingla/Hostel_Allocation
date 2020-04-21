from flask import Flask, render_template, request, flash, url_for, redirect, sessions, session

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', title="Home")

@app.route('/studentlogin')
def slogin():
    return render_template('studentlogin.html', title="Login")

@app.route('/facultylogin')
def flogin():
    return render_template('facultylogin.html', title="Login")

if __name__ == "__main__":
    app.run(debug = True)
