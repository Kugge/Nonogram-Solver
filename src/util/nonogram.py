# nonogram.py - Sofiane DJERBI & Salem HAFTARI
""" CONVENTIONS
 | Les nonogrammes donnent les informations en partant du haut et de la gauche.
 | row[x], col[y] : infos de la case en position x,y (Coordonnées matricielles)
"""
import time
import math
import pickle

def _convert(n, c, d=0, prec=[]): # O(t) avec t la taille de l'arbre construit
    """ CALCULE LES COMBINAISONS POSSIBLES PAR LIGNE
    Paramètres:
        - n: Taille de la ligne/colonne
        - c: Les coefficients
    Retourne:
        - Une liste avec le nombre d'espaces possibles entre chaque coefficient
    """
    l = list(range(d, n - sum(c) - len(c) + 2)) # Case maximale accessible
    if len(c) == 1:
        for i in l:
            yield prec + [i] # On ne s'arrête pas
    else:
        # d = 1 : On est obligé d'avoir au minimum une case d'écart
        # n-i-c[0] : On enlève les cases prises par le premier coef
        # Cette ligne construit les arbres des possibilités
        for i in l:
            yield from _convert(n-i-c[0], c[1:], 1, prec + [i])


def convert(n, c): # O(n^3) + O(t) avec n le nombre de coef par ligne et O(t) la complexité de _convert
    """ WRAPPER POUR CONVERT, RETOURNE DES DONNEES EXPLOITABLES
    Paramètres:
        - n: Taille de la ligne/colonne
        - c: Les coefficients
    Retourne:
        - Une liste comprise dans le produit cartésien {1, -1}^n
    """
    c = [i for i in c if i != 0] # On enleve les 0
    if len(c) == 0: # Si aucun coef, tout est rogné
        yield [-1]*n
        return
    for x in _convert(n, c): # Parcours des configurations
        l = [-1]*n # Tout invalide par défaut, on rend ca valide après
        pos = 0 # pos de départ des 1
        for y, z in zip(c, x): # y = parcours du coefficient, z = espace précédents associés
            l[pos+z:pos+z+y] = [1]*y # On fixe les cases avant et on avance du coefficient
            pos = pos+z+y
        yield l


class Nonogram:
    """ NONOGRAMME
    Cet objet représente un nonogramme.
    Variables:
        - x, y: Taille du nonogramme
        - name: Nom du nonogramme
        - row: Informations des lignes du nonogramme
        - col: Informations des colonnes du nonogramme
        - colors: Le nonogramme est-il en couleur ? (Booléen)
        - formula: Formule logique correspondant au booléen (FND/FNC)
    """
    def __init__(self, size=(0,0), row=[], col=[], name=""): # O(1)
        """ INITIALISATION
        Paramètres:
            - x,y: Taile du nonogramme
            - name: Nom du nonogramme
            - row: Informations des lignes du nonogramme
            - col: Informations des colonnes du nonogramme
        """
        self.y, self.x = size
        self.name = name
        self.row = row
        self.col = col

    def __str__(self):
        return f"Size: {self.y}x{self.x}, row:{self.row}, col:{self.col}"

    def solve(self, engine):
        """ CONVERTIS LE NONOGRAMME EN FORMULE ET LE RESOUD AVEC UN SOLVEUR """
        instance = engine() # Formule principale
        compteur = self.x*self.y + 1 # Pour ne pas interférer avec les cases
        print("\nLoading CNF...")
        a = time.time()

        # LIGNES
        for i, c in enumerate(self.row): # i = ligne, c = coefficient
            lines = [] # Liste des configurations par ligne
            for config in convert(self.y, c): # Parcours des config
                x = list(range(i*self.y+1, (i+1)*self.y+1)) # Numéros de la ligne
                for v in [a*b for a,b in zip(x,config)]: # Parcours des variables
                    instance.add_clause([-compteur, v]) # LISTE DES IMPLICATIONS
                lines.append(compteur)
                compteur += 1 # On passe a la prochaine config
            instance.add_clause(lines)
        # COLONNES
        for i, c in enumerate(self.col): # i = ligne, c = coefficient
            lines = [] # Liste des configurations par ligne
            for config in convert(self.x, c): # Parcours des config
                x = [i%self.y + self.y * j + 1 for j in range(self.y)] # Numéros de la colonne
                for v in [a*b for a,b in zip(x,config)]: # Parcours des variables
                    instance.add_clause([-compteur, v]) # LISTE DES IMPLICATIONS
                lines.append(compteur)
                compteur += 1 # On passe a la prochaine config
            instance.add_clause(lines)

        t = time.time() - a
        print("Loaded in {:.2f} seconds!".format(t))
        print("\nSolving...")
        a = time.time()
        solvable = instance.solve()
        t = time.time() - a
        print("Solved in {:.2f} seconds!".format(t))

        if solvable:
            return instance.get_model()
        return None # "Sinon" pas obligatoire car le if retourne



    def save(self, path="."): # O(1)
        """ SAUVEGARDE
        Sauvegarde le nonogramme dans un dossier, nom donné automatiquement
        Paramètres:
            - path: Chemin du dossier
        """
        print("Saving nonogram...")
        if path[-1] == "/": # Petite correction de syntaxe..
            path = path[:-1]
        path = f"{path}/{self.name.lower()}.nng" # nng = NoNoGram
        # Ci dessous: Dictionnaire qui regroupe les variables du nonogramme
        d = {"x": self.x, "y": self.y, "name": self.name, "row": self.row,
             "col": self.col}
        with open(path, 'wb+') as file: # On ouvre en write + binary + créer
            pickle.dump(d, file)
        print(f"NNG {self.name} sucessfully saved.")

    def load(self, path):
        """ CHARGER
        Charge le fichier .nng d'un nonogramme
        Paramètres:
            - path: Chemin du fichier (et non du dossier cette fois-ci !)
        """
        print("Loading nonogram...")
        with open(path, 'rb') as file: # On ouvre en read + binary
            d = pickle.load(file) # Chargement du dictionnaire
        self.name = d["name"]
        self.x = d["x"]
        self.y = d["y"]
        self.row = d["row"]
        self.col = d["col"]
        print(f"NNG {self.name} sucessfully loaded.")

    def print_complexity(self):
        s = 0 # Somme
        c = 0 # Clauses
        m = 0 # Max
        print("\nComputing complexity...")
        l = max(self.x, self.y) # Plus grande colonne/ligne
        for i in self.row:
            i = [x for x in i if x != 0]
            n = self.y - sum(i) - len(i) + 1
            a = math.comb(len(i) + n, len(i))
            s += a # Nombre de configurations
            c += a*self.y + 1 # Nombre de clauses associées à chaque conf

        for i in self.col:
            i = [x for x in i if x != 0]
            n = self.x - sum(i) - len(i) + 1
            a = math.comb(len(i) + n, len(i))
            s += a # Nombre de configurations
            c += a*self.x + 1 # Nombre de clauses associées à chaque conf

        mbs = int(c*5/8)//1000000 # On admet que 1 clause = 5 octet
        print(f"Configs: {s}\nClauses: {c}\nMBs approximation: {mbs}")


if __name__ == '__main__':
    for i in range(10):
        print(len(list(_convert(i, [1,1]))))
    for i in range(15):
        print(len(list(_convert(i, [1,1,1]))))
    for i in range(15):
        print(len(list(_convert(i, [1,1,1,1]))))
