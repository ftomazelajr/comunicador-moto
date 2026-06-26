import asyncio
import websockets
import json
import os

usuarios = {"motorista": None, "passageiro": None}

async def gerenciar_conexoes(websocket):
    global usuarios
    try:
        async for msg in websocket:
            dados = json.loads(msg)
            tipo_usuario = dados.get("origem")
            
            if tipo_usuario in ["motorista", "passageiro"]:
                usuarios[tipo_usuario] = websocket
            
            destino = "passageiro" if tipo_usuario == "motorista" else "motorista"
            if usuarios[destino]:
                await usuarios[destino].send(msg)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        for papel, ws in list(usuarios.items()):
            if ws == websocket:
                usuarios[papel] = None

async def main():
    porta = int(os.environ.get("PORT", 8765))
    async with websockets.serve(gerenciar_conexoes, "0.0.0.0", porta):
        await asyncio.Future()  # Mantém o servidor rodando para sempre

if __name__ == "__main__":
    asyncio.run(main())
