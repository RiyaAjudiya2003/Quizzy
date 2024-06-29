
import mysql
import os
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.utils import secure_filename

import connection

app = Flask(__name__)
app.secret_key = "abcd"


@app.route("/")
def home():
    connection.cursor.execute("select * from category")
    cate = connection.cursor.fetchall()
    return render_template("index.html", data=cate)


@app.route("/aboutus")
def aboutus():
    return render_template("about.html")


@app.route("/content/<int:id>/<string:name>", methods=['GET', 'POST'])
def content(id, name):
    session.pop("ans", None)
    session.pop("question_id", None)
    connection.cursor.execute("SELECT * FROM test WHERE c_id = %s ORDER BY t_id LIMIT 1", [id])
    cate = connection.cursor.fetchall()
    session["qid"] = cate[0][0]
    session["category"] = id
    session["rightans"] = 0
    session["wrongans"] = 0
    session["question"] = 1
    session["skipans"] = 0
    session["answers"] = ""
    session["question_id"] = ""
    return render_template("content.html", data=cate, cat=name)


@app.route("/next/<int:id>/<string:name>/<int:tid>", methods=['GET', 'POST'])
def next(id, name, tid):
    session.pop("ans", None)
    connection.cursor.execute("select * from test where t_id=%s and c_id=%s", [id + 1, tid])
    cate = connection.cursor.fetchall()
    session["question"] = session["question"] + 1
    return render_template("content.html", data=cate, cat=name)


@app.route("/checkans/<int:id>/<string:name>/<string:aid>", methods=['GET'])
def checkans(id, name, aid):
    session.pop("ans", None)
    connection.cursor.execute("select * from test where t_id=%s", [id])
    cate = connection.cursor.fetchall()
    session['soption'] = aid
    if session["answers"]:
       session["answers"] = session["answers"] + "," + session['soption']
    else:
       session["answers"] = session['soption']
    session["question_id"] = session["question_id"] + "," + str(cate[0][0])
    session['result'] = cate[0][7]

    if aid == cate[0][7]:
        session["ans"] = "True"
        session["rightans"] = session["rightans"] + 1
    elif aid != cate[0][7]:
        session["ans"] = "False"
        session["wrongans"] = session["wrongans"] + 1
    return render_template("content.html", data=cate, cat=name, ansid=aid)


@app.route("/error")
def error():
    return render_template("error.html")


@app.route("/showresult")
def showresult():
    id=session["category"]
    connection.cursor.execute("select * from test where c_id=%s order by t_id",[id])
    cate = connection.cursor.fetchall()
    return render_template("showresult.html",data=cate)


@app.route("/category")
def category():
    connection.cursor.execute("select * from category")
    cate = connection.cursor.fetchall()
    return render_template("category.html", data=cate)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        nm = request.form['name']
        em = request.form['email']
        sub = request.form['subject']
        msgg = request.form['message']
        connection.cursor.execute("insert into contact(name,email,subject,msg) values(%s,%s,%s,%s)",
                                  (nm, em, sub, msgg))
        connection.con.commit()
        msg=" Your Feedback is Sucessfully Submitted"
        return render_template('contact.html', msg=msg)
    else:
        return render_template('contact.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    session['login'] = False
    if request.method == 'POST':
        em = request.form['email']
        pw = request.form['password']
        connection.cursor.execute("select * from register where r_email=%s and r_pw=%s", (em, pw))
        ac = connection.cursor.fetchone()
        if ac:
            session['login'] = True
            session['id'] = ac[0]
            session['name'] = ac[1]
            return redirect(url_for("home"))
        else:
            return render_template("login.html")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("id", None)
    session.pop("name", None)
    session.pop("login", None)
    return redirect("/")


@app.route("/adlogout")
def adlogout():
    session.pop("id", None)
    session.pop("name", None)
    session.pop("adlogin", None)
    return redirect("adminlogin")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fnm = request.form['fnm']
        lnm = request.form['lnm']
        email = request.form['email']
        pw = request.form['password']
        connection.cursor.execute("insert into register(r_fnm,r_lnm,r_email,r_pw) values(%s,%s,%s,%s)",
                                  (fnm, lnm, email, pw))
        connection.con.commit()
        return redirect("/")
    else:
        return render_template('register.html')


@app.route("/admin")
def admin():
    return render_template("admin/index.html")


@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    session['adlogin'] = False
    if request.method == 'POST':
        unm = request.form['unm']
        pas = request.form['pw']
        connection.cursor.execute("select * from admin where name=%s and password=%s", (unm, pas))
        ac = connection.cursor.fetchone()
        if ac:
            session['adlogin'] = True
            session['id'] = ac[0]
            session['user'] = ac[1]
            return render_template("admin/index.html")
        else:
            return render_template("admin/adminlogin.html")
    else:
        return render_template("admin/adminlogin.html")


@app.route("/addadmin", methods=['GET', 'POST'])
def addadmin():
    if request.method == 'POST':
        unm = request.form['username']
        pas = request.form['password']
        connection.cursor.execute("insert into admin(name,password) values(%s,%s)", (unm, pas))
        connection.con.commit()
        return redirect("/addadmin")
    else:
        return render_template("admin/addadmin.html")


@app.route('/editadmin/<int:id>', methods=['GET', 'POST'])
def editadmin(id):
    if request.method == 'POST':
        eid = request.form['id']
        unm = request.form['username']
        pas = request.form['password']
        connection.cursor.execute("update admin set name = %s, password = %s WHERE id = %s", (unm, pas, eid))
        connection.con.commit()
        return redirect("/viewadmin")
    else:
        connection.cursor.execute("select *  from admin where id=%s", [id])
        output = connection.cursor.fetchone()
        return render_template("admin/edit_admin.html", data=output)


@app.route("/edit_admin")
def edit_admin():
    return render_template("admin/edit_admin.html")


@app.route("/viewadmin")
def viewadmin():
    connection.cursor.execute("select * from admin")
    output = connection.cursor.fetchall()
    return render_template("admin/viewadmin.html", data=output)


@app.route('/delete_admin/<int:id>', methods=['GET'])
def delete_admin(id):
    sql = "DELETE FROM admin WHERE id=%s"
    connection.cursor.execute(sql, [id])
    connection.con.commit()
    return redirect('/viewadmin')


@app.route('/delete_category/<int:id>', methods=['GET'])
def delete_cate(id):
    sql = "DELETE FROM category WHERE c_id=%s"
    connection.cursor.execute(sql, [id])
    connection.con.commit()
    return redirect('/viewcategory')


@app.route('/editcategory/<int:id>', methods=['GET', 'POST'])
def editcategory(id):
    if request.method == 'POST':
        filename=""
        eid = request.form['id']
        unm = request.form['name']

        if request.files["file"].filename=='':
            filename=request.form["hidden"]
        else:
            file = request.files['file']
            filename = secure_filename(file.filename)
            file.save(os.path.join('static/upload/', filename))
            os.rename('static/upload/' + filename, 'static/upload/' + file.filename)
        connection.cursor.execute("update category set c_name = %s, c_photo = %s WHERE c_id = %s", (unm, filename, eid))
        connection.con.commit()
        return redirect("/viewcategory")
    else:
        connection.cursor.execute("select *  from category where c_id=%s", [id])
        output = connection.cursor.fetchone()
        return render_template("admin/edit_category.html", data=output)


@app.route("/edit_category")
def edit_category():
    return render_template("admin/edit_category.html")


@app.route("/addcategory", methods=['GET', 'POST'])
def addcategory():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join('static/upload', filename))
        os.rename('static/upload/' + filename, 'static/upload/' + file.filename)
        nm = request.form['nm']

        connection.cursor.execute("insert into category(c_name,c_photo) values(%s,%s)", (nm, filename))
        connection.con.commit()
        return redirect("viewcategory")
    else:
        return render_template("admin/addcategory.html")


@app.route("/viewcategory")
def viewcategory():
    # if request.method =="post":
    connection.cursor.execute("select * from category")
    output = connection.cursor.fetchall()
    return render_template("admin/viewcategory.html", data=output)


@app.route("/display/<filename>")
def display_image(filename):
    print('display image' + filename)
    return redirect(url_for('static', filename='upload/' + filename), code=301)


@app.route("/addquestion", methods=['GET', 'POST'])
def addquestion():
    if request.method == 'POST':
        l1 = request.form['list1']
        que = request.form['question']
        a = request.form['a']
        b = request.form['b']
        c = request.form['c']
        d = request.form['d']
        ans = request.form['list2']
        connection.cursor.execute(
            "insert into test(c_id, t_question, t_a, t_b, t_c, t_d, t_ans) values(%s,%s,%s,%s,%s,%s,%s)",
            (l1, que, a, b, c, d, ans))
        connection.con.commit()
        return redirect("/viewquestion")
    else:
        connection.cursor.execute("select *  from category")
        output1 = connection.cursor.fetchall()
        return render_template("admin/addquestion.html", cat=output1)


@app.route('/editquestion/<int:id>', methods=['GET', 'POST'])
def editquestion(id):
    if request.method == 'POST':
        eid = request.form['id']
        cat = request.form['list1']
        que = request.form['question']
        a = request.form['A']
        b = request.form['B']
        c = request.form['C']
        d = request.form['D']
        ans = request.form['list2']
        connection.cursor.execute(
            "update test set c_id = %s , t_question = %s, t_a = %s, t_b =%s , t_c = %s, t_d = %s , t_ans = %s WHERE t_id = %s",
            (cat, que, a, b, c, d, ans, eid))
        connection.con.commit()
        return redirect("/viewquestion")
    else:
        connection.cursor.execute("select *  from test where t_id=%s", [id])
        output = connection.cursor.fetchone()
        connection.cursor.execute("select *  from category")
        output1 = connection.cursor.fetchall()
        return render_template("admin/edit_question.html", data=output, cat=output1)


@app.route("/edit_question")
def edit_question():
    return render_template("admin/edit_question.html")


@app.route('/viewquestion', methods=['GET', 'POST'])
def viewquestion():
    if request.method == 'POST':
        list1 = request.form['list1']
        connection.cursor.execute("select * from test where c_id=%s", [list1])
        output = connection.cursor.fetchall()
        connection.cursor.execute("select * from category")
        output1 = connection.cursor.fetchall()
        return render_template("admin/viewquestion.html", data=output, cat=output1)
    else:
        connection.cursor.execute("select * from test")
        output = connection.cursor.fetchall()
        connection.cursor.execute("select * from category")
        output1 = connection.cursor.fetchall()
        return render_template("admin/viewquestion.html", data=output, cat=output1)


@app.route('/delete_question/<int:id>', methods=['GET'])
def delete_question(id):
    sql = "DELETE FROM test WHERE t_id=%s"
    connection.cursor.execute(sql, [id])
    connection.con.commit()
    return redirect('/viewquestion')


@app.route('/delete_user/<int:id>', methods=['GET'])
def delete_user(id):
    sql = "DELETE FROM register WHERE r_id=%s"
    connection.cursor.execute(sql, [id])
    connection.con.commit()
    return redirect('/viewuser')


@app.route('/delete_feedback/<int:id>', methods=['GET'])
def delete_feedback(id):
    sql = "DELETE FROM contact WHERE id=%s"
    connection.cursor.execute(sql, [id])
    connection.con.commit()
    return redirect('/viewfeedback')


@app.route("/viewuser", methods=['GET'])
def viewuser():
    # if request.method =="post":
    connection.cursor.execute("select * from register")
    output = connection.cursor.fetchall()
    return render_template("admin/viewuser.html", data=output)


@app.route("/viewfeedback", methods=['GET'])
def viewfeedback():
    # if request.method =="post":
    connection.cursor.execute("select * from contact")
    output = connection.cursor.fetchall()
    return render_template("admin/viewfeedback.html", data=output)


if __name__ == "__main__":
    app.run(debug=True)
