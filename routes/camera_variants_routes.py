@app.route("/camera-variants")
def camera_variants():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    variants_query = """
    SELECT
        cv.variant_id,
        cv.variant_name,
        c.camera_name,
        cv.release_year,
        cv.frame_format,
        cv.production_end_year,
        cv.notes
    FROM camera_variants cv
    JOIN cameras c ON cv.camera_id = c.camera_id
    ORDER BY cv.variant_name;
    """

    cameras_query = """
    SELECT camera_id, camera_name
    FROM cameras
    ORDER BY camera_name;
    """

    cursor.execute(variants_query)
    variants = cursor.fetchall()

    cursor.execute(cameras_query)
    cameras = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "camera_variants.html",
        variants=variants,
        cameras=cameras
    )