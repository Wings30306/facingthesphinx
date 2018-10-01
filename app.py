import os
from flask import Flask, render_template, redirect


app = Flask(__name__)

@app.route("/")
def hello():
  message = "Hello World"
  return render_template('riddle.html', message=message)

if __name__ == "__main__":
  app.run(host=os.getenv("IP"),
          port=os.getenv("PORT"),
          debug=True)