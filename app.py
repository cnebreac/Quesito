# app.py
import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Vales contigo 🧀💛", page_icon="🧀", layout="centered")

# =========================
# Definición de vales
# =========================
VALES = [
    {"id": 0, "titulo": "Abrazo largo 🧀", "texto": "Vale por un abrazo largo que arregla el día."},
    {"id": 1, "titulo": "Charla tranquila 🧀", "texto": "Vale por una conversación sin prisas y sin móviles."},
    {"id": 2, "titulo": "Peli elegida por ti 🧀", "texto": "Vale por elegir tú la peli… incluso si es un horror 😏."},
    {"id": 3, "titulo": "Masaje 🧀", "texto": "Vale por un masaje de 10 minutos donde tú elijas."},
    {"id": 4, "titulo": "Paseo juntos 🧀", "texto": "Vale por un paseo para desconectar del mundo."},
    {"id": 5, "titulo": "Merienda sorpresa 🧀", "texto": "Vale por una merienda improvisada preparada por mí."},
    {"id": 6, "titulo": "Reinicio del día 🧀", "texto": "Vale por borrar lo malo y seguir juntos."},
    {"id": 7, "titulo": "Mimos ilimitados 🧀", "texto": "Vale por un rato de mimos sin límite de tiempo."},
    {"id": 8, "titulo": "Confesión pendiente 🧀", "texto": "Vale por contarte algo bonito que aún no sabes."},
    {"id": 9, "titulo": "Cita especial 🧀", "texto": "Vale por una cita sencilla pero muy tú y yo."},
]

# =========================
# Funciones con PIN
# =========================

def get_json_path(pin: str) -> Path:
    """
    Devuelve la ruta del JSON personal según el PIN.
    """
    safe_pin = pin.replace(" ", "_").replace("/", "_")  # limpiar caracteres raros
    return Path(f"estado_vales_{safe_pin}.json")

def cargar_estado(pin: str):
    """
    Carga los vales usados desde el JSON vinculado al PIN.
    """
    path = get_json_path(pin)
    if not path.exists():
        return set()
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("vales_usados", []))
    except:
        return set()

def guardar_estado(pin: str, vales_usados: set):
    """
    Guarda los vales usados en el JSON vinculado al PIN.
    """
    path = get_json_path(pin)
    with path.open("w", encoding="utf-8") as f:
        json.dump({"vales_usados": list(vales_usados)}, f, ensure_ascii=False, indent=2)

# =========================
# Pantalla de PIN
# =========================
if "pin" not in st.session_state:
    st.session_state.pin = None

if st.session_state.pin is None:
    st.markdown("<h2 style='text-align:center;'>Introduce tu PIN 🧀</h2>", unsafe_allow_html=True)
    pin_input = st.text_input("PIN (puede ser texto, números o emojis 🧀❤️):", type="password")
    
    if st.button("Entrar 🧀"):
        if pin_input.strip() == "":
            st.warning("El PIN no puede estar vacío.")
        else:
            st.session_state.pin = pin_input
            st.experimental_rerun()
    st.stop()

pin = st.session_state.pin
vales_usados = cargar_estado(pin)

# =========================
# Interfaz principal
# =========================

st.markdown(f"<h1 style='text-align: center;'>Vales contigo 🧀💛</h1>", unsafe_allow_html=True)
st.caption(f"PIN activo: **{pin}**")

st.write(
    """
    - Los vales **no usados** están en color normal.  
    - Los vales **usados** se ven en gris y marcados como **🧀 USADO**.  
    - Todo se guarda según tu PIN: si entras mañana con el mismo PIN, verás tu progreso.
    """
)

st.divider()

# =========================
# Mostrar tarjetas
# =========================

n_cols = 2
ids = [v["id"] for v in VALES]
rows = [ids[i:i+n_cols] for i in range(0, len(ids), n_cols)]

for row in rows:
    cols = st.columns(len(row))
    for col, vid in zip(cols, row):
        vale = next(v for v in VALES if v["id"] == vid)
        usado = vid in vales_usados

        if usado:
            bg = "#e8e8e8"
            txt = "#777"
            badge = """
            <div style="padding:3px 8px;border-radius:999px;background:#ccc;
            font-size:0.7rem;font-weight:600;display:inline-block;color:#555;">🧀 USADO</div>
            """
        else:
            bg = "#ffffff"
            txt = "#222"
            badge = ""

        with col:
            st.markdown(
                f"""
                <div style="
                    border-radius: 14px;
                    padding: 16px;
                    background: {bg};
                    border: 1px solid #ddd;
                    box-shadow: 0 0 10px rgba(0,0,0,0.05);
                    color: {txt};
                ">
                    {badge}
                    <h4 style="margin-top:6px;margin-bottom:4px;color:{txt};">{vale['titulo']}</h4>
                    <p style="margin-top:0;color:{txt};">{vale['texto']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if not usado:
                if st.button(f"🧀 Usar vale", key=f"usar_{vid}"):
                    st.session_state.vale_a_confirmar = vid

            else:
                st.markdown(
                    "<span style='font-size:0.8rem;color:#777;'>Ya has usado este vale 🧀</span>",
                    unsafe_allow_html=True
                )

st.divider()

# =========================
# Confirmación
# =========================

vid_conf = st.session_state.get("vale_a_confirmar", None)

if vid_conf is not None and vid_conf not in vales_usados:
    vale_conf = next(v for v in VALES if v["id"] == vid_conf)

    st.info(
        f"¿Seguro que quieres usar el vale **{vale_conf['titulo']}**?\n\n"
        f"“{vale_conf['texto']}”",
        icon="❓"
    )

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Sí, gastar 🧀"):
            vales_usados.add(vid_conf)
            guardar_estado(pin, vales_usados)
            st.session_state.vale_a_confirmar = None
            st.success("Vale usado 🧀✨")
            st.experimental_rerun()

    with c2:
        if st.button("No, cancelar"):
            st.session_state.vale_a_confirmar = None

