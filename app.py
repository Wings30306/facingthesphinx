import os
from flask import Flask, render_template, redirect, request, url_for, session
import json
import random

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register")
def show_register():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():
    player = request.form["new_user"].lower()
    start_score = 0
    start_question_number = 1
    with open("data/riddles.json", "r", encoding="utf-8") as riddle_data:
        riddles_list = json.load(riddle_data)["riddles"]
        random.shuffle(riddles_list)
    with open("data/users.txt", "r") as userfile:
        active_users = userfile.read().splitlines()
        if player in active_users:
            message = "taken"
        else:
            file = open("data/users.txt", "a")
            file.write(player + "\n")
            session['user'] = player
            session['score'] = start_score
            session['question_number'] = start_question_number
            session['riddles'] = riddles_list
            return redirect(f"/riddles")
        return render_template("register.html",
                               register_message=message)


@app.route("/signin")
def show_signin():
    return render_template("signin.html")


@app.route("/signin", methods=["POST"])
def sign_in():
    player = request.form["username"].lower()
    start_score = 0
    start_question_number = 1
    with open("data/riddles.json", "r") as riddle_data:
        riddles_list = json.load(riddle_data)["riddles"]
        random.shuffle(riddles_list)
    with open("data/users.txt", "r", encoding="utf-8") as userfile:
        active_users = userfile.read().splitlines()
        if player in active_users:
            session['user'] = player
            session['score'] = start_score
            session['question_number'] = start_question_number
            session['riddles'] = riddles_list
            return redirect(f"/riddles")
        else:
            message = "Sorry, this username is incorrect. New user? "
            return render_template("signin.html", signin_message=message)


@app.route("/playagain")
def play_again():
    with open("data/riddles.json", "r", encoding="utf-8)") as riddle_data:
        riddles_list = json.load(riddle_data)["riddles"]
        random.shuffle(riddles_list)
    session['score'] = 0
    session['question_number'] = 1
    session['riddles'] = riddles_list
    return redirect(f"/riddles")


@app.route("/riddles")
def show_riddles():
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


@app.route("/riddles", methods=["POST"])
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


@app.route("/skip_question")
def skip():
    if session:
        session['question_number'] += 1
        if session['question_number'] >= 11:
            return write_to_LB()
        else:
            session['message'] = "skipped"
            return next_question()
    else:
        return redirect(url_for("index"))


@app.route("/answers")
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


@app.route("/answers", methods=["POST"])
def answer_buttons():
    if session:
        if session['question_number'] >= 11:
            write_to_LB()
        else:
            next_question()
    else:
        return redirect(url_for("index"))


@app.route("/next_question", methods=["POST"])
def next_question():
    return redirect(url_for('show_riddles'))


@app.route("/view_leaderboard", methods=["GET", "POST"])
def write_to_LB():
    with open("data/score.json", "r") as score_data:
        player_score = {"user": session['user'], "score": session['score']}
        leaderboard = json.load(score_data)
        leaderboard["users"].append(player_score)
        with open("data/score.json", "w") as score_data_updated:
            json.dump(leaderboard, score_data_updated, indent=2)
    return redirect(url_for('show_LB'))


@app.route("/leaderboard")
def show_LB():
    with open("data/score.json", "r", encoding="utf-8") as score_data:
        data = json.load(score_data)["users"]
    return render_template("leaderboard.html", scores=data)


@app.route("/log_out")
def log_out():
    session.pop("user", None)
    session.pop("question_number", None)
    session.pop("score", None)
    session.pop("riddles", None)
    session.pop("message", None)
    session.pop("user_answer", None)
    session.pop("correct_answer", None)
    return render_template("loggedout.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(host=os.getenv("IP"),
            port=os.getenv("PORT"),
            debug=False)
