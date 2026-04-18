from flask import Flask, jsonify, render_template, request

import SITA_module

app = Flask(__name__)
server = app


def _matrix_to_csv(matrix):
    return "\n".join(",".join(f"{v:g}" for v in row) for row in matrix)


def _json_error(message, status=400):
    return jsonify({"error": str(message)}), status


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/matrix")
def api_matrix():
    payload = request.get_json(silent=True) or {}
    formula = (payload.get("formula") or "").strip()
    backbone_c = payload.get("backbone_c")

    if not formula:
        return _json_error("formula is required")
    if backbone_c is None or backbone_c == "":
        return _json_error("backbone_c is required")
    try:
        backbone_c = int(backbone_c)
    except (TypeError, ValueError):
        return _json_error("backbone_c must be an integer")

    try:
        matrix = SITA_module.LabelledCompound(
            formula=formula, labelled_element="C", backbone_c=backbone_c
        ).correction_matrix()
    except (ValueError, KeyError) as exc:
        return _json_error(exc)

    rows = matrix.tolist()
    return jsonify({"matrix": rows, "csv": _matrix_to_csv(rows)})


@app.post("/api/mdv-star")
def api_mdv_star():
    payload = request.get_json(silent=True) or {}
    formula = (payload.get("formula") or "").strip()
    backbone_c = payload.get("backbone_c")
    mdv = (payload.get("mdv") or "").strip()

    if not formula:
        return _json_error("formula is required")
    if backbone_c is None or backbone_c == "":
        return _json_error("backbone_c is required")
    if not mdv:
        return _json_error("measured mdv is required")
    try:
        backbone_c = int(backbone_c)
    except (TypeError, ValueError):
        return _json_error("backbone_c must be an integer")

    try:
        mdv_star = SITA_module.LabelledCompound(
            formula=formula,
            labelled_element="C",
            backbone_c=backbone_c,
            mdv_a=mdv,
        ).mdv_star()
    except (ValueError, KeyError) as exc:
        return _json_error(exc)

    rows = mdv_star.tolist()
    return jsonify({"mdv_star": rows, "csv": _matrix_to_csv(rows)})


if __name__ == "__main__":
    app.run(debug=True)
