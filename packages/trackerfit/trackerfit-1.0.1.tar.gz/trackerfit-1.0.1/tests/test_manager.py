# tests/test_manager.py
# -------------------------------
# Requierements
# -------------------------------
from trackerfit import SessionManager

# -------------------------------
# Helpers
# -------------------------------
def test_sesion_inicia_vacia():
    manager = SessionManager()
    assert not manager.sesion_activa()
