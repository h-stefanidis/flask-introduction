from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

# Define the database model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return '<Task %r>' % self.id

# Define the routes
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method=='POST':
        task_content = request.form['content'].strip()        
        if not task_content:
            flash('Task content cannot be empty')
            return redirect('/')
        
        new_task = Todo(content=task_content)
        
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return flash('There was an issue adding your task')
        
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
        return 'There was a problem deleting that task'
    
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task_content = request.form['content'].strip()

        if not task_content:
            flash('Task content cannot be empty')
            return redirect(f'/update/{id}')
        
        task.content = task_content
        try:
            db.session.commit()
            return redirect('/')
        except:
            flash('There was an issue updating your task')
            return redirect(f'/update/{id}')
        
    else:
        return render_template('update.html', task=task)

# Create database tables and run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)