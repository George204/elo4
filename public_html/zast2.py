from dict import *
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import asyncio
def plan_lekcji(res_content):
    soup = BeautifulSoup(res_content, 'html.parser')
    table = soup.find('table', {"class": "tabela"})
    rows = table.find_all('tr')
    plan = []
    for row in rows[1:]:
        cells = row.find_all('td')
        rowex = []
        for cell in cells:
            cell_text = " ".join(cell.stripped_strings)
            rowex.append(cell_text)
        plan.append(rowex)
    return plan

def zast_wszys(res_text):
    soup = BeautifulSoup(res_text, 'html.parser')
    tables = soup.find_all('table')
    for i, table in enumerate(tables, 1):
        table_data = []
        rows = table.find_all('tr')
        for row in rows:
            row_data = []
            cells = row.find_all(['td', 'th'])
            if len(cells) != 1:
                cells.pop(0)
            for cell in cells:
                cell_text = cell.get_text(strip=True)
                row_data.append(cell_text)
            if row_data != ['','','',''] and row_data != ['',]:
                table_data.append(row_data)
        return table_data

def zastepstwa_2(klasa,res_text):
    klasa_tabela = []
    tabela = zast_wszys(res_text)
    nauczy = ""
    for row in tabela:
        if len(row) > 1 and len(row[1]) > 1 and len(row[1])<4 :
            if row[1] == klasa or row[1][:2] == klasa or row[1][0]+row[1][-1] == klasa:
                if len(row[2]) == 3 or len(row[2]) == 2:
                    if row[2][1] == 'j' or row[2][0] == 'N':
                        row[2] = nauczy
                klasa_tabela.append(row)
        elif len(row) == 1:
            if row[0][0] == 'p':
                nauczy = row[0]
    return klasa_tabela

async def pobierz(dates, klasa, plan_l):
    loop = asyncio.get_event_loop()
    url1 = 'http://www.lo4.poznan.pl/zast/z2.php?plik=http%3A%2F%2Fswojska.lo4.poznan.pl%2Fzast%2F'
    url2 = '.xls'
    url = f"http://www.lo4.poznan.pl/plan/plan/plany/{klasy[klasa]}.html"
    future1 = loop.run_in_executor(None, requests.get, url1+dates[0]+url2) 
    future2 = loop.run_in_executor(None, requests.get, url1+dates[1]+url2)
    future3 = loop.run_in_executor(None, requests.get, url1+dates[2]+url2)
    future4 = loop.run_in_executor(None, requests.get, url1+dates[3]+url2)
    future5 = loop.run_in_executor(None, requests.get, url1+dates[4]+url2)
    future6 = loop.run_in_executor(None, requests.get, url)
    responese1 = await future1
    responese2 = await future2
    responese3 = await future3
    responese4 = await future4
    responese5 = await future5
    responese6 = await future6
    plan_l.append(responese6.content)
    dates[0] = responese1
    dates[1] = responese2
    dates[2] = responese3
    dates[3] = responese4
    dates[4] = responese5

def num_to_day(day):
    days = {
        0:"Poniedziałek",
        1:"Wtorek",
        2:"Środa",
        3:"Czwartek",
        4:"Piątek"
    }
    return days[day]

def zast_and_plan(klasa):
    dziś = datetime.now() 
    zastempstaw = []
    dates = ["","","","",""]
    plan_l = []
    for i in range(7):
        data = dziś + timedelta(days=i)
        if data.weekday() < 5:
            dates[data.weekday()] = data.strftime("%y%m%d")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop) 
    loop.run_until_complete(pobierz(dates, klasa, plan_l))
    for i, day in enumerate(dates):
        if day.content[-8::] != b'readable':
            dates[i] = zastepstwa_2(klasa, day.text)
        else:
            dates[i] = "None"
    plan = plan_lekcji(plan_l[0])
    for i, day in enumerate(dates):
        if day != "None":
            for lekcja in day:
                grupa = ''
                if lekcja[2] != '':
                    grupa = "grupa:" + lekcja[2] + ' '
                if lekcja[0] != '':
                    ststst = ""
                    if plan[int(lekcja[0])-1][i+2] != '':
                        ststst = " "
                    plan[int(lekcja[0])-1][i+2] = plan[int(lekcja[0])-1][i+2] + ststst + "{"+ grupa + lekcja[3] + "}"
                else:
                    lekcja[0] = num_to_day(i)
                    zastempstaw.append(lekcja)
    return plan, zastempstaw  
