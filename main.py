from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

#Bus de eventos

def publicar_evento(nombre_evento, data):

    print(f"Evento publicado: {nombre_evento} con datos: {data}")

    if nombre_evento == "factura_vencida":
        notificar_cliente(data)
        registrar_evento(data)
        log_evento(data)

#Reacciones de los consumidores

def notificar_cliente(data):
    print(f"Notificando al {data['cliente_id']} sobre la factura vencida ({data['dias_mora']} días de mora).")


def registrar_evento(data):
    print(f"Registrando evento de factura vencida para el cliente {data['cliente_id']} en la base de datos.")


def log_evento(data):
    print(f"LOG: evento procesado correctamente")


#Ruta base

@app.route('/')
def home():
    return "API Aquasucre Funcionando..."


#Endpoint principal

@app.route('/facturas', methods=['POST'])
def crear_factura():
    data = request.get_json()
    cliente_id = data.get('cliente_id')
    valor = data.get('valor')
    fecha_vencimiento = data.get('fecha_vencimiento')

    #validación básica
    if not cliente_id or not valor or not fecha_vencimiento:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    
    try:
        fecha_vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d')
        valor = float(valor)
    except ValueError:
        return jsonify({"error": "Formato de fecha invalido. Utiliza 'YYYY-MM-DD'"}), 400
    
    hoy = datetime.now()

    print(f"\n factura recibida para cliente {cliente_id}")


    #logica de negocio

    if hoy > fecha_vencimiento:
        dias_mora = (hoy - fecha_vencimiento).days
        evento = {
            "cliente_id": cliente_id,
            "valor": valor,
            "dias_mora": dias_mora,
            "timestamp": fecha_vencimiento.strftime('%Y-%m-%d'),
            
        }
        publicar_evento("factura_vencida", evento)
        return jsonify({
            "mensaje": f"Factura vencida detectada",
            "evento": "factura_vencida",
            "dias_mora": dias_mora
        }), 200
    
    else:
        return jsonify({"mensaje": "Factura registrada sin mora"}), 200
    
#Ejecucion para render

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
    