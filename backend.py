

# backend.py

class Vehicle:
    def __init__(self, vid, x, y, length, orientation, color):
        """
        vid        : identifiant (string) unique du véhicule
        x, y       : position de la case en haut-à-gauche (0-index)
        length     : longueur (2 pour voiture, 3 pour camion)
        orientation: 'H' ou 'V'
        color      : tuple RGB, ex. (255,0,0)
        """
        self.id = vid
        self.x = x
        self.y = y
        self.length = length
        self.orientation = orientation
        self.color = color

    def cells_occupied(self):
        """Retourne la liste des (x, y) occupées par ce véhicule."""
        cells = []
        for i in range(self.length):
            if self.orientation == 'H':
                cells.append((self.x + i, self.y))
            else:
                cells.append((self.x, self.y + i))
        return cells
    
    def move(self, delta, board):
        """
        Tente de déplacer ce véhicule de `delta` cases (±1) dans son axe.
        :return: True si réussi, False sinon.
        """
        new_x, new_y = self.x, self.y
        if self.orientation == 'H':
            new_x += delta
        else:
            new_y += delta
        if board.can_move(self, new_x, new_y):
            self.x, self.y = new_x, new_y
            return True
        return False

class Board:
    def __init__(self, width=6, height=6):
        self.width = width
        self.height = height
        self.vehicles = []

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def is_free(self, x, y, ignore=None):
        """Vérifie si (x,y) est dans la grille et non occupé (sauf par ignore)."""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        for v in self.vehicles:
            if v is ignore:
                continue
            if (x, y) in v.cells_occupied():
                return False
        return True

    def can_move(self, vehicle, new_x, new_y):
        """
        Vérifie si `vehicle` peut être positionné à (new_x, new_y)
        sans chevaucher ni sortir de la grille.
        """
        for i in range(vehicle.length):
            if vehicle.orientation == 'H':
                x, y = new_x + i, new_y
            else:
                x, y = new_x, new_y + i
            if not self.is_free(x, y, ignore=vehicle):
                return False
        return True



