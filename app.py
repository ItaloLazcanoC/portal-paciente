
import streamlit as st
import pandas as pd
import json, ast
from datetime import datetime

st.set_page_config(page_title="Portal Paciente/Familia", layout="wide", page_icon="💊")

@st.cache_data
def cargar_datos():
    url = "https://raw.githubusercontent.com/ItaloLazcanoC/Data/main/pacientes_simulado.csv"
    try:
        df = pd.read_csv(url)
        if df.shape[1] == 1 and df.columns[0].startswith("<!DOCTYPE"):
            raise ValueError("El enlace apunta a HTML, no a un CSV crudo.")
        return df
    except Exception:
        st.warning("No se pudo cargar desde GitHub. Intentando lectura local 'pacientes_simulado.csv'...")
        return pd.read_csv("pacientes_simulado.csv")

def _parse_list(x):
    if isinstance(x, list):
        return x
    try:
        return ast.literal_eval(x)
    except Exception:
        try:
            return json.loads(x)
        except Exception:
            return [str(x)] if pd.notna(x) else []

df = cargar_datos()

st.image("assets/banner_minsal.png", use_container_width=True)
st.markdown("**Consulta segura y accesible** sobre el estado de pacientes hospitalizados. Este portal es un *prototipo educativo* que refleja la solución seleccionada en el documento base.")

with st.sidebar:
    st.header("🔐 Autenticación")
    rut = st.text_input("RUT del paciente (ej: 12345678-9)")
    clave_unica = st.text_input("Clave Única (simulada)", type="password")
    autenticado = st.button("Ingresar")
    st.markdown("---")
    st.caption("Si no recuerda el RUT exacto, puede revisar el listado de ejemplo abajo.")
    with st.expander("Ver RUT disponibles (demo)"):
        st.write(df["rut"].head(20).tolist())

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if autenticado:
    st.session_state.autenticado = True
    st.session_state.rut = rut

if st.session_state.autenticado:
    paciente = df[df["rut"] == st.session_state.get("rut","")]
    if paciente.empty:
        st.error("No se encontró información para el RUT ingresado.")
    else:
        datos = paciente.iloc[0].to_dict()
        tabs = st.tabs(["🏥 Estado Clínico","📢 Notificaciones","💬 Asistente Virtual","📚 Educación","🫂 Apoyo","📊 Encuesta"])

        with tabs[0]:
            colA, colB, colC, colD = st.columns(4)
            colA.metric("Estado", datos["estado_salud"])
            colB.metric("Próxima visita médica", datos["proxima_visita_medica"])
            colC.metric("Última actualización", datos["ultima_actualizacion"])
            colD.metric("Paciente", datos["nombre"])
            st.markdown("---")
            c1, c2 = st.columns([2,1])
            with c1:
                st.subheader("Resumen de tratamiento")
                st.info(f"**Tratamiento indicado:** {datos['tratamiento']}")
                st.write("**Indicaciones clínicas destacadas** (demo):")
                st.markdown("- Mantener reposo relativo.\n- Hidratación adecuada.\n- Control de signos vitales cada 4h.\n- Seguimiento por medicina interna.")
            with c2:
                st.image("assets/icon_estado.png", use_container_width=True)
            st.subheader("Línea de tiempo (últimas 24-48h)")
            eventos = _parse_list(datos.get("notificaciones","[]"))[::-1]
            for i, ev in enumerate(eventos[:5], 1):
                st.markdown(f"**{i}.** {ev}  \n*{datos['ultima_actualizacion']}*")

        with tabs[1]:
            st.subheader("Centro de notificaciones")
            st.image("assets/icon_notif.png", width=140)
            notifs = _parse_list(datos.get("notificaciones","[]"))
            if notifs:
                for n in notifs:
                    st.warning(f"🔔 {n}")
            else:
                st.success("No hay notificaciones pendientes.")

        with tabs[2]:
            st.subheader("Asistente Virtual (FAQ)")
            st.image("assets/icon_chat.png", width=140)
            faq = st.selectbox("Seleccione una pregunta frecuente",[
                "¿Cuáles son los horarios de visita?",
                "¿Cómo actualizo el número de contacto del familiar?",
                "¿Qué significa 'en observación'?",
                "¿Cómo solicito un informe médico?",
            ])
            respuestas = {
                "¿Cuáles son los horarios de visita?": "🕑 10:00 a 12:00 y 17:00 a 19:00 (puede variar por unidad).",
                "¿Cómo actualizo el número de contacto del familiar?": "Use el formulario del hospital o contacte OIRS para actualizar sus datos.",
                "¿Qué significa 'en observación'?": "Que el paciente está siendo monitoreado continuamente para evaluar evolución clínica.",
                "¿Cómo solicito un informe médico?": "Debe solicitarlo al equipo tratante o vía OIRS según protocolo del hospital.",
            }
            st.info(respuestas[faq])
            st.markdown("### O haga una consulta libre")
            consulta = st.text_input("Escriba su consulta")
            if st.button("Enviar consulta"):
                if "visita" in consulta.lower():
                    st.success("🕑 Los horarios de visita son 10:00-12:00 y 17:00-19:00.")
                elif consulta.strip():
                    st.info("Su consulta será derivada al equipo clínico para respuesta (demo).")
                else:
                    st.warning("Por favor, escriba una consulta.")

        with tabs[3]:
            st.subheader("Material educativo para la familia")
            st.image("assets/icon_ed.png", width=140)
            st.markdown(f"{datos['educacion']}")
            with st.expander("Consejos generales de cuidado"):
                st.markdown("- Lávese las manos antes y después de la visita.\n- Evite traer alimentos sin autorización del equipo clínico.\n- Respete las indicaciones del personal y los horarios.\n- Mantenga un canal de comunicación respetuoso y claro.")
            st.markdown("**Enlaces útiles (externos)**")
            st.markdown("- SaludableMente (MINSAL): https://www.gob.cl/saludablemente/")
            st.markdown("- Derechos y deberes de los pacientes (BCN): https://www.bcn.cl/leychile/navegar?idNorma=1203827")

        with tabs[4]:
            st.subheader("Apoyo emocional y orientación")
            st.image("assets/icon_support.png", width=140)
            st.markdown("Si necesita apoyo, puede comunicarse con:\n- 📞 *Fono Salud Mental*: 600 360 7777\n- 💻 SaludableMente (MINSAL): https://www.gob.cl/saludablemente/\n- 🧭 OIRS de su hospital para orientación y trámites.")
            st.info("Este portal es un demo educativo; en un despliegue real se integraría con los canales oficiales.")

        with tabs[5]:
            st.subheader("Encuesta de satisfacción")
            st.image("assets/icon_survey.png", width=140)
            c1, c2 = st.columns(2)
            with c1:
                util = st.slider("¿Qué tan útil le resultó este portal?", 1, 5, 4)
                claridad = st.slider("Claridad de la información", 1, 5, 4)
                ansiedad = st.slider("Reducción de ansiedad", 1, 5, 3)
            with c2:
                comentario = st.text_area("Comentario adicional (opcional)", height=160)
            if st.button("Enviar retroalimentación"):
                try:
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    row = {"timestamp": ts, "rut": datos["rut"], "util": util, "claridad": claridad, "ansiedad": ansiedad, "comentario": comentario}
                    fb_path = "feedback.csv"
                    try:
                        df_fb = pd.read_csv(fb_path)
                        df_fb = pd.concat([df_fb, pd.DataFrame([row])], ignore_index=True)
                    except Exception:
                        df_fb = pd.DataFrame([row])
                    df_fb.to_csv(fb_path, index=False)
                    st.success("✅ ¡Gracias por su opinión!")
                    st.download_button("Descargar mis respuestas", data=pd.DataFrame([row]).to_csv(index=False).encode("utf-8"), file_name=f"feedback_{datos['rut']}.csv", mime="text/csv")
                except Exception as e:
                    st.error(f"No fue posible guardar la respuesta: {e}")
else:
    st.info("Por favor, ingrese su RUT y clave única en el panel izquierdo para acceder al portal.")
    st.image("assets/banner_minsal.png", use_container_width=True)
    st.caption("Imágenes referenciales creadas para este prototipo. Reemplace por logos oficiales del MINSAL si corresponde.")
