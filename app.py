from flask import Flask, render_template, request, redirect
import pandas as pd

from scraper import NaverMapScraper

app = Flask("NaverMapScraper")

db = {}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/report")
def report():
    location = request.args.get("location")
    if location==None:
        return redirect("/")
    else:
        if db.get(location):
            places = db[location]
        else:
            spider = NaverMapScraper(location)
            places = spider.scrape_info()
            db[location] = places
        
    return render_template(
        "report.html", 
        resultNumbers=len(places), 
        searchingBy=location,
        places = places
        )

@app.route("/export")
def export():
    try:
        location = request.args.get("location")
        if not location:
            raise Exception()
        jobs = db.get(location)
        if not jobs:
            raise Exception()
        return f"Generate CSV for {location}"
    except:
        return redirect("/")
    
app.run() 