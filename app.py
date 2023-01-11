import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Database Setup
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base=automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
mea=Base.classes.measurement
sta=Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f'Available Route:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/startdate=2017-01-01<br/>'
        f'/api/v1.0/startdate=2016-09-02<br/>'
        f'/api/v1.0/startdate=2012-03-04/enddate=2017-02-02<br/>'
        f'/api/v1.0/startdate=2016-05-04/enddate=2016-12-31'
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    session=Session(engine)
    # Starting from the most recent data point in the database. 
    max_date=session.query(mea.date).order_by(mea.date.desc()).first()
    max_date_dt=datetime.strptime(max_date.date,'%Y-%m-%d')

    # Calculate the date one year from the last date in data set.
    year_ago_dt= max_date_dt - relativedelta(months=12)

    #Query 12 month data of Date and Prcp from Measurement
    results = session.query(mea.date,mea.prcp).\
        filter(mea.date >= str(year_ago_dt)).order_by(mea.date.asc())
    session.close()

    # Create a dictionary from the row data and append to prcp list
    precipitation_12month = []
    for date,prcp in results:
        prcp_dict={}
        prcp_dict["Date"]=date
        prcp_dict["Precipitation"]=prcp
        precipitation_12month.append(prcp_dict)
    
    return jsonify(precipitation_12month)


@app.route("/api/v1.0/stations")
def station():
    session=Session(engine)
    results=session.query(sta.id,sta.station,sta.name,sta.latitude,sta.longitude,sta.elevation)
    session.close()
    
    station_list = []
    for id,station,name,latitude,longitude,elevation in results:
        sta_dict={}
        sta_dict["id"]=id
        sta_dict["station"]=station
        sta_dict["name"]=name
        sta_dict["latitude"]=latitude
        sta_dict["longitude"]=longitude
        sta_dict["elevation"]=elevation

        station_list.append(sta_dict)
    
    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
    session=Session(engine)
    # Find most active station
    mea_query=session.query(mea.station,func.count(mea.station)).group_by(mea.station).order_by(func.count(mea.station).desc()).first()
    most_active_station=mea_query.station

    # Find Max date of Most Active Station
    max_date=session.query(mea.date).order_by(mea.date.desc()).first()
    max_date_active_station=session.query(mea.date).filter(mea.station==most_active_station).order_by(mea.date.desc()).first()
    max_date_active_station_dt=datetime.strptime(max_date.date,'%Y-%m-%d')

    # Find timestamp of 12 months before Max date of Most Active Staion
    year_ago_active_station_dt= max_date_active_station_dt - relativedelta(months=12)

    #Query
    results=session.query(mea.date,mea.tobs).filter(mea.station==most_active_station).\
    filter(mea.date >= str(year_ago_active_station_dt)).order_by(mea.date.asc())

    session.close()

    tobs_list=[]
    for date,tobs in results:
        tobs_dic={}
        tobs_dic['date']=date
        tobs_dic['tobs']=tobs
        tobs_list.append(tobs_dic)

    return jsonify(tobs_list)

@app.route("/api/v1.0/startdate=<start>")
def from_date(start):
    session=Session(engine)
    results=session.query(func.min(mea.tobs),
                         func.max(mea.tobs),
                         func.avg(mea.tobs)).filter(mea.date >= str(start))
    session.close()
    stat_list=[]
    for s in results:
        stat_dic={}
        stat_dic['Min tobs']=s[0]
        stat_dic['Max tobs']=s[1]
        stat_dic['Average tobs']=s[2]
        stat_list.append(stat_dic)
    return jsonify(stat_list)

@app.route('/api/v1.0/startdate=<start>/enddate=<end>')
def from_to_date(start,end):
    session=Session(engine)
    results=session.query(func.min(mea.tobs),
                         func.max(mea.tobs),
                         func.avg(mea.tobs)).filter(mea.date >= str(start),mea.date < str(end))
    session.close()
    stat_list=[]
    for s in results:
        stat_dic={}
        stat_dic['Min tobs']=s[0]
        stat_dic['Max tobs']=s[1]
        stat_dic['Average tobs']=s[2]
        stat_list.append(stat_dic)
    return jsonify(stat_list)
    
if __name__ == '__main__':
    app.run(debug=True)