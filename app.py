from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin


app = Flask(__name__)
CORS(app)

db = SQLAlchemy(app)

app.secret_key = 'my secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://chloe:123@localhost:5432/typeracer'

migrate = Migrate(app,db)

class User(UserMixin, db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)

class Score(db.Model):
    __tablename__='scores'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    excerpt_id = db.Column(db.Integer, db.ForeignKey('excerpts.id')) ## foreignkey
    time = db.Column(db.Integer)
    wpm = db.Column(db.Integer)
    error = db.Column(db.Integer)

class Excerpt(db.Model):
    __tablename__='excerpts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    ## relationship here
    scores = db.relationship('Score', backref='excerpt', lazy=True)
    

db.create_all()
 
@app.route('/')
def root():
    return jsonify(['Hello', 'World'])


@app.route('/scores', methods = ['GET', 'POST'])
def create_score():
    if request.method == 'POST':
        score=Score(user_id = 1,
                    excerpt_id = 1,
                    time = request.get_json()['time'],
                    wpm = request.get_json()['wpm'],
                    error = request.get_json()['errorCount'])
        db.session.add(score)
        db.session.commit()
        excerpt = Excerpt.query.filter_by(id=1).first()
        scores = Score.query.filter_by(excerpt_id=1).order_by(Score.wpm.desc()).limit(3)
        count = Score.query.filter_by(excerpt_id=1).count()
        print(scores)
        res = {
            "excerpt":{
                "id":excerpt.id,
                "body": excerpt.body,
                "scores":{
                    "top":[{ 'id': score.id, 
                        'time': score.time,
                        'wpm': score.wpm,
                        'error': score.error                   
                        } for score in scores],
                    "count": count
                }
            }
        }
        return jsonify(res)

@app.route('/excerpts')
def list():
    excerpts = Excerpt.query.all() ## a list of class Excerpt
    # translate the classes into dictionaries (object in javascript)
    response = { "data": [ {"id":excerpt.id,
                            "body": excerpt.body} for excerpt in excerpts]}
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True, ssl_context='adhoc')