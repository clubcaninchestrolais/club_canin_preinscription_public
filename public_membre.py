import streamlit as st
from supabase import create_client, Client
import datetime

# -----------------------------
# Connexion Supabase
# -----------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Préinscription membre", page_icon="🐶", layout="centered")

# -----------------------------
# En-tête
# -----------------------------
st.title("Préinscription membre du Club Canin")
st.write("Cette page est réservée aux **membres déjà inscrits au club**.")

# -----------------------------
# Charger les membres
# -----------------------------
membres = supabase.table("membres").select("*").execute().data
chiens = supabase.table("chiens").select("*").execute().data
seances = supabase.table("seances").select("*").execute().data

# -----------------------------
# Sélection du membre
# -----------------------------
liste_membres = {f"{m['nom']} {m['prenom']}": m["id"] for m in membres}
membre_nom = st.selectbox("Sélectionnez votre nom", list(liste_membres.keys()))
membre_id = liste_membres[membre_nom]

# -----------------------------
# Sélection du chien
# -----------------------------
chiens_membre = [c for c in chiens if c["membre_id"] == membre_id]
liste_chiens = {c["nom"]: c["id"] for c in chiens_membre}

if len(liste_chiens) == 0:
    st.error("Aucun chien enregistré pour ce membre.")
    st.stop()

chien_nom = st.selectbox("Sélectionnez votre chien", list(liste_chiens.keys()))
chien_id = liste_chiens[chien_nom]

# -----------------------------
# Sélection de la séance
# -----------------------------
liste_seances = {f"{s['date']} - {s['type']}": s["id"] for s in seances}
seance_nom = st.selectbox("Séance", list(liste_seances.keys()))
seance_id = liste_seances[seance_nom]

# -----------------------------
# Bouton d'inscription
# -----------------------------
if st.button("S'inscrire à la séance"):
    data = {
        "membre_id": membre_id,
        "chien_id": chien_id,
        "seance_id": seance_id,
        "type": "membre",
        "statut": "en_attente",
        "traitee": False,
        "date_inscription": datetime.datetime.now().isoformat()
    }

    supabase.table("preinscriptions").insert(data).execute()
    st.success("Votre préinscription a été envoyée !")
