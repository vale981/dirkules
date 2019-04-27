from flask import Flask, render_template, redirect, request, url_for, flash
from dirkules import app
import dirkules.driveManagement.driveController as drico
import dirkules.serviceManagement.serviceManager as servMan
from dirkules.models import Drive, Cleaning
import dirkules.viewManager.viewManager as viewManager
from dirkules.validation.validators import CleaningForm
from sqlalchemy import asc


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', service=servMan.service_state())


@app.route('/drives', methods=['GET'])
def drives():
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


@app.route('/cleaning', methods=['GET'])
def cleaning():
    remove = request.args.get('remove')
    changestate = request.args.get('changestate')
    if not(remove is not None and changestate is not None):
        if remove is not None:
            print("remove")
        elif changestate is not None:
            print("change")
    else:
        flash("Auswahl nicht eindeutig!")
    elements = []
    for element in Cleaning.query.order_by(asc(Cleaning.name)).all():
        elements.append(viewManager.db_object_as_dict(element))
    return render_template('cleaning.html', elements=elements)


@app.route('/add_cleaning', methods=['GET', 'POST'])
def add_cleaning():
    form = CleaningForm(request.form)
    if request.method == 'POST' and form.validate():
        viewManager.create_cleaning_obj(form.jobname.data, form.path.data, form.active.data)
        return redirect(url_for('cleaning'))
    return render_template('add_cleaning.html', form=form)
