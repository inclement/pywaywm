from __future__ import division, print_function
from pywlc import ffi, lib
from pywlc import wlc
# from pywm.callbacks import lib, ffi

def get_topmost(output, offset):
    views, num_views = wlc.output_get_views(output)
    if num_views > 0:
        return views[(num_views - 1 + offset) % num_views]
    return 0

def do_layout(output):
    size = wlc.output_get_virtual_resolution(output)
    print('size is', size)
    
    views, num_views = wlc.output_get_views(output)
    print('views, num views', views, num_views)

    positioned = 0
    for i in range(num_views):
        if wlc.view_positioner_get_anchor_rect(views[i]) == wlc.NULL:
            positioned += 1

    toggle = 0
    y = 0
    n = max((1 + positioned) // 2, 1)
    print('size is', size)
    w = size.w // 2
    h = size.h // n
    ew = size.w - w * 2
    eh = size.h - h * n
    j = 0

    for i in range(num_views):
        anchor_rect = wlc.view_positioner_get_anchor_rect(views[i])
        if anchor_rect == wlc.NULL:
            g = wlc.WlcGeometry()
            g.origin.x = w + ew if toggle else 0
            g.origin.y = y
            g.size.w = (
                size.w if ((1 - toggle) and j == positioned - 1)
                else (w if toggle else w + ew))
            g.size.h = h + eh if j < 2 else h

            print('i is {}, x is {}, y is {}, w is {}, h is {}'.format(i, g.origin.x, g.origin.y, g.size.w, g.size.h))
            wlc.view_set_geometry(views[i], 0, g)

            toggle = 1 - toggle
            y = y + (g.size.h if not toggle else 0)
            j += 1

        else:
            size_req = wlc.view_positioner_get_size(views[i])
            print('size req', size_req)
            if size_req.w <= 0 or size_req.h <= 0:
                current = wlc.view_get_geometry(views[i])
                size_req = current.size

            g = wlc.WlcGeometry()
            g.origin = anchor_rect.origin
            g.size = size_req

            parent = wlc.view_get_parent(views[i])

            if parent:
                parent.geometry = wlc.view_get_geometry(parent)
                g.origin.x += parent_geometry.origin.x
                g.origin.y += parent_geometry.origin.y

            wlc.view_set_geometry(views[i], 0, g)
    

def output_resolution(output, from_size, to_size):
    print('output resolution', output, from_size, to_size)
    do_layout(output)
    
def view_created(view):
    print('view_created', view)

    wlc.view_set_mask(view, wlc.output_get_mask(wlc.view_get_output(view)))
    wlc.view_bring_to_front(view)
    wlc.view_focus(view)

    do_layout(wlc.view_get_output(view))

    return 1

def view_destroyed(view):
    print('view_destroyed')

    wlc.view_focus(get_topmost(wlc.view_get_output(view), 0))
    do_layout(wlc.view_get_output(view))

def view_focus(view, focus):
    print('view_focus')
    wlc.view_set_state(view, lib.WLC_BIT_ACTIVATED, focus)

def view_request_move(view):
    print('view_request_move')

def view_request_resize(view):
    print('view_request_resize')

def keyboard_key(view, time, modifiers, key, state):
    print('keyboard_key', view, time, modifiers, key, state)

    sym = wlc.keyboard_get_keysym_for_key(key)

    if view:
        if 'ctrl' in modifiers:
            if sym == wlc.keysym('q'):
                if state:
                    wlc.view_close(view)

    if 'ctrl' in modifiers:
        if sym == wlc.keysym('Escape'):
            if state:
                wlc.terminate()
            return 1

        if sym == wlc.keysym('Return'):
            if state:
                wlc.exec('weston-terminal')
            return 1

    return 0

def pointer_button(view):
    print('pointer_button')

def pointer_motion(handle, time, position):
    # print('pointer_motion', handle, timee, position)

    wlc.pointer_set_position(position)

    return 0

def init_callbacks():
    wlc.set_output_resolution_cb(output_resolution)
    wlc.set_view_created_cb(view_created)
    wlc.set_view_destroyed_cb(view_destroyed)
    wlc.set_view_focus_cb(view_focus)
    wlc.set_view_request_move_cb(view_request_move)
    wlc.set_view_request_resize_cb(view_request_resize)
    wlc.set_keyboard_key_cb(keyboard_key)
    wlc.set_pointer_button_cb(pointer_button)
    wlc.set_pointer_motion_cb(pointer_motion)

def run():
    init_callbacks()

    lib.wlc_init()
    lib.wlc_run()


if __name__ == "__main__":
    run()

