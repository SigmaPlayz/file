# TurboCraft Unified Script - Menu + Game
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import pickle, socket, threading, os, random, types, importlib

# --- Patch for Python 3.12 importlib issue ---
if not hasattr(importlib, 'util'):
    importlib.util = types.SimpleNamespace(find_spec=lambda name: None)

# --- Safe Texture Loader ---
def safe_load_texture(path):
    try:
        return load_texture(path)
    except Exception as e:
        print(f"Texture load error: {path} => {e}")
        return load_texture('white_cube')  # fallback

textures = []  # Will be loaded after Ursina starts

world_data = {}
inventory = [10]*32
current_block = 1
gamemode = 'creative'
player_name = 'Turbo'
server_address = ('localhost', 65432)

# ---------------- Game Code ---------------- #
def start_game():
    app = Ursina()
    window.borderless = False
    window.title = "TurboCraft 1.0"

    global textures
    textures = [safe_load_texture(f'assets/block_{i}.png') for i in range(1, 33)]

    class Voxel(Button):
        def __init__(self, position=(0,0,0), texture_id=1):
            super().__init__(
                parent=scene,
                position=position,
                model='cube',
                origin_y=0.5,
                texture=textures[texture_id-1],
                color=color.white,
                scale=0.5
            )
            self.texture_id = texture_id
            world_data[str(position)] = texture_id

        def input(self, key):
            if self.hovered:
                if key == 'left mouse down' and gamemode == 'creative':
                    destroy(self)
                    del world_data[str(self.position)]
                if key == 'right mouse down':
                    pos = self.position + mouse.normal
                    if gamemode == 'creative' or inventory[current_block-1] > 0:
                        Voxel(position=pos, texture_id=current_block)
                        if gamemode == 'survival':
                            inventory[current_block-1] -= 1

    hotbar = [Button(texture=textures[i], parent=camera.ui, scale=0.08, x=(i-16)*0.05, y=-0.45) for i in range(32)]
    player = FirstPersonController()
    ground = Entity(model='plane', texture='white_cube', scale=64, collider='box')

    def save_world():
        with open('save.tcworld', 'wb') as f:
            pickle.dump(world_data, f)

    def load_world():
        if os.path.exists('save.tcworld'):
            with open('save.tcworld', 'rb') as f:
                loaded = pickle.load(f)
                for pos, tex_id in loaded.items():
                    pos = eval(pos)
                    Voxel(position=pos, texture_id=tex_id)

    def save_inventory():
        with open('player.tcsave', 'wb') as f:
            pickle.dump(inventory, f)

    def load_inventory():
        global inventory
        if os.path.exists('player.tcsave'):
            with open('player.tcsave', 'rb') as f:
                inventory = pickle.load(f)

    def connect():
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(server_address)
            threading.Thread(target=listen_server, args=(client,), daemon=True).start()
            client.send(f"{player_name} joined the game".encode())
        except:
            print("Connection failed")

    def listen_server(client):
        while True:
            try:
                msg = client.recv(1024).decode()
                print(f"[Server] {msg}")
            except:
                break

    def input(key):
        global current_block, gamemode
        if key.isdigit():
            num = int(key)
            if 1 <= num <= 9:
                current_block = num
        if key == 'g':
            gamemode = 'creative' if gamemode == 'survival' else 'survival'
            print(f"Gamemode: {gamemode}")
        if key == 'k': save_world()
        if key == 'l': load_world()
        if key == 'i': save_inventory()
        if key == 'o': load_inventory()
        if key == 'j': connect()

    load_world()
    load_inventory()
    app.run()

# ---------------- Main Menu Code ---------------- #
app = Ursina()
window.title = 'TurboCraft Launcher'
window.borderless = False
window.fullscreen = False

bg = Entity(model='quad', texture='assets/bg.jpg', scale=(16, 9), z=1)

splash_texts = [
    "Now with multiplayer!",
    "Turbo powered!",
    "Build your dream world!",
    "100% Ursina!",
    "Eat. Code. Build.",
]
splash = Text(
    text=random.choice(splash_texts),
    position=(0.6, 0.4),
    origin=(0, 0),
    scale=1.5,
    color=color.yellow
)

title = Text("TurboCraft", scale=3, position=(-0.4, 0.4), color=color.azure)

def start_singleplayer():
    destroy_all()
    start_game()

def start_multiplayer():
    print("Multiplayer coming soon!")

def quit_game():
    application.quit()

btns = [
    Button(text='Singleplayer', scale=(0.3, 0.08), y=0.1, on_click=start_singleplayer),
    Button(text='Multiplayer', scale=(0.3, 0.08), y=0, on_click=start_multiplayer),
    Button(text='Options', scale=(0.3, 0.08), y=-0.1),
    Button(text='Quit', scale=(0.3, 0.08), y=-0.2, on_click=quit_game),
]
for b in btns:
    b.x = 0

app.run()
