if st.button("S'inscrire à la séance"):

    seance = next(s for s in seances if s["id"] == seance_id)

    data = {
        "membre_id": membre_id,
        "chien_id": chien_id,
        "seance_id": seance_id,

        "cours_id": seance.get("cours_id"),
        "cours_nom": map_cours.get(seance.get("cours_id")),
        "date_seance": seance["date_seance"],
        "heure_debut": seance.get("heure_debut"),

        "type": "membre",
        "traitee": False,
        "acceptee": True   # un membre est toujours accepté
    }

    supabase.table("preinscriptions").insert(data).execute()
    st.success("Votre préinscription a été enregistrée !")
