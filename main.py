import random
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

##Connect to Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random", methods=["GET"])
def random_entry():
    results = db.session.query(Cafe).all()
    random_cafe = random.choice(results)
    cafe_dict = {
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price,
        "has_sockets": random_cafe.has_sockets,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "id": random_cafe.id,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "map_url": random_cafe.map_url,
        "name": random_cafe.name,
        "seats": random_cafe.seats,
    }
    cafe_json = jsonify(cafe=cafe_dict)
    return cafe_json


# Search
@app.route("/search", methods=["GET"])
def search():
    location = request.args.get("loc")
    results = Cafe.query.filter_by(location=location).all()
    cafe_list = []
    if len(results) < 1:
        return jsonify(error={"Not Found": "No cafes found at this location"})
    for cafe in results:
        cafe_list.append(cafe.to_dict())
    return jsonify(cafes=cafe_list)


## HTTP GET - Read Record
@app.route("/all", methods=["GET"])
def all():
    results = db.session.query(Cafe).all()
    cafe_list = []
    for cafe in results:
        cafe_list.append(cafe.to_dict())
    return jsonify(cafes=cafe_list)


## HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["PUT"])
def update_price(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if cafe:
        new_price = request.args.get("new_price")
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(success="Successfully updated the price"), 200
    else:
        return (
            jsonify(
                error={
                    "Not Found": "Sorry, a cafe with that id was not found in the database"
                }
            ),
            404,
        )


## HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def report_closed(cafe_id):
    key = request.args.get("api-key")
    cafe = Cafe.query.get(cafe_id)
    if cafe:
        if key == "auth_key":
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(success="Cafe deleted")
        else:
            return jsonify(error="Sorrty, that's not allowed."), 403
    return (
        jsonify(
            error={
                "Not Found": "Sorry, a cafe with that id was not found in the database"
            }
        ),
        404,
    )


if __name__ == "__main__":
    app.run(debug=True)
