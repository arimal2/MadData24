from flask import Flask, render_template, request, redirect, url_for, render_template_string
import folium
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from backend.generatePaths import GeneratePaths

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
        event_name = request.form['name'] #get event name from user input
        event_location = request.form['location']

        start_str = request.form['startTime'] #get event start time from user input
        event_startTime = datetime.strptime(start_str, '%H:%M')
        
        end_str = request.form['endTime'] #get event end time from user input
        
        if start_str > end_str:
            return "start time cannot be after end time" #start/end time violation 
        
        event_endTime = datetime.strptime(end_str, '%H:%M')
        
        events = Event.query.order_by(Event.startTime).all()
        new_event = Event(name=event_name, location=event_location, startTime=event_startTime, endTime = event_endTime)

        if (len(events) > 0):
            if events[len(events) - 1].endTime > new_event.startTime:
                return "Start time conflicts with previous end time" #start/end time violation 
            
        try:
            #add new event, and return to home page
            db.session.add(new_event)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your event.' 
    else:
        events = Event.query.order_by(Event.startTime).all()
        return render_template('index.html', events=events) #return to home page


@app.route('/delete/<int:id>')
def delete(id):
    event_to_delete = Event.query.get_or_404(id)
    
    try:
        #delete event and return to home page
        db.session.delete(event_to_delete)
        db.session.commit()
        return redirect('/')

    except:
        return 'Problem deleting that event.'
    
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    event = Event.query.get_or_404(id) #get event associated with id 

    #if form submission was successful
    if request.method == 'POST': 
        
        if (request.form['name'] != ""):
            event.name = request.form['name'] #if new name is not empty string, update event name

        if (request.form['location'] != ""):
            event.location = request.form['location'] #if new location is not empty string, update event location
        
        time_str = request.form['startTime']
        if (time_str != ""):
            event.startTime = datetime.strptime(time_str, '%H:%M') #if new start time is not empty string, update event start time
        
        time_str = request.form['endTime']
        if (time_str != ""):
            event.endTime = datetime.strptime(time_str, '%H:%M') #if new end time is not empty string, update event end time

        try:
            #update event, and return to home page 
            db.session.commit()
            return redirect('/')
        except:
            return "Couldn't update event." #Error updating event 
        
    #otherwise, if form submission was unsuccessful 
    else:
        return render_template('update.html', event=event)

@app.route('/map', methods=["GET", "POST"])
def map():
    if request.method == "POST": 
        checked = request.form.getlist("checked") #get checked locations from user submission 

        #Create map object
        mapObj = folium.Map(location=[43.0757, -89.4040],
                        zoom_start=15, width=800, height=500)

        #for each location add a marker to map object 
        for check in checked: 
            coords = backend.getCoords(check)
            name = check
            folium.Marker(coords, 
                        popup=name).add_to(mapObj)
        #render map object 
        mapObj.get_root().render()
        
        #derive script and style tags to be rendered in HTML head
        header = mapObj.get_root().header.render()

        #derive the div container to be rendered in the HTML body
        body_html = mapObj.get_root().html.render()

        #save as HTML file
        mapObj.save("./templates/output.html")

        return render_template("output.html")
    
    else:
        return "Sorry, you have to check something"
    

@app.route('/study_spots/<int:id>')
def study_spots(id):
    #use backend func to get list of libraries 
    events = Event.query.order_by(Event.startTime).all()
    index = events.index(Event.query.get_or_404(id))

    #if last class, return 
    if index == len(events) - 1: 
        return "Go anywhere: the world is your oyster"
    
    #otherwise, generate list of study spots 
    else: 
        temp = backend.generateNearByDict(events[index].location, events[index + 1].location, "library", 500) #500m = 7 min walk
        locations=list(temp.keys())

        #go to page with list of places to study
        return render_template('study_spots.html', locations=locations)

@app.route('/food_spots/<int:id>')
def food_spots(id):

    #use backend func to get list of restaurants  
    events = Event.query.order_by(Event.startTime).all()
    index = events.index(Event.query.get_or_404(id))

    #if last class, return 
    if index == len(events) - 1: 
        return "Go anywhere: the world is your oyster"
    
    #otherwise, generate list of food spots
    else: 
        temp = backend.generateNearByDict(events[index].location, events[index + 1].location, "restaurant", 500) #500m = 7 min walk
        locations=list(temp.keys())

        #go to page with list of places to get food
        return render_template('food_spots.html', locations=locations)

if __name__ == '__main__':
    app.run(debug=True)
