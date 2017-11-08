from flask import Flask, url_for, render_template, json, request, redirect
app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html'), 200
  
@app.route('/about/')
def about():
  return render_template('about.html'), 200

@app.route('/membership/')
def membership():
  return render_template('membership.html'), 200
  
@app.route('/annual_ride/')
def annual_ride():
  return render_template('annual_ride.html'), 200

@app.errorhandler(404)
def page_not_found(error):
	return render_template('404.html'), 404

if __name__ == ("__main__"):
  app.run(host='0.0.0.0', debug=True)
