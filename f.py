from fasthtml.common import *
from monsterui.all import *

app, rt = fast_app(hdrs=Theme.slate.headers())

def IconCard(icon_name):
    return Card(
        DivCentered(
            UkIcon(icon_name, height=40, width=40),
            H4(icon_name, cls="mt-4"),
            cls="p-4"
        ),
        cls=(CardT.hover, "cursor-pointer")  # Use CardT.hover for proper hover effect
    )

def make_colors(color):
    return f"bg-{color}-500", f"bg-{color}-200"

def make_card(name, birth_year, color):
    bright_color, subdued_color = make_colors(color)
    return Div(
            Div(name, cls="mt-1 ml-2 font-serif bold text-sm"),
            DivLAligned(
                P(f"{birth_year}", cls="font-sans ml-2 italic text-xs text-gray-400 inline-block"),
                Div(
                    Div(cls=f"mt-0 w-20 h-2 {subdued_color} group-hover:{bright_color} hover:{bright_color} inline-block ml-2"),
                    Div(cls=f"mt-2 w-20 h-2 {bright_color} group-hover:{bright_color} hover:{bright_color} inline-block"),
                    cls="flex flex-row justify-between h-4"
                ),
                cls="mb-1 ml-1",
            ),
            cls=(CardT.hover, "max-w-sm", "m-4", "w-60", "group")  # Added 'group' class
        )

@rt("/artistic-card")
def artistic_card():
    return Div(
        make_card("Diana", 1937, "yellow"),
        make_card("Johannes", 1959, "orange"),
        make_card("Farahnaz", 1961, "rose"),
        make_card("Hannes", 1933, "slate"),
        make_card("Abbas", 1940, "lime"),
        make_card("Akhtar", 1944, "blue"),
    )

@rt("/")
def get():
    icons = [
        "user", "user-circle", "users", "user-round", 
        "user-cog", "user-check", "male", "female", "baby"
    ]
    
    return Titled("User & Gender Icons",
        Container(
            H1("User & Gender Icons from Lucide"),
            P("Click any icon card to copy its name", cls="mb-6 text-gray-600"),
            Grid(*[IconCard(icon) for icon in icons], 
                 cols_sm=2, cols_md=3, cols_lg=4, 
                 gap=4),
            Script("""
                document.querySelectorAll('.card').forEach(card => {
                    card.onclick = (e) => {
                        const text = card.querySelector('h4').textContent;
                        navigator.clipboard.writeText(text);
                        alert('Copied: ' + text);
                    }
                });
            """)
        )
    )

serve()
