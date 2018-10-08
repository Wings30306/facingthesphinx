import os
from flask import Flask, render_template, redirect, request, url_for, session
import json
import random
from shutil import copyfile

app = Flask(__name__)
app.secret_key=os.urandom(24)


@app.route("/")
def index():
    copyfile("data/riddles.json", "data/riddles_shuffled.json")
    with open("data/riddles_shuffled.json", "r") as riddle_data:
        data = json.load(riddle_data)
        random.shuffle(data["riddles"])
        with open("data/riddles_shuffled.json", "w") as riddles_shuffled_updated:
            json.dump(data, riddles_shuffled_updated, indent=2)
    return render_template("index.html")


@app.route("/register")
def show_register():
  return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():
    player = request.form["new_user"]
    start_score = 0
    start_question_number = 1
    with open("data/riddles_shuffled.json", "r", encoding="utf-8") as riddle_data:
        riddles_list = json.load(riddle_data)["riddles"]
    with open("data/users.txt", "r") as file:
        active_users = file.read().splitlines()
        if player in active_users:
            register_message = "Sorry, this username is taken. Please choose a different username.\nAre you already registered? "
        else:
            file = open("data/users.txt", "a")
            file.write(player + "\n")
            session['user'] = player
            session['score'] = start_score
            session['question_number'] = start_question_number
            session['riddles'] = riddles_list
            user = session['user']
            return redirect(f"/riddles/{user}")
        return render_template("register.html", register_message=register_message)


@app.route("/signin")
def show_signin():
  return render_template("signin.html")


@app.route("/signin", methods=["POST"])
def sign_in():
    player = request.form["username"]
    start_score = 0
    start_question_number = 1
    with open("data/riddles_shuffled.json", "r", encoding="utf-8") as riddle_data:
        riddles_list = json.load(riddle_data)["riddles"]
    with open("data/users.txt", "r") as file:
        active_users = file.read().splitlines()
        if player in active_users:
            session['user'] = player
            session['score'] = start_score
            session['question_number'] = start_question_number
            session['riddles'] = riddles_list
            user = session['user']
            return redirect(f"/riddles/{user}")
        else:
            signin_message = "Sorry, this username is incorrect. New user? "
            return render_template("signin.html", signin_message=signin_message)


@app.route("/riddles/<user>")
def show_riddles(user):
    if user == session['user']:
        question_number = session['question_number']
        data = session['riddles']
        score = session['score']
        return render_template('riddle.html', riddles=data, question_number=question_number, score=score)
    else:
        return redirect(url_for("index"))


@app.route("/riddles/<user>", methods=["POST"])
def check_answer(user):
    if user == session['user']:
        correct_answer = request.form.get("correct_answer")
        user_answer = request.form.get("guess").lower()
        if correct_answer in user_answer:
            message = "correct"
            session['score'] += 1
        else:
            message = "wrong"
        return redirect(url_for("answer_result", user=user, message=message, user_answer=user_answer, correct_answer=correct_answer))
    else:
        return redirect(url_for("index"))


@app.route("/answers/<user>/<message>/<user_answer>/<correct_answer>")
def answer_result(user, message, user_answer, correct_answer):
    if user == session['user']:
        return render_template("answer.html", message=message, user_answer=user_answer, correct_answer=correct_answer, score=session['score'], question_number=session['question_number'], user=user)
    else:
        return redirect(url_for("index"))

@app.route("/answers/<user>/<message>/<user_answer>/<correct_answer>", methods=["POST"])
def next_question(user, message, user_answer, correct_answer):
    if user == session['user']:
        score = session['score']
        if session['question_number'] == 10:
            with open("data/score.json", "r") as score_data:
                player_score = {"user": user, "score": score}
                leaderboard = json.load(score_data)
                leaderboard["users"].append(player_score)
                with open("data/score.json", "w") as score_data_updated:
                    json.dump(leaderboard, score_data_updated, indent=2)
            return redirect(url_for('show_LB'))
        else:
            session['question_number'] += 1
            return redirect(f"/riddles/{user}")
    else:
        return redirect(url_for("index"))


@app.route("/leaderboard")
def show_LB():
  with open("data/score.json", "r", encoding="utf-8") as score_data:
    data = json.load(score_data)["users"]
  return render_template("leaderboard.html", scores=data)


@app.route("/log_out")
def log_out():
    session.pop("user", None)
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
