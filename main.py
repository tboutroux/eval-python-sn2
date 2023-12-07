import sqlite3 # Import de sqlite
import sys # pour quitter le programme
import datetime # pour la date et l'heure
import os # pour effacer le terminal
import time # pour le temps

"""
Table Livre :
- id
- titre 
- auteur
- catégorie
- est_emprunte
- id_utilisateur

Table Utilisateur :
- id
- nom
- prenom
"""

conn = sqlite3.connect("bibliotheque.db")
cur = conn.cursor()

class Bibliotheque:
    """
    Classe pour la bibliothèque
    """
    _instance = None

    def __new__(cls):
        """
        Méthode pour créer un singleton
        """
        if not cls._instance:
            cls._instance = super(Bibliotheque, cls).__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """
        Constructeur de la classe
        """
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS livre (
                    id INTEGER PRIMARY KEY, 
                    titre VARCHAR(50), 
                    auteur VARCHAR(50), 
                    categorie VARCHAR(50),
                    est_emprunte TINYINT, 
                    id_utilisateur INT,
                    FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id)
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS utilisateur (
                    id INTEGER PRIMARY KEY, 
                    nom VARCHAR(50), 
                    prenom VARCHAR(50),
                    est_banni TINYINT,
                    date_ban DATETIME
                )
            """)

            conn.commit()

        except sqlite3.OperationalError:
            print("Erreur lors de la création des tables !")
            sys.exit()

    def afficher_livre(self, livre):
        """
        Méthode pour afficher un livre
        """
        print("+------------------------------------+")
        print(f"Titre : {livre[1]}")
        print(f"Auteur : {livre[2]}")
        print(f"Catégorie : {livre[3]}")
        print(f"Emprunté : {livre[4]}")
        print(f"Utilisateur : {livre[5]}")
        print("+------------------------------------+")

    def recherche_livre_titre(self, titre):
        """
        Méthode pour rechercher un livre par son titre
        """
        cur.execute("SELECT * FROM livre WHERE titre LIKE ?", (f"%{titre}%",))
        livre = cur.fetchone()
        if livre:
            self.afficher_livre(livre)
        else:
            print("Ce livre n'existe pas !")

    def recherche_livre_auteur(self, auteur):
        """
        Méthode pour rechercher un livre par son auteur
        """
        cur.execute("SELECT * FROM livre WHERE auteur LIKE ?", (f"%{auteur}%",))
        livre = cur.fetchone()
        if livre:
            self.afficher_livre(livre)
        else:
            print("Ce livre n'existe pas !")

    def recherche_livre_categorie(self, categorie):
        """
        Méthode pour rechercher un livre par sa catégorie
        """
        cur.execute("SELECT * FROM livre WHERE categorie LIKE ?", (f"%{categorie}%",))
        livre = cur.fetchone()
        if livre:
            self.afficher_livre(livre)
        else:
            print("Ce livre n'existe pas !")

    def afficher_utilisateurs(self, mot):
        """
        Méthode pour afficher les utilisateurs
        """
        if mot == "bannis":
            cur.execute("SELECT * FROM utilisateur WHERE est_banni = 1")
        
        elif mot == "non bannis":
            cur.execute("SELECT * FROM utilisateur WHERE est_banni = 0")

        utilisateurs = cur.fetchall()
        for utilisateur in utilisateurs:
            print(utilisateur)

class Livre:
    """
    Classe pour les livres
    """
    def __init__(self, titre, auteur, categorie):
        """
        Constructeur de la classe
        """
        self.titre = titre
        self.auteur = auteur
        self.categorie = categorie
        self.est_emprunte = False
        self.utilisateur = None

    def ajouter_livre(self):
        """
        Méthode pour ajouter un livre
        """
        try:
            cur.execute("""
                INSERT INTO livre (
                    titre, 
                    auteur, 
                    categorie, 
                    est_emprunte, 
                    id_utilisateur
                ) VALUES (?, ?, ?, ?, ?)""", (self.titre, self.auteur, self.categorie, self.est_emprunte, self.utilisateur))
            conn.commit()
            print("Le livre a bien été ajouté à la base de données !")
            time.sleep(2)
            os.system("clear")
        
        except sqlite3.IntegrityError:
            print("Ce livre existe déjà !")
            time.sleep(4)
            os.system("clear")

    def supprimer_livre(self):
        """
        Méthode pour supprimer un livre
        """
        try:    
            cur.execute("DELETE FROM livre WHERE titre = ?", (self.titre,))
            conn.commit()
            print("Le livre a bien été supprimé de la base de données !")
            time.sleep(2)
            os.system("clear")
        
        except sqlite3.IntegrityError:
            print("Ce livre n'existe pas !")
            time.sleep(4)
            os.system("clear")

    def emprunter_livre(self, titre, nom, prenom):
        """
        Méthode pour emprunter un livre
        """

        try:

            try:
                # Récupération de l'id de l'utilisateur
                cur.execute("SELECT id FROM utilisateur WHERE nom = ? AND prenom = ?", (nom, prenom))
                id_utilisateur = cur.fetchone()[0]
                
                # Vérification que l'utilisateur n'est pas banni
                cur.execute("SELECT est_banni FROM utilisateur WHERE id = ?", (id_utilisateur,))
                est_banni = cur.fetchone()[0] == False if 0 else True
            
            except TypeError:
                print("Cet utilisateur n'existe pas !")
                time.sleep(2)
                os.system("clear")
                return

            if not est_banni:
                cur.execute("""
                    UPDATE livre 
                    SET est_emprunte = 1, id_utilisateur = ?
                    WHERE titre = ?
                    """, (id_utilisateur, titre))
                conn.commit()
                print("Le livre a bien été emprunté !")
                time.sleep(2)
                os.system("clear")
            
            else:
                print("Cet utilisateur est banni !")
                time.sleep(4)
                os.system("clear")
        
        except sqlite3.IntegrityError:
            print("Ce livre n'existe pas !")
            time.sleep(2)
            os.system("clear")

    def rendre_livre(self, titre):
        """
        Méthode pour rendre un livre
        """

        try:
            # Création d'une liste contenant les livres empruntés
            cur.execute("SELECT titre FROM livre WHERE est_emprunte = 1")
            livres_empruntes = cur.fetchall()
            livres_empruntes = [livre[0] for livre in livres_empruntes]

            # Vérification que le livre est bien emprunté
            if titre in livres_empruntes:
                cur.execute("UPDATE livre SET est_emprunte = 0, id_utilisateur = NULL WHERE titre = ?", (titre,))
                conn.commit()
                print("Le livre a bien été rendu !")
                time.sleep(2)
                os.system("clear")

            else:
                print("Ce livre n'est pas emprunté !")
                time.sleep(2)
                os.system("clear")

        except sqlite3.IntegrityError:
            print("Ce livre n'existe pas !")
            time.sleep(4)
            os.system("clear")

class LivreFactory:
    """
    Classe pour la création des livres
    """
    @staticmethod
    def creer_livre(titre, auteur, categorie):
        """
        Méthode pour créer un livre
        """
        return Livre(titre, auteur, categorie)

class Utilisateurs:
    """
    Classe pour les utilisateurs
    """
    def __init__(self, nom, prenom):
        """
        Constructeur de la classe
        """
        self.nom = nom
        self.prenom = prenom

    def ajouter_utilisateur(self):
        """
        Méthode pour ajouter un utilisateur
        """
        cur.execute("""
            INSERT INTO utilisateur (
                nom, 
                prenom
            ) VALUES (?, ?)""", (self.nom, self.prenom))
        conn.commit()
        print("L'utilisateur a bien été ajouté à la base de données !")
        time.sleep(2)
        os.system("clear")

    def supprimer_utilisateur(self):
        """
        Méthode pour supprimer un utilisateur
        """
        cur.execute("DELETE FROM utilisateur WHERE nom = ?", (self.nom,))
        conn.commit()
        print("L'utilisateur a bien été supprimé de la base de données !")
        time.sleep(2)
        os.system("clear")

class UtilisateursBannis(Utilisateurs):
    """
    Classe pour les utilisateurs bannis
    """
    def __init__(self, nom, prenom, date_ban):
        """
        Constructeur de la classe
        """
        super().__init__(nom, prenom)
        self.date_ban = date_ban

    def bannir_utilisateur(self):
        """
        Méthode pour bannir un utilisateur
        """
        cur.execute("""
            UPDATE utilisateur SET est_banni = 1, date_ban = ? WHERE nom = ?
        """, (self.date_ban, self.nom))
        conn.commit()
        print("L'utilisateur a bien été banni !")
        time.sleep(2)
        os.system("clear")

    def debannir_utilisateur(self):
        """
        Méthode pour débannir un utilisateur
        """
        cur.execute("""
            UPDATE utilisateur SET est_banni = 0, date_ban = NULL WHERE nom = ?
        """, (self.nom,))
        conn.commit()
        print("L'utilisateur a bien été débanni !")
        time.sleep(2)
        os.system("clear")

class UtilisateursFactory:
    """
    Classe pour la création des utilisateurs
    """
    @staticmethod
    def creer_utilisateur(nom, prenom):
        """
        Méthode pour créer un utilisateur
        """
        return Utilisateurs(nom, prenom)

def afficher_livres():
        """
        Méthode pour afficher les livres
        """
        cur.execute("SELECT * FROM livre")
        livres = cur.fetchall()
        for livre in livres:
            print(livre)

if __name__ == "__main__":
    bibliotheque = Bibliotheque()

    while True:
        print("Bienvenue dans la bibliothèque !")
        print("1. Rechercher un livre")
        print("2. Ajouter un livre")
        print("3. Supprimer un livre")
        print("4. Emprunter un livre")
        print("5. Rendre un livre")
        print("6. Ajouter un utilisateur")
        print("7. Supprimer un utilisateur")
        print("8. Bannir un utilisateur")
        print("9. Débannir un utilisateur")
        print("10. Afficher les utilisateurs")
        print("11. Afficher les livres")
        print("12. Quitter")
        choix = input("Que voulez-vous faire ? (1-12) ")

        match choix:

            case "1":
                print("1. Rechercher un livre par son titre")
                print("2. Rechercher un livre par son auteur")
                print("3. Rechercher un livre par sa catégorie")
                choix = input("Que voulez-vous faire ? ")
    
                if choix == "1":
                    titre = input("Quel est le titre du livre ? ")
                    bibliotheque.recherche_livre_titre(titre)
    
                elif choix == "2":
                    auteur = input("Quel est l'auteur du livre ? ")
                    bibliotheque.recherche_livre_auteur(auteur)
    
                elif choix == "3":
                    categorie = input("Quelle est la catégorie du livre ? ")
                    bibliotheque.recherche_livre_categorie(categorie)
    
                else:
                    print("Ce choix n'existe pas !")
                    time.sleep(2)
                    os.system("clear")
    
            case "2":
                titre = input("Quel est le titre du livre ? ")
                auteur = input("Quel est l'auteur du livre ? ")
                categorie = input("Quelle est la catégorie du livre ? ")
                livre = LivreFactory.creer_livre(titre, auteur, categorie)
                livre.ajouter_livre()
    
            case "3":
                titre = input("Quel est le titre du livre ? ")
                livre = LivreFactory.creer_livre(titre, None, None)
                livre.supprimer_livre()
    
            case "4":
            
                # Création d'une liste contenant les livres empruntés
                cur.execute("SELECT titre FROM livre WHERE est_emprunte = 1")
                livres_empruntes = cur.fetchall()
                livres_empruntes = [livre[0] for livre in livres_empruntes]
    
                # Affichage des livres empruntés
                print("------------------------")
                print("Liste des livres empruntés :")
                for livre in livres_empruntes:
                    print(livre)
                print("------------------------")
    
                titre = input("Quel est le titre du livre ? ")
                nom = input("Quel est le nom de l'utilisateur ? ")
                prenom = input("Quel est le prénom de l'utilisateur ? ")
                livre = LivreFactory.creer_livre(titre, None, None)
                livre.emprunter_livre(titre, nom, prenom)
    
            case "5":
                titre = input("Quel est le titre du livre ? ")
                livre = LivreFactory.creer_livre(titre, None, None)
                livre.rendre_livre(titre)
    
            case "6":
                nom = input("Quel est le nom de l'utilisateur ? ")
                prenom = input("Quel est le prénom de l'utilisateur ? ")
                utilisateur = UtilisateursFactory.creer_utilisateur(nom, prenom)
                utilisateur.ajouter_utilisateur()
    
            case "7":
                nom = input("Quel est le nom de l'utilisateur ? ")
                prenom = input("Quel est le prénom de l'utilisateur ? ")
                utilisateur = UtilisateursFactory.creer_utilisateur(nom, prenom)
                utilisateur.supprimer_utilisateur()
    
            case "8":
                nom = input("Quel est le nom de l'utilisateur ? ")
                prenom = input("Quel est le prénom de l'utilisateur ? ")
                date_ban = datetime.datetime.now()
                utilisateur = UtilisateursBannis(nom, prenom, date_ban)
                utilisateur.bannir_utilisateur()
    
            case "9":
                nom = input("Quel est le nom de l'utilisateur ? ")
                prenom = input("Quel est le prénom de l'utilisateur ? ")
                utilisateur = UtilisateursBannis(nom, prenom, None)
                utilisateur.debannir_utilisateur()
    
            case "10":
            
                print("Liste des utilisateurs bannis :")
                bibliotheque.afficher_utilisateurs("bannis")
                print("------------------------")
    
                print("Liste des utilisateurs non bannis :")
                bibliotheque.afficher_utilisateurs("non bannis")
                print("------------------------")
    
            case "11":
                print("Liste des livres :")
                print("------------------------")
                afficher_livres()
                print("------------------------")
    
            case "12":
                os.system("clear")
                sys.exit()
            
            case _ :
                print("Ce choix n'existe pas !")
                time.sleep(2)
                os.system("clear")
    