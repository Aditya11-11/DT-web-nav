from flask import *
import requests
import datetime

timestamp = 1726636384

dt_object = datetime.datetime.utcfromtimestamp(timestamp)

# print(dt_object.strftime("%Y-%m-%d %H:%M:%S"))
apikey = '9b84156024a1157f9ceaf83477c026d7'
_chatbot = '''
 <div class="chatbot-frame">
        
        <div class="chatbot">
            <div class="chatbot-head">Voice Assistant</div>
            <div class="chatbot-display" id="display">
                <div class="chatbot-chatbar">
                    <div class="chatbot-chat chatbot-bot">Hello. How can I assist you today?</div>
                </div>
            </div>
            <div class="chatbot-controls">
                <div class="center">
                    <input type="text" name="" id="prompt">
                </div>
                <div class="center">
                    <button id="voice">▶️</button>
                    
                </div>
                <div class="center">
                    <button id="send">✅</button>
                    
                </div>
                
            </div>
        </div>
        <div class="toggle-btn"><button id="toggle-btn">T</button></div>
    </div>
'''
class Weather:

    def check(self,item):
        if item:
            return f',{item}'
        return ''
    
    def presencechecker(self,a,value):
        try:
            return a[value]
        except:
            return 'not avaliable'

    
    def getweatherdata(self,city_name):
        api = f'http://api.openweathermap.org/geo/1.0/direct?q={city_name},IN&appid={apikey}'
        print(api)
        try:
            response = requests.get(api)
            data = response.json()
            # print(data)
            lat = data[0]['lat']
            lon = data[0]['lon']
        except requests.exceptions.RequestException as e:
            return f'error: {e}'
        try:
            response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={apikey}')
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            return f'error: {e}'



app = Flask(__name__)

obj = Weather()

@app.route('/') 
def home():
    return render_template('index.html',chatbot =_chatbot)

@app.route('/customer') 
def customer():
    return render_template('customer.html',chatbot =_chatbot)

@app.route('/location') 
def location():
    return render_template('location.html',chatbot =_chatbot)

@app.route('/opportunities')
def opportunities():
    return render_template('opportunities.html',chatbot =_chatbot)

@app.route('/dispatch')
def dispatch():
    return render_template('dispatch.html',chatbot =_chatbot)

@app.route('/tracking')
def tracking():
    return render_template('tracking.html',chatbot =_chatbot)

@app.route('/settings')
def settings():
    return render_template('settings.html',chatbot =_chatbot)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        city = request.form.get('city_name')
        # country_code = request.form.get('city_name')
        
        data = obj.getweatherdata(city_name=city)
        
        dt  = obj.presencechecker( data,'dt')
        dt_object = datetime.datetime.utcfromtimestamp(dt)
        dt = dt_object.strftime("%Y-%m-%d %H:%M:%S")

        sunrise  = obj.presencechecker( data['sys'],'sunrise')
        dt_object = datetime.datetime.utcfromtimestamp(sunrise)
        sunrise = dt_object.strftime("%Y-%m-%d %H:%M:%S")

        sunset  = obj.presencechecker( data['sys'],'sunset')
        dt_object = datetime.datetime.utcfromtimestamp(sunset)
        sunset = dt_object.strftime("%Y-%m-%d %H:%M:%S")

        return render_template('location.html',
                            longitude = obj.presencechecker( data['coord'],'lon'),
                            latitude = obj.presencechecker( data['coord'],'lat'),
                            main = obj.presencechecker( data['weather'][0],'main').upper(),
                            description = obj.presencechecker( data['weather'][0],'description'),
                            icon = obj.presencechecker( data['weather'][0],'icon'),
                            temp  = obj.presencechecker( data['main'],'temp'),
                            feels_like  = obj.presencechecker( data['main'],'feels_like'),
                            temp_min  = obj.presencechecker( data['main'],'temp_min'),
                            temp_max  = obj.presencechecker( data['main'],'temp_max'),
                            pressure  = obj.presencechecker( data['main'],'pressure'),
                            humidity  = obj.presencechecker( data['main'],'humidity'),
                            sea_level  = obj.presencechecker( data['main'],'sea_level'),
                            grnd_level  = obj.presencechecker( data['main'],'grnd_level'),
                            visibility  = obj.presencechecker( data,'visibility'),
                            speed  = obj.presencechecker( data['wind'],'speed'),
                            deg  = obj.presencechecker( data['wind'],'deg'),
                            gust  = obj.presencechecker( data['wind'],'gust'),
                            rain  = obj.presencechecker( obj.presencechecker(data,'rain'),'1h'),
                            clouds  = obj.presencechecker( data['clouds'],'all'),
                            country  = obj.presencechecker( data['sys'],'country'),
                            dt  = dt,
                            sunrise  = sunrise,
                            sunset  = sunset,
                            cityname  = obj.presencechecker( data,'name').upper(),
                               )

if __name__ == '__main__':
    app.run(debug=True)