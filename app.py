import os
from flask import Flask, render_template, redirect, request, url_for, session
import json
import random

app = Flask(__name__)
app.secret_key = os.urandom(24)


"""HELPER FUNCTIONS"""

"""Error Handlers"""
"""Page Not Found"""
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


"""Server Error"""
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500 


"""Read User File"""
def users():
    with open("data/users.txt", "r") as userfile:
        active_users = userfile.read().splitlines()
        return active_users


"""Create questions list"""
def shuffle_riddles():
    with open("data/riddles.json", "r", encoding="utf-8") as riddle_data:
        riddles_list = json.load(riddle_data)["riddles"]
        random.shuffle(riddles_list)
        return riddles_list


"""set start of game variables"""
def start():
    session['score'] = 0
    session['question_number'] = 1
    session['riddles'] = shuffle_riddles()
    return session['score'], session['question_number'], session['riddles']


"""Read Score file"""
def scores():
    with open("data/score.json", "r", encoding="utf-8") as score_data:
        data = json.load(score_data)
        return data


"""APP ROUTES"""

"""Displays Index Page"""
@app.route("/")
def index():
    return render_template("index.html")


"""Displays Register Page"""
@app.route("/register")
def show_register():
    return render_template("register.html")


"""Writes User Input To File; Redirects to Riddles"""
@app.route("/register", methods=["POST"])
def register():
    player = request.form["new_user"].lower()
    active_users = users()
    if player in active_users:
        message = "taken"
    else:
        userfile = open("data/users.txt", "a")
        userfile.write(player + "\n")
        session['user'] = player
        start()
        return redirect(url_for("show_riddle"))
    return render_template("register.html",
                            register_message=message)


"""Displays Log-In Page"""
@app.route("/signin")
def show_signin():
    return render_template("signin.html")


"Create session for registered user, shows warning if user is not yet registered."
@app.route("/signin", methods=["POST"])
def sign_in():
    player = request.form["username"].lower()
    active_users = users()
    if player in active_users:
        session['user'] = player
        start()
        return redirect(f"/riddle")
    else:
        message = "Sorry, this username is incorrect. New user? "
        return render_template("signin.html", signin_message=message)


"""Resets score and question number and creates new riddle list if user in session wants to play again"""
@app.route("/playagain")
def reset():
    if session: 
        start()
        return redirect(f"/riddle")
    else:
        return redirect(url_for("index"))


"""Displays Riddle Page"""
@app.route("/riddle")
def show_riddle():
    if session:
        question_number = session['question_number']
        data = session['riddles']
        score = session['score']
        return render_template('riddle.html',
                               riddles=data,
                               question_number=question_number,
                               score=score)
    else:
        return redirect(url_for("index"))


"""Compares user's answer with expected keyword for correct answer"""
@app.route("/riddle", methods=["POST"])
def check_answer():
    if session:
        session['correct_answer'] = request.form.get("correct_answer")
        session['user_answer'] = request.form.get("guess").lower()
        session['question_number'] += 1
        if session['correct_answer'] in session['user_answer']:
            session['message'] = "correct"
            session['score'] += 1
        else:
            session['message'] = "wrong"
        return redirect(url_for("answer_result"))
    else:
        return redirect(url_for("index"))


"""Allows user to skip question and immediately proceed to the next riddle"""
@app.route("/skip_question")
def skip():
    if session:
        session['question_number'] += 1
        if session['question_number'] >= 11:
            return redirect(url_for("write_to_LB"))
        else:
            session['message'] = "skipped"
            return redirect(url_for("show_riddle"))
    else:
        return redirect(url_for("index"))


"""Displays Answer Page"""
@app.route("/answer")
def answer_result():
    if session:
        return render_template("answer.html",
                               message=session['message'],
                               user_answer=session['user_answer'],
                               correct_answer=session['correct_answer'],
                               score=session['score'],
                               question_number=session['question_number'],
                               user=session['user'])
    else:
        return redirect(url_for("index"))



@app.route("/answer_redirect", methods=["POST"])
def redirecting_from_answer_page():
    if session:
        if session['question_number'] >= 11:
            return redirect(url_for("write_to_LB"))
        else:
            return redirect(url_for("show_riddle"))
    else:
        return redirect(url_for("index"))


"""Writes username and score to leaderboard at end of game"""
@app.route("/leaderboard", methods=["GET", "POST"])
def write_to_LB():
    if session: 
        session['question_number']=11
        player_score = {"user": session['user'], "score": session['score']}
        leaderboard = scores()
        leaderboard["users"].append(player_score)
        with open("data/score.json", "w") as score_data:
            json.dump(leaderboard, score_data, indent=2)
        return redirect(url_for('show_LB'))
    else:
        return redirect(url_for("index"))


"""Displays Leaderboard Page"""
@app.route("/view_leaderboard")
def show_LB():
    data=scores()["users"]
    return render_template("leaderboard.html", scores=data)


"""Clears Session And Displays Log-Out Page"""
@app.route("/log_out")
def log_out():
    if session:
        session.clear()
        return render_template("loggedout.html")
    else:
        return redirect(url_for("index"))


"""Runs application"""
if __name__ == "__main__":
    app.run(host=os.getenv("IP"),
            port=os.getenv("PORT"),
            debug=True)
