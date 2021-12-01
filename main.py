from flask import Flask
from sympy import *
import numpy as np
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route("/")
def index():
    return "<p>test</p>"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)