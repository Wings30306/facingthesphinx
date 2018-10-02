import os
from flask import Flask, render_template, redirect, request, url_for
import json

app = Flask(__name__)

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/riddles")
def show_riddles():
  data = []
  question_number=1
  with open("data/riddles.json", "r", encoding="utf-8") as riddle_data:
    data = json.load(riddle_data)["riddles"]
  return render_template('riddle.html', riddles = data, question_number=question_number)


@app.route("/riddles", methods=["POST"])
def check_answer():
  correct_answer=request.form.get("correct_answer")
  user_answer=request.form.get("guess")
  if correct_answer in user_answer:
    message="correct!"
  else:
    message="wrong!"
  return render_template("answer.html", message=message, user_answer=user_answer, correct_answer=correct_answer)
      



if __name__ == "__main__":
  app.run(host=os.getenv("IP"),
          port=os.getenv("PORT"),
          debug=True)