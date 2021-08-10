import requests
import json
from urllib.parse import urlencode
import pandas as pd
import time

class GooglePlaces:
	def __init__(self, list_kelurahan, kecamatan, kota, api_key):
		self.list_kelurahan = list_kelurahan
		self.kecamatan = kecamatan
		self.kota = kota
		self.api_key = api_key
		self.radius = 2000
		self.count = 1

	def start(self):
		df_kelurahan = self.extract_lat_lng()
		for self.nama_kelurahan, self.latitude_kelurahan, self.longitude_kelurahan in zip(df_kelurahan.Kelurahan, df_kelurahan.Latitude, df_kelurahan.Longitude):
			types = ['cafe', 'restaurant', 'bus_station', 'parking', 'train_station']
			for type in types:
				print(type)
				params = {
					"location": f"{self.latitude_kelurahan},{self.longitude_kelurahan}",
					"radius": self.radius,
					"type": type,
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
		result = self.request_data(params, type_search="nearbysearch", sleep=8)
		for data in result['results']:
			name = data['name']
			vicinity = data['vicinity']
			types = [type for type in data['types']]
			location = [data['geometry']['location'][loc] for loc in data['geometry']['location']]
			lat = location[0]
			lng = location[1]
			print(f"{self.count}. {self.nama_kelurahan} {name} {lat}, {lng}")
			self.count+=1

		print(page)
		if(page==2):
			print("##################### Selesai")
		else:
			page+=1
			next_page_token = result['next_page_token']
			params ={
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

api_key = 'xxxxxx' # api key
list_kelurahan= ['Tanjung Barat', 'Jagakarsa', 'Cipedak', 'Lenteng Agung', 'Srengseng Sawah', 'Ciganjur']
kecamatan = 'Jagakarsa'
kota = "Jakarta Selatan"

model = GooglePlaces(list_kelurahan, kecamatan, kota, api_key)
model.start()
