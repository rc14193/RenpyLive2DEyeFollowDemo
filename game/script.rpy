init python:
    from renpy.display.core import absolute
    from line_displayable import LineDisplayable
    import math

    # The update func doesn't get passed the offsets so we want them explicitly
    # otherwise if we move the model and just use the model size our handle_position
    # would only be returning the eye location with the model at xpos and ypos 0
    # I tried _location, renpy.get_placement, etc. and all kept returning none
    # so explicitly setting location is the work around
    screen_x, screen_y = config.screen_width,config.screen_height
    xloc = screen_x/2 
    yloc = screen_y/2

    # flag to trigger changes in the live2d update func
    click_flag = False

    def handle_click():
        global click_flag
        if hiyori_obj is not None:
            motions = list(hiyori_obj.common.motions.keys())
            next_motion = motions[renpy.random.randint(0,len(motions)-1)]
            print(f"{next_motion=}")
            renpy.show(f"hiyori {next_motion}")
        click_flag = True

    # from renpy repo using the same logic for scaling and positioning live2d models
    # https://github.com/renpy/renpy/blob/master/renpy/gl2/live2d.py#L1110
    def get_scaled_size(live_obj):
        zoom = live_obj.zoom
        sw, sh = live_obj.common.model.get_size()
        if zoom is None:
            top = absolute.compute_raw(live_obj.top, sh)
            base = absolute.compute_raw(live_obj.base, sh)

            size = max(base - top, 1.0)

            zoom = 1.0 * live_obj.height * renpy.config.screen_height / size
        else:
            size = sh
            top = 0

        return top, base, sw*zoom, size*zoom

    def handle_position(live_obj):
        top, base, sw, sh = get_scaled_size(live_obj)
        return [(0, (-top*base)),(sw, sh*.2)]

    def hiyori_update_func(live_obj, show_time):
        # remember screen origin is 0,0 (top left corner)
        # x, y of the live2d for the live2d vector from screen origin
        pos = handle_position(live_obj)
        # x, y of the mouse vector from screen origin
        x, y = renpy.get_mouse_pos()
        # mouse_vector-live2d vector is the vector from the eyes to the mouse
        # most cartesian coords ↑ is +y, in images ↓ is +y so that's why *(-1)
        vec_x, vec_y = (x-xloc,-1*(y-pos[1][1]))
        magnitude = math.sqrt(vec_x**2+vec_y**2)
        # eye param is [-1,1] so normalize vector to use for value
        # and avoid divide by 0 error by just setting eyes zero
        if(magnitude > 0):
            norm_x, norm_y = vec_x/magnitude, vec_y/magnitude
        else:
            norm_x, norm_y = 0,0
        # over write the eye parameter with the vector component to look toward the mouse
        live_obj.blend_parameter("ParamEyeBallX", "Overwrite", norm_x)
        live_obj.blend_parameter("ParamEyeBallY", "Overwrite", norm_y)
        # update function returns delay in seconds until it should be run again
        # hardcode 1/30 or 30 FPS for the delay
        return 1/30

    # define model
    hiyori_obj = Live2D("Resources/hiyori_free", base=.9, update_function=hiyori_update_func, loop=True, default_fade=0.0)
    # most models will be bigger than the screen so we need to know how it lies on the screen
    t, b, hiyori_w, hiyori_h = get_scaled_size(hiyori_obj)
    # According to live2D Hiyori is (2976,4175) if we use our mouse and look at the location in the live2d editor
    # Her eyes are at about 800 or ~20% so that's why we multiply by .2, I adjusted it until it looked good
    # line to indicate the eyes for visualization
    line = LineDisplayable([[(xloc-10,hiyori_h*.2),(xloc+10,hiyori_h*.2)]], color="#f00", width=2)

image hiyori = hiyori_obj
# Again since renpy doesn't pass x, y pos of the model in the update func
# we want to set it explicitly so we can know exactly where the eyes are
screen displayLine:
    add line
    button:
        action Function(handle_click)
        xysize (config.screen_width, config.screen_height)

transform positioning:
    # xpos center of screen and then minus half zoom width so hiyori is centered
    # otherwise it would be the left edge of the model image that's centered
    xpos int(xloc)-int(hiyori_w/2) 

label start:
    show screen displayLine
    show hiyori still at positioning
    "" ""
