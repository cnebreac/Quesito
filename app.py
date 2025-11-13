# app.py
import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Vales contigo", page_icon="💙", layout="centered")

# =========================
# Definición de vales
# =========================
VALES = [
    {"id": 0, "titulo": "Abrazo largo", "texto": "Vale por un abrazo largo que arregla el día."},
    {"id": 1, "titulo": "Charla tranquila", "texto": "Vale por una conversación sin prisas y sin móviles."},
    {"id": 2, "titulo": "Peli elegida por ti", "texto": "Vale por elegir tú la peli, aunque sea malísima."},
    {"id": 3, "titulo": "Masaje", "texto": "Vale por un masaje de 10 minutos donde tú elijas."},
    {"id": 4, "titulo": "Paseo juntos", "texto": "Vale por un paseo para desconectar del mundo."},
    {"id": 5, "titulo": "Merienda sorpresa", "texto": "Vale por una merienda improvisada preparada por mí."},
    {"id": 6, "titulo": "Reinicio del día", "texto": "Vale por borrar lo malo y seguir juntos."},
    {"id": 7, "titulo": "Mimos ilimitados", "texto": "Vale por un rato de mimos sin límite de tiempo."},
    {"id": 8, "titulo": "Confesión pendiente", "texto": "Vale por contarte algo bonito que aún no sabes."},
    {"id": 9, "titulo": "Cita especial", "texto": "Vale por una cita sencilla pero muy tú y yo."},
]

# =========================
# Funciones con PIN / JSON
# =========================

def get_json_path(pin: str) -> Path:
    safe_pin = pin.replace(" ", "_").replace("/", "_")
    return Path(f"estado_vales_{safe_pin}.json")

def cargar_estado(pin: str):
    path = get_json_path(pin)
    if not path.exists():
        return set()
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("vales_usados", []))
    except Exception:
        return set()

def guardar_estado(pin: str, vales_usados: set):
    path = get_json_path(pin)
    with path.open("w", encoding="utf-8") as f:
        json.dump({"vales_usados": list(vales_usados)}, f, ensure_ascii=False, indent=2)

# =========================
# Pantalla de PIN (fijo = 'quesito')
# =========================

if "pin" not in st.session_state:
    st.session_state.pin = None

if st.session_state.pin is None:
    st.markdown("## Introduce tu PIN")
    pin_input = st.text_input("PIN:", type="password")

    if st.button("Entrar"):
        if pin_input.strip() == "":
            st.warning("El PIN no puede estar vacío.")
        elif pin_input != "quesito":
            st.error("PIN incorrecto.")
        else:
            st.session_state.pin = "quesito"
            st.rerun()

    st.stop()

pin = st.session_state.pin
vales_usados = cargar_estado(pin)

if "vale_a_confirmar" not in st.session_state:
    st.session_state.vale_a_confirmar = None

# =========================
# Cabecera
# =========================

st.markdown("# Vales contigo 💙")
st.caption(f"PIN activo: **{pin}**")

st.divider()

# =========================
# Tarjetas en cuadrícula
# =========================

n_cols = 2
ids = [v["id"] for v in VALES]
rows = [ids[i:i + n_cols] for i in range(0, len(ids), n_cols)]

for row in rows:
    cols = st.columns(len(row))

    for col, vid in zip(cols, row):
        vale = next(v for v in VALES if v["id"] == vid)
        usado = vid in vales_usados
        seleccionado = st.session_state.vale_a_confirmar == vid

        with col:
            # Azul pastel para vales disponibles y usados
            if usado:
                bg = "#f3f3f3"   # azul pastel apagado
                txt = "#777"  # gris-azulado
                extra = '<p style="margin:0; margin-top:10px; font-size:0.85rem; color:#6B7A8C;">Ya has usado este vale.</p>'
            else:
                bg = "#E6F0FA"   # azul pastel claro
                txt = "#1F3B57"  # azul suave oscuro
                extra = ""

            html_card = f"""
            <div style="
                border-radius: 14px;
                padding: 16px;
                border: 1px solid #b8c6d9;
                box-shadow: 0 0 10px rgba(0,0,0,0.03);
                background-color: {bg};
                min-height: 180px;
                margin-bottom: 20px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            ">
                <div>
                    <h4 style="margin:0 0 .5rem 0; color:{txt};">{vale['titulo']}</h4>
                    <p style="margin:0 0 .75rem 0; color:{txt};">{vale['texto']}</p>
                </div>
                {extra}
            </div>
            """

            st.markdown(html_card, unsafe_allow_html=True)

            # ------------ BOTÓN USAR ------------
            if not usado and not seleccionado:
                if st.button("Usar este vale", key=f"usar_{vid}", use_container_width=True):
                    st.session_state.vale_a_confirmar = vid
                    st.rerun()

            # ------------ CONFIRMACIÓN JUSTO DEBAJO ------------
            if seleccionado:
                st.info(
                    f"¿Quieres usar **{vale['titulo']}**?\n\n“{vale['texto']}”",
                )
                c1, c2 = st.columns(2)

                with c1:
                    if st.button("Sí, gastar", key=f"confirmar_{vid}"):
                        vales_usados.add(vid)
                        guardar_estado(pin, vales_usados)
                        st.session_state.vale_a_confirmar = None
                        st.rerun()

                with c2:
                    if st.button("No, cancelar", key=f"cancelar_{vid}"):
                        st.session_state.vale_a_confirmar = None
                        st.rerun()

st.divider()

# =========================
# Sidebar: ver / descargar / reactivar
# =========================

with st.sidebar.expander("Zona para mí (estado de vales)"):
    usados_sorted = sorted(list(vales_usados))
    st.write("Vales usados:", usados_sorted)

    # Reactivar
    if usados_sorted:
        opciones = {vid: next(v["titulo"] for v in VALES if v["id"] == vid) for vid in usados_sorted}
        seleccion = st.multiselect(
            "Selecciona vales para reactivar:",
            options=list(opciones.keys()),
            format_func=lambda vid: opciones[vid],
        )

        if st.button("Reactivar seleccionados"):
            for vid in seleccion:
                vales_usados.discard(vid)
            guardar_estado(pin, vales_usados)
            st.success("Vales reactivados")
            st.rerun()
    else:
        st.caption("No hay vales usados todavía.")

    # Descargar JSON
    json_data = json.dumps({"vales_usados": list(vales_usados)}, ensure_ascii=False, indent=2)
    st.download_button(
        "Descargar JSON",
        data=json_data,
        file_name=f"estado_vales_{pin}.json",
        mime="application/json",
    )
