############## Import statements #############
import mujoco as mj
from mujoco.glfw import glfw
import numpy as np
from matplotlib import pyplot as plt
import os
import csv
# from ik_functions import *
import time

########################################################################
################# working with mujoco file ###############
xml_path = 'model.xml'    #xml file (assumes this is in the same folder as this file)
simend = 20               #simulation time
print_camera_config = 0  #set to 1 to print camera config
                          #this is useful for initializing view of the model)

# # For callback functions
# button_left = False
# button_middle = False
# button_right = False
# lastx = 0
# lasty = 0

def init_controller(model,data):
    #initialize the controller here. This function is called once, in the beginning
    pass

def controller(model, data):
    #put the controller here. This function is called inside the simulation.
    pass


# def keyboard(window, key, scancode, act, mods):
#     if act == glfw.PRESS and key == glfw.KEY_BACKSPACE:
#         mj.mj_resetData(model, data)
#         mj.mj_forward(model, data)

# def mouse_button(window, button, act, mods):
#     # update button state
#     global button_left
#     global button_middle
#     global button_right

#     button_left = (glfw.get_mouse_button(
#         window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS)
#     button_middle = (glfw.get_mouse_button(
#         window, glfw.MOUSE_BUTTON_MIDDLE) == glfw.PRESS)
#     button_right = (glfw.get_mouse_button(
#         window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS)

#     # update mouse position
#     glfw.get_cursor_pos(window)

# def mouse_move(window, xpos, ypos):
#     # compute mouse displacement, save
#     global lastx
#     global lasty
#     global button_left
#     global button_middle
#     global button_right

#     dx = xpos - lastx
#     dy = ypos - lasty
#     lastx = xpos
#     lasty = ypos

#     # no buttons down: nothing to do
#     if (not button_left) and (not button_middle) and (not button_right):
#         return

#     # get current window size
#     width, height = glfw.get_window_size(window)

#     # get shift key state
#     PRESS_LEFT_SHIFT = glfw.get_key(
#         window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS
#     PRESS_RIGHT_SHIFT = glfw.get_key(
#         window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS
#     mod_shift = (PRESS_LEFT_SHIFT or PRESS_RIGHT_SHIFT)

#     # determine action based on mouse button
#     if button_right:
#         if mod_shift:
#             action = mj.mjtMouse.mjMOUSE_MOVE_H
#         else:
#             action = mj.mjtMouse.mjMOUSE_MOVE_V
#     elif button_left:
#         if mod_shift:
#             action = mj.mjtMouse.mjMOUSE_ROTATE_H
#         else:
#             action = mj.mjtMouse.mjMOUSE_ROTATE_V
#     else:
#         action = mj.mjtMouse.mjMOUSE_ZOOM

#     mj.mjv_moveCamera(model, action, dx/height,
#                       dy/height, scene, cam)

# def scroll(window, xoffset, yoffset):
#     action = mj.mjtMouse.mjMOUSE_ZOOM
#     mj.mjv_moveCamera(model, action, 0.0, -0.05 *
#                       yoffset, scene, cam)


#get the full path
dirname = os.path.dirname(__file__)
abspath = os.path.join(dirname + "/" + xml_path)
xml_path = abspath

# MuJoCo data structures
model = mj.MjModel.from_xml_path(xml_path)  # MuJoCo model
data = mj.MjData(model)                # MuJoCo data
cam = mj.MjvCamera()                        # Abstract camera
opt = mj.MjvOption()                        # visualization options

# Init GLFW, create window, make OpenGL context current, request v-sync
glfw.init()
window = glfw.create_window(1080, 720, "Snake Simulation", None, None)
glfw.make_context_current(window)
glfw.swap_interval(1)

# initialize visualization data structures
mj.mjv_defaultCamera(cam)
mj.mjv_defaultOption(opt)
scene = mj.MjvScene(model, maxgeom=10000)
context = mj.MjrContext(model, mj.mjtFontScale.mjFONTSCALE_100.value)

# # install GLFW mouse and keyboard callbacks
# glfw.set_key_callback(window, keyboard)
# glfw.set_cursor_pos_callback(window, mouse_move)
# glfw.set_mouse_button_callback(window, mouse_button)
# glfw.set_scroll_callback(window, scroll)

# setting camera configuration
cam.azimuth = 97.52755905511809 ; cam.elevation = -41.13779527559077 ; cam.distance =  1.9578218344602798
cam.lookat =np.array([ 0.0 , 0.0 , 0.0 ])

#initialize the controller here. This function is called once, in the beginning
init_controller(model,data)

#set the controller
mj.set_mjcb_control(controller)

#initialize the model parameters 

myls = []
with open('input.csv', 'r') as file:
    reader = csv.reader(file)
    for i in reader:
        myls.append(i)

angles = np.array(myls[0], dtype=float)
goal = np.array(myls[1], dtype=float)

angles = angles.reshape(8,1)
goal = goal.reshape(3,1)

t = 0
dt = 0.01;
tolerance = 1e-4
flag = False    # flag to check if goal is reached or not 


for i in range(8):
    data.qpos[i] = angles[i][0]

mj.mj_forward(model,data)
pos_ee = data.site_xpos[0]
print(pos_ee)

filepath = os.path.join(dirname + "/" + "output.csv")
file = open(filepath, "a")
file.write("Timestamp  ,    j0    ,    j1    ,    j2    ,    j3    ,    j4     ,    j5    ,      j8    ,    j7    ")

while not glfw.window_should_close(window):
    
    t0 = t

    while ((t-t0) < 1.0/60.0):
        
        pos_ee = data.site_xpos[0]
        # print(pos_ee, '\n\n')
        j = np.zeros((3,8))
        mj.mj_jac(model, data, j, None, pos_ee, 8)
        jpinv = np.linalg.pinv(j)
        error = np.array([goal[0]-pos_ee[0], goal[1]-pos_ee[1], goal[2]-pos_ee[2]])
        dX = error.reshape(3,1)
        dq = jpinv @ dX
        # print(dq,'\n\n')
        
        for k in range(8):
            data.qpos[k] += 0.01 *dq[k][0]
        
        if (np.linalg.norm(error) < tolerance):
            print('Goal reached !!\nError in Position of end effector is :\n',error)
            flag = True
            break
        
        val = f"{t}, {data.qpos[0]},{data.qpos[1]},{data.qpos[2]},{data.qpos[3]},{data.qpos[4]},{data.qpos[5]},{data.qpos[6]},{data.qpos[7]}"

        file.write(val)
        
        mj.mj_forward(model, data)
        # print('t: ', t,data.qpos[:])
        t += dt

    if (flag == True):
        time.sleep(5)   # model will be displayed till 5 seconds after goal is reached
        file.close()    
        break
    # get framebuffer viewport
    viewport_width, viewport_height = glfw.get_framebuffer_size(window)
    viewport = mj.MjrRect(0, 0, viewport_width, viewport_height)

    # print camera configuration (help to initialize the view)
    if (print_camera_config==1):
        print('cam.azimuth =',cam.azimuth,';','cam.elevation =',cam.elevation,';','cam.distance = ',cam.distance)
        print('cam.lookat =np.array([',cam.lookat[0],',',cam.lookat[1],',',cam.lookat[2],'])')
        print('\n\n')

    # # Update scene and render
    mj.mjv_updateScene(model, data, opt, None, cam, mj.mjtCatBit.mjCAT_ALL.value, scene)
    mj.mjr_render(viewport, scene, context)

    ## swap OpenGL buffers (blocking call due to v-sync)
    glfw.swap_buffers(window)

    ## process pending GUI events, call GLFW callbacks
    glfw.poll_events()

glfw.terminate()
