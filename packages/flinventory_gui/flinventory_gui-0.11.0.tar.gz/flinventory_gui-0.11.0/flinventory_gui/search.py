"""Search in a thing list."""

import argparse
import asyncio
import datetime
import importlib.resources
import itertools
import logging
import os.path
import random
import re
import string
import sys
import time
from typing import Optional, Iterable, cast, Sequence
import nicegui
from nicegui import ui
import i18n

import flinventory
from flinventory import BoxedThing, inventory_io, Inventory, generate_labels

try:
    # for running in a package
    from . import thing_editor
    from . import images
    from . import translation
except ImportError:
    # for running locally
    import thing_editor
    import images
    import translation

STATIC_DIRECTORY = "website_resources"
"""Directory in the data directory where static files are located."""
FAVICON = "favicon.ico"
"""File name of the favicon in the STATIC_DIRECTORY."""
TRANSLATION_DIRECTORY = "translation"
"""Directory within STATIC_DIRECTORY with translation files."""

gl_options: argparse.Namespace
"""Global (module-wide) variables."""


def t(key: str, **kwargs) -> str:
    """Translate a string, suitable for this module and the current user locale.

    Translation string for this module are located in translation/search.LOCALE.yml.

    Fallback locale is english but that should never be used since the language in
    the user storage should be set.

    Args:
        key: the key in the yml file for the string looked for
        kwargs: further arguments for t
    """
    return i18n.t(
        f"search.{key}",
        locale=nicegui.app.storage.user.get(
            "locale", gl_inventory.options.languages[0]
        ),
        **kwargs,
    )


def get_options() -> argparse.Namespace:
    """Abuse argparse for collecting file names."""
    parser = argparse.ArgumentParser()
    inventory_io.add_file_args(parser)
    parser.add_argument(
        "--port",
        "-p",
        help="Port on which to serve the website.",
        type=int,
        default=11111,
    )
    parser.add_argument(
        "--host",
        help="Host on which to run. "
        "For some cases 0.0.0.0 is necessary for accessability from outside. "
        "Passed to nicegui.ui.run.",
        default="0.0.0.0",
    )
    parser.add_argument(
        "--title",
        help="Title shown in the tab name in the browser.",
        default="Fahrradteile",
    )
    parser.add_argument(
        "--no-auto-show",
        help="Do not load website in browser immediately.",
        action="store_false",
        dest="auto_show",
    )
    return parser.parse_args()


def load_data() -> Inventory:
    """Load data from text files and save to global thing list.

    Could implement that data is only loaded when necessary.
    Then an argument force would be useful to reload.

    Note that old things and other data might still be floating around.

    The only real added benefit of this function is the timing.

    Returns:
        the loaded inventory. Can be used to replace gl_inventory
    """
    start = time.monotonic()
    inventory = Inventory.from_json_files(directory=gl_options.dataDirectory)
    end = time.monotonic()
    print(f"Data loaded in {end-start} seconds.")
    ui.notify(f"Data loaded in {end-start} seconds.", position="top", type="positive")
    return inventory


def save_data() -> None:
    """Save things to files.

    This should be used sparingly because it needs to open and write hundreds of files,
    mostly unnecessary since during every change data is already written.
    """
    gl_inventory.save()
    ui.notify(message="Data saved", position="top", type="positive")


def antilen(string: str):
    """Return a bigger number for shorter strings, except 0 for ""."""
    return 1 / len(string) if string else 0


async def find_things(
    things: list[BoxedThing], search_string: str, max_number: int = 10
) -> Iterable[BoxedThing]:
    """Gives things that the user might have searched for.

    Args:
        things: the list of things to search in
        search_string: Input of user
        max_number: maximum number of returned things
    Returns:
        - list of things that include the search string
        - list of things that fuzzily include the search string
        both lists together have a maximum number of max_number elements
    """
    fuzzy = re.compile(
        ".*"
        + ".*".join(filter(lambda char: char not in string.whitespace, search_string))
        + ".*",
        flags=re.IGNORECASE,
    )
    score_categories = ("startswith", "startswithLower", "inLower", "fuzzy")

    def match_score_one(text: Optional[str]) -> dict[str, float]:
        """Sortable tuple of decreasing importance. Compare just text to search string."""
        if text is None:
            return {category: 0 for category in score_categories}
        return {
            "startswith": antilen(text) if text.startswith(search_string) else 0,
            "startswithLower": (
                antilen(text) if text.lower().startswith(search_string.lower()) else 0
            ),
            "inLower": (antilen(text) if search_string.lower() in text.lower() else 0),
            "fuzzy": antilen(text) if bool(fuzzy.match(text)) else 0,
        }

    def max_scores(scores: Sequence[dict[str, float]]) -> dict[str, float]:
        """Use best score.

        Assume that all dicts have the same keys: score_categories

        Args:
            scores: tuple[score_category : score]
        Returns:
            category: max_score
        """
        try:
            return {
                category: max((score[category] for score in scores))
                for category in score_categories
            }
        except ValueError:  # if iterable is empty
            return {category: 0 for category in score_categories}

    def match_score(thing: BoxedThing) -> tuple[float, ...]:
        """Return sortable tuple of decreasing importance.

        Good matches have high numbers.
        """
        assert isinstance(thing, BoxedThing)
        score_name = match_score_one(thing.best("name", backup=""))
        assert isinstance(thing.get("name", {}), dict)
        assert all(isinstance(name, str) for name in thing.get("name", {}).values())
        score_name_lang = max_scores(
            list(
                map(
                    match_score_one,
                    cast(Iterable[str], cast(dict, thing.get("name", {})).values()),
                )
            )
        )
        score_name_alt = max_scores(
            list(
                map(
                    match_score_one,
                    itertools.chain(
                        *cast(dict[str, tuple[str]], thing.get("name_alt", {})).values()
                    ),
                )
            )
        )
        score_description = max_scores(
            list(
                map(
                    match_score_one,
                    cast(
                        Iterable[str], cast(dict, thing.get("description", {})).values()
                    ),
                )
            )
        )
        return (
            score_name["startswith"],
            score_name_lang["startswith"],
            score_name["startswithLower"],
            score_name_lang["startswithLower"],
            score_name_alt["startswith"],
            score_name_alt["startswithLower"],
            score_name["inLower"],
            score_name_lang["inLower"],
            score_name_alt["inLower"],
            score_name["fuzzy"],
            score_name_lang["fuzzy"],
            score_name_alt["fuzzy"],
            score_description["inLower"],
            score_description["fuzzy"],
        )

    if search_string:
        scored_things = [(thing, match_score(thing)) for thing in things]
        good_matches = list(
            map(
                lambda pair: pair[0],
                sorted(
                    filter(lambda pair: any(pair[1][:9]), scored_things),
                    key=lambda pair: pair[1],
                    reverse=True,
                )[:max_number],
            )
        )
        if len(good_matches) < max_number:
            less_good_matches = list(
                map(
                    lambda pair: pair[0],
                    sorted(
                        filter(
                            lambda pair: any(pair[1][9:])
                            and pair[0] not in good_matches,
                            scored_things,
                        ),
                        key=lambda pair: pair[1],
                        reverse=True,
                    )[: max_number - len(good_matches)],
                )
            )
        else:
            less_good_matches = []
        return good_matches, less_good_matches
    return [], []


def switch_language(language: str = "en") -> None:
    """Set the given language in the browser storage and reload the page to apply the change."""
    nicegui.app.storage.user["locale"] = language
    ui.navigate.reload()


def navigation_row():
    """Add a navigation row with save and page change buttons."""
    # this function will probably be called by every user, so setting the locale
    # here will make sure that it is set when needed
    nicegui.app.storage.user.setdefault("locale", gl_inventory.options.languages[0])
    nicegui.app.storage.user.setdefault("expert_mode", False)
    with ui.row():
        ui.button(t("search")).on_click(lambda click_event: ui.navigate.to(search_page))
        with ui.button().on_click(edit_random_thing):
            ui.image(images.DICE).classes("w-7 h-7 m-auto")
        ui.button(t("add_thing")).on_click(lambda click_event: new_thing())
        # ui.button("Save").on_click(lambda click_event: save_data())
        ui.button(t("info")).on_click(lambda click_event: ui.navigate.to(info_page))
        ui.button("English").on_click(lambda click_event: switch_language("en"))
        ui.button("Deutsch").on_click(lambda click_event: switch_language("de"))
        ui.switch(t("expert")).bind_value(nicegui.app.storage.user, "expert_mode")


def edit_random_thing():
    """Display editing window for a random thing, preferring those with less information."""
    weights = [
        (10 if thing.get(("name", 0), None) is None else 0)
        + (7 if thing.get(("name", 1), None) is None else 0)
        + 5 / (len(thing.get(("name_alt", 0), [])) + 1)
        + 4 / (len(thing.get(("name_alt", 1), [])) + 1)
        + 1 / (len(thing.get("part_of", [])) + 1)
        + 1 / (1 + len(thing.get("subclass_of", [])) + 1)
        + (0 if thing.thing.image_path() is None else 5)
        for thing in gl_inventory
    ]
    ui.navigate.to(
        f"/editThing/{gl_inventory.get_id(random.choices(gl_inventory, weights, k=1)[0])}"
    )


@ui.page("/info")
def info_page():
    """Show basic information about the program."""
    navigation_row()
    ui.markdown(
        """
        # flinventory GUI
        This is an instance of the GUI for flinventory.
        The source code can be found on [Codeberg](https://codeberg.org/flukx/flinventory-gui).
        Thanks for hosting!
        You are welcome to use it also for your workshop, improve it and
        share your experiences.

        # Attribution
        This code uses [a pencil image by Dazzle UI](https://www.svgrepo.com/svg/532977/pencil)
        under the Attribution CC BY licence.

        This code use [a copy image by javisperez](https://www.svgrepo.com/svg/493667/copy-clipboard-memory-editor-copy-paste-document)
        under the Apache license.
        """
    )
    ui.button(t("create_all_signs"), on_click=sign_print).bind_visibility_from(
        nicegui.app.storage.user, "expert_mode"
    )


@ui.page("/signprint")
def sign_print():
    """Create pdf with all signs for printing."""
    start_notification = ui.notification(t("Start_sign_pdf"), type="ongoing")
    os.makedirs(gl_options.output_dir, exist_ok=True)
    try:
        pdf = gl_sign_printer.create_signs_pdf(gl_inventory)
    except flinventory.constant.MissingProgramError as missing_latex:
        ui.notify(
            f"Program {missing_latex.program_name} is missing on the server. Cannot create signs.",
            type="negative",
        )
    except FileNotFoundError as other_error:
        ui.notify(
            f"Some problem occured: {other_error}", type="negative", multi_line=True
        )
    except flinventory.signprinter_latex.LaTeXError as latex_error:
        ui.notify(f"LaTeX exited with error. No sign pdf could be created.")
    else:
        ui.notify(t("Success_sign_pdf"), type="positive")
        ui.download(
            pdf,
            f"signs_{datetime.datetime.now().isoformat()}.pdf",
            media_type="application/pdf",
        )
    finally:
        start_notification.dismiss()


@ui.page("/editThing/{thing}")
def edit_thing(thing: Optional[str] = None):
    """A page that allows to edit a thing and possibly create it.

    Args:
        thing: the id of the thing (its directory name)
          if empty or None or 'new' or 'neu', create a new thing
    """
    print("thing_definer called")
    navigation_row()
    if thing in (None, "", "new", "neu"):
        thing = gl_inventory.get_id(gl_inventory.add_thing())
        print(f"Create new thing {thing}")
        ui.navigate.to(f"/editThing/{thing}")
    with ui.card() as card:
        print("Show thing changer:")
        try:
            thing_to_edit = gl_inventory.get_by_id(cast(str, thing))
        except KeyError:
            ui.navigate.to(f"/editThing/new")
        else:
            thing_editor.show_thing_changer(
                card, thing_to_edit, gl_inventory, gl_sign_printer
            )


def new_thing():
    """Open a dialog to add a new thing."""
    thing = gl_inventory.get_id(gl_inventory.add_thing())
    print(f"Create new thing {thing}")
    ui.navigate.to(f"/editThing/{thing}")


def display_thing(card: ui.card, thing: BoxedThing) -> None:
    """Create ui elements showing information about the given thing.

    Args:
        card: the ui.card in which to display the information
        thing: thing with information
    """
    # supplying card and thing as default arguments makes it use the current
    # value instead of the value at the time of usage

    def change_card(_, c: ui.element = card, t: BoxedThing = thing):
        thing_editor.show_thing_changer(c, t, gl_inventory, gl_sign_printer)

    with card:
        print(
            f"Create card {id(card)} for {thing.best('name', backup=thing.best("name_alt", backup=["??"])[0])}."
        )

        with ui.row(wrap=False):
            with ui.column():
                with ui.row():
                    ui.label(text=(primary_name := thing.best("name", backup="??")))
                    secondary_name = thing.get(("name", 1), None)
                    if secondary_name and (secondary_name != primary_name):
                        ui.label(text=f"({secondary_name})").style("font-size: 70%")
                    with ui.button().on_click(change_card):
                        ui.image(images.PENCIL).classes("w-5 h-5 m-auto")
                    with ui.button() as copy_button:
                        copy_button.on_click(
                            lambda event: ui.clipboard.write(gl_inventory.get_id(thing))
                        )
                        copy_button.on_click(
                            lambda event: ui.notify(
                                f"Copied ID {gl_inventory.get_id(thing)} for "
                                f"{thing.best('name', backup="?")} to clipboard.",
                                type="info",
                            )
                        )
                        copy_button.tooltip(
                            t("copy_id")
                            # "Copy ID to clipboard to enter. Use it to add this to other things."
                        )
                        ui.image(images.COPY).classes("w-5 h-5 m-auto")
                if other_names := ", ".join(
                    itertools.chain(*cast(dict, thing.get("name_alt", {})).values())
                ):
                    ui.label(other_names).style("font-size: 70%")
                for description in thing.get("description", {}).values():
                    ui.markdown(description).style("font-size: 70%")
                if thing.location:
                    with ui.label(thing.location.long_name):
                        ui.tooltip(thing.where)
                if super_things := gl_inventory.ancestors(thing, "subclass_of"):
                    with ui.row():
                        ui.label(t("subclass_of")).style("font-size: 70%")
                        for super_thing in super_things:
                            ui.link(
                                text=super_thing.best("name", backup="?"),
                                target=f"/thing/{gl_inventory.get_id(super_thing)}",
                            ).style("font-size: 70%")
                if super_things := gl_inventory.super_things(thing):
                    with ui.row():
                        ui.label(t("part_of")).style("font-size: 70%")
                        for super_thing in super_things:
                            ui.link(
                                text=super_thing.best("name", backup="?"),
                                target=f"/thing/{gl_inventory.get_id(super_thing)}",
                            ).style("font-size: 70%")
            if image := thing.thing.image_path():
                ui.image(image).props("width=50%").props("height=100px").props(
                    "fit='scale-down'"
                )


@ui.page("/thing/{thing}")
def show_thing(thing: str):
    """Show information about a thing."""
    navigation_row()
    card = ui.card()
    try:
        boxed_thing = gl_inventory.get_by_id(thing)
    except KeyError:
        with card:
            ui.label(
                "No such thing exists unfortunately. "
                "You can create a new one with the button above."
            )
    else:
        display_thing(card, boxed_thing)


async def list_things(
    ui_element: nicegui.ui.element,
    things: tuple[Iterable[BoxedThing], Iterable[BoxedThing]],
) -> None:
    """Replaces content of ui_element with information about the things.

    Args:
        ui_element: Some UI element that can be changed.
        things: things to be displayed, both good and less good options
    """
    # gives other searches 10 ms time to abort this display which might take long
    await asyncio.sleep(0.01)
    ui_element.clear()
    with ui_element:
        for thing in things[0]:
            card = ui.card()
            display_thing(card, thing)
        if not things[0]:
            ui.label(t("no_good_matches"))
        ui.button(t("add_thing")).on_click(lambda click_event: new_thing())
        if things[1]:
            ui.label(t("less_good_matches"))
            for thing in things[1]:
                card = ui.card()
                display_thing(card, thing)
            ui.button(t("add_thing")).on_click(lambda click_event: new_thing())


@ui.page("/")
def search_page() -> None:
    """Create a NiceGUI page with a search input field and search results.

    Uses global gl_inventory thing list.
    """
    print("(Re)build search page.")
    # UI container for the search results.
    results: Optional[ui.element] = None

    # Search queries (max. 1) running. Here to be cancellable by different search coroutines.
    running_queries: list[asyncio.Task] = []

    navigation_row()

    async def search(event: nicegui.events.ValueChangeEventArguments) -> None:
        """Search for cocktails as you type.

        Args:
            event: the input field change event. The new value event.value is used.
        """
        print(f"Event type: {type(event)=} with {event.value=}")
        if running_queries:
            for query in running_queries:
                query.cancel()
        sleep = asyncio.create_task(asyncio.sleep(0.5))
        running_queries.append(sleep)
        try:
            await sleep
        except asyncio.exceptions.CancelledError:
            # the next letter was already typed, do not search and rerender for this query
            return
        query = asyncio.create_task(find_things(gl_inventory, event.value))
        running_queries.append(query)
        try:
            start = time.monotonic()
            response = await query
            end = time.monotonic()
            if end - start > 0.01:
                print(f"Query {event.value}: {end - start} seconds")
        except asyncio.exceptions.CancelledError:
            pass
        else:
            if results:
                display = asyncio.create_task(list_things(results, response))
                running_queries.append(display)
                try:
                    start = time.monotonic()
                    await display
                    if end - start > 0.01:
                        print(f"Display {event.value}: {end - start} seconds")
                except asyncio.exceptions.CancelledError:
                    pass
            else:
                ui.notify("Internal error: results element is None.")

    ui.input(on_change=search).props(
        'autofocus outlined rounded item-aligned input-class="ml-3"'
    ).classes("w-96 self-center mt-24 transition-all")
    results = ui.column()


gl_options = get_options()
gl_inventory = load_data()
gl_sign_printer = flinventory.SignPrinterLaTeX(gl_options)
FAVICON_PATH = os.path.join(
    gl_options.dataDirectory, flinventory.constant.DISPLAY_RESOURCES, "favicon.ico"
)


def main_run(reload: bool = False):
    """Start the Nicegui server.

    Args:
        reload: True for reload on file changes. Set to true for development setup.
            Otherwise, leave at False as an entrypoint for a ready-to-use program.
    """
    # todo: make verbosity a command-line option
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    i18n.set("fallback", gl_inventory.options.languages[0])
    i18n.load_path.append(
        os.path.join(
            gl_options.dataDirectory,
            flinventory.constant.DISPLAY_RESOURCES,
            TRANSLATION_DIRECTORY,
        )
    )
    with importlib.resources.as_file(
        importlib.resources.files(translation)
    ) as translation_dir:
        print(f"Load translations from {translation_dir.as_posix()}")
        i18n.load_path.append(translation_dir.as_posix())

        # lock=True assumes that the translation files do not change (that's true)
        # and is supposed to improve performance.
        # also it might be necessary since the files do not exist anymore when the context
        # manager from importlib is closed
        i18n.load_everything(lock=True)
    ui.run(
        title=gl_options.title,
        favicon=FAVICON_PATH if os.path.isfile(FAVICON_PATH) else None,
        language="de",
        host=gl_options.host,
        port=gl_options.port,
        reload=reload,
        show=gl_options.auto_show,
        uvicorn_reload_includes="*py,translation/**/*.yml",
        storage_secret="anyWeirdString",  # this is necessary for app.storage.* to work,
        # but I do not understand it and how it is secret
    )


if __name__ in {"__main__", "__mp_main__"}:
    main_run(reload=True)
