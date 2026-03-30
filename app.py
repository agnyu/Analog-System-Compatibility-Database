from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB")
    )
    return connection

@app.route("/")
def index():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT 
        fs.film_id,
        fs.film_name,
        m.manufacturer_name,
        fs.iso,
        ff.format_name,
        fs.color_type,
        fs.release_year,
        fs.discontinued,
        fs.notes
    FROM film_stocks fs
    JOIN manufacturers m ON fs.manufacturer_id = m.manufacturer_id
    JOIN film_formats ff ON fs.format_id = ff.format_id
    ORDER BY fs.film_id;
    """

    cursor.execute(query)
    films = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("index.html", films=films)

@app.route("/add", methods=["GET", "POST"])
def add_film():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM manufacturers ORDER BY manufacturer_name;")
    manufacturers = cursor.fetchall()

    cursor.execute("SELECT * FROM film_formats ORDER BY format_name;")
    formats = cursor.fetchall()

    if request.method == "POST":
        film_name = request.form["film_name"]
        manufacturer_id = request.form["manufacturer_id"]
        iso = request.form["iso"] or None
        format_id = request.form["format_id"]
        color_type = request.form["color_type"] or None
        release_year = request.form["release_year"] or None
        discontinued = 1 if request.form.get("discontinued") == "on" else 0
        notes = request.form["notes"] or None

        insert_query = """
        INSERT INTO film_stocks
        (film_name, manufacturer_id, iso, format_id, color_type, release_year, discontinued, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            film_name, manufacturer_id, iso, format_id,
            color_type, release_year, discontinued, notes
        )

        cursor.execute(insert_query, values)
        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("index"))

    cursor.close()
    connection.close()

    return render_template("add_film.html", manufacturers=manufacturers, formats=formats)

@app.route("/edit/<int:film_id>", methods=["GET", "POST"])
def edit_film(film_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM manufacturers ORDER BY manufacturer_name;")
    manufacturers = cursor.fetchall()

    cursor.execute("SELECT * FROM film_formats ORDER BY format_name;")
    formats = cursor.fetchall()

    cursor.execute("SELECT * FROM film_stocks WHERE film_id = %s;", (film_id,))
    film = cursor.fetchone()

    if request.method == "POST":
        film_name = request.form["film_name"]
        manufacturer_id = request.form["manufacturer_id"]
        iso = request.form["iso"] or None
        format_id = request.form["format_id"]
        color_type = request.form["color_type"] or None
        release_year = request.form["release_year"] or None
        discontinued = 1 if request.form.get("discontinued") == "on" else 0
        notes = request.form["notes"] or None

        update_query = """
        UPDATE film_stocks
        SET film_name = %s,
            manufacturer_id = %s,
            iso = %s,
            format_id = %s,
            color_type = %s,
            release_year = %s,
            discontinued = %s,
            notes = %s
        WHERE film_id = %s
        """
        values = (
            film_name, manufacturer_id, iso, format_id,
            color_type, release_year, discontinued, notes, film_id
        )

        cursor.execute(update_query, values)
        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("index"))

    cursor.close()
    connection.close()

    return render_template(
        "edit_film.html",
        film=film,
        manufacturers=manufacturers,
        formats=formats
    )

@app.route("/delete/<int:film_id>", methods=["POST"])
def delete_film(film_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM film_stocks WHERE film_id = %s;", (film_id,))
    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)