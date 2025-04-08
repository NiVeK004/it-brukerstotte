from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from models import db, User, Ticket
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
app.config['SECRET_KEY'] = config.SECRET_KEY

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Admin Required Check
def admin_required():
    if current_user.role != "admin":
        abort(403)


@app.route("/admin_tickets")
@login_required
def admin_tickets():
    admin_required()
    # Hvis admin, henter alle henvendelser
    tickets = Ticket.query.all()
    return render_template("admin_tickets.html", tickets=tickets)


@app.route("/")
@login_required
def index():
    tickets = Ticket.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", tickets=tickets)


# Route for user login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)


            # Hvis ikke admin, gå til hovedmeny
            if user.role == "admin":
                return redirect(url_for("admin_tickets"))
            else:
                return redirect(url_for("index"))

        else:
            return redirect(url_for("login"))

    return render_template("login.html")


# Route for logging out
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# Route for creating tickets
@app.route("/create_ticket", methods=["GET", "POST"])
@login_required
def create_ticket():
    if request.method == "POST":
        tittel = request.form["tittel"]
        description = request.form["description"]
        ticket = Ticket(
            tittel=tittel,
            description=description,
            user_id=current_user.id)
        db.session.add(ticket)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("create_ticket.html")


# Route to View a Ticket
@app.route("/ticket/<int:ticket_id>")
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.user_id != current_user.id:
        return redirect(url_for("index"))
    return render_template("view_ticket.html", ticket=ticket)



# Lukke henvendelse
@app.route("/ticket/<int:ticket_id>/close", methods=["POST"])
@login_required
def close_ticket(ticket_id):
    # Check if the user is an admin before closing the ticket
    if current_user.role != "admin":
        return admin_required()  # If not admin, redirect to index

    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.status = "Lukket"
    db.session.commit()  # Commit the changes to the database
    return redirect(url_for("admin_tickets"))  # Redirect back to admin tickets page

# Løse henvendelse
@app.route("/ticket/<int:ticket_id>/resolve", methods=["POST"])
@login_required
def resolve_ticket(ticket_id):
    # Sjekker hvis bruker som løser er Admin
    if current_user.role != "admin":
        return redirect(url_for("index"))
    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.status = "Løst"
    db.session.commit()  # Commit the change to the database
    return redirect(url_for("admin_tickets"))  # Redirect to the admin tickets page




if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

