"""
NutriBot - UI con Gradio

Ejecutar:
    cd langchain-langgraph-study
    python src/diet_planner/app.py
"""

import os
import sys
from dotenv import load_dotenv

import gradio as gr

# Resolver imports desde cualquier directorio de ejecución
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env")))

from diet_planner import DietChatbot

# ─────────────────────────────────────────────────────────
# Estado de la aplicación (una instancia por sesión)
# ─────────────────────────────────────────────────────────
bot = DietChatbot()
_started = False


def init_chat() -> list:
    """Llamado al cargar la UI: arranca la conversación con el saludo del bot."""
    global _started
    if not _started:
        greeting = bot.start()
        _started = True
        return [(None, greeting)]
    return []


def respond(message: str, history: list) -> tuple[list, str]:
    """Enviar mensaje al bot y actualizar el historial de la UI."""
    if not message.strip():
        return history, ""

    bot_response = bot.chat(message)
    history.append((message, bot_response))
    return history, ""


def generate_plan_action() -> str:
    """Generar el plan de comidas con structured output y mostrarlo."""
    if len(bot.history) < 8:
        return (
            "Todavia no hay suficiente informacion.\n"
            "Completa la conversacion con NutriBot primero:\n"
            "  1. Objetivo\n"
            "  2. Preferencias alimentarias\n"
            "  3. Restricciones/alergias\n"
            "  4. Presupuesto semanal\n"
            "  5. Tiempo disponible para cocinar\n"
            "  6. Numero de personas"
        )
    try:
        bot.generate_plan()
        return bot.format_plan()
    except Exception as e:
        return f"Error generando el plan: {e}"


def reset_action() -> tuple[list, str, str]:
    """Reiniciar el chatbot y la UI por completo."""
    global bot, _started
    bot.reset()
    _started = False
    greeting = bot.start()
    _started = True
    return [(None, greeting)], "", ""


# ─────────────────────────────────────────────────────────
# Interfaz Gradio
# ─────────────────────────────────────────────────────────
with gr.Blocks(title="NutriBot", theme=gr.themes.Soft()) as demo:

    gr.Markdown(
        """
        # NutriBot - Planificacion Dietetica Personalizada
        Habla con NutriBot para que recopile tu informacion y luego genera tu plan semanal.
        """
    )

    with gr.Row():

        # ── Columna izquierda: Chat ──────────────────────────
        with gr.Column(scale=3):
            chatbot_ui = gr.Chatbot(
                label="Conversacion con NutriBot",
                height=520,
                bubble_full_width=False,
                show_label=True,
            )
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Escribe tu mensaje y presiona Enter...",
                    label="",
                    scale=5,
                    container=False,
                )
                send_btn = gr.Button("Enviar", scale=1, variant="primary")

        # ── Columna derecha: Plan ────────────────────────────
        with gr.Column(scale=2):
            gr.Markdown("### Plan de Comidas")
            plan_display = gr.Textbox(
                label="",
                lines=24,
                max_lines=30,
                placeholder="Tu plan aparecera aqui una vez que completes la conversacion y presiones 'Generar Plan'...",
                interactive=False,
            )
            with gr.Row():
                generate_btn = gr.Button("Generar Plan", variant="primary", scale=2)
                reset_btn = gr.Button("Nueva Conversacion", variant="secondary", scale=1)

    # ── Eventos ─────────────────────────────────────────────
    demo.load(init_chat, outputs=[chatbot_ui])

    send_btn.click(respond, inputs=[msg_input, chatbot_ui], outputs=[chatbot_ui, msg_input])
    msg_input.submit(respond, inputs=[msg_input, chatbot_ui], outputs=[chatbot_ui, msg_input])

    generate_btn.click(generate_plan_action, outputs=[plan_display])
    reset_btn.click(reset_action, outputs=[chatbot_ui, msg_input, plan_display])


if __name__ == "__main__":
    demo.launch(share=False)
