import altair as alt
from flask import (Flask, url_for, render_template, request, redirect, session)
from markupsafe import Markup
from io import StringIO
from kgmodel import (Foresatt, Barn, Soknad, Barnehage)
from kgcontroller import (form_to_object_soknad, kalkuler_barnehage_tilbud, insert_soknad, commit_all, select_alle_barnehager, select_alle_soknader, hent_barnehage_statistikk)

alt.renderers.enable('html')

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
        har_bh_tilbud = kalkuler_barnehage_tilbud(obj)
        
        print(log)
        
        session['søknad_informasjon'] = sd
        session['har_barnehage_tilbud'] = har_bh_tilbud

        return redirect(url_for('svar')) #[1]
    else:
        return render_template('soknad.html')

@app.route('/svar')
def svar():
    information = session['søknad_informasjon']
    har_barnehage_tilbud = session['har_barnehage_tilbud']
    
    return render_template('svar.html', data=information, har_barnehage_tilbud=har_barnehage_tilbud)

@app.route('/commit')
def commit():
    result = commit_all()
    return render_template('commit.html', data=result)

@app.route("/soknader")
def soknader():
    soknader = select_alle_soknader()
    barnehage_tilbud = map(kalkuler_barnehage_tilbud, soknader)
    
    return render_template('soknader.html', data=zip(soknader, barnehage_tilbud))

@app.route("/statistikk", methods=['GET', 'POST'])
def statistikk():
    kommune = request.form.get('kommune', None)
    html = None

    if kommune is not None:
        try:
            s = hent_barnehage_statistikk(kommune)
            s = s.melt(id_vars=['Kommune'], var_name='År', value_name='Antall')

            chart = alt.Chart(s).mark_bar().encode(
                x="År:Q",
                y=alt.Y("Antall:Q", scale=alt.Scale(domain=(0, 100))),
                color="Kommune:N",
            )
            
            io = StringIO()
            chart.save(io, format="html", inline=True)
            
            html = io.getvalue()
        except Exception as e:
            s = None
            html = str(e)
    
    return render_template('statistikk.html', html=Markup(html), kommune=kommune)

"""
Referanser
[1] https://stackoverflow.com/questions/21668481/difference-between-render-template-and-redirect
"""

"""
Søkeuttrykk

"""
