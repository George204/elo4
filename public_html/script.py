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
    numery = ['1','2','3','4']
    tytul = klasa
    if tytul[0] not in numery:
        tytul = 'p.'+tytul
    plan, zast = zast_and_plan(klasa)
    plan_tab = (plan,kol)
    output = render_template('plan.html',plan_tab=plan_tab,zast=zast,klasa=tytul)
    resp = make_response(output)
    expire_date =  datetime.now() + timedelta(days=90)
    resp.set_cookie('klasa', klasa, expires = expire_date)  
    return resp

@app.route('/buttons')
def buttons():
    return render_template("buttons.html",klasy_v=klasy_v)

@app.route('/nauczyciele')
def nauczyciele():
    columna = 0
    col = [[],[],[]]
    for i in sorted(nauczyciele_l):
        col[columna].append(i)
        columna+=1
        if columna > 2:
            columna =0
    return render_template("nauczyciele.html",col=col)

if __name__ == '__main__':
    app.run(debug=True)
