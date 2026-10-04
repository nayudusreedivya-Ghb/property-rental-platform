from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect("property.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()

    # Property table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            location TEXT NOT NULL,
            property_type TEXT NOT NULL,
            price INTEGER NOT NULL,
            bedrooms INTEGER NOT NULL,
            description TEXT NOT NULL
        )
    """)

    # Inquiry table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS inquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    # Add sample properties
    count = conn.execute(
        "SELECT COUNT(*) FROM properties"
    ).fetchone()[0]

    if count == 0:

        properties = [

            (
                "Modern 2BHK Apartment",
                "Chennai",
                "Apartment",
                18000,
                2,
                "Spacious 2BHK apartment with parking and security."
            ),

            (
                "Luxury 3BHK Flat",
                "Bangalore",
                "Apartment",
                30000,
                3,
                "Modern 3BHK flat located near IT parks."
            ),

            (
                "Single Room",
                "Hyderabad",
                "Room",
                8000,
                1,
                "Affordable single room suitable for students and working professionals."
            ),

            (
                "Independent House",
                "Vijayawada",
                "House",
                22000,
                3,
                "Beautiful independent house with parking facility."
            )
        ]

        for property_data in properties:

            conn.execute("""
                INSERT INTO properties
                (title, location, property_type, price, bedrooms, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, property_data)

    conn.commit()
    conn.close()


# ---------------- HOME ----------------

@app.route("/")
def index():

    conn = get_db()

    properties = conn.execute(
        "SELECT * FROM properties LIMIT 6"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        properties=properties
    )


# ---------------- PROPERTY LIST ----------------

@app.route("/properties")
def properties():

    location = request.args.get("location", "")

    conn = get_db()

    if location:

        property_list = conn.execute(
            """
            SELECT * FROM properties
            WHERE location LIKE ?
            """,
            ("%" + location + "%",)
        ).fetchall()

    else:

        property_list = conn.execute(
            "SELECT * FROM properties"
        ).fetchall()

    conn.close()

    return render_template(
        "properties.html",
        properties=property_list,
        location=location
    )


# ---------------- PROPERTY DETAILS ----------------

@app.route("/property/<int:property_id>")
def details(property_id):

    conn = get_db()

    property_data = conn.execute(
        "SELECT * FROM properties WHERE id = ?",
        (property_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "details.html",
        property=property_data
    )


# ---------------- ADD PROPERTY ----------------

@app.route("/add-property", methods=["GET", "POST"])
def add_property():

    if request.method == "POST":

        title = request.form["title"]
        location = request.form["location"]
        property_type = request.form["property_type"]
        price = request.form["price"]
        bedrooms = request.form["bedrooms"]
        description = request.form["description"]

        conn = get_db()

        conn.execute("""
            INSERT INTO properties
            (title, location, property_type, price, bedrooms, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            title,
            location,
            property_type,
            price,
            bedrooms,
            description
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("properties"))

    return render_template("add_property.html")


# ---------------- RENTAL INQUIRY ----------------

@app.route("/inquiry/<int:property_id>", methods=["GET", "POST"])
def inquiry(property_id):

    conn = get_db()

    property_data = conn.execute(
        "SELECT * FROM properties WHERE id = ?",
        (property_id,)
    ).fetchone()

    conn.close()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        message = request.form["message"]

        conn = get_db()

        conn.execute("""
            INSERT INTO inquiries
            (property_id, name, email, phone, message)
            VALUES (?, ?, ?, ?, ?)
        """, (
            property_id,
            name,
            email,
            phone,
            message
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template(
        "inquiry.html",
        property=property_data
    )


# ---------------- ADMIN ----------------

@app.route("/admin")
def admin():

    conn = get_db()

    inquiries = conn.execute("""
        SELECT
            inquiries.*,
            properties.title
        FROM inquiries
        JOIN properties
        ON inquiries.property_id = properties.id
        ORDER BY inquiries.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        inquiries=inquiries
    )


# ---------------- RUN ----------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)