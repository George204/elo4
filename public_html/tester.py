import requests
from zast2 import pobierz_przyciski, zrub_przyciski
przyciski = zrub_przyciski(pobierz_przyciski())
mego = {}
for i in przyciski:
    mego.update(i)
for i in mego:
    url = f"https://elo4.pl/plan/{i}%20{mego[i]}"
    re = requests.get(url)
    print(i,end=" ")
    print(mego[i], end=" ")
    if re.ok:
        print("\033[32mok",end=" ")
    else:
        for i in range(20):
            print("\033[31mporzażka!!!!!!!",end=" ")
    print(re.status_code,"\033[0m")
