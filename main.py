import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from supabase import create_client, Client

# --- DATOS DE CONEXIÓN ---
# Conexión usando el objeto secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="CDCE RIBAS V2", layout="wide", page_icon="📊")

# --- BLOQUE 1: BOTONES SUPERIORES ---
c_espacio, c_btn1, c_btn2 = st.columns([3, 1, 1])

with c_btn1:
    # Quitamos 'use_container_width' para que el botón solo ocupe lo que mide su texto
    if st.button("⚙️ Perfil"):
        ventana_configuracion()

with c_btn2:
    if st.button("🚪 Salir"):
        st.session_state.clear()
        st.rerun()

# Espacio sutil después de los botones
st.write("")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .card {
        background-color: #ffffff !important; /* Fondo blanco forzado */
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        margin-bottom: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .card h3 {
        color: #1f3b64 !important; /* Azul oscuro forzado para títulos */
        margin-bottom: 5px;
        font-size: 16px;
    }
    .card p {
        color: #333333 !important; /* Gris casi negro para los números/texto */
        font-size: 24px;
        font-weight: bold;
        margin: 0;
    }
    /* Esto asegura que el contenedor de Streamlit no interfiera */
    div[data-testid="stMarkdownContainer"] {
        color: inherit;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE AUTENTICACIÓN ---
def login():
# --- BLOQUE 1: BOTONES SUPERIORES ---
c_espacio, c_btn1, c_btn2 = st.columns([3, 1, 1])

with c_btn1:
    # Quitamos 'use_container_width' para que el botón solo ocupe lo que mide su texto
    if st.button("⚙️ Perfil"):
        ventana_configuracion()

with c_btn2:
    if st.button("🚪 Salir"):
        st.session_state.clear()
        st.rerun()

# Espacio sutil después de los botones
st.write("")

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
    # --- SUBTÍTULO CENTRADO CON ESTILO ---
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
                        st.error("⚠️ Error de conexión: No se pudo contactar con la base de datos. Verifique su internet.")
            
            # --- PARTE RESTAURADA ---
            st.markdown("---")
            if st.button("¿Olvidaste tu contraseña?"):
                st.info("Por favor, contacta al administrador del sistema.")
                st.markdown("[📩 Contactar por WhatsApp](https://wa.me/584124613466?text=Hola,%20olvidé%20mi%20clave%20del%20sistema)")

# --- CONTROL DE SESIÓN ---
if "logeado" not in st.session_state: st.session_state["logeado"] = False

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

if not st.session_state["logeado"]:
    login()
    st.stop()

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

# --- INTERFAZ PRINCIPAL ---
u_data = st.session_state["user_data"]
rol_usuario = str(u_data.get("rol", "")).lower()
c_mes, c_logo2, c_logo= st.columns([1, 1, 2])
with c_mes:
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_sel = st.selectbox("📅 Período:", meses, index=datetime.now().month-1)
with c_logo:
    if os.path.exists("static/mppe.png"):
        st.image("static/mppe.png", width=120)
    else:
        st.markdown("<h3 style='text-align:center; color:#002D57;'>CDCE RIBAS</h3>", unsafe_allow_html=True)

        st.session_state.clear()
        st.rerun()
st.markdown("<h2 class='main-title'>Sistema Integrado de Estadísticas</h2>", unsafe_allow_html=True)
modo = st.pills("Acción:", ["📊 Consultar", "📥 Cargar Datos"], default="📊 Consultar") if rol_usuario in ["admin", "director"] else "📊 Consultar"

# ==========================================
# 📥 MÓDULO DE CARGA DE DATOS
# ==========================================
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
        
        # --- TAB ESTUDIANTES ---
        with t1:
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
                    v_in = st.number_input("Varones Inscritos:", min_value=0, step=1, key="vi_est")
                    v_as = st.number_input("Asistencia Promedio V:", min_value=0.0, format="%.2f", key="va_est")
                with c_h:
                    h_in = st.number_input("Hembras Inscritas:", min_value=0, step=1, key="hi_est")
                    h_as = st.number_input("Asistencia Promedio H:", min_value=0.0, format="%.2f", key="ha_est")

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
                    else: st.warning("⚠️ La matrícula total no puede ser cero.")

        # --- TAB PERSONAL ---
        with t2:
            niveles_p = {
                "Inicial": ["maternal", "preescolar"], "Primaria": ["primaria"],
                "Media": ["media general", "media técnica"], "Especial": ["educacion especial"],
                "Adultos": ["jovenes y adultos"], "Otros": ["no aplica"]
            }
            np_s = st.selectbox("Nivel Educativo:", list(niveles_p.keys()), key="np_p_c")
            sub_np_s = st.selectbox("Detalle del Nivel:", niveles_p[np_s], key="sub_np_p_c")

            with st.form("f_per_v3", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                with c1: car_s = st.selectbox("Cargo:", ["Docente", "Administrativo", "Obrero", "Cocineras", "Vigilantes"], key="car_p_c")
                with c2:
                    v_c = st.number_input("Varones Contratados:", min_value=0, step=1, key="vc_p_c")
                    h_c = st.number_input("Hembras Contratadas:", min_value=0, step=1, key="hc_p_c")
                with c3:
                    va_p = st.number_input("Asis. Promedio V:", min_value=0.0, format="%.2f", key="va_p_c")
                    ha_p = st.number_input("Asis. Promedio H:", min_value=0.0, format="%.2f", key="ha_p_c")

                if st.form_submit_button("🚀 GUARDAR PERSONAL", use_container_width=True):
                    if (v_c + h_c) > 0:
                        datos_p = {
                            "escuela_id": int(id_inst), "nivel_educativo": np_s,
                            "detalle_grupo": sub_np_s, "tipo_personal": car_s,
                            "varones_contratados": int(v_c), "hembras_contratadas": int(h_c),
                            "asistencia_v": int(va_p), "asistencia_h": int(ha_p),
                            "mes_carga": mes_sel, "ano_escolar": "2025-2026"
                        }
                        try:
                            # ON_CONFLICT DEBE COINCIDIR CON LA REGLA SQL (escuela, mes, año, detalle)
                            supabase.table("personal").upsert(datos_p, on_conflict="escuela_id, mes_carga, ano_escolar, detalle_grupo, tipo_personal").execute()
                            st.success(f"✅ ¡{car_s} guardado correctamente!")
                        except Exception as e: st.error(f"❌ Error: {e}")
                    else: st.warning("Ingrese al menos una persona.")

        # --- TAB LABORAL ---
        with t3:
            if not df_cat_car.empty:
                with st.form("f_lab_v3", clear_on_submit=True):
                    cl1, cl2 = st.columns(2)
                    with cl1:
                        d_car = dict(zip(df_cat_car['nombre'], df_cat_car['id']))
                        d_con = dict(zip(df_cat_con['nombre'], df_cat_con['id']))
                        c_s = st.selectbox("Cargo:", list(d_car.keys()))
                        co_s = st.selectbox("Condición:", list(d_con.keys()))
                    with cl2:
                        lv = st.number_input("Varones:", min_value=0, step=1)
                        lh = st.number_input("Hembras:", min_value=0, step=1)

                    if st.form_submit_button("🚀 GUARDAR CONDICIÓN", use_container_width=True):
                        if (lv + lh) > 0:
                            datos_l = {
                                "escuela_id": int(id_inst),
                                "mes": mes_sel,                # Revisa si en tu tabla es 'mes' o 'mes_carga'
                                "ano_escolar": "2025-2026",
                                "cargo_id": d_car[c_s],
                                "condicion_id": d_con[co_s],
                                "varones": int(lv),            # Forzamos entero para evitar el error 22P02
                                "hembras": int(lh)             # Forzamos entero
                            }
                            try:
                                supabase.table("condicion_laboral").upsert(datos_l, on_conflict="escuela_id, mes, ano_escolar, cargo_id, condicion_id").execute()
                                st.success("✅ ¡Condición guardada!")
                            except Exception as e: st.error(f"❌ Error: {e}")
            else: st.warning("⚠️ Ingrese al menos una cantidad en varones o hembras.")

# ==========================================
# 📊 MÓDULO DE CONSULTA DE DATOS (CORREGIDO)
# ==========================================
else: 
    # 1. SELECTOR DE MÓDULO
    modulo = st.radio("Módulo a visualizar:", ["Estudiantes", "Docentes", "Personal No Docente", "Condición Laboral"], horizontal=True)
    
    # 2. FILTROS DE ALCANCE (Municipio, Circuito, Institución)
    escuelas_ids_usuario = u_data.get('escuelas_asignadas', [])
    if rol_usuario in ["admin", "supervisor"]:
        res_esc_all = supabase.table("escuelas").select("id, nombre_actual").execute()
        df_ver = pd.DataFrame(res_esc_all.data)
        ids_para_query_global = df_ver['id'].tolist()
    else:
        res_esc_prop = supabase.table("escuelas").select("id, nombre_actual").in_("id", escuelas_ids_usuario).execute()
        df_ver = pd.DataFrame(res_esc_prop.data)
        ids_para_query_global = escuelas_ids_usuario

    st.markdown("### 🔍 Configuración del Reporte")
    c1, c2 = st.columns(2)
    with c1:
        alcance = st.selectbox("Nivel de Agrupación:", ["🌍 Municipio (Global)", "🛰️ Por Circuito", "🏫 Por Institución"])

    ids_para_query = ids_para_query_global # Valor por defecto

    if alcance == "🛰️ Por Circuito":
        with c2:
            circ_nom = st.selectbox("Seleccione Circuito:", df_circuitos['nombre'])
            id_c = df_circuitos[df_circuitos['nombre'] == circ_nom]['id'].values[0]
            res_e = supabase.table("escuelas").select("id").eq("circuito_id", id_c).execute()
            ids_para_query = [e['id'] for e in res_e.data]
    elif alcance == "🏫 Por Institución":
        with c2:
            inst_nom = st.selectbox("Seleccione Institución:", df_ver['nombre_actual'])
            ids_para_query = [df_ver[df_ver['nombre_actual'] == inst_nom]['id'].values[0]]

    st.write("---")

    # --- LÓGICA DE CONSULTA SEGÚN MÓDULO ---
# --- A. LÓGICA DE CONDICIÓN LABORAL (DISEÑO SEGÚN CAPTURE 13/14) ---
    if modulo == "Condición Laboral":
            # Usamos .eq("mes", mes_sel) porque tu tabla usa 'mes' en vez de 'mes_carga'
            res_lab = supabase.table("condicion_laboral").select("*").eq("mes", mes_sel).in_("escuela_id", ids_para_query).execute()
            df_lab = pd.DataFrame(res_lab.data)

            if not df_lab.empty:
                # Mapeo de nombres desde los catálogos
                df_lab['Cargo'] = df_lab['cargo_id'].map(df_cat_car.set_index('id')['nombre'].to_dict())
                df_lab['Condición'] = df_lab['condicion_id'].map(df_cat_con.set_index('id')['nombre'].to_dict())
                
                # Consolidación
                df_res = df_lab.groupby(['Condición', 'Cargo']).agg({'varones': 'sum', 'hembras': 'sum'}).reset_index()
                df_res['Total'] = df_res['varones'] + df_res['hembras']
                
                # KPIs Superiores
                t_v, t_h = df_res['varones'].sum(), df_res['hembras'].sum()
                k1, k2, k3 = st.columns(3)
                k1.metric("Total Personal", f"{int(t_v + t_h)}")
                k2.metric("Total Varones", f"{int(t_v)}")
                k3.metric("Total Hembras", f"{int(t_h)}")
                st.write("---")

                st.markdown("#### 📋 Detalle por Condición y Cargo")
                c_tarjetas = st.columns(2)
                
                for i, r in df_res.iterrows():
                    with c_tarjetas[i % 2]:
                        # CRÍTICO: El uso de f-strings con triple comilla y unsafe_allow_html=True
                        st.markdown(f"""
                            <div style="background-color: white; padding: 20px; border-radius: 20px; border-left: 10px solid #4A90E2; box-shadow: 4px 4px 15px rgba(0,0,0,0.1); text-align: center; margin-bottom: 25px; min-height: 350px;">
                                <div style="margin-bottom: 15px;">
                                    <p style="color: #666; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 1px; margin: 0;">CARGO</p>
                                    <h3 style="color: #002D57; margin: 5px 0; font-size: 1.1rem; text-transform: uppercase;">{r['Cargo']}</h3>
                                </div>
                                <div style="background-color: #F8F9FA; padding: 15px; border-radius: 15px; margin-bottom: 15px; border: 1px solid #E9ECEF;">
                                    <p style="color: #666; text-transform: uppercase; font-size: 0.7rem; margin: 0;">CANTIDAD</p>
                                    <h2 style="color: #4A90E2; margin: 5px 0; font-size: 2rem;">{int(r['Total'])}</h2>
                                    <p style="color: #444; font-size: 0.9rem; margin: 0;">♂ {int(r['varones'])} &nbsp; | &nbsp; ♀ {int(r['hembras'])}</p>
                                </div>
                                <div>
                                    <p style="color: #666; text-transform: uppercase; font-size: 0.7rem; margin: 0;">CONDICIÓN LABORAL</p>
                                    <p style="color: #333; font-weight: bold; margin: 5px 0; font-size: 1rem; text-transform: uppercase;">{r['Condición']}</p>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.info(f"No hay registros de condición laboral para {mes_sel}.")

    else: # Estudiantes, Docentes, Personal No Docente
        if modulo == "Estudiantes":
            tabla, col_v, col_h, col_av, col_ah = "estudiantes", "varones", "hembras", "asistencia_varones", "asistencia_hembras"
            query = supabase.table(tabla).select("*").eq("mes_carga", mes_sel).in_("escuela_id", ids_para_query)
        else:
            tabla, col_v, col_h, col_av, col_ah = "personal", "varones_contratados", "hembras_contratadas", "asistencia_v", "asistencia_h"
            roles = ["Docente"] if modulo == "Docentes" else ["Administrativo", "Obrero", "Cocineras", "Vigilantes"]
            query = supabase.table(tabla).select("*").eq("mes_carga", mes_sel).in_("escuela_id", ids_para_query).in_("tipo_personal", roles)

        res = query.execute()
        df = pd.DataFrame(res.data)

        if not df.empty:
            # Cálculos de KPIs
            v, h = df[col_v].sum(), df[col_h].sum()
            av, ah = df[col_av].sum(), df[col_ah].sum()
            total = v + h
            porc = ((av + ah) / total * 100) if total > 0 else 0

            # Mostrar KPIs Reales
            st.markdown(f"### 📈 Resumen de {modulo}")
            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("Matrícula", f"{int(total)}")
            k2.metric("Varones", f"{int(v)}")
            k3.metric("Hembras", f"{int(h)}")
            k4.metric("Asistencia", f"{int(av + ah)}")
            k5.metric("% Real", f"{porc:.1f}%")

            # Gráfico Comparativo
            # Agrupamos según el módulo (nivel educativo para estudiantes, tipo para personal)
            eje_x = "nivel_educativo" if modulo == "Estudiantes" else "tipo_personal"
            df_g = df.groupby(eje_x).agg({col_v:'sum', col_h:'sum', col_av:'sum', col_ah:'sum'}).reset_index()
            
            fig = px.bar(df_g, x=eje_x, y=[col_v, col_h], 
                         title=f"Distribución de {modulo} por Sexo", 
                         labels={"value": "Cantidad", "variable": "Sexo"},
                         barmode="group", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            # --- GRÁFICO 2: COMPARATIVO MATRÍCULA VS ASISTENCIA (Horizontal) ---
            st.markdown("#### 📊 Comparativo Matrícula vs Asistencia")
            
            # Creamos un resumen total para el gráfico horizontal
            df_h = pd.DataFrame({
                "Concepto": ["Personal Contratado" if modulo != "Estudiantes" else "Matrícula Inscrita", 
                             "Promedio Asistencia"],
                "Cantidad": [int(total), int(av + ah)]
            })

            fig_horiz = px.bar(df_h, 
                               y="Concepto", 
                               x="Cantidad", 
                               orientation='h',
                               text="Cantidad",
                               title=f"Rendimiento Mensual: {modulo}",
                               color="Concepto",
                               color_discrete_sequence=["#002D57", "#1f77b4"],
                               template="plotly_white")
            
            fig_horiz.update_traces(textposition='outside')
            fig_horiz.update_layout(showlegend=False, height=300)
            
            st.plotly_chart(fig_horiz, use_container_width=True)
        else:
            st.info(f"No se encontraron registros de {modulo} para {mes_sel} en la selección actual.")    
