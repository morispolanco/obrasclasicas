# content_generation.py

import streamlit as st
import requests

def call_openrouter_api(messages, model="qwen/qwen-2.5-72b-instruct"):
    """
    Llama a la API de OpenRouter para obtener una respuesta basada en los mensajes proporcionados.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}"
    }
    data = {
        "model": model,
        "messages": messages
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except requests.exceptions.HTTPError as err:
        st.error(f"Error en la API de OpenRouter: {err}")
        return None
    except Exception as e:
        st.error(f"Error inesperado en la API de OpenRouter: {e}")
        return None

def generate_title_description(work_title, author, work_type, description):
    """
    Genera un título y una descripción para el estudio basado en la obra.
    """
    prompt = f"""Genera un título y una descripción para un estudio detallado de la siguiente obra clásica. El estudio debe ser educativo, claro y profesional.
    
Título de la obra: {work_title}
Autor: {author}
Tipo de obra: {work_type}
Descripción de la obra: {description}

Formato de respuesta:
Título del Estudio: [Título del estudio]
Descripción: [Descripción del estudio]
"""
    messages = [
        {"role": "user", "content": prompt}
    ]
    response = call_openrouter_api(messages)
    if response:
        # Separar el título y la descripción
        lines = response.split('\n')
        title = ""
        description = ""
        for line in lines:
            if line.startswith("Título del Estudio:"):
                title = line.replace("Título del Estudio:", "").strip()
            elif line.startswith("Descripción:"):
                description = line.replace("Descripción:", "").strip()
        return title, description
    return None, None

def generate_table_of_contents(work_title, author, work_type, total_sections):
    """
    Genera una tabla de contenidos para el estudio basado en la obra.
    """
    prompt = f"""Genera una tabla de contenidos para un estudio detallado de la siguiente obra clásica. La tabla debe contener {total_sections} secciones con títulos descriptivos y relevantes, adaptados al tipo de obra.
    
Título de la obra: {work_title}
Autor: {author}
Tipo de obra: {work_type}

Formato de respuesta:
Sección 1: [Título de la Sección 1]
Sección 2: [Título de la Sección 2]
...
Sección {total_sections}: [Título de la Sección {total_sections}]
"""
    messages = [
        {"role": "user", "content": prompt}
    ]
    response = call_openrouter_api(messages)
    if response:
        table = []
        for line in response.split('\n'):
            if line.startswith("Sección"):
                parts = line.split(":")
                if len(parts) >= 2:
                    try:
                        sec_num = int(parts[0].split(" ")[1])
                        sec_title = parts[1].strip()
                        table.append({"number": sec_num, "title": sec_title, "content": "", "references": []})
                    except ValueError:
                        continue  # Salta líneas que no cumplen el formato esperado
        return table
    return None

def generate_section_title(work_title, author, work_type, section_num):
    """
    Genera un título único y descriptivo para una sección específica del estudio.
    """
    prompt = f"""Genera un título único y descriptivo para la sección {section_num} de un estudio detallado de la siguiente obra clásica.
    
Título de la obra: {work_title}
Autor: {author}
Tipo de obra: {work_type}

Formato de respuesta:
Título de la Sección {section_num}: [Título Único]
"""
    messages = [
        {"role": "user", "content": prompt}
    ]
    response = call_openrouter_api(messages)
    if response:
        title = ""
        for line in response.split('\n'):
            if line.startswith(f"Título de la Sección {section_num}:"):
                title = line.replace(f"Título de la Sección {section_num}:", "").strip()
                break
        return title
    return None

def generate_section(work_title, author, work_type, section_num):
    """
    Genera el contenido detallado para una sección específica del estudio.
    """
    # Definir el tipo de análisis según el tipo de obra
    if work_type.lower() == "literaria":
        analysis_prompt = f"""Escribe el contenido de la sección {section_num} para un estudio detallado de la obra "{work_title}" de {author}.
        
Tipo de obra: Literatura

La sección debe incluir análisis de personajes, técnicas narrativas, contexto histórico, biografía del autor y cualquier otro análisis relevante.

El contenido debe ser claro, educativo y bien estructurado, con aproximadamente 3000 tokens. Incluye referencias académicas pertinentes al final de la sección en formato APA.
"""
    elif work_type.lower() == "filosófica":
        analysis_prompt = f"""Escribe el contenido de la sección {section_num} para un estudio detallado de la obra "{work_title}" de {author}.
        
Tipo de obra: Filosofía

La sección debe incluir estudio del autor, contexto histórico, ideas principales, discusiones académicas en torno a las ideas presentadas y cualquier otro análisis relevante.

El contenido debe ser claro, educativo y bien estructurado, con aproximadamente 3000 tokens. Incluye referencias académicas pertinentes al final de la sección en formato APA.
"""
    elif work_type.lower() == "política":
        analysis_prompt = f"""Escribe el contenido de la sección {section_num} para un estudio detallado de la obra "{work_title}" de {author}.
        
Tipo de obra: Política

La sección debe incluir estudio del autor, contexto histórico, teorías políticas presentadas, impacto en la sociedad, discusiones académicas y cualquier otro análisis relevante.

El contenido debe ser claro, educativo y bien estructurado, con aproximadamente 3000 tokens. Incluye referencias académicas pertinentes al final de la sección en formato APA.
"""
    else:
        analysis_prompt = f"""Escribe el contenido de la sección {section_num} para un estudio detallado de la obra "{work_title}" de {author}.
        
Tipo de obra: {work_type}

La sección debe incluir análisis detallado relevante al tipo de obra, estructurado de manera clara y educativa, con aproximadamente 3000 tokens. Incluye referencias académicas pertinentes al final de la sección en formato APA.
"""
    
    messages = [
        {"role": "user", "content": analysis_prompt}
    ]
    response = call_openrouter_api(messages)
    return response
