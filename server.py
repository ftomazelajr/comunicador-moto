import asyncio
import websockets
import json
import os

usuarios = {"motorista": None, "passageiro": None}

async def gerenciar_conexoes(websocket, path):
    global usuarios
    try:
        async for msg in websocket:
            dados = json.loads(msg)
            tipo_usuario = dados.get("origem")
            
            if tipo_usuario in ["motorista", "passageiro"]:
                usuarios[tipo_usuario] = websocket
            
            destino = "passageiro" if tipo_usuario == "motorista" else "motorista"
            if usuarios[destino] and usuarios[destino].open:
                await usuarios[destino].send(msg)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        for papel, ws in list(usuarios.items()):
            if ws == websocket:
                usuarios[papel] = None

porta = int(os.environ.get("PORT", 8765))
start_server = websockets.serve(gerenciar_conexoes, "0.0.0.0", porta)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

