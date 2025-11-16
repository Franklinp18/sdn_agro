from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# Ledger en memoria: batch_id -> lista de eventos
ledger = {}


@app.route("/events", methods=["POST"])
def add_event():
    data = request.get_json(force=True)
    batch_id = data.get("batch_id")
    event_type = data.get("event_type")
    payload = data.get("payload", {})
    if not batch_id or not event_type:
        return jsonify({"error": "batch_id y event_type son requeridos"}), 400
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    event = {
        "timestamp": ts,
        "event_type": event_type,
        "payload": payload
    }
    ledger.setdefault(batch_id, []).append(event)
    return jsonify({"message": "evento registrado en ledger", "event": event}), 201


@app.route("/events/<batch_id>", methods=["GET"])
def get_events(batch_id):
    return jsonify({"batch_id": batch_id, "events": ledger.get(batch_id, [])})


@app.route("/events", methods=["GET"])
def all_events():
    return jsonify(ledger)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)