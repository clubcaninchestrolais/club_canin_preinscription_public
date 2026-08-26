import streamlit as st
from supabase import create_client, Client
from menu import hide_streamlit_menu, menu_lateral
import datetime

hide_streamlit_menu()
menu_lateral()

# --- Connexion Supabase ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("👤 Portail membre")

# --- Récupérer le membre connecté (exemple avec email en session) ---
# À adapter selon ton système d'authentification
email = st.session_state.get("user_email", None)

if not email:
    st.warning("Vous devez être connecté pour accéder au portail.")
    st.stop()

membre_req = (
    supabase.table("membres")
    .select("*")
    .eq("email", email)
    .execute()
)

if not membre_req.data:
    st.error("Aucun membre trouvé pour cet utilisateur.")
    st.stop()

membre = membre_req.data[0]
membre_id = membre["id"]

st.subheader(f"Bienvenue {membre['prenom']} {membre['nom']}")

st.markdown("---")

# --- Récupérer les séances à venir pour ce membre (via cours_presences ou inscriptions) ---
# Ici, on affiche simplement toutes les séances à venir, avec le nom du cours

aujourd_hui = datetime.date.today().isoformat()

seances_req = (
    supabase
    .table("cours_seances")
    .select("*, cours(*)")
    .gte("date_seance", aujourd_hui)
    .order("date_seance")
    .execute()
)

seances = seances_req.data

if not seances:
    st.info("Aucune séance à venir.")
    st.stop()

st.subheader("📅 Séances à venir")

for s in seances:
    # s contient les champs de cours_seances + l'objet cours
    date = s["date_seance"]
    heure_debut = s.get("heure_debut", "")
    heure_fin = s.get("heure_fin", "")
    cours = s.get("cours", {})
    nom_cours = cours.get("nom_cours", "Cours")

    # Affichage propre
    st.markdown(
        f"- **{date}** – {nom_cours}"
        + (f" ({heure_debut} → {heure_fin})" if heure_debut and heure_fin else "")
    )

st.markdown("---")

st.info("Les séances affichées sont celles à venir, avec le nom du cours (chiots, intermédiaires, confirmés…).")
