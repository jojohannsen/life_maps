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

@rt("/artistic-card")
def artistic_card():
    return Card(
        CardHeader(
            Div("Diana", cls="font-serif italic bold text-sm"),
            cls="p-2"
        ),
        CardBody(
            DivCentered(
                Div(
                    P("b. 1937", cls="font-sans text-sm text-gray-600 inline-block"),
                    Div(cls="w-48 h-2 bg-cyan-500 inline-block ml-4"),
                    cls="flex items-center"
                ),
            ),
            cls="p-2"
        ),
        cls=(CardT.hover, "max-w-sm", "m-4")  # Add hover effect and max width
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
