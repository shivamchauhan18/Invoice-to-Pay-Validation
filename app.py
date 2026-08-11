from flask import Flask, render_template, request, jsonify, Response
from werkzeug.utils import secure_filename
from pathlib import Path
import json

from main import app


# ==================================================
# Flask application
# ==================================================

flask_app = Flask(__name__)


# ==================================================
# Upload folder
# ==================================================

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


# ==================================================
# LangGraph node information
# ==================================================

NODE_INFO = {
    "extract": {
        "message": "Extracting details from Invoice and Purchase Order",
        "progress": 25
    },

    "invoice_schema": {
        "message": "Extracting structured details from Invoice",
        "progress": 50
    },

    "po_schema": {
        "message": "Extracting structured details from Purchase Order",
        "progress": 75
    },

    "validation": {
        "message": "Comparing Invoice with Purchase Order",
        "progress": 100
    }
}


# ==================================================
# Home page
# ==================================================

@flask_app.route("/")
def home():

    return render_template("index.html")


# ==================================================
# Validate Invoice + PO
# ==================================================

@flask_app.route("/validate", methods=["POST"])
def validate():

    invoice_file = request.files.get("invoice")
    po_file = request.files.get("po")


    # ------------------------------------------------
    # Check uploaded files
    # ------------------------------------------------

    if not invoice_file or not po_file:

        return jsonify({
            "success": False,
            "error": "Please upload both Invoice and PO."
        }), 400


    if not invoice_file.filename:

        return jsonify({
            "success": False,
            "error": "Invoice file is missing."
        }), 400


    if not po_file.filename:

        return jsonify({
            "success": False,
            "error": "Purchase Order file is missing."
        }), 400


    # ------------------------------------------------
    # Secure filenames
    # ------------------------------------------------

    invoice_filename = secure_filename(
        invoice_file.filename
    )

    po_filename = secure_filename(
        po_file.filename
    )


    # ------------------------------------------------
    # Create paths
    # ------------------------------------------------

    invoice_path = (
        UPLOAD_FOLDER / invoice_filename
    )

    po_path = (
        UPLOAD_FOLDER / po_filename
    )


    # ------------------------------------------------
    # Save files
    # ------------------------------------------------

    invoice_file.save(invoice_path)

    po_file.save(po_path)


    # =================================================
    # Streaming generator
    # =================================================

    def generate():

        try:

            # -----------------------------------------
            # Start message
            # -----------------------------------------

            yield json.dumps({
                "type": "start",
                "message": "Starting Invoice-to-Pay validation",
                "progress": 0
            }) + "\n"


            # -----------------------------------------
            # Run LangGraph
            # -----------------------------------------

            for event in app.stream({

                "invoice_path": str(invoice_path),

                "po_path": str(po_path)

            }):


                # event contains the node that
                # has just completed

                for node_name, output in event.items():


                    # ---------------------------------
                    # Ignore unknown nodes
                    # ---------------------------------

                    if node_name not in NODE_INFO:

                        continue


                    node_info = NODE_INFO[node_name]


                    # ---------------------------------
                    # Basic progress information
                    # ---------------------------------

                    response_data = {

                        "type": "progress",

                        "node": node_name,

                        "message": node_info["message"],

                        "progress": node_info["progress"]

                    }


                    # =================================
                    # EXTRACT NODE
                    # =================================
                    #
                    # Send only Markdown to frontend.
                    #
                    # Do NOT send the complete node
                    # output because it may contain
                    # unnecessary internal state.
                    # =================================

                    if node_name == "extract":

                        response_data["invoice_markdown"] = (
                            output.get("invoice_text", "")
                        )

                        response_data["po_markdown"] = (
                            output.get("po_text", "")
                        )


                    # =================================
                    # VALIDATION NODE
                    # =================================

                    if node_name == "validation":

                        response_data["validation"] = (
                            output.get("validation")
                        )


                    # ---------------------------------
                    # Send one NDJSON line
                    # ---------------------------------

                    yield json.dumps(
                        response_data,
                        default=str
                    ) + "\n"


            # =================================================
            # Graph completed
            # =================================================

            yield json.dumps({

                "type": "complete",

                "message":
                    "Invoice-to-Pay validation completed",

                "progress": 100

            }) + "\n"


        except Exception as e:


            # =================================================
            # Error
            # =================================================

            yield json.dumps({

                "type": "error",

                "message": str(e),

                "progress": 0

            }) + "\n"


    # ==================================================
    # Return streaming response
    # ==================================================

    return Response(

        generate(),

        mimetype="application/x-ndjson",

        headers={

            "Cache-Control": "no-cache",

            "X-Accel-Buffering": "no-cache"

        }

    )


# ==================================================
# Run Flask
# ==================================================

if __name__ == "__main__":

    flask_app.run(

        host="0.0.0.0",

        port=5001,

        debug=True,

        threaded=True

    )