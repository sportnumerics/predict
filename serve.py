from flask import Flask, send_file
app = Flask(__name__)

@app.route("/ratings")
def ratings():
    return send_file('pcd_ratings.json',mimetype='application/json')

if __name__ == "__main__":
    app.run()
