# main.py

import streamlit as st
from open_library import search_open_library, extract_work_info
from content_generation import generate_title_description, generate_table_of_contents, generate_section_title, generate_section
from utils import export_to_word
from predefined_lists import PREDEFINED_WORKS, PREDEFINED_AUTHORS
import markdown
from bs4 import BeautifulSoup
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="Generador de Estudios de Obras Clásicas",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Título de la aplicación
st.title("Generador de Estudios de Obras Clásicas")

# Descripción de la aplicación
st.markdown("""
Esta aplicación genera automáticamente estudios detallados de grandes obras clásicas en campos como la literatura, filosofía, política, entre otros.
Puedes seleccionar una obra de una lista predefinida o ingresar una obra y autor personalizados. Además, puedes generar secciones de análisis una por una, lo que te permite pausar el proceso en cualquier momento. Finalmente, puedes exportar el estudio a un archivo en formato Word, ya sea completo o parcial, con referencias académicas incluidas.
""")

# Inicialización de variables en el estado de la sesión
if 'title' not in st.session_state:
    st.session_state.title = ""
if 'author' not in st.session_state:
    st.session_state.author = ""
if 'description' not in st.session_state:
    st.session_state.description = ""
if 'table_of_contents' not in st.session_state:
    st.session_state.table_of_contents = []
if 'sections' not in st.session_state:
    st.session_state.sections = []  # Lista de diccionarios: [{'number': 1, 'title': 'Título', 'content': 'Contenido'}, ...]
if 'current_section' not in st.session_state:
    st.session_state.current_section = 1
if 'total_sections' not in st.session_state:
    st.session_state.total_sections = 10  # Total de secciones, ajustable según necesidades
if 'markdown_content' not in st.session_state:
    st.session_state.markdown_content = ""
if 'generation_complete' not in st.session_state:
    st.session_state.generation_complete = False
if 'selected_section' not in st.session_state:
    st.session_state.selected_section = None
if 'references' not in st.session_state:
    st.session_state.references = []  # Lista de referencias académicas
if 'work_type' not in st.session_state:
    st.session_state.work_type = ""  # Tipo de obra: literaria, filosófica, política, etc.

# Función para reiniciar el estado de la sesión
def reset_session():
    st.session_state.title = ""
    st.session_state.author = ""
    st.session_state.description = ""
    st.session_state.table_of_contents = []
    st.session_state.sections = []
    st.session_state.current_section = 1
    st.session_state.markdown_content = ""
    st.session_state.generation_complete = False
    st.session_state.selected_section = None
    st.session_state.references = []
    st.session_state.work_type = ""

# Barra Lateral
with st.sidebar:
    st.header("Menú de Navegación")
    
    # Botón para reiniciar la generación
    if st.button("Reiniciar Generación"):
        reset_session()
        st.success("Estado de la generación reiniciado.")
    
    st.markdown("---")
    
    # Menú desplegable para ver secciones generadas
    if st.session_state.sections:
        selected_section = st.selectbox(
            "Selecciona una sección para ver:",
            [f"Sección {sec['number']}" for sec in st.session_state.sections],
            key="select_section"
        )
        section_index = int(selected_section.split(" ")[1]) - 1
        # Verificar que el índice esté dentro del rango
        if 0 <= section_index < len(st.session_state.sections):
            st.session_state.selected_section = section_index
        else:
            st.error("Sección seleccionada no válida.")
    else:
        st.info("No hay secciones generadas aún.")

# Entrada de usuario para seleccionar una obra predefinida o personalizada
st.header("Selecciona una Obra Clásica")

# Radio buttons para elegir entre lista predefinida o personalizada
selection_type = st.radio(
    "¿Deseas seleccionar una obra de la lista predefinida o ingresar una personalizada?",
    ("Lista Predefinida", "Personalizada")
)

if selection_type == "Lista Predefinida":
    # Dropdown para seleccionar una obra predefinida
    selected_work = st.selectbox(
        "Selecciona una obra:",
        options=PREDEFINED_WORKS
    )
    # Obtener el autor correspondiente
    selected_author = PREDEFINED_AUTHORS[PREDEFINED_WORKS.index(selected_work)]
    st.write(f"**Autor:** {selected_author}")
    work_title = selected_work
    author = selected_author
else:
    # Entrada de usuario para el título de la obra
    work_title = st.text_input("Ingresa el título de la obra clásica:", "")
    
    # Entrada de usuario para el autor de la obra
    author = st.text_input("Ingresa el autor de la obra:", "")

# Botón para generar título, descripción y tabla de contenidos
if not st.session_state.title:
    if st.button("Generar Estudio"):
        if not work_title or not author:
            st.warning("Por favor, completa tanto el título como el autor de la obra para generar el estudio.")
        else:
            with st.spinner("Buscando información de la obra en Open Library..."):
                work = search_open_library(work_title, author)
                if work:
                    work_info = extract_work_info(work)
                    st.session_state.work_type = work_info['work_type']
                    
                    # Generar título y descripción del estudio
                    title, description = generate_title_description(work_info['title'], work_info['author'], work_info['work_type'], work_info['description'])
                    
                    if title and description:
                        # Generar tabla de contenidos
                        table_of_contents = generate_table_of_contents(work_info['title'], work_info['author'], work_info['work_type'], st.session_state.total_sections)
                        if table_of_contents:
                            st.session_state.title = title
                            st.session_state.description = description
                            st.session_state.table_of_contents = table_of_contents
                            
                            # Construir el contenido Markdown
                            st.session_state.markdown_content = f"# {title}\n\n{description}\n\n## Tabla de Contenidos\n\n"
                            for sec in table_of_contents:
                                st.session_state.markdown_content += f"{sec['number']}. {sec['title']}\n"
                            st.session_state.markdown_content += "\n"
                            
                            # Inicializar la lista de secciones sin contenido
                            st.session_state.sections = [{"number": sec['number'], "title": sec['title'], "content": "", "references": []} for sec in table_of_contents]
                            
                            st.success("Título, descripción y tabla de contenidos generados exitosamente.")
                            st.subheader("Título")
                            st.write(title)
                            st.subheader("Descripción")
                            st.write(description)
                            st.subheader("Tabla de Contenidos")
                            st.write("1. " + "\n2. ".join([sec['title'] for sec in table_of_contents]))
                        else:
                            st.error("No se pudo generar la tabla de contenidos.")
                    else:
                        st.error("No se pudo generar el título y la descripción.")
                else:
                    st.error("No se encontró información sobre la obra proporcionada en Open Library.")
else:
    st.info("El estudio ya ha sido generado. Si deseas generar nuevamente, reinicia la generación.")

# Permitir edición de la información inicial si ya se ha generado
if st.session_state.title and st.session_state.description and st.session_state.table_of_contents:
    st.markdown("---")
    st.header("Editar Información Inicial")
    
    with st.form("edit_initial_info"):
        # Editar Título del Estudio
        edited_title = st.text_input("Título del Estudio:", st.session_state.title)
        
        # Editar Descripción del Estudio
        edited_description = st.text_area("Descripción del Estudio:", st.session_state.description, height=200)
        
        # Editar Tabla de Contenidos
        st.subheader("Tabla de Contenidos")
        edited_table = []
        for sec in st.session_state.sections:
            edited_title_sec = st.text_input(f"Sección {sec['number']}:", sec['title'], key=f"sec_{sec['number']}")
            edited_table.append({"number": sec['number'], "title": edited_title_sec, "content": sec['content'], "references": sec['references']})
        
        submit_edit = st.form_submit_button("Guardar Cambios")
        
        if submit_edit:
            st.session_state.title = edited_title
            st.session_state.description = edited_description
            st.session_state.table_of_contents = edited_table
            st.session_state.sections = edited_table
            # Reconstruir el contenido Markdown
            st.session_state.markdown_content = f"# {st.session_state.title}\n\n{st.session_state.description}\n\n## Tabla de Contenidos\n\n"
            for sec in st.session_state.table_of_contents:
                st.session_state.markdown_content += f"{sec['number']}. {sec['title']}\n"
            st.session_state.markdown_content += "\n"
            st.success("Información inicial actualizada exitosamente.")

# Mostrar la sección para generar análisis solo si el título, descripción y tabla de contenidos han sido generados
if st.session_state.title and st.session_state.description and st.session_state.table_of_contents:
    st.markdown("---")
    st.header("Generación de Secciones de Análisis")

    # Barra de progreso
    generated_sections = len([sec for sec in st.session_state.sections if sec['content']])
    progress = generated_sections / st.session_state.total_sections
    progress_bar = st.progress(progress)

    # Botón para regenerar la sección seleccionada
    if st.session_state.selected_section is not None:
        with st.container():
            section = st.session_state.sections[st.session_state.selected_section]
            if section['title']:
                st.subheader(f"Sección {section['number']}: {section['title']}")
            else:
                st.subheader(f"Sección {section['number']}")
            if section['content']:
                # Mostrar contenido de la sección sin las referencias para evitar redundancia
                if "Referencias" in section['content']:
                    main_content, ref_content = section['content'].split("Referencias", 1)
                    st.markdown(main_content)
                    with st.expander("Ver Referencias"):
                        st.markdown(ref_content)
                else:
                    st.markdown(section['content'])
            else:
                st.info("Esta sección aún no ha sido generada.")
            if st.button("Regenerar Sección"):
                with st.spinner(f"Regenerando sección {section['number']}..."):
                    sec_num = section['number']
                    # Generar un nuevo título para la sección
                    new_title = generate_section_title(st.session_state.title, st.session_state.author, st.session_state.work_type, sec_num)
                    if not new_title:
                        st.error(f"No se pudo generar el título para la sección {sec_num}.")
                    else:
                        # Generar contenido para la sección
                        new_content = generate_section(st.session_state.title, st.session_state.author, st.session_state.work_type, sec_num)
                        if new_content:
                            # Extraer referencias del nuevo contenido
                            new_references = extract_references(new_content)
                            # Actualizar la sección con el nuevo título, contenido y referencias
                            st.session_state.sections[st.session_state.selected_section]['title'] = new_title
                            st.session_state.sections[st.session_state.selected_section]['content'] = new_content
                            st.session_state.sections[st.session_state.selected_section]['references'] = new_references
                            
                            # Agregar referencias al estado global de referencias si no están duplicadas
                            for ref in new_references:
                                if ref not in st.session_state.references:
                                    st.session_state.references.append(ref)
                            
                            # Actualizar el contenido Markdown
                            if "Referencias" in section['content']:
                                chapter_heading_old = f"## Sección {sec_num}: " + (section['title'] if section['title'] else f"Sección {sec_num}") + "\n\n"
                                chapter_main_old, _ = section['content'].split("Referencias", 1)
                            else:
                                chapter_heading_old = f"## Sección {sec_num}: " + (section['title'] if section['title'] else f"Sección {sec_num}") + "\n\n"
                                chapter_main_old = section['content']
                            
                            chapter_heading_new = f"## Sección {sec_num}: {new_title}\n\n"
                            chapter_content_new = new_content + "\n\n"
                            
                            # Reemplazar en markdown_content
                            st.session_state.markdown_content = st.session_state.markdown_content.replace(
                                chapter_heading_old + chapter_main_old,
                                chapter_heading_new + chapter_content_new
                            )
                            
                            st.success(f"Sección {sec_num} regenerada exitosamente.")
                            # Actualizar la barra de progreso si la sección antes no tenía contenido
                            if not section['content']:
                                generated_sections += 1
                                progress = generated_sections / st.session_state.total_sections
                                progress_bar.progress(progress)
                        else:
                            st.error(f"No se pudo generar el contenido para la sección {sec_num}.")

    # Botón para generar la siguiente sección
    if st.session_state.current_section <= st.session_state.total_sections:
        if st.button("Generar Siguiente Sección"):
            with st.spinner(f"Generando sección {st.session_state.current_section}..."):
                section = st.session_state.sections[st.session_state.current_section - 1]
                if not section['content']:
                    # Generar título para la sección
                    generated_title = generate_section_title(st.session_state.title, st.session_state.author, st.session_state.work_type, st.session_state.current_section)
                    if not generated_title:
                        st.error(f"No se pudo generar el título para la sección {st.session_state.current_section}.")
                    else:
                        # Generar contenido para la sección
                        generated_content = generate_section(st.session_state.title, st.session_state.author, st.session_state.work_type, st.session_state.current_section)
                        if generated_content:
                            # Extraer referencias del contenido generado
                            generated_references = extract_references(generated_content)
                            # Actualizar la sección con título, contenido y referencias
                            st.session_state.sections[st.session_state.current_section - 1]['title'] = generated_title
                            st.session_state.sections[st.session_state.current_section - 1]['content'] = generated_content
                            st.session_state.sections[st.session_state.current_section - 1]['references'] = generated_references
                            
                            # Agregar referencias al estado global de referencias si no están duplicadas
                            for ref in generated_references:
                                if ref not in st.session_state.references:
                                    st.session_state.references.append(ref)
                            
                            # Agregar al contenido Markdown
                            section_heading = f"## Sección {st.session_state.current_section}: {generated_title}\n\n"
                            section_content = generated_content + "\n\n"
                            st.session_state.markdown_content += f"{section_heading}{section_content}"
                            
                            st.success(f"Sección {st.session_state.current_section} generada exitosamente.")
                            st.session_state.current_section += 1
                            
                            # Actualizar la barra de progreso
                            generated_sections += 1
                            progress = generated_sections / st.session_state.total_sections
                            progress_bar.progress(progress)
                        else:
                            st.error(f"No se pudo generar el contenido para la sección {st.session_state.current_section}.")
                else:
                    st.info(f"La sección {st.session_state.current_section} ya ha sido generada.")

    # Actualizar la barra de progreso hasta completar
    if len([sec for sec in st.session_state.sections if sec['content']]) == st.session_state.total_sections:
        st.session_state.generation_complete = True

    # Botones para exportar a Word
    if st.session_state.sections:
        with st.spinner("Preparando la exportación..."):
            # Exportar contenido parcial
            partial_markdown = f"# {st.session_state.title}\n\n{st.session_state.description}\n\n## Tabla de Contenidos\n\n"
            for sec in st.session_state.sections:
                if sec['content']:
                    partial_markdown += f"{sec['number']}. {sec['title']}\n"
            partial_markdown += "\n"
            for sec in st.session_state.sections:
                if sec['content']:
                    partial_markdown += f"## Sección {sec['number']}: {sec['title']}\n\n{sec['content']}\n\n"
                else:
                    break  # Solo incluir secciones generadas hasta el momento
            # Agregar referencias al final si hay
            if st.session_state.references:
                partial_markdown += "## Referencias\n\n"
                for ref in st.session_state.references:
                    partial_markdown += f"{ref}\n"
            partial_word_file = export_to_word(partial_markdown, st.session_state.references)
            
            # Exportar contenido completo
            if st.session_state.generation_complete:
                complete_markdown = st.session_state.markdown_content
                # Agregar todas las referencias al final
                complete_markdown += "\n## Referencias\n\n"
                for ref in st.session_state.references:
                    complete_markdown += f"{ref}\n"
                complete_word_file = export_to_word(complete_markdown, st.session_state.references)
                st.success("Preparado para descargar el estudio completo.")
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
                    label="Descargar Estudio Completo en Word",
                    data=complete_word_file,
                    file_name=f"{st.session_state.title.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

    # Opcional: Mostrar todo el contenido generado
    with st.expander("Mostrar Contenido Completo"):
        st.markdown(st.session_state.markdown_content)
