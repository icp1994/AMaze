import cocos
import pyglet

import amaze

from cocos import scenes
from pyglet.window import key
from random import randrange

MAP_WIDTH = 1280        # 40*32
MAP_HEIGHT = 1280       # 40*32
SCREEN_WIDTH = 960      # 60*16
SCREEN_HEIGHT = 540     # 60*9


def random_rgb():
    return randrange(0, 255), randrange(0, 255), randrange(0, 255), 255


class MenuBackground(cocos.layer.Layer):

    def __init__(self):
        super().__init__()
        self.sprite = cocos.sprite.Sprite(pyglet.image.load('assets/menu_background.png'))
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
        amaze.director.replace(scenes.transitions.FadeTransition(amaze.GamePlayScene()))

    def difficulty(self):
        self.get_ancestor(cocos.layer.MultiplexLayer).switch_to(1)

    def high_score(self):
        self.get_ancestor(cocos.layer.MultiplexLayer).switch_to(2)

    def quit(self):
        self.get_ancestor(cocos.layer.MultiplexLayer).switch_to(3)


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
        self.create_menu(items)

    def on_quit(self):
        self.get_ancestor(cocos.layer.MultiplexLayer).switch_to(0)

    def difficulty_callback(self, i):
        with open('difficulty.txt', 'w') as infile:
            infile.write(str(i))
        self.get_ancestor(cocos.layer.MultiplexLayer).switch_to(0)


class LeaderBoard(cocos.layer.Layer):

    is_event_handler = True

    def __init__(self):
        super().__init__()
        entries = []
        try:
            with open('leaderboard.txt', 'r') as infile:
                for line in infile:
                    if line != '\n':
                        entries.append(line.rstrip().split(','))
        except FileNotFoundError:
            with open('leaderboard.txt', 'w') as infile:
                infile.write('\n')

        header_label = cocos.text.Label(
            text='AMaze Leaderboard',
            position=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50),
            font_name='Ubuntu Mono',
            font_size=40,
            color=random_rgb(),
            anchor_x='center',
            anchor_y='center'
        )
        self.add(header_label)

        title_label = cocos.text.Label(
            text='RANK  TIME    NAME',
            position=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120),
            font_name='Ubuntu Mono',
            font_size=30,
            color=random_rgb(),
            anchor_x='center',
            anchor_y='center'
        )
        self.add(title_label)

        x_pos = SCREEN_WIDTH // 2 - 140
        color = random_rgb()
        for rank, detail in enumerate(entries, 1):
            text = '{}.     {:03d}        {}'.format(rank, int(detail[0]), detail[1])
            y_pos = SCREEN_HEIGHT // 2 + (3 - rank) * 25
            rank_label = cocos.text.Label(
                text=text,
                position=(x_pos, y_pos),
                font_name='Ubuntu Mono',
                font_size=20,
                color=color,
                anchor_y='center'
            )
            self.add(rank_label)

        footer_label = cocos.text.Label(
            text='Press ESC to go back',
            position=(SCREEN_WIDTH // 2, 50),
            font_name='Ubuntu Mono',
            font_size=40,
            color=random_rgb(),
            anchor_x='center',
            anchor_y='center'
        )
        self.add(footer_label)

    def on_key_press(self, symbol, modifier):
        if symbol == key.ESCAPE:
            self.get_ancestor(cocos.layer.MultiplexLayer).switch_to(0)
            return 1


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
            cocos.menu.MenuItem("Ooos, Sorry!", self.on_cancel),
            cocos.menu.MenuItem("Yes, Please!", pyglet.app.exit)
        ]
        self.create_menu(items, layout_strategy=cocos.menu.fixedPositionMenuLayout(((360, 250), (600, 250))))

    def _generate_title(self):
        super()._generate_title()
        self.title_label.y = 300

    def on_cancel(self):
        self.get_ancestor(cocos.layer.MultiplexLayer).switch_to(0)

    def on_quit(self):
        """Doing this prevents pressing ESC to quit the game."""


class ScoreSubmitMenu(cocos.menu.Menu):

    def __init__(self):
        super().__init__("Congratulations! Your time is eligible for leaderboard entry!")
        self.name = ''
        self.font_title['font_name'] = 'Ubuntu Mono'
        self.font_title['font_size'] = 20
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
            cocos.menu.EntryMenuItem('Enter your name : ', self.on_entry, '', 10),
            cocos.menu.MenuItem('SUBMIT', self.on_submit),
            cocos.menu.MenuItem('CANCEL', self.on_cancel)
        ]
        positions = (
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40),
            (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2),
            (SCREEN_WIDTH // 2 + 80, SCREEN_HEIGHT // 2)
        )
        self.create_menu(items, layout_strategy=cocos.menu.fixedPositionMenuLayout(positions))

    def on_entry(self, value):
        self.name = value

    def on_submit(self):
        with open('leaderboard.txt', 'a') as infile:
            entry_string = '{},{}\n'.format(
                self.get_ancestor(cocos.scene.Scene).score, self.name
            )
            infile.write(entry_string)
        amaze.director.replace(scenes.transitions.FadeTRTransition(amaze.MenuScene()))

    def on_cancel(self):
        amaze.director.replace(scenes.transitions.FadeTRTransition(amaze.MenuScene()))

    def on_quit(self):
        pass


class GameMenu(cocos.layer.MultiplexLayer):

    def __init__(self):
        super().__init__(GameMainMenu(), GameDifficultyMenu(), LeaderBoard(), GameQuitMenu())

if __name__ == '__main__':
    amaze.play()
