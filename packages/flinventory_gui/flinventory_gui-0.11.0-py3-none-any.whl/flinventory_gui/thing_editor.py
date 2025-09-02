"""Functions and classes for a display that allows changing the information about a thing."""

import asyncio
import itertools
import os
import urllib.request
import urllib.error
from typing import (
    Union,
    Callable,
    Any,
    Literal,
    Optional,
    override,
    cast,
    Iterable,
    MutableMapping,
)
import i18n
import filetype

import nicegui
from nicegui import ui
import nicegui.events

import flinventory
from flinventory import BoxedThing

try:
    from . import images
except ImportError:
    import images

# maybe better move this to flinventory
ACCEPTED_IMAGE_TYPES = (
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
    "image/tiff",
    "image/svg",
)


def t(key: str, **kwargs) -> str:
    """Translate a string, suitable for this module and the current user locale.

    Translation string for this module are located in translation/search.LOCALE.yml.

    Fallback locale is "en" but this should never be used because the locale should
    be set to the primary language of the inventory.

    Args:
        key: the key in the yml file for the string looked for
        kwargs: further arguments for the i18n.t function
    """
    return i18n.t(
        f"thing_editor.{key}",
        locale=nicegui.app.storage.user.get("locale", "en"),
        **kwargs,
    )


def try_conversion(
    value: str, conversions: Iterable[Union[Callable[[str], Any], Literal["bool"]]]
) -> Any:
    """Try to convert value into other values.

    Args:
        value: value to be converted
        conversions: tuple of conversion functions that raise Exception upon failure
            or "bool" which converts the strings "true", "false"
    """
    for conversion in conversions:
        if conversion == "bool":
            try:
                low_value = value.lower()
            except AttributeError:
                continue
            if low_value == "true":
                return True
            if low_value == "false":
                return False
            continue
        try:
            return conversion(value)
        except Exception:  # pylint: disable=broad-exception-caught
            pass
    return value


class SlowInputSaver[Container: MutableMapping]:
    """Saves content of an input field to a dict-like (a BoxedThing).

    Does so with a bit of delay to avoid creating save operations if
    new letters are typed immediately after.

    Can be used as an on-change-action connected to an input field.

    Maybe it makes sense to make SlowInputSaver dependent on the type of the data
    object. We will see.
    """

    def __init__(
        self,
        data: Container,
        member: flinventory.defaulted_data.Key,
        wait_time: Union[float, int] = 1,
        post_handlers: Optional[list[Callable[[], None]]] = None,
    ):
        """Create a SlowInputSaver.

        Args:
            data: the data object (think thing) to be altered
            member: which information to be altered. thing[member] = <something suitable>
                must be allowed
            wait_time: how long (in seconds) the saver should wait
                until it assumes no further changes and actually saves input
            post_handlers: Functions or callable objects that are done after the setter function.
                Or None, then nothing is done.
        """
        self.data = data
        self.member = member
        self.wait_time = wait_time
        self._running_queries: list[asyncio.Task] = []
        self.post_handlers = [] if post_handlers is None else post_handlers

    def converter(self, value: Any) -> Any:
        """A hook for subclasses to override for value conversion.

        Since subclasses might do different things with it, it needs to stay a method.
        The linter gets it by actually overriding it in another class. (Where it still
        could be a static method.)
        """
        return value

    def setter(self, value: Any):
        """How the value of the input element is saved.

        This can be overridden by subclasses.
        """
        if not value:
            try:
                del self.data[self.member]
            except KeyError:
                # already gone, so already fine
                pass
        else:
            self.data[self.member] = value

    async def __call__(self, event: nicegui.events.ValueChangeEventArguments):
        """Value has changed. Now save it. If saving is not cancelled by further changes."""
        for query in self._running_queries:
            query.cancel()
        sleep = asyncio.create_task(asyncio.sleep(self.wait_time))
        self._running_queries.append(sleep)
        try:
            await sleep
        except asyncio.exceptions.CancelledError:
            # the next letter was already typed, do not search and rerender for this query
            return
        self.setter(self.converter(event.value))
        if self.post_handlers is not None:
            for post_handler in self.post_handlers:
                post_handler()


class TooltipSetter:
    """Class that is function to set the tooltip of an input field."""

    def __init__(
        self,
        thing: BoxedThing,
        input_ui: ui.element,
        tooltip: Callable[[BoxedThing], str],
    ):
        """Create a tooltip setter."""
        self.thing = thing
        self.input = input_ui
        self.tooltip = tooltip

    def __call__(self, event: Any = None):
        """Set the result of the tooltip function as the tooltip of the ui element."""
        self.input.tooltip(self.tooltip(self.thing))


class PrintNullifier:
    """Class that is a function to set the sign to not printed."""

    def __init__(self, thing: BoxedThing, printed_switch: ui.switch):
        """Create the PrintNullifier."""
        self.thing = thing
        self.switch = printed_switch

    def __call__(self, event: Any = None):
        """Set the sign of the thing the switch to not printed."""
        self.thing.sign["printed"] = False
        self.switch.value = not self.thing.sign.get("printed", False)


class SlowSignChanger(SlowInputSaver[flinventory.Sign]):
    """Special case for signs: add resetting printed attribute."""

    @override
    def setter(self, value: Any):
        """Sets the value and sets printed to false."""
        if not value:
            if "printed" in self.data and self.member in self.data:
                del self.data["printed"]
            try:
                del self.data[self.member]
            except KeyError:
                # already not there, fine
                pass
        else:
            previous = self.data.get(self.member, "")
            self.data[self.member] = try_conversion(
                value,
                (
                    cast(Callable[[str], Any], int),
                    cast(Callable[[str], Any], float),
                    "bool",
                ),
            )
            if previous != self.data[self.member]:
                try:
                    del self.data["printed"]
                except KeyError:
                    pass


class SlowListChanger(SlowInputSaver):
    """Special case for alt names: add splitting at ;

    This is for simple lists with several strings in one input field.
    """

    @override
    def converter(self, value: Any) -> Any:
        """Split at ;."""
        return list(filter(None, map(str.strip, value.split(";"))))


class SlowLocationSaver(SlowInputSaver[flinventory.Location]):
    """Special case for location info."""

    def __init__(
        self,
        data: flinventory.Location,
        level: flinventory.Schema,
        ui_element: ui.element,
        wait_time: float = 0.3,
    ):
        """Create a special saver that handles location data.

        Args:
            data: the location
            level: the level including the level name that is changed
            ui_element: the ui element that needs update after a change
            wait_time: time in seconds waited before saving for case of quickly changed input
        """
        # wait less long because I want to quickly get the autocompletion
        # and the next input field
        super().__init__(data, level.levelname, wait_time=wait_time)
        self.level = level
        self.ui_element = ui_element

    @override
    def converter(self, value: Any) -> Any:
        """Convert to bool or int if possible."""
        return try_conversion(value, (int, "bool"))

    @override
    def setter(self, value: Any):
        """Set the value and update the ui."""
        if value in self.data.EMPTY:
            self.data[self.level.levelname] = value
            update_location_element(
                self.ui_element,
                loc=self.data,
                focus=self.level.levelname,
            )
            return
        try:
            sub_schema = self.level.get_subschema(value)
        except flinventory.location.InvalidLocationSchema as error:
            print("InvalidLocationSchema: ", error)
        except flinventory.location.InvalidLocation:
            print(f"InvalidLocation {value}: Do not save")
        else:
            # if possible focus on subschema level because that is the one
            # that most likely needs to be edited next:
            try:
                focus = sub_schema.levelname
            except flinventory.location.InvalidLocation:
                focus = self.level.levelname
            self.data[self.level.levelname] = value
            update_location_element(
                self.ui_element,
                loc=self.data,
                focus=focus,
            )


def update_location_element(
    location_ui_element, loc: flinventory.Location, focus: Optional[str] = None
) -> dict[str, SlowLocationSaver]:
    """List location information with input fields.

    Args:
        location_ui_element: ui_element which content get replaced
        loc: location data to be displayed
        focus: the level name of the schema which input field should have the cursor
            None if no focus should be set
    Returns:
        SlowInputSavers that should get sign changers as post handlers because changes influence
        the sign of the thing
    """
    location_ui_element.clear()
    slow_changers = {}
    with location_ui_element:
        location_info = loc.to_jsonable_data()
        schema_hierarchy = loc.schema.get_schema_hierarchy(loc)
        ui.label(str(schema_hierarchy[0].name))
        editable_levelnames = []
        for level in schema_hierarchy:
            try:
                level_name = level.levelname
            except flinventory.location.InvalidLocation:
                # bottom most location (in hierarchy) has no subs and therefore
                # needs no input
                continue
            else:
                editable_levelnames.append(level_name)
            # some Value error because it gets value Werkstatt from somewhere:
            if subs := level.get_valid_subs(shortcuts="no"):
                current_value = location_info.get(level.levelname, "")
                options = (
                    ([current_value] if current_value not in subs else [])
                    + ([""] if (current_value != "" and "" not in subs) else [])
                    + subs
                )
                ui.select(
                    options=options,
                    label=t(level.levelname),
                    value=current_value,
                    clearable=True,
                    with_input=True,
                    # new_value_mode="add",
                    on_change=(
                        slow_changer := SlowLocationSaver(
                            loc, level, location_ui_element, wait_time=0
                        )
                    ),
                ).props(
                    "autogrow dense" + (" autofocus" if level_name == focus else "")
                )
            else:
                ui.input(
                    label=t(level.levelname),
                    value=str(location_info.get(level.levelname, "")),
                ).props(
                    "autogrow dense" + (" autofocus" if level_name == focus else "")
                ).on_value_change(
                    slow_changer := SlowLocationSaver(loc, level, location_ui_element)
                )
            slow_changers[f"location.{level_name}"] = slow_changer
        additional_info = [
            (key, value)
            for key, value in location_info.items()
            if not key in editable_levelnames
        ]
        if additional_info:
            ui.label(t("unused_location_info") + ":")
        for key, value in additional_info:
            ui.label(f"{t(key)}: {value}")
        return slow_changers


class SignImageUpdater:
    """Class that is a function to update a nicegui element with the current sign image

    Without the slow stuff and event handling.
    """

    def __init__(
        self,
        thing: BoxedThing,
        image_element: ui.image,
        sign_creator: flinventory.SignPrinterLaTeX,
    ):
        """Create the SignImageUpdater."""
        self.thing = thing
        self.ui_element = image_element
        self.sign_creator = sign_creator

    def __call__(self, event: Any = None):
        """Recreate the sign image.

        args:
            event: ignore it
        """
        # takes a while, should be done async. Let's see if it is annoying in the usage.
        svg_file = self.sign_creator.create_sign_svg(self.thing)
        if svg_file:
            if os.path.isfile(svg_file):
                ui.notify("Created sign preview", type="positive")
                self.ui_element.set_source(svg_file)
            else:
                ui.notify(
                    f"Finished sign preview generation but image {svg_file} is missing.",
                    type="negative",
                )
                self.ui_element.set_source("")
        else:
            ui.notify("Error during sign preview generation.", type="negative")


def update_sign_element(
    sign_ui_element: ui.element,
    thing: BoxedThing,
    options: flinventory.Options,
    sign_printer: flinventory.SignPrinterLaTeX,
) -> list[Callable[[], None]]:
    """Replace content of sign_ui_element with input fields for the sign.

    Args:
        sign_ui_element: a nice_gui element, usually an ui.column which content
            gets replaced by input fields
        thing: thing which's sign should be displayed and is changable by the new input fields
        options: options including the languages
        sign_printer: Sign printer instance that can generate sign svgs

    Returns:
        list of callables that should be called if the sign is changed somehow, e.g. by a new name
    """
    input_fields: dict[tuple[str, str] | str, ui.element] = {}
    sign = thing.sign
    with sign_ui_element:
        sign_image = ui.image(images.PENCIL)
        print_switch = ui.switch(
            text=t("print_needed"),
            value=not sign.get("printed", False),
            on_change=lambda event, s=sign: s.__setitem__("printed", not event.value),
        )
        print_switcher = PrintNullifier(thing, print_switch)
        sign_image_updater = SignImageUpdater(thing, sign_image, sign_printer)
        sign_image.on("click", sign_image_updater)

        # each slow input changer has to get each sign updater as a post handler:
        sign_updaters: list[Callable[[], None]] = [print_switcher, sign_image_updater]
        slow_changers = {}

        for sign_member, lang, tooltip in (
            ("width", "", "[cm]"),
            # cm needs to be replaced by options.length_unit once this option is actually used
            ("height", "", "[cm]"),
            (
                "name",
                options.languages[0],
                lambda th: f"{t("default")}: {th.get(("name", 0), t("default_main_name"))}",
            ),
            (
                "name",
                options.languages[1],
                lambda th: f"{t("default")}: {th.get(("name", 1), t("default_main_name"))}",
            ),
            (
                "fontsize",
                options.languages[0],
                # :.3g is format specifier for 3 digits, ignoring 0 at end
                lambda th: f"{t("default")}: {sign_printer.guess_font_size(th)[0]:.3g}",
            ),
            (
                "fontsize",
                options.languages[1],
                lambda th: f"{t("default")}: {sign_printer.guess_font_size(th)[1]:.3g}",
            ),
            (
                "imageheight",
                "",
                lambda th: f"[{options.length_unit}]; {t("default")}: {sign_printer.image_height_vspace(
                    th, sign_printer.height(th))[0]}",
            ),
            (
                "location_shift_down",
                "",
                f"{t("default")}: {flinventory.signprinter_latex.STANDARD_LOCATION_SHIFT_DOWN}",
            ),
        ):
            label = f"{t('sign')} {t(sign_member)} {f'({t(lang)})' if lang else ''}"
            member = (sign_member, lang) if lang else sign_member
            slow_changers[f"sign.{member}"] = SlowSignChanger(sign, member)
            input_fields[f"sign.{member}"] = (
                ui.input(
                    label=label,
                    value=str(sign.get_undefaulted(member, backup="")),
                )
                .props("autogrow dense")
                .on_value_change(slow_changers[f"sign.{member}"])
            )
            if isinstance(tooltip, str):
                input_fields[f"sign.{member}"].tooltip(tooltip)
            elif tooltip is not None:
                assert callable(
                    tooltip
                ), f"tooltip must be str or callable, but it is {str(tooltip)}"
                tooltip_updater = TooltipSetter(
                    thing, input_fields[f"sign.{member}"], tooltip=tooltip
                )
                tooltip_updater()
                sign_updaters.append(tooltip_updater)
        ui.switch(
            text=t("location_shortened"),
            value=not sign.get("location_long", True),
            on_change=lambda event, s=sign: s.__setitem__(
                "location_long", not event.value
            ),
        ).on_value_change(sign_image_updater).on_value_change(print_switcher)
        # move it to the end. it was necessary to define at the beginning to have
        # it available for creating the click/ change handling
        sign_image.move(sign_ui_element)
    for slow_changer in slow_changers.values():
        slow_changer.post_handlers.extend(sign_updaters)
    return sign_updaters


class SlowImageFetcher(SlowInputSaver[flinventory.Thing]):
    """Special case for image url.

    In addition to saving the inputted URL,
    this saver tries to fetch the specified url and saves it as an image if it is one.

    If the fetched file is huge, this might be problematic.
    Do I assume no malicious actor?
    """

    @override
    def converter(self, value: str) -> str:
        """Add http if no protocol is given."""
        if "://" not in value:
            return "http://" + value
        return value

    @override
    def setter(self, value: str):
        """Saves the URL and tries to save the linked image.

        If the url is removed, the image is not removed. Need a separate button for that.
        If an image exists, it is overwritten.
        It is assumed that there is some data backup system like a git repository.

        todo: show image after download.
        """
        super().setter(value)
        try:
            if any(
                value.lower().endswith(extension := image_type)
                for image_type in flinventory.constant.IMAGE_FILE_TYPES
            ):
                extension = "." + extension
            else:
                extension = ""
            destination_file_name = os.path.join(
                self.data.directory, flinventory.constant.IMAGE_FILE_BASE + extension
            )
            urllib.request.urlretrieve(value, destination_file_name)
        except urllib.error.ContentTooShortError as interrupted:
            ui.notify(
                f"Error downloading image from {value}: \n"
                f"reason: {interrupted.reason}\n"
                f"aim filename: {interrupted.filename}\n"
                f"other info: {interrupted.args}, {interrupted}",
                type="negative",
            )
        except ValueError as unknown_url:
            ui.notify(
                f"No download of {value} possible: {unknown_url}", type="negative"
            )
        except urllib.error.HTTPError as http_error:
            ui.notify(f"Download unsuccessful: {http_error}.", type="negative")
        except FileNotFoundError as directory_missing:
            ui.notify(
                f"Saving image failed. Programming error: {directory_missing}",
                type="negative",
            )
        except OSError as network_unreachable:
            if network_unreachable.errno == 101:
                ui.notify(
                    "No internet connection. Cannot download image but the url is saved.",
                    type="negative",
                )
        else:
            if not os.path.isfile(destination_file_name):
                ui.notify(t("image_not_downloaded"), type="negative")
            else:
                ui.notify(t("image_downloaded"), type="positive")
                # todo: move this utility to flinventory
                # because it could be used, together with trimming for more images
                if extension == "":
                    # no extension given in the URL, so try to guess it from the file
                    image_type = filetype.guess(destination_file_name)
                    if image_type is None:
                        ui.notify(t("type_guess_failed"), type="negative")
                    else:
                        os.rename(
                            destination_file_name,
                            destination_file_name + "." + image_type.extension,
                        )
                        destination_file_name + "." + image_type.extension


class SlowThingListAdder(SlowInputSaver):
    """Adds a thing id to a list if input is unique.

    This is for lists where the elements are thing IDs.
    """

    def __init__(
        self,
        inventory: flinventory.inventory_io.Inventory,
        thing: flinventory.defaulted_data.DefaultedDict,
        member: flinventory.defaulted_data.Key,
        list_ui_element: ui.element,
        input_element: ui.input,
        description: Optional[str],
    ):
        """Create the ListRemover and tell it what to remove and what to update afterward.

        Args:
            inventory: Inventory needed for calling update_list_input
            thing: defaulted dict (so far only things) to be changed
            member: which list should be changed (the key)
            list_ui_element: nicegui ui element to be called update_list_input
            input_element: nicegui input element which might get additional letters
            description: argument of update_list_input called afterward
        """
        super().__init__(thing, member)
        self.inventory = inventory
        self.list_ui_element = list_ui_element
        self.input_element = input_element
        self.description = description

    @override
    def setter(self, value: Any):
        """Add new thing if value is unique.

        If new thing is added, reload list ui element.
        """
        try:
            new_thing = self.inventory.get_by_id(value)
        except KeyError:
            new_thing_options = itertools.chain(
                self.inventory.get_by_key(("name", lang), value)
                for lang in self.inventory.options.languages
            )
            new_thing = None  # default if Iterator is empty
            for new_thing in new_thing_options:
                # use first element
                break
            # else:
            #     could add code to fill the input field as much as all options agree
            for _ in new_thing_options:
                ui.notify(t("ambiguous_name", name=value))
                new_thing = None
                break
        if new_thing is not None:
            assert isinstance(self.data.get(self.member, tuple()), tuple), (
                f"{self.data.best('name', backup="?")} is not a tuple but "
                f"{self.data.get[self.member]} of type {type(self.data.get[self.member])}"
                f" (in Adder)."
            )
            self.data[self.member] = list(self.data.get(self.member, tuple())) + [
                self.inventory.get_id(new_thing)
            ]
            update_list_input(
                self.list_ui_element,
                self.inventory,
                self.data,
                self.member,
                self.description,
            )


class ListRemover:
    """A function (implemented as a class with __call__) that removes a value from a list.

    Not slow because it is intended for a button which should act immediately.
    """

    def __init__(
        self,
        inventory: flinventory.inventory_io.Inventory,
        thing: flinventory.defaulted_data.DefaultedDict,
        member: flinventory.defaulted_data.Key,
        value_to_be_removed: flinventory.defaulted_data.Immutable,
        ui_element: ui.element,
        description: Optional[str],
    ):
        """Create the ListRemover and tell it what to remove and what to update afterward.

        Args:
            inventory: Inventory needed for calling update_list_input
            thing: defaulted dict (so far only things) to be changed
            member: which list should be changed (the key)
            value_to_be_removed: the value to be removed (not its index)
            ui_element: nicegui ui element to be called update_list_input
            description: argument of update_list_input called afterward
        """
        self.inventory = inventory
        self.thing = thing
        self.member = member
        self.value = value_to_be_removed
        self.ui_element = ui_element
        self.description = description

    def __call__(self, _: Any):
        """Remove the specified element from the list and call update_list_input.

        Ignore the argument.
        """
        current = self.thing.get_undefaulted(self.member, backup=tuple())
        assert isinstance(current, tuple), (
            f"{self.thing.best('name', backup="")}.{self.member} is "
            f"not a tuple but {self.thing[self.member]}."
        )
        new = [value for value in current if value != self.value]
        if new:
            self.thing[self.member] = new
        else:
            del self.thing[self.member]
        update_list_input(
            self.ui_element, self.inventory, self.thing, self.member, self.description
        )


def update_list_input(
    ui_element: ui.element,
    inventory: flinventory.inventory_io.Inventory,
    thing: flinventory.DefaultedDict,
    member: flinventory.defaulted_data.Key,
    description: Optional[str] = None,
) -> None:
    """A set of ui elements for adding and removing references to other things.

    thing[member] must be a tuple. If member is a translatable list member.

    Args:
        ui_element: nicegui element which is cleared and refilled
        inventory: inventory needed to translate names and UUIDs to things
        thing: thing (or other defaulted dict) that should be changed
        member: the key whose value should be changed. Current value can be non-existing.
        description: what is written in front of list to tell the user what s:he is editing.
            If None (default) use member or "_".join(member)
    """
    ui_element.clear()
    if description is None:
        description = member if isinstance(member, str) else "_".join(member)
    with ui_element:
        ui.label(description + ":")
        assert isinstance(thing.get(member, tuple()), tuple), (
            f"{thing.best("name", backup="")}.{member} is not a tuple but "
            f"{thing[member]} of type {type(thing[member])}!"
        )
        for thing_id in thing.get_undefaulted(member, backup=tuple()):
            try:
                other_thing = inventory.get_by_id(thing_id)
            except KeyError:
                # ignore
                continue
            with ui.label():
                ui.link(
                    text=other_thing.best("name", backup="?"),
                    target=f"/thing/{thing_id}",
                    new_tab=True,
                )
                ui.button("X").on_click(
                    ListRemover(
                        inventory, thing, member, thing_id, ui_element, description
                    )
                )
        input_element = ui.input(label=t("new")).props("autogrow dense")
        input_element.on_value_change(
            SlowThingListAdder(
                inventory, thing, member, ui_element, input_element, description
            )
        )


class ImageSaver:
    """Save an uploaded image."""

    def __init__(
        self,
        inventory: flinventory.Inventory,
        thing: flinventory.BoxedThing,
        post_handlers: Optional[list[Callable[[], None]]] = None,
    ):
        """Create a new Image Saver saving a file for the given thing.

        post_handlers are executed after successful upload.
        """
        self.inventory = inventory
        self.thing = thing
        self.post_handlers = [] if post_handlers is None else post_handlers

    def __call__(self, upload: nicegui.events.UploadEventArguments):
        """Save an uploaded image."""
        extension = os.path.splitext(upload.name)[1].lstrip(".").lower()
        # filetype uses jpg as extension, so .jpeg files must be recognized as .jpg to not
        # raise error later on
        extension = {"jpeg": "jpg"}.get(extension, extension)
        checked_filetype = filetype.guess(upload.content)
        if checked_filetype is None:
            ui.notify(f"{t("filetype_unknown")}, {t("ignore")}", type="negative")
        else:
            if (
                checked_filetype.MIME != upload.type
                or checked_filetype.extension != extension
            ):
                ui.notify(
                    f"{t("filetype_nonmatching")}: {checked_filetype.MIME} "
                    f"({checked_filetype.extension}) "
                    f"≠ {upload.type} ({extension}), {t("ignore")}",
                    type="negative",
                )
            elif checked_filetype.MIME in ACCEPTED_IMAGE_TYPES:
                upload.content.seek(0)
                content = upload.content.read()
                path = os.path.join(
                    self.thing.directory, "image." + checked_filetype.extension
                )
                with open(path, mode="wb") as image:
                    image.write(content)
                for image_name in os.listdir(self.thing.directory):
                    image_path = os.path.join(self.thing.directory, image_name)
                    image_type = filetype.guess(image_path)
                    if (
                        image_type is not None
                        and image_type.MIME in ACCEPTED_IMAGE_TYPES
                        and image_path != path
                    ):
                        os.remove(image_path)
                ui.notify(t("image_saved"), type="positive")
                for post_handler in self.post_handlers:
                    post_handler()
            else:
                ui.notify(
                    f"{t("unsupported_image_type")}: {checked_filetype.MIME} "
                    f"(.{checked_filetype.extension})"
                )


def update_thing_basics_element(
    ui_element: nicegui.ui.element,
    thing: BoxedThing,
    inventory: flinventory.inventory_io.Inventory,
) -> dict[str, SlowInputSaver[flinventory.thing]]:
    """Clear content of ui element and instead display editing fields for basic info, like name.

    Returns:
        slow input savers that should get post_handlers to change sign stuff
    """
    ui_element.clear()
    slow_changers = {}
    with ui_element:
        for language in inventory.options.languages:
            member: tuple[str, str] | str
            for member in ("name", "description"):
                input_field = (
                    ui.input(
                        label=f"{t(member)} ({language})",
                        value=thing.thing.get_undefaulted(
                            (member, language), backup=""
                        ),
                    )
                    .props("autogrow dense")
                    .on_value_change(
                        slow_changer := SlowInputSaver(thing.thing, (member, language))
                    )
                )  # thing instead of thing.thing works as well but gives type error
                # since thing is not officially a mapping
                if member == "description":
                    input_field.bind_visibility_from(
                        nicegui.app.storage.user, "expert_mode"
                    )
                slow_changers[f"thing.{member}-{language}"] = slow_changer
            member = "name_alt"
            ui.input(
                label=f"{t(member)} ({language}) ({t("separated", sep=";")})",
                value="; ".join(
                    thing.thing.get_undefaulted((member, language), backup=[])
                ),
            ).props("autogrow dense").on_value_change(
                SlowListChanger(thing.thing, (member, language))
            )
            # the alternative names do not appear on the sign, so do not add the SlowInputSaver
            # to the slow_changer dict
        ui.input(
            label=t("image_url"),
            value=thing.thing.get_undefaulted("image_url", backup=""),
        ).props("dense").on_value_change(
            slow_changer := SlowImageFetcher(thing.thing, "image_url")
        ).bind_visibility_from(
            nicegui.app.storage.user, "expert_mode"
        )
        slow_changers["thing.image_url"] = slow_changer
        ui.upload(
            on_upload=(slow_changer := ImageSaver(inventory, thing)),
            max_file_size=5_000_000,
            on_rejected=lambda event: ui.notify(
                f"{t("filetype_nonmatching")} {event.value}"
            ),
        ).props('accept="' + ",".join(ACCEPTED_IMAGE_TYPES) + '"').props(
            "no-thumbnails"
        ).props(
            f'label="{t("upload_image")}"'
        ).props(
            "auto-upload"
        ).classes(
            "w-full"
        )
        slow_changers["thing.upload_image"] = slow_changer
        for member in ("subclass_of", "part_of"):
            with ui.column().bind_visibility_from(
                nicegui.app.storage.user, "expert_mode"
            ) as super_row:
                update_list_input(
                    super_row,
                    inventory,
                    thing.thing,
                    member,
                    t(member),
                )
    return slow_changers


def show_thing_changer(
    ui_element: nicegui.ui.element,
    thing: BoxedThing,
    inventory: flinventory.inventory_io.Inventory,
    sign_printer: flinventory.SignPrinterLaTeX,
) -> None:
    """Clear content of ui element and instead display editing fields.

    Args:
        ui_element: the ui element (e.g. a card) on which to show the thing changing ui
        inventory: the inventory needed for references to other things. Also used for its options,
            including the languages.
        thing: the thing to change
        sign_printer: a sign printer class. Given as an argument to only create it once which
            means only reading template files once
    """
    options = inventory.options

    print(
        f"Try to let edit {thing.best('name', backup="a new thing")} with {id(ui_element)}."
    )
    ui_element.clear()
    with ui_element:
        with ui.row():
            with ui.column() as basics_column:
                sign_changers = update_thing_basics_element(
                    basics_column, thing, inventory
                )
            with ui.column() as location_column:
                sign_changers.update(
                    update_location_element(location_column, thing.location)
                )
            with ui.column() as sign_column:
                sign_column.bind_visibility_from(
                    nicegui.app.storage.user, "expert_mode"
                )
                sign_updaters = update_sign_element(
                    sign_column, thing, options, sign_printer
                )
            for sign_changer in sign_changers.values():
                sign_changer.post_handlers.extend(sign_updaters)
            if image := thing.thing.image_path():
                ui.image(image).props("width=50%").props("height=100px").props(
                    "fit='scale-down'"
                )
