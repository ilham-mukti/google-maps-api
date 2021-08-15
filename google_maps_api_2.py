import time
import json
import requests
import pandas as pd
from urllib.parse import urlencode

class GooglePlaces:
	def __init__(self, path, list_kelurahan, kecamatan, kota, api_key):
		self.list_kelurahan = list_kelurahan
		self.kecamatan = kecamatan
		self.kota = kota
		self.api_key = api_key
		self.radius = 2000
		self.count = 1
		self.path = path

	def start(self):
		df_kelurahan = self.extract_lat_lng()
		for self.nama_kelurahan, self.latitude_kelurahan, self.longitude_kelurahan in zip(df_kelurahan.Kelurahan, df_kelurahan.Latitude, df_kelurahan.Longitude):
			types = ['cafe', 'restaurant']
			for self.type in types:
				print(type)
				params = {
					"location": f"{self.latitude_kelurahan},{self.longitude_kelurahan}",
					"radius": self.radius,
					"type": self.type,
					"key": self.api_key,
					"rankby": "prominence"
				}
				self.parse_places(params)

	def extract_lat_lng(self):
		lat_kelurahan, lng_kelurahan = [], []
		for kelurahan in self.list_kelurahan:
			address = f"{kelurahan},{self.kecamatan},{self.kota}"
			params = {'address': address, 'key': self.api_key}
			result = self.request_data(params)
			lat = result['results'][0]['geometry']['location']['lat']
			lng = result['results'][0]['geometry']['location']['lng']
			lat_kelurahan.append(lat)
			lng_kelurahan.append(lng)

		df_kelurahan = pd.DataFrame({"Kelurahan": self.list_kelurahan, "Latitude": lat_kelurahan, "Longitude": lng_kelurahan})
		return df_kelurahan

	def parse_places(self, params, page=0):
    	my_dict = {'nama_kelurahan': [], 'nama_tempat': [], 'type_tempat': [], 'rating': [], 'user_ratings_total': []}
		result = self.request_data(params, type_search="nearbysearch", sleep=8)
		for data in result['results']:
			name = data['name']
			vicinity = data['vicinity']
      		rating = data['rating']
      		user_ratings_total = data['user_ratings_total']
			types = [type for type in data['types']]
			location = [data['geometry']['location'][loc] for loc in data['geometry']['location']]
			lat = location[0]
			lng = location[1]
			print(f"{self.count}. {self.nama_kelurahan} {name} {lat}, {lng}")
			self.count+=1
    
			my_dict['nama_kelurahan'].append(self.nama_kelurahan)
			my_dict['nama_tempat'].append(name)
			my_dict['type_tempat'].append(self.type)
			my_dict['rating'].append(rating)
			my_dict['user_ratings_total'].append(user_ratings_total)


		print(page)
		if(page==2):
			print("##################### Selesai")
		else:
			page+=1
			next_page_token = result['next_page_token']
			params = {
				'pagetoken': next_page_token,
				'key': api_key
				}
			self.parse_places(params, page)

	def request_data(self, params, type_search='geocode', sleep=0):
		if type_search == 'nearbysearch':
			type_search = 'place/nearbysearch'
		params_encoded = urlencode(params)
		url = f"https://maps.googleapis.com/maps/api/{type_search}/json?{params_encoded}"
		result = requests.get(url, time.sleep(sleep)).json()
		return result

  	def save_to(self, dict_row):
	    path_output = self.path+ "kecamatan_" +self.kecamatan+".csv"
	    is_new = not os.path.isfile(path_output)
	    rows = zip(*dict_row.values())
	    modes = 'a'
	    if is_new:
			os.makedirs(os.path.dirname(path_output), exist_ok=True)
			modes = 'w'
	    with open(path_output, mode=modes, newline='', encoding='utf-8') as csv_file:
			writer = csv.writer(csv_file)
			if is_new:
				writer.writerow(dict_row.keys())
			for row in rows:
				writer.writerow(row)
            
api_key = 'xxxx' # Api Key
list_kelurahan= ['Tanjung Barat', 'Jagakarsa','Lenteng Agung']
kecamatan = 'Jagakarsa'
kota = "Jakarta Selatan"
path = "/content/scraping_kelurahan/"

model = GooglePlaces(path, list_kelurahan, kecamatan, kota, api_key)
model.start()
