import collections
import os
import threading
import time


def _clear():
    os.system('cls' if os.name == 'nt' else 'clear')


class Building(object):
    def __init__(self, name, price, prod):
        self.name = name
        self.price = price
        self.prod = prod

    def __repr__(self):
        return 'Building(name={}, price={}, prod={})'.format(
                self.name, self.price, self.prod)


class ClickHandler(object):
    def __init__(self, stats):
        self.stats = stats

    def start(self):
        _clear()
        while True:
            click = input(
                'Press "s" to visit the store, otherwise attract a kitten\n')
            if click == 's':
                self.visit_store()
            else:
                with self.stats.kitten_count_lock:
                    self.stats.kitten_count += 1
            _clear()
            print('There are now {} kittens'.format(self.stats.kitten_count))

    def visit_store(self):
        _clear()
        print('   Building                 |Price          |Production')
        print('   -------------------------|---------------|----------')
        for index, building in self.stats.store.items():
            if self.stats.kitten_count < building.price:
                break
            price = str(building.price) + ' kittens'
            print('{}) {}|{}|{} k/s'.format(
                index, building.name.ljust(25), price.ljust(15),
                building.prod))
        print('\nYou currently have {} kittens '
                'and are producing {} kittens per second'.format(
                self.stats.kitten_count, self.stats.prod_per_sec))

        try:
            selection = self.stats.store[int(input())]
        except (ValueError, KeyError):
            return

        if self.stats.kitten_count < selection.price:
            return

        with self.stats.kitten_count_lock:
            self.stats.kitten_count -= selection.price
        self.stats.prod_per_sec += selection.prod
        selection.price = int(selection.price * 1.15)


class GameEngine(threading.Thread):
    def __init__(self, stats, *args, **kwargs):
        super(GameEngine, self).__init__(*args, **kwargs)
        self.daemon = True

        self._update_cycle = 1.0
        self.stats = stats

    def update(self):
        with self.stats.kitten_count_lock:
            self.stats.kitten_count += self.stats.prod_per_sec

    def run(self):
        update_delta = self._update_cycle

        while True:
            time.sleep(update_delta)

            start_time = time.time()
            self.update()

            elapsed_time = time.time() - start_time
            update_delta = self._update_cycle - elapsed_time


class Stats(object):
    def __init__(self):
        self.kitten_count = 0
        self.kitten_count_lock = threading.Lock()

        self.prod_per_sec = 0

        buildings = [
            Building(name='Empty Box', price=10, prod=1),
            Building(name='Scratching Post', price=100, prod=10),
            Building(name='Kitten Perch', price=1000, prod=100),
            Building(name='Delux Scratching Post', price=10000, prod=1000),
            Building(name='Delux Kitten Perch', price=100000, prod=10000),
            Building(name='Kitten Hotel', price=1000000, prod=100000),
        ]
        self.store = collections.OrderedDict((i, s) for i, s in
                enumerate(buildings))


def start_game():
    # Create the stats object
    stats = Stats()

    # Start the game engine which holds the ioloop
    game_engine = GameEngine(stats)
    game_engine.start()

    # Start the click handler thread which will listen for click events
    click_handler = ClickHandler(stats)
    click_handler.start()


if __name__ == '__main__':
    start_game()
