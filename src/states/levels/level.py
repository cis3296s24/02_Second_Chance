import csv
import random
import pygame as pg

import src.entities.enemies.enemy as enemy
import src.states.menu.menus as menus
import src.states.menu.winscreen as winscreen
from src.utils.leaderboard import LeaderboardManager
from src.constants import *
from src.entities.player import Player
from src.objects.tiles import Tile
from src.states.minigames.minigame import Minigame
from src.states.state import State
from src.utils.timer import Timer

from src.entities.enemies.eyeball import Eyeball  # Import the Eyeball class
from src.entities.enemies.skeleton import Skeleton  # Import the Skeleton class
from src.entities.enemies.archer import archer
from src.entities.enemies.wolf import Wolf # Import the Wolf class

# Necessary to access minigames from the minigames package
from src.states.minigames import *


class Level(State):

    def __init__(self, level: int, music_file: str, imgArr=None):
        super().__init__()
        self.level = level
        self.scroll = 0
        self.level_scroll = 0
        self.timer = Timer(start=True) # Timer starts when it's instantiated
        self.init_tiles()
        self.init_sprites()
        self.init_attributes()
        self.init_background(imgArr)
        self.init_music(music_file)

    def handle_events(self, events):
        for event in events:
            if event.type != pg.KEYDOWN:  # Ignore all inputs except key presses
                return
            if event.key == pg.K_ESCAPE:  # Open pause menu
                self.manager.set_state(menus.PauseMenu(self.timer), save_prev=True)

    def update(self, events):
        self.current_time = self.timer.get_time(ms=True)
        
        self.scroll = self.player.update()
        visible_enemies = self.get_visible_enemies()
        visible_enemies.update(self.player, self.scroll)
        self.objects.update(self.scroll)
        self.tiles.update(self.scroll)

        # Check for collision between player's melee attacks and enemy

        collisions = pg.sprite.groupcollide(self.player.melee_attacks, visible_enemies, False, False)  # Change False to True to remove the melee attack sprite upon collision
        range_attack_collisions = pg.sprite.groupcollide(self.player.range_attacks, visible_enemies, True, False)

        

        for attack, enemies in collisions.items():
            for enemy in enemies:
                enemy.decrease_health(attack.damage_value)
        for attack,enemies in range_attack_collisions.items():
            for enemy in enemies:
                enemy.decrease_health(attack.damage_value)

        for portal in self.portals: 
            if portal.rect.colliderect(self.player.rect):
                if len(self.enemies) == 0: # If no enemies left
                    # Transition to the start menu state

                    timer = LeaderboardManager(self.game)
                    timer.update_leaderboard(self.game.username, self.current_time)

                    self.manager.set_state(winscreen.WinScreen)
                else:
                    self.last_portal_time = self.current_time

        self.update_text()

        # Check for player death
        if self.player.health <= 0:
            self.timer.pause()
            self.manager.set_state(
                globals()[random.choice(self.minigames)], # Select a random minigame
                save_prev=True)

    def draw(self):
        self.draw_bg()
        self.portals.draw(self.screen)
        # self.enemies.draw()
        self.objects.draw(self.screen)
        self.tiles.draw(self.screen)
        self.player.draw()
        self.platforms.draw(self.screen)
        self.draw_health_bar()
        self.draw_text_surfaces()

        enemy_bounds = {}

        for enemy_instance in self.enemies:
            if isinstance(enemy_instance, Eyeball):  # Check the class type directly
                enemy_bounds[enemy_instance] = (100, 200)
            # Add more bounds for other enemy types as needed

        # Check player's position against enemy bounds
        player_x = self.player.rect.x
        for enemy_instance, bounds in enemy_bounds.items():
            if bounds[0] <= player_x <= bounds[1]:
                # Draw the enemy if it falls within the bounds
                enemy_instance.draw()

    def get_visible_enemies(self):
        visible_enemies = pg.sprite.Group()
        screen_rect = pg.Rect((0, 0), self.screen.get_size())

        # Iterate through all enemies and add the ones within the visible bounds to the group
        for enemy_instance in self.enemies:
            if screen_rect.colliderect(enemy_instance.rect):
                visible_enemies.add(enemy_instance)

        return visible_enemies

    def init_tiles(self):
        self.world_data = []
        self.tile_list = []

        for x in range(TILE_TYPES):
            img = pg.image.load(f"assets/tiles/{x}.png")
            img = pg.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            self.tile_list.append(img)

        # create empty tile list
        for row in range(ROWS):
            r = [-1] * COLS
            self.world_data.append(r)
        # load in level data and create world
        with open(f"assets/csvs/level{1}_data.csv", newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    self.world_data[x][y] = int(tile)

    def init_sprites(self):
        self.platforms = pg.sprite.Group()
        self.portals = pg.sprite.Group()
        self.tiles = pg.sprite.Group()
        self.objects = pg.sprite.Group()
        self.world = World(self.tile_list, self.objects, self.tiles, self.screen)
        self.enemies = enemy.EnemyGroup()
        self.player = Player(100, 100, self.platforms, self.portals, self.tiles)

        self.create_platforms()
        self.spawn_enemies()
        self.world.process_data(self.world_data)  # call method to process csv data

        self.add_portal()

    def init_attributes(self):
        # Timed events
        self.current_time = 0
        self.last_portal_time = 0
        self.next_portal_time = 0 # Next time to display message
        self.instruction_duration = 5 # Amount of seconds to display message
        
        # A list of all current minigames
        self.minigames = [cls.__name__ for cls in Minigame.__subclasses__()]

        self.controls = self.get_text_surface(
            "Press 'Escape' to pause", "white", font_size=36
        )
        self.kill_instruction = self.get_text_surface(
            "You must kill all enemies before you can enter the portal", "red", font_size=36
        )
        self.timer_text = self.get_text_surface(
            f"Level {self.level} Time: {self.timer.get_time()}", "white",
            font_size=36
        )
        self.health_text_surface = self.get_text_surface(
            f"Health: {self.player.health}", "white", font_size=36
        )

    def init_background(self, imgArr):
        self.bg_images = []

        if imgArr is not None:
            for i in range(1, 6):
                bg_image = pg.image.load(f"assets/backgrounds/plx-{i}.png").convert_alpha()
                bg_image = pg.transform.smoothscale(bg_image, self.screen.get_size())
                self.bg_images.append(bg_image)
                self.bg_width = self.bg_images[0].get_width()

    def init_music(self, music_file):
        # Load background music
        pg.mixer.music.load(os.path.join("assets/music", f"{music_file}"))
        self.volume = menus.volume  # Initial volume level (between 0 and 1)
        pg.mixer.music.set_volume(menus.volume)
        pg.mixer.music.play(-1)  # Start playing background music on a loop

    def create_platforms(self):
        pass  # Level-specific behavior

    def spawn_enemies(self):
        pass  # Level-specific behavior

    def add_portal(self):
        pass  # Level-specific behavior

    def update_text(self):
        self.timer_text = self.get_text_surface(
            f"Level {self.level} Time: {self.timer.get_time()}", "white",
            font_size=36
        )
        self.health_text_surface = self.get_text_surface(
            f"Health: {self.player.health}", "white", font_size=36
        )
        
        # Determine if kill_instruction should be displayed on the screen
        if self.current_time > self.next_portal_time:
            if self.last_portal_time > self.next_portal_time:
                self.next_portal_time = self.last_portal_time + self.instruction_duration
            self.kill_instruction = pg.Surface((0, 0))
        else:
            self.kill_instruction = self.get_text_surface(
                "You must kill all enemies before you can enter the portal", "red", font_size=36
            )  
        
    def draw_bg(self):
        for x in range(25):
            speed = 1
            for i in self.bg_images:
                self.screen.blit(i, ((x * self.bg_width) - self.player.level_scroll * speed, 0))
                speed += 0.2

    def draw_health_bar(self):
        # Calculate the width of the health bar based on current health
        health_bar_width = (self.player.health / self.player.max_health) * self.player.health_bar_length
        # Calculate the position of the health bar above the player
        health_bar_x = self.player.rect.x - (self.player.rect.width * (self.player.scale_factor - 1)) / 2
        health_bar_y = self.player.rect.y - 20  # Adjust this value to position the health bar properly
        # Draw the health bar
        pg.draw.rect(self.screen, (255, 0, 0),
                     (health_bar_x, health_bar_y, self.player.health_bar_length, self.player.health_bar_height))
        pg.draw.rect(self.screen, self.player.health_bar_color,
                     (health_bar_x, health_bar_y, health_bar_width, self.player.health_bar_height))

    def draw_text_surfaces(self):
        self.screen.blit(self.controls, (20, 20))
        self.screen.blit(self.health_text_surface, (20, 50))
        self.screen.blit(self.timer_text, (self.screen.get_width() - 220, 20))
        self.screen.blit(self.kill_instruction, (100, 100))


class World:
    def __init__(self, tile_list, objects, tiles, screen):
        self.tile_list = tile_list
        self.objects = objects
        self.tiles = tiles
        self.screen = screen

    def process_data(self, data):
        # iterate through data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                collision = True
                if tile in [11, 13, 14, 20]:
                    collision = False
                if tile >= 0:
                    if tile >= 0 and tile <= 8:
                        pass
                    elif tile > 9 and tile <= 10:
                        pass  # water(potentially added later to kill player when colliding)
                    elif tile >= 11 and tile <= 14:
                        pass  # decoration
                    elif tile == 15:
                        pass  # create player
                    elif tile == 16:
                        pass  # create enemy
                    elif tile == 20:
                        pass  # create exit
                    img = self.tile_list[tile]
                    t = Tile(img, x * TILE_SIZE, y * TILE_SIZE, tile)
                    if collision:
                        self.tiles.add(t)
                    else:
                        self.objects.add(t)
