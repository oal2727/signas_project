activar:

.\env\Scripts\activate

# Actualmente al estar dentro del .env no me permita usar mediapipe
# requerido trabajar sin env por investigar

# socket room:
https://socket.io/docs/v3/rooms/index.html
socket.to

socket.on (escuchar dato emitido)
socket.emmit (emitir ya sea desde cliente o servidor)
socket.off (remover data)

'''
@socketio.on("connect")
def connected():
    """event listener when client connects to the server"""
    print(request.sid)
    print("client has connected")
    # emit("connect",{"data":f"id: {request.sid} is connected"})

@socketio.on('data')
def handle_message(data):
    """event listener when client types a message"""
    print("data from the front end: ",str(data))
    emit("data",{'data':data,'id':request.sid},broadcast=True)
@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the server"""
    print("user disconnected")
'''

# Nota sobre sockets
1. la conexion del socket con lleva de lo siguiente:
* 

python3 detection.py --image image.jpg