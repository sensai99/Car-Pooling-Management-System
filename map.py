# from flask import Flask,render_template
# import requests

# URL = "https://geocoder.api.here.com/6.2/geocode.json"
# # URL = "https://geocoder.ls.hereapi.com/6.2/geocode.json"
# location = input("Enter the location here: ")
# app_ID = 'kGYbB4SbpOzg5ghXVaaM'
# app_CODE = 'Pt65udBSns_bm0IivAvdfw'
# PARAMS = {'app_id':app_ID,'app_code':app_CODE,'searchtext':location} 

# print('hello')
# # sending get request and saving the response as response object 
# r = requests.get(url = URL, params = PARAMS) 
# data = r.json()

# print('hello.')
# latitude = data['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Latitude']
# longitude = data['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Longitude']

# print('lat', latitude, longitude)

# app = Flask(__name__)

# @app.route('/')

# def map_func():

#     print('yes')
#     return render_template('map.html',app_ID=app_ID,app_CODE=app_CODE,latitude=latitude,longitude=longitude)

# if __name__ == '__main__':
#     app.run(debug = False)


from flask import Flask,render_template
import requests

URL = "https://geocode.search.hereapi.com/v1/geocode"
location = input("Enter the location here: ") #taking user input
api_key = '3Z7958BKQnwVgrS2RvT_8ujlglfJ_YMQbAJC7RHC0DM' # Acquire from developer.here.com
PARAMS = {'apikey':api_key,'q':location} 

# sending get request and saving the response as response object 
r = requests.get(url = URL, params = PARAMS) 
data = r.json()

latitude = data['items'][0]['position']['lat']
longitude = data['items'][0]['position']['lng']

print(latitude, longitude)

app = Flask(__name__)

@app.route('/')
def map_func():
	return render_template('map.html', lati = latitude, longi = longitude)
if __name__ == '__main__':
    app.run(debug = True)    