import ipywidgets as widgets
from IPython.display import display, HTML, Javascript
from typing import Callable


def chatbot_ui(bot: Callable[[str], str], height="300px"):
    # Output widget for chat messages
    chat_output = widgets.Output(
        layout=widgets.Layout(
            width="100%", height=height, border="1px solid black", overflow="auto"
        )
    )
    chat_output.add_class("chat-container")

    # Input widgets
    user_input = widgets.Text(placeholder="Type a message:", continuous_update=False)
    send_button = widgets.Button(description="Send", button_style="success")

    # Store chat history
    chat_history = []

    # Simple bot logic

    # Render chat bubbles inside Output widget
    def render_chat():
        with chat_output:
            chat_output.clear_output(wait=True)
            # Build HTML for all messages
            html = "<div style='display:flex; flex-direction:column; gap:5px;'>"
            for sender, msg in chat_history:
                if sender == "user":
                    html += f"""
                    <div style='align-self:flex-end; background-color:#DCF8C6; padding:5px 10px;
                                border-radius:10px; max-width:70%; word-wrap:break-word;'>{msg}</div>
                    """
                else:
                    html += f"""
                    <div style='align-self:flex-start; background-color:#E8E8E8; padding:5px 10px;
                                border-radius:10px; max-width:70%; word-wrap:break-word;'>{msg}</div>
                    """
            html += "</div>"
            display(HTML(html))

            # Scroll to bottom inside Output widget
            display(
                Javascript(
                    f"""
            var container = document.querySelector('.chat-container');
            if (container) {{
                container.scrollTop = container.scrollHeight;
            }}
            """
                )
            )

    # Send message function
    def send_message(msg):
        msg = msg.strip()
        if msg:
            chat_history.append(("user", msg))
            chat_history.append(("bot", bot(msg)))
            render_chat()
            user_input.value = ""

    # Bind button click
    send_button.on_click(lambda _: send_message(user_input.value))

    # Bind Enter key using observe
    def on_enter(change):
        send_message(change["new"])

    user_input.observe(on_enter, names="value")

    # Layout: chat on top, input below
    chat_ui = widgets.VBox([chat_output, widgets.HBox([user_input, send_button])])

    display(chat_ui)
