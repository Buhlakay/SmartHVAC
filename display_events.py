from flask import Flask, redirect
from flask import render_template
from flask import request
import os

app = Flask(__name__)
port = os.getenv('VCAP_APP_PORT', '5000')


@app.route('/')
def door_route():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
