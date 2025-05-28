# rush1.py
import pygame, sys, random, colorsys
from collections import deque
from backend import Vehicle, Board

pygame.init()

# ---- Constantes ----
SIZE       = 600
CELL       = SIZE // 6
UI_HEIGHT  = 50
ANIM_DELAY = 500       # ms entre mouvements auto
EXIT_COL   = 5         # colonne de sortie = index 5

# Couleurs
BTN_COLOR   = (100, 100, 100)
BTN_BORDER  = (255, 255, 255)
GRID_BG     = (20, 20, 40)
GRID_LINE   = (60, 60, 80)
WINDOW_BG   = (10, 10, 20)
MSG_COLOR   = (255, 255, 0)

# Polices
FONT         = pygame.font.SysFont(None, 24)
MESSAGE_FONT = pygame.font.SysFont(None, 48)

# Fenêtre
WIN = pygame.display.set_mode((SIZE, SIZE + UI_HEIGHT))
pygame.display.set_caption("Rush Hour – Niveau 1 Lunatique")

# ---- Configurations prédéfinies ----
def config1(board):
    board.vehicles.clear()
    board.add_vehicle(Vehicle("R", 1,2,2,'H',(255,0,0)))
    board.add_vehicle(Vehicle("A", 0,0,2,'V',(0,0,255)))
    board.add_vehicle(Vehicle("B", 3,0,3,'H',(0,255,0)))

def config2(board):
    board.vehicles.clear()
    board.add_vehicle(Vehicle("R", 2,3,2,'H',(255,0,0)))
    board.add_vehicle(Vehicle("C", 0,1,3,'H',(0,128,255)))
    board.add_vehicle(Vehicle("D", 5,0,3,'V',(255,128,0)))
    board.add_vehicle(Vehicle("E", 4,4,2,'V',(128,0,255)))

def config3(board):
    board.vehicles.clear()
    board.add_vehicle(Vehicle("R", 0,2,2,'H',(255,0,0)))
    board.add_vehicle(Vehicle("F", 2,0,2,'V',(0,200,100)))
    board.add_vehicle(Vehicle("G", 3,3,3,'H',(200,200,0)))
    board.add_vehicle(Vehicle("H", 5,2,2,'V',(0,200,200)))

# ---- Aléatoire ----
def random_board(board, num_cars=4, num_trucks=3):
    board.vehicles.clear()
    # voiture rouge
    while True:
        x = random.randint(0, 4)
        v = Vehicle("R", x, 2, 2, 'H', (255,0,0))
        if board.can_move(v, x, 2):
            board.add_vehicle(v)
            break
    # autres véhicules
    def place(vid, length, ori):
        for _ in range(100):
            x = random.randint(0, 5 - (length if ori=='H' else 1))
            y = random.randint(0, 5 - (1 if ori=='H' else length))
            color = (random.randint(50,255), random.randint(50,255), random.randint(50,255))
            v = Vehicle(vid, x, y, length, ori, color)
            if board.can_move(v, x, y):
                board.add_vehicle(v)
                return True
        return False
    for i in range(num_cars):   place(f"C{i}", 2, random.choice(['H','V']))
    for i in range(num_trucks): place(f"T{i}", 3, random.choice(['H','V']))

# ---- Solveur BFS ----
def solve(vehicles, width=6, height=6):
    proto = [(v.id, v.length, v.orientation, v.color) for v in vehicles]
    start = tuple((v.x, v.y) for v in vehicles)
    parent = {start: None}
    move_from = {}
    q = deque([start])
    def is_win(state):
        x, _ = state[0]
        return x + proto[0][1] - 1 == EXIT_COL
    def make_board(state):
        b = Board(width, height)
        for (vid, length, ori, col), (x, y) in zip(proto, state):
            b.add_vehicle(Vehicle(vid, x, y, length, ori, col))
        return b
    goal = None
    while q:
        st = q.popleft()
        if is_win(st):
            goal = st; break
        b = make_board(st)
        for i, (x, y) in enumerate(st):
            vid, length, ori, col = proto[i]
            for d in (-1, 1):
                nx, ny = (x+d, y) if ori=='H' else (x, y+d)
                v = Vehicle(vid, x, y, length, ori, col)
                b.vehicles[i] = v
                if b.can_move(v, nx, ny):
                    ns = list(st)
                    ns[i] = (nx, ny)
                    ns = tuple(ns)
                    if ns not in parent:
                        parent[ns] = st
                        move_from[ns] = (i, d)
                        q.append(ns)
    if goal is None:
        return []
    path = []
    s = goal
    while parent[s] is not None:
        path.append(move_from[s])
        s = parent[s]
    return list(reversed(path))

# ---- UI Setup ----
LABELS_FUNCS = [
    ("Carte 1",    config1),
    ("Carte 2",    config2),
    ("Carte 3",    config3),
    ("Aléatoire",  random_board),
    ("Solution",   None),
]
BUTTON_WIDTH = SIZE // len(LABELS_FUNCS)
BUTTONS = [
    (pygame.Rect(i*BUTTON_WIDTH, 0, BUTTON_WIDTH, UI_HEIGHT), lbl, fn)
    for i, (lbl, fn) in enumerate(LABELS_FUNCS)
]

def draw_ui():
    mx, _ = pygame.mouse.get_pos()
    for rect, label, _ in BUTTONS:
        col = BTN_COLOR if not rect.collidepoint(mx, 0) else tuple(min(255,c+50) for c in BTN_COLOR)
        pygame.draw.rect(WIN, col, rect, border_radius=8)
        pygame.draw.rect(WIN, BTN_BORDER, rect, 2, border_radius=8)
        txt = FONT.render(label, True, BTN_BORDER)
        WIN.blit(txt, txt.get_rect(center=rect.center))

# ---- Starfield ----
class Star:
    def __init__(self):
        self.x = random.random() * SIZE
        self.y = random.random() * SIZE
        self.speed = random.uniform(0.1, 0.5)
    def update(self):
        self.x -= self.speed
        if self.x < 0:
            self.x = SIZE
            self.y = random.random() * SIZE
            self.speed = random.uniform(0.1, 0.5)
    def draw(self):
        WIN.set_at((int(self.x), int(self.y)+UI_HEIGHT), (200,200,255))
stars = [Star() for _ in range(150)]

# ---- Confetti ----
class Confetto:
    def __init__(self):
        self.x = random.random() * SIZE
        self.y = UI_HEIGHT
        self.vx = random.uniform(-1,1)
        self.vy = random.uniform(1,3)
        self.color = [random.randint(50,255) for _ in range(3)]
        self.life = random.randint(60,120)
    def update(self):
        self.x += self.vx; self.y += self.vy; self.vy += 0.05; self.life -= 1
    def draw(self):
        if self.life>0:
            pygame.draw.circle(WIN, self.color, (int(self.x), int(self.y)), 3)
confetti = []

# ---- Helpers ----
def wrap_text(text, font, max_w):
    words = text.split(); lines = []; line = ""
    for w in words:
        test = (line+" "+w).strip()
        if font.size(test)[0] <= max_w:
            line = test
        else:
            lines.append(line)
            line = w
    if line: lines.append(line)
    return lines

def draw_message():
    msg = "BRAVO LA VOITURE EST SORTIE DES BOUCHONS "
    margin = 40; max_w = SIZE - 2*margin
    lines = wrap_text(msg, MESSAGE_FONT, max_w)
    lh = MESSAGE_FONT.get_linesize(); th = lh * len(lines)
    y0 = UI_HEIGHT + (SIZE-th)//2
    for i, ln in enumerate(lines):
        surf = MESSAGE_FONT.render(ln, True, MSG_COLOR)
        rect = surf.get_rect(center=(SIZE//2, y0 + i*lh + lh//2))
        WIN.blit(surf, rect)

def draw_no_solution():
    surf = MESSAGE_FONT.render("Aucune solution possible", True, MSG_COLOR)
    rect = surf.get_rect(center=(SIZE//2, UI_HEIGHT+SIZE//2))
    WIN.blit(surf, rect)

def hue_border_color():
    t = (pygame.time.get_ticks() % 5000) / 5000
    r,g,b = colorsys.hsv_to_rgb(t,1,1)
    return int(r*255), int(g*255), int(b*255)

def get_rainbow_color():
    t = (pygame.time.get_ticks() % 2000) / 2000
    r,g,b = colorsys.hsv_to_rgb(t,1,1)
    return int(r*255), int(g*255), int(b*255)

# ---- Drawing vehicles ----
def draw_vehicle(v, override_color=None):
    color = override_color if override_color else v.color
    w = CELL*v.length if v.orientation=='H' else CELL
    h = CELL if v.orientation=='H' else CELL*v.length
    px, py = v.x*CELL, UI_HEIGHT + v.y*CELL
    body = pygame.Rect(px, py, w, h)
    # carrosserie
    pygame.draw.rect(WIN, color, body, border_radius=8)
    pygame.draw.rect(WIN, (30,30,30), body, 2, border_radius=8)
    # vitres
    glass = tuple(min(255,c+60) for c in color)
    if v.orientation=='H':
        gh = h//3; gy = py + (h-gh)//2
        for gx in (px + w*0.1, px + w*0.55):
            r = pygame.Rect(gx, gy, w*0.35, gh)
            pygame.draw.rect(WIN, glass, r, border_radius=4)
    else:
        gw = w//3; gx = px + (w-gw)//2
        for gy in (py + h*0.1, py + h*0.55):
            r = pygame.Rect(gx, gy, gw, h*0.35)
            pygame.draw.rect(WIN, glass, r, border_radius=4)
    # roues
    wr = CELL//6; wc = (20,20,20)
    offs = []
    if v.orientation=='H':
        offs = [
            (px+wr*2, py+h-wr),
            (px+w-wr*2, py+h-wr),
            (px+wr*2, py+wr),
            (px+w-wr*2, py+wr),
        ]
    else:
        offs = [
            (px+wr, py+wr*2),
            (px+wr, py+h-wr*2),
            (px+w-wr, py+wr*2),
            (px+w-wr, py+h-wr*2),
        ]
    for cx, cy in offs:
        pygame.draw.circle(WIN, wc, (int(cx), int(cy)), wr)

trails = {}

def draw_board(board, selected, show_victory):
    # fond grille
    WIN.fill(GRID_BG, (0, UI_HEIGHT, SIZE, SIZE))
    # étoiles
    for s in stars:
        s.draw(); s.update()
    # grille
    for i in range(7):
        x = i*CELL; y = UI_HEIGHT + i*CELL
        pygame.draw.line(WIN, GRID_LINE, (x, UI_HEIGHT), (x, UI_HEIGHT+SIZE))
        pygame.draw.line(WIN, GRID_LINE, (0, y), (SIZE, y))
    # véhicules + trails
    for v in board.vehicles:
        # dessine trails
        for t in trails.get(v.id, []):
            surf = pygame.Surface((t['rect'].w, t['rect'].h), pygame.SRCALPHA)
            surf.fill((*t['col'], t['alpha']))
            WIN.blit(surf, (t['rect'].x, t['rect'].y))
            t['alpha'] -= 5
        trails[v.id] = [t for t in trails.get(v.id, []) if t['alpha']>0]
        # override red car color if victory
        override = get_rainbow_color() if (show_victory and v.id=="R") else None
        draw_vehicle(v, override)
    # surbrillance cyclique
    if selected:
        col = hue_border_color()
        w = CELL*selected.length if selected.orientation=='H' else CELL
        h = CELL if selected.orientation=='H' else CELL*selected.length
        rect = pygame.Rect(selected.x*CELL, UI_HEIGHT+selected.y*CELL, w, h)
        pygame.draw.rect(WIN, col, rect, 4, border_radius=8)

# créations
stars = [Star() for _ in range(120)]

# ---- Boucle principale ----
def main():
    clock = pygame.time.Clock()
    board = Board(); config1(board)
    selected       = None
    solution_moves = []
    animating      = False
    show_victory   = False
    show_no_sol    = False
    anim_timer     = 0

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                mx, my = ev.pos
                # UI ?
                if my < UI_HEIGHT:
                    selected = None
                    animating = False
                    show_victory = False
                    show_no_sol = False
                    confetti.clear()
                    for rect, _, fn in BUTTONS:
                        if rect.collidepoint(mx, my):
                            if fn:
                                fn(board)
                            else:
                                solution_moves = solve(board.vehicles)
                                if solution_moves:
                                    animating = True
                                    anim_timer = pygame.time.get_ticks()
                                else:
                                    show_no_sol = True
                            break
                    continue
                # sélection
                gx,gy = mx//CELL,(my-UI_HEIGHT)//CELL
                selected = None
                for v in board.vehicles:
                    if (gx,gy) in v.cells_occupied():
                        selected = v; break
            elif ev.type==pygame.KEYDOWN and selected:
                d = 0
                if ev.key==pygame.K_LEFT  and selected.orientation=='H': d=-1
                if ev.key==pygame.K_RIGHT and selected.orientation=='H': d=1
                if ev.key==pygame.K_UP    and selected.orientation=='V': d=-1
                if ev.key==pygame.K_DOWN  and selected.orientation=='V': d=1
                if d:
                    # ajouter trail
                    w = CELL*selected.length if selected.orientation=='H' else CELL
                    h = CELL if selected.orientation=='H' else CELL*selected.length
                    r = pygame.Rect(selected.x*CELL, UI_HEIGHT+selected.y*CELL, w, h)
                    trails.setdefault(selected.id, []).append({
                        'rect': r.copy(), 'col': (200,200,50), 'alpha': 150
                    })
                    selected.move(d, board)

        # victoire manuelle
        if not animating and not show_victory and not show_no_sol:
            red = board.vehicles[0]
            if red.orientation=='H' and red.x + red.length - 1 == EXIT_COL:
                show_victory = True
                confetti.extend(Confetto() for _ in range(100))

        # animation auto
        if animating and solution_moves:
            now = pygame.time.get_ticks()
            if now - anim_timer >= ANIM_DELAY:
                i, d = solution_moves.pop(0)
                v = board.vehicles[i]
                w = CELL*v.length if v.orientation=='H' else CELL
                h = CELL if v.orientation=='H' else CELL*v.length
                r = pygame.Rect(v.x*CELL, UI_HEIGHT+v.y*CELL, w, h)
                trails.setdefault(v.id, []).append({
                    'rect': r.copy(), 'col': (200,200,50), 'alpha': 150
                })
                board.vehicles[i].move(d, board)
                selected = None
                anim_timer = now
        elif animating:
            animating    = False
            show_victory = True
            confetti.extend(Confetto() for _ in range(100))

        # confettis
        for c in list(confetti):
            c.update(); c.draw()
            if c.life <= 0:
                confetti.remove(c)

        # rendu
        WIN.fill(WINDOW_BG)
        draw_ui()
        draw_board(board, selected, show_victory)
        if show_victory:
            draw_message()
        if show_no_sol:
            draw_no_solution()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
