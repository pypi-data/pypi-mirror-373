import requests
class Weather:
    def __init__(self,apikey,city=None,lat=None,lon=None):
        if city:
            url=f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={apikey}"
            r=requests.get(url)
            self.data=r.json()
        elif lat and lon:
            url=f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={apikey}"
            r = requests.get(url)
            self.data = r.json()
        else:
            raise TypeError("provide city or lat and lon values")
        if self.data['cod']!="200":
            raise ValueError(self.data['message'])

    def next_12h(self):
        return self.data['list'][:4]


    def next_12h_simplified(self):
        simple_data=[]
        for dicty in self.data['list'][:4]:
            simple_data.append((dicty['dt_txt'],dicty['main']['temp'],dicty['weather'][0]['description']))
        return simple_data

