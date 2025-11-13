# app.py
import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Vales contigo", page_icon="💛", layout="centered")

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
# Funciones con PIN
# =========================

def get_json_path(pin: str) -> Path:
    """Devuelve la ruta del JSON personal según el PIN."""
    safe_pin = pin.replace(" ", "_").replace("/", "_")
    return Path(f"estado_vales_{safe_pin}.json")

def cargar_estado(pin: str):
    """Carga los vales usados desde el JSON vinculado al PIN."""
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
    """Guarda los vales usados en el JSON vinculado al PIN."""
    path = get_json_path(pin)
    with path.open("w", encoding="utf-8") as f:
        json.dump({"vales_usados": list(vales_usados)}, f, ensure_ascii=False, indent=2)

# =========================
# Pantalla de PIN
# =========================

if "pin" not in st.session_state:
    st.session_state.pin = None

if st.session_state.pin is None:
    st.markdown("## Introduce tu PIN")
    pin_input = st.text_input(
        "PIN (puede ser texto, números o lo que queráis):",
        type="password",
    )

    if st.button("Entrar"):
        if pin_input.strip() == "":
            st.warning("El PIN no puede estar vacío.")
        else:
            st.session_state.pin = pin_input
            st.rerun()
    st.stop()

# A partir de aquí ya tenemos PIN
pin = st.session_state.pin
vales_usados = cargar_estado(pin)

if "vale_a_confirmar" not in st.session_state:
    st.session_state.vale_a_confirmar = None

# =========================
# Interfaz principal
# =========================

st.markdown("# Vales contigo 💛")
st.caption(f"PIN activo: **{pin}**")

st.write(
    """
    - Los vales no usados aparecen en normal.  
    - Los vales usados se ven en gris y marcados como usados.  
    - Todo se guarda según tu PIN: si entras otro día con el mismo PIN, verás el mismo estado.
    """
)

st.divider()

# =========================
# Mostrar tarjetas en cuadrícula
# =========================

n_cols = 2
ids = [v["id"] for v in VALES]
rows = [ids[i:i + n_cols] for i in range(0, len(ids), n_cols)]

for row in rows:
    cols = st.columns(len(row))
    for col, vid in zip(cols, row):
        vale = next(v for v in VALES if v["id"] == vid)
        usado = vid in vales_usados

        with col:
            card = st.container()
            with card:
                if usado:
                    st.markdown(f"#### {vale['titulo']}")
                    st.caption("Ya has usado este vale")
                    st.write(f":grey[{vale['texto']}]")
                else:
                    st.markdown(f"#### {vale['titulo']}")
                    st.write(vale["texto"])
                    if st.button("Usar este vale", key=f"usar_{vid}"):
                        st.session_state.vale_a_confirmar = vid

st.divider()

# =========================
# Confirmación de uso
# =========================

vid_conf = st.session_state.get("vale_a_confirmar", None)

if vid_conf is not None and vid_conf not in vales_usados:
    vale_conf = next(v for v in VALES if v["id"] == vid_conf)

    st.info(
        f"¿Seguro que quieres usar el vale **{vale_conf['titulo']}**?\n\n"
        f"\"{vale_conf['texto']}\""
    )

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Sí, gastar"):
            vales_usados.add(vid_conf)
            guardar_estado(pin, vales_usados)
            st.session_state.vale_a_confirmar = None
            st.success("Vale usado")
            st.rerun()

    with c2:
        if st.button("No, cancelar"):
            st.session_state.vale_a_confirmar = None

