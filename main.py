import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from supabase import create_client, Client

# --- DATOS DE CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CDCE RIBAS V2", layout="wide", page_icon="📊")

# --- CONFIGURACIÓN DE MARCA DE AGUA (FONDO) ---
import base64

def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return None

bin_str = get_base64("static/mppe.png")
if bin_str:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-attachment: fixed;
            background-size: 40%;
            background-repeat: no-repeat;
            background-position: center;
            background-color: rgba(255, 255, 255, 0.70);
            background-blend-mode: overlay;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .card {
        background-color: #ffffff !important;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        margin-bottom: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- VENTANAS DIALOG ---
@st.dialog("Configuración de Perfil")
def ventana_configuracion():
    st.write("Introduzca su nueva contraseña:")
    nueva_p = st.text_input("Nueva Contraseña", type="password")
    confirmar_p = st.text_input("Confirmar Nueva Contraseña", type="password")
    if st.button("Guardar Cambios", use_container_width=True):
        if len(nueva_p) < 6: st.error("Mínimo 6 caracteres.")
        elif nueva_p != confirmar_p: st.error("No coinciden.")
        else:
            try:
                supabase.table("usuarios").update({"password": nueva_p}).eq("id", st.session_state["user_data"]['id']).execute()
                st.success("✅ ¡Actualizada!")
            except: st.error("Error al conectar.")

@st.dialog("📊 Resumen de Cierre: Marzo")
def mostrar_resumen_supervisor():
    try:
        mes_consulta = "Marzo"
        res = supabase.table("estudiantes").select("escuela_id").eq("mes_carga", mes_consulta).execute()
        df_conteo = pd.DataFrame(res.data)
        res_total = supabase.table("escuelas").select("id", count="exact").execute()
        total_sistema = res_total.count
        if not df_conteo.empty:
            total_cargadas = df_conteo['escuela_id'].nunique()
            st.write(f"### Estado de carga: **{mes_consulta}**")
            st.metric("Instituciones", f"{total_cargadas} de {total_sistema}")
            st.progress(total_cargadas / total_sistema)
    except: st.error("Error al obtener estadísticas.")
    if st.button("Entrar al Panel", use_container_width=True): st.rerun()

# --- FUNCIONES CORE ---
def login():
    st.markdown("<h1 style='text-align: center;'>🔐 Sistema de Estadísticas</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        u_input = st.text_input("Usuario (Cédula)")
        p_input = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar", use_container_width=True):
            try:
                res = supabase.table("usuarios").select("*").eq("usuario", u_input).eq("password", p_input).eq("activo", True).execute()
                if res.data:
                    user = res.data[0]
                    res_esc = supabase.table("usuario_escuelas").select("escuela_id").eq("usuario_id", user['id']).execute()
                    user['escuelas_asignadas'] = [e['escuela_id'] for e in res_esc.data]
                    st.session_state["logeado"] = True
                    st.session_state["user_data"] = user
                    st.session_state["mostrar_popup"] = True
                    st.rerun()
                else: st.error("Credenciales inválidas.")
            except: st.error("Error de conexión.")

@st.cache_data(ttl=600)
def obtener_catalogos():
    try:
        res_car = supabase.table("cat_cargo").select("*").execute()
        res_con = supabase.table("cat_condicion").select("*").execute()
        res_dep = supabase.table("cat_dependencia").select("*").execute()
        res_cir = supabase.table("circuitos").select("*").order("id").execute()
        return (pd.DataFrame(res_car.data), pd.DataFrame(res_con.data), pd.DataFrame(res_dep.data), pd.DataFrame(res_cir.data))
    except: return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- INICIO DE APLICACIÓN ---
if "logeado" not in st.session_state: st.session_state["logeado"] = False

df_cat_car, df_cat_con, df_cat_dep, df_circuitos = obtener_catalogos()

if not st.session_state["logeado"]:
    login()
    st.stop()

u_data = st.session_state["user_data"]
rol_usuario = str(u_data.get("rol", "")).lower()

if st.session_state.get("mostrar_popup") and rol_usuario == "supervisor":
    st.session_state["mostrar_popup"] = False
    mostrar_resumen_supervisor()

# Interfaz Superior
c_vacia, c_btn2, c_btn1 = st.columns([4, 1, 1])
with c_btn1:
    if st.button("⚙️ Perfil"): ventana_configuracion()
with c_btn2:
    if st.button("🚪 Salir"):
        st.session_state.clear()
        st.rerun()

c_mes, _ = st.columns([2, 4])
with c_mes:
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_sel = st.selectbox("📅 Período:", meses, index=(datetime.now().month - 2) % 12)

st.markdown("<h1 style='text-align: center; color: #1f3b64;'>Sistema Integrado de Estadísticas</h1>", unsafe_allow_html=True)
modo = st.pills("Acción:", ["📊 Consultar", "📥 Cargar Datos"], default="📊 Consultar") if rol_usuario in ["admin", "director"] else "📊 Consultar"

# --- BLOQUE DE CARGA ---
if modo == "📥 Cargar Datos":
    res_esc_all = supabase.table("escuelas").select("id, nombre_actual").execute()
    df_esc_all = pd.DataFrame(res_esc_all.data)
    df_opciones_carga = df_esc_all if rol_usuario == "admin" else df_esc_all[df_esc_all['id'].isin(u_data.get('escuelas_asignadas', []))]

    if df_opciones_carga.empty:
        st.warning("⚠️ No tiene instituciones asignadas.")
    else:
        inst_nom_carga = st.selectbox("Seleccione Institución:", df_opciones_carga['nombre_actual'])
        id_inst = df_opciones_carga[df_opciones_carga['nombre_actual'] == inst_nom_carga]['id'].values[0]
        
        t1, t2, t3 = st.tabs(["Estudiantes", "Personal", "Laboral"])
        with t1:
            opciones_grados = {"Inicial": ["maternal(0-1)", "maternal(1-2)", "maternal(2-3)", "preescolar(3-4)", "preescolar(4-5)", "preescolar(5-6)"], "Primaria": ["1º grado", "2º grado", "3º grado", "4º grado", "5º grado", "6º grado"], "Media General": ["1º año", "2º año", "3º año", "4º año", "5º año"], "Especial": ["Único"]}
            n_sel_c = st.selectbox("Nivel Educativo:", list(opciones_grados.keys()))
            g_sel_c = st.selectbox("Grado/Sección:", opciones_grados[n_sel_c])
            with st.form("f_est"):
                c_v, c_h = st.columns(2)
                v_in = c_v.number_input("Varones Inscritos:", min_value=0, step=1)
                h_in = c_h.number_input("Hembras Inscritas:", min_value=0, step=1)
                if st.form_submit_button("🚀 GUARDAR ESTUDIANTES"):
                    total = v_in + h_in
                    if total > 0:
                        datos = {"escuela_id": int(id_inst), "mes_carga": mes_sel, "ano_escolar": "2025-2026", "nivel_educativo": n_sel_c, "detalle_grupo": g_sel_c, "varones": v_in, "hembras": h_in, "total_matricula": total}
                        supabase.table("estudiantes").upsert(datos, on_conflict="escuela_id, nivel_educativo, detalle_grupo, mes_carga, ano_escolar").execute()
                        st.success("✅ ¡Guardado!")

        with t2: # Personal
            with st.form("f_per"):
                tipo_p = st.selectbox("Tipo:", ["Docente", "Administrativo", "Obrero", "Cocineras"])
                c1, c2 = st.columns(2)
                v_p = c1.number_input("Varones:", min_value=0)
                h_p = c2.number_input("Hembras:", min_value=0)
                if st.form_submit_button("🚀 GUARDAR PERSONAL"):
                    datos_p = {"escuela_id": int(id_inst), "tipo_personal": tipo_p, "varones_contratados": v_p, "hembras_contratadas": h_p, "mes_carga": mes_sel, "ano_escolar": "2025-2026"}
                    supabase.table("personal").upsert(datos_p, on_conflict="escuela_id, mes_carga, ano_escolar, tipo_personal").execute()
                    st.success("✅ Guardado")

        with t3: # Laboral
            if not df_cat_car.empty:
                with st.form("f_lab"):
                    d_car = dict(zip(df_cat_car['nombre'], df_cat_car['id']))
                    d_con = dict(zip(df_cat_con['nombre'], df_cat_con['id']))
                    car_s = st.selectbox("Cargo:", list(d_car.keys()))
                    con_s = st.selectbox("Condición:", list(d_con.keys()))
                    v_l = st.number_input("V:", min_value=0)
                    h_l = st.number_input("H:", min_value=0)
                    if st.form_submit_button("🚀 GUARDAR"):
                        d_l = {"escuela_id": int(id_inst), "mes": mes_sel, "ano_escolar": "2025-2026", "cargo_id": d_car[car_s], "condicion_id": d_con[con_s], "varones": v_l, "hembras": h_l}
                        supabase.table("condicion_laboral").upsert(d_l, on_conflict="escuela_id, mes, ano_escolar, cargo_id, condicion_id").execute()
                        st.success("✅ Guardado")

# --- BLOQUE DE CONSULTA ---
else:
    modulo = st.radio("Módulo:", ["Estudiantes", "Docentes", "Personal No Docente", "Condición Laboral"], horizontal=True)
    
    # Definición de alcance de escuelas
    if rol_usuario in ["admin", "supervisor"]:
        res_esc_all = supabase.table("escuelas").select("id, nombre_actual").execute()
        df_ver = pd.DataFrame(res_esc_all.data)
        ids_para_query = df_ver['id'].tolist()
    else:
        ids_usuario = u_data.get('escuelas_asignadas', [])
        res_esc_prop = supabase.table("escuelas").select("id, nombre_actual").in_("id", ids_usuario).execute()
        df_ver = pd.DataFrame(res_esc_prop.data)
        ids_para_query = ids_usuario

    alcance = st.selectbox("Agrupación:", ["🌍 Municipio", "🛰️ Circuito", "🏫 Institución"])
    
    if alcance == "🛰️ Circuito":
        circ_nom = st.selectbox("Circuito:", df_circuitos['nombre'])
        id_c = df_circuitos[df_circuitos['nombre'] == circ_nom]['id'].values[0]
        res_e = supabase.table("escuelas").select("id").eq("circuito_id", id_c).execute()
        ids_para_query = [e['id'] for e in res_e.data]
    elif alcance == "🏫 Institución":
        inst_nom = st.selectbox("Institución:", df_ver['nombre_actual'])
        ids_para_query = [df_ver[df_ver['nombre_actual'] == inst_nom]['id'].values[0]]

    # Lógica de visualización por módulo
    if modulo == "Condición Laboral":
        res_lab = supabase.table("condicion_laboral").select("*").eq("mes", mes_sel).in_("escuela_id", ids_para_query).execute()
        df_lab = pd.DataFrame(res_lab.data)
        if not df_lab.empty:
            df_lab['Cargo'] = df_lab['cargo_id'].map(df_cat_car.set_index('id')['nombre'].to_dict())
            df_lab['Condición'] = df_lab['condicion_id'].map(df_cat_con.set_index('id')['nombre'].to_dict())
            st.dataframe(df_lab[['Cargo', 'Condición', 'varones', 'hembras']])
        else: st.info("No hay datos.")

    else: # Estudiantes / Personal
        if modulo == "Estudiantes":
            tabla, col_v, col_h = "estudiantes", "varones", "hembras"
            query = supabase.table(tabla).select("*").eq("mes_carga", mes_sel).in_("escuela_id", ids_para_query)
        else:
            tabla, col_v, col_h = "personal", "varones_contratados", "hembras_contratadas"
            roles = ["Docente"] if modulo == "Docentes" else ["Administrativo", "Obrero", "Cocineras"]
            query = supabase.table(tabla).select("*").eq("mes_carga", mes_sel).in_("escuela_id", ids_para_query).in_("tipo_personal", roles)

        res = query.execute()
        df_res = pd.DataFrame(res.data)
        if not df_res.empty:
            st.metric("Total", int(df_res[col_v].sum() + df_res[col_h].sum()))
            fig = px.bar(df_res, x="escuela_id", y=[col_v, col_h], barmode="group")
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Sin registros.")
