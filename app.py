import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Préinscription Club Canin", page_icon="🐾")

# --- Connexion Supabase ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("🐾 Préinscription extérieure")

st.write("Merci de remplir ce formulaire pour vous inscrire au club canin.")

nom = st.text_input("Nom")
prenom = st.text_input("Prénom")
email = st.text_input("Email")
telephone = st.text_input("Téléphone")
chien_nom = st.text_input("Nom du chien")
chien_race = st.text_input("Race du chien")

if st.button("Envoyer la préinscription"):
    data = {
        "nom": nom,
        "prenom": prenom,
        "email": email,
        "telephone": telephone,
        "chien_nom": chien_nom,
        "chien_race": chien_race,
        "statut": "en_attente"
    }
    supabase.table("preinscriptions").insert(data).execute()
    st.success("Votre préinscription a été envoyée au club !")
