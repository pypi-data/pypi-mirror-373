import asyncio
import cobalt_sdk
from cobalt_sdk import Objects


async def main():
    MAX_FRAMES = 100
    with open("objects.csv", "w+") as w:
        w.write("frame,id,heading,px,py")
        async with cobalt_sdk.data_connect() as h3:
            await cobalt_sdk.subscribe_objects(h3)

            frame_num = 0
            while frame_num < MAX_FRAMES:
                async with asyncio.timeout(5):
                    data = await h3.recv()
                    print("Write objects")
                    objects = Objects.from_bytes(data)

                    for obj in objects.objects:
                        w.write(
                            f"{frame_num},{obj.object_id},{obj.theta},{obj.x},{obj.y}\n"
                        )
                    frame_num += 1


if __name__ == "__main__":
    asyncio.run(main())
