#dependencies go here
import numpy as np
import datetime as dt
from datetime import timedelta


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify




#Set up the engine to connect to HW8 database
postgresStr = ("postgresql://postgres:password@localhost:5432/HW8-sqlalchemy-vacation")
engine = create_engine(postgresStr)

# reflect existing tables/classes
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurements
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Set up flask routes
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precip():
    
    #Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    #Return the JSON representation of your dictionary.
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #query the db, get a list of all precip measurements and dates
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Convert list of tuples into normal list
    precip = list(np.ravel(results))
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    
    #Return a JSON list of stations from the dataset
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #query the db, get a list of the stations and their respective names
    results = session.query(Station.station, Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    stationlist = list(np.ravel(results))
    return jsonify(stationlist)

#query for the dates and temperature observations from a year from the last data point.
# return a JSON list of Temperature Observations (tobs) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    #find the last date in the dataset, query the prior year's temperature observations
    last = session.query(func.max(Measurement.date)).limit(1).all()
    q_end = last[0][0].strftime("%Y-%m-%d")
    q_start = (last[0][0]-dt.timedelta(days = 365)).strftime("%Y-%m-%d")
    
    tobs_results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date < q_end).\
        filter(Measurement.date >= q_start).all()
    
    session.close()

    # Convert list of tuples into normal list
    tobslist = list(np.ravel(tobs_results))
    
    return jsonify(tobslist)

@app.route("/api/v1.0/<start>")
def startonly(start):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #find the last date in the dataset to use as an ending point for our temperature calculations
    last = session.query(func.max(Measurement.date)).limit(1).all()
    q_end = last[0][0].strftime("%Y-%m-%d")
    
    stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= q_end).all()

    statslist = list(np.ravel(stats))
    
    return jsonify({"StartDate":start,"EndDate":q_end,"TMIN": statslist[0],"TAVG":statslist[1],"TMAX":statslist[2]})

    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    #When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

@app.route("/api/v1.0/<start>/<end>")
def daterange(start,end):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
       
    stats2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    statslist = list(np.ravel(stats2))
    
    return jsonify({"StartDate":start,"EndDate":end,"TMIN": statslist[0],"TAVG":statslist[1],"TMAX":statslist[2]})

    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    #When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.


if __name__ == '__main__':
    app.run(debug=True)
