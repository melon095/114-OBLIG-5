from flask import Flask
from flask import url_for
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from kgmodel import (Foresatt, Barn, Soknad, Barnehage)
from kgcontroller import (form_to_object_soknad, insert_soknad, commit_all, select_alle_barnehager, kalkuler_ledige_plasser)

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY' # nødvendig for session

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/barnehager')
def barnehager():
    information = select_alle_barnehager()
    return render_template('barnehager.html', data=information)

@app.route('/behandle', methods=['GET', 'POST'])
def behandle():
    if request.method == 'POST':
        sd = request.form
        
        print(sd)
        
        obj = form_to_object_soknad(sd)
        
        log = insert_soknad(obj)
        ledig = kalkuler_ledige_plasser(obj)
        
        print(log)
        
        session['information'] = { "soknad": sd, "ledig": ledig }

        return redirect(url_for('svar')) #[1]
    else:
        return render_template('soknad.html')

@app.route('/svar')
def svar():
    information = session['information']
    return render_template('svar.html', data=information)

@app.route('/commit')
def commit():
    commit_all()
    return render_template('commit.html')




"""
Referanser
[1] https://stackoverflow.com/questions/21668481/difference-between-render-template-and-redirect
"""

"""
Søkeuttrykk

"""