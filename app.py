from flask import Flask, render_template, request, redirect, url_for, render_template_string
import folium
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' # 3 fslash = relative path, 4 is absolute. We want this to reside in project location
db = SQLAlchemy(app)

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

        time_str = request.form['startTime']
        event_startTime = datetime.strptime(time_str, '%H:%M')
        
        time_str = request.form['endTime']
        event_endTime = datetime.strptime(time_str, '%H:%M')

        new_event = Event(name=event_name, location=event_location, startTime=event_startTime, endTime = event_endTime)
        
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
    task_to_delete = Todo.query.get_or_404(id)
    
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')

    except:
        return 'Problem deleting that task.'
    
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']
        
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "Couldn't update task."
    else:
        return render_template('update.html', task=task)


@app.route('/map')
def map():
    #Create map object
    mapObj = folium.Map(location=[43.099613, -89.5078801],
                     zoom_start=9, width=800, height=500)

    #add marker to map object
    folium.Marker([43.099613, -89.5078801], 
                  popup="<i>This is a marker</i>").add_to(mapObj)
    #render map obj
    mapObj.get_root().render()
    
    #derive script and style tags to be rendered in HTML head
    header = mapObj.get_root().header.render()

    #derive the div container to be rendered in the HTML body
    body_html = mapObj.get_root().html.render()

    #save as HTML file
    mapObj.save("./templates/output.html")

    return render_template("output.html")

@app.route('/study_spots')
def study_spots():
    #use backend func to get list of libraries 
    return render_template('study_spots.html')

@app.route('/food_spots')
def food_spots():
    #use backend func to get list of restaurants  
    return render_template('food_spots.html')

if __name__ == '__main__':
    app.run(debug=True)
