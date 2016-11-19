import os
from flask import Flask, render_template
from damscraper import scrape_dam_forum

app = Flask(__name__)

@app.route("/")
def index():
    posts = scrape_dam_forum()
    return render_template("results.html", posts=posts)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
