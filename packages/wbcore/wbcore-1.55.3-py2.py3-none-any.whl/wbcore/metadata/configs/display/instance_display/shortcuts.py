from .display import Display
from .layouts import Inline, Layout, Section
from .operators import default
from .pages import Page
from .styles import Style


def create_simple_display(
    grid_template_areas: list[list[str]],
    sections: list[Section] | None = None,
    inlines: list[Inline] | None = None,
) -> Display:
    """Creates a simple display without having to specify all the intermediary classes

    Args:
        grid_template_areas: 2D string array containing all fields that should be displayed
        sections: A list of sections included in the `grid_template_areas`
        inlines: A list of inlines if necessary.

    Returns:
        A `Display` containing 1 `Page` with all fields in 1 `Section` with all columns and rows having the same dimensions

    """
    return Display(
        pages=[
            Page(
                layouts={
                    default(): Layout(
                        grid_template_areas=grid_template_areas,
                        grid_auto_columns=Style.fr(1),
                        inlines=inlines if inlines else [],
                        sections=sections if sections else [],
                    )
                }
            )
        ]
    )


def create_simple_section(
    key: str,
    title: str,
    grid_template_areas: list[list[str]] | None = None,
    inline_key: str | None = None,
    extra_display_kwargs: dict | None = None,
    **kwargs,
) -> Section:
    """Creates a simple section without having to specify everything

    Args:
        key: A string that will be later referenced in the display's `grid_template_areas`
        title: A string which is used as a header
        grid_template_areas: 2D string array containing all fields that should be displayed
        inline_key: if the section is a nested table, the inline is the corresponding endpoint
        extra_display_kwargs: an additional dictionary for create_simple_display parameters.

    Returns:
        A `Section` containing a simple `Display`

    """
    return Section(
        key=key,
        title=title,
        display=create_simple_display(
            grid_template_areas=grid_template_areas if grid_template_areas else [],
            inlines=[Inline(key=inline_key, endpoint=inline_key)] if inline_key else [],
            **extra_display_kwargs if extra_display_kwargs else {},
        ),
        **kwargs,
    )


def create_simple_page_with_inline(title: str, key: str) -> Page:
    return Page(
        title=title,
        layouts={
            default(): Layout(
                grid_template_areas=[[key]], grid_template_rows=["100%"], inlines=[Inline(key=key, endpoint=key)]
            )
        },
    )
