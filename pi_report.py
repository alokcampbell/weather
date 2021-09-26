import os
import json
import gspread
import requests
from time import time, ctime
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# config
healthcheck_url = ''
WEATHERAPI_KEY = ''

# log that the script has been run
try:
    requests.get(healthcheck_url + "/start", timeout=5)
except requests.exceptions.RequestException:
    # If the network request fails for any reason, we don't want
    # it to prevent the main job from running
    pass


# json credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
gc = gspread.authorize(credentials)

sheet = gc.open_by_key('').worksheet('Sheet2')
print(sheet.url)
# next available row function
def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)

def bytesToMbps(input):
    return round((int(input) * 8) / 1000000)

def kTof(kelvin=int()):
    """ KELVIN TO FAHREN. """
    return round((1.8*kelvin)-459.67)

# run speedtest and store output
cmd = 'speedtest --accept-license -f json -s 5309 > speedtest.json'
os.system(cmd)

with open('speedtest.json') as f:
    test = json.load(f)

# runs open weather api



api_address = 'https://api.openweathermap.org/data/2.5/forecast'
# ?lat={lat}&lon={lon}&appid=

params = {
    'lat': '',
    'lon': '',
    'appid': WEATHERAPI_KEY
}

r = requests.get(api_address, params=params)

weatherdata = json.loads(r.text)
print(weatherdata)

# time
now= datetime.now()
maintime = now.strftime("%-m/%-e %I:%M")
print(maintime)

# check if raining or snowing
if 'rain' in weatherdata['list'][0] and float(weatherdata['list'][0]['rain']) > 0.5:
    isRaining = True
else:
    isRaining = False

if 'snow' in weatherdata['list'][0] and float(weatherdata['list'][0]['snow']) > 0.5:
    isSnowing = True
else:
    isSnowing = False

# update the sheet
next_row = next_available_row(sheet)
sheet.update_acell("A{}".format(next_row), maintime)
sheet.update_acell("B{}".format(next_row), bytesToMbps(test['download']['bandwidth']))
sheet.update_acell("C{}".format(next_row), bytesToMbps(test['upload']['bandwidth']))
sheet.update_acell("D{}".format(next_row), kTof(weatherdata['list'][0]['main']['temp']))
sheet.update_acell("E{}".format(next_row), weatherdata['list'][0]['weather'][0]['main'])
sheet.update_acell("F{}".format(next_row), weatherdata['list'][0]['weather'][0]['description'])
sheet.update_acell("G{}".format(next_row), isRaining)
sheet.update_acell("H{}".format(next_row), isSnowing)

# done!
requests.get(healthcheck_url)
