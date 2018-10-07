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
    session['user'] = request.form["new_user"]
    user = session['user']
    score = 0
    question_number = 1
    with open("data/users.txt", "r") as file:
        active_users = file.read().splitlines()
        if user in active_users:
            register_message = "Sorry, this username is taken. Please choose a different username.\nAre you already registered? "
        else:
            file = open("data/users.txt", "a")
            file.write(user + "\n")
            return redirect(f"/riddles/{user}/question{question_number}/{score}")
        return render_template("register.html", register_message=register_message)


@app.route("/signin")
def show_signin():
  return render_template("signin.html")


@app.route("/signin", methods=["POST"])
def sign_in():
    new_user = request.form["username"]
    score = 0
    question_number = 1
    with open("data/users.txt", "r") as file:
        active_users = file.read().splitlines()
        if new_user in active_users:
            session['user'] = new_user
            user = session['user']
            return redirect(f"/riddles/{user}/question{question_number}/{score}")
        else:
            signin_message = "Sorry, this username is incorrect. New user? "
            return render_template("signin.html", signin_message=signin_message)


@app.route("/riddles/<user>/question<question_number>/<score>")
def show_riddles(user, score, question_number):
    if user == session['user']:
        question_number = question_number
        with open("data/riddles_shuffled.json", "r", encoding="utf-8") as riddle_data:
            data = json.load(riddle_data)["riddles"]
        return render_template('riddle.html', riddles=data, question_number=question_number, score=score)
    else:
        return redirect(url_for("index"))


@app.route("/riddles/<user>/question<question_number>/<score>", methods=["POST"])
def check_answer(score, question_number, user):
    if user == session['user']:
        correct_answer = request.form.get("correct_answer")
        score = int(score)
        user_answer = request.form.get("guess").lower()
        if correct_answer in user_answer:
            message = "correct"
            score += 1
        else:
            message = "wrong"
        return redirect(url_for("answer_result", user=user, message=message, user_answer=user_answer, correct_answer=correct_answer, score=score, question_number=question_number))
    else:
        return redirect(url_for("index"))


@app.route("/answers/<user>/question<question_number>/<score>/<message>/<user_answer>/<correct_answer>")
def answer_result(user, message, user_answer, correct_answer, score, question_number):
    if user == session['user']:
        return render_template("answer.html", message=message, user_answer=user_answer, correct_answer=correct_answer, score=score, question_number=question_number, user=user)
    else:
        return redirect(url_for("index"))

@app.route("/answers/<user>/question<question_number>/<score>/<message>/<user_answer>/<correct_answer>", methods=["POST"])
def next_question(question_number, score, user, message, user_answer, correct_answer):
    if user == session['user']:
        question_number = int(question_number)
        question_number += 1
        score = score
        user = user
        return redirect(f"/riddles/{user}/question{question_number}/{score}")
    else:
        return redirect(url_for("index"))


@app.route("/answers/<user>/question10/<score>/<message>/<user_answer>/<correct_answer>", methods=["POST"])
def player_score_write_to_LB(score, user, message, user_answer, correct_answer):
    score=int(score)
    if score > 10:
        return redirect(url_for('cheat'))
    elif score < 0:
        return redirect(url_for('cheat'))
    elif score != int(score):
        return redirect(url_for('cheat'))
    else:
        if user == session['user']:
            player_score = {"user": user, "score": score}
            player_score = (player_score)
            with open("data/score.json", "r") as score_data:
                player_score = {"user": user, "score": score}
                leaderboard = json.load(score_data)
                leaderboard["users"].append(player_score)
                with open("data/score.json", "w") as score_data_updated:
                    json.dump(leaderboard, score_data_updated, indent=2)
            return redirect(url_for('show_LB'))
        else:
            return redirect(url_for("index"))


@app.route("/leaderboard")
def show_LB():
  with open("data/score.json", "r", encoding="utf-8") as score_data:
    data = json.load(score_data)["users"]
  return render_template("leaderboard.html", scores=data)


@app.route("/cheat")
def cheat():
    session.pop("user", None)
    return render_template("cheat.html")


@app.route("/log_out")
def log_out():
    session.pop("user", None)
    return render_template("loggedout.html")


if __name__ == "__main__":
    app.run(host=os.getenv("IP"),
            port=os.getenv("PORT"),
            debug=True)
