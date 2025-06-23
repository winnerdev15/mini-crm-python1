import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
import csv
from db import init_db

# Initialisation de la base
init_db()
id_client_selectionne = None

# Fonction pour ajouter un client
def ajouter_client():
    nom = entry_nom.get()
    prenom = entry_prenom.get()
    telephone = entry_tel.get()
    email = entry_email.get()
    entreprise = entry_entreprise.get()

    if not nom or not prenom:
        messagebox.showwarning("Champs manquants", "Le nom et le prénom sont obligatoires.")
        return

    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO clients (nom, prenom, telephone, email, entreprise)
        VALUES (?, ?, ?, ?, ?)
    ''', (nom, prenom, telephone, email, entreprise))
    conn.commit()
    conn.close()

    messagebox.showinfo("Succès", "Client ajouté avec succès.")
    for entry in [entry_nom, entry_prenom, entry_tel, entry_email, entry_entreprise]:
        entry.delete(0, tk.END)

    charger_clients()

# Fonction pour charger tous les clients dans la liste
def charger_clients():
    listbox_clients.delete(0, tk.END)
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nom, prenom, entreprise FROM clients ORDER BY id DESC")
    for row in cursor.fetchall():
        nom, prenom, entreprise = row
        affichage = f"{prenom} {nom} - {entreprise}"
        listbox_clients.insert(tk.END, affichage)
    conn.close()

# Fonction pour supprimer un client sélectionné
def supprimer_client():
    selection = listbox_clients.curselection()
    if not selection:
        messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un client à supprimer.")
        return

    index = selection[0]
    ligne = listbox_clients.get(index)
    nom_complet = ligne.split(" - ")[0]
    prenom, nom = nom_complet.split(" ")

    if not messagebox.askyesno("Confirmation", f"Supprimer {prenom} {nom} ?"):
        return

    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients WHERE nom = ? AND prenom = ?", (nom, prenom))
    conn.commit()
    conn.close()

    messagebox.showinfo("Supprimé", f"{prenom} {nom} a été supprimé.")
    charger_clients()

# Fonction pour exporter tous les clients en fichier CSV
def exporter_csv():
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nom, prenom, telephone, email, entreprise FROM clients")
    clients = cursor.fetchall()
    conn.close()

    if not clients:
        messagebox.showinfo("Aucun client", "Aucun client à exporter.")
        return

    fichier = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("Fichiers CSV", "*.csv")],
        title="Enregistrer sous..."
    )

    if fichier:
        with open(fichier, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Nom", "Prénom", "Téléphone", "Email", "Entreprise"])
            writer.writerows(clients)

        messagebox.showinfo("Export réussi", f"Liste exportée dans : {fichier}")

# Fonction pour charger les infos du client dans les champs
def charger_donnees_client(event):
    global id_client_selectionne
    selection = listbox_clients.curselection()
    if not selection:
        return

    index = selection[0]
    ligne = listbox_clients.get(index)
    nom_complet = ligne.split(" - ")[0]
    prenom, nom = nom_complet.split(" ")

    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom, prenom, telephone, email, entreprise FROM clients WHERE nom = ? AND prenom = ?", (nom, prenom))
    client = cursor.fetchone()
    conn.close()

    if client:
        id_client_selectionne = client[0]
        entry_nom.delete(0, tk.END)
        entry_nom.insert(0, client[1])
        entry_prenom.delete(0, tk.END)
        entry_prenom.insert(0, client[2])
        entry_tel.delete(0, tk.END)
        entry_tel.insert(0, client[3])
        entry_email.delete(0, tk.END)
        entry_email.insert(0, client[4])
        entry_entreprise.delete(0, tk.END)
        entry_entreprise.insert(0, client[5])

# Fonction pour mettre à jour le client sélectionné
def mettre_a_jour_client():
    global id_client_selectionne
    if id_client_selectionne is None:
        messagebox.showwarning("Aucun client", "Sélectionnez un client à modifier.")
        return

    nom = entry_nom.get()
    prenom = entry_prenom.get()
    telephone = entry_tel.get()
    email = entry_email.get()
    entreprise = entry_entreprise.get()

    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE clients
        SET nom = ?, prenom = ?, telephone = ?, email = ?, entreprise = ?
        WHERE id = ?
    ''', (nom, prenom, telephone, email, entreprise, id_client_selectionne))
    conn.commit()
    conn.close()

    messagebox.showinfo("Mise à jour", "Client mis à jour avec succès.")
    id_client_selectionne = None
    for entry in [entry_nom, entry_prenom, entry_tel, entry_email, entry_entreprise]:
        entry.delete(0, tk.END)
    charger_clients()

# Interface graphique
root = tk.Tk()
root.title("Mini CRM - Gestion de clients")
root.geometry("420x650")

# Formulaires
tk.Label(root, text="Nom").pack()
entry_nom = tk.Entry(root)
entry_nom.pack()

tk.Label(root, text="Prénom").pack()
entry_prenom = tk.Entry(root)
entry_prenom.pack()

tk.Label(root, text="Téléphone").pack()
entry_tel = tk.Entry(root)
entry_tel.pack()

tk.Label(root, text="Email").pack()
entry_email = tk.Entry(root)
entry_email.pack()

tk.Label(root, text="Entreprise").pack()
entry_entreprise = tk.Entry(root)
entry_entreprise.pack()

tk.Button(root, text="Ajouter le client", command=ajouter_client, bg="#0a9396", fg="white").pack(pady=10)

# Liste des clients
tk.Label(root, text="Liste des clients enregistrés").pack()
listbox_clients = tk.Listbox(root, width=50)
listbox_clients.pack(pady=10, expand=True, fill=tk.BOTH)
listbox_clients.bind('<<ListboxSelect>>', charger_donnees_client)

# Boutons supplémentaires
tk.Button(root, text="Supprimer le client sélectionné", command=supprimer_client, bg="red", fg="white").pack(pady=5)
tk.Button(root, text="Exporter en CSV", command=exporter_csv, bg="#198754", fg="white").pack(pady=5)
tk.Button(root, text="Mettre à jour le client", command=mettre_a_jour_client, bg="#ffc107", fg="black").pack(pady=5)

# Lancement de l'app
charger_clients()
root.mainloop()
