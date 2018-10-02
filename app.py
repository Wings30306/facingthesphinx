import os
from flask import Flask, render_template, redirect, request
import json

app = Flask(__name__)

@app.route("/")
def show_riddles():
  data = []
  question_number=20
  with open("data/riddles.json", "r", encoding="utf-8") as riddle_data:
    data = json.load(riddle_data)["riddles"]
  return render_template('riddle.html', riddles = data, question_number=question_number)


      



if __name__ == "__main__":
  app.run(host=os.getenv("IP"),
          port=os.getenv("PORT"),
          debug=True)