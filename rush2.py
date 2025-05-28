# rush2.py
import pygame, sys, random, colorsys
from collections import deque
from backend import Vehicle, Board

pygame.init()

# ---- Constantes ----
SIZE        = 600
CELL        = SIZE // 6
UI_HEIGHT   = 50
ANIM_DELAY  = 500   # ms entre mouvements auto
EXIT_COL    = 5     # index de la colonne de sortie

# Couleurs
BTN_COLOR   = (100, 100, 100)
BTN_BORDER  = (255, 255, 255)
GRID_BG     = (20, 20, 40)
GRID_LINE   = (60, 60, 80)
WINDOW_BG   = (10, 10, 20)
MSG_COLOR   = (255, 255, 0)
TEXT_COLOR  = (255, 255, 255)

# Polices
FONT         = pygame.font.SysFont(None, 24)
MESSAGE_FONT = pygame.font.SysFont(None, 48)

# Fenêtre
WIN = pygame.display.set_mode((SIZE, SIZE + UI_HEIGHT))
pygame.display.set_caption("Rush Hour – Niveau 2")

# ---- Starfield ----
class Star:
    def __init__(self):
        self.x     = random.random() * SIZE
        self.y     = random.random() * SIZE
        self.speed = random.uniform(0.1, 0.5)
    def update(self):
        self.x -= self.speed
        if self.x < 0:
            self.x     = SIZE
            self.y     = random.random() * SIZE
            self.speed = random.uniform(0.1, 0.5)
    def draw(self):
        WIN.set_at((int(self.x), int(self.y)+UI_HEIGHT), (200,200,255))
stars = [Star() for _ in range(150)]

# ---- Confetti ----
class Confetto:
    def __init__(self):
        self.x     = random.random() * SIZE
        self.y     = UI_HEIGHT
        self.vx    = random.uniform(-1,1)
        self.vy    = random.uniform(1,3)
        self.color = [random.randint(50,255) for _ in range(3)]
        self.life  = random.randint(60,120)
    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.05
        self.life -= 1
    def draw(self):
        if self.life > 0:
            pygame.draw.circle(WIN, self.color, (int(self.x), int(self.y)), 3)
confetti = []

# ---- Texte multi-ligne ----
def wrap_text(text, font, max_w):
    words, lines, line = text.split(), [], ""
    for w in words:
        trial = (line + " " + w).strip()
        if font.size(trial)[0] <= max_w:
            line = trial
        else:
            lines.append(line)
            line = w
    if line: lines.append(line)
    return lines

def draw_message():
    msg = "BRAVO LA VOITURE EST SORTIE DES BOUCHONS"
    margin, max_w = 40, SIZE - 2*40
    lines = wrap_text(msg, MESSAGE_FONT, max_w)
    lh = MESSAGE_FONT.get_linesize()
    th = lh * len(lines)
    y0 = UI_HEIGHT + (SIZE - th)//2
    for i, ln in enumerate(lines):
        surf = MESSAGE_FONT.render(ln, True, MSG_COLOR)
        rect = surf.get_rect(center=(SIZE//2, y0 + i*lh + lh//2))
        WIN.blit(surf, rect)

def draw_no_solution():
    surf = MESSAGE_FONT.render("Aucune solution possible", True, MSG_COLOR)
    rect = surf.get_rect(center=(SIZE//2, UI_HEIGHT + SIZE//2))
    WIN.blit(surf, rect)

def hue_color(period_ms):
    t = (pygame.time.get_ticks() % period_ms) / period_ms
    r, g, b = colorsys.hsv_to_rgb(t, 1, 1)
    return int(r*255), int(g*255), int(b*255)

# ---- Dessin des véhicules ----
def draw_vehicle(v, override_color=None):
    color = override_color or v.color
    if v.orientation == 'H':
        w, h = CELL * v.length, CELL
    else:
        w, h = CELL, CELL * v.length

    px, py = v.x*CELL, UI_HEIGHT + v.y*CELL
    body = pygame.Rect(px, py, w, h)
    pygame.draw.rect(WIN, color, body, border_radius=8)
    pygame.draw.rect(WIN, (30,30,30), body, 2, border_radius=8)

    glass = tuple(min(255, c+60) for c in color)
    if v.orientation == 'H':
        gh = h // 3
        gy = py + (h-gh)//2
        for gx in (px + 0.1*w, px + 0.55*w):
            r = pygame.Rect(gx, gy, 0.35*w, gh)
            pygame.draw.rect(WIN, glass, r, border_radius=4)
    else:
        gw = w // 3
        gx = px + (w-gw)//2
        for gy in (py + 0.1*h, py + 0.55*h):
            r = pygame.Rect(gx, gy, gw, 0.35*h)
            pygame.draw.rect(WIN, glass, r, border_radius=4)

    wr = CELL//6; wc = (20,20,20)
    if v.orientation == 'H':
        offs = [
            (px+2*wr, py+h-wr), (px+w-2*wr, py+h-wr),
            (px+2*wr, py+wr),   (px+w-2*wr, py+wr),
        ]
    else:
        offs = [
            (px+wr,     py+2*wr), (px+wr,     py+h-2*wr),
            (px+w-wr,   py+2*wr), (px+w-wr,   py+h-2*wr),
        ]
    for cx, cy in offs:
        pygame.draw.circle(WIN, wc, (int(cx), int(cy)), wr)

trails = {}

def draw_board(board, selected, show_victory):
    # on ne touche pas à la barre UI : on ne remplit que sous UI_HEIGHT
    WIN.fill(GRID_BG, (0, UI_HEIGHT, SIZE, SIZE))
    for s in stars:
        s.draw(); s.update()
    # quadrillage
    for i in range(7):
        x, y = i*CELL, UI_HEIGHT + i*CELL
        pygame.draw.line(WIN, GRID_LINE, (x,UI_HEIGHT),(x,UI_HEIGHT+SIZE))
        pygame.draw.line(WIN, GRID_LINE, (0,y),(SIZE,y))

    for v in board.vehicles:
        # traînées
        for t in trails.get(v.id, []):
            surf = pygame.Surface((t['rect'].w, t['rect'].h), pygame.SRCALPHA)
            surf.fill((*t['col'], t['alpha']))
            WIN.blit(surf, (t['rect'].x, t['rect'].y))
            t['alpha'] -= 5
        trails[v.id] = [t for t in trails.get(v.id, []) if t['alpha']>0]

        override = hue_color(2000) if (show_victory and v.id == "R") else None
        draw_vehicle(v, override)

    if selected:
        col = hue_color(5000)
        w = CELL*selected.length if selected.orientation=='H' else CELL
        h = CELL if selected.orientation=='H' else CELL*selected.length
        r = pygame.Rect(selected.x*CELL, UI_HEIGHT+selected.y*CELL, w, h)
        pygame.draw.rect(WIN, col, r, 4, border_radius=8)

# ---- Cahier de charge Niveau 2 ----
def config1(board):
    board.vehicles.clear()
    board.add_vehicle(Vehicle("R",1,2,2,'H',(255,0,0)))
    board.add_vehicle(Vehicle("A",0,0,2,'V',(0,0,255)))
    board.add_vehicle(Vehicle("B",3,0,3,'H',(0,255,0)))

def config2(board):
    board.vehicles.clear()
    board.add_vehicle(Vehicle("R",2,3,2,'H',(255,0,0)))
    board.add_vehicle(Vehicle("C",0,1,3,'H',(0,128,255)))
    board.add_vehicle(Vehicle("D",5,0,3,'V',(255,128,0)))
    board.add_vehicle(Vehicle("E",4,4,2,'V',(128,0,255)))

def config3(board):
    board.vehicles.clear()
    board.add_vehicle(Vehicle("R",0,2,2,'H',(255,0,0)))
    board.add_vehicle(Vehicle("F",2,0,2,'V',(0,200,100)))
    board.add_vehicle(Vehicle("G",3,3,3,'H',(200,200,0)))
    board.add_vehicle(Vehicle("H",5,2,2,'V',(0,200,200)))

def _generate_once(board):
    board.vehicles.clear()
    while True:
        x = random.randint(0,4)
        v = Vehicle("R",x,2,2,'H',(255,0,0))
        if board.can_move(v,x,2):
            board.add_vehicle(v); break
    def place(id_,L,ori):
        for _ in range(100):
            xx = random.randint(0,5-(L if ori=='H' else 1))
            yy = random.randint(0,5-(1 if ori=='H' else L))
            c = (random.randint(50,255),random.randint(50,255),random.randint(50,255))
            v = Vehicle(id_,xx,yy,L,ori,c)
            if board.can_move(v,xx,yy):
                board.add_vehicle(v); return True
        return False
    for i in range(4): place(f"C{i}",2, random.choice(['H','V']))
    for i in range(3): place(f"T{i}",3, random.choice(['H','V']))

def random_board(board):
    while True:
        _generate_once(board)
        if solve(board.vehicles):
            return

def solve(vehicles):
    proto = [(v.id,v.length,v.orientation,v.color) for v in vehicles]
    start = tuple((v.x,v.y) for v in vehicles)
    parent, move_from = {start:None}, {}
    q = deque([start])
    def is_win(s):
        x,_ = s[0]
        return x + proto[0][1] -1 == EXIT_COL
    def make_board(s):
        b = Board()
        for (id_,L,ori,col),(x,y) in zip(proto,s):
            b.add_vehicle(Vehicle(id_,x,y,L,ori,col))
        return b

    goal = None
    while q:
        s = q.popleft()
        if is_win(s): goal = s; break
        b = make_board(s)
        for i,(x,y) in enumerate(s):
            id_,L,ori,col = proto[i]
            for d in (-1,1):
                nx,ny = (x+d,y) if ori=='H' else (x,y+d)
                v = Vehicle(id_,x,y,L,ori,col)
                b.vehicles[i] = v
                if b.can_move(v,nx,ny):
                    t = list(s); t[i] = (nx,ny); t = tuple(t)
                    if t not in parent:
                        parent[t], move_from[t] = s, (i,d)
                        q.append(t)

    if not goal: return []
    path, cur = [], goal
    while parent[cur] is not None:
        path.append(move_from[cur])
        cur = parent[cur]
    return list(reversed(path))

# ---- UI et interactions ----
BUTTONS_INFO = [
    ("Carte 1", config1),
    ("Carte 2", config2),
    ("Carte 3", config3),
    ("Aléatoire", random_board),
    ("Solution", None),
]
BUTTON_W = SIZE // len(BUTTONS_INFO)
BUTTONS  = [(pygame.Rect(i*BUTTON_W, 0, BUTTON_W, UI_HEIGHT), lbl, fn)
             for i,(lbl,fn) in enumerate(BUTTONS_INFO)]

def draw_ui(min_moves, played_moves):
    mx,my = pygame.mouse.get_pos()
    for rect,lbl,fn in BUTTONS:
        bg = tuple(min(255,c+50) for c in BTN_COLOR) if rect.collidepoint(mx,my) else BTN_COLOR
        pygame.draw.rect(WIN,bg,rect,border_radius=8)
        pygame.draw.rect(WIN,BTN_BORDER,rect,2,border_radius=8)
        txt = FONT.render(lbl, True, BTN_BORDER)
        WIN.blit(txt, txt.get_rect(center=rect.center))

    # ** Stats DESSOUS la barre UI **
    y0 = UI_HEIGHT + 5
    WIN.blit(FONT.render(f"Min : {min_moves}", True, TEXT_COLOR), (10, y0))
    wm = FONT.render(f"Joués : {played_moves}", True, TEXT_COLOR)
    WIN.blit(wm, (SIZE - wm.get_width() - 10, y0))

def main():
    clock        = pygame.time.Clock()
    board        = Board()
    config1(board)

    selected       = None
    solution       = []
    animating      = False
    show_victory   = False
    show_no_sol    = False
    anim_timer     = 0
    min_moves      = 0
    played_moves   = 0

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx,my = ev.pos
                if my < UI_HEIGHT:
                    selected = None
                    animating = False
                    show_victory = show_no_sol = False
                    confetti.clear()
                    played_moves = 0
                    for rect,lbl,fn in BUTTONS:
                        if rect.collidepoint(mx,my):
                            if fn:
                                fn(board)
                                if lbl == "Aléatoire":
                                    solution = solve(board.vehicles)
                                    min_moves = len(solution)
                            else:
                                solution = solve(board.vehicles)
                                min_moves = len(solution)
                                if solution:
                                    animating  = True
                                    anim_timer = pygame.time.get_ticks()
                                else:
                                    show_no_sol = True
                            break
                    continue

                gx,gy = mx//CELL, (my-UI_HEIGHT)//CELL
                selected = None
                for v in board.vehicles:
                    if (gx,gy) in v.cells_occupied():
                        selected = v
                        break

            elif ev.type == pygame.KEYDOWN and selected:
                d=0
                if ev.key==pygame.K_LEFT  and selected.orientation=='H': d=-1
                if ev.key==pygame.K_RIGHT and selected.orientation=='H': d=1
                if ev.key==pygame.K_UP    and selected.orientation=='V': d=-1
                if ev.key==pygame.K_DOWN  and selected.orientation=='V': d=1
                if d:
                    w = CELL*selected.length if selected.orientation=='H' else CELL
                    h = CELL if selected.orientation=='H' else CELL*selected.length
                    r = pygame.Rect(selected.x*CELL, UI_HEIGHT+selected.y*CELL, w, h)
                    trails.setdefault(selected.id,[]).append({'rect':r.copy(),'col':(200,200,50),'alpha':150})
                    selected.move(d, board)
                    played_moves += 1

        red = board.vehicles[0]
        if not animating and not show_victory and not show_no_sol:
            if red.orientation=='H' and red.x + red.length -1 == EXIT_COL:
                show_victory = True
                confetti.extend(Confetto() for _ in range(100))

        if animating and solution:
            now = pygame.time.get_ticks()
            if now - anim_timer >= ANIM_DELAY:
                i,d = solution.pop(0)
                v = board.vehicles[i]
                w = CELL*v.length if v.orientation=='H' else CELL
                h = CELL if v.orientation=='H' else CELL*v.length
                r = pygame.Rect(v.x*CELL, UI_HEIGHT+v.y*CELL, w, h)
                trails.setdefault(v.id,[]).append({'rect':r.copy(),'col':(200,200,50),'alpha':150})
                board.vehicles[i].move(d, board)
                selected = None
                anim_timer = now
        elif animating:
            animating = False
            show_victory = True
            confetti.extend(Confetto() for _ in range(100))

        for c in list(confetti):
            c.update(); c.draw()
            if c.life <= 0:
                confetti.remove(c)

        WIN.fill(WINDOW_BG)
        # 1) DESSINER D'ABORD LE PLATEAU
        draw_board(board, selected, show_victory)
        # 2) PUIS LES BOUTONS + COMPTEURS
        draw_ui(min_moves, played_moves)
        if show_victory: draw_message()
        if show_no_sol:  draw_no_solution()
        pygame.display.flip()
        clock.tick(60)

if __name__=="__main__":
    main()
