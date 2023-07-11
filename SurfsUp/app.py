# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)
inspector = inspect(engine)

# Collect the names of tables within the database
inspector.get_table_names()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Calculate the date one year from the last date in data set.
year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
        )


# A precipitation route that:
# Convert the query results from your precipitation analysis 
# (i.e. retrieve only the last 12 months of data) 

@app.route("/api/v1.0/precipitation")
def precipitation():
    prcp_scores = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).\
        order_by(Measurement.date).all()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    prcp_results = {}
    for result in prcp_scores:
        prcp_results[result.date] = result.prcp

    # Return the JSON representation of the dictionary.
    return jsonify(prcp_results)

#########################################################################################################################

# A stations route that: 
# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    # return results
    return {id:loc for id, loc in session.query(Station.station,Station.name).all()}

#########################################################################################################################

# A tobs route that:
# Returns jsonified data for the most active station
# Only returns the jsonified data for the last year of data

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    temperature_all_year = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= year_ago, Measurement.station == 'USC00519281').all()

    # Return a JSON list of temperature observations for the previous year.
    return {date:temp for date,temp in temperature_all_year}

#########################################################################################################################

# A start route that:
# Accepts the start date as a parameter from the URL
# Returns the min, max, and average temperatures calculated from the given start date to the end of the dataset

# A start/end route that:
# Accepts the start and end dates as parameters from the URL
# Returns the min, max, and average temperatures calculated from the given start date to the given end date 


# /api/v1.0/<start> and /api/v1.0/<start>/<end>
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def desplace(start, end='2017-08-23'):
    session = Session(engine)
    
    print(start,end)

    temperature = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end, Measurement.station == 'USC00519281').first()
    
    print(temperature)

    result = {
        "TMIN": temperature[0],
        "TMAX": temperature[1],
        "TAVG": temperature[2]
    }

    # Return the JSON representation of the list.
    return result
    
if __name__ == '__main__':
    app.run(debug=False)