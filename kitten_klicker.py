import aiohttp.web
import aiohttp_jinja2
import asyncio
import jinja2
import json
import threading
import time


class Building(object):
    def __init__(self, name, price, prod):
        self.name = name
        self.price = price
        self.prod = prod

    def __repr__(self):
        return 'Building(name={}, price={}, prod={})'.format(
                self.name, self.price, self.prod)


class ClickHandler(object):
    def __init__(self, ws, stats):
        self.ws = ws
        self.stats = stats

    async def start(self):
        async for msg in self.ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await self.ws.close()
                else:
                    await self.handle_click(msg.data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' %
                      self.ws.exception())

    async def handle_click(self, data):
        if data.startswith('store_'):
            self.visit_store(data)
        else:
            with self.stats.kitten_count_lock:
                self.stats.kitten_count += 1
        await self.ws.send_str(self.stats.to_json())

    def visit_store(self, data):
        try:
            selection = data.split('_')[1]
            selection = self.stats.store[int(selection)]
        except (ValueError, KeyError):
            return

        if self.stats.kitten_count < selection.price:
            return

        with self.stats.kitten_count_lock:
            self.stats.kitten_count -= selection.price
        self.stats.prod_per_sec += selection.prod


class GameEngine(threading.Thread):
    def __init__(self, ws, stats, *args, **kwargs):
        super(GameEngine, self).__init__(*args, **kwargs)
        self.daemon = True

        self._update_cycle = 1.0
        self.ws = ws
        self.stats = stats
        self.loop = asyncio.get_event_loop()

    async def update(self):
        with self.stats.kitten_count_lock:
            self.stats.kitten_count += self.stats.prod_per_sec

        await self.ws.send_str(self.stats.to_json())

    def run(self):
        update_delta = self._update_cycle

        while not self.ws.closed:
            time.sleep(update_delta)

            start_time = time.time()
            asyncio.run_coroutine_threadsafe(self.update(), self.loop)

            elapsed_time = time.time() - start_time
            update_delta = self._update_cycle - elapsed_time


class Stats(object):

    store = [
        Building(name='Empty Box', price=10, prod=1),
        Building(name='Scratching Post', price=100, prod=10),
        Building(name='Kitten Perch', price=1000, prod=100),
        Building(name='Delux Scratching Post', price=10000, prod=1000),
        Building(name='Delux Kitten Perch', price=100000, prod=10000),
        Building(name='Kitten Hotel', price=1000000, prod=100000),
    ]

    def __init__(self):
        self.kitten_count = 0
        self.kitten_count_lock = threading.Lock()

        self.prod_per_sec = 0

    def to_json(self):
        return json.dumps({
            'kitten_count': self.kitten_count,
            'prod_per_sec': self.prod_per_sec,
        })


async def ws_communicate(request):
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)

    # Create the stats object
    stats = Stats()

    # Start the game engine which holds the ioloop
    game_engine = GameEngine(ws, stats)
    game_engine.start()

    # Start the click handler which listens for click events
    click_handler = ClickHandler(ws, stats)
    await click_handler.start()

    return ws


@aiohttp_jinja2.template('index.html')
async def game(request):
    return {
        'store': Stats.store,
    }


if __name__ == '__main__':
    app = aiohttp.web.Application()
    app.router.add_static('/static', 'static')
    aiohttp_jinja2.setup(app,
            loader=jinja2.FileSystemLoader('templates'))

    app.router.add_get('/ws', ws_communicate)
    app.router.add_get('/', game)

    aiohttp.web.run_app(app)
