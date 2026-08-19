import streamlit as st
from supabase import create_client, Client
import datetime

# ---------------------------------------------------------
# Connexion Supabase
# ---------------------------------------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Préinscription membre", page_icon="🐶", layout="centered")

st.title("Préinscription membre du Club Canin")
st.write("Cette page est réservée aux **membres déjà inscrits au club**.")

# ---------------------------------------------------------
# Identification par email
# ---------------------------------------------------------
email = st.text_input("Votre email (celui enregistré au club)")

if email:
    membre = (
        supabase.table("membres")
        .select("*")
        .eq("email", email)
        .execute()
        .data
    )

    if not membre:
        st.error("Email inconnu. Vous devez être membre du club.")
        st.stop()

    membre = membre[0]
    membre_id = membre["id"]

    st.success(f"Bienvenue {membre['prenom']} {membre['nom']} !")

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
            "date_presence": str(datetime.date.today()),
            "present": False
        }

        supabase.table("cours_presences").insert(data).execute()
        st.success("Votre inscription a été enregistrée !")

