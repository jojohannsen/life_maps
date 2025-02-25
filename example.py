Div(
    Button('Dropdown', type='button', cls='uk-button uk-button-default'),
    Div(
        Ul(
            Li(
                A('Active', href='#'),
                cls='uk-active'
            ),
            Li(
                A('Item', href='#')
            ),
            Li('Header', cls='uk-nav-header'),
            Li(
                A('Item', href='#')
            ),
            Li(
                A('Item', href='#')
            ),
            Li(cls='uk-nav-divider'),
            Li(
                A('Item', href='#')
            ),
            cls='uk-nav uk-dropdown-nav'
        ),
        uk_dropdown=''
    ),
    cls='uk-inline'
)