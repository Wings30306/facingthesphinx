import os
from flask import Flask, render_template, redirect, request, url_for
import json

app = Flask(__name__)

@app.route("/")
def index():
  return render_template("index.html")

score=0
question_number=1

@app.route("/riddles/question<question_number>/<score>")
def show_riddles(score, question_number):
  data = []
  question_number=1
  with open("data/riddles.json", "r", encoding="utf-8") as riddle_data:
    data = json.load(riddle_data)["riddles"]
  return render_template('riddle.html', riddles = data, question_number=question_number, score=score)


@app.route("/riddles/question<question_number>/<score>", methods=["POST"])
def check_answer(score, question_number):
  correct_answer=request.form.get("correct_answer")
  score = int(score)
  user_answer=request.form.get("guess")
  if correct_answer in user_answer:
    message="correct"
    score += 1
  else:
    message="wrong"
  return redirect(url_for("next_question", message=message, user_answer=user_answer, correct_answer=correct_answer, score=score, question_number=question_number))

@app.route ("/answers/question<question_number>/<score>/<message>/<user_answer>/<correct_answer>")
def answer_result(message, user_answer, correct_answer, score, question_number):
  return render_template("answer.html", message=message, user_answer=user_answer, correct_answer=correct_answer, score=score, question_number=question_number)

@app.route ("/answers/question<question_number>/<score>", methods=["POST"])
def next_question(question_number, score):
  question_number=int(question_number)
  question_number +=1
  score=score
  return redirect(url_for("show_riddles", question_number=question_number, score=score))



if __name__ == "__main__":
  app.run(host=os.getenv("IP"),
          port=os.getenv("PORT"),
          debug=True)