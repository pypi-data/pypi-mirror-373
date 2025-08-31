import asyncio

from wiliot_tools.test_equipment.test_equipment import CognexNetwork


async def main():
    print('cognex network')
    c = CognexNetwork(ip_address='192.168.111.2')
    while not c.connected:
        print("Waiting for connection...")
        await asyncio.sleep(0.5)

    await c.trigger_on(continuously=True)

    print('Waiting 5 seconds for barcode scan...')
    await asyncio.sleep(5)

    ex_id = await c.read_batch(n_msg=10)
    print(f"Extracted IDs: {ex_id}")

    await c.trigger_off()
    await c.close_port()
    print('Done')


if __name__ == '__main__':
    asyncio.run(main())