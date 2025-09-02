import ctypes
from ctypes import c_int, c_float, c_bool, c_void_p, POINTER

import importlib.resources as pkg_resources
from pathlib import Path
import monmoteur
# --------------------
# Définir les constantes et types C
# --------------------
TAILLE_LIEN_GT = 256

class TextureEntry(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_char * TAILLE_LIEN_GT),
        ("texture", c_void_p)
    ]

class GestionnaireTextures(ctypes.Structure):
    _fields_ = [
        ("entrees", POINTER(TextureEntry)),
        ("taille", c_int),
        ("capacite", c_int),
        ("rendu", c_void_p)
    ]

class GestionnaireEntrees(ctypes.Structure):
    _fields_ = [
        ("mouse_x", c_int),
        ("mouse_y", c_int),
        ("mouse_pressed", c_bool),
        ("mouse_just_pressed", c_bool),
        ("keys", c_bool * 512),
        ("keys_pressed", c_bool * 512),
        ("quit", c_bool)
    ]

class Image(ctypes.Structure):
    _fields_ = [
        ("id", c_int),
        ("posx", c_float),
        ("posy", c_float),
        ("taillex", c_float),
        ("tailley", c_float),
        ("sens", c_int),
        ("texture", c_void_p)
    ]

class TableauImage(ctypes.Structure):
    _fields_ = [
        ("tab", POINTER(Image)),
        ("nb_images", c_int),
        ("capacite_images", c_int)
    ]

class FondActualiser(ctypes.Structure):
    _fields_ = [
        ("r", c_int),
        ("g", c_int),
        ("b", c_int),
        ("dessiner", c_bool)
    ]

class Gestionnaire(ctypes.Structure):
    _fields_ = [
        ("run", c_bool),
        ("dt", c_float),
        ("largeur", c_int),
        ("hauteur", c_int),
        ("coeff_minimise", c_int),
        ("largeur_actuel", c_int),
        ("hauteur_actuel", c_int),
        ("plein_ecran", c_bool),
        ("temps_frame", c_int),
        ("fenetre", c_void_p),
        ("rendu", c_void_p),
        ("fond", POINTER(FondActualiser)),
        ("image", POINTER(TableauImage)),
        ("entrees", POINTER(GestionnaireEntrees)),
        ("textures", POINTER(GestionnaireTextures)),
    ]

def charger_dll():
    dll_path = pkg_resources.files(monmoteur) / "dll" / "jeu.dll"
    return ctypes.CDLL(str(dll_path))

jeu = charger_dll()
# Définir les signatures
jeu.initialisation.argtypes = (c_int, c_int, c_float, c_int,
                               ctypes.c_char_p, c_bool, c_int, c_int, c_int)
jeu.initialisation.restype = POINTER(Gestionnaire)

jeu.update.argtypes = (POINTER(Gestionnaire),)
jeu.update.restype = None

jeu.ajouter_image_au_tableau.argtypes = (POINTER(Gestionnaire), ctypes.c_char_p,
                                         c_float, c_float, c_float, c_float,
                                         c_int, c_int)
jeu.ajouter_image_au_tableau.restype = c_int

jeu.supprimer_images_par_id.argtypes = (POINTER(Gestionnaire), c_int)
jeu.supprimer_images_par_id.restype = None

jeu.modifier_images.argtypes = (POINTER(Gestionnaire), c_float, c_float,
                                c_float, c_float, c_int, c_int)
jeu.modifier_images.restype = None

jeu.modifier_texture_image.argtypes = (POINTER(Gestionnaire), ctypes.c_char_p, c_int)
jeu.modifier_texture_image.restype = None

jeu.touche_juste_presse.argtypes = (POINTER(Gestionnaire), ctypes.c_char_p)
jeu.touche_juste_presse.restype = c_bool

jeu.touche_enfoncee.argtypes = (POINTER(Gestionnaire), ctypes.c_char_p)
jeu.touche_enfoncee.restype = c_bool

jeu.redimensionner_fenetre.argtypes = (POINTER(Gestionnaire),)
jeu.redimensionner_fenetre.restype = None

jeu.boucle_principale.argtypes = (POINTER(Gestionnaire),)
jeu.boucle_principale.restype = None

# Callback C <-> Python
UPDATEFUNC = ctypes.CFUNCTYPE(None, POINTER(Gestionnaire))
jeu.set_update_callback.argtypes = (UPDATEFUNC,)
jeu.set_update_callback.restype = None


class Projet:
    def __init__(self, largeur=320, hauteur=180, dt=1/60,coeff_ecran_minimise=3, chemin_image="",dessiner_fond=True, r=0, g=0, b=0):

        self.gestionnaire = jeu.initialisation(
            hauteur, largeur, dt, coeff_ecran_minimise,
            chemin_image.encode("utf-8"), dessiner_fond, r, g, b
        )
        if not self.gestionnaire:
            raise RuntimeError("Erreur d'initialisation du moteur")



        self._update_func = UPDATEFUNC(self._internal_update)
        jeu.set_update_callback(self._update_func)

        self.time = self.gestionnaire.contents.temps_frame
        self.largeur = self.gestionnaire.contents.largeur_actuel
        self.hauteur = self.gestionnaire.contents.hauteur_actuel
        self.dt = self.gestionnaire.contents.dt


    def ajouter_image(self, chemin, x, y, w, h, id_num,sens=0):
        return jeu.ajouter_image_au_tableau(
            self.gestionnaire, chemin.encode("utf-8"), x, y, w, h, sens, id_num
        )

    def supprimer_images(self, id_num):
        jeu.supprimer_images_par_id(self.gestionnaire, id_num)

    def modifier_image(self, x, y, w, h, sens, id_num):
        jeu.modifier_images(self.gestionnaire, x, y, w, h, sens, id_num)

    def changer_texture(self, chemin, id_num):
        jeu.modifier_texture_image(self.gestionnaire, chemin.encode("utf-8"), id_num)

    def touche_juste_presse(self, touche: str) -> bool:
        return jeu.touche_juste_presse(self.gestionnaire, touche.encode("utf-8"))

    def touche_enfoncee(self, touche: str) -> bool:
        return jeu.touche_enfoncee(self.gestionnaire, touche.encode("utf-8"))

    def redimensionner(self):
        return jeu.redimensionner_fenetre(self.gestionnaire)

    def _internal_update(self, g_ptr):
        # mettre à jour les champs automatiquement
        self.time = g_ptr.contents.temps_frame
        self.largeur = g_ptr.contents.largeur_actuel
        self.hauteur = g_ptr.contents.hauteur_actuel
        self.dt = g_ptr.contents.dt

        # appeler la méthode de l’utilisateur
        self.update()
    def update(self):
        pass
        

    def lancer(self):
        jeu.boucle_principale(self.gestionnaire)
