# Import the dependencies.
import datetime as dt
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
New_Base = automap_base()
# reflect the tables
New_Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = New_Base.classes.measurement
Station = New_Base.classes.station

# Create our session (link) from Python to the DB
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
    return (
        f"Aloha, This is the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Precipitation Data last_year"""
    # date from 1 year ago from last time point
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    precipitations = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()

    session.close()
    # Dictionary with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitations}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    """Return JSON List of Stations."""
    results = session.query(Station.station).all()

    session.close()

    # Convert to a list and return JSON
    stations = list(np.ravel(results))
    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    """ Temperature observations (tobs) for last_year."""
    # date from 1 year ago from last time point
    # This might be redundant. not sure If i can reuse from above
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the last 12 months of temperature observation data for this station
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= last_year).all()

    session.close()
    # Convert tobs into a 1D array and store in list
    temperatures = list(np.ravel(results))

    # Return the results
    return jsonify(temperatures=temperatures)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Calculate and JSON TMIN, TAVG, TMAX."""

    # Select statement
    select = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        
        # start = dt.datetime.strptime(start, "%m/%d/%Y")
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*select).\
            filter(Measurement.date >= start).all()

        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)

        # calculate TMIN, TAVG, TMAX with start and stop
        start = dt.datetime.strptime(start, "%m%d%Y")
        end = dt.datetime.strptime(end, "%m%d%Y")

        results = session.query(*select).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # put results into 1D array and return JSON
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


if __name__ == '__main__':
    app.run()
    












