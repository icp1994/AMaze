import cocos
import pyglet

import game_menu

from random import randrange
from cocos import layer
from cocos import scenes
from pyglet.window import key

MAP_WIDTH = 1280        # 40*32
MAP_HEIGHT = 1280       # 40*32
SCREEN_WIDTH = 960      # 60*16
SCREEN_HEIGHT = 540     # 60*9

director, keyboard, scroller, desert = None, None, None, None


class MenuScene(cocos.scene.Scene):

    def __init__(self):
        super().__init__(game_menu.MenuBackground(), game_menu.GameMenu())


class GameOn(layer.scrolling.ScrollableLayer):

    is_event_handler = True
    key_dict = {
        65363: (65361, 'right', (250, 0)), 65361: (65363, 'left', (-250, 0)),
        65362: (65364, 'up', (0, 250)), 65364: (65362, 'down', (0, -250))
    }

    def __init__(self):
        super().__init__()
        self.keys_pressed = set()
        self.sprite = cocos.sprite.Sprite(pyglet.image.load('assets/standing_right.png'))
        self.sprite.position = randrange(75, 1200), 1200
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
                    'assets/standing_' + GameOn.key_dict[keys][1] + '.png'
                )


class DirectionalWalk(cocos.actions.Action):

    def init(self, keys):
        self.keys = keys
        self.revkeys = GameOn.key_dict[keys][0]

    def start(self):
        self.target.image = pyglet.image.load_animation(
            'assets/walking_' + GameOn.key_dict[self.keys][1] + '.gif'
        )

    def step(self, dt):
        super().step(dt)
        initialpos = cocos.euclid.Vector2(*self.target.position)
        movement = keyboard[self.keys] * dt * cocos.euclid.Vector2(*GameOn.key_dict[self.keys][2])
        finalpos = initialpos + movement
        if desert.get_at_pixel(*finalpos).get('Collidable'):
            finalpos = initialpos
        self.target.do(cocos.actions.MoveTo(finalpos, dt))
        scroller.set_focus(*finalpos)
        if desert.get_at_pixel(*finalpos).get('Winnable'):
            with open('difficulty.txt') as infile:
                i = infile.read()
            t_initial = 60 * (3 - int(i))
            s = self.target.get_ancestor(cocos.scene.Scene).get_children()[1].timer.element.text
            j, k = s.split(':')
            t_final = 60 * int(j) + int(k)
            delta = t_initial - t_final
            self.target.position = 250, 1200
            self._done = True
            director.return_value = delta
            director.replace(scenes.transitions.SlideInRTransition(GameWinScene()))


class GameWin(cocos.layer.ColorLayer):

    def __init__(self):
        super().__init__(*game_menu.random_rgb())
        self.sprite = cocos.sprite.Sprite(pyglet.image.load_animation('assets/game_win.gif'))
        self.sprite.position = 480, 200
        self.label = cocos.text.Label(
            text='You Win!',
            position=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150),
            font_name='Ubuntu Mono',
            font_size=40,
            color=game_menu.random_rgb(),
            anchor_x='center',
            anchor_y='center'
        )
        self.add(self.sprite)
        self.add(self.label)


class ScoreSubmitScene(cocos.scene.Scene):

    def __init__(self):
        super().__init__(cocos.layer.ColorLayer(*game_menu.random_rgb()), game_menu.ScoreSubmitMenu())
        self.score = director.return_value


class GameWinScene(cocos.scene.Scene):
    def __init__(self):
        super().__init__(GameWin())
        self.get_children()[0].do(WaitToScene(ScoreSubmitScene))


class GameTimer(cocos.layer.Layer):

    def __init__(self):
        super().__init__()
        difficulty = 0
        try:
            with open('difficulty.txt', 'r') as infile:
                difficulty = int(infile.read())
        except FileNotFoundError:
            with open('difficulty.txt', 'w') as infile:
                infile.write('0')
        text = '0{}:01'.format(3 - difficulty)
        # text = '00:04'
        self.timer = cocos.text.Label(
            text=text,
            position=(900, 500),
            font_name='Ubuntu Mono',
            font_size=24,
            anchor_x='center',
            anchor_y='center'
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
                director.replace(scenes.transitions.SlideInLTransition(GameLoseScene()))
            mins = '{:02d}'.format(self.time // 60)
            secs = '{:02d}'.format(self.time % 60)
            self.target.element.text = mins + ':' + secs


class GameLose(cocos.layer.ColorLayer):

    def __init__(self):
        super().__init__(*game_menu.random_rgb())
        self.sprite = cocos.sprite.Sprite(pyglet.image.load('assets/game_lose.png'))
        self.sprite.position = 480, 200
        self.label = cocos.text.Label(
            text='You Lose!',
            position=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150),
            font_name='Ubuntu Mono',
            font_size=40,
            color=game_menu.random_rgb(),
            anchor_x='center',
            anchor_y='center'
        )
        self.add(self.sprite)
        self.add(self.label)


class GameLoseScene(cocos.scene.Scene):

    def __init__(self):
        super().__init__(GameLose())
        self.get_children()[0].do(WaitToScene(MenuScene))


class WaitToScene(cocos.actions.Action):

    def init(self, next_scene, duration=5):
        self.next_scene = next_scene
        self.duration = duration

    def step(self, dt):
        super().step(dt)
        if self._elapsed >= self.duration:
            self._done = True
            director.replace(scenes.transitions.FadeTRTransition(self.next_scene()))


class GamePlayScene(cocos.scene.Scene):

    def __init__(self):
        super().__init__(scroller, GameTimer())


def play():
    global director, keyboard, scroller, desert
    director = cocos.director.director
    director.init(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    keyboard = key.KeyStateHandler()
    director.window.push_handlers(keyboard)
    scroller = layer.scrolling.ScrollingManager()
    desert = cocos.tiles.load('maps/maze.tmx')["Ground"]
    scroller.add(desert)
    scroller.add(GameOn())
    scroller.scale = 1

    director.run(MenuScene())
