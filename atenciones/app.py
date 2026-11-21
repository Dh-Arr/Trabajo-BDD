"""Aplicación de atenciones médicas (Streamlit + PostgreSQL).

Ejecutar:  streamlit run app.py
"""
import datetime as dt

import pandas as pd
import psycopg2
import streamlit as st

from db import consultar, ejecutar

st.set_page_config(page_title="Atenciones médicas", layout="wide")

# ---------------------------------------------------------------- consultas
SQL_PACIENTES = "SELECT id_paciente, rut, nombre, telefono FROM paciente ORDER BY id_paciente"
SQL_MEDICOS = "SELECT id_medico, nombre, especialidad, telefono FROM medico ORDER BY id_medico"
SQL_ATENCIONES = """
    SELECT a.id_atencion, p.nombre AS paciente, m.nombre AS medico,
           a.fecha_atencion, a.fecha_alta, a.diagnostico, a.costo
    FROM atencion a
    JOIN paciente p ON p.id_paciente = a.id_paciente
    JOIN medico   m ON m.id_medico   = a.id_medico
    ORDER BY a.id_atencion
"""
# Punto 5: atenciones vigentes = sin fecha de alta
SQL_VIGENTES = """
    SELECT p.nombre AS nombre_paciente, m.nombre AS nombre_medico, m.especialidad
    FROM atencion a JOIN paciente p ON a.id_paciente = p.id_paciente
    JOIN medico m ON a.id_medico = m.id_medico
    WHERE a.fecha_alta IS NULL;
"""


# ---------------------------------------------------------------- utilidades
def flash(mensaje):
    """Guarda un mensaje para mostrarlo tras recargar la página."""
    st.session_state["flash"] = mensaje
    st.rerun()


def guardar(sql, params, mensaje):
    try:
        ejecutar(sql, params)
    except psycopg2.Error as e:
        st.error(f"Error de base de datos: {e.pgerror or e}")
        return
    flash(mensaje)


def texto_o_none(valor):
    valor = valor.strip()
    return valor or None


def selector_fk(etiqueta, df, col_id, col_texto, actual=None, key=None):
    """Lista desplegable cargada desde la BD; devuelve el id elegido."""
    ids = df[col_id].tolist()
    textos = dict(zip(df[col_id], df[col_texto]))
    indice = ids.index(actual) if actual in ids else 0
    return st.selectbox(etiqueta, ids, index=indice,
                        format_func=lambda i: f"{i} - {textos[i]}", key=key)


# ---------------------------------------------------------------- INGRESAR
def ingresar_paciente():
    with st.form("form_paciente", clear_on_submit=True):
        rut = st.text_input("RUT *")
        nombre = st.text_input("Nombre *")
        telefono = st.text_input("Teléfono")
        if st.form_submit_button("Guardar paciente"):
            if not rut.strip() or not nombre.strip():
                st.warning("RUT y nombre son obligatorios.")
            else:
                guardar("INSERT INTO paciente (rut, nombre, telefono) VALUES (%s, %s, %s)",
                        (rut.strip(), nombre.strip(), texto_o_none(telefono)),
                        "Paciente ingresado correctamente.")


def ingresar_medico():
    with st.form("form_medico", clear_on_submit=True):
        nombre = st.text_input("Nombre *")
        especialidad = st.text_input("Especialidad *")
        telefono = st.text_input("Teléfono")
        if st.form_submit_button("Guardar médico"):
            if not nombre.strip() or not especialidad.strip():
                st.warning("Nombre y especialidad son obligatorios.")
            else:
                guardar("INSERT INTO medico (nombre, especialidad, telefono) VALUES (%s, %s, %s)",
                        (nombre.strip(), especialidad.strip(), texto_o_none(telefono)),
                        "Médico ingresado correctamente.")


def ingresar_atencion():
    pacientes, medicos = consultar(SQL_PACIENTES), consultar(SQL_MEDICOS)
    if pacientes.empty or medicos.empty:
        st.info("Primero debes ingresar al menos un paciente y un médico.")
        return
    with st.form("form_atencion", clear_on_submit=True):
        id_paciente = selector_fk("Paciente *", pacientes, "id_paciente", "nombre")
        id_medico = selector_fk("Médico *", medicos, "id_medico", "nombre")
        fecha_atencion = st.date_input("Fecha de atención *", value=dt.date.today())
        con_alta = st.checkbox("Registrar fecha de alta (dejar sin marcar = atención vigente)")
        fecha_alta = st.date_input("Fecha de alta", value=dt.date.today())
        diagnostico = st.text_area("Diagnóstico")
        costo = st.number_input("Costo (opcional)", min_value=0, step=1000, value=0)
        if st.form_submit_button("Guardar atención"):
            alta = fecha_alta if con_alta else None
            if alta and alta < fecha_atencion:
                st.warning("La fecha de alta no puede ser anterior a la fecha de atención.")
            else:
                guardar("""INSERT INTO atencion
                           (id_paciente, id_medico, fecha_atencion, fecha_alta, diagnostico, costo)
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (id_paciente, id_medico, fecha_atencion, alta,
                         texto_o_none(diagnostico), costo),
                        "Atención ingresada correctamente.")


def pagina_ingresar():
    st.header("Ingresar datos")
    tab_p, tab_m, tab_a = st.tabs(["Paciente", "Médico", "Atención"])
    with tab_p:
        ingresar_paciente()
    with tab_m:
        ingresar_medico()
    with tab_a:
        ingresar_atencion()


# ---------------------------------------------------------------- MODIFICAR
def elegir_registro(df, col_id, texto, etiqueta):
    """Muestra los datos existentes y deja elegir uno para editar."""
    st.subheader("Datos existentes")
    st.dataframe(df, use_container_width=True, hide_index=True)
    if df.empty:
        st.info("No hay registros para modificar.")
        return None
    return st.selectbox(etiqueta, df[col_id].tolist(),
                        format_func=lambda i: f"{i} - {texto[i]}")


def modificar_paciente():
    df = consultar(SQL_PACIENTES)
    id_sel = elegir_registro(df, "id_paciente", dict(zip(df.id_paciente, df.nombre)),
                             "Selecciona el paciente a modificar")
    if id_sel is None:
        return
    fila = df[df.id_paciente == id_sel].iloc[0]
    with st.form(f"mod_paciente_{id_sel}"):
        rut = st.text_input("RUT *", value=fila.rut)
        nombre = st.text_input("Nombre *", value=fila.nombre)
        telefono = st.text_input("Teléfono", value=fila.telefono or "")
        if st.form_submit_button("Guardar cambios"):
            if not rut.strip() or not nombre.strip():
                st.warning("RUT y nombre son obligatorios.")
            else:
                guardar("UPDATE paciente SET rut=%s, nombre=%s, telefono=%s WHERE id_paciente=%s",
                        (rut.strip(), nombre.strip(), texto_o_none(telefono), int(id_sel)),
                        "Paciente modificado correctamente.")


def modificar_medico():
    df = consultar(SQL_MEDICOS)
    id_sel = elegir_registro(df, "id_medico", dict(zip(df.id_medico, df.nombre)),
                             "Selecciona el médico a modificar")
    if id_sel is None:
        return
    fila = df[df.id_medico == id_sel].iloc[0]
    with st.form(f"mod_medico_{id_sel}"):
        nombre = st.text_input("Nombre *", value=fila.nombre)
        especialidad = st.text_input("Especialidad *", value=fila.especialidad)
        telefono = st.text_input("Teléfono", value=fila.telefono or "")
        if st.form_submit_button("Guardar cambios"):
            if not nombre.strip() or not especialidad.strip():
                st.warning("Nombre y especialidad son obligatorios.")
            else:
                guardar("UPDATE medico SET nombre=%s, especialidad=%s, telefono=%s WHERE id_medico=%s",
                        (nombre.strip(), especialidad.strip(), texto_o_none(telefono), int(id_sel)),
                        "Médico modificado correctamente.")


def modificar_atencion():
    df = consultar(SQL_ATENCIONES)
    textos = {r.id_atencion: f"{r.paciente} / {r.medico} ({r.fecha_atencion})"
              for r in df.itertuples()}
    id_sel = elegir_registro(df, "id_atencion", textos, "Selecciona la atención a modificar")
    if id_sel is None:
        return
    id_sel = int(id_sel)
    actual = consultar("SELECT * FROM atencion WHERE id_atencion = %s", (id_sel,)).iloc[0]
    pacientes, medicos = consultar(SQL_PACIENTES), consultar(SQL_MEDICOS)
    tiene_alta = actual.fecha_alta is not None and str(actual.fecha_alta) != "NaT"

    with st.form(f"mod_atencion_{id_sel}"):
        id_paciente = selector_fk("Paciente *", pacientes, "id_paciente", "nombre",
                                  actual=actual.id_paciente)
        id_medico = selector_fk("Médico *", medicos, "id_medico", "nombre",
                                actual=actual.id_medico)
        fecha_atencion = st.date_input("Fecha de atención *", value=actual.fecha_atencion)
        con_alta = st.checkbox("Tiene fecha de alta (desmarcar = dejar vigente)", value=tiene_alta)
        fecha_alta = st.date_input("Fecha de alta",
                                   value=actual.fecha_alta if tiene_alta else dt.date.today())
        diagnostico = st.text_area("Diagnóstico", value=actual.diagnostico or "")
        costo_actual = None if pd.isna(actual.costo) else int(actual.costo)
        costo = st.number_input("Costo (opcional)", min_value=0, step=1000, value=costo_actual)
        if st.form_submit_button("Guardar cambios"):
            alta = fecha_alta if con_alta else None
            if alta and alta < fecha_atencion:
                st.warning("La fecha de alta no puede ser anterior a la fecha de atención.")
            else:
                guardar("""UPDATE atencion
                           SET id_paciente=%s, id_medico=%s, fecha_atencion=%s,
                               fecha_alta=%s, diagnostico=%s, costo=%s
                           WHERE id_atencion=%s""",
                        (int(id_paciente), int(id_medico), fecha_atencion, alta,
                         texto_o_none(diagnostico), costo, id_sel),
                        "Atención modificada correctamente.")


def pagina_modificar():
    st.header("Modificar datos")
    tabla = st.radio("Tabla a modificar", ["Paciente", "Médico", "Atención"], horizontal=True)
    {"Paciente": modificar_paciente,
     "Médico": modificar_medico,
     "Atención": modificar_atencion}[tabla]()


# ---------------------------------------------------------------- CONSULTA
def pagina_vigentes():
    st.header("Atenciones vigentes (sin fecha de alta)")
    st.code(SQL_VIGENTES.strip(), language="sql")
    if st.button("Ejecutar consulta", type="primary"):
        try:
            df = consultar(SQL_VIGENTES)
        except psycopg2.Error as e:
            st.error(f"Error de base de datos: {e.pgerror or e}")
            return
        if df.empty:
            st.info("No hay atenciones vigentes.")
        else:
            st.success(f"{len(df)} atención(es) vigente(s).")
            st.dataframe(df, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------- MAIN
st.title("Gestión de atenciones médicas")
pagina = st.sidebar.radio("Menú", ["Ingresar datos", "Modificar datos", "Atenciones vigentes"])

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

try:
    {"Ingresar datos": pagina_ingresar,
     "Modificar datos": pagina_modificar,
     "Atenciones vigentes": pagina_vigentes}[pagina]()
except psycopg2.OperationalError as e:
    st.error(f"No se pudo conectar a PostgreSQL. Revisa db.py o las variables PG*.\n\n{e}")
