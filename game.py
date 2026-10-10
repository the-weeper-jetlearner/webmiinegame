from __future__ import annotations

import asyncio
import json
import math
import os
import random
import sys
from dataclasses import dataclass

import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 640
ORE_LIST_TOP = 54
ORE_ROW_HEIGHT = 64
WORLD_LEFT, WORLD_RIGHT = 300, 700
WORLD_GROUND = 426
MINING_DISTANCE = 92
ORE_PLAYER_SEPARATION = 74
ORE_HARDNESS_PER_LEVEL = 0.4
MAX_HEAT = 100
HEAT_PER_HIT = 5
SAVE_FILE = os.path.join(os.path.expanduser("~"), ".earth_corp_mining_save.json")
SAVE_KEY = "earth-corp-mining-save-v1"


def is_browser_runtime():
    return sys.platform.startswith("emscripten")

LEVELS = [
    ("Poor", 0, 0),
    ("Medium", 3, 15),
    ("Rich", 8, 50),
    ("Strong", 15, 120),
    ("Elite", 25, 250),
    ("Mythic", 40, 500),
    ("Apex", 55, 900),
    ("Cosmic", 75, 1600),
    ("Eternal", 100, 2600),
]

RARITY = {
    "Common": (60, (200, 200, 200)),
    "Uncommon": (25, (110, 220, 110)),
    "Rare": (10, (90, 160, 255)),
    "Epic": (4, (190, 100, 255)),
    "Legendary": (1, (255, 170, 40)),
}

ORE_DATA = [
    ("Coal", "ores/01_coal_ore.png", 5, 1, 0, "Common"),
    ("Iron", "ores/02_iron_ore.png", 7, 2, 0, "Common"),
    ("Copper", "ores/03_copper_ore.png", 10, 3, 0, "Common"),
    ("Tin", "ores/04_tin_ore.png", 14, 6, 0, "Common"),
    ("Lead", "ores/05_lead_ore.png", 18, 9, 0, "Uncommon"),
    ("Zinc", "ores/06_zinc_ore.png", 24, 12, 0, "Uncommon"),
    ("Nickel", "ores/07_nickel_ore.png", 29, 15, 0, "Uncommon"),
    ("Silver", "ores/08_silver_ore.png", 35, 19, 0, "Rare"),
    ("Gold", "ores/09_gold_ore.png", 41, 23, 0, "Rare"),
    ("Platinum", "ores/10_platinum_ore.png", 48, 28, 0, "Epic"),
    ("Titanium", "ores/11_titanium_ore.png", 55, 32, 1, "Common"),
    ("Bauxite", "ores/12_bauxite_ore.png", 62, 37, 1, "Common"),
    ("Cobalt", "ores/13_cobalt_ore.png", 69, 42, 1, "Common"),
    ("Tungsten", "ores/14_tungsten_ore.png", 77, 47, 1, "Common"),
    ("Uranium", "ores/15_uranium_ore.png", 85, 53, 1, "Uncommon"),
    ("Lithium", "ores/16_lithium_ore.png", 93, 59, 1, "Uncommon"),
    ("Magnesium", "ores/17_magnesium_ore.png", 102, 65, 1, "Uncommon"),
    ("Chromium", "ores/18_chromium_ore.png", 110, 71, 1, "Rare"),
    ("Manganese", "ores/19_manganese_ore.png", 119, 77, 1, "Rare"),
    ("Cinnabar", "ores/20_cinnabar_ore.png", 128, 83, 1, "Epic"),
    ("Sulfur", "ores/21_sulfur_ore.png", 137, 90, 2, "Common"),
    ("Rock Salt", "ores/22_rock_salt_ore.png", 146, 97, 2, "Common"),
    ("Quartz", "ores/23_quartz_ore.png", 156, 104, 2, "Common"),
    ("Diamond", "ores/24_diamond_ore.png", 166, 111, 2, "Common"),
    ("Emerald", "ores/25_emerald_ore.png", 176, 118, 2, "Uncommon"),
    ("Ruby", "ores/26_ruby_ore.png", 186, 126, 2, "Uncommon"),
    ("Sapphire", "ores/27_sapphire_ore.png", 196, 133, 2, "Uncommon"),
    ("Amethyst", "ores/28_amethyst_ore.png", 206, 141, 2, "Rare"),
    ("Topaz", "ores/29_topaz_ore.png", 217, 149, 2, "Rare"),
    ("Opal", "ores/30_opal_ore.png", 228, 157, 2, "Epic"),
    ("Garnet", "ores/31_garnet_ore.png", 238, 165, 3, "Common"),
    ("Jade", "ores/32_jade_ore.png", 249, 173, 3, "Common"),
    ("Obsidian", "ores/33_obsidian_ore.png", 260, 182, 3, "Common"),
    ("Onyx", "ores/34_onyx_ore.png", 272, 190, 3, "Common"),
    ("Peridot", "ores/35_peridot_ore.png", 283, 199, 3, "Uncommon"),
    ("Aquamarine", "ores/36_aquamarine_ore.png", 295, 208, 3, "Uncommon"),
    ("Turquoise", "ores/37_turquoise_ore.png", 306, 217, 3, "Uncommon"),
    ("Moonstone", "ores/38_moonstone_ore.png", 318, 226, 3, "Rare"),
    ("Sunstone", "ores/39_sunstone_ore.png", 330, 235, 3, "Rare"),
    ("Lapis", "ores/40_lapis_ore.png", 342, 244, 3, "Epic"),
    ("Malachite", "ores/41_malachite_ore.png", 354, 253, 4, "Common"),
    ("Azurite", "ores/42_azurite_ore.png", 367, 263, 4, "Common"),
    ("Graphite", "ores/43_graphite_ore.png", 379, 273, 4, "Common"),
    ("Flint", "ores/44_flint_ore.png", 392, 282, 4, "Common"),
    ("Amber", "ores/45_amber_ore.png", 404, 292, 4, "Uncommon"),
    ("Fluorite", "ores/46_fluorite_ore.png", 417, 302, 4, "Uncommon"),
    ("Cryolite", "ores/47_cryolite_ore.png", 430, 312, 4, "Uncommon"),
    ("Mythril", "ores/48_mythril_ore.png", 443, 323, 4, "Rare"),
    ("Adamantite", "ores/49_adamantite_ore.png", 456, 333, 4, "Rare"),
    ("Orichalcum", "ores/50_orichalcum_ore.png", 469, 344, 4, "Epic"),
    ("Starmetal", "ores/51_starmetal_ore.png", 483, 354, 5, "Common"),
    ("Voidstone", "ores/52_voidstone_ore.png", 496, 365, 5, "Common"),
    ("Ember Crystal", "ores/53_ember_crystal_ore.png", 510, 375, 5, "Common"),
    ("Frost Crystal", "ores/54_frost_crystal_ore.png", 523, 386, 5, "Common"),
    ("Luminite", "ores/55_luminite_ore.png", 537, 397, 5, "Uncommon"),
    ("Plasma Ore", "ores/56_plasma_ore_ore.png", 551, 408, 5, "Uncommon"),
    ("Aether Shard", "ores/57_aether_shard_ore.png", 565, 420, 5, "Uncommon"),
    ("Bloodstone", "ores/58_bloodstone_ore.png", 579, 431, 5, "Rare"),
    ("Meteorite", "ores/59_meteorite_ore.png", 593, 442, 5, "Rare"),
    ("Celestine", "ores/60_celestine_ore.png", 607, 454, 5, "Legendary"),
]

class Ore:
    def __init__(
        self,
        name: str,
        icon: pygame.Surface,
        dark_icon: pygame.Surface,
        image: pygame.Surface,
        color: tuple,
        health: int,
        coin: int,
        level: int,
        rarity: str,
        found: int = 0,
    ):
        self.name = name
        self.icon = icon
        self.dark_icon = dark_icon
        self.image = image
        self.color = color
        self.health = health
        self.coin = coin
        self.level = level
        self.rarity = rarity
        self.found = found


@dataclass
class Upgrade:
    name: str
    description: str
    base_cost: int
    max_level: int
    level: int = 0

    @property
    def cost(self):
        return int(self.base_cost * 1.6 ** self.level)

    @property
    def is_maxed(self):
        return self.level >= self.max_level


@dataclass
class Particle:
    x: float
    y: float
    velocity_x: float
    velocity_y: float
    lifetime: float
    color: tuple

    def update(self, delta_time):
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        self.velocity_y += 700 * delta_time
        self.lifetime -= delta_time

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), 6, 6))


@dataclass
class Popup:
    text: str
    x: int
    y: float
    lifetime: float

    def update(self, delta_time):
        self.y -= 50 * delta_time
        self.lifetime -= delta_time


class Miner:
    def __init__(self, idle_frame, walk_frames, x):
        self.idle_frame = idle_frame
        self.walk_frames = walk_frames
        self.x = float(x)
        self.jump_height = 0
        self.jump_velocity = 0
        self.facing = 1
        self.animation_timer = 0
        self.frame_index = 0
        self.is_walking = False

    def jump(self, world_scale):
        if self.jump_height > 0 or self.jump_velocity > 0:
            return False
        self.jump_velocity = 500 * world_scale
        return True

    def update(
        self,
        delta_time,
        keys,
        ore_x,
        world_left,
        world_right,
        movement_speed,
    ):
        if keys is None:
            direction = 0
        else:
            direction = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(
                keys[pygame.K_a] or keys[pygame.K_LEFT]
            )
        if self.jump_height > 0 or self.jump_velocity > 0:
            self.jump_height += self.jump_velocity * delta_time
            self.jump_velocity -= 1000 * delta_time
            if self.jump_height <= 0 and self.jump_velocity <= 0:
                self.jump_height = 0
                self.jump_velocity = 0
        self.is_walking = direction != 0
        if direction:
            next_x = self.x + direction * movement_speed * delta_time
            if self.jump_height == 0:
                if direction > 0 and self.x < ore_x:
                    next_x = min(next_x, ore_x - ORE_PLAYER_SEPARATION)
                elif direction < 0 and self.x > ore_x:
                    next_x = max(next_x, ore_x + ORE_PLAYER_SEPARATION)
            self.x = max(
                world_left + 36,
                min(world_right - 36, next_x),
            )
            self.facing = direction
            self.animation_timer += delta_time
            self.frame_index = int(self.animation_timer * 10) % len(self.walk_frames)
        else:
            self.animation_timer = 0
            self.frame_index = 0

    @property
    def frame(self):
        if self.is_walking:
            return self.walk_frames[self.frame_index]
        return self.idle_frame


class Game:
    def __init__(self):
        global SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_LEFT, WORLD_RIGHT, WORLD_GROUND
        global MINING_DISTANCE, ORE_PLAYER_SEPARATION

        pygame.init()
        # Web (pygbag/emscripten) needs a fixed window, no FULLSCREEN/SCALED flags.
        # Desktop keeps fullscreen for the original experience.
        if is_browser_runtime():
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            SCREEN_WIDTH, SCREEN_HEIGHT = self.screen.get_size()
        WORLD_LEFT = max(80, int(SCREEN_WIDTH * 0.055))
        WORLD_RIGHT = SCREEN_WIDTH - WORLD_LEFT
        WORLD_GROUND = int(SCREEN_HEIGHT * 0.76)
        self.world_scale = max(1.0, SCREEN_HEIGHT / 640)
        MINING_DISTANCE = round(92 * self.world_scale)
        ORE_PLAYER_SEPARATION = round(74 * self.world_scale)
        pygame.display.set_caption("Earth Corp")
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        self.ores = [self._load_ore(data) for data in ORE_DATA]
        self.player = self._load_player()
        self.pickaxe = Upgrade("Pickaxe", "+1 damage per swing", 10, 99)
        self.auto_miner = Upgrade("Auto Miner", "+1 damage per second", 50, 99)
        self.gold_touch = Upgrade("Gold Touch", "+10% coins per ore", 100, 99)
        self.lucky_strike = Upgrade("Lucky Strike", "+5% chance of double hit", 150, 10)
        self.heavy_swing = Upgrade("Heavy Swing", "+2 damage per click", 75, 25)
        self.ore_radar = Upgrade("Ore Radar", "+5% rare ore odds per level", 120, 10)
        self.dynamite = Upgrade("Dynamite", "5% chance for +5 damage", 200, 10)
        self.oil_tank = Upgrade("Oil Tank", "+25 maximum oil capacity per level", 100, 10)
        self.upgrades = [
            self.pickaxe,
            self.auto_miner,
            self.gold_touch,
            self.lucky_strike,
            self.heavy_swing,
            self.ore_radar,
            self.dynamite,
            self.oil_tank,
        ]

        self.coins = 0
        self.collected = 0
        self.level = 0
        self.current_ore_index = 0
        self.ore_health = 1
        self.ore_max_health = 1
        self.heat = MAX_HEAT
        self.last_mining_message = ""
        self.scroll = 0
        self.shake = 0
        self.auto_timer = 0
        self.banner_text = ""
        self.banner_timer = 0
        self.particles = []
        self.popups = []
        self.ore_rect = pygame.Rect(
            0, 0, int(88 * self.world_scale), int(88 * self.world_scale)
        )
        self.heater_x = self.renderer.heater_x
        self.active_panel = None
        self.dialogue_index = 0
        self.running = True
        self.won = False
        self.progress_dirty = False
        self.save_timer = 0
        self.spawn_ore()
        self.load_progress()

    @staticmethod
    def _load_ore(data):
        name, path, health, coin, level, rarity = data
        image = pygame.image.load(os.path.join(BASE_DIR, path)).convert_alpha()
        dark_icon = pygame.transform.scale(image, (40, 40))
        icon = dark_icon.copy()
        dark_icon.fill((60, 60, 60, 255), special_flags=pygame.BLEND_RGBA_MULT)
        try:
            avg = pygame.transform.average_color(image)
        except Exception:
            avg = (200, 200, 200, 255)
        return Ore(
            name=name,
            icon=icon,
            dark_icon=dark_icon,
            image=pygame.transform.scale(image, (256, 256)),
            color=avg,
            health=health,
            coin=coin,
            level=level,
            rarity=rarity,
        )

    @staticmethod
    def _load_player():
        def load_frame(name):
            path = os.path.join(BASE_DIR, "player", name)
            image = pygame.image.load(path).convert_alpha()
            size = max(64, int(64 * SCREEN_HEIGHT / 640))
            return pygame.transform.scale(image, (size, size))

        idle = load_frame("player_idle.png")
        walk_frames = [
            load_frame("player_walk_%d.png" % index)
            for index in range(1, 5)
        ]
        return Miner(
            idle,
            walk_frames,
            WORLD_LEFT + 55 * max(1.0, SCREEN_HEIGHT / 640),
        )

    @property
    def current_ore(self):
        return self.ores[self.current_ore_index]

    @property
    def upgrades_bought(self):
        return sum(upgrade.level for upgrade in self.upgrades)

    @property
    def max_heat(self):
        return MAX_HEAT + self.oil_tank.level * 25

    @property
    def discovered_ores(self):
        return sum(ore.found > 0 for ore in self.ores)

    def progress_data(self):
        return {
            "coins": self.coins,
            "collected": self.collected,
            "level": self.level,
            "current_ore_index": self.current_ore_index,
            "ore_health": self.ore_health,
            "heat": self.heat,
            "player_x": self.player.x,
            "upgrades": {upgrade.name: upgrade.level for upgrade in self.upgrades},
            "ores_found": [ore.found for ore in self.ores],
            "won": self.won,
        }

    def load_progress(self):
        if is_browser_runtime():
            from platform import window

            saved_text = window.localStorage.getItem(SAVE_KEY)
            if saved_text is None:
                return
        else:
            try:
                with open(SAVE_FILE, encoding="utf-8") as save_file:
                    saved_text = save_file.read()
            except FileNotFoundError:
                return
            except OSError as error:
                print("Could not load saved game progress: %s" % error)
                return

        try:
            saved_data = json.loads(saved_text)
        except (json.JSONDecodeError, TypeError) as error:
            print("Could not load saved game progress: %s" % error)
            return

        if not isinstance(saved_data, dict):
            print("Could not load saved game progress: save data is not an object")
            return

        def saved_integer(name, default, minimum=0, maximum=None):
            value = saved_data.get(name, default)
            if isinstance(value, bool) or not isinstance(value, int):
                return default
            value = max(minimum, value)
            return min(value, maximum) if maximum is not None else value

        self.coins = saved_integer("coins", self.coins)
        self.collected = saved_integer("collected", self.collected)
        self.level = saved_integer("level", self.level, maximum=len(LEVELS) - 1)

        saved_upgrades = saved_data.get("upgrades", {})
        if isinstance(saved_upgrades, dict):
            for upgrade in self.upgrades:
                saved_level = saved_upgrades.get(upgrade.name, upgrade.level)
                if isinstance(saved_level, int) and not isinstance(saved_level, bool):
                    upgrade.level = max(0, min(upgrade.max_level, saved_level))

        found_counts = saved_data.get("ores_found", [])
        if isinstance(found_counts, list):
            for ore, found_count in zip(self.ores, found_counts):
                if isinstance(found_count, int) and not isinstance(found_count, bool):
                    ore.found = max(0, found_count)

        self.current_ore_index = saved_integer(
            "current_ore_index",
            self.current_ore_index,
            maximum=len(self.ores) - 1,
        )
        self.heat = saved_integer("heat", self.heat, maximum=self.max_heat)
        self.ore_health = saved_integer("ore_health", self.ore_health)
        self.won = saved_data.get("won", False) is True

        saved_player_x = saved_data.get("player_x")
        if (
            isinstance(saved_player_x, (int, float))
            and not isinstance(saved_player_x, bool)
            and math.isfinite(saved_player_x)
        ):
            self.player.x = max(
                WORLD_LEFT + 36,
                min(WORLD_RIGHT - 36, float(saved_player_x)),
            )

        selected_ore = self.current_ore
        self.ore_max_health = round(
            selected_ore.health * (1 + ORE_HARDNESS_PER_LEVEL * selected_ore.level)
        )
        self.ore_health = min(self.ore_health, self.ore_max_health)
        self.progress_dirty = False
        self.check_win()

    def save_progress(self):
        saved_text = json.dumps(self.progress_data())
        if is_browser_runtime():
            from platform import window

            window.localStorage.setItem(SAVE_KEY, saved_text)
        else:
            temporary_file = SAVE_FILE + ".tmp"
            try:
                with open(temporary_file, "w", encoding="utf-8") as save_file:
                    save_file.write(saved_text)
                os.replace(temporary_file, SAVE_FILE)
            except OSError as error:
                print("Could not save game progress: %s" % error)
                return False
        self.progress_dirty = False
        self.save_timer = 0
        return True

    def check_win(self):
        if (
            not self.won
            and self.level == len(LEVELS) - 1
            and self.discovered_ores == len(self.ores)
        ):
            self.won = True
            self.banner_text = "CAMPAIGN COMPLETE"
            self.banner_timer = 4
            self.save_progress()

    def reward_for(self, ore):
        return max(1, round(ore.coin * (1 + 0.1 * self.gold_touch.level)))

    def spawn_ore(self):
        rarity_ranks = {rarity: rank for rank, rarity in enumerate(RARITY)}
        weights = []
        for ore in self.ores:
            if ore.level > self.level:
                weights.append(0)
                continue
            level_weight = 3 if ore.level == self.level else 1
            rarity_boost = (
                1 + self.ore_radar.level * rarity_ranks[ore.rarity] * 0.05
            )
            weights.append(RARITY[ore.rarity][0] * level_weight * rarity_boost)
        self.current_ore_index = random.choices(range(len(self.ores)), weights)[0]
        ore = self.current_ore
        self.ore_max_health = round(
            ore.health * (1 + ORE_HARDNESS_PER_LEVEL * ore.level)
        )
        self.ore_health = self.ore_max_health
        self.ore_rect.center = (
            self.renderer.ore_x,
            WORLD_GROUND - self.ore_rect.height // 2,
        )

    @property
    def is_near_ore(self):
        return abs(self.player.x - self.ore_rect.centerx) <= MINING_DISTANCE

    @property
    def is_near_heater(self):
        return abs(self.player.x - self.heater_x) <= MINING_DISTANCE

    @property
    def can_mine(self):
        return self.heat >= HEAT_PER_HIT

    def try_mine(self):
        if self.is_near_ore:
            return self.hit(self.click_damage())
        return False

    def try_refuel(self):
        if self.is_near_heater and self.heat < self.max_heat:
            self.heat = self.max_heat
            self.last_mining_message = "HEAT RESTORED"
            self.banner_text = "HEAT RESTORED"
            self.banner_timer = 1.5
            self.progress_dirty = True
            return True
        return False

    def check_level(self):
        while (
            self.level + 1 < len(LEVELS)
            and self.upgrades_bought >= LEVELS[self.level + 1][1]
            and self.collected >= LEVELS[self.level + 1][2]
        ):
            self.level += 1
            self.banner_text = "LEVEL UP: " + LEVELS[self.level][0]
            self.banner_timer = 2.5
        self.check_win()

    def click_damage(self):
        damage = 1 + self.pickaxe.level + 2 * self.heavy_swing.level
        if random.random() < 0.05 * self.lucky_strike.level:
            damage *= 2
        if random.random() < 0.05 * self.dynamite.level:
            damage += 5
        return damage

    def hit(self, damage):
        if not self.can_mine:
            self.last_mining_message = "RETURN TO THE OIL FACTORY"
            if self.banner_text != self.last_mining_message or self.banner_timer <= 0:
                self.banner_text = self.last_mining_message
                self.banner_timer = 1.2
            return False

        self.heat = max(0, self.heat - HEAT_PER_HIT)
        self.progress_dirty = True
        self.last_mining_message = ""
        ore = self.current_ore
        self.ore_health -= damage
        self.shake = 0.15
        for _ in range(6):
            self.particles.append(
                Particle(
                    self.ore_rect.centerx + random.randint(-60, 60),
                    self.ore_rect.centery + random.randint(-60, 60),
                    random.uniform(-120, 120),
                    random.uniform(-220, -40),
                    0.6,
                    ore.color,
                )
            )

        if self.ore_health <= 0:
            gain = self.reward_for(ore)
            self.coins += gain
            self.collected += 1
            ore.found += 1
            self.popups.append(
                Popup("+%d" % gain, self.ore_rect.centerx - 20, self.ore_rect.top, 1.0)
            )
            for _ in range(24):
                self.particles.append(
                    Particle(
                        self.ore_rect.centerx,
                        self.ore_rect.centery,
                        random.uniform(-300, 300),
                        random.uniform(-350, 50),
                        0.9,
                        RARITY[ore.rarity][1],
                    )
                )
            self.check_level()
            self.spawn_ore()
        return True

    def shop_item_rect(self, index):
        return self.renderer.shop_item_rect(index, len(self.upgrades))

    def panel_button_rect(self, name):
        return self.renderer.panel_button_rect(name)

    @property
    def panel_close_rect(self):
        return self.renderer.panel_close_rect

    @property
    def jump_button_rect(self):
        return self.renderer.jump_button_rect

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.save_progress()
            self.running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.active_panel:
                self.active_panel = None
            else:
                self.save_progress()
                self.running = False
        elif self.won:
            return
        elif event.type == pygame.KEYDOWN and event.key in (
            pygame.K_u,
            pygame.K_g,
            pygame.K_t,
        ):
            panel = {
                pygame.K_u: "shop",
                pygame.K_g: "guide",
                pygame.K_t: "dialogue",
            }[event.key]
            self.active_panel = None if self.active_panel == panel else panel
        elif (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_w
            and self.active_panel is None
        ):
            self.player.jump(self.world_scale)
        elif event.type == pygame.MOUSEWHEEL:
            if self.active_panel == "guide":
                self.scroll -= event.y * 40
        elif event.type == pygame.KEYDOWN and event.key in (
            pygame.K_e,
            pygame.K_SPACE,
        ) and self.active_panel is None:
            if event.key == pygame.K_e and not self.try_refuel():
                self.try_mine()
            elif event.key == pygame.K_SPACE:
                self.try_mine()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)

    def handle_click(self, position):
        if self.active_panel is None and self.jump_button_rect.collidepoint(position):
            self.player.jump(self.world_scale)
            return

        for name in ("shop", "guide", "dialogue"):
            if self.panel_button_rect(name).collidepoint(position):
                self.active_panel = (
                    None if self.active_panel == name else name
                )
                return

        if self.active_panel is not None:
            if self.panel_close_rect.collidepoint(position):
                self.active_panel = None
            elif self.active_panel == "shop":
                self.buy_upgrade_at(position)
            elif self.active_panel == "dialogue":
                self.dialogue_index += 1
            return

        if self.ore_rect.collidepoint(position):
            self.try_mine()

    def buy_upgrade_at(self, position):
        for index, upgrade in enumerate(self.upgrades):
            if (
                self.shop_item_rect(index).collidepoint(position)
                and not upgrade.is_maxed
                and self.coins >= upgrade.cost
            ):
                self.coins -= upgrade.cost
                upgrade.level += 1
                self.progress_dirty = True
                self.check_level()
                self.save_progress()
                break

    def update(self, delta_time):
        if self.won:
            return

        if self.active_panel == "guide":
            guide_height = self.renderer.panel_rect.height - 120
            self.scroll = max(
                0,
                min(self.scroll, len(self.ores) * 52 - guide_height),
            )
        else:
            self.scroll = 0
        keys = pygame.key.get_pressed() if self.active_panel is None else None
        self.player.update(
            delta_time,
            keys,
            self.ore_rect.centerx,
            WORLD_LEFT,
            WORLD_RIGHT,
            190 * self.world_scale,
        )

        if self.auto_miner.level and self.is_near_ore:
            self.auto_timer += delta_time
            if self.auto_timer >= 1 and self.can_mine:
                self.auto_timer -= 1
                self.hit(self.auto_miner.level)
            elif not self.can_mine:
                self.auto_timer = 0
        else:
            self.auto_timer = 0

        self.shake = max(0, self.shake - delta_time)
        self.banner_timer = max(0, self.banner_timer - delta_time)
        for particle in self.particles:
            particle.update(delta_time)
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for popup in self.popups:
            popup.update(delta_time)
        self.popups = [p for p in self.popups if p.lifetime > 0]

        if self.progress_dirty:
            self.save_timer += delta_time
            if self.save_timer >= 2:
                self.save_progress()

    async def run(self):
        while self.running:
            delta_time = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(delta_time)
            self.renderer.draw(self)
            await asyncio.sleep(0)
        if self.progress_dirty:
            self.save_progress()
        if not is_browser_runtime():
            pygame.quit()


class Renderer:
    BACKGROUND = (13, 17, 28)
    PANEL = (18, 23, 35)
    CARD = (26, 33, 48)
    RAISED = (33, 41, 58)
    TEXT = (235, 240, 248)
    MUTED = (160, 173, 192)
    ACCENT = (83, 205, 177)
    GOLD = (255, 195, 92)

    def __init__(self, screen):
        self.screen = screen
        def _font(size, bold=False):
            for name in ("segoeui", "arial", "dejavu", None):
                try:
                    if name is None:
                        return pygame.font.Font(None, size)
                    f = pygame.font.SysFont(name, size, bold)
                    if f is not None:
                        return f
                except Exception:
                    continue
            return pygame.font.Font(None, size)
        self.font = _font(16)
        self.small = _font(13)
        self.mid = _font(21, True)
        self.big = _font(30, True)
        self.title_font = _font(17, True)
        self.world_rect = screen.get_rect()
        self.world_scale = SCREEN_HEIGHT / 640
        self.panel_width = min(560, SCREEN_WIDTH - 140)
        self.panel_height = min(SCREEN_HEIGHT - 100, 760)
        self.active_panel = None
        self.sky = self._load_scaled(
            "background/bg_sky.png", (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.clouds = self._load_scaled(
            "background/bg_clouds.png", (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.far_hills = self._load_scaled(
            "background/bg_hills_far.png", (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.near_hills = self._load_scaled(
            "background/bg_hills_near.png", (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.mine_building = self._load_scaled(
            "buildings/mine.png", (round(112 * self.world_scale), round(112 * self.world_scale))
        )
        self.power_plant = self._load_scaled(
            "buildings/fossil_fuel_processing_plant.png",
            (round(144 * self.world_scale), round(112 * self.world_scale)),
        )
        tile_size = max(32, round(32 * self.world_scale))
        self.ground_top = self._load_scaled("ground/ground_top.png", (tile_size, tile_size))
        self.ground_dirt = self._load_scaled("ground/ground_dirt.png", (tile_size, tile_size))
        self.ground_stone = self._load_scaled("ground/ground_stone.png", (tile_size, tile_size))
        self.pipe_horizontal = self._load_scaled(
            "pipes/pipe_horizontal.png", (tile_size, tile_size)
        )
        self.pipe_valve = self._load_scaled("pipes/pipe_valve.png", (tile_size, tile_size))
        self.miner_robot = self._load_scaled("robots/robot_miner.png", (tile_size, tile_size))
        self.dialogue_robot = self._load_scaled(
            "robots/robot_scrapper.png", (round(96 * self.world_scale), round(96 * self.world_scale))
        )
        self.mine_x = max(WORLD_LEFT + 10, round(SCREEN_WIDTH * 0.16))
        self.plant_x = min(
            WORLD_RIGHT - self.power_plant.get_width() - 10,
            round(SCREEN_WIDTH * 0.72),
        )
        self.ore_x = (
            self.mine_x
            + self.mine_building.get_width()
            + round(82 * self.world_scale)
        )
        self.heater_x = self.plant_x + self.power_plant.get_width() // 2

    def _load_scaled(self, relative_path, size):
        path = os.path.join(BASE_DIR, relative_path)
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, size)

    @property
    def panel_rect(self):
        height = (
            min(self.panel_height, 420)
            if self.active_panel == "dialogue"
            else self.panel_height
        )
        return pygame.Rect(
            (SCREEN_WIDTH - self.panel_width) // 2,
            (SCREEN_HEIGHT - height) // 2,
            self.panel_width,
            height,
        )

    @property
    def panel_close_rect(self):
        return pygame.Rect(
            self.panel_rect.right - 48,
            self.panel_rect.y + 16,
            32,
            32,
        )

    @property
    def jump_button_rect(self):
        return pygame.Rect(SCREEN_WIDTH - 122, SCREEN_HEIGHT - 105, 104, 48)

    def panel_button_rect(self, name):
        button_width, button_height = 88, 54
        if name == "shop":
            return pygame.Rect(
                18, SCREEN_HEIGHT // 2 - 88, button_width, button_height
            )
        if name == "guide":
            return pygame.Rect(
                18, SCREEN_HEIGHT // 2 - 20, button_width, button_height
            )
        return pygame.Rect(
            SCREEN_WIDTH - button_width - 18,
            SCREEN_HEIGHT // 2 - 54,
            button_width,
            button_height,
        )

    def shop_item_rect(self, index, item_count):
        panel = self.panel_rect
        row_height = (panel.height - 116) // item_count
        return pygame.Rect(
            panel.x + 20,
            panel.y + 88 + index * row_height,
            panel.width - 40,
            row_height - 8,
        )

    def text(self, font, value, color, position):
        self.screen.blit(font.render(value, True, color), position)

    def centered_text(self, font, value, color, y):
        x = 500 - font.size(value)[0] // 2
        self.text(font, value, color, (x, y))

    def card(self, rect, color=None, border=None, radius=10):
        pygame.draw.rect(
            self.screen,
            color or self.CARD,
            rect,
            border_radius=radius,
        )
        if border:
            pygame.draw.rect(
                self.screen,
                border,
                rect,
                width=1,
                border_radius=radius,
            )

    def progress_bar(self, rect, amount, color, background=None):
        self.card(rect, background or self.RAISED, radius=rect.height // 2)
        fill = rect.inflate(-4, -4)
        fill.width = max(0, min(fill.width, int(fill.width * amount)))
        if fill.width:
            pygame.draw.rect(self.screen, color, fill, border_radius=fill.height // 2)

    def draw(self, game):
        self.active_panel = game.active_panel
        self.draw_mining_scene(game)
        self.draw_effects(game)
        self.draw_hud(game)
        self.draw_side_buttons(game)
        self.draw_jump_button(game)
        if game.active_panel == "shop":
            self.draw_shop(game)
        elif game.active_panel == "guide":
            self.draw_guide(game)
        elif game.active_panel == "dialogue":
            self.draw_dialogue(game)
        if game.won:
            self.draw_victory(game)
        pygame.display.flip()

    def draw_victory(self, game):
        shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        shade.fill((3, 7, 14, 210))
        self.screen.blit(shade, (0, 0))

        panel = pygame.Rect(
            SCREEN_WIDTH // 2 - 250,
            SCREEN_HEIGHT // 2 - 120,
            500,
            240,
        )
        self.card(panel, self.PANEL, self.ACCENT, radius=20)
        title = self.big.render("CAMPAIGN COMPLETE", True, self.GOLD)
        subtitle = self.font.render(
            "Every ore discovered. The whole site is yours!",
            True,
            self.TEXT,
        )
        stats = self.font.render(
            "%s ores mined  |  %s coins earned"
            % (format(game.collected, ","), format(game.coins, ",")),
            True,
            self.MUTED,
        )
        exit_hint = self.small.render("Press ESC to exit", True, self.MUTED)
        self.screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 66)))
        self.screen.blit(
            subtitle,
            subtitle.get_rect(center=(panel.centerx, panel.y + 118)),
        )
        self.screen.blit(stats, stats.get_rect(center=(panel.centerx, panel.y + 157)))
        self.screen.blit(
            exit_hint,
            exit_hint.get_rect(center=(panel.centerx, panel.y + 204)),
        )

    def draw_mining_scene(self, game):
        self.screen.blit(self.sky, (0, 0))
        self.screen.blit(self.clouds, (0, 0))
        self.screen.blit(self.far_hills, (0, 0))
        self.screen.blit(self.near_hills, (0, 0))

        ground_top = WORLD_GROUND - round(18 * self.world_scale)
        self.screen.blit(
            self.mine_building,
            (self.mine_x, ground_top - self.mine_building.get_height()),
        )
        self.screen.blit(
            self.power_plant,
            (self.plant_x, ground_top - self.power_plant.get_height()),
        )
        tile_width = self.ground_top.get_width()
        pipe_y = ground_top - round(52 * self.world_scale)
        pipe_start = self.mine_x + self.mine_building.get_width()
        for x in range(pipe_start, self.plant_x, tile_width):
            self.screen.blit(self.pipe_horizontal, (x, pipe_y))
        if self.plant_x - pipe_start > tile_width:
            self.screen.blit(self.pipe_valve, (pipe_start + tile_width, pipe_y))
        robot_x = min(WORLD_RIGHT - tile_width, round(SCREEN_WIDTH * 0.59))
        self.screen.blit(self.miner_robot, (robot_x, WORLD_GROUND - tile_width))
        tile_width = self.ground_top.get_width()
        for tile_x in range(0, SCREEN_WIDTH, tile_width):
            self.screen.blit(self.ground_top, (tile_x, ground_top))
            self.screen.blit(self.ground_dirt, (tile_x, ground_top + tile_width))
            self.screen.blit(self.ground_stone, (tile_x, ground_top + tile_width * 2))

        ore = game.current_ore
        ore_rect = game.ore_rect
        rarity_color = RARITY[ore.rarity][1]
        ring_color = rarity_color if game.is_near_ore else (70, 83, 103)
        pygame.draw.ellipse(
            self.screen,
            (14, 19, 30),
            (
                ore_rect.x - 5,
                WORLD_GROUND - round(12 * self.world_scale),
                ore_rect.width + 10,
                round(20 * self.world_scale),
            ),
        )
        ore_radius = ore_rect.width // 2
        pygame.draw.circle(self.screen, ring_color, ore_rect.center, ore_radius + 7, 3)
        pygame.draw.circle(self.screen, (20, 27, 39), ore_rect.center, ore_radius)
        icon_size = int(ore_rect.width * 0.88 * (1 + game.shake * 0.6))
        ore_icon = pygame.transform.scale(ore.icon, (icon_size, icon_size))
        self.screen.blit(ore_icon, ore_icon.get_rect(center=ore_rect.center))

        name = self.small.render(ore.name, True, self.TEXT)
        rarity = self.small.render(ore.rarity.upper(), True, rarity_color)
        label_width = max(name.get_width(), rarity.get_width()) + 18
        label_rect = pygame.Rect(
            ore_rect.centerx - label_width // 2,
            ore_rect.top - 50,
            label_width,
            40,
        )
        self.card(label_rect, self.PANEL, (54, 67, 87), radius=8)
        self.screen.blit(name, (label_rect.centerx - name.get_width() // 2, label_rect.y + 4))
        self.screen.blit(
            rarity,
            (label_rect.centerx - rarity.get_width() // 2, label_rect.y + 21),
        )

        heater_radius = round(28 * self.world_scale)
        heater_center = (game.heater_x, WORLD_GROUND - heater_radius)
        heater_color = (255, 202, 98) if game.is_near_heater else (213, 126, 74)
        pygame.draw.ellipse(
            self.screen,
            (18, 19, 27),
            (
                game.heater_x - heater_radius - 12,
                WORLD_GROUND - 12,
                (heater_radius + 12) * 2,
                round(18 * self.world_scale),
            ),
        )
        pygame.draw.circle(self.screen, (42, 29, 31), heater_center, heater_radius + 7)
        pygame.draw.circle(self.screen, heater_color, heater_center, heater_radius + 5, 3)
        pygame.draw.circle(
            self.screen,
            (244, 114, 65),
            (game.heater_x, heater_center[1] - round(5 * self.world_scale)),
            max(4, round(10 * self.world_scale)),
        )
        heater_label = "OIL  %d / %d" % (game.heat, game.max_heat)
        heater_surface = self.small.render(heater_label, True, heater_color)
        heater_rect = pygame.Rect(
            0,
            0,
            heater_surface.get_width() + 18,
            round(27 * self.world_scale),
        )
        heater_rect.center = (game.heater_x, WORLD_GROUND - heater_radius * 2)
        self.card(heater_rect, self.PANEL, (110, 77, 66), radius=9)
        self.screen.blit(heater_surface, heater_surface.get_rect(center=heater_rect.center))

        player_image = game.player.frame
        if game.player.facing < 0:
            player_image = pygame.transform.flip(player_image, True, False)
        player_rect = player_image.get_rect(
            midbottom=(
                round(game.player.x),
                WORLD_GROUND - round(game.player.jump_height),
            )
        )
        self.screen.blit(player_image, player_rect)

        if game.is_near_heater and game.heat < game.max_heat:
            prompt = "PRESS E TO REFILL AT OIL FACTORY"
            prompt_color = (255, 202, 98)
        elif not game.can_mine:
            prompt = "NO HEAT  |  RETURN TO OIL FACTORY AND PRESS E"
            prompt_color = (255, 144, 108)
        elif game.is_near_heater:
            prompt = "OIL FACTORY READY  |  E REFILLS HEAT"
            prompt_color = (255, 202, 98)
        elif game.is_near_ore:
            prompt = "IN RANGE  |  PRESS E / SPACE TO MINE"
            prompt_color = self.ACCENT
        else:
            prompt = "MOVE TO THE DEPOSIT  |  A / D OR ARROWS"
            prompt_color = self.TEXT
        prompt_surface = self.small.render(prompt, True, prompt_color)
        prompt_rect = pygame.Rect(0, 0, prompt_surface.get_width() + 28, 34)
        prompt_rect.center = (
            SCREEN_WIDTH // 2,
            WORLD_GROUND + round(58 * self.world_scale),
        )
        self.card(prompt_rect, self.PANEL, (54, 67, 87), radius=12)
        self.screen.blit(prompt_surface, prompt_surface.get_rect(center=prompt_rect.center))

    def draw_hud(self, game):
        hud = pygame.Rect(SCREEN_WIDTH // 2 - 240, 20, 480, 92)
        self.card(hud, (15, 21, 33, 230), (88, 105, 128), radius=14)
        self.text(self.title_font, "EARTH CORP  /  MINING SITE", self.TEXT, (hud.x + 18, hud.y + 11))
        self.text(
            self.small,
            "TIER %s  |  ORES MINED %s" % (
                LEVELS[game.level][0].upper(),
                format(game.collected, ","),
            ),
            self.MUTED,
            (hud.x + 18, hud.y + 42),
        )
        damage = 1 + game.pickaxe.level + 2 * game.heavy_swing.level
        self.text(
            self.small,
            "MINING POWER  %d  |  AUTO %d/S" % (damage, game.auto_miner.level),
            self.ACCENT,
            (hud.x + 18, hud.y + 63),
        )
        balance = "$ " + format(game.coins, ",")
        balance_surface = self.mid.render(balance, True, self.GOLD)
        self.screen.blit(balance_surface, (hud.right - balance_surface.get_width() - 18, hud.y + 24))

        footer = pygame.Rect(SCREEN_WIDTH // 2 - 240, SCREEN_HEIGHT - 88, 480, 72)
        self.card(footer, (15, 21, 33, 230), (88, 105, 128), radius=12)
        self.text(
            self.small,
            "ORE",
            self.TEXT,
            (footer.x + 14, footer.y + 10),
        )
        self.progress_bar(
            pygame.Rect(footer.x + 65, footer.y + 12, 240, 13),
            max(0, game.ore_health) / game.ore_max_health,
            (235, 92, 98),
            (67, 42, 51),
        )
        self.text(
            self.small,
            "%d / %d" % (max(0, game.ore_health), game.ore_max_health),
            self.TEXT,
            (footer.x + 320, footer.y + 10),
        )
        self.text(
            self.small,
            "HEAT",
            (255, 202, 98),
            (footer.x + 14, footer.y + 42),
        )
        heat_color = (255, 170, 80) if game.heat > 25 else (255, 104, 88)
        self.progress_bar(
            pygame.Rect(footer.x + 65, footer.y + 44, 240, 13),
            game.heat / game.max_heat,
            heat_color,
            (67, 42, 51),
        )
        self.text(
            self.small,
            "%d/%d | E REFILL" % (game.heat, game.max_heat),
            heat_color,
            (footer.x + 320, footer.y + 42),
        )

    def draw_side_buttons(self, game):
        labels = {
            "shop": ("SHOP", "U"),
            "guide": ("ORES", "G"),
            "dialogue": ("TALK", "T"),
        }
        for name, (label, shortcut) in labels.items():
            rect = self.panel_button_rect(name)
            selected = game.active_panel == name
            color = self.RAISED if selected else self.PANEL
            border = self.ACCENT if selected else (88, 105, 128)
            self.card(rect, color, border, radius=12)
            label_surface = self.font.render(label, True, self.TEXT)
            key_surface = self.small.render("[%s]" % shortcut, True, self.MUTED)
            self.screen.blit(
                label_surface,
                label_surface.get_rect(center=(rect.centerx, rect.y + 18)),
            )
            self.screen.blit(
                key_surface,
                key_surface.get_rect(center=(rect.centerx, rect.y + 39)),
            )
        self.text(
            self.small,
            "ESC  EXIT",
            self.TEXT,
            (SCREEN_WIDTH - 95, SCREEN_HEIGHT - 30),
        )

    def draw_jump_button(self, game):
        rect = self.jump_button_rect
        color = self.RAISED if game.player.jump_height > 0 else self.PANEL
        self.card(rect, color, self.ACCENT, radius=12)
        label = self.font.render("JUMP", True, self.TEXT)
        shortcut = self.small.render("[W]", True, self.MUTED)
        self.screen.blit(label, label.get_rect(center=(rect.centerx, rect.y + 17)))
        self.screen.blit(
            shortcut,
            shortcut.get_rect(center=(rect.centerx, rect.y + 36)),
        )

    def draw_ore_list(self, game):
        pygame.draw.rect(
            self.screen, self.PANEL, (0, 0, 300, SCREEN_HEIGHT)
        )
        old_clip = self.screen.get_clip()
        self.screen.set_clip(
            pygame.Rect(0, ORE_LIST_TOP, 300, SCREEN_HEIGHT - ORE_LIST_TOP)
        )
        for index, ore in enumerate(game.ores):
            rect = pygame.Rect(
                8,
                ORE_LIST_TOP + 6 + index * ORE_ROW_HEIGHT - game.scroll,
                284,
                ORE_ROW_HEIGHT - 6,
            )
            if rect.bottom < ORE_LIST_TOP or rect.top > SCREEN_HEIGHT:
                continue
            locked = ore.level > game.level
            selected = index == game.current_ore_index
            background = self.RAISED if selected else self.CARD
            border = self.ACCENT if selected else None
            self.card(rect, background, border, radius=9)
            if index == game.current_ore_index:
                pygame.draw.rect(
                    self.screen,
                    self.ACCENT,
                    (rect.x, rect.y + 10, 3, rect.height - 20),
                    border_radius=2,
                )
            icon = ore.dark_icon if locked else ore.icon
            self.screen.blit(icon, (rect.x + 6, rect.y + 10))
            name_color = self.MUTED if locked else self.TEXT
            self.text(self.font, ore.name, name_color, (rect.x + 56, rect.y + 5))
            if locked:
                level_name = LEVELS[ore.level][0]
                self.text(
                    self.small,
                    "Locked: " + level_name,
                    self.MUTED,
                    (rect.x + 56, rect.y + 24),
                )
            else:
                level_name = LEVELS[ore.level][0]
                self.text(
                    self.small,
                    "%s  %s" % (level_name, ore.rarity),
                    RARITY[ore.rarity][1],
                    (rect.x + 56, rect.y + 25),
                )
                self.text(
                    self.small,
                    "HP %d  $%d" % (ore.health, ore.coin),
                    (190, 199, 214),
                    (rect.x + 56, rect.y + 43),
                )
                if ore.found:
                    count = "x%d" % ore.found
                    count_rect = pygame.Rect(
                        rect.right - self.small.size(count)[0] - 17,
                        rect.y + 7,
                        self.small.size(count)[0] + 10,
                        19,
                    )
                    self.card(count_rect, self.CARD, radius=8)
                    self.text(
                        self.small,
                        count,
                        self.TEXT,
                        (count_rect.x + 5, count_rect.y + 2),
                    )
        self.screen.set_clip(old_clip)
        pygame.draw.rect(self.screen, self.PANEL, (0, 0, 300, 54))
        discovered = sum(ore.found > 0 for ore in game.ores)
        self.text(self.title_font, "FIELD GUIDE", self.TEXT, (14, 7))
        self.text(
            self.small,
            "%d / %d discovered" % (discovered, len(game.ores)),
            self.MUTED,
            (14, 31),
        )
        self.progress_bar(
            pygame.Rect(185, 35, 99, 7),
            discovered / len(game.ores),
            self.ACCENT,
        )

    def draw_ore_area(self, game):
        ore = game.current_ore
        self.text(
            self.small,
            "ACTIVE SITE  |  +40% ORE HP PER TIER",
            self.ACCENT,
            (321, 17),
        )
        self.text(self.small, "CURRENT TIER", self.MUTED, (321, 42))
        self.text(self.font, LEVELS[game.level][0], self.TEXT, (321, 58))
        balance = pygame.Rect(516, 9, 164, 62)
        self.card(balance, self.RAISED, (49, 61, 79), radius=12)
        self.text(self.small, "BALANCE", self.MUTED, (balance.x + 12, balance.y + 7))
        self.text(
            self.mid,
            "$ %s" % format(game.coins, ","),
            self.GOLD,
            (balance.x + 12, balance.y + 25),
        )

        if game.level + 1 < len(LEVELS):
            next_level = LEVELS[game.level + 1]
            upgrade_goal = next_level[1]
            ore_goal = next_level[2]
            progress = min(
                1,
                game.upgrades_bought / max(1, upgrade_goal),
                game.collected / max(1, ore_goal),
            )
            tier_label = "NEXT TIER  %s" % next_level[0].upper()
        else:
            upgrade_goal = game.upgrades_bought
            ore_goal = game.collected
            progress = 1
            tier_label = "MAXIMUM TIER REACHED"
        progress_card = pygame.Rect(320, 83, 360, 48)
        self.card(progress_card, self.CARD, radius=10)
        self.text(self.small, tier_label, self.TEXT, (progress_card.x + 12, progress_card.y + 7))
        requirements = "UPGRADES  %d/%d     ORES  %d/%d" % (
            game.upgrades_bought,
            upgrade_goal,
            game.collected,
            ore_goal,
        )
        self.text(self.small, requirements, self.MUTED, (progress_card.x + 12, progress_card.y + 26))
        self.progress_bar(
            pygame.Rect(progress_card.right - 84, progress_card.y + 29, 70, 9),
            progress,
            self.ACCENT,
        )

        health_card = pygame.Rect(320, 469, 360, 59)
        self.card(health_card, self.CARD, radius=10)
        self.text(self.small, "ORE INTEGRITY", self.MUTED, (health_card.x + 12, health_card.y + 8))
        self.text(
            self.font,
            "%d / %d" % (max(0, game.ore_health), game.ore_max_health),
            self.TEXT,
            (health_card.right - 75, health_card.y + 7),
        )
        self.progress_bar(
            pygame.Rect(health_card.x + 12, health_card.y + 33, health_card.width - 24, 12),
            max(0, game.ore_health) / game.ore_max_health,
            (235, 92, 98),
            (67, 42, 51),
        )
        self.card(pygame.Rect(320, 539, 174, 48), self.CARD, radius=9)
        self.card(pygame.Rect(506, 539, 174, 48), self.CARD, radius=9)
        self.text(self.small, "ORE VALUE", self.MUTED, (332, 546))
        self.text(
            self.font,
            "%s coins" % format(game.reward_for(ore), ","),
            self.GOLD,
            (332, 563),
        )
        damage = 1 + game.pickaxe.level + 2 * game.heavy_swing.level
        self.text(self.small, "MINING POWER", self.MUTED, (518, 546))
        self.text(
            self.font,
            "%d hit  |  %d auto/s" % (damage, game.auto_miner.level),
            self.ACCENT,
            (518, 563),
        )

    def draw_effects(self, game):
        for particle in game.particles:
            particle.draw(self.screen)
        for popup in game.popups:
            self.text(self.mid, popup.text, (255, 230, 100), (popup.x, popup.y))
        if game.banner_timer > 0:
            label = self.big.render(game.banner_text, True, (255, 230, 100))
            shadow = self.big.render(game.banner_text, True, (20, 14, 30))
            position = (
                SCREEN_WIDTH // 2 - label.get_width() // 2,
                SCREEN_HEIGHT // 2 - label.get_height() // 2,
            )
            self.screen.blit(shadow, (position[0] + 3, position[1] + 3))
            self.screen.blit(label, position)

    def draw_panel_base(self, title, subtitle):
        shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        shade.fill((3, 7, 14, 175))
        self.screen.blit(shade, (0, 0))

        panel = self.panel_rect
        self.card(panel, self.PANEL, (91, 112, 139), radius=18)
        self.text(self.title_font, title, self.TEXT, (panel.x + 24, panel.y + 18))
        self.text(self.small, subtitle, self.MUTED, (panel.x + 24, panel.y + 44))
        self.card(self.panel_close_rect, self.RAISED, (91, 112, 139), radius=9)
        close = self.mid.render("X", True, self.TEXT)
        self.screen.blit(close, close.get_rect(center=self.panel_close_rect.center))

    def draw_shop(self, game):
        self.draw_panel_base("WORKSHOP", "Upgrade your gear with mined coins")
        for index, upgrade in enumerate(game.upgrades):
            rect = self.shop_item_rect(index, len(game.upgrades))
            can_buy = not upgrade.is_maxed and game.coins >= upgrade.cost
            if upgrade.is_maxed:
                background, accent = (24, 43, 43), self.ACCENT
                state = "MAX"
            elif can_buy:
                background, accent = (39, 39, 48), self.GOLD
                state = "BUY"
            else:
                background, accent = self.CARD, (76, 91, 111)
                state = ""
            self.card(rect, background, (43, 53, 70), radius=10)
            pygame.draw.rect(
                self.screen,
                accent,
                (rect.x, rect.y + 10, 3, rect.height - 20),
                border_radius=2,
            )
            self.text(
                self.font,
                "%s  Lv %d" % (upgrade.name, upgrade.level),
                self.TEXT,
                (rect.x + 14, rect.y + 4),
            )
            self.text(
                self.small,
                upgrade.description,
                self.MUTED,
                (rect.x + 14, rect.y + 25),
            )
            self.progress_bar(
                pygame.Rect(rect.x + 14, rect.bottom - 15, 96, 7),
                upgrade.level / upgrade.max_level,
                accent,
            )
            if upgrade.is_maxed:
                cost_text = state
                cost_color = self.ACCENT
            else:
                cost_text = "%s  %s" % (state, format(upgrade.cost, ","))
                cost_color = self.GOLD if can_buy else self.MUTED
            cost_surface = self.small.render(cost_text, True, cost_color)
            self.screen.blit(
                cost_surface,
                (
                    rect.right - cost_surface.get_width() - 13,
                    rect.bottom - cost_surface.get_height() - 5,
                ),
            )

    def draw_guide(self, game):
        self.draw_panel_base(
            "ORE FIELD GUIDE",
            "%d of %d ores discovered  |  Scroll to browse"
            % (sum(ore.found > 0 for ore in game.ores), len(game.ores)),
        )
        panel = self.panel_rect
        row_height = 52
        list_rect = pygame.Rect(
            panel.x + 12,
            panel.y + 78,
            panel.width - 24,
            panel.height - 92,
        )
        old_clip = self.screen.get_clip()
        self.screen.set_clip(list_rect)
        for index, ore in enumerate(game.ores):
            rect = pygame.Rect(
                list_rect.x + 4,
                list_rect.y + index * row_height - game.scroll,
                list_rect.width - 8,
                row_height - 5,
            )
            if rect.bottom < list_rect.top or rect.top > list_rect.bottom:
                continue
            locked = ore.level > game.level
            self.card(rect, self.CARD, radius=8)
            self.screen.blit(
                ore.dark_icon if locked else ore.icon,
                (rect.x + 7, rect.y + 4),
            )
            name = ore.name if not locked else "Undiscovered ore"
            self.text(self.font, name, self.TEXT if not locked else self.MUTED, (rect.x + 54, rect.y + 3))
            if locked:
                detail = "Unlock at %s tier" % LEVELS[ore.level][0]
                detail_color = self.MUTED
            else:
                detail = "%s  |  %s  |  HP %d  |  %s coins" % (
                    LEVELS[ore.level][0],
                    ore.rarity,
                    round(ore.health * (1 + ORE_HARDNESS_PER_LEVEL * ore.level)),
                    format(game.reward_for(ore), ","),
                )
                detail_color = RARITY[ore.rarity][1]
            self.text(self.small, detail, detail_color, (rect.x + 54, rect.y + 25))
            if ore.found:
                found = "MINED %s" % format(ore.found, ",")
                found_surface = self.small.render(found, True, self.ACCENT)
                self.screen.blit(
                    found_surface,
                    (rect.right - found_surface.get_width() - 10, rect.y + 5),
                )
        self.screen.set_clip(old_clip)

    def draw_dialogue(self, game):
        self.draw_panel_base("FIELD CHAT", "A quick word with your mining partner")
        panel = self.panel_rect
        sprite_rect = self.dialogue_robot.get_rect(
            midbottom=(panel.x + 104, panel.bottom - 74)
        )
        pygame.draw.ellipse(
            self.screen,
            (13, 18, 28),
            (sprite_rect.x - 15, sprite_rect.bottom - 10, sprite_rect.width + 30, 20),
        )
        self.screen.blit(self.dialogue_robot, sprite_rect)
        self.text(self.small, "SCRAPPER  /  SITE ROBOT", self.ACCENT, (panel.x + 185, panel.y + 104))
        self.text(self.title_font, "Mining partner", self.TEXT, (panel.x + 185, panel.y + 128))

        ore = game.current_ore
        lines = [
            "The site is yours, boss. Walk up to a deposit and press E or Space to mine.",
            "This %s is worth %s coins. Tougher ores take more hits, but pay better."
            % (ore.name, format(game.reward_for(ore), ",")),
            "Each swing uses 5 heat. Refill by standing next to the oil factory and pressing E.",
            "Move with A and D or the arrows. Jump with W or the JUMP button to cross the ore.",
            "Spend coins in the Workshop, then keep digging to unlock the next tier.",
            "Your progress saves automatically in this browser.",
        ]
        line = lines[game.dialogue_index % len(lines)]
        self._draw_wrapped_text(
            line,
            pygame.Rect(panel.x + 185, panel.y + 170, panel.width - 220, 120),
        )
        next_label = self.small.render("CLICK TO CONTINUE  > ", True, self.GOLD)
        self.screen.blit(
            next_label,
            (panel.right - next_label.get_width() - 25, panel.bottom - 35),
        )

    def _draw_wrapped_text(self, text, rect):
        words = text.split()
        lines = []
        current = ""
        for word in words:
            candidate = word if not current else current + " " + word
            if self.font.size(candidate)[0] > rect.width and current:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        for index, line in enumerate(lines):
            self.text(self.font, line, self.TEXT, (rect.x, rect.y + index * 25))

if __name__ == "__main__":
    asyncio.run(Game().run())
