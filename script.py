from flask import Flask, render_template, make_response, request
from datetime import datetime, timedelta
from zast2 import *
app = Flask(__name__)

@app.route('/')
def index():
    cookie = request.cookies.get('klasa')
    return render_template('index.html', klasa=cookie)

@app.route('/home')
def home():
    resp = make_response(render_template("main.html", klasa="None"))
    resp.delete_cookie('klasa')
    return resp

@app.route('/main')
def main():
    cookie = request.cookies.get('klasa')
    return render_template("main.html", klasa=cookie)

@app.route('/plan/<klasa>')
def plan(klasa):
    if klasa == "None":
        return "<h1>Wybierz Klasę lub Nauczyciela</h1>"
    kol = ["Nr", "Godz", "Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek"]
    numery = ['1', '2', '3', '4']
    tytul = klasa
    plan, zast = zast_and_plan(klasa)
    plan_tab = (plan, kol)
    output = render_template('plan.html', plan_tab=plan_tab, zast=zast, klasa=tytul)
    resp = make_response(output)
    expire_date = datetime.now() + timedelta(days=90)
    resp.set_cookie('klasa', klasa, expires=expire_date)
    return resp

@app.route('/buttons')
def buttons():
    przyciski = pobierz_przyciski()
    przyciski = zrub_przyciski(przyciski)
    klasy = []
    last = 1
    nauczyciele = []
    nauczyciele_schowel = [{}, {}, {}]
    schowek = {}
    for i, cell in enumerate(przyciski[0]):
        if last < int(cell[0]):
            klasy.append(schowek)
            schowek = {}
            last = int(cell[0])
        schowek[cell] = przyciski[0][cell]
    klasy.append(schowek)
    schowek = {}
    for i, cell in enumerate(przyciski[1]):
        nauczyciele_schowel[i % 3][cell] = przyciski[1][cell]
    nauczyciele = nauczyciele_schowel
    return render_template("przyciski.html", klasy=klasy, nauczyciele=nauczyciele, ind=[przyciski[2]])

@app.route('/wiadomosci')
def formularz():
    return render_template('wiadomosci.html')


if __name__ == '__main__':
    app.run(debug=True)
