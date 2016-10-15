import os

import cocos
import pyglet

import amaze

from cocos import scenes
from pyglet.gl import glPushMatrix, glPopMatrix
from random import randrange

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets/')
MAPS_DIR = os.path.join(BASE_DIR, 'maps/')

MAP_WIDTH = 1280        # 40*32
MAP_HEIGHT = 1280       # 40*32
SCREEN_WIDTH = 960      # 60*16
SCREEN_HEIGHT = 540     # 60*9


def random_rgb():
    return randrange(0, 255), randrange(0, 255), randrange(0, 255), 255


class MenuBackground(cocos.layer.Layer):

    def __init__(self):
        super().__init__()
        self.sprite = cocos.sprite.Sprite(pyglet.image.load(ASSETS_DIR + 'menu_background.png'))
        self.sprite.position = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.add(self.sprite)
        self.sprite.do(
            cocos.actions.Repeat(cocos.actions.ScaleTo(2) + cocos.actions.ScaleTo(1))
        )


class GameMainMenu(cocos.menu.Menu):

    def __init__(self):
        super().__init__("AMaze")
        self.menu_halign = cocos.menu.RIGHT
        self.menu_hmargin = 50
        self.font_title['font_name'] = 'Ubuntu Mono'
        self.font_title['color'] = random_rgb()
        self.font_item['font_size'] = 65
        self.font_item_selected['font_size'] = 80
        items = [
            cocos.menu.ImageMenuItem('assets/new_game.png', self.new_game),
            cocos.menu.ImageMenuItem('assets/difficulty.png', self.difficulty),
            cocos.menu.ImageMenuItem("assets/high_score.png", self.high_score),
            cocos.menu.ImageMenuItem('assets/quit.png', self.quit)
        ]
        self.create_menu(items)

    @staticmethod
    def on_quit():
        pyglet.app.exit()

    def new_game(self):
        amaze.director.replace(scenes.transitions.FadeTransition(
            cocos.scene.Scene(amaze.scroller, amaze.GameTimer()), duration=2)
        )

    def difficulty(self):
        self.get_ancestor(cocos.layer.MultiplexLayer).switch_to(1)

    def high_score(self):
        print(0)

    def quit(self):
        self.get_ancestor(cocos.layer.MultiplexLayer).switch_to(2)


class GameDifficultyMenu(cocos.menu.Menu):

    def __init__(self):
        super().__init__("Choose a difficulty level")
        self.font_title['font_name'] = 'Ubuntu Mono'
        self.font_title['font_size'] = 40
        self.font_title['color'] = random_rgb()
        self.font_item['font_name'] = 'Ubuntu Mono'
        self.font_item['font_size'] = 25
        self.font_item['color'] = random_rgb()
        self.font_item_selected['font_name'] = 'Ubuntu Mono'
        self.font_item_selected['font_size'] = 35
        self.font_item_selected['color'] = self.font_item['color']
        items = [
            cocos.menu.MenuItem('EASY', lambda: self.difficulty_callback(0)),
            cocos.menu.MenuItem('MEDIUM', lambda: self.difficulty_callback(1)),
            cocos.menu.MenuItem('HARD', lambda: self.difficulty_callback(2))
        ]
        self.back_label = cocos.text.Label(
            text='Press ESC to go back',
            position=(480, 100),
            font_name='Ubuntu Mono',
            font_size=40,
            color=random_rgb(),
            anchor_x='center',
            anchor_y='center'
        )
        self.create_menu(items)

    def on_quit(self):
        self.get_ancestor(cocos.layer.MultiplexLayer).switch_to(0)

    def draw(self):
        glPushMatrix()
        self.transform()
        self.title_label.draw()
        self.back_label.draw()
        glPopMatrix()

    def difficulty_callback(self, i):
        with open('difficulty.txt', 'w') as infile:
            infile.write(str(i))
        self.get_ancestor(cocos.layer.MultiplexLayer).switch_to(0)


class GameQuitMenu(cocos.menu.Menu):

    def __init__(self):
        super().__init__("Do you really wish to quit AMaze?")
        self.font_title['font_name'] = 'Ubuntu Mono'
        self.font_title['font_size'] = 25
        self.font_title['color'] = random_rgb()
        self.font_title['bold'] = True
        self.font_title['italic'] = True
        self.font_item['font_name'] = 'Ubuntu Mono'
        self.font_item['font_size'] = 20
        self.font_item['color'] = random_rgb()
        self.font_item_selected['font_name'] = 'Ubuntu Mono'
        self.font_item_selected['font_size'] = 25
        self.font_item_selected['color'] = self.font_item['color']
        items = [
            cocos.menu.MenuItem("Yes, Please!", pyglet.app.exit),
            cocos.menu.MenuItem("Ooos, Sorry!", self.on_cancel)
        ]
        self.create_menu(items, layout_strategy=cocos.menu.fixedPositionMenuLayout(((360, 250), (600, 250))))

    def _generate_title(self):
        super()._generate_title()
        self.title_label.y = 300

    def on_cancel(self):
        self.get_ancestor(cocos.layer.MultiplexLayer).switch_to(0)

    def on_quit(self):
        """Doing this prevents pressing ESC to quit the game."""


class GameMenu(cocos.layer.MultiplexLayer):

    def __init__(self):
        super().__init__(GameMainMenu(), GameDifficultyMenu(), GameQuitMenu())

if __name__ == '__main__':
    amaze.play()
