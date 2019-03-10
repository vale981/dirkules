from flask import Flask, render_template
from dirkules import app
import dirkules.driveManagement.driveController as drico
from dirkules.models import Drive
from dirkules import scheduler
import dirkules.viewManager.viewManager as viewManager


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/drives', methods=['GET'])
def drives():
    drives = drico.getAllDrives()
    print(scheduler.get_jobs())
    dbDrives = []
    print(Drive.query.all())
    for drive in Drive.query.all():
        d = viewManager.db_object_as_dict(drive)
        dbDrives.append(d)
    return render_template('drives.html', drives=dbDrives)


@app.route('/about', methods=['GET'])
def about():
    version = "1.0"
    return render_template('about.html', version=version)


@app.route('/partitions/<part>', methods=['GET'])
def partitions(part):
    part = part.replace("_", "/")
    parts = drico.getPartitions(part)
    return render_template('partitions.html', parts=parts)
