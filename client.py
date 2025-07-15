from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from math import sin

app = Ursina()

# === Constants ===
CHUNK_SIZE = 8
RENDER_DISTANCE = 2

# === Assets ===
block_texture = load_texture('assets/block_1.png')

# === State ===
blocks = {}
chunks_loaded = set()
player = None
player_enabled = False
paused = False

# === Main Menu UI ===
menu_bg = Entity(model='quad', scale=20, texture='white_cube', color=color.azure)
play_btn = Button(
    text='Play',
    scale=(0.2, 0.1),
    y=0,
    color=color.rgba(255,255,255,220),
    text_color=color.black,
    highlight_color=color.lime,
    pressed_color=color.green
)

# === Pause Menu UI ===
pause_bg = Entity(model='quad', scale=20, texture='white_cube',
                  color=color.rgba(0,0,0,150), enabled=False)
resume_btn = Button(text='Resume', scale=(0.2,0.1), y=0.1, enabled=False)
quit_btn   = Button(text='Quit',   scale=(0.2,0.1), y=-0.1, enabled=False)

# === Chunk Generation ===
def generate_chunk(cx, cz):
    for x in range(CHUNK_SIZE):
        for z in range(CHUNK_SIZE):
            wx = cx * CHUNK_SIZE + x
            wz = cz * CHUNK_SIZE + z
            pos = (wx, 0, wz)
            if pos not in blocks:
                b = Entity(
                    model='cube',
                    position=pos,
                    texture=block_texture,
                    collider='box'
                )
                blocks[pos] = b

def update_chunks():
    if not player_enabled or paused: 
        return
    px, _, pz = player.position
    cx = int(px // CHUNK_SIZE)
    cz = int(pz // CHUNK_SIZE)
    for x in range(cx - RENDER_DISTANCE, cx + RENDER_DISTANCE + 1):
        for z in range(cz - RENDER_DISTANCE, cz + RENDER_DISTANCE + 1):
            if (x, z) not in chunks_loaded:
                generate_chunk(x, z)
                chunks_loaded.add((x, z))

# === Input Handling ===
def input(key):
    global paused
    if key == 'escape' and player_enabled:
        paused = not paused
        toggle_pause(paused)
    if not player_enabled or paused:
        return

    hit = raycast(camera.world_position, camera.forward, distance=5, ignore=[player], traverse_target=scene)

    if hit.hit:
        block_pos = hit.entity.position

        if key == 'left mouse down':
            destroy(hit.entity)
            blocks.pop(tuple(block_pos), None)

        elif key == 'right mouse down':
            place_pos = block_pos + hit.normal
            place_pos = Vec3(round(place_pos.x), round(place_pos.y), round(place_pos.z))

            if tuple(place_pos) not in blocks:
                b = Entity(model='cube', position=place_pos, texture=block_texture, collider='box')
                blocks[tuple(place_pos)] = b

# === Pause Handling ===
def toggle_pause(state):
    pause_bg.enabled = state
    resume_btn.enabled = state
    quit_btn.enabled = state
    if state:
        mouse.locked = False
        player.disable()
    else:
        mouse.locked = True
        player.enable()

# === Player Spawn ===
def spawn_player_after_chunks(x, y, z):
    global player, player_enabled
    player = FirstPersonController()
    player.gravity = 0  # gravity off initially
    player.position = (x, y+2, z)
    player_enabled = True
    mouse.locked = True
    invoke(enable_gravity_for_player, delay=0.2)

def enable_gravity_for_player():
    if player:
        player.gravity = 1

# === Start Game ===
def start_game():
    global player_enabled
    menu_bg.enabled = False
    play_btn.enabled = False

    # Generate all chunks
    for cx in range(-RENDER_DISTANCE, RENDER_DISTANCE+1):
        for cz in range(-RENDER_DISTANCE, RENDER_DISTANCE+1):
            generate_chunk(cx, cz)
            chunks_loaded.add((cx, cz))

    # Solid spawn block
    spawn_x = CHUNK_SIZE * RENDER_DISTANCE // 2
    spawn_z = CHUNK_SIZE * RENDER_DISTANCE // 2
    spawn_y = 0
    spawn_pos = (spawn_x, spawn_y, spawn_z)
    if spawn_pos not in blocks:
        b = Entity(model='cube', position=spawn_pos, texture=block_texture, collider='box')
        blocks[spawn_pos] = b

    # Spawn player after a short delay
    invoke(spawn_player_after_chunks, spawn_x, spawn_y, spawn_z, delay=0.3)

# === Main Update Loop ===
def update():
    if player_enabled and not paused:
        update_chunks()

    # Day-night cycle
    cycle_speed = 0.2
    intensity = sin(time.time() * cycle_speed) * 0.5 + 0.5
    window.color = color.rgb(150*intensity+50, 150*intensity+50, 255*intensity)

# === Button Actions ===
play_btn.on_click   = start_game
resume_btn.on_click = lambda: toggle_pause(False)
quit_btn.on_click   = application.quit

app.run()
