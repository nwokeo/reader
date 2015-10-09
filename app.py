from flask import Flask, request, jsonify, render_template
from flask.ext.restless import APIManager
from flask.ext.sqlalchemy import SQLAlchemy
import ConfigParser
#from sqlalchemy import create_engine
import psycopg2
import os

config = ConfigParser.RawConfigParser()
config.read('reader.cfg')

#import cors
import collections
import json #diff b/w jsonify?
 
app = Flask(__name__)
 
#app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + \
                                        config.get('Database', 'username') + ':' + \
                                        config.get('Database', 'password') + '@' + \
                                        config.get('Database', 'host') + '/reader'
db = SQLAlchemy(app)


class FeedsLabels(db.Model):
    __tablename__ = 'feedslabels'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512))
    link = db.Column(db.String(255))
    #labels = db.Column(db.Text)
    description = db.Column(db.String(255))
    homepage = db.Column(db.Text)
    icon = db.Column(db.LargeBinary)
    unread_count = db.Column(db.Integer)
    add_date = db.Column(db.DateTime)
    active_flag = db.Column(db.Boolean)
    label = db.Column(db.String(255))
    #articles = db.relationship('Articles', backref='feeds', lazy='dynamic')


class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, db.ForeignKey('feedslabels.id'))
    link = db.Column(db.Text)
    title = db.Column(db.Text)
    content = db.Column(db.Text)
    viewed_flag = db.Column(db.Boolean)
    read_later_flag = db.Column(db.Boolean)
    add_date = db.Column(db.DateTime)
    update_date = db.Column(db.DateTime)
    rating_int = db.Column(db.Integer)
    rating_enum = db.Column(db.Text)


class Labels_v(db.Model):
    __tablename__ = 'labels_v'
    label = db.Column(db.String(255), primary_key=True)

db.create_all()

api_manager = APIManager(app, flask_sqlalchemy_db=db)
api_manager.create_api(FeedsLabels, methods=['GET', 'POST', 'DELETE', 'PUT'])  # , max_results_per_page=-1
api_manager.create_api(Articles, methods=['GET', 'POST', 'DELETE', 'PUT'])
api_manager.create_api(Labels_v, methods=['GET'])

@app.route('/client/')
def client():
    #print(request.args.get('id'))
    #a = request.args.get('a', 0, type=int)
    #b = request.args.get('b', 0, type=int)
    return render_template('client.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)

