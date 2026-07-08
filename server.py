import asyncio
import os
import websockets

clients = {}  # websocket -> nickname

async def broadcast(message, exclude=None):
    dead = []
    for ws in list(clients.keys()):
        if ws is exclude:
            continue
        try:
            await ws.send(message)
        except Exception:
            dead.append(ws)
    for ws in dead:
        clients.pop(ws, None)

async def handler(ws):
    nickname = None
    try:
        # İlk mesaj = nickname (client "nick\n" yolluyor)
        first = await ws.recv()
        nickname = first.strip().split("\n", 1)[0][:20] or "Anonim"
        clients[ws] = nickname
        print(f"[+] {nickname} bağlandı ({len(clients)} online)")
        await broadcast(f"*** {nickname} kanala katıldı ***", exclude=ws)

        async for raw in ws:
            for line in raw.split("\n"):
                line = line.strip()
                if not line:
                    continue
                await broadcast(f"{nickname}: {line}", exclude=ws)
    except Exception as e:
        print(f"[!] {nickname}: {e}")
    finally:
        clients.pop(ws, None)
        if nickname:
            print(f"[-] {nickname} ayrıldı")
            await broadcast(f"*** {nickname} ayrıldı ***")

async def main():
    port = int(os.environ.get("PORT", 5555))
    print(f"WebSocket server dinleniyor: 0.0.0.0:{port}")
    async with websockets.serve(handler, "0.0.0.0", port, ping_interval=30):
        await asyncio.Future()  # forever

if __name__ == "__main__":
    asyncio.run(main())
