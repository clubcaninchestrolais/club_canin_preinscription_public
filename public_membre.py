import streamlit as st
from supabase_rest import supabase
import datetime

st.set_page_config(page_title="Préinscription membre", page_icon="🐶", layout="centered")

st.title("Préinscription membre du Club Canin")
st.write("Cette page est réservée aux **membres déjà inscrits au club**.")

# ---------------------------------------------------------
# Charger les membres
# ---------------------------------------------------------
membres = (
    supabase.table("membres")
    .select("*")
    .order("nom")
    .execute()
    .data
)

if not membres:
    st.error("Aucun membre trouvé.")
    st.stop()

# Sélection du membre
membre_labels = {f"{m['prenom']} {m['nom']}": m["id"] for m in membres}
membre_nom = st.selectbox("Votre nom :", list(membre_labels.keys()))
membre_id = membre_labels[membre_nom]

# ---------------------------------------------------------
# Charger les chiens du membre
# ---------------------------------------------------------
chiens = (
    supabase.table("chiens")
    .select("*")
    .eq("membre_id", membre_id)
    .execute()
    .data
)

if not chiens:
    st.error("Aucun chien enregistré pour ce membre.")
    st.stop()

chien_labels = {f"{c['nom']} ({c['race']})": c["id"] for c in chiens}
chien_nom = st.selectbox("Votre chien :", list(chien_labels.keys()))
chien_id = chien_labels[chien_nom]

# ---------------------------------------------------------
# Charger les séances
# ---------------------------------------------------------
seances = (
    supabase.table("cours_seances")
    .select("*")
    .order("date_seance")
    .execute()
    .data
)

if not seances:
    st.error("Aucune séance disponible.")
    st.stop()

seance_labels = {
    f"{s['date_seance']} - {s['heure_debut']}": s["id"]
    for s in seances
}

seance_nom = st.selectbox("Séance :", list(seance_labels.keys()))
seance_id = seance_labels[seance_nom]

# ---------------------------------------------------------
# Bouton d'inscription
# ---------------------------------------------------------
if st.button("S'inscrire à la séance"):
    data = {
        "membre_id": membre_id,
        "chien_id": chien_id,
        "seance_id": seance_id,
        "type": "membre",
        "statut": "en_attente",
        "traitee": False,
        "date_inscription": str(datetime.date.today())
    }

    supabase.table("preinscriptions").insert(data).execute()
    st.success("Votre préinscription a été envoyée !")
