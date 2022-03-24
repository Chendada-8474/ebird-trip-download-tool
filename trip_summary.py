import requests
import json
import pandas as pd
from tqdm import tqdm
from datetime import datetime

try:
  TRIP_ID = input("your trip report ID: ")
  EBIRD_TOKEN = input("your eBird token: ")

  s = requests.Session()
  cookies = dict(I18N_LANGUAGE='zh')

  trips_path = 'https://ebird.org/tripreport-internal/v1/checklists/'
  checklist_path = 'https://api.ebird.org/v2/product/checklist/view/'

  payload={}
  headers = {'X-eBirdApiToken': EBIRD_TOKEN}

  checklists = requests.request("GET", trips_path + TRIP_ID, headers=headers, data=payload)
  checklists = checklists.json()

  with open('./breeding_code.json', encoding="utf-8") as f:
    breeding_codes = json.load(f)

  with open('./sp_info.json', encoding="utf-8") as f:
    sp_info = json.load(f)



  pro_code = {
    "P20": "eBird - Casual Observation",
    "P21": "eBird - Stationary Count",
    "P22": "eBird - Traveling Count",
    "P23": "eBird - Exhaustive Area Count",
  }

except Exception as e:
  print(e)
  input("input any key to exit: ")

def trip_download():
  print("start downloading...")
  trip_data = {
    "Submission ID": [],
    "Common Name": [],
    "Scientific Name": [],
    "Taxonomic Order": [],
    "Count": [],
    "State/Province": [],
    "County": [],
    "Location ID": [],
    "Location": [],
    "Latitude": [],
    "Longitude": [],
    "Date": [],
    "Time": [],
    "Protocol": [],
    "Duration (Min)": [],
    "All Obs Reported": [],
    "Distance Traveled (km)": [],
    "Area Covered (ha)": [],
    "Number of Observers": [],
    "Breeding Code": [],
    "Observation Details": [],
    "Checklist Comments": [],
    }

  for c in tqdm(checklists):
    ob = requests.request("GET", checklist_path + c["subId"], headers=headers, data=payload)
    ob = ob.json()

    ob_keys = tuple(ob.keys())

    for s in ob["obs"]:
      sp = sp_info[s["speciesCode"]]

      s_id = ob["subId"]
      c_name = sp["c_name"]
      s_name = sp["s_name"]
      t_order = sp["t_order"]
      count = s["howManyAtmost"]
      sta_pro = ob["subnational1Code"]
      l_id = ob["locId"]
      loc = c["loc"]["locName"]
      lat = c["loc"]["lat"]
      lon = c["loc"]["lng"]
      date = ob["obsDt"].split(" ")[0]
      time = ob["obsDt"].split(" ")[1]
      prot = pro_code[ob["protocolId"]]

      if "durationHrs" in ob_keys:
        dur = float(ob["durationHrs"])*60
      else:
        dur = None

      if ob["allObsReported"]:
        aor = 1
      else:
        aor = 0

      if "effortDistanceKm" in ob_keys:
        d_trav = ob["effortDistanceKm"]
      else:
        d_trav = None

      if "effortAreaHa" in ob_keys:
        a_cov = ob["effortAreaHa"]
      else:
        a_cov = None

      n_obser = ob["numObservers"]

      s_keys = tuple(s.keys())

      if "obsAux" in s_keys:
        b_code = breeding_codes[s["obsAux"][0]["auxCode"]]
      else:
        b_code = None

      if "comments" in s_keys:
        o_det = s["comments"]
      else:
        o_det = None

      if "comments" in ob_keys:
        c_comm = ob["comments"]
      else:
        c_comm = None

      trip_data['Submission ID'].append(s_id)
      trip_data['Common Name'].append(c_name)
      trip_data['Scientific Name'].append(s_name)
      trip_data['Taxonomic Order'].append(t_order)
      trip_data['Count'].append(count)
      trip_data['State/Province'].append(sta_pro)
      trip_data['County'].append(None)
      trip_data['Location ID'].append(l_id)
      trip_data['Location'].append(loc)
      trip_data['Latitude'].append(lat)
      trip_data['Longitude'].append(lon)
      trip_data['Date'].append(date)
      trip_data['Time'].append(time)
      trip_data['Protocol'].append(prot)
      trip_data['Duration (Min)'].append(dur)
      trip_data['All Obs Reported'].append(aor)
      trip_data['Distance Traveled (km)'].append(d_trav)
      trip_data['Area Covered (ha)'].append(a_cov)
      trip_data['Number of Observers'].append(n_obser)
      trip_data['Breeding Code'].append(b_code)
      trip_data['Observation Details'].append(o_det)
      trip_data['Checklist Comments'].append(c_comm)

  trip_data = pd.DataFrame(trip_data)
  time_now = datetime.strftime(datetime.now(), '%Y-%m-%d_%H%M')
  trip_data.to_csv("./trip_report_%s_%s.csv" % (TRIP_ID, time_now), index = False)

  print("Download successed!")
  input("input any key to exit: ")


try:
  trip_download()

except Exception as e:
  print(e)
  input("input any key to exit: ")