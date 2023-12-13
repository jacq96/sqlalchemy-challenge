#Import the dependencies
from flask import Flask
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base


#Create an app
app = Flask(__name__)

#Connect to the SQLite Database
db_url = "sqlite:///Resources/hawaii.sqlite"
engine = create_engine(db_url)

#Reflect the database tables
Base = automap_base()
Base.prepare(autoload_with=engine)

#Map Measurement and Station Tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create a Session
session = Session(engine)

#Define Routes
@app.route("/")
def home():
    return (
        f"Welcome to the Climate Analysis API.<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

#Define Preciptation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Calculate the date  months ago from the most recent date in the dataset
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date_row = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = most_recent_date_row[0] if most_recent_date_row else None
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d') if most_recent_date else None
    one_yr_ago = most_recent_date - timedelta(days=365) if most_recent_date else None

    #Query for the precipitation data for the last 12 months
    precipitation_data = (session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_yr_ago).all())

    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

#Define Stations Route
@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    station_data = len(session.query(Station.station).all())

    # Convert the results to a list
    stations_list = [station[0] for station in station_data]

    return jsonify(stations_list)

#Define Tobs Route
@app.route("/api/v1.0/tobs")
def tobs():
    # Identify the most active station
    most_active_station_id = (
        Session.query(Measurement.station)
        .group_by(Measurement.station)
        .order_by(func.count(Measurement.station).desc())
        .first()[0]
    )

    # Calculate the date 12 months ago from the most recent date in the dataset
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date_row = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date = most_recent_date_row[0] if most_recent_date_row else None
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d') if most_recent_date else None
    one_yr_ago = most_recent_date - timedelta(days=365) if most_recent_date else None

    # Query temperature data for the last 12 months from the most active station
    twelve_mo_temp_data = (session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station_id).filter(Measurement.date >= one_year_ago).all())

    # Convert the results to a list of dictionaries
    tobs_list = [{'Date': date, 'Temperature': tobs} for date, tobs in temperature_data]

    return jsonify(tobs_list)

#Define Start Route
@app.route("/api/v1.0/<start>")
def start_date(start):
    # Query temperature statistics for the dates greater than or equal to the start date
    temperature_stats = (
        Session.query(func.min(Measurement.tobs).label('min_temp'),
                      func.avg(Measurement.tobs).label('avg_temp'),
                      func.max(Measurement.tobs).label('max_temp'))
        .filter(Measurement.date >= start)
        .first()
    )

    return jsonify({
        'Min Temperature': temperature_stats.min_temp,
        'Average Temperature': temperature_stats.avg_temp,
        'Max Temperature': temperature_stats.max_temp
    })

#Define Start/End Date Route
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Query temperature statistics for the date range from start date to end date
    temperature_stats = (
        Session.query(func.min(Measurement.tobs).label('min_temp'),
                      func.avg(Measurement.tobs).label('avg_temp'),
                      func.max(Measurement.tobs).label('max_temp'))
        .filter(Measurement.date >= start)
        .filter(Measurement.date <= end)
        .first()
    )

    return jsonify({
        'Min Temperature': temperature_stats.min_temp,
        'Average Temperature': temperature_stats.avg_temp,
        'Max Temperature': temperature_stats.max_temp
    })

if __name__ == "__main__":
    app.run(debug=True)