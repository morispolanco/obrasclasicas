import streamlit as st
import requests
import markdown
from bs4 import BeautifulSoup
from docx import Document
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="Generador de Manual Universitario",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Título de la aplicación
st.title("Generador de Manual Universitario")

# Descripción de la aplicación
st.markdown("""
Esta aplicación genera automáticamente el título, descripción, tabla de contenidos y contenido de un manual universitario sobre el tema proporcionado. 
Puedes generar los capítulos uno por uno, lo que te permite pausar el proceso en cualquier momento. Además, puedes editar la información inicial y regenerar capítulos específicos si lo deseas.
Finalmente, puedes exportar el manual a un archivo en formato Word, ya sea completo o parcial.
""")

# Inicialización de variables en el estado de la sesión
if 'title' not in st.session_state:
    st.session_state.title = ""
if 'description' not in st.session_state:
    st.session_state.description = ""
if 'table_of_contents' not in st.session_state:
    st.session_state.table_of_contents = []
if 'chapters' not in st.session_state:
    st.session_state.chapters = []  # Lista de diccionarios: [{'number': 1, 'title': 'Título', 'content': 'Contenido'}, ...]
if 'current_chapter' not in st.session_state:
    st.session_state.current_chapter = 1
if 'total_chapters' not in st.session_state:
    st.session_state.total_chapters = 12  # Total de capítulos
if 'markdown_content' not in st.session_state:
    st.session_state.markdown_content = ""
if 'generation_complete' not in st.session_state:
    st.session_state.generation_complete = False
if 'selected_chapter' not in st.session_state:
    st.session_state.selected_chapter = None

# Función para reiniciar el estado de la sesión
def reset_session():
    st.session_state.title = ""
    st.session_state.description = ""
    st.session_state.table_of_contents = []
    st.session_state.chapters = []
    st.session_state.current_chapter = 1
    st.session_state.markdown_content = ""
    st.session_state.generation_complete = False
    st.session_state.selected_chapter = None

# Función para llamar a la API de OpenRouter
def call_openrouter_api(messages, model="qwen/qwen-2.5-72b-instruct"):
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
        st.error(f"Error en la API: {err}")
        return None
    except Exception as e:
        st.error(f"Error inesperado: {e}")
        return None

# Función para generar título y descripción
def generate_title_description(topic):
    prompt = f"""Genera un título y una descripción para un manual universitario sobre el siguiente tema. El manual debe ser educativo y claro.
    
Tema: {topic}

Formato de respuesta:
Título: [Título del manual]
Descripción: [Descripción del manual]
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
            if line.startswith("Título:"):
                title = line.replace("Título:", "").strip()
            elif line.startswith("Descripción:"):
                description = line.replace("Descripción:", "").strip()
        return title, description
    return None, None

# Función para generar la tabla de contenidos
def generate_table_of_contents(topic, total_chapters):
    prompt = f"""Genera una tabla de contenidos para un manual universitario sobre el siguiente tema. La tabla debe contener {total_chapters} capítulos con títulos descriptivos y relevantes.
    
Tema: {topic}

Formato de respuesta:
Capítulo 1: [Título del Capítulo 1]
Capítulo 2: [Título del Capítulo 2]
...
Capítulo {total_chapters}: [Título del Capítulo {total_chapters}]
"""
    messages = [
        {"role": "user", "content": prompt}
    ]
    response = call_openrouter_api(messages)
    if response:
        table = []
        for line in response.split('\n'):
            if line.startswith("Capítulo"):
                parts = line.split(":")
                if len(parts) >= 2:
                    chap_num = int(parts[0].split(" ")[1])
                    chap_title = parts[1].strip()
                    table.append({"number": chap_num, "title": chap_title, "content": ""})
        return table
    return None

# Función para generar un título de capítulo
def generate_chapter_title(topic, chapter_num):
    prompt = f"""Genera un título único y descriptivo para el capítulo {chapter_num} de un manual universitario sobre el siguiente tema.
    
Tema: {topic}

Formato de respuesta:
Título del Capítulo {chapter_num}: [Título Único]
"""
    messages = [
        {"role": "user", "content": prompt}
    ]
    response = call_openrouter_api(messages)
    if response:
        title = ""
        for line in response.split('\n'):
            if line.startswith(f"Título del Capítulo {chapter_num}:"):
                title = line.replace(f"Título del Capítulo {chapter_num}:", "").strip()
                break
        return title
    return None

# Función para generar un capítulo
def generate_chapter(topic, chapter_num):
    prompt = f"""Escribe el contenido del capítulo {chapter_num} para un manual universitario sobre el siguiente tema.
    
Tema: {topic}

El capítulo debe tener aproximadamente 3000 tokens y estar estructurado de manera clara y educativa.
"""
    messages = [
        {"role": "user", "content": prompt}
    ]
    response = call_openrouter_api(messages)
    return response

# Función para exportar a Word
def export_to_word(markdown_content):
    # Convertir Markdown a HTML
    html = markdown.markdown(markdown_content)
    
    # Parsear HTML con BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Crear un documento de Word
    doc = Document()
    
    # Iterar sobre los elementos del HTML y agregarlos al documento
    for element in soup.descendants:
        if isinstance(element, str):
            continue  # Ignorar cadenas de texto directas
        if element.name == 'h1':
            doc.add_heading(element.get_text(), level=1)
        elif element.name == 'h2':
            doc.add_heading(element.get_text(), level=2)
        elif element.name == 'h3':
            doc.add_heading(element.get_text(), level=3)
        elif element.name == 'p':
            doc.add_paragraph(element.get_text())
    
    # Guardar el documento en un objeto BytesIO
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- Barra Lateral ---
with st.sidebar:
    st.header("Menú de Navegación")
    
    # Botón para reiniciar la generación
    if st.button("Reiniciar Generación"):
        reset_session()
        st.success("Estado de la generación reiniciado.")
    
    st.markdown("---")
    
    # Menú desplegable para ver capítulos generados
    if st.session_state.chapters:
        selected_chapter = st.selectbox(
            "Selecciona un capítulo para ver:",
            [f"Capítulo {chap['number']}" for chap in st.session_state.chapters],
            key="select_chapter"
        )
        chapter_index = int(selected_chapter.split(" ")[1]) - 1
        # Verificar que el índice esté dentro del rango
        if 0 <= chapter_index < len(st.session_state.chapters):
            st.session_state.selected_chapter = chapter_index
        else:
            st.error("Capítulo seleccionado no válido.")
    else:
        st.info("No hay capítulos generados aún.")

# --- Sección Principal ---

# Entrada de usuario para el tema
topic = st.text_input("Ingresa el tema de tu manual universitario:", "")

# Botón para generar título, descripción y tabla de contenidos
if not st.session_state.title:
    if st.button("Generar Título, Descripción y Tabla de Contenidos"):
        if not topic:
            st.warning("Por favor, ingresa un tema para generar el manual.")
        else:
            with st.spinner("Generando título, descripción y tabla de contenidos..."):
                title, description = generate_title_description(topic)
                if title and description:
                    table_of_contents = generate_table_of_contents(topic, st.session_state.total_chapters)
                    if table_of_contents:
                        st.session_state.title = title
                        st.session_state.description = description
                        st.session_state.table_of_contents = table_of_contents
                        # Construir el contenido Markdown
                        st.session_state.markdown_content = f"# {title}\n\n{description}\n\n## Tabla de Contenidos\n\n"
                        for chap in table_of_contents:
                            st.session_state.markdown_content += f"{chap['number']}. {chap['title']}\n"
                        st.session_state.markdown_content += "\n"
                        # Inicializar la lista de capítulos sin contenido
                        st.session_state.chapters = [{"number": chap['number'], "title": chap['title'], "content": ""} for chap in table_of_contents]
                        st.success("Título, descripción y tabla de contenidos generados exitosamente.")
                        st.subheader("Título")
                        st.write(title)
                        st.subheader("Descripción")
                        st.write(description)
                        st.subheader("Tabla de Contenidos")
                        st.write("1. " + "\n2. ".join([chap['title'] for chap in table_of_contents]))
                    else:
                        st.error("No se pudo generar la tabla de contenidos.")
                else:
                    st.error("No se pudo generar el título y la descripción.")
else:
    st.info("El título, descripción y tabla de contenidos ya han sido generados. Si deseas generar nuevamente, reinicia la generación.")

# Permitir edición de la información inicial si ya se ha generado
if st.session_state.title and st.session_state.description and st.session_state.table_of_contents:
    st.markdown("---")
    st.header("Editar Información Inicial")
    
    with st.form("edit_initial_info"):
        # Editar Título
        edited_title = st.text_input("Título del Manual:", st.session_state.title)
        
        # Editar Descripción
        edited_description = st.text_area("Descripción del Manual:", st.session_state.description, height=200)
        
        # Editar Tabla de Contenidos
        st.subheader("Tabla de Contenidos")
        edited_table = []
        for chap in st.session_state.chapters:
            edited_title_chap = st.text_input(f"Capítulo {chap['number']}:", chap['title'], key=f"chap_{chap['number']}")
            edited_table.append({"number": chap['number'], "title": edited_title_chap, "content": chap['content']})
        
        submit_edit = st.form_submit_button("Guardar Cambios")
        
        if submit_edit:
            st.session_state.title = edited_title
            st.session_state.description = edited_description
            st.session_state.table_of_contents = edited_table
            st.session_state.chapters = edited_table
            # Reconstruir el contenido Markdown
            st.session_state.markdown_content = f"# {st.session_state.title}\n\n{st.session_state.description}\n\n## Tabla de Contenidos\n\n"
            for chap in st.session_state.table_of_contents:
                st.session_state.markdown_content += f"{chap['number']}. {chap['title']}\n"
            st.session_state.markdown_content += "\n"
            st.success("Información inicial actualizada exitosamente.")

# Mostrar la sección para generar capítulos solo si el título, descripción y tabla de contenidos han sido generados
if st.session_state.title and st.session_state.description and st.session_state.table_of_contents:
    st.markdown("---")
    st.header("Generación de Capítulos")

    # Barra de progreso
    generated_chapters = len([chap for chap in st.session_state.chapters if chap['content']])
    progress = generated_chapters / st.session_state.total_chapters
    progress_bar = st.progress(progress)

    # Botón para regenerar el capítulo seleccionado
    if st.session_state.selected_chapter is not None:
        with st.container():
            chapter = st.session_state.chapters[st.session_state.selected_chapter]
            if chapter['title']:
                st.subheader(f"Capítulo {chapter['number']}: {chapter['title']}")
            else:
                st.subheader(f"Capítulo {chapter['number']}")
            if chapter['content']:
                st.markdown(chapter['content'])
            else:
                st.info("Este capítulo aún no ha sido generado.")
            if st.button("Regenerar Capítulo"):
                with st.spinner(f"Regenerando capítulo {chapter['number']}..."):
                    chapter_num = chapter['number']
                    # Generar un nuevo título para el capítulo
                    new_title = generate_chapter_title(topic, chapter_num)
                    if not new_title:
                        st.error(f"No se pudo generar el título para el capítulo {chapter_num}.")
                    else:
                        # Generar el contenido del capítulo
                        new_content = generate_chapter(topic, chapter_num)
                        if new_content:
                            # Actualizar el capítulo con el nuevo título y contenido
                            st.session_state.chapters[st.session_state.selected_chapter]['title'] = new_title
                            st.session_state.chapters[st.session_state.selected_chapter]['content'] = new_content
                            
                            # Actualizar el contenido Markdown
                            # Primero, eliminar el contenido anterior del capítulo en markdown_content
                            chapter_heading_old = f"## Capítulo {chapter_num}: " + (chapter['title'] if chapter['title'] else f"Capítulo {chapter_num}") + "\n\n"
                            chapter_heading_new = f"## Capítulo {chapter_num}: {new_title}\n\n"
                            chapter_content_new = new_content + "\n\n"

                            # Reemplazar en markdown_content
                            st.session_state.markdown_content = st.session_state.markdown_content.replace(chapter_heading_old, chapter_heading_new)
                            # Luego, reemplazar el contenido
                            st.session_state.markdown_content = st.session_state.markdown_content.replace(chapter_heading_new + chapter['content'] + "\n\n", chapter_heading_new + chapter_content_new)

                            # Actualizar la tabla de contenidos si el título ha cambiado
                            st.session_state.table_of_contents[chapter_num - 1]['title'] = new_title
                            # Actualizar la lista de capítulos
                            st.session_state.chapters[chapter_num - 1]['title'] = new_title

                            st.success(f"Capítulo {chapter_num} regenerado exitosamente.")
                            # Actualizar la barra de progreso si el capítulo antes no tenía contenido
                            if not chapter['content']:
                                generated_chapters += 1
                                progress = generated_chapters / st.session_state.total_chapters
                                progress_bar.progress(progress)
                        else:
                            st.error(f"No se pudo generar el contenido para el capítulo {chapter_num}.")

    # Botón para generar el siguiente capítulo
    if st.session_state.current_chapter <= st.session_state.total_chapters:
        if st.button("Generar Siguiente Capítulo"):
            with st.spinner(f"Generando capítulo {st.session_state.current_chapter}..."):
                chapter = st.session_state.chapters[st.session_state.current_chapter - 1]
                if not chapter['content']:
                    # Generar título para el capítulo
                    generated_title = generate_chapter_title(topic, st.session_state.current_chapter)
                    if not generated_title:
                        st.error(f"No se pudo generar el título para el capítulo {st.session_state.current_chapter}.")
                    else:
                        # Generar contenido para el capítulo
                        generated_content = generate_chapter(topic, st.session_state.current_chapter)
                        if generated_content:
                            # Actualizar el capítulo con título y contenido
                            st.session_state.chapters[st.session_state.current_chapter - 1]['title'] = generated_title
                            st.session_state.chapters[st.session_state.current_chapter - 1]['content'] = generated_content
                            
                            # Agregar al contenido Markdown
                            chapter_heading = f"## Capítulo {st.session_state.current_chapter}: {generated_title}\n\n"
                            chapter_content = generated_content + "\n\n"
                            st.session_state.markdown_content += f"{chapter_heading}{chapter_content}"
                            
                            st.success(f"Capítulo {st.session_state.current_chapter} generado exitosamente.")
                            st.session_state.current_chapter += 1
                            
                            # Actualizar la barra de progreso
                            generated_chapters += 1
                            progress = generated_chapters / st.session_state.total_chapters
                            progress_bar.progress(progress)
                        else:
                            st.error(f"No se pudo generar el contenido para el capítulo {st.session_state.current_chapter}.")
                else:
                    st.info(f"El capítulo {st.session_state.current_chapter} ya ha sido generado.")

    # Actualizar la barra de progreso hasta completar
    if len([chap for chap in st.session_state.chapters if chap['content']]) == st.session_state.total_chapters:
        st.session_state.generation_complete = True

    # Botones para exportar a Word
    if st.session_state.chapters:
        with st.spinner("Preparando la exportación..."):
            # Exportar contenido parcial
            partial_markdown = f"# {st.session_state.title}\n\n{st.session_state.description}\n\n## Tabla de Contenidos\n\n"
            for chap in st.session_state.chapters:
                if chap['content']:
                    partial_markdown += f"{chap['number']}. {chap['title']}\n"
            partial_markdown += "\n"
            for chap in st.session_state.chapters:
                if chap['content']:
                    partial_markdown += f"## Capítulo {chap['number']}: {chap['title']}\n\n{chap['content']}\n\n"
                else:
                    break  # Solo incluir capítulos generados hasta el momento
            partial_word_file = export_to_word(partial_markdown)
            
            # Exportar contenido completo
            if st.session_state.generation_complete:
                complete_markdown = st.session_state.markdown_content
                complete_word_file = export_to_word(complete_markdown)
                st.success("Preparado para descargar el manual completo.")
            else:
                complete_word_file = None

            # Botón para descargar contenido parcial en Word
            st.download_button(
                label="Descargar Contenido Parcial en Word",
                data=partial_word_file,
                file_name=f"{st.session_state.title.replace(' ', '_')}_Parcial.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
            # Botón para descargar contenido completo en Word (solo si está completo)
            if st.session_state.generation_complete:
                st.download_button(
                    label="Descargar Manual Completo en Word",
                    data=complete_word_file,
                    file_name=f"{st.session_state.title.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

    # Opcional: Mostrar todo el contenido generado
    with st.expander("Mostrar Contenido Completo"):
        st.markdown(st.session_state.markdown_content)
