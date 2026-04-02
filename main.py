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

# --- FUNCIÓN PARA CONVERTIR IMAGEN A BASE64 ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Intentamos cargar la imagen de la carpeta static
try:
    bin_str = get_base64("static/mppe.png")
    
    # --- APLICAR MARCA DE AGUA CON BASE64 ---
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-attachment: fixed;
            background-size: 60%; /* Ajusta el tamaño aquí */
            background-repeat: no-repeat;
            background-position: center;
            background-color: rgba(255, 255, 255, 0.95); /* Fondo blanco tenue */
            background-blend-mode: overlay; /* Esto crea el efecto de marca de agua suave */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
except Exception:
    # Si falla la carga, no rompe la app, solo no muestra el fondo
    pass# --- ESTILOS PERSONALIZADOS ---
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
    .card h3 {
        color: #1f3b64 !important;
        margin-bottom: 5px;
        font-size: 16px;
    }
    .card p {
        color: #333333 !important;
        font-size: 24px;
        font-weight: bold;
        margin: 0;
    }
    div[data-testid="stMarkdownContainer"] {
        color: inherit;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VENTANA DE CONFIGURACIÓN ---
@st.dialog("Configuración de Perfil")
def ventana_configuracion():
    st.write("Introduzca su nueva contraseña:")
    nueva_p = st.text_input("Nueva Contraseña", type="password")
    confirmar_p = st.text_input("Confirmar Nueva Contraseña", type="password")
    if st.button("Guardar Cambios", use_container_width=True):
        if len(nueva_p) < 6: 
            st.error("Mínimo 6 caracteres.")
        elif nueva_p != confirmar_p: 
            st.error("No coinciden.")
        else:
            try:
                supabase.table("usuarios").update({"password": nueva_p}).eq("id", st.session_state["user_data"]['id']).execute()
                st.success("✅ ¡Actualizada!")
            except: 
                st.error("Error al conectar.")

# --- FUNCIÓN DE AUTENTICACIÓN ---
def login():
    st.markdown(
        """
        <div style='width: 100%; display: flex; justify-content: center;'>
            <h1 style='text-align: center; color: #1f3b64; width: 100%;'>
                🔐Sistema Integrado de Estadísticas
            </h1>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <div style='width: 100%; display: flex; justify-content: center; margin-top: -10px;'>
            <p style='text-align: center; color: #555555; font-size: 1.2rem; font-weight: 500;'>
                Acceso CDCE-RIBAS
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                u_input = st.text_input("Usuario (Cédula)")
                p_input = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Ingresar al Sistema", use_container_width=True):
                    try:
                        res = supabase.table("usuarios").select("*").eq("usuario", u_input).eq("password", p_input).eq("activo", True).execute()
                        if res.data:
                            user = res.data[0]
                            res_esc = supabase.table("usuario_escuelas").select("escuela_id").eq("usuario_id", user['id']).execute()
                            user['escuelas_asignadas'] = [e['escuela_id'] for e in res_esc.data]
                            
                            st.session_state["logeado"] = True
                            st.session_state["user_data"] = user
                            st.rerun()
                        else:
                            st.error("Credenciales inválidas o usuario inactivo.")
                    except Exception:
                        st.error("⚠️ Error de conexión.")
            
            st.markdown("---")
            if st.button("¿Olvidaste tu contraseña?"):
                st.info("Por favor, contacta al administrador.")
                st.markdown("[📩 Contactar por WhatsApp](https://wa.me/584124613466)")

# --- CONTROL DE SESIÓN ---
if "logeado" not in st.session_state: 
    st.session_state["logeado"] = False

# --- CARGA GLOBAL DE CATÁLOGOS ---
@st.cache_data(ttl=600)
def obtener_catalogos():
    try:
        res_car = supabase.table("cat_cargo").select("*").execute()
        res_con = supabase.table("cat_condicion").select("*").execute()
        res_dep = supabase.table("cat_dependencia").select("*").execute()
        res_cir = supabase.table("circuitos").select("*").order("id").execute()
        return (pd.DataFrame(res_car.data), pd.DataFrame(res_con.data), pd.DataFrame(res_dep.data), pd.DataFrame(res_cir.data))
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_cat_car, df_cat_con, df_cat_dep, df_circuitos = obtener_catalogos()

# --- LÓGICA DE PANTALLAS ---
if not st.session_state["logeado"]:
    login()
    st.stop()
else:
    # --- INTERFAZ PRINCIPAL (SOLO SI ESTÁ LOGEADO) ---
    # 1. Botones de Control Alineados
    c_btn2, c_btn1, c_espacio_btns = st.columns([1, 1, 4])
    with c_btn1:
        if st.button("⚙️ Perfil"):
            ventana_configuracion()
    with c_btn2:
        if st.button("🚪 Salir"):
            st.session_state.clear()
            st.rerun()

    # 2. Logo y Período
    # --- BLOQUE 2: PERÍODO Y DISTINTIVO ---
# Usamos solo 2 columnas para que no se desordene en el móvil
c_mes, c_distintivo = st.columns([2, 1])

with c_mes:
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    # El selector de mes ahora ocupa un espacio más cómodo
    mes_sel = st.selectbox("📅 Período:", meses, index=datetime.now().month-1)

    with c_distintivo:
        # Como el logo ya está en el fondo (marca de agua), 
        # aquí solo ponemos el nombre de la institución como referencia rápida.
        st.markdown(
            """
            <div style='text-align: right; margin-top: 25px;'>
                <span style='color: #002D57; font-weight: bold; font-size: 0.9rem;'>
                    CDCE RIBAS
                </span>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    # 3. Título Centrado
    st.markdown(
        """
        <div style='width: 100%; display: flex; justify-content: center;'>
            <h1 style='text-align: center; color: #1f3b64; width: 100%;'>
                Sistema Integrado de Estadísticas
            </h1>
        </div>
        """, 
        unsafe_allow_html=True
    )

    u_data = st.session_state["user_data"]
    rol_usuario = str(u_data.get("rol", "")).lower()
    
    modo = st.pills("Acción:", ["📊 Consultar", "📥 Cargar Datos"], default="📊 Consultar") if rol_usuario in ["admin", "director"] else "📊 Consultar"

    # --- MÓDULO DE CARGA ---
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
            
            with t1: # Estudiantes
                opciones_grados = {
                    "Inicial": ["maternal(0-1)", "maternal(1-2)", "maternal(2-3)", "preescolar(3-4)", "preescolar(4-5)", "preescolar(5-6)"],
                    "Primaria": ["1º grado", "2º grado", "3º grado", "4º grado", "5º grado", "6º grado"],
                    "Media General": ["1º año", "2º año", "3º año", "4º año", "5º año"],
                    "Especial": ["Único"]
                }
                n_sel_c = st.selectbox("Nivel Educativo:", list(opciones_grados.keys()), key="n_c_est")
                g_sel_c = st.selectbox("Grado/Sección:", opciones_grados[n_sel_c], key="g_c_est")

                with st.form("f_est_v3", clear_on_submit=True):
                    c_v, c_h = st.columns(2)
                    with c_v:
                        v_in = st.number_input("Varones Inscritos:", min_value=0, step=1)
                        v_as = st.number_input("Asistencia Promedio V:", min_value=0.0)
                    with c_h:
                        h_in = st.number_input("Hembras Inscritas:", min_value=0, step=1)
                        h_as = st.number_input("Asistencia Promedio H:", min_value=0.0)

                    if st.form_submit_button("🚀 GUARDAR ESTUDIANTES", use_container_width=True):
                        total_inscritos = v_in + h_in
                        if total_inscritos > 0:
                            p_real = ((v_as + h_as) / total_inscritos) * 100
                            datos = {
                                "escuela_id": int(id_inst), "mes_carga": mes_sel, "ano_escolar": "2025-2026",
                                "nivel_educativo": n_sel_c, "detalle_grupo": g_sel_c,
                                "varones": v_in, "hembras": h_in, "total_matricula": total_inscritos,
                                "asistencia_varones": v_as, "asistencia_hembras": h_as,
                                "asistencia_promedio_real": round(p_real, 2)
                            }
                            try:
                                supabase.table("estudiantes").upsert(datos, on_conflict="escuela_id, nivel_educativo, detalle_grupo, mes_carga, ano_escolar").execute()
                                st.success("✅ ¡Datos guardados!")
                            except Exception as e: st.error(f"❌ Error: {e}")

            with t2: # Personal
                niveles_p = {"Inicial": ["maternal", "preescolar"], "Primaria": ["primaria"], "Media": ["media general"], "Especial": ["educacion especial"], "Otros": ["no aplica"]}
                np_s = st.selectbox("Nivel Educativo:", list(niveles_p.keys()))
                sub_np_s = st.selectbox("Detalle:", niveles_p[np_s])

                with st.form("f_per_v3", clear_on_submit=True):
                    c1, c2, c3 = st.columns(3)
                    with c1: car_s = st.selectbox("Cargo:", ["Docente", "Administrativo", "Obrero", "Cocineras", "Vigilantes"])
                    with c2:
                        v_c = st.number_input("V. Contratados:", min_value=0)
                        h_c = st.number_input("H. Contratadas:", min_value=0)
                    with c3:
                        va_p = st.number_input("Asis. V:", min_value=0.0)
                        ha_p = st.number_input("Asis. H:", min_value=0.0)

                    if st.form_submit_button("🚀 GUARDAR PERSONAL", use_container_width=True):
                        if (v_c + h_c) > 0:
                            datos_p = {
                                "escuela_id": int(id_inst), "nivel_educativo": np_s, "detalle_grupo": sub_np_s, 
                                "tipo_personal": car_s, "varones_contratados": int(v_c), "hembras_contratadas": int(h_c),
                                "asistencia_v": int(va_p), "asistencia_h": int(ha_p), "mes_carga": mes_sel, "ano_escolar": "2025-2026"
                            }
                            try:
                                supabase.table("personal").upsert(datos_p, on_conflict="escuela_id, mes_carga, ano_escolar, detalle_grupo, tipo_personal").execute()
                                st.success("✅ Guardado")
                            except Exception as e: st.error(f"❌ Error: {e}")

            with t3: # Laboral
                if not df_cat_car.empty:
                    with st.form("f_lab_v3", clear_on_submit=True):
                        cl1, cl2 = st.columns(2)
                        with cl1:
                            d_car = dict(zip(df_cat_car['nombre'], df_cat_car['id']))
                            d_con = dict(zip(df_cat_con['nombre'], df_cat_con['id']))
                            c_s = st.selectbox("Cargo:", list(d_car.keys()))
                            co_s = st.selectbox("Condición:", list(d_con.keys()))
                        with cl2:
                            lv = st.number_input("Varones:", min_value=0)
                            lh = st.number_input("Hembras:", min_value=0)

                        if st.form_submit_button("🚀 GUARDAR CONDICIÓN", use_container_width=True):
                            datos_l = {
                                "escuela_id": int(id_inst), "mes": mes_sel, "ano_escolar": "2025-2026",
                                "cargo_id": d_car[c_s], "condicion_id": d_con[co_s], "varones": int(lv), "hembras": int(lh)
                            }
                            try:
                                supabase.table("condicion_laboral").upsert(datos_l, on_conflict="escuela_id, mes, ano_escolar, cargo_id, condicion_id").execute()
                                st.success("✅ ¡Éxito!")
                            except Exception as e: st.error(f"❌ Error: {e}")

    # --- MÓDULO DE CONSULTA ---
    else:
        modulo = st.radio("Módulo:", ["Estudiantes", "Docentes", "Personal No Docente", "Condición Laboral"], horizontal=True)
        escuelas_ids_usuario = u_data.get('escuelas_asignadas', [])
        
        if rol_usuario in ["admin", "supervisor"]:
            res_esc_all = supabase.table("escuelas").select("id, nombre_actual").execute()
            df_ver = pd.DataFrame(res_esc_all.data)
            ids_para_query_global = df_ver['id'].tolist()
        else:
            res_esc_prop = supabase.table("escuelas").select("id, nombre_actual").in_("id", escuelas_ids_usuario).execute()
            df_ver = pd.DataFrame(res_esc_prop.data)
            ids_para_query_global = escuelas_ids_usuario

        alcance = st.selectbox("Agrupación:", ["🌍 Municipio", "🛰️ Circuito", "🏫 Institución"])
        ids_para_query = ids_para_query_global

        if alcance == "🛰️ Circuito":
            circ_nom = st.selectbox("Circuito:", df_circuitos['nombre'])
            id_c = df_circuitos[df_circuitos['nombre'] == circ_nom]['id'].values[0]
            res_e = supabase.table("escuelas").select("id").eq("circuito_id", id_c).execute()
            ids_para_query = [e['id'] for e in res_e.data]
        elif alcance == "🏫 Institución":
            inst_nom = st.selectbox("Institución:", df_ver['nombre_actual'])
            ids_para_query = [df_ver[df_ver['nombre_actual'] == inst_nom]['id'].values[0]]

        if modulo == "Condición Laboral":
            res_lab = supabase.table("condicion_laboral").select("*").eq("mes", mes_sel).in_("escuela_id", ids_para_query).execute()
            df_lab = pd.DataFrame(res_lab.data)
            if not df_lab.empty:
                df_lab['Cargo'] = df_lab['cargo_id'].map(df_cat_car.set_index('id')['nombre'].to_dict())
                df_lab['Condición'] = df_lab['condicion_id'].map(df_cat_con.set_index('id')['nombre'].to_dict())
                df_res = df_lab.groupby(['Condición', 'Cargo']).agg({'varones': 'sum', 'hembras': 'sum'}).reset_index()
                st.dataframe(df_res, use_container_width=True)
            else:
                st.info("Sin datos.")
        else:
            # Lógica para Estudiantes/Personal similar...
            st.info("Módulo de consulta en desarrollo con la nueva indentación.")
