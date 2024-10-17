# open_library.py

import requests
import streamlit as st

def search_open_library(title, author):
    """
    Busca una obra en Open Library usando el título y el autor.
    Retorna la información de la obra si se encuentra, de lo contrario, retorna None.
    """
    query = f"title:{title} author:{author}"
    url = f"https://openlibrary.org/search.json?q={requests.utils.quote(query)}&limit=1"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data['numFound'] > 0:
            work = data['docs'][0]
            return work
        else:
            return None
    except requests.exceptions.HTTPError as err:
        st.error(f"Error al consultar Open Library: {err}")
        return None
    except Exception as e:
        st.error(f"Error inesperado al consultar Open Library: {e}")
        return None

def extract_work_info(work):
    """
    Extrae información relevante de la obra obtenida de Open Library.
    """
    title = work.get('title', 'Título no disponible')
    authors = work.get('author_name', ['Autor no disponible'])
    author = ", ".join(authors)
    subjects = work.get('subject', [])
    description = work.get('first_sentence', ['Descripción no disponible'])[0] if work.get('first_sentence') else 'Descripción no disponible'
    
    # Intentar determinar el tipo de obra basado en los géneros o temas
    work_type = determine_work_type_from_subjects(subjects)
    
    return {
        'title': title,
        'author': author,
        'subjects': subjects,
        'description': description,
        'work_type': work_type
    }

def determine_work_type_from_subjects(subjects):
    """
    Determina el tipo de obra basado en los géneros (subjects) de Open Library.
    """
    literatura_keywords = ["novel", "poetry", "drama", "short story", "literature"]
    filosofia_keywords = ["philosophy", "thought", "idea", "ethics", "metaphysics", "ontology"]
    politica_keywords = ["politics", "political theory", "state", "government", "society"]

    combined_subjects = " ".join(subjects).lower()

    if any(keyword in combined_subjects for keyword in literatura_keywords):
        return "Literaria"
    elif any(keyword in combined_subjects for keyword in filosofia_keywords):
        return "Filosófica"
    elif any(keyword in combined_subjects for keyword in politica_keywords):
        return "Política"
    else:
        return "Otro"
