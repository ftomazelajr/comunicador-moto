import asyncio
import websockets
import json
import os
import http

usuarios = {"motorista": None, "passageiro": None}

# Função para o Render saber que o servidor está vivo via HTTP comum
async def health_check(path, request_headers):
    if path == "/":
        return http.HTTPStatus.OK, [("Content-Type", "text/plain")], b"OK"
    return None

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
    # O Render injeta a porta automaticamente aqui
    porta = int(os.environ.get("PORT", 8765))
    
    # Iniciamos o servidor escutando na porta correta com o validador de saúde ativo
    async with websockets.serve(gerenciar_conexoes, "0.0.0.0", porta, process_request=health_check):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
