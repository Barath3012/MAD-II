from flask import Flask, redirect, url_for, render_template, request, session, flash
from database import connect
import sqlite3
app = Flask(__name__)

app.secret_key = 'dev'
app.config['SESSION_TYPE'] = 'filesystem'

app.jinja_env.add_extension('jinja2.ext.do')

if not connect():
    print("DATABASE CONNECTION WAS NOT ESTABLISHED. ABORTING!!!")
    quit(0)

def getCart(data):
    toRet = []
    with sqlite3.connect("database.db") as con:
        cur = con.cursor()

        for pid in data:
            qty = data[pid]
            cur.execute("SELECT PRODUCT_NAME,PRODUCT_PRICE FROM PRODUCTS WHERE PRODUCT_ID = ?;",(pid,))
            pname,price = cur.fetchone()
            toRet.append({"name":pname,"price":price,"quantity":qty,"total":qty*price})
        tot=0
        for i in toRet:
            tot+=i["total"]
        return toRet,tot

def getSessionData():
    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("SELECT P.PRODUCT_ID,P.PRODUCT_NAME,P.PRODUCT_PRICE,S.SECTION_NAME FROM PRODUCTS P,\
                     SECTIONS S WHERE P.SECTION_ID = S.SECTION_ID;")
        data = cur.fetchall()
        toRet = {}
        #print("GETTING DATA:",data)
        for i in data:
            
            if i[3] in toRet:
                #print("appending...",i)
                toRet[i[3]].append(i)
            else:
                toRet[i[3]] = [i]
        cur.execute("SELECT SECTION_NAME FROM SECTIONS;")
        data = cur.fetchall()
        for i in data:
            if i[0] not in toRet:
                toRet[i[0]] = []
        return toRet

params = {
    "sectiondata":getSessionData()
}



@app.route("/")
def default():
    if not session.get('logged_in'):
        return redirect("/login")
    else:
        return redirect("/home")
    
@app.route("/login",methods=["GET","POST"])
def login():
    if not session.get('logged_in'):
        if request.method=="POST":
            username = request.form.get("username")
            password = request.form.get("password")
            
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("SELECT USER_NAME,USER_PASSWORD,ROLE_ID,USER_ID FROM USER WHERE USER_NAME = ?",(username,))
                data = cur.fetchone()
                if data is None or (len(data)==0 or password != data[1]):
                    flash("Error!","Invalid credentials.")
                else:
                    session['logged_in'] = True
                    session['userid'] = data[3]
                    session['username'] = username
                    session['role'] = 2
                    if data[2] == 1:
                        return redirect(url_for("admin_home"))    
                    return redirect(url_for("home"))
        return render_template("index.html",params=params,htmlfile="login.html")
    else:
        return redirect(url_for("home"))

@app.route("/home",methods=["GET","POST"])
def home():
    if session.get('logged_in') and session.get('role')!=1:
        if request.method == "POST":
            if str(request.form.get("plus")):
                session_data = getSessionData()
            
                product_index,section_name = request.form.get("plus").split()
                product_index = int(product_index)
                product_data = session_data[section_name][product_index]

                with sqlite3.connect("database.db") as con:
                    cur = con.cursor()
                    cur.execute("SELECT USER_ID,CART_ITEMS FROM USER_CART WHERE USER_ID = ?;",(session.get("userid"),))
                    data = cur.fetchall()
                    if data:
                        
                        cart_data = eval(data[0][1])
                        if product_data[0] in cart_data:

                            cart_data[product_data[0]] += 1
                        else:
                            cart_data[product_data[0]] = 1
                        cur.execute("UPDATE USER_CART SET CART_ITEMS = ? WHERE USER_ID = ?;",(str(cart_data),session.get("userid")))
                    else:
                        cur.execute("INSERT INTO USER_CART(USER_ID,CART_ITEMS) VALUES(?,?);",(session.get("userid"),str({product_data[0]:1})))
                    flash("Success!","Product added to cart!")
                    con.commit()
        return render_template("index.html",params=params,htmlfile="home.html")
    else:
        return redirect("/login")

@app.route("/admin",methods=["GET","POST"])
def admin_login():
    if not session.get('logged_in') or session.get('role')!=1:
        if request.method=="POST":
            username = request.form.get("username")
            password = request.form.get("password")
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("SELECT USER_NAME,USER_PASSWORD,ROLE_ID FROM USER WHERE USER_NAME = ?",(username,))
                data = cur.fetchone()
                if data is None or (len(data)==0 or password != data[1] or data[2]!=1):
                    
                    flash("Error!","Invalid credentials.")
                else:
                    session['logged_in'] = True
                    session['role'] = 1
                    return redirect(url_for("admin_home"))
        return render_template("index.html",params=params,htmlfile="admin.html")
    else:
        return redirect("/admin/home")
    

@app.route("/admin/product",methods=["POST"])
def admin_product():
    if session.get('logged_in'):
        if request.method=="POST":
            section_name = request.form.get("section_name")
            prodName = request.form.get("prodName")
            unitValues = request.form.get("unitValues")
            ratePerUnit = request.form.get("ratePerUnit")
            quantity = request.form.get("quantity")
            try:
                
                ratePerUnit = int(ratePerUnit)
                
                quantity = int(quantity)
                
                session_data = getSessionData()
                if not any([(prodName in i) for i in session_data[section_name]]):
                     with sqlite3.connect("database.db") as con:
                        cur = con.cursor()
                        cur.execute("SELECT SECTION_ID FROM SECTIONS WHERE SECTION_NAME = ?",(section_name,))
                        sid = cur.fetchone()[0]
                        
                        cur.execute("INSERT INTO PRODUCTS(PRODUCT_NAME,SECTION_ID,PRODUCT_PRICE,PRODUCT_UNIT) VALUES(?,?,?,?);",(prodName,sid,ratePerUnit,unitValues))
                        cur.execute("SELECT PRODUCT_ID FROM PRODUCTS WHERE SECTION_ID = ? AND PRODUCT_NAME = ? AND PRODUCT_PRICE = ? AND PRODUCT_UNIT = ?;",(sid,prodName,ratePerUnit,unitValues))
                        pid = cur.fetchone()[0]
                        cur.execute("INSERT INTO PRODUCT_INVENTORY(PRODUCT_ID,PRODUCT_INVENTORY_QUANTITY) VALUES(?,?);",(pid,quantity))
                else:
                    flash("Error!","Product name already exists")
            except Exception as e:
                flash("Error!","Invalid form")
          
            params["sectiondata"] = getSessionData()
        return redirect("/admin/home")
@app.route("/admin/home",methods=["GET","POST"])
def admin_home():

    if session.get('logged_in'):
        if request.method=="POST":
            if request.form.get('section_name'):
                session['section_name'] = request.form.get('section_name')
            else:
                category = request.form.get('catName')
                with sqlite3.connect("database.db") as con:
                    cur = con.cursor()
                    cur.execute("SELECT SECTION_NAME FROM SECTIONS;")
                    data = cur.fetchall()

                    if not (category,) in data:
                        cur.execute("INSERT INTO SECTIONS(SECTION_NAME) VALUES (?);",(category,))   
                        
            params["sectiondata"] = getSessionData()
            
        return render_template("index.html",params=params,htmlfile="admin_modal.html")
    else:
        return redirect("/admin")
    
@app.route("/register",methods=['GET','POST'])
def register():
    if not session.get('logged_in'):
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            cpassword = request.form.get("confirm_password")
            role_id = 2

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM USER WHERE USER_NAME = ?",(username,))
                all_users = cur.fetchone()
                if password == cpassword:
                    
                    if not all_users or username not in all_users: 
                        cur.execute("INSERT INTO USER(ROLE_ID, USER_NAME ,USER_PASSWORD) VALUES(?,?,?)",(role_id,username,password))
                        return redirect(url_for('login'))
                    else:
                        #flash("Username already exists. Try a different one.")
                        return render_template('register.html', error="Username already exists")
                else:
                    #flash("Passwords did not match.")
                    return render_template('register.html', error="Passwords did not match.")
        return render_template("index.html", params=params, htmlfile="register.html")
    else:
        return redirect("/home")

@app.route("/thankyou")
def done():
    if session.get("logged_in"):
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT USER_ID,CART_ITEMS FROM USER_CART WHERE USER_ID = ?",(session.get('userid'),))
            data = cur.fetchall()
            if not request.args.get('total'):
                return "Error!"
            for i in data:
                cur.execute("INSERT INTO USER_BILLS(USER_ID,BILL_ITEMS,BILL_AMOUNT) VALUES (?,?,?)",(i[0],i[1],request.args.get('total')))
            cur.execute("DELETE FROM USER_CART WHERE USER_ID = ?",(session.get('userid'),))
            con.commit()
        return "<h3>Order purchased successfully! Thank you for your purchase!</h3>"

@app.route("/cart")
def cart():
    data = "not logged in"
    if session.get("logged_in"):
        with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("SELECT CART_ITEMS FROM USER_CART WHERE USER_ID = ?;",(session.get("userid"),))
                data = cur.fetchone()
                
        if not data:
            data = {}
            tot=0
        else:
            
            data = eval(data[0])
            data,tot=getCart(data)
        return render_template("index.html", params=params, htmlfile="cart.html",data=data,totalcost=tot)
    return redirect('/login')



@app.route("/logout")
def logout():
    try:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("DELETE FROM USER_CART WHERE USER_ID = ?",(session.get('userid'),))
            con.commit()
    except:
        print("ERROR LOGGING OUT")

    session.clear()
    return redirect(url_for('login'))


#if __name__ == "__main__":
app.run(debug=True)