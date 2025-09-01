import cobalt_sdk
import asyncio
from websockets import ClientConnection

"""This script assumes we have an active pipeline. It connects with the python API,
and prints out some information about the object."""

"""このスクリプトはアクティブなパイプラインが実行中であることを前提としています。
Python APIを使用して接続し、オブジェクトに関する情報を出力します。"""


async def main():
    ws: ClientConnection
    async with cobalt_sdk.data_connect() as ws:
        # Tell the perception to start sending objects to this websocket connection
        # 認識システムにこのWebSocket接続にオブジェクトの送信を開始するよう指示します
        await cobalt_sdk.subscribe_objects(ws)

        while True:
            async with asyncio.timeout(1):
                data = await ws.recv()
                objects = cobalt_sdk.Objects.from_bytes(data)
                print(f"Got {objects.num_objects} object")
                if objects.num_objects > 0:
                    obj: cobalt_sdk.Object = objects.objects[0]
                    print(
                        f"ID: {obj.object_id}. X={obj.x:.2f}, Y={obj.y:.2f}, Z={obj.z:.2f}"
                    )


asyncio.run(main())
