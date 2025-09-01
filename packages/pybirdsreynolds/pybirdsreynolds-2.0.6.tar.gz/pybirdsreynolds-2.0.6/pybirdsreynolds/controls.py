import types
import copy
import sys
import tkinter as tk
import pybirdsreynolds.const as const
import pybirdsreynolds.params as params
import pybirdsreynolds.variables as variables
import pybirdsreynolds.reynolds as reynolds
import pybirdsreynolds.draw as draw
from pybirdsreynolds.args import get_help_text
from pybirdsreynolds.draw import (
    draw_root,
    draw_status_overlays,
    draw_birds,
    draw_panels,
    draw_box,
    maximize_minimize,
    is_maximized,
    next_frame,
)
from pybirdsreynolds.reynolds import move_birds


def signal_handler(sig, frame):
    print("Interrupted! Closing application...")
    draw.root.destroy()
    sys.exit(0)


def on_click(l, sens):
    """
    Select a parameter from a clicked line and trigger navigation.

    - Finds the clicked parameter from `l`.
    - Builds the list of active params (`*_DOC` / `*_TEXT`).
    - Updates `params.SELECTED_INDEX`.
    - Calls `on_other_key` with `sens`.

    Args:
        l (str): Clicked line.
        sens (str): Key direction/action.
    """
    first_word = l.split()[0] if l.split() else None
    lines = [
        f"{name.removesuffix('_DOC'):15} :    {str(getattr(params, name.removesuffix('_DOC'))).split(maxsplit=1)[0]}"
        for name in vars(params)
        if name.endswith("_DOC") and getattr(params, f"{name[:-4]}_ACTIVATED") == 2
    ] + [
        f"{name.removesuffix('_TEXT'):15} :    {getattr(params, name)} [{getattr(params, name.replace('_TEXT', '_COMMAND'))}]"
        for name in vars(params)
        if name.endswith("_TEXT") and getattr(params, f"{name[:-5]}_ACTIVATED") == 2
    ]
    params.SELECTED_INDEX = next(
        (i for i, line in enumerate(lines) if line.split(":")[0].strip() == first_word),
        0,
    )
    on_other_key(types.SimpleNamespace(keysym=sens))


def _repeat(ligne, direction):
    on_click(ligne, direction)
    if variables.REPEATING["active"]:
        variables.REPEATING["job"] = draw.canvas.after(
            100, lambda: _repeat(ligne, direction)
        )


def start_repeat(ligne, direction):
    variables.REPEATING["active"] = True
    _repeat(ligne, direction)


def stop_repeat():
    variables.REPEATING["active"] = False
    if variables.REPEATING["job"]:
        draw.canvas.after_cancel(variables.REPEATING["job"])
        variables.REPEATING["job"] = None


def on_shift_press(event):
    variables.shift_pressed = True


def on_shift_release(event):
    variables.shift_pressed = False


def toggle_pause(event=None):
    variables.BLINK_STATE = True
    variables.PAUSED = not variables.PAUSED
    draw_panels(False, on_other_key, start_repeat, stop_repeat)
    draw_status_overlays()


def on_other_key(event):
    """
    Handle key events for parameter control and UI actions.

    - Shift modifies step size (×10).
    - Arrows: navigate or adjust selected param.
    - Special params: toggle TRIANGLES, COLOR, FREE, FONT_TYPE.
    - Triggers redraw/update (birds, UI panels, messages).
    - Supports commands: reset, regenerate, toggle FPS/pause/maximize,
      next frame, average display, documentation, hide panels.

    Args:
        event: Key event object with `keysym` and optional `state`.
    """
    # If SHIFT_ACTIVATED == 0, force Shift to be ignored
    if params.SHIFT_ACTIVATED == 0:
        shift_pressed = False
    else:
        # Detect if Shift is pressed
        shift_pressed = getattr(event, "state", None)
        if shift_pressed is not None:
            # bitmask: check Shift key
            shift_pressed = (shift_pressed & 0x1) != 0
        else:
            # fallback to stored state
            shift_pressed = variables.SHIFT_PRESSED

    # Multiplier: x10 when Shift is pressed, otherwise x1
    multiplier = 10 if shift_pressed else 1

    # Value: positive for "Right" key, negative for others (e.g. "Left")
    val = multiplier if event.keysym == "Right" else -multiplier

    # Get currently selected parameter from the UI order
    param = params.PARAM_ORDER_IHM[params.SELECTED_INDEX]

    # If the window is maximized, prevent changes for WIDTH or HEIGHT
    if param in ("WIDTH", "HEIGHT") and is_maximized():
        val = 0

    # Navigate through parameters using arrow keys if arrows are activated
    if params.ARROWS_ACTIVATED > 0 and not variables.HIDDEN:
        if event.keysym == "Up":
            params.SELECTED_INDEX = (params.SELECTED_INDEX - 1) % len(
                params.PARAM_ORDER_IHM
            )
        elif event.keysym == "Down":
            params.SELECTED_INDEX = (params.SELECTED_INDEX + 1) % len(
                params.PARAM_ORDER_IHM
            )

    # Change value with Right and Left
    if (
        event.keysym == "Right" or event.keysym == "Left"
    ) and params.ARROWS_ACTIVATED >= 1 and not variables.HIDDEN:
        # Specific cases
        if param == "TRIANGLES":
            variables.POINTS_ID = []
            draw.canvas.delete("bird")
            params.TRIANGLES = not params.TRIANGLES
        elif param == "FONT_TYPE":
            current_index = const.FONT_TYPE_LIST.index(params.FONT_TYPE)
            params.FONT_TYPE = const.FONT_TYPE_LIST[
                (current_index + val) % len(const.FONT_TYPE_LIST)
            ]
        elif param == "COLOR":
            variables.POINTS_ID = []
            draw.canvas.delete("bird")
            params.COLOR = not params.COLOR
            if not params.COLOR:
                variables.CANVAS_BG = "black"
                variables.FILL_COLOR = "white"
                variables.OUTLINE_COLOR = "white"
                variables.INFO_COLOR = "yellow"
            else:
                variables.CANVAS_BG = "#87CEEB"
                variables.FILL_COLOR = "black"
                variables.OUTLINE_COLOR = "black"
                variables.INFO_COLOR = "orange"
        elif param == "FREE":
            params.FREE = not params.FREE
            # Readjust params one by one if needed (no free)
            if not params.FREE:
                for paramm in params.PARAM_ORDER_IHM:
                    if paramm not in ["FREE", "COLOR", "TRIANGLES", "FONT_TYPE"]:
                        setattr(params, paramm, change_value(paramm, 0, params.FREE))
        else:
            setattr(params, param, change_value(param, val, params.FREE))

        # regenerate birds and ihm
        move_birds(False, False)
        draw_root()
        draw_panels(True, on_other_key, start_repeat, stop_repeat)
        draw_birds()
        draw_box()
        draw_status_overlays()
    # Reset case
    elif (
        getattr(event, "keysym", "").lower() == str(params.RESET_COMMAND)
        and params.RESET_ACTIVATED >= 1
    ):
        restore_options()
        move_birds(False, False)
        draw_panels(False, on_other_key, start_repeat, stop_repeat)
        draw_birds()
        draw_box()
        draw_status_overlays()
        draw_root()
        draw_panels(True, on_other_key, start_repeat, stop_repeat)
        draw.root.state("normal")
        draw.root.focus_force()
        draw.root.focus_set()
    # Rebirds
    elif (
        getattr(event, "keysym", "").lower() == str(params.REGENERATION_COMMAND)
        and params.REGENERATION_ACTIVATED >= 1
    ):
        reynolds.velocities = []
        reynolds.birds = []
        move_birds(False, False)
        draw_birds()
    # Toggle FPS
    elif (
        getattr(event, "keysym", "").lower() == str(params.TOGGLE_FPS_COMMAND)
        and params.TOGGLE_FPS_ACTIVATED >= 1
    ):
        variables.FPS = not variables.FPS
        draw_status_overlays()
    # Toggle Start Pause
    elif (
        getattr(event, "keysym", "").lower() == str(params.TOGGLE_START_PAUSE_COMMAND)
        and params.TOGGLE_START_PAUSE_ACTIVATED >= 1
    ):
        toggle_pause()
    # Next Frame
    elif (
        getattr(event, "keysym", "").lower() == str(params.NEXT_FRAME_COMMAND)
        and params.NEXT_FRAME_ACTIVATED >= 1
    ):
        next_frame()
    # Toggle Minimimize Maximize
    elif (
        getattr(event, "keysym", "").lower() == str(params.TOGGLE_MAXIMIZE_COMMAND)
        and params.TOGGLE_MAXIMIZE_ACTIVATED >= 1
    ):
        maximize_minimize(False)
    # Toggle Average Positon
    elif (
        getattr(event, "keysym", "").lower() == str(params.AVERAGE_COMMAND)
        and params.AVERAGE_ACTIVATED >= 1
    ):
        variables.AVERAGE = not variables.AVERAGE
        draw_status_overlays()
    # Documentation display
    elif (
        getattr(event, "keysym", "").lower() == str(params.DOC_COMMAND)
        and params.DOC_ACTIVATED >= 1
    ):
        help = f"pybirdsreynolds {const.VERSION_PROG}\n\n" + get_help_text()
        popin = tk.Toplevel(draw.canvas)
        popin.title("Documentation - pybirdreynolds 🐦")
        popin.transient(draw.canvas.winfo_toplevel())
        popin.geometry("+200+200")
        popin.configure(bg=variables.CANVAS_BG)

        frame = tk.Frame(popin, bg=variables.CANVAS_BG)
        frame.pack(padx=10, pady=10)

        text_widget = tk.Text(
            frame,
            wrap="word",
            width=80,
            height=20,
            bg=variables.CANVAS_BG,
            fg=variables.FILL_COLOR,
            insertbackground=variables.CANVAS_BG,
            highlightthickness=0,
            bd=0,
        )
        text_widget.insert("1.0", help)
        text_widget.config(state="disabled")
        text_widget.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame, command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=scrollbar.set)
        popin.wait_visibility()
        popin.grab_set()
    # Toggle Hide Command
    elif (
        getattr(event, "keysym", "").lower() == str(params.HIDE_COMMAND)
        and params.HIDE_ACTIVATED >= 1
    ):
        if not variables.HIDDEN:
            variables.HIDDEN = True
            if is_maximized():
                maximize_minimize(True)
            variables.TRANS_HIDDEN = True
            variables.WIDTH_PARAMS = 0
            variables.WIDTH_CONTROLS = 0
            variables.HEIGHT_PARAMS_CONTROLS = 0
            params.HEIGHT_MIN=50
            params.HEIGHT_FREE_MIN=50
            params.WIDTH_MIN=50
            params.WIDTH_FREE_MIN=50
            draw_panels(True, on_other_key, start_repeat, stop_repeat)
            draw_root()
            draw_panels(False, on_other_key, start_repeat, stop_repeat)
            draw_box()
            draw_status_overlays()
            move_birds(False, True)
            draw_birds()
        else:
            variables.HIDDEN = False
            variables.WIDTH_PARAMS = const.WIDTH_PARAMS_DEFAULT
            variables.WIDTH_CONTROLS = const.WIDTH_CONTROLS_DEFAULT
            variables.HEIGHT_PARAMS_CONTROLS = const.HEIGHT_PARAMS_CONTROLS_DEFAULT
            if is_maximized():
                params.WIDTH = (
                    draw.root.winfo_width()
                    - variables.WIDTH_PARAMS
                    - variables.WIDTH_CONTROLS
                )
            params.HEIGHT_MIN=500
            params.HEIGHT_FREE_MIN=500
            params.WIDTH_MIN=500
            params.WIDTH_FREE_MIN=500    
            if params.HEIGHT<params.HEIGHT_MIN:
                params.HEIGHT=params.HEIGHT_MIN
            if params.WIDTH<params.WIDTH_MIN:
                params.WIDTH=params.WIDTH_MIN                
            draw_root()
            move_birds(False, True)
            draw_birds()
            draw_status_overlays()
            draw_panels(True, on_other_key, start_repeat, stop_repeat)
            draw_box()
            draw_root()
            draw_box()
    draw_panels(False, on_other_key, start_repeat, stop_repeat)


def restore_options():

    params.MAX_SPEED = copy.deepcopy(params.MAX_SPEED_INIT)
    params.NEIGHBOR_RADIUS = copy.deepcopy(params.NEIGHBOR_RADIUS_INIT)
    params.NUM_BIRDS = copy.deepcopy(params.NUM_BIRDS_INIT)
    params.WIDTH = copy.deepcopy(params.WIDTH_INIT)
    params.HEIGHT = copy.deepcopy(params.HEIGHT_INIT)
    params.REFRESH_MS = copy.deepcopy(params.REFRESH_MS_INIT)
    params.RANDOM_SPEED = copy.deepcopy(params.RANDOM_SPEED_INIT)
    params.RANDOM_ANGLE = copy.deepcopy(params.RANDOM_ANGLE_INIT)
    params.SEP_WEIGHT = copy.deepcopy(params.SEP_WEIGHT_INIT)
    params.ALIGN_WEIGHT = copy.deepcopy(params.ALIGN_WEIGHT_INIT)
    params.COH_WEIGHT = copy.deepcopy(params.COH_WEIGHT_INIT)
    params.SIZE = copy.deepcopy(params.SIZE_INIT)
    params.COLOR = copy.deepcopy(params.COLOR_INIT)
    params.FREE = copy.deepcopy(params.FREE_INIT)
    params.TRIANGLES = copy.deepcopy(params.TRIANGLES_INIT)
    params.FONT_TYPE = copy.deepcopy(params.FONT_TYPE_INIT)

    if not params.COLOR:
        variables.CANVAS_BG = "black"
        variables.FILL_COLOR = "white"
        variables.OUTLINE_COLOR = "white"
        variables.INFO_COLOR = "yellow"
    else:
        variables.CANVAS_BG = "#87CEEB"
        variables.FILL_COLOR = "black"
        variables.OUTLINE_COLOR = "black"
        variables.INFO_COLOR = "orange"
    variables.POINTS_ID = []
    draw.canvas.delete("bird")


def change_value(type, val, free):
    """
    Update a parameter value by adding `val` and clamp it within defined bounds.

    Bounds are taken from attributes in `params`:
      - Normal mode (`free=False`): <TYPE>_MIN / <TYPE>_MAX
      - Free mode   (`free=True`):  <TYPE>_FREE_MIN / <TYPE>_FREE_MAX

    Args:
        type (str): Parameter name (e.g., "speed").
        val (float): Increment to apply.
        free (bool): Whether to use free-mode bounds.

    Returns:
        float: The updated, bounded value.
    """
    value = getattr(params, type, None)
    prefix = type.upper()
    min_value = getattr(params, f"{prefix}_MIN", None)
    max_value = getattr(params, f"{prefix}_MAX", None)
    min_free_value = getattr(params, f"{prefix}_FREE_MIN", None)
    max_free_value = getattr(params, f"{prefix}_FREE_MAX", None)
    value += val
    if not free:
        if max_value is not None:
            value = min(value, max_value)
        if min_value is not None:
            value = max(value, min_value)
    else:
        if max_free_value is not None:
            value = min(value, max_free_value)
        if min_free_value is not None:
            value = max(value, min_free_value)
    return value
