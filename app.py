from flask import Flask, render_template, redirect,session
from flask_wtf import FlaskForm

from wtforms import TextAreaField, RadioField, StringField, validators
from wtforms.validators import DataRequired,length
from wtforms.widgets import PasswordInput
import sqlite3
import os
from datetime import datetime


app = Flask(__name__)
app.debug = True
app.secret_key = 'kascf ascfhasiocfhasiocfhasiocfh'

aktuani_adresar = os.path.abspath(os.path.dirname(__file__))
databaze_uzivatele="uzivatele.db"
databaze_poznamky="poznamky.db"
class PoznamkaForm(FlaskForm):
    poznamka = TextAreaField("Poznámka", validators=[DataRequired()])
    soukrome_verejne = RadioField("soukrome nebo verejne",
                      choices=[('soukromé', 'soukromé'), ('veřejné', 'veřejné')])
    dulezitost = RadioField("dulezitost poznamky",
                      choices=[("1", "nedůležitá poznámka"), ("2", 'normální poznámka'), ("3", 'důležitá poznámka')])

class UpravaForm(FlaskForm):
    id=""
    uprava = TextAreaField("uprava", validators=[DataRequired(),length(min=1,max=250)])


class RegistraceForm(FlaskForm):
    jmeno = StringField("jmeno", validators=[DataRequired()])
    heslo = StringField("heslo", validators=[DataRequired()], widget=PasswordInput(hide_value=False))
    heslo_znovu = StringField("heslo_znovu", validators=[DataRequired()], widget=PasswordInput(hide_value=False))
    obrazek = StringField("obrazek")

class PrihlaseniForm(FlaskForm):
    jmeno = StringField("jmeno", validators=[DataRequired()])
    heslo = StringField("heslo", validators=[DataRequired()], widget=PasswordInput(hide_value=False))


@app.route('/', methods=['GET','POST'])
def zobraz_vsechny_poznamky():
    """Zobrazí formulář por poznámky"""
    max_delka = 250

    conn = sqlite3.connect('poznamky.db')
    cursor = conn.cursor()
    cursor.execute(f'CREATE TABLE IF NOT EXISTS poznamky (jmeno varchar(30), poznamka varchar({max_delka}) , datum varchar(40), soukrome varchar(10), dulezitost int)')
    conn.commit()
    
    form = []
    
    prihlasen = 0
    if not 'prihlasen' in session:
        jmeno="anonym"
        session['prihlasen']=0
        registrovat="registrovat se"
        prihlaseni="přihlásit se"
        odhlaseni=""
    else:
        
        prihlasen = session['prihlasen']
        if prihlasen==0:
            jmeno="anonym"
            registrovat="registrovat se"
            prihlaseni="přihlásit se"
            odhlaseni=""
        else:
            jmeno=session['jmeno']
            registrovat=""
            prihlaseni=""
            odhlaseni="odhlásit se"

    
    data = cursor.execute('SELECT rowid,* FROM poznamky ORDER BY datum DESC')

    poznamky = data.fetchall()
    poznamky3 = [list(i) for i in poznamky]
    if not poznamky:
        poznamky2="zatím nebyla vložena žádná poznámka"
    else:
        poznamky2=""
    conn_uzivatele = sqlite3.connect('uzivatele.db')
    try:
        cursor_uzivatele = conn_uzivatele.cursor()
        data_uzivatele = cursor_uzivatele.execute('SELECT * FROM uzivatele')
        data_uzivatele2 = data_uzivatele.fetchall()
    except:
        data_uzivatele2 = ""
    conn_uzivatele.close()

    i = 0
    for radky in poznamky3:            
        if poznamky3[i][1] == "anonym":
            poznamky3[i].append("https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/1200px-No_image_available.svg.png")
            poznamky3[i].append("rgb(25,25,25)")
            if not jmeno=="Admin":
                poznamky3[i][0] = -1

        else:
            uzivatel_se_nasel = False
            for radky2 in data_uzivatele2:
                if radky2[0] == poznamky3[i][1]:
                    poznamky3[i].append(str(radky2[3]))
                    if not jmeno=="Admin" and not jmeno==poznamky[i][1]:
                        poznamky3[i][0] = -1


                    uzivatel_se_nasel = True
            if not uzivatel_se_nasel:
                poznamky3[i].append("https://previews.123rf.com/images/happyvector071/happyvector0711608/happyvector071160800591/62947847-abstract-creative-vector-design-layout-with-text-do-not-exist-.jpg")
                poznamky3[i][0] = -1
            if poznamky3[i][1] == jmeno:
                if poznamky3[i][4] == "soukromé":
                    poznamky3[i].append("rgb(100,0,0)")
                else:
                    poznamky3[i].append("rgb(6, 53, 18)")
            else:
                poznamky3[i].append("rgb(25,25,25)")
            
        poznamky3[i][3] = datetime.strptime(poznamky3[i][3], '%Y-%m-%d %H:%M:%S.%f').strftime("%d.%m.%Y %H:%M")
        i+=1

    poznamky4=[]
    i = 0
    poznamky_dulezite="Žádná důležitá poznámka"
    poznamky_normalni="Žádná normální poznámka"
    poznamky_nedulezite="Žádná nedůležitá poznámka"
    for radky in poznamky3:            
        if not radky[4] == "soukromé" or (jmeno != "anonym" and jmeno == radky[1]):
            form.append(UpravaForm())
            form[i].uprava.data=radky[2]
            form[i].id = radky[0]
            i+=1
            if radky[5] == 1:
                poznamky_nedulezite=""
            if radky[5] == 2:
                poznamky_normalni=""
            if radky[5] == 3:
                poznamky_dulezite=""
            poznamky4.append(radky)
            


    conn.close()
    return render_template('index.html', form=form,
    poznamky=poznamky4, poznamky2=poznamky2 , jmeno=jmeno,registrovat=registrovat,prihlaseni=prihlaseni, odhlaseni=odhlaseni,
    poznamky_dulezite=poznamky_dulezite, poznamky_normalni=poznamky_normalni, poznamky_nedulezite=poznamky_nedulezite)

@app.route('/poznamka/vlozit', methods=['GET','POST'])
def vloz_poznamku():
    """Zobrazí formulář por poznámky"""
    max_delka = 250
    form = PoznamkaForm()

    conn = sqlite3.connect('poznamky.db')
    cursor = conn.cursor()
    cursor.execute(f'CREATE TABLE IF NOT EXISTS poznamky (jmeno varchar(30), poznamka varchar({max_delka}) , datum varchar(40), soukrome varchar(10))')
    conn.commit()
    

    prihlasen = 0
    if not 'prihlasen' in session:
        jmeno="anonym"
        session['prihlasen']=0
        registrovat="registrovat se"
        prihlaseni="přihlásit se"
        odhlaseni=""
    else:
        
        prihlasen = session['prihlasen']
        if prihlasen==0:
            jmeno="anonym"
            registrovat="registrovat se"
            prihlaseni="přihlásit se"
            odhlaseni=""
        else:
            jmeno=session['jmeno']
            registrovat=""
            prihlaseni=""
            odhlaseni="odhlásit se"

    if form.validate_on_submit():

        text=form.poznamka.data
        
        if jmeno == "anonym" and form.soukrome_verejne.data=="soukromé":
            upozorneni=" přihlašte se pro vkládání soukromých poznámek!"
            return render_template('vlozit_poznamku.html', form=form,upozorneni=upozorneni, jmeno=jmeno,registrovat=registrovat,prihlaseni=prihlaseni, odhlaseni=odhlaseni)
        elif jmeno == "anonym" and form.dulezitost.data=="3":
            upozorneni=" přihlašte se pro vkládání důležitých poznámek!"
            return render_template('vlozit_poznamku.html', form=form,upozorneni=upozorneni, jmeno=jmeno,registrovat=registrovat,prihlaseni=prihlaseni, odhlaseni=odhlaseni)
        elif len(text) > max_delka:
            upozorneni=" překročil jsi limit " + str(max_delka) + " znaků (máš " + str(len(text)) + " znaků)"
            return render_template('vlozit_poznamku.html', form=form,upozorneni=upozorneni, jmeno=jmeno,registrovat=registrovat,prihlaseni=prihlaseni, odhlaseni=odhlaseni)
        else:
            datum = datetime.now()
            data_do_databaze = (jmeno,form.poznamka.data,datum,form.soukrome_verejne.data,int(form.dulezitost.data),)
            cursor.execute('INSERT INTO poznamky VALUES(?,?,?,?,?)',data_do_databaze)
            conn.commit()
            cursor.close()
            conn.close()

            conn = sqlite3.connect(databaze_uzivatele)
            cursor = conn.cursor()
            data_uzivatele = cursor.execute('SELECT * FROM uzivatele')

            if not jmeno == "Anonym":
                for radky in data_uzivatele:
                    if radky[0] == jmeno:
                        pocet = int(radky[4]) + 1
                        data_do_databaze = (pocet,jmeno,)
                        cursor.execute('UPDATE uzivatele SET pocet_poznamek=? WHERE jmeno=?',data_do_databaze)
                        conn.commit()
                        cursor.close()
                        conn.close()
                        break

            return redirect('/')
    form.poznamka.data="zde napište poznámku"
    form.soukrome_verejne.data="veřejné"
    form.dulezitost.data = "1"
    conn.close()
   
    return render_template('vlozit_poznamku.html', form=form,upozorneni=" limit je " + str(max_delka) + " znaků", jmeno=jmeno,registrovat=registrovat,prihlaseni=prihlaseni, odhlaseni=odhlaseni)


@app.route('/poznamky', methods=['GET'])
def zobraz_poznamky():
    form = []
    prihlasen = session['prihlasen']
    if prihlasen==0:
        jmeno="anonym"
        registrovat="registrovat se"
        prihlaseni="přihlásit se"
        odhlaseni=""
    else:
        jmeno=session['jmeno']
        registrovat=""
        prihlaseni=""
        odhlaseni="odhlásit se"
    if jmeno=="anonym":
        return render_template('chyba.html', chybova_hlaska_nadpis="Chyba při otevírání poznámek",chybova_hlaska_text="Nejste přihlášen, prosím přihlašte se pro opravu této chyby")
    else:
        conn = sqlite3.connect('poznamky.db')
        cursor = conn.cursor()
        data_do_databaze = (jmeno,)
        data=cursor.execute('SELECT rowid,* FROM poznamky WHERE jmeno = ? ORDER BY datum DESC',data_do_databaze)
        poznamky=data.fetchall()
        conn.commit()

        poznamky2 = [list(i) for i in poznamky]
        if poznamky:
            conn_uzivatele = sqlite3.connect('uzivatele.db')
            cursor_uzivatele = conn_uzivatele.cursor()
            data_do_databaze = (jmeno,)
            data_uzivatele = cursor_uzivatele.execute('SELECT * FROM uzivatele WHERE jmeno = ?',data_do_databaze)
            data_uzivatele2 = data_uzivatele.fetchall()
            conn_uzivatele.close()
            i=0
            for radky in poznamky2:
                form.append(UpravaForm())
                form[i].uprava.data=radky[2]
                form[i].id = radky[0]
                uzivatel_se_nasel = False
                for radky2 in data_uzivatele2:
                    if radky2[0] == poznamky2[i][1]:
                        poznamky2[i].append(str(radky2[3]))
                        uzivatel_se_nasel = True
                if not uzivatel_se_nasel:
                    poznamky2[i].append("https://previews.123rf.com/images/happyvector071/happyvector0711608/happyvector071160800591/62947847-abstract-creative-vector-design-layout-with-text-do-not-exist-.jpg")
                poznamky2[i][3] = datetime.strptime(poznamky2[i][3], '%Y-%m-%d %H:%M:%S.%f').strftime("%d.%m.%Y %H:%M")
                
                i+=1
        return render_template('poznamky.html',form=form , poznamky=poznamky2, jmeno=jmeno,registrovat=registrovat,prihlaseni=prihlaseni, odhlaseni=odhlaseni)

@app.route('/profil/<jmeno_profilu>', methods=['GET'])
def zobraz_profil(jmeno_profilu):
    if not jmeno_profilu == "anonym":
    
        conn_uzivatele = sqlite3.connect('uzivatele.db')
        cursor_uzivatele = conn_uzivatele.cursor()
        data_do_databaze = (jmeno_profilu,)
        data_uzivatele = cursor_uzivatele.execute('SELECT * FROM uzivatele WHERE jmeno = ?',data_do_databaze)
        data_uzivatele2 = data_uzivatele.fetchall()
        conn_uzivatele.close()
        for radky in data_uzivatele2:
            jmeno=radky[0]
            registrace=datetime.strptime(radky[2], '%Y-%m-%d %H:%M:%S.%f').strftime("%d.%m.%Y %H:%M")
            obrazek=radky[3]
            poznamky=radky[4]

        return render_template('profil.html',obrazek=obrazek, jmeno=jmeno, poznamky=poznamky, registrace=registrace)
    return render_template('chyba.html', chybova_hlaska_nadpis="Chyba při otevírání profilu",chybova_hlaska_text="Snažíš se zobrazit profil anonym, tento profil neexistuje, slouží pouze pro nepřihlášené uživatele")


@app.route('/profil/<jmeno_profilu>/edit', methods=['GET'])
def edituj_profil(jmeno_profilu):
    return redirect(f'/profil/{jmeno_profilu}')
    #return render_template('chyba.html', chybova_hlaska_nadpis="Chyba při otevírání profilu",chybova_hlaska_text="Profily ještě nejsou hotové")
    #return render_template('chyba.html', chybova_hlaska_nadpis="Chyba při otevírání profilu",chybova_hlaska_text="Nejste přihlášen, prosím přihlašte se pro opravu této chyby")

@app.route('/registrace', methods=['GET','POST'])
def registrace():
    form=RegistraceForm()
    delka_jmena = 30
    delka_hesla = 50
    delka_odkazu = 300
    upozorneni=" maximální délka jména je " + str(delka_jmena) + " znaků, hesla " + str(delka_hesla) + " znaků" + " a odkazu na obrázek " + str(delka_odkazu) + " znaků"
    if form.validate_on_submit():
        vse_spravne=True
        upozorneni=" |"
        if len(form.jmeno.data) > delka_jmena :
            vse_spravne=False
            upozorneni+=" jméno je delší, než " + str(delka_jmena) + " znaků! [" + str(len(form.jmeno.data)) + "] znaků |"
        if len(form.heslo.data) > delka_hesla:
            vse_spravne=False
            upozorneni+=" heslo je delší, než " + str(delka_hesla) + " znaků! [" + str(len(form.heslo.data)) + "] znaků |"   
        if form.heslo.data != form.heslo_znovu.data:
            vse_spravne=False
            upozorneni+=" hesla se neshodují|"
        if len(form.obrazek.data) > delka_odkazu:
            vse_spravne=False
            upozorneni+=" příliš dlouhý odkaz na obrázek[ " + str(form.obrazek.data) + " / " + str(delka_odkazu) + " ]|"
        if form.jmeno.data == "anonym":
            vse_spravne=False
            upozorneni+=" jméno anonym nemůžete použít|"
        if vse_spravne==True:
            conn = sqlite3.connect('uzivatele.db')
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE IF NOT EXISTS uzivatele (jmeno varchar(30), heslo varchar(50) , datum_registrace varchar(40), obrazek varchar(300), pocet_poznamek int)')
            conn.commit()
            data = cursor.execute('SELECT * FROM uzivatele')
            uzivatel_se_nasel = False
            for radky2 in data:
                if radky2[0] == form.jmeno.data:
                    uzivatel_se_nasel = True
            if not uzivatel_se_nasel:

                datum = datetime.now()
                if len(form.obrazek.data) > 0:
                    obrazek=form.obrazek.data
                else:
                    obrazek="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/1200px-No_image_available.svg.png"
                data_do_databaze = (form.jmeno.data,form.heslo.data,datum,obrazek,)
                cursor.execute("INSERT INTO uzivatele VALUES(?,?,?,?,0)",data_do_databaze)
                conn.commit()
                conn.close()
                return redirect('/prihlaseni')
            else:
                upozorneni="zvolené jméno již existuje, zvolte jiné"
            
    return render_template('registrace.html', form=form,upozorneni=upozorneni)

@app.route('/prihlaseni', methods=['GET','POST'])
def prihlaseni():
    upozorneni=""
    form = PrihlaseniForm()

    if form.validate_on_submit():
        conn = sqlite3.connect('uzivatele.db')
        cursor = conn.cursor()
        data = cursor.execute('SELECT * FROM uzivatele')
        poznamky = data.fetchall()
        conn.close()
        for radek in poznamky:
            if form.jmeno.data == radek[0] and form.heslo.data == radek[1]:
                session['jmeno']=radek[0]
                session['prihlasen']=1
                return redirect('/')
        upozorneni=" nenašla se vhodná kombinace jména a hesla"


    return render_template('prihlaseni.html', form=form,upozorneni=upozorneni)

@app.route('/odhlaseni')
def odhlaseni():
    session['prihlasen']=0
    session['jmeno']=""
    return redirect('/')

@app.route('/smaz/<predchozi_stranka>/<jmeno_uzivatele>/<int:id_poznamky>')
def smaz_poznamku(predchozi_stranka,jmeno_uzivatele,id_poznamky):
    if predchozi_stranka == "index":
        predchozi_stranka = ""
    
    conn = sqlite3.connect(databaze_poznamky)
    cursor = conn.cursor()
    data_do_databaze=(id_poznamky,)
    cursor.execute("DELETE FROM poznamky WHERE rowid=?", data_do_databaze)
    conn.commit()
    cursor.close()
    conn.close()
    

    conn = sqlite3.connect(databaze_uzivatele)
    cursor = conn.cursor()
    data_uzivatele = cursor.execute('SELECT * FROM uzivatele')

    if not jmeno_uzivatele == "Anonym":
        for radky in data_uzivatele:
            if radky[0] == jmeno_uzivatele:
                pocet = int(radky[4]) - 1
                data_do_databaze = (pocet,jmeno_uzivatele,)
                cursor.execute('UPDATE uzivatele SET pocet_poznamek=? WHERE jmeno=?',data_do_databaze)
                conn.commit()
                cursor.close()
                conn.close()
                break
       

    

    return redirect(f"/{predchozi_stranka}")

@app.route("/upravit/<predchozi_stranka>/<int:id>", methods=['GET','POST'])
def uprav_poznamku(predchozi_stranka, id):
    if predchozi_stranka == "index":
        predchozi_stranka = ""
    form = UpravaForm()

    if form.validate_on_submit():
        conn = sqlite3.connect(databaze_poznamky)
        cursor = conn.cursor()
        data_do_databaze=(form.uprava.data, id)
        cursor.execute("UPDATE poznamky set poznamka=? WHERE rowid=?", data_do_databaze)
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(f"/{predchozi_stranka}")
        
    else:
        return render_template('chyba.html', chybova_hlaska_nadpis="Chyba při změně poznámky",chybova_hlaska_text="Poznámka byla příliš dlouhá (" + str(len(form.uprava.data)) +"/250)")

        

    

    

if __name__ == '__main__':
    app.run()


