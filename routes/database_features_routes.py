from flask import Blueprint, render_template, request
from db import fetch_all, fetch_one, execute_query

database_features_bp = Blueprint("database_features_bp", __name__)


def load_database_features_context(
    procedure_message=None,
    procedure_error=None,
    variant_workflow_results=None,
    function_result=None
):
    documentation_reference_rows = fetch_all("""
        SELECT
            documentation_id,
            title,
            document_type,
            source,
            publication_year,
            url,
            parent_camera,
            variant_name,
            notes
        FROM vw_documentation_reference
        ORDER BY publication_year DESC, title
        LIMIT 10;
    """)

    film_workflow_rows = fetch_all("""
        SELECT
            development_id,
            film_name,
            box_iso,
            format_name,
            color_type,
            developer_name,
            developer_type,
            shot_iso,
            temperature_celsius,
            dilution,
            development_time_minutes
        FROM vw_film_development_workflow
        ORDER BY film_name, developer_name
        LIMIT 10;
    """)

    variant_compatibility_rows = fetch_all("""
        SELECT
            variant_id,
            variant_name,
            parent_camera,
            frame_format,
            accessory_name,
            accessory_type,
            compatibility_type,
            compatibility_notes,
            accessory_description
        FROM vw_variant_compatibility_overview
        ORDER BY parent_camera, variant_name, accessory_name
        LIMIT 10;
    """)

    accessories = fetch_all("""
        SELECT accessory_id, accessory_name
        FROM accessories
        ORDER BY accessory_name;
    """)

    variants = fetch_all("""
        SELECT variant_id, variant_name
        FROM camera_variants
        ORDER BY variant_name;
    """)

    cameras = fetch_all("""
        SELECT camera_id, camera_name
        FROM cameras
        ORDER BY camera_name;
    """)

    lenses = fetch_all("""
        SELECT lens_id, lens_name
        FROM lenses
        ORDER BY lens_name;
    """)

    camera_audit_rows = fetch_all("""
        SELECT
            camera_audit_id,
            camera_id,
            old_camera_name,
            new_camera_name,
            old_mount_id,
            new_mount_id,
            old_manufacturer_id,
            new_manufacturer_id,
            old_camera_type,
            new_camera_type,
            changed_at
        FROM camera_audit
        ORDER BY changed_at DESC
        LIMIT 15;
    """)

    film_development_guide_audit_rows = fetch_all("""
        SELECT
            audit_id,
            development_id,
            old_film_id,
            new_film_id,
            old_developer_id,
            new_developer_id,
            old_temperature_celsius,
            new_temperature_celsius,
            old_dilution,
            new_dilution,
            changed_at
        FROM film_development_guide_audit
        ORDER BY changed_at DESC
        LIMIT 15;
    """)

    return {
        "documentation_reference_rows": documentation_reference_rows,
        "film_workflow_rows": film_workflow_rows,
        "variant_compatibility_rows": variant_compatibility_rows,
        "accessories": accessories,
        "variants": variants,
        "cameras": cameras,
        "lenses": lenses,
        "camera_audit_rows": camera_audit_rows,
        "film_development_guide_audit_rows": film_development_guide_audit_rows,
        "procedure_message": procedure_message,
        "procedure_error": procedure_error,
        "variant_workflow_results": variant_workflow_results or [],
        "function_result": function_result
    }


@database_features_bp.route("/database-features")
def database_features():
    context = load_database_features_context()
    return render_template("database_features.html", **context)


@database_features_bp.route("/database-features/run-add-accessory-compatibility", methods=["POST"])
def run_add_accessory_compatibility():
    accessory_id = request.form.get("accessory_id", type=int)
    variant_id = request.form.get("variant_id", type=int)
    compatibility_type = request.form.get("compatibility_type", type=str)
    notes = request.form.get("notes", type=str)

    procedure_message = None
    procedure_error = None

    try:
        execute_query(
            "CALL sp_add_accessory_compatibility(%s, %s, %s, %s);",
            (
                accessory_id,
                variant_id,
                compatibility_type if compatibility_type else None,
                notes if notes else None
            )
        )
        procedure_message = "Accessory compatibility procedure executed successfully."
    except Exception as e:
        procedure_error = str(e)

    context = load_database_features_context(
        procedure_message=procedure_message,
        procedure_error=procedure_error
    )
    return render_template("database_features.html", **context)


@database_features_bp.route("/database-features/run-variant-film-workflow", methods=["POST"])
def run_variant_film_workflow():
    variant_id = request.form.get("variant_id", type=int)

    procedure_message = None
    procedure_error = None
    variant_workflow_results = []

    try:
        variant_workflow_results = fetch_all(
            "CALL sp_get_variant_film_workflow(%s);",
            (variant_id,)
        )
        procedure_message = "Variant film workflow procedure executed successfully."
    except Exception as e:
        procedure_error = str(e)

    context = load_database_features_context(
        procedure_message=procedure_message,
        procedure_error=procedure_error,
        variant_workflow_results=variant_workflow_results
    )
    return render_template("database_features.html", **context)


@database_features_bp.route("/database-features/run-lens-camera-function", methods=["POST"])
def run_lens_camera_function():
    camera_id = request.form.get("camera_id", type=int)
    lens_id = request.form.get("lens_id", type=int)

    function_result = None
    procedure_error = None

    try:
        result_row = fetch_one("""
            SELECT fn_is_lens_compatible_with_camera(%s, %s) AS compatibility_result;
        """, (camera_id, lens_id))

        if result_row:
            function_result = result_row["compatibility_result"]
        else:
            function_result = "No result returned."
    except Exception as e:
        procedure_error = str(e)

    context = load_database_features_context(
        procedure_error=procedure_error,
        function_result=function_result
    )
    return render_template("database_features.html", **context)