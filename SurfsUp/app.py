# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///hawaii.sqlite")


# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

# app routing for precipitation for the past 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():
    # create session link
    session = Session(engine)
    # query the last 12 months of precipitation data
    cutoff_date = '2016-08-22'
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > cutoff_date).all()
    session.close()

    # create a dictionary from the results and append to a list of precipitation_data
    precipitation_data = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation_data.append(precipitation_dict)

    return jsonify(precipitation_data)

 # app routing for station list
@app.route("/api/v1.0/stations")
def stations():
    # create session link
    session = Session(engine)
    # query the names of all stations in the list
    results = session.query(Measurement.station).distinct().all()
    session.close()

    # create a dictionary of the active stations and their counts
    station_data = []
    for station in results:
        station_dict = {}
        station_dict["station name"] = station[0]
        station_data.append(station_dict)

    return jsonify(station_data)

# app routing observed for the past 12 months
@app.route("/api/v1.0/tobs")
def tobs():
    # create session link
    session = Session(engine)
    # query last 12 months of temperature data from the most active observation station (i.e USC00519281)
    cutoff_date = '2016-08-22'
    results = session.query(Measurement.date, Measurement.tobs).filter((Measurement.station == 'USC00519281') & (Measurement.date > cutoff_date)).all()
    session.close()

    # create dictionary of tobs data for the most active station
    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Observed Temperature"] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

# app routing for min temp, avg and max temperature for a specified start date
@app.route("/api/v1.0/<start_date>")
def temps_start(start_date):
    session = Session(engine)

    results = session.query(func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    temp_data = {
        "TMIN": results[0][1],
        "TAVG": results[0][0],
        "TMAX": results[0][2]
        }
    
    return jsonify(temp_data)

# app routing for min temp, avg and max temperature for a specified start date to the end date
@app.route("/api/v1.0/<start_date>/<end_date>")
def temps_start_end(start_date=None, end_date=None):
    session = Session(engine)

    results = session.query(func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).\
        filter((Measurement.date >= start_date)&(Measurement.date <= end_date)).\
        all()

    temp_data = {
        "TMIN": results[0][1],
        "TAVG": results[0][0],
        "TMAX": results[0][2]
        }

    return jsonify(temp_data)

if __name__ == "__main__":
    app.run(debug=True)



