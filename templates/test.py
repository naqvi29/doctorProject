# @app.route("/CaseView/list", methods=["GET", "POST"])
# def caseviewlist():
#     try:
#         if session.get("status") and session.get("userid") and session.get("username") and session.get("role"):
#             status = session.get("status")
#             message = ""
#             if session.get("message"):
#                 message = session.get("message")
#                 session.pop("message", None)
#             error = ""
#             if session.get("error"):
#                 error = session.get("error")
#                 session.pop("error", None)
#
#             connection = mysql.connect()
#             cur = connection.cursor()
#             cur.execute('''select form_id, title, status, created_at from form;''')
#             data = cur.fetchall()
#             cur.close()
#             connection.close()
#             headers = ["S.NO", "TITLE", "STATUS", "CREATED_AT", "ACTION"]
#             return render_template("caseviewlist.html", status=status, message=message, data=data,
#                                    headers=headers, error=error)
#         else:
#             return redirect(url_for("login"))
#     except Exception as e:
#         error = str(e)
#         return render_template("reportlist.html", error=error)


from werkzeug.security import generate_password_hash, check_password_hash


pas = generate_password_hash('12345')
print(pas)