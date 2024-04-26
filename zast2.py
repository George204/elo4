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

def zastempstwa_u(klasa,res_text):
    klasa_tabela = []
    tabela = zast_wszys(res_text)
    nauczy = ""
    klasa = klasa.upper()
    for row in tabela:
        if len(row) > 1 and len(row[1]) > 1 and len(row[1])<4 :
            if row[1] == klasa or row[1][:2] == klasa or row[1][0]+row[1][-1] == klasa:
                if len(row[2]) == 3 or len(row[2]) == 2:
                    if row[2][1] == 'j' or row[2][0] == 'N':
                        row[2] = nauczy
                if row[2] != '':
                    row[2] = "grupa: " + row[2] + " "
                klasa_tabela.append(row)
        elif len(row) == 1:
            if row[0][0] == 'p':
                nauczy = row[0]
    return klasa_tabela

def zastempstwa_n(klasa,res_text):
    klasa = klasa.split(".")[1]
    klasa_tabela = []
    tabela = zast_wszys(res_text)
    for row in tabela:
        if len(row) > 1 and klasa in row[3]:
            if row[2] != '':
                row[2] = "grupa: " + row[2] + " "
            if row[1] != '':
                row[2] = "klasa: " + row[1] + " " + row[2]
            klasa_tabela.append(row)
    return klasa_tabela

def zastempstwa_i(klasa,res_text):
    klasa_tabela = []
    tabela = zast_wszys(res_text)
    klasa = klasa.upper()
    for row in tabela:
        if len(row) > 1 and len(row[1]) > 1 and len(row[1])>3 :
            if row[1] == klasa:
                if row[2] != '':
                    row[2] = "grupa: " + row[2] + " "
                klasa_tabela.append(row)
    return klasa_tabela

async def pobierz(dates, numerek, plan_l):
    loop = asyncio.get_event_loop()
    url1 = 'http://www.lo4.poznan.pl/zast/z2.php?plik=http%3A%2F%2Fswojska.lo4.poznan.pl%2Fzast%2F'
    url2 = '.xls'
    url = f"http://www.lo4.poznan.pl/plan/plan/plany/{numerek}.html"
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

def pobierz_przyciski():
    url = f"http://www.lo4.poznan.pl/plan/plan/lista.html"
    przyciski = requests.get(url)
    return przyciski.content
    
def zrub_przyciski(przyciski):
    output = []
    soup = BeautifulSoup(przyciski, 'html.parser')
    tables = soup.find_all('select')
    for i in tables:
        temp = {}
        for j in i.find_all('option', value=True):
            temp[j.get_text(strip=True)]=j['value']
        output.append(temp)   
    for i, tekst in enumerate(output[0]):
        output[0][tekst] = "o" + output[0][tekst] 
    swap = {}
    for i, tekst in enumerate(output[1]):
        swap[tekst.split(" ")[0]] = "n" + output[1][tekst]
    output[1] = swap
    
    output.pop(2)
    ind = {}
    for i, tekst in enumerate(output[0]):
        if len(tekst) > 4:
            ind[tekst] = output[0][tekst]
    swap = {}
    for tekst in ind:
        output[0].pop(tekst)
        swap[tekst.split(" ")[0]] = ind[tekst]
    ind = swap 
    output.append(ind)
    return output

def num_to_day(day):
    days = {
        0:"Poniedziałek",
        1:"Wtorek",
        2:"Środa",
        3:"Czwartek",
        4:"Piątek"
    }
    return days[day]

def zast_and_plan(tekst):
    klasa, numerek = tekst.split(" ")[0], tekst.split(" ")[1] 
    dziś = datetime.now() 
    zastempstaw = []
    dates = ["","","","",""]
    plan_l = []
    case = 0 
    if len(klasa) > 2:
        case = 2
    if numerek[0] == "n":
        case = 1

    for i in range(7):
        data = dziś + timedelta(days=i)
        if data.weekday() < 5:
            dates[data.weekday()] = data.strftime("%y%m%d")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop) 
    loop.run_until_complete(pobierz(dates, numerek, plan_l))

    for i, day in enumerate(dates):
        if day.content[-8::] != b'readable':
            if case == 0:
                dates[i] = zastempstwa_u(klasa, day.text)
            elif case == 1:
                dates[i] = zastempstwa_n(klasa, day.text)
            else:
                dates[i] = zastempstwa_i(klasa, day.text)
        else:
            dates[i] = "None"
    plan = plan_lekcji(plan_l[0])
    for row in plan:
        for i in range(len(row)):
            posss = ["",""]
            spacecount = 0
            for j in row[i]:
                if j == ' ':
                    spacecount += 1
                if spacecount > 2:
                    posss[1] += j
                else:
                    posss[0] += j
            row[i] = posss
    for i, day in enumerate(dates):
        if day != "None":
            for lekcja in day:
                if lekcja[0] != '' and int(lekcja[0]) > 0:
                    if len(plan)-1 < int(lekcja[0]):
                        for z in range(int(lekcja[0])-len(plan)):
                            plan.append([[f'{len(plan)+z+1}', ''],['', ''],['', ''],['', ''],['', ''],['', ''],['', '']])
                    plan[int(lekcja[0])-1][i+2].append("{" + lekcja[2] + lekcja[3] + "}")
                else:
                    if lekcja[0] != '':
                        lekcja[0] = 'Lekcja: ' + lekcja[0]+ ' '
                    lekcja[0] += 'Dzień: ' + num_to_day(i)
                    zastempstaw.append(lekcja)
    return plan, zastempstaw  
