from flask import Flask, render_template, request, redirect
import pandas as pd

from scraper import NaverMapScraper

app = Flask("NaverMapScraper")

db = {}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/report")
def potato():
    location = request.args.get("location")
    if location==None:
        return redirect("/")
    else:
        spider = NaverMapScraper(location)
        df = spider.scrape_info()
        db[location] = df
        
    return render_template("report.html", searchingBy=location)

app.run() 