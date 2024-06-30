from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'

db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_city = request.form.get('city')
        
        if new_city:
            new_city_obj = City(name=new_city)

            db.session.add(new_city_obj)
            db.session.commit()

    cities = City.query.order_by(City.id.desc()).all()  # Order cities by ID descending

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=ae1a65c0f151a20f9fc55044a780552a'

    weather_data = []

    for city in cities:
        try:
            r = requests.get(url.format(city.name)).json()

            # Check if city not found in API response
            if r.get('cod') != 200:
                #print(f"City '{city.name}' not found. Skipping...")
                continue

            weather = {
                'city': city.name,
                'temperature': r['main']['temp'],
                'description': r['weather'][0]['description'],
                'icon': r['weather'][0]['icon'],
            }

            weather_data.append(weather)
        except Exception as e:
            print(f"Error fetching weather for {city.name}: {str(e)}")

    return render_template('weather.html', weather_data=weather_data)

@app.route('/delete/<name>', methods=['POST'])
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    if city:
        db.session.delete(city)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return f"City {name} not found in the database."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
