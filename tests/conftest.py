"""Configuración común de las pruebas.

Matplotlib tiene que usar un backend sin ventana: `panel()` dispara su callback
en cuanto se construye, y ese callback dibuja. Con un backend interactivo,
`plt.show()` se queda esperando a que alguien cierre una ventana que nadie va a
ver, y el suite se cuelga.
"""
import matplotlib

matplotlib.use("Agg")
