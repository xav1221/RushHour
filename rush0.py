# rush0.py
import pygame, sys
from collections import deque
from backend import Vehicle, Board

pygame.init()

# Constantes
SIZE      = 600       # taille de la grille
CELL      = SIZE // 6 # taille d'une case
UI_HEIGHT = 50        # hauteur de la barre de boutons
ANIM_DELAY = 500      # ms entre chaque mouvement de l'animation

# Fenêtre 600×650 (50 px pour la UI en haut)
WIN = pygame.display.set_mode((SIZE, SIZE + UI_HEIGHT))
pygame.display.set_caption("Rush Hour – Niveau 0")

# Configurations prédéfinies
def config1(board):
    board.vehicles.clear()
    board.add_vehicle(Vehicle("R", 1, 2, 2, 'H', (255, 0, 0)))
    board.add_vehicle(Vehicle("A", 0, 0, 2, 'V', (0, 0, 255)))
    board.add_vehicle(Vehicle("B", 3, 0, 3, 'H', (0, 255, 0)))

def config2(board):
    board.vehicles.clear()
    board.add_vehicle(Vehicle("R", 2, 3, 2, 'H', (255, 0, 0)))
    board.add_vehicle(Vehicle("C", 0, 1, 3, 'H', (0, 128, 255)))
    board.add_vehicle(Vehicle("D", 5, 0, 3, 'V', (255, 128, 0)))
    board.add_vehicle(Vehicle("E", 4, 4, 2, 'V', (128, 0, 255)))

def config3(board):
    board.vehicles.clear()
    board.add_vehicle(Vehicle("R", 0, 2, 2, 'H', (255, 0, 0)))
    board.add_vehicle(Vehicle("F", 2, 0, 2, 'V', (0, 200, 100)))
    board.add_vehicle(Vehicle("G", 3, 3, 3, 'H', (200, 200, 0)))
    board.add_vehicle(Vehicle("H", 5, 2, 2, 'V', (0, 200, 200)))

# Solveur BFS minimal
def solve(vehicles, width=6, height=6):
    """
    Retourne la liste des mouvements (i, delta) qui fait sortir la voiture rouge.
    i = index du véhicule dans vehicles, delta = -1 ou +1.
    """
    # Proto-descriptions (id, length, ori, color)
    proto = [(v.id, v.length, v.orientation, v.color) for v in vehicles]
    start = tuple((v.x, v.y) for v in vehicles)
    parent = {start: None}
    move_from = {}
    q = deque([start])

    def is_win(state):
        # la voiture rouge est toujours l'index 0
        x, y = state[0]
        length = proto[0][1]
        return x + length - 1 == width - 1

    def make_board(state):
        b = Board(width, height)
        for (vid, length, ori, color), (x, y) in zip(proto, state):
            b.add_vehicle(Vehicle(vid, x, y, length, ori, color))
        return b

    goal = None
    while q:
        state = q.popleft()
        if is_win(state):
            goal = state
            break
        board = make_board(state)
        for i, (x, y) in enumerate(state):
            vid, length, ori, color = proto[i]
            for delta in (-1, +1):
                nx, ny = (x + delta, y) if ori=='H' else (x, y + delta)
                v = Vehicle(vid, x, y, length, ori, color)
                board.vehicles[i] = v
                if board.can_move(v, nx, ny):
                    new_state = list(state)
                    new_state[i] = (nx, ny)
                    new_state = tuple(new_state)
                    if new_state not in parent:
                        parent[new_state] = state
                        move_from[new_state] = (i, delta)
                        q.append(new_state)
    if goal is None:
        return []

    # Reconstitution du chemin
    path = []
    s = goal
    while parent[s] is not None:
        path.append(move_from[s])
        s = parent[s]
    path.reverse()
    return path

# Boutons UI : (rectangle, label, fonction)
BUTTONS = [
    (pygame.Rect(  0, 0, 150, UI_HEIGHT), "Carte 1", config1),
    (pygame.Rect(150, 0, 150, UI_HEIGHT), "Carte 2", config2),
    (pygame.Rect(300, 0, 150, UI_HEIGHT), "Carte 3", config3),
    (pygame.Rect(450, 0, 150, UI_HEIGHT), "Solution", None),
]
FONT = pygame.font.SysFont(None, 24)

def draw_ui():
    """Dessine la barre de boutons."""
    for rect, label, _func in BUTTONS:
        pygame.draw.rect(WIN, (100,100,100), rect)
        pygame.draw.rect(WIN, (255,255,255), rect, 2)
        txt = FONT.render(label, True, (255,255,255))
        WIN.blit(txt, txt.get_rect(center=rect.center))

def draw_board(board, selected=None):
    """Dessine la grille et les véhicules (offset UI_HEIGHT)."""
    # grille
    WIN.fill((200,200,200), (0, UI_HEIGHT, SIZE, SIZE))
    for i in range(7):
        x = i*CELL
        y = UI_HEIGHT + i*CELL
        pygame.draw.line(WIN, (150,150,150), (x, UI_HEIGHT), (x, UI_HEIGHT+SIZE))
        pygame.draw.line(WIN, (150,150,150), (0, y), (SIZE, y))
    # véhicules
    for v in board.vehicles:
        if v.orientation=='H':
            w, h = CELL*v.length, CELL
        else:
            w, h = CELL, CELL*v.length
        px = v.x*CELL
        py = UI_HEIGHT + v.y*CELL
        rect = pygame.Rect(px, py, w, h)
        pygame.draw.rect(WIN, v.color, rect)
        if v is selected:
            pygame.draw.rect(WIN, (255,255,0), rect, 4)

def main():
    clock = pygame.time.Clock()
    board = Board()
    config1(board)
    selected = None

    # Variables d’animation
    solution_moves = []
    anim_timer     = 0
    animating      = False

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # Clic souris
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                # UI ?
                if my < UI_HEIGHT:
                    for rect, _label, func in BUTTONS:
                        if rect.collidepoint(mx, my):
                            if func:
                                func(board)
                                selected    = None
                                animating   = False
                            else:
                                # Lancer le solveur
                                solution_moves = solve(board.vehicles)
                                anim_timer     = pygame.time.get_ticks()
                                animating      = True
                            break
                    continue
                # grille → sélection
                gx = mx // CELL
                gy = (my - UI_HEIGHT) // CELL
                selected = None
                for v in board.vehicles:
                    if (gx, gy) in v.cells_occupied():
                        selected = v
                        break

            # Flèches → déplacement manuel
            elif ev.type == pygame.KEYDOWN and selected:
                if ev.key == pygame.K_LEFT and selected.orientation=='H':
                    selected.move(-1, board)
                elif ev.key == pygame.K_RIGHT and selected.orientation=='H':
                    selected.move(1, board)
                elif ev.key == pygame.K_UP and selected.orientation=='V':
                    selected.move(-1, board)
                elif ev.key == pygame.K_DOWN and selected.orientation=='V':
                    selected.move(1, board)

        # Animation auto
        if animating and solution_moves:
            now = pygame.time.get_ticks()
            if now - anim_timer >= ANIM_DELAY:
                i, delta = solution_moves.pop(0)
                board.vehicles[i].move(delta, board)
                selected    = None
                anim_timer  = now
        elif animating:
            animating = False  # terminé

        # Dessin
        WIN.fill((0,0,0))
        draw_ui()
        draw_board(board, selected)
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
