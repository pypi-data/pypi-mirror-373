import time
import math
import types
import tkinter as tk
import pybirdsreynolds.const as const
import pybirdsreynolds.params as params
import pybirdsreynolds.variables as variables
import pybirdsreynolds.reynolds as reynolds
from tkinter import font
from pybirdsreynolds.reynolds import move_birds
from pybirdsreynolds.args import display_range

root = None
canvas = None


def patch_1():

    # TODO BUGFIX
    root.geometry(
        f"{variables.WIDTH_PARAMS + params.WIDTH +1+ variables.WIDTH_CONTROLS}x{max(params.HEIGHT -1, variables.HEIGHT_PARAMS_CONTROLS)}"
    )


def patch_2():
    # TODO BUGFIX
    root.geometry(
        f"{variables.WIDTH_PARAMS + params.WIDTH +3+ variables.WIDTH_CONTROLS}x{max(params.HEIGHT -3, variables.HEIGHT_PARAMS_CONTROLS)}"
    )


def next_frame():
    if variables.PAUSED:
        move_birds(True, False)
        draw_birds()


def update():
    """
    Main loop: update simulation, redraw, and track FPS.

    - If not paused: move birds, redraw, count frames, compute FPS.
    - If paused: reset FPS counters.
    - Reschedules itself with `root.after`.

    Returns:
        None
    """
    if not variables.PAUSED:
        move_birds(True, False)
        draw_birds()
        draw_status_overlays()
        variables.FRAME_COUNT += 1
        now = time.time()
        if not variables.COUNT:
            variables.LAST_TIME = now
            variables.COUNT = True
        # to stabilize fps
        if now - variables.LAST_TIME >= 1.0:
            variables.FPS_VALUE = variables.FRAME_COUNT / (now - variables.LAST_TIME)
            variables.FRAME_COUNT = 0
            variables.LAST_TIME = now
    # reset fps if paused
    else:
        variables.FRAME_COUNT = 0
        variables.COUNT = False
        variables.FPS_VALUE = 0

    root.after(params.REFRESH_MS, update)


def draw_panels(fullRefreshControls, on_other_key, start_repeat, stop_repeat):
    """
    Draw/update parameter and control panels on the canvas.

    - Build parameter/control lines from `params`.
    - Highlight selected param and attach tooltips.
    - If `fullRefreshControls=True`, create or update buttons (params & controls).
    - Handles button bindings for click/repeat navigation.
    - Clears everything if panels are hidden.
    """
    normal_font = font.Font(
        family=params.FONT_TYPE, size=params.FONT_SIZE, weight="normal"
    )

    # Build display lines:
    # - *_DOC → params with a docstring
    # - *_TEXT → control buttons with label + command
    lines = [
        f"{name.removesuffix('_DOC'):15} :     {str(getattr(params, name.removesuffix('_DOC'))).split(maxsplit=1)[0]}"
        for name in vars(params)
        if name.endswith("_DOC") and getattr(params, f"{name[:-4]}_ACTIVATED") == 2
    ] + [
        f"{name.removesuffix('_TEXT'):15} : {getattr(params, name)} [{getattr(params, name.replace('_TEXT', '_COMMAND'))}]"
        for name in vars(params)
        if name.endswith("_TEXT") and getattr(params, f"{name[:-5]}_ACTIVATED") == 2
    ]
    # Initial offsets
    x_text = 10
    y_text = 10
    # Clear previous drawings
    canvas.delete("controls")
    canvas.delete("params")

    # If panels are hidden → clear buttons and return
    if variables.WIDTH_PARAMS == 0 and variables.WIDTH_CONTROLS == 0:
        canvas.delete("params_button")
        canvas.delete("controls_button")
        for name in dir(params):
            if name.endswith(("_BUTTON", "_BUTTON_UP", "_BUTTON_DOWN")):
                setattr(params, name, None)
        return

    i_param = -1
    i_control = -1
    y_pos_control = 0

    # Iterate through each line to draw parameters & controls
    for i, line in enumerate(lines):
        key = line.split()[0]
        font_to_use = normal_font
        fill = variables.FILL_COLOR

        # Highlight selected param if arrows navigation is active
        if i == params.SELECTED_INDEX and params.ARROWS_ACTIVATED > 0:
            i_param = i_param + 1
            fill = "red"
            item = canvas.create_text(
                x_text + variables.WIDTH_CONTROLS + params.WIDTH,
                y_text + i_param * 2.3 * params.FONT_SIZE,
                anchor="nw",
                fill=fill,
                font=font_to_use,
                tags="params",
                text=line.lower(),
            )
            # Tooltip: docstring + value range
            add_canvas_tooltip(
                item,
                getattr(params, key.upper() + "_DOC")
                + " ("
                + display_range(key.upper())
                + ")",
            )
        # If it's a control line ([...]) -tooltip will be made later
        elif "[" in line:
            i_control = i_control + 1
        # Else → standard param
        elif not "[" in line:
            i_param = i_param + 1
            item = canvas.create_text(
                x_text + variables.WIDTH_CONTROLS + params.WIDTH,
                y_text + i_param * 2.3 * params.FONT_SIZE,
                anchor="nw",
                fill=variables.FILL_COLOR,
                font=font_to_use,
                tags="params",
                text=line.lower(),
            )
            add_canvas_tooltip(
                item,
                getattr(params, key.upper() + "_DOC")
                + " ("
                + display_range(key.upper())
                + ")",
            )

        # Track control & param vertical positions
        y_pos_control = y_text + i_control * 2.3 * 2 * params.FONT_SIZE
        y_pos_param = y_text + i_param * 2.3 * params.FONT_SIZE - 5

        # --- Full refresh: create/update buttons ---
        if fullRefreshControls:
            first_colon_index = line.find(":") + 1
            f = font.Font(font=font_to_use)
            x_offset = 0

            # Case: control button (with icon + command)
            if "[" in line:
                key = line.split()[0]
                btn_font = (params.FONT_TYPE, params.FONT_SIZE * 2)
                btn_width = 2
                btn_height = 1
                highlight_color = "black"
                highlight_thickness = 2

                name_button = key + "_BUTTON"
                key = line.split()[0]
                icon = getattr(params, key.upper() + "_ICON")
                cmd = getattr(params, key.upper() + "_COMMAND")

                lbl_btn_tmp = tk.Label(
                    canvas,
                    text=icon,
                    fg="black",
                    bg="white",
                    font=btn_font,
                    width=btn_width,
                    height=btn_height,
                    anchor="center",
                    highlightbackground=highlight_color,
                    highlightthickness=highlight_thickness,
                )

                tooltip_text = f"{getattr(params, key.upper() + '_TEXT')} [{getattr(params, key.upper() + '_COMMAND')}]"
                add_widget_tooltip(lbl_btn_tmp, tooltip_text)

                # Bind button → simulate key event
                lbl_btn_tmp.bind(
                    "<Button-1>",
                    lambda e, c=cmd: on_other_key(types.SimpleNamespace(keysym=c)),
                )

                # Create or reposition control button
                if getattr(params, name_button, None) is None:
                    setattr(
                        params,
                        name_button,
                        canvas.create_window(
                            x_text + x_offset + 2,
                            y_pos_control,
                            anchor="nw",
                            window=lbl_btn_tmp,
                            tags=("controls_button",),
                        ),
                    )
                else:
                    canvas.coords(
                        getattr(params, name_button),
                        x_text + x_offset + 2,
                        y_pos_control,
                    )

            # Case: param with +/- buttons (if arrows are active)
            first_colon_index = line.find(":") + 1
            f = font.Font(font=font_to_use)
            x_offset = f.measure(line[:first_colon_index])
            if "[" not in line and params.ARROWS_ACTIVATED > 0:
                highlight_color = "black"
                highlight_thickness = 1
                # LEFT/DOWN CASE
                name_button_down = key + "_BUTTON_DOWN"
                lbl_left = tk.Label(
                    canvas,
                    text="<",
                    fg="black",
                    bg="white",
                    font=font_to_use,
                    highlightbackground=highlight_color,
                    highlightthickness=highlight_thickness,
                )
                lbl_left.bind(
                    "<ButtonPress-1>", lambda e, l=line: start_repeat(l, "Left")
                )
                lbl_left.bind("<ButtonRelease-1>", lambda e: stop_repeat())
                # create op update button's position
                if (
                    not hasattr(params, name_button_down)
                    or getattr(params, name_button_down) is None
                ):
                    setattr(
                        params,
                        name_button_down,
                        canvas.create_window(
                            x_text
                            + x_offset
                            + 1
                            + variables.WIDTH_CONTROLS
                            + params.WIDTH,
                            y_pos_param,
                            anchor="nw",
                            window=lbl_left,
                            tags=("params_button",),
                        ),
                    )
                else:
                    canvas.coords(
                        getattr(params, name_button_down),
                        x_text + x_offset + 1 + variables.WIDTH_CONTROLS + params.WIDTH,
                        y_pos_param,
                    )

                # RIGHT/UP CASE
                name_button_up = key + "_BUTTON_UP"
                lbl_right = tk.Label(
                    canvas,
                    text=">",
                    fg="black",
                    bg="white",
                    font=font_to_use,
                    highlightbackground=highlight_color,
                    highlightthickness=highlight_thickness,
                )
                lbl_right.bind(
                    "<ButtonPress-1>", lambda e, l=line: start_repeat(l, "Right")
                )
                lbl_right.bind("<ButtonRelease-1>", lambda e: stop_repeat())
                # create op update button's position
                if (
                    not hasattr(params, name_button_up)
                    or getattr(params, name_button_up) is None
                ):
                    setattr(
                        params,
                        name_button_up,
                        canvas.create_window(
                            x_text
                            + x_offset
                            + 18
                            + variables.WIDTH_CONTROLS
                            + params.WIDTH,
                            y_pos_param,
                            anchor="nw",
                            window=lbl_right,
                            tags=("params_button",),
                        ),
                    )
                else:
                    canvas.coords(
                        getattr(params, name_button_up),
                        x_text
                        + x_offset
                        + 18
                        + variables.WIDTH_CONTROLS
                        + params.WIDTH,
                        y_pos_param,
                    )


def draw_status_overlays():
    """
    Draw overlay messages on the canvas (paused, FPS, hidden panels, average point).

    - Shows "PAUSED" when simulation is paused.
    - Displays FPS value (or "NA/...").
    - Indicates when panels are hidden.
    - Marks average position if enabled.
    """
    canvas.delete("paused")
    if variables.PAUSED:
        canvas.create_text(
            variables.WIDTH_CONTROLS,
            max(params.HEIGHT, variables.HEIGHT_PARAMS_CONTROLS),
            anchor="sw",
            fill="red",
            font=(params.FONT_TYPE, params.FONT_SIZE, "bold"),
            tags="paused",
            text=" PAUSED ",
        )
    canvas.delete("fps")
    if variables.FPS:
        if not variables.PAUSED:
            if variables.FPS_VALUE == 0:
                value = "..."
            else:
                value = f"{variables.FPS_VALUE:.1f}"
        else:
            value = "NA"
        canvas.create_text(
            variables.WIDTH_CONTROLS,
            0,
            anchor="nw",
            fill="gray",
            font=(params.FONT_TYPE, params.FONT_SIZE, "bold"),
            tags="fps",
            text=f" FPS : {value}",
        )
    canvas.delete("hidden")
    if variables.HIDDEN:
        canvas.create_text(
            variables.WIDTH_CONTROLS + params.WIDTH,
            max(params.HEIGHT, variables.HEIGHT_PARAMS_CONTROLS),
            anchor="se",
            fill="gray",
            font=(params.FONT_TYPE, params.FONT_SIZE),
            tags="hidden",
            text="h to restore panels ",
        )
    canvas.delete("average")
    if variables.AVERAGE:
        canvas.create_oval(
            variables.AVG_X - 2 * params.SIZE,
            variables.AVG_Y - 2 * params.SIZE,
            variables.AVG_X + 2 * params.SIZE,
            variables.AVG_Y + 2 * params.SIZE,
            fill="red",
            outline="red",
            tag="average",
        )


def draw_box():
    if not is_maximized():
        const.WIDTH_BEFORE_MAXIMIZED = params.WIDTH
        const.HEIGHT_BEFORE_MAXIMIZED = params.HEIGHT
    canvas.delete("boundary")
    canvas.create_rectangle(
        variables.WIDTH_CONTROLS,
        0,
        variables.WIDTH_CONTROLS + params.WIDTH,
        params.HEIGHT,
        outline=variables.FILL_COLOR,
        width=const.MARGIN,
        tags="boundary",
    )


def draw_root():
    if not variables.HIDDEN:
        root.geometry(
            f"{variables.WIDTH_PARAMS+params.WIDTH+variables.WIDTH_CONTROLS+2}x{max(params.HEIGHT, variables.HEIGHT_PARAMS_CONTROLS)}"
        )
        canvas.config(
            width=variables.WIDTH_PARAMS + params.WIDTH + variables.WIDTH_CONTROLS + 2,
            height=max(params.HEIGHT, variables.HEIGHT_PARAMS_CONTROLS),
            bg=variables.CANVAS_BG,
        )
    else:
        root.geometry(
            f"{params.WIDTH}x{max(params.HEIGHT, variables.HEIGHT_PARAMS_CONTROLS)}"
        )
        root.minsize(params.WIDTH, params.HEIGHT)
        root.maxsize(params.WIDTH, params.HEIGHT)
        width_tmp = params.WIDTH
        height_tmp = params.HEIGHT
        root.update()
        root.minsize(params.WIDTH_MIN, params.HEIGHT_MIN)
        root.maxsize(10000, 10000)
        root.update()
        params.WIDTH = width_tmp
        params.HEIGHT = height_tmp


def is_maximized():
    if root.tk.call("tk", "windowingsystem") == "aqua":
        return bool(root.attributes("-fullscreen"))
    if root.state() == "zoomed":
        return True
    try:
        if root.attributes("-zoomed"):
            return True
    except tk.TclError:
        pass
    return (
        root.winfo_width() >= root.winfo_screenwidth()
        and root.winfo_height() >= root.winfo_screenheight()
    )


def draw_birds():
    fill = variables.FILL_COLOR
    outline = variables.OUTLINE_COLOR
    size = params.SIZE
    cos_150 = math.cos(math.radians(150))
    sin_150 = math.sin(math.radians(150))

    triangle_size = 6 * size
    triangle_width = 4 * size

    # First creation of positions
    if not variables.POINTS_ID:
        for (x, y), (vx, vy) in zip(reynolds.birds, reynolds.velocities):
            if not params.TRIANGLES:
                pid = canvas.create_oval(
                    x - size,
                    y - size,
                    x + size,
                    y + size,
                    fill=fill,
                    outline=outline,
                    tag="bird",
                )
            else:
                angle = math.atan2(vy, vx)
                cos_a, sin_a = math.cos(angle), math.sin(angle)

                tip_x = x + cos_a * triangle_size
                tip_y = y + sin_a * triangle_size

                left_x = x + (cos_a * cos_150 - sin_a * sin_150) * triangle_width
                left_y = y + (sin_a * cos_150 + cos_a * sin_150) * triangle_width

                right_x = x + (cos_a * cos_150 + sin_a * sin_150) * triangle_width
                right_y = y + (sin_a * cos_150 - cos_a * sin_150) * triangle_width

                pid = canvas.create_polygon(
                    tip_x,
                    tip_y,
                    left_x,
                    left_y,
                    right_x,
                    right_y,
                    fill=fill,
                    outline=outline,
                    tag="bird",
                )
            variables.POINTS_ID.append(pid)

    # Update positions
    for pid, (x, y), (vx, vy) in zip(
        variables.POINTS_ID, reynolds.birds, reynolds.velocities
    ):
        if not params.TRIANGLES:
            canvas.coords(pid, x - size, y - size, x + size, y + size)
        else:
            angle = math.atan2(vy, vx)
            cos_a, sin_a = math.cos(angle), math.sin(angle)

            tip_x = x + cos_a * triangle_size
            tip_y = y + sin_a * triangle_size

            left_x = x + (cos_a * cos_150 - sin_a * sin_150) * triangle_width
            left_y = y + (sin_a * cos_150 + cos_a * sin_150) * triangle_width

            right_x = x + (cos_a * cos_150 + sin_a * sin_150) * triangle_width
            right_y = y + (sin_a * cos_150 - cos_a * sin_150) * triangle_width

            canvas.coords(pid, tip_x, tip_y, left_x, left_y, right_x, right_y)

    # Delete uncesserary points
    if len(variables.POINTS_ID) > len(reynolds.birds):
        for pid in variables.POINTS_ID[len(reynolds.birds) :]:
            canvas.delete(pid)
        variables.POINTS_ID = variables.POINTS_ID[: len(reynolds.birds)]
    # Create missing points
    elif len(variables.POINTS_ID) < len(reynolds.birds):
        for x, y in reynolds.birds[len(variables.POINTS_ID) :]:
            if not params.TRIANGLES:
                pid = canvas.create_oval(
                    x - size,
                    y - size,
                    x + size,
                    y + size,
                    fill=fill,
                    outline=outline,
                    tag="bird",
                )
            else:
                angle = math.atan2(0, 1)  # orientation par défaut
                cos_a, sin_a = math.cos(angle), math.sin(angle)

                tip_x = x + cos_a * triangle_size
                tip_y = y + sin_a * triangle_size

                left_x = x + (cos_a * cos_150 - sin_a * sin_150) * triangle_width
                left_y = y + (sin_a * cos_150 + cos_a * sin_150) * triangle_width

                right_x = x + (cos_a * cos_150 + sin_a * sin_150) * triangle_width
                right_y = y + (sin_a * cos_150 - cos_a * sin_150) * triangle_width

                pid = canvas.create_polygon(
                    tip_x,
                    tip_y,
                    left_x,
                    left_y,
                    right_x,
                    right_y,
                    fill=fill,
                    outline=outline,
                    tag="bird",
                )
            variables.POINTS_ID.append(pid)


def maximize_minimize(force):
    if is_maximized():
        root.state("normal")
        try:
            root.attributes("-zoomed", False)
        except tk.TclError:
            pass
        if not force:
            params.WIDTH = const.WIDTH_BEFORE_MAXIMIZED
            params.HEIGHT = const.HEIGHT_BEFORE_MAXIMIZED
    else:
        const.WIDTH_BEFORE_MAXIMIZED = params.WIDTH
        const.HEIGHT_BEFORE_MAXIMIZED = params.HEIGHT

        wm = root.tk.call("tk", "windowingsystem")
        if wm == "aqua":  # macOS
            root.attributes("-fullscreen", True)
        elif wm == "win32":  # Windows
            root.state("zoomed")
        else:  # Linux
            try:
                root.attributes("-zoomed", True)
            except tk.TclError:
                root.attributes("-fullscreen", True)
    root.focus_force()
    root.focus_set()


def show_tip(widget, text, event=None, dx=10, dy=10, wraplength=200):

    if variables.TIP_WINDOW is not None:
        try:
            variables.TIP_WINDOW.destroy()
        except:
            pass
        variables.TIP_WINDOW = None

    if not text:
        return

    if event:
        x = widget.winfo_rootx() + event.x + dx
        y = widget.winfo_rooty() + event.y + dy
    else:
        x = widget.winfo_rootx() + dx
        y = widget.winfo_rooty() + widget.winfo_height() + dy

    variables.TIP_WINDOW = tw = tk.Toplevel(widget)
    tw.wm_overrideredirect(True)
    tw.wm_geometry(f"+{x}+{y}")
    label = tk.Label(
        tw,
        text=text,
        background=variables.INFO_COLOR,
        relief="solid",
        borderwidth=1,
        font=(params.FONT_TYPE, params.FONT_SIZE),
        wraplength=wraplength,
    )
    label.pack(ipadx=4, ipady=2)


def hide_tip(event=None):
    if variables.TIP_WINDOW:
        variables.TIP_WINDOW.destroy()
        variables.TIP_WINDOW = None


def add_canvas_tooltip(item, text):
    canvas.tag_bind(item, "<Enter>", lambda e: show_tip(canvas, text, e))
    canvas.tag_bind(item, "<Leave>", hide_tip)


def add_widget_tooltip(widget, text):
    widget.bind("<Enter>", lambda e: show_tip(widget, text))
    widget.bind("<Leave>", hide_tip)


def on_resize(on_other_key, start_repeat, stop_repeat, event):
    if variables.TRANS_HIDDEN:
        params.WIDTH = max(
            event.width - variables.WIDTH_PARAMS - variables.WIDTH_CONTROLS,
            params.WIDTH_MIN,
        )
        params.HEIGHT = max(event.height, variables.HEIGHT_PARAMS_CONTROLS)
        move_birds(False, False)
        draw_birds()
        draw_box()
        draw_status_overlays()
        variables.TRANS_HIDDEN = False
        return
    # TODO BUGIFX
    params.WIDTH = max(
        event.width - variables.WIDTH_PARAMS - variables.WIDTH_CONTROLS - 2,
        params.WIDTH_MIN,
    )
    params.HEIGHT = max(event.height, variables.HEIGHT_PARAMS_CONTROLS)
    # params.WIDTH = max(event.width - variables.WIDTH_PARAMS - variables.WIDTH_CONTROLS,params.WIDTH_MIN)
    # params.HEIGHT = max(event.height,const.HEIGHT_PARAMS_CONTROLS_DEFAULT)
    move_birds(False, False)
    draw_panels(True, on_other_key, start_repeat, stop_repeat)
    draw_birds()
    draw_box()
    draw_status_overlays()
