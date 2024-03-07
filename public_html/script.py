from flask import Flask, render_template, make_response, request
from datetime import datetime, timedelta
from zmienne import *
from zast2 import *
app = Flask(__name__)

@app.route('/')
def index():
    cookie = request.cookies.get('klasa')
    return render_template('index.html', klasa = cookie)

@app.route('/home')
def home():
    resp = make_response(render_template("main.html",klasa="None"))
    resp.delete_cookie('klasa')
    return resp

@app.route('/main')
def main():
    cookie = request.cookies.get('klasa')
    return render_template("main.html",klasa=cookie)

@app.route('/plan/<klasa>')
def plan(klasa):
    if klasa == "None":
        return "<h1>Wybierz Klasę</h1>"
    kol = ["NR","Godz","Poniedziałek","Wtorek","Środa","Czwartek","Piątek"]
    plan, zast = zast_and_plan(klasa)
    plan_tab = (plan,kol)
    output = render_template('plan.html',plan_tab=plan_tab,zast=zast,klasa=klasa)
    resp = make_response(output)
    expire_date =  datetime.now() + timedelta(days=90)
    resp.set_cookie('klasa', klasa, expires = expire_date)  
    return resp

@app.route('/buttons')
def buttons():
    return render_template("buttons.html",klasy_v=klasy_v)

@app.route('/nauczyciele')
def nauczyciele():
    return render_template("nauczyciele.html",nauczyciele=nauczyciele_l)

if __name__ == '__main__':
    app.run(debug=True)
