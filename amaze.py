import os

import cocos
import pyglet

from cocos import layer
from cocos import scenes
from pyglet.window import key
from random import randrange

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets/')
MAPS_DIR = os.path.join(BASE_DIR, 'maps/')

MAP_WIDTH = 1280        # 40*32
MAP_HEIGHT = 1280       # 40*32
OFFSET = 32
SCREEN_WIDTH = 960      # 60*16
SCREEN_HEIGHT = 540     # 60*9

director, keyboard, scroller, desert = None, None, None, None


def random_rgb():
    return randrange(0, 255), randrange(0, 255), randrange(0, 255), 1000


class GameMenu(cocos.menu.Menu):
    def __init__(self):
        super().__init__("AMaze")
        self.menu_halign = cocos.menu.CENTER
        self.menu_valign = cocos.menu.CENTER
        items = [
            (cocos.menu.MenuItem("New Game", self.new_game)),
            (cocos.menu.MenuItem("High Score", self.high_score)),
            (cocos.menu.MenuItem("Quit", self.quit))
        ]
        self.create_menu(items)

    def on_quit(self):
        pyglet.app.exit()

    @staticmethod
    def new_game():
        director.replace(scenes.transitions.FadeTransition(cocos.scene.Scene(scroller, GameTimer()), duration=1))

    @staticmethod
    def high_score():
        print(0)

    @staticmethod
    def quit():
        print("Quitting...")
        pyglet.app.exit()


class GameOn(layer.scrolling.ScrollableLayer):

    is_event_handler = True
    key_dict = {
        65363: (65361, 'right', (100, 0)), 65361: (65363, 'left', (-100, 0)),
        65362: (65364, 'up', (0, 100)), 65364: (65362, 'down', (0, -100))
    }

    def __init__(self):
        super().__init__()
        self.keys_pressed = set()
        self.sprite = cocos.sprite.Sprite(pyglet.image.load(ASSETS_DIR + 'standing_right.png'))
        self.sprite.position = 250, 1200
        self.sprite.scale = 0.20
        self.add(self.sprite)
        scroller.set_focus(*self.sprite.position)
        self.lastkey = None

    def on_key_press(self, keys, mods):
        if keys in (key.RIGHT, key.LEFT, key.UP, key.DOWN):
            self.keys_pressed.add(keys)
            self.sprite.do(DirectionalWalk(keys))

    def on_key_release(self, keys, mods):
        if keys in (key.RIGHT, key.LEFT, key.UP, key.DOWN):
            self.keys_pressed.discard(keys)
            self.lastkey = keys
            if not self.keys_pressed:
                self.sprite.image = pyglet.image.load(
                    ASSETS_DIR + 'standing_' + GameOn.key_dict[keys][1] + '.png'
                )


class DirectionalWalk(cocos.actions.Action):

    def __init__(self, keys):
        super().__init__()
        self.keys = keys
        self.revkeys = GameOn.key_dict[keys][0]

    def start(self):
        self.target.image = pyglet.image.load_animation(
            ASSETS_DIR + 'walking_' + GameOn.key_dict[self.keys][1] + '.gif'
        )

    def step(self, dt):
        super().step(dt)
        movement = [v * keyboard[self.keys] * dt / 2
                    for v in GameOn.key_dict[self.keys][2]]
        nextpos = self.target.x + movement[0], self.target.y + movement[1]
        if desert.get_at_pixel(*nextpos).get('Collidable'):
            movement = [0, 0]
        if not (OFFSET < self.target.x + movement[0] < MAP_WIDTH - OFFSET):
            movement[0] = 0
        if not (OFFSET < self.target.y + movement[1] < MAP_HEIGHT - OFFSET):
            movement[1] = 0
        self.target.do(cocos.actions.MoveBy(movement, dt))
        scroller.set_focus(*self.target.position)
        if desert.get_at_pixel(*self.target.position).get('Winnable'):
            self.target.position = 250, 1200
            self._done = True
            director.replace(scenes.transitions.SlideInRTransition(cocos.scene.Scene(GameWin()), duration=3))


class GameWin(cocos.layer.ColorLayer):

    def __init__(self):
        super().__init__(*random_rgb())
        self.sprite = cocos.sprite.Sprite(pyglet.image.load_animation(ASSETS_DIR + 'game_win.gif'))
        self.sprite.position = 480, 200
        self.label = cocos.text.Label(
            'You Win!', (480, 400), font_name='Ubuntu Mono', font_size=40, anchor_x='center', anchor_y='center'
        )
        self.add(self.sprite)
        self.add(self.label)

    def on_exit(self):
        director.replace(scenes.transitions.ShuffleTransition(
            cocos.scene.Scene(cocos.layer.ColorLayer(*random_rgb()), GameMenu()), duration=2))


class GameTimer(cocos.layer.Layer):

    def __init__(self):
        super().__init__()
        self.timer = cocos.text.Label(
            '03:01', (900, 500), font_name='Ubuntu Mono', font_size=24, anchor_x='center', anchor_y='center'
        )
        self.add(self.timer)
        self.timer.do(CountDown())


class CountDown(cocos.actions.Action):

    def start(self):
        i, j = self.target.element.text.split(':')
        self.time = 60 * int(i) + int(j)

    def step(self, dt):
        self._elapsed += dt
        if self._elapsed >= 1:
            self._elapsed = 0
            self.time -= 1
            if self.time == 0:
                self._done = True
                director.replace(scenes.transitions.SlideInLTransition(cocos.scene.Scene(GameLose()), duration=3))
            mins = '{:02d}'.format(self.time // 60)
            secs = '{:02d}'.format(self.time % 60)
            self.target.element.text = mins + ':' + secs


class GameLose(cocos.layer.ColorLayer):

    def __init__(self):
        super().__init__(*random_rgb())
        self.sprite = cocos.sprite.Sprite(pyglet.image.load(ASSETS_DIR + 'game_lose.png'))
        self.sprite.position = 480, 200
        self.label = cocos.text.Label(
            'You Lose!', (480, 400), font_name='Ubuntu Mono', font_size=40, anchor_x='center', anchor_y='center'
        )
        self.add(self.sprite)
        self.add(self.label)

    def on_exit(self):
        director.replace(scenes.transitions.FadeTRTransition(
            cocos.scene.Scene(cocos.layer.ColorLayer(*random_rgb()), GameMenu()), duration=2))


def main():
    global director, keyboard, scroller, desert
    director = cocos.director.director
    director.init(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    keyboard = key.KeyStateHandler()
    director.window.push_handlers(keyboard)
    scroller = cocos.layer.scrolling.ScrollingManager()
    desert = cocos.tiles.load(MAPS_DIR + 'maze.tmx')["Ground"]
    scroller.add(desert)
    scroller.add(GameOn())
    scroller.scale = 6

    director.run(cocos.scene.Scene(cocos.layer.ColorLayer(*random_rgb()), GameMenu()))

if __name__ == '__main__':
    main()
