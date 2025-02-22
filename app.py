from flask import Flask, render_template, request, redirect, url_for
import folium
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' # 3 fslash = relative path, 4 is absolute. We want this to reside in project location
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Task %r>' % self.id
    
    
@app.route('/')
def home():
    #Create map object
    mapObj = folium.Map(location=[43.099613, -89.5078801],
                     zoom_start=9, width=800, height=500)

    #add marker to map object
    folium.Marker([43.099613, -89.5078801], 
                  popup="<i>This is a marker</i>").add_to(mapObj)
    #render map obj
    mapObj.get_rcot().render()
    
    #derive script and style tags to be rendered in HTML head
    header = mapObj.get_root().header.render()

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)
        
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

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
    
    # try:
    #     db.session.update(task_to_update)
    #     db.session.commit()
    #     return redirect('/')

    # except:
    #     return 'Problem deleting that task.'

if __name__ == '__main__':
    app.run(debug=True)
