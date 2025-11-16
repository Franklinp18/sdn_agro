from flask import Flask, request, jsonify
import time
import requests

app = Flask(__name__)

# Dirección del nodo ledger (blockchain)
BLOCKCHAIN_URL = "http://10.0.2.13:6000"

# Bases de datos en memoria
batches = {}  # batch_id -> info del lote
events = {}   # batch_id -> lista de eventos
invoices = {} # invoice_id -> info de factura


def add_event(batch_id, event_type, payload=None):
    """
    Registra un evento localmente y lo envía al servicio ledger.
    """
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    ev = {
        "timestamp": ts,
        "event_type": event_type,
        "payload": payload or {}
    }
    events.setdefault(batch_id, []).append(ev)

    # Enviar al servicio ledger
    try:
        bc_payload = {
            "batch_id": batch_id,
            "event_type": event_type,
            "payload": payload or {}
        }
        requests.post(f"{BLOCKCHAIN_URL}/events", json=bc_payload, timeout=2)
    except Exception as e:
        print(f"[WARN] No se pudo enviar evento a blockchain: {e}")


@app.route("/batches", methods=["POST"])
def create_batch():
    data = request.get_json(force=True)
    batch_id = data.get("batch_id")
    if not batch_id:
        return jsonify({"error": "batch_id requerido"}), 400
    if batch_id in batches:
        return jsonify({"error": "batch_id ya existe"}), 400

    batches[batch_id] = {
        "product": data.get("product", "unknown"),
        "farm": data.get("farm", "unknown"),
        "extra": data.get("extra", {})
    }
    add_event(batch_id, "CREATED", {"product": batches[batch_id]["product"]})
    return jsonify({"message": "batch creado", "batch": batches[batch_id]}), 201


@app.route("/batches", methods=["GET"])
def list_batches():
    return jsonify(batches)


@app.route("/sensor-data", methods=["POST"])
def sensor_data():
    data = request.get_json(force=True)
    batch_id = data.get("batch_id")
    if batch_id not in batches:
        return jsonify({"error": "batch_id no existe"}), 400
    add_event(batch_id, "SENSOR_UPDATE", data)
    return jsonify({"message": "sensor data registrado"}), 200


@app.route("/batches/<batch_id>/move", methods=["POST"])
def move_batch(batch_id):
    if batch_id not in batches:
        return jsonify({"error": "batch_id no existe"}), 400
    data = request.get_json(force=True)
    status = data.get("status")
    if not status:
        return jsonify({"error": "status requerido"}), 400
    batches[batch_id]["status"] = status
    add_event(batch_id, "STATUS_CHANGE", {"status": status})
    return jsonify({"message": "estado actualizado", "batch": batches[batch_id]}), 200


@app.route("/invoices", methods=["POST"])
def create_invoice():
    data = request.get_json(force=True)
    invoice_id = data.get("invoice_id")
    batch_id = data.get("batch_id")
    if not invoice_id or not batch_id:
        return jsonify({"error": "invoice_id y batch_id requeridos"}), 400
    if batch_id not in batches:
        return jsonify({"error": "batch_id no existe"}), 400
    if invoice_id in invoices:
        return jsonify({"error": "invoice_id ya existe"}), 400
    invoices[invoice_id] = {
        "batch_id": batch_id,
        "amount": data.get("amount", 0),
        "buyer": data.get("buyer", "unknown")
    }
    add_event(batch_id, "INVOICED", {"invoice_id": invoice_id})
    return jsonify({"message": "factura creada", "invoice": invoices[invoice_id]}), 201


@app.route("/trace/<batch_id>", methods=["GET"])
def trace_batch(batch_id):
    if batch_id not in batches:
        return jsonify({"error": "batch_id no existe"}), 400
    return jsonify({"batch": batches[batch_id], "events": events.get(batch_id, [])})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)