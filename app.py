# FLASK_APP=flask-hello-app.py python3 -m flask run
# FLASK_APP=flask-hello-app.py FLASK_DEBUG=true python3 -m flask run

from os import error
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://yuhaolu@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

# db.create_all()

# add Todo items 
# @app.route('/todos/create', methods=['POST'])
# def create_todo():
#     description = request.form.get('description', '')
#     todo = Todo(description=description)
#     db.session.add(todo)
#     db.session.commit()
#     return redirect(url_for('index'))

# Create: add Todo items - AJAX 
@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        description = request.get_json()['description']
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort (400)
    else:
        return jsonify(body)

# Update: check Todo items
@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        # todo = Todo.query.filter_by(id=todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

# Delete: delete Todo items
@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        # todo = Todo.query.get(todo_id) 
        # db.session.delete(todo)
        print(Todo.query.filter_by(id=todo_id))
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({ 'success': True })

@app.route('/')
def index():
    # .order_by('id') to fix the list ordering when click refresh on the website
    return render_template('index.html', data=Todo.query.order_by('id').all())

if __name__ == '__main__':
    app.run()