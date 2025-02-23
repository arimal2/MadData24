from flask import Flask, render_template, request, redirect, url_for, render_template_string
import folium
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from backend.generatePaths import GeneratePaths
from dotenv import load_dotenv
import logging

#  app.logger.debug(f"{var}")  # Debugging line

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' # 3 fslash = relative path, 4 is absolute. We want this to reside in project location
db = SQLAlchemy(app)

backend = GeneratePaths()

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    startTime = db.Column(db.DateTime)
    endTime = db.Column(db.DateTime)
    location = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return '<Event %r>' % self.id

# to add an event to the schedule
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        event_name = request.form['name']
        event_location = request.form['location']

        start_str = request.form['startTime']
        event_startTime = datetime.strptime(start_str, '%H:%M')
        
        end_str = request.form['endTime']
        
        if start_str > end_str:
            return "start time cannot be after end time"
        
        event_endTime = datetime.strptime(end_str, '%H:%M')
        
        events = Event.query.order_by(Event.startTime).all()
        new_event = Event(name=event_name, location=event_location, startTime=event_startTime, endTime = event_endTime)

        if (len(events) > 0):
            if events[len(events) - 1].endTime > new_event.startTime:
                return "Start time conflicts with previous end time"
            
        try:
            db.session.add(new_event)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your event.'
    else:
        events = Event.query.order_by(Event.startTime).all()
        return render_template('index.html', events=events)

@app.route('/delete/<int:id>')
def delete(id):
    event_to_delete = Event.query.get_or_404(id)
    
    try:
        db.session.delete(event_to_delete)
        db.session.commit()
        return redirect('/')

    except:
        return 'Problem deleting that event.'
    
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    event = Event.query.get_or_404(id)

    if request.method == 'POST':
        
        if (request.form['name'] != ""):
            event.name = request.form['name']
        event.location = request.form['location']

        if (request.form['name'] != ""):
            time_str = request.form['startTime']
        
        if (time_str != ""):
            event.startTime = datetime.strptime(time_str, '%H:%M')
        
        time_str = request.form['endTime']
        
        if (time_str != ""):
            event.endTime = datetime.strptime(time_str, '%H:%M')

        try:
            db.session.commit()
            return redirect('/')
        except:
            return "Couldn't update event."
    else:
        return render_template('update.html', event=event)

@app.route('/map/<int:id>', methods=["GET", "POST"])
def map(id):
    addresses = []
    checked = []

    # getting start and end locations
    events = Event.query.order_by(Event.startTime).all()
    index = events.index(Event.query.get_or_404(id))
    start_location = events[index].location
    end_location = events[index + 1].location

    if request.method == "POST": 
        
        checkedAll = request.form.getlist("checked")
        checked.append(start_location)
        addresses.append(start_location)

        app.logger.debug(f"{checkedAll}")

        for item in checkedAll:
            location, address = item.split(' - ')
            checked.append(location)
            addresses.append(address)
        checked.append(end_location)
        addresses.append(end_location)


        #Create map object
        mapObj = folium.Map(location=[43.0757, -89.4040],
                        zoom_start=15, width=800, height=500)
        
        waypoints = []

        #for each location add a marker to map object 
        for check in checked: 
            coords = backend.getCoords(check)
            name = check
            folium.Marker(coords, 
                        popup=name).add_to(mapObj)
            waypoints.append(coords)

        shortestPath = backend.getShortestPath(addresses)

        for index, route in enumerate(shortestPath):
            color = "red" if index % 2 == 0 else "black"
            folium.PolyLine(route, color=color, weight=5, opacity=0.7).add_to(mapObj)

        # render map obj
        mapObj.get_root().render()
        
        #derive script and style tags to be rendered in HTML head
        header = mapObj.get_root().header.render()

        # derive the div container to be rendered in the HTML body
        body_html = mapObj.get_root().html.render()

        # save as HTML file
        mapObj.save("./templates/output.html")

        return render_template("output.html")
    
    else:
        return "Sorry, you have to check something"
    
@app.route('/study_spots/<int:id>')
def study_spots(id):
    # use backend func to get list of libraries 
    events = Event.query.order_by(Event.startTime).all()

    index = events.index(Event.query.get_or_404(id))

    if index == len(events) - 1: 
        return "Go anywhere: the world is your oyster"
    
    else: 
        locations = backend.generateNearByDict(events[index].location, events[index + 1].location, "library", 500) #500m = 7 min walk

        return render_template('study_spots.html', locations=locations, id=id)

@app.route('/food_spots/<int:id>')
def food_spots(id):

    # use backend func to get list of restaurants  
    events = Event.query.order_by(Event.startTime).all()
    index = events.index(Event.query.get_or_404(id))

    # if event is last in schedule 
    if index == len(events) - 1: 
        return "Go anywhere: the world is your oyster"
    
    else: 
        locations = backend.generateNearByDict(events[index].location, events[index + 1].location, "restaurant", 500) #500m = 7 min walk
        

    return render_template('food_spots.html', locations=locations, id=id)

if __name__ == '__main__':
    app.run(debug=True)
