from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

development_guide_bp = Blueprint("development_guide_bp", __name__)


@development_guide_bp.route("/development-guide")
def development_guide():
    search = request.args.get("search", type=str)
    film_id = request.args.get("film_id", type=int)
    developer_id = request.args.get("developer_id", type=int)
    shot_iso = request.args.get("shot_iso", type=int)
    dilution = request.args.get("dilution", type=str)
    temp_min = request.args.get("temp_min", type=float)
    temp_max = request.args.get("temp_max", type=float)
    time_min = request.args.get("time_min", type=float)
    time_max = request.args.get("time_max", type=float)
    selected_development_id = request.args.get("selected_development_id", type=int)

    mode = request.args.get("mode")

    films_query = """
    SELECT film_id, film_name
    FROM film_stocks
    ORDER BY film_name;
    """

    developers_query = """
    SELECT developer_id, developer_name
    FROM film_developers
    ORDER BY developer_name;
    """

    dilutions_query = """
    SELECT DISTINCT dilution
    FROM film_development_guide
    WHERE dilution IS NOT NULL
      AND TRIM(dilution) <> ''
    ORDER BY dilution;
    """

    guides_query = """
    SELECT
        fdg.development_id,
        fdg.film_id,
        fs.film_name,
        fdg.developer_id,
        fd.developer_name,
        fdg.temperature_celsius,
        fdg.dilution,
        fdg.shot_iso,
        fdg.development_time_minutes,
        fdg.agitation_notes,
        fdg.notes
    FROM film_development_guide fdg
    JOIN film_stocks fs ON fdg.film_id = fs.film_id
    JOIN film_developers fd ON fdg.developer_id = fd.developer_id
    WHERE 1=1
    """

    values = []

    if search and search.strip():
        search_term = f"%{search.strip()}%"
        guides_query += """
        AND (
            fs.film_name LIKE %s
            OR fd.developer_name LIKE %s
            OR COALESCE(fdg.dilution, '') LIKE %s
            OR COALESCE(fdg.agitation_notes, '') LIKE %s
            OR COALESCE(fdg.notes, '') LIKE %s
        )
        """
        values.extend([search_term, search_term, search_term, search_term, search_term])

    if film_id:
        guides_query += " AND fdg.film_id = %s"
        values.append(film_id)

    if developer_id:
        guides_query += " AND fdg.developer_id = %s"
        values.append(developer_id)

    if shot_iso:
        guides_query += " AND fdg.shot_iso = %s"
        values.append(shot_iso)

    if dilution:
        guides_query += " AND fdg.dilution = %s"
        values.append(dilution)

    if temp_min is not None:
        guides_query += " AND fdg.temperature_celsius >= %s"
        values.append(temp_min)

    if temp_max is not None:
        guides_query += " AND fdg.temperature_celsius <= %s"
        values.append(temp_max)

    if time_min is not None:
        guides_query += " AND fdg.development_time_minutes >= %s"
        values.append(time_min)

    if time_max is not None:
        guides_query += " AND fdg.development_time_minutes <= %s"
        values.append(time_max)

    if selected_development_id:
        guides_query += " AND fdg.development_id = %s"
        values.append(selected_development_id)

    guides_query += " ORDER BY fs.film_name, fd.developer_name;"

    guides = fetch_all(guides_query, tuple(values))
    films = fetch_all(films_query)
    developers = fetch_all(developers_query)
    dilutions = fetch_all(dilutions_query)

    selected_guide = None
    linked_film = None
    linked_developer = None

    if selected_development_id:
        selected_guide = fetch_one("""
            SELECT
                fdg.development_id,
                fdg.film_id,
                fs.film_name,
                fdg.developer_id,
                fd.developer_name,
                fdg.temperature_celsius,
                fdg.dilution,
                fdg.shot_iso,
                fdg.development_time_minutes,
                fdg.agitation_notes,
                fdg.notes
            FROM film_development_guide fdg
            JOIN film_stocks fs ON fdg.film_id = fs.film_id
            JOIN film_developers fd ON fdg.developer_id = fd.developer_id
            WHERE fdg.development_id = %s;
        """, (selected_development_id,))

        if selected_guide:
            linked_film = fetch_one("""
                SELECT
                    fs.film_id,
                    fs.film_name,
                    m.manufacturer_name,
                    ff.format_name,
                    fs.iso,
                    fs.color_type,
                    fs.release_year,
                    fs.discontinued,
                    fs.notes
                FROM film_stocks fs
                JOIN manufacturers m ON fs.manufacturer_id = m.manufacturer_id
                JOIN film_formats ff ON fs.format_id = ff.format_id
                WHERE fs.film_id = %s;
            """, (selected_guide["film_id"],))

            linked_developer = fetch_one("""
                SELECT
                    d.developer_id,
                    d.developer_name,
                    m.manufacturer_name,
                    d.developer_type,
                    d.notes
                FROM film_developers d
                JOIN manufacturers m ON d.manufacturer_id = m.manufacturer_id
                WHERE d.developer_id = %s;
            """, (selected_guide["developer_id"],))

    browse_params = {
        "search": search,
        "film_id": film_id,
        "developer_id": developer_id,
        "shot_iso": shot_iso,
        "dilution": dilution,
        "temp_min": temp_min,
        "temp_max": temp_max,
        "time_min": time_min,
        "time_max": time_max
    }

    return render_template(
        "development_guide.html",
        guides=guides,
        films=films,
        developers=developers,
        dilutions=dilutions,
        guide_to_edit=None,
        mode=mode,
        selected_guide=selected_guide,
        linked_film=linked_film,
        linked_developer=linked_developer,
        selected_search=search,
        selected_film_id=film_id,
        selected_developer_id=developer_id,
        selected_shot_iso=shot_iso,
        selected_dilution=dilution,
        selected_temp_min=temp_min,
        selected_temp_max=temp_max,
        selected_time_min=time_min,
        selected_time_max=time_max,
        browse_params=browse_params
    )


@development_guide_bp.route("/development-guide/edit/<int:development_id>")
def edit_development_guide(development_id):
    guides_query = """
    SELECT
        fdg.development_id,
        fdg.film_id,
        fs.film_name,
        fdg.developer_id,
        fd.developer_name,
        fdg.temperature_celsius,
        fdg.dilution,
        fdg.shot_iso,
        fdg.development_time_minutes,
        fdg.agitation_notes,
        fdg.notes
    FROM film_development_guide fdg
    JOIN film_stocks fs ON fdg.film_id = fs.film_id
    JOIN film_developers fd ON fdg.developer_id = fd.developer_id
    ORDER BY fs.film_name, fd.developer_name;
    """

    films_query = """
    SELECT film_id, film_name
    FROM film_stocks
    ORDER BY film_name;
    """

    developers_query = """
    SELECT developer_id, developer_name
    FROM film_developers
    ORDER BY developer_name;
    """

    dilutions_query = """
    SELECT DISTINCT dilution
    FROM film_development_guide
    WHERE dilution IS NOT NULL
      AND TRIM(dilution) <> ''
    ORDER BY dilution;
    """

    guides = fetch_all(guides_query)
    films = fetch_all(films_query)
    developers = fetch_all(developers_query)
    dilutions = fetch_all(dilutions_query)

    guide_to_edit = fetch_one(
        "SELECT * FROM film_development_guide WHERE development_id = %s;",
        (development_id,)
    )

    return render_template(
        "development_guide.html",
        guides=guides,
        films=films,
        developers=developers,
        dilutions=dilutions,
        guide_to_edit=guide_to_edit,
        mode=None,
        selected_guide=None,
        linked_film=None,
        linked_developer=None,
        selected_search=None,
        selected_film_id=None,
        selected_developer_id=None,
        selected_shot_iso=None,
        selected_dilution=None,
        selected_temp_min=None,
        selected_temp_max=None,
        selected_time_min=None,
        selected_time_max=None,
        browse_params={}
    )


@development_guide_bp.route("/development-guide/add", methods=["POST"])
def add_development_guide():
    film_id = request.form["film_id"]
    developer_id = request.form["developer_id"]
    temperature_celsius = request.form["temperature_celsius"] or None
    dilution = request.form["dilution"] or None
    shot_iso = request.form["shot_iso"] or None
    development_time_minutes = request.form["development_time_minutes"] or None
    agitation_notes = request.form["agitation_notes"] or None
    notes = request.form["notes"] or None

    insert_query = """
    INSERT INTO film_development_guide
    (film_id, developer_id, temperature_celsius, dilution, shot_iso, development_time_minutes, agitation_notes, notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        film_id,
        developer_id,
        temperature_celsius,
        dilution,
        shot_iso,
        development_time_minutes,
        agitation_notes,
        notes
    )

    execute_query(insert_query, values)
    return redirect(url_for("development_guide_bp.development_guide"))


@development_guide_bp.route("/development-guide/update/<int:development_id>", methods=["POST"])
def update_development_guide(development_id):
    film_id = request.form["film_id"]
    developer_id = request.form["developer_id"]
    temperature_celsius = request.form["temperature_celsius"] or None
    dilution = request.form["dilution"] or None
    shot_iso = request.form["shot_iso"] or None
    development_time_minutes = request.form["development_time_minutes"] or None
    agitation_notes = request.form["agitation_notes"] or None
    notes = request.form["notes"] or None

    update_query = """
    UPDATE film_development_guide
    SET film_id = %s,
        developer_id = %s,
        temperature_celsius = %s,
        dilution = %s,
        shot_iso = %s,
        development_time_minutes = %s,
        agitation_notes = %s,
        notes = %s
    WHERE development_id = %s
    """

    values = (
        film_id,
        developer_id,
        temperature_celsius,
        dilution,
        shot_iso,
        development_time_minutes,
        agitation_notes,
        notes,
        development_id
    )

    execute_query(update_query, values)
    return redirect(url_for("development_guide_bp.development_guide"))


@development_guide_bp.route("/development-guide/delete/<int:development_id>", methods=["POST"])
def delete_development_guide(development_id):
    execute_query(
        "DELETE FROM film_development_guide WHERE development_id = %s;",
        (development_id,)
    )
    return redirect(url_for("development_guide_bp.development_guide"))