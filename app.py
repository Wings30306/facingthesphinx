import os
from flask import Flask, render_template, redirect, request, url_for
import json

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signin")
def show_signin():
  return render_template("signin.html")


@app.route("/signin", methods=["POST"])
def sign_in():
    user = request.form["username"]
    with open("data/users.txt", "r") as file:
        score = 0
        question_number = 1
        active_users = file.read().splitlines()
        if user in active_users:
            return redirect(f"/riddles/{user}/question{question_number}/{score}")
        else:
            signin_message = "Sorry, this username is incorrect. New user? "
            return render_template("signin.html", signin_message=signin_message)


@app.route("/register")
def show_register():
  return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():
    user = request.form["new_user"]
    with open("data/users.txt", "r") as file:
        active_users = file.read().splitlines()
        if user in active_users:
            register_message = "Sorry, this username is taken. Please choose a different username.\nAre you already a user? "
        else:
            file = open("data/users.txt", "a")
            file.write(user + "\n")
            register_message = "You are now registered. "
        return render_template("register.html", register_message=register_message)


@app.route("/riddles/<user>/question<question_number>/<score>")
def show_riddles(user, score, question_number):
    data = []
    question_number = question_number
    with open("data/riddles.json", "r", encoding="utf-8") as riddle_data:
        data = json.load(riddle_data)["riddles"]
    return render_template('riddle.html', riddles=data, question_number=question_number, score=score)


@app.route("/riddles/<user>/question<question_number>/<score>", methods=["POST"])
def check_answer(score, question_number, user):
    correct_answer = request.form.get("correct_answer")
    score = int(score)
    user_answer = request.form.get("guess").lower()
    if correct_answer in user_answer:
        message = "correct"
        score += 1
    else:
        message = "wrong"
    return redirect(url_for("answer_result", user=user, message=message, user_answer=user_answer, correct_answer=correct_answer, score=score, question_number=question_number))


@app.route("/answers/<user>/question<question_number>/<score>/<message>/<user_answer>/<correct_answer>")
def answer_result(user, message, user_answer, correct_answer, score, question_number):
    return render_template("answer.html", message=message, user_answer=user_answer, correct_answer=correct_answer, score=score, question_number=question_number, user=user)


@app.route("/answers/<user>/question<question_number>/<score>/<message>/<user_answer>/<correct_answer>", methods=["POST"])
def next_question(question_number, score, user, message, user_answer, correct_answer):
    question_number = int(question_number)
    question_number += 1
    score = score
    user = user
    return redirect(f"/riddles/{user}/question{question_number}/{score}")


@app.route("/answers/<user>/question20/<score>/<message>/<user_answer>/<correct_answer>", methods=["POST"])
def player_score_write_to_LB(score, user, message, user_answer, correct_answer):
    score=int(score)
    player_score = {"user": user, "score": score}
    player_score = (player_score)
    with open("data/score.json", "r") as score_data:
        player_score = {"user": user, "score": score}
        leaderboard = json.load(score_data)
        leaderboard["users"].append(player_score)
        with open("data/score.json", "w") as score_data_updated:
            json.dump(leaderboard, score_data_updated, indent=2)


if __name__ == "__main__":
    app.run(host=os.getenv("IP"),
            port=os.getenv("PORT"),
            debug=True)
