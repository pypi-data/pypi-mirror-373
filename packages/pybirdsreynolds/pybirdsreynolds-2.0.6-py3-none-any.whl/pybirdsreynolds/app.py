import signal
import copy
import tkinter as tk
import pybirdsreynolds.const as const
import pybirdsreynolds.params as params
import pybirdsreynolds.variables as variables
import pybirdsreynolds.draw as draw
from tkinter import font
from functools import partial
from pybirdsreynolds.args import compute_args
from pybirdsreynolds.draw import (
    draw_status_overlays,
    update,
    on_resize,
    patch_1,
    patch_2,
)
from pybirdsreynolds.controls import (
    on_other_key,
    start_repeat,
    stop_repeat,
    toggle_pause,
    on_shift_press,
    on_shift_release,
    signal_handler,
    restore_options,
)


def app():

    # Set params values: use user-provided options if available,
    # otherwise fall back to *_DEFAULT values.
    options = compute_args()
    for var_name in dir(params):
        if var_name.endswith("_DEFAULT"):
            option_name = var_name[:-8]
            default_value = getattr(params, var_name)
            value = getattr(options, option_name.lower(), default_value)
            setattr(params, option_name, value)
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

    # Save initial default values to allow restoring params later if needed.
    params.MAX_SPEED_INIT = copy.deepcopy(params.MAX_SPEED)
    params.NEIGHBOR_RADIUS_INIT = copy.deepcopy(params.NEIGHBOR_RADIUS)
    params.NUM_BIRDS_INIT = copy.deepcopy(params.NUM_BIRDS)
    params.WIDTH_INIT = copy.deepcopy(params.WIDTH)
    params.HEIGHT_INIT = copy.deepcopy(params.HEIGHT)
    params.REFRESH_MS_INIT = copy.deepcopy(params.REFRESH_MS)
    params.RANDOM_SPEED_INIT = copy.deepcopy(params.RANDOM_SPEED)
    params.RANDOM_ANGLE_INIT = copy.deepcopy(params.RANDOM_ANGLE)
    params.SEP_WEIGHT_INIT = copy.deepcopy(params.SEP_WEIGHT)
    params.ALIGN_WEIGHT_INIT = copy.deepcopy(params.ALIGN_WEIGHT)
    params.COH_WEIGHT_INIT = copy.deepcopy(params.COH_WEIGHT)
    params.SIZE_INIT = copy.deepcopy(params.SIZE)
    params.FONT_SIZE_INIT = copy.deepcopy(params.FONT_SIZE)
    params.FONT_TYPE_INIT = copy.deepcopy(params.FONT_TYPE)
    params.TRIANGLES_INIT = copy.deepcopy(params.TRIANGLES)
    params.FREE_INIT = copy.deepcopy(params.FREE)
    params.COLOR_INIT = copy.deepcopy(params.COLOR)

    # Save and set the parameters displayed in the UI
    param_docs_ihm = {
        name.removesuffix("_DOC"): value
        for name, value in vars(params).items()
        if name.endswith("_DOC") and getattr(params, f"{name[:-4]}_ACTIVATED") == 2
    }
    params.PARAM_ORDER_IHM = list(param_docs_ihm.keys())

    # set tk app
    draw.root = tk.Tk()
    draw.root.title(f"pybirdsreynolds 🐦")
    draw.root.minsize(
        variables.WIDTH_PARAMS + params.WIDTH_MIN + variables.WIDTH_CONTROLS,
        max(params.HEIGHT, variables.HEIGHT_PARAMS_CONTROLS),
    )
    draw.canvas = tk.Canvas(
        draw.root,
        width=variables.WIDTH_PARAMS + params.WIDTH + variables.WIDTH_CONTROLS,
        height=params.HEIGHT,
        bg=variables.CANVAS_BG,
    )
    draw.canvas.pack(fill="both", expand=True, padx=0, pady=0)

    # Handle fonts (must be done after creating the Tk root window).
    const.FONT_TYPE_LIST = [f for f in const.FONT_TYPE_LIST if f in font.families()]
    if params.FONT_TYPE not in const.FONT_TYPE_LIST:
        params.FONT_TYPE = const.FONT_TYPE_LIST[0]
        params.FONT_TYPE_INIT = copy.deepcopy(params.FONT_TYPE)
    draw_status_overlays()
    update()

    # Handle bindings
    draw.root.bind("p", toggle_pause)
    draw.root.bind("<Key>", on_other_key)
    draw.root.bind_all("<Shift_L>", on_shift_press)
    draw.root.bind_all("<Shift_R>", on_shift_press)
    draw.root.bind_all("<KeyRelease-Shift_L>", on_shift_release)
    draw.root.bind_all("<KeyRelease-Shift_R>", on_shift_release)
    draw.canvas.bind(
        "<Configure>", partial(on_resize, on_other_key, start_repeat, stop_repeat)
    )
    signal.signal(signal.SIGINT, signal_handler)

    # lauch tk app
    draw.root.after(100, patch_1)
    draw.root.after(200, patch_2)
    restore_options()
    draw.root.update()
    draw.root.mainloop()
