# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENCE BLOCK #####


bl_info = {
    "name": "My Big Button",
    "author": "Hokuss",
    "version": (0, 3, 9),
    "blender": (2, 80, 0),
    "location": "PROPERTIES WINDOW > Render & 3D View > UI > Render Tab & 3D View header",
    "description": "Render Button & Camera Manager for Blender 2.80",
    "warning": "",
    "wiki_url": "https://blenderartists.org/t/big-render-button-for-blender-2-80/1159414",
    "category": "Render",
    }

import bpy
import os, platform, subprocess
import aud
from bl_ui.utils import PresetPanel
import time, datetime
from bpy.utils import register_class, unregister_class

from bpy.types import (
    Operator,
    Panel,Scene, PropertyGroup,Object,Menu, Panel, UIList
)
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       )

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#SETTINGS//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class MYBIGBUTTON_Settings(PropertyGroup):

### Render Button[ -------------------------------------------
    switchStillAnim_prop : bpy.props.BoolProperty(
        name="Animation",
        description="Activate Animation Rendering",
        default = False)
    ### ]Render Button


### Render button panel Quick Settings[ -----------------------------
    mbbOptions : bpy.props.BoolProperty(
        name="Render Quick Settings",
        #description="Toggle Quick Settings",
        default = False)

    ## Sound alarm[---
    playAfterRender: bpy.props.BoolProperty(
        name="Play sound",
        description="Play Sound when render is done",
        default = False)

    soundToPlay: bpy.props.StringProperty(
        name="Choose Audio File",
        description="Specify location of audio file to play after render",
        default="",
        subtype="FILE_PATH")

    loopSoundToPlay: bpy.props.BoolProperty(
        name="loop sound",
        description="Play loop Sound",
        default = False)

    repeatSoundToPlay: bpy.props.IntProperty(
        name='Repeat Sound',
        description='Repeat sound after render',
        min=0, max=100,step=1,default = 0)

    alarmInProgress: bpy.props.BoolProperty(
        name="Alarm In Progress",
        description="Alarm In Progress",
        default = False)

    abortAlarm: bpy.props.BoolProperty(
        name="Abort Alarm",
        description="Abort Alarm",
        default = False)
        ## ]Sound alarm

    ## Power off[---
    poweroffAfterRender: bpy.props.BoolProperty(
        name="Power Off",
        description="Power Off after render",
        default = False)

    timeoutPowerOff: bpy.props.IntProperty(
        name='Timeout Delay',
        description='Delay in secondes before Power Off',
        min=15, max=1200,step=1,default = 60)

    countDownAfterRender : bpy.props.IntProperty(
        name="Countdown after render",
        description="Countdown after render",
        default = 0)

    saveAtPowerOff: bpy.props.BoolProperty(
        name="Save Blender File",
        description="Save Blender file before Power Off",
        default = False)
        ## ]Power off

    ## Auto save render[---
    saveInBlendFolder: bpy.props.BoolProperty(
        name="Save in blend folder",
        description="Save Camera Output in blend folder",
        default = False)

    storeRenderInSlots: bpy.props.BoolProperty(
        name="Store in Slots",
        description="Store Cameras Output in Render Slots",
        default = False)
        ## ]Auto save render
    ### ]Render button panel Quick Settings


### Dimensions settings[ -------------------------------------
    switchRenderRotation_prop : bpy.props.BoolProperty(
        name="Rotation",
        description="Toggle Landscape / Portrait",
        default = False)

    Default_HRes_prop : bpy.props.IntProperty(
        name="DHres",
        description="Horizontal Default Dimension",
        default = 1920,max=65536,min=4,step=1
        )

    Default_VRes_prop : bpy.props.IntProperty(
        name="DVres",
        description="Vertical Default Dimension",
        default = 1080,max=65536,min=4,step=1
        )

    Default_HPixRes_prop : bpy.props.FloatProperty(
        name="DHPix",
        description="Horizontal Default Pixel Aspect",
        default = 1)

    Default_VPixRes_prop : bpy.props.FloatProperty(
        name="DVPix",
        description="Vertical Default Pixel Aspect",
        default = 1)
    ### ]Dimensions settings


### Camera Manager panel Quick Settings[ -----------------------------------------
    ## Cameras Manager quick settings UI[---
    cmOptions : bpy.props.BoolProperty(
        name="Camera Manager Quick Settings",
        #description="Toggle Quick Settings",
        default = False)

    cmBut_Render : bpy.props.BoolProperty(
        name="Toggle Render Camera",
        default = True)

    cmBut_AlignV : bpy.props.BoolProperty(
        name="Toggle Align Camera To View",
        default = True)

    cmBut_AlignO : bpy.props.BoolProperty(
        name="Toggle Aligne Camera To Object",
        default = True)

    cmBut_Trackto : bpy.props.BoolProperty(
        name="Toggle Track To",
        default = True)

    cmBut_Marker : bpy.props.BoolProperty(
        name="Toggle Marker",
        default = True)

    cmBut_AnimData : bpy.props.BoolProperty(
        name="Toggle AnimData",
        default = True)

    Manager_ShowSelect : bpy.props.BoolProperty(
        name="Hilighlight Selected Camera",
        default = True)

    Manager_ShowSelect_Color : bpy.props.BoolProperty(
        name="Selected Camera Hilighlight with red",
        description="Selected Camera Hilighlight with red",
        default = True)

    Manager_ShowSelect_Gray : bpy.props.BoolProperty(
        name="Not selected Camera Grayed out",
        description="Not selected Camera Grayed out",
        default = True)

    Manager_ShowSelect_Pointer : bpy.props.BoolProperty(
        name="Add a pointer before Selected Camera",
        description="Add a pointer before Selected Camera",
        default = False)
        ## ]Cameras Manager quick settings UI

    ## Default settings for new cameras[---
    NewCam_lensPersp : bpy.props.IntProperty(
        name='Focal Length',
        description='New camera Focal Length ',
        min=1, max=5000,step=1,default = 50)

    NewCam_lensOrtho : bpy.props.FloatProperty(
        name='Orthographic Scale',
        description='New camera Orthographic Scale',
        min=0.001, max=100000,step=0.1,default = 35.000, precision= 3)

    NewCam_ClipStart : bpy.props.FloatProperty(
        name='Clip Start',
        description='New camera Clip start',
        min=0.001, max=100000,step=0.1,default = 0.1, precision= 3)

    NewCam_ClipEnd : bpy.props.FloatProperty(
        name='Clip End',
        description='New camera clip end',
        min=0.001, max=100000,step=0.1,default = 1000, precision= 3)

    NewCam_ClipStartOrtho : bpy.props.FloatProperty(
        name='Ortho Clip Start',
        description='New camera Orthographic clip start',
        min=0.001, max=100000,step=0.1,default = 0.1, precision= 3)

    NewCam_ClipEndOrtho : bpy.props.FloatProperty(
        name='Ortho Clip End',
        description='New camera Orthographic clip end',
        min=0.001, max=100000,step=0.1,default = 1000, precision= 3)
        ## ]Default settings for new cameras
    ### ]Camera Manager panel Quick Settings


### Batch Render Property[ -----------------------------------------
    switchRenderSelection: bpy.props.BoolProperty(
        name="Cameras Listing ",
        description="Toglle to Cameras listing for Batch Rendering",
        default = False)
    ### ]Batch Render Property

### Frame Render Type[ -----------------------------------------
    frameRenderType: bpy.props.StringProperty(
        name="Frame render type",
        description="Specify frame render type",
        default="")
    ### ]Frame Render Type

### Current Format Render Type[ -----------------------------------------
    currentFormatRenderType: bpy.props.StringProperty(
        name="Current frame render type",
        description="Current frame render type",
        default="")
    ### ]Current Format Render Type

### Only For This Job[ -----------------------------------------
    onlyForThisJob: bpy.props.BoolProperty(
        name="Set Render Format For This Job",
        description="Revert To Current Format After This Job",
        default = False)
    ### ]Only For This Job





class MYBIGBUTTON_obj_Settings(PropertyGroup):
### Cameras Properties[ -------------------------------------------------
    Custom_Camtrack_prop : bpy.props.BoolProperty(
        name="Track",
        description="Camera Track To property",
        default = False)

    Custom_CamMarker_prop : bpy.props.BoolProperty(
        name="Marker",
        description="Camera Marker property",
        default = False)

    Custom_CamRes_prop : bpy.props.BoolProperty(
        name="Custom Resolution",
        description="Camera custom resolution property",
        default = False)

    Custom_CamRender_prop : bpy.props.BoolProperty(
        name="Add This Camera",
        description="Add in batch rendering list",
        default = False)
    ### ]Cameras Properties


## Cameras Custom resolution[------------------------------------------
    Custom_CamHRes_prop : bpy.props.IntProperty(
        name="Custom Horizontal Resolution",
        description="Custom Horizontal Resolution",
        default = 1920)

    Custom_CamVRes_prop : bpy.props.IntProperty(
        name="Custom Vertical Resolution",
        description="Custom Vertical Resolution",
        default = 1080)

    Custom_CamHPixRes_prop : bpy.props.FloatProperty(
        name="Custom Horizontal Pixel Aspect",
        description="Custom Horizontal Pixel Aspect",
        default = 1)

    Custom_CamVPixRes_prop : bpy.props.FloatProperty(
        name="Custom Vertical Pixel Aspect",
        description="Custom Vertical Pixel Aspect",
        default = 1)
    ## ]Cameras Custom resolution



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#Function /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


def visualAlarm(self, context):
    scene = context.scene
    rd    = scene.render
    rs    = scene.RBTab_Settings

    layout      = self.layout
    row         = layout.row(align=True)
    row.scale_y = 3
    row.alert   = True

    if rs.countDownAfterRender == 0 and rs.playAfterRender == True:
        row.prop(rs,"abortAlarm", text="RENDER IS DONE",icon='BLANK1',emboss=False)
    elif rs.countDownAfterRender == 0:
        row.prop(rs,"abortAlarm", text="RENDER IS DONE".format(rs.countDownAfterRender),icon='BLANK1',emboss=False)
    else:
        if rs.countDownAfterRender%2 == 0 :
            row.alert = False
        else : row.alert = True
        row.prop(rs,"abortAlarm", text="POWER OFF IN {0} SEC".format(rs.countDownAfterRender),icon='BLANK1',emboss=False)

    row       = layout.row(align=True)
    row.alert = False

    row.prop(rs,"abortAlarm", text="Click or ESC to Abort",icon='BLANK1',emboss=False)


def SetCameraDimension(self, context):
        scene  = context.scene
        render = scene.render

        chosen_camera       = context.active_object
        previousSceneCamera = scene.camera
        scene.camera        = chosen_camera

        cs = chosen_camera.RBTab_obj_Settings
        rs = scene.RBTab_Settings

        if cs.Custom_CamRes_prop == True:
            render.resolution_x   = cs.Custom_CamHRes_prop
            render.resolution_y   = cs.Custom_CamVRes_prop
            render.pixel_aspect_x = cs.Custom_CamHPixRes_prop
            render.pixel_aspect_y = cs.Custom_CamVPixRes_prop
        else :
            render.resolution_x   = rs.Default_HRes_prop
            render.resolution_y   = rs.Default_VRes_prop
            render.pixel_aspect_x = rs.Default_HPixRes_prop
            render.pixel_aspect_y = rs.Default_VPixRes_prop

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#OPERATOR /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# ADD CAMERA ##################################################################################
class SCENECAMERA_OT_Add(Operator):
    bl_idname      = "cameramanager.add_scene_camera"
    bl_label       = "add Camera"
    bl_description = "Add Camera"
    bl_options = {'UNDO'}

    def execute(self, context):

        scene = context.scene
        rd    = scene.render
        sp    = scene.RBTab_Settings

        #Store active collection before add Camera
        Active_Coll = bpy.context.view_layer.active_layer_collection

        # Make Master Collection active before add camera
        context.view_layer.active_layer_collection = context.view_layer.layer_collection

        bpy.ops.object.camera_add()

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                if context.area.spaces[0].region_3d.is_perspective:
                    bpy.context.object.data.type       = 'PERSP'
                    bpy.context.object.data.lens       = sp.NewCam_lensPersp
                    bpy.context.object.data.clip_start = sp.NewCam_ClipStart
                    bpy.context.object.data.clip_end   = sp.NewCam_ClipEnd
                else:
                    bpy.context.object.data.type        = 'ORTHO'
                    bpy.context.object.data.ortho_scale = sp.NewCam_lensOrtho
                    bpy.context.object.data.clip_start  = sp.NewCam_ClipStartOrtho
                    bpy.context.object.data.clip_end    = sp.NewCam_ClipEndOrtho
                break

        bpy.context.object.show_name      = True
        bpy.context.object.data.show_name = True

        #Restore collection active before adding camera
        bpy.context.view_layer.active_layer_collection = Active_Coll

    ###Align to view last camera added
        chosen_camera = context.active_object
        scene.camera  = chosen_camera

        bpy.context.space_data.camera = bpy.data.objects[chosen_camera.name]

        bpy.ops.object.select_all(action='DESELECT')
        chosen_camera.select_set(state = True)

        if rd.resolution_x != sp.Default_HRes_prop or rd.resolution_y != sp.Default_VRes_prop:
            chosen_camera.RBTab_obj_Settings.Custom_CamRes_prop     = True
            chosen_camera.RBTab_obj_Settings.Custom_CamHRes_prop    = rd.resolution_x
            chosen_camera.RBTab_obj_Settings.Custom_CamVRes_prop    = rd.resolution_y
            chosen_camera.RBTab_obj_Settings.Custom_CamHPixRes_prop = rd.pixel_aspect_x
            chosen_camera.RBTab_obj_Settings.Custom_CamVPixRes_prop = rd.pixel_aspect_y

        # trick to prevent error if align camera to view in camera view mode!
        bpy.ops.view3d.view_persportho()
        bpy.ops.view3d.view_persportho()

        bpy.ops.view3d.camera_to_view()
        bpy.ops.view3d.view_center_camera()

        return {'FINISHED'}


# ACTIV & PREVIEW CHOSEN CAMERA ##################################################################################
class SCENECAMERA_OT_ActivPreview(Operator):
    bl_idname      = "cameramanager.activpreview_scene_camera"
    bl_label       = "Preview Camera"
    bl_description = "Active & Preview Camera"
    #bl_options = {'UNDO'}

    DeselectCam : bpy.props.BoolProperty(default = False)

    def invoke(self, context, event):

        scene         = context.scene
        chosen_camera = context.active_object

        previousSceneCamera = scene.camera

        render        = scene.render
        cs            = chosen_camera.RBTab_obj_Settings
        rs            = scene.RBTab_Settings
        marker_list   = context.scene.timeline_markers

        selectedObj = bpy.context.selected_objects
        selectedCam = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)

        if event.shift or self.DeselectCam == True:
            if chosen_camera in selectedCam:
                chosen_camera.select_set(state = False)
                self.DeselectCam = False
            else:
                chosen_camera.select_set(state = True)
                scene.camera  = chosen_camera
                bpy.context.view_layer.objects.active = chosen_camera

        elif event!= 'shift' :
            scene.camera = chosen_camera
            for marker in marker_list:
                if marker.camera == scene.camera:
                    scene.frame_current = marker.frame

            bpy.context.view_layer.objects.active = chosen_camera

            #if len(selectedCam)<=1 and chosen_camera not in selectedCam:
            if chosen_camera not in selectedCam:
                bpy.ops.object.select_all(action='DESELECT')
                chosen_camera.select_set(state = True)

        #ACTIV & PREVIEW CHOSEN CAMERA

            bpy.context.space_data.camera = bpy.data.objects[chosen_camera.name]

            SetCameraDimension(self, context)

            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    if context.area.spaces[0].region_3d.view_perspective == 'CAMERA' and scene.camera == previousSceneCamera and scene.camera in selectedCam:
                        bpy.ops.view3d.view_camera()
                    else:
                        bpy.ops.view3d.view_camera()
                        context.area.spaces[0].region_3d.view_perspective = 'CAMERA'
                    break
        return {'FINISHED'}



# ALIGN CHOSEN CAMERA TO ACTIV VIEW ##################################################################################
class SCENECAMERA_OT_AlignView(Operator):
    bl_idname      = "cameramanager.alignview_scene_camera"
    bl_label       = "Align Camera View to Activ View"
    bl_options = {'UNDO'}
    bl_description = (" \u2022 In perpective View: Align to View \n"
                      " \u2022 In Camera View: Align to Cursor")

    def execute(self, context):
        scene         = context.scene
        chosen_camera = context.active_object
        scene.camera  = chosen_camera
        render        = scene.render
        cs            = chosen_camera.RBTab_obj_Settings
        rs            = scene.RBTab_Settings
        marker_list   = context.scene.timeline_markers

        for marker in marker_list:
            if marker.camera == scene.camera:
                scene.frame_current = marker.frame

        object_to_track = bpy.context.selected_objects
        bpy.context.view_layer.objects.active = chosen_camera

        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')

    #ALIGN CHOSEN CAMERA TO ACTIV VIEW

        # Align to 3d Cursor IF in camera view
        if area.spaces[0].region_3d.view_perspective == 'CAMERA':
            if len(chosen_camera.constraints) > 0:
                CamTarget = chosen_camera.constraints[0].target
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[CamTarget.name].select_set(state = True)
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
                bpy.ops.object.select_all(action='DESELECT')
                chosen_camera.select_set(state = True)

            else:
                Active_Coll = bpy.context.view_layer.active_layer_collection
                context.view_layer.active_layer_collection = context.view_layer.layer_collection

                bpy.ops.object.empty_add(type='PLAIN_AXES')

                bpy.context.view_layer.active_layer_collection = Active_Coll
                bpy.context.object.name = "target"
                object_to_track = bpy.context.selected_objects
                chosen_camera.select_set(state = True)
                scene.camera = chosen_camera

                bpy.context.view_layer.objects.active = bpy.data.objects[object_to_track[0].name]
                bpy.ops.object.track_set(type='TRACKTO')
                bpy.ops.object.track_clear(type='CLEAR_KEEP_TRANSFORM')
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects["target"].select_set(state = True)
                bpy.ops.object.delete(use_global=False, confirm=False)
                bpy.ops.object.select_all(action='DESELECT')
                chosen_camera.select_set(state = True)

        # Align to activ View IF NOT in Camera View
        else:
            bpy.ops.object.select_all(action='DESELECT')
            chosen_camera.select_set(state = True)
            bpy.ops.view3d.view_persportho()
            bpy.ops.view3d.view_persportho()
            bpy.ops.view3d.camera_to_view()

        chosen_camera.select_set(state = False)

        bpy.context.view_layer.objects.active = chosen_camera
        bpy.context.space_data.camera = bpy.data.objects[chosen_camera.name]

        SetCameraDimension(self, context)

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                context.area.spaces[0].region_3d.view_perspective = 'CAMERA'
                break
        return {'FINISHED'}


# ALIGN CHOSEN CAMERA TO SELECTED OBJECT ##################################################################################
class SCENECAMERA_OT_AlignObj(Operator):
    bl_idname      = "cameramanager.alignobj_scene_camera"
    bl_label       = "Align Camera View to Object(s)"
    bl_options = {'UNDO'}
    bl_description = (" \u2022 Object(s) Selected: Align to Object(s) \n"
                      " \u2022 No Object Selected: View All")

    def execute(self, context):
        scene         = context.scene
        chosen_camera = context.active_object
        render        = scene.render
        op            = chosen_camera.RBTab_obj_Settings
        sp            = scene.RBTab_Settings

        selectedAny   = bpy.context.selected_objects
        selectedObj   = sorted([o for o in selectedAny if o.type != 'CAMERA'],key=lambda o: o.name)
        selectedCams  = sorted([o for o in selectedAny if o.type == 'CAMERA'],key=lambda o: o.name)

        chosen_camera = context.active_object
        scene.camera  = chosen_camera

        if chosen_camera not in selectedCams:
            selectedCams = []
            selectedCams.append(chosen_camera)

        bpy.context.view_layer.objects.active = chosen_camera


    #ALIGN CHOSEN CAMERA TO SELECTED OBJECT

        # View All IF no object selected OR current camera selected
        if len(selectedObj) == 0:# or chosen_camera.name == selectedObj[0].name:
            for cam in selectedCams:
                chosen_camera = cam
                scene.camera  = chosen_camera

                bpy.ops.object.select_all(action='SELECT')
                bpy.ops.view3d.camera_to_view_selected()
                bpy.ops.object.select_all(action='DESELECT')

        # View Selected object(s)
        else:
            for cam in selectedCams:
                chosen_camera = cam
                scene.camera  = chosen_camera

                bpy.ops.view3d.camera_to_view_selected()

        bpy.ops.object.select_all(action='DESELECT')
        if len(selectedCams) > 1:
            for cam in selectedCams:
                cam.select_set(state = True)

        SetCameraDimension(self, context)

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                context.area.spaces[0].region_3d.view_perspective = 'CAMERA'
                break
        return {'FINISHED'}


## TRACK TO SELECTED OBJECT ##
### ADD TRACK ################################################################################
class SCENECAMERA_OT_AddTrackTo(Operator):
    bl_idname      = "cameramanager.trackto_scene_camera"
    bl_label       = "Track to Object"
    #bl_options = {'UNDO'}
    bl_description = (" \u2022 Object Selected: Track to Object Selected \n"
                      " \u2022 No Object Selected: Track to New Empty")

    event_Shift: bpy.props.BoolProperty(default = False)

    def invoke(self, context, event):
        if event.shift: self.event_Shift = True
        else: self.event_Shift = False

        return self.execute(context)

    def execute(self, context):
        scene  = context.scene
        render = scene.render

        selectedObj     = bpy.context.selected_objects
        object_to_track = sorted([o for o in selectedObj if o.type != 'CAMERA'],key=lambda o: o.name)
        selectedCams    = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)
        constraintsCams = sorted([o for o in selectedCams if len(o.constraints) > 0],key=lambda o: o.name)

        chosen_camera = context.active_object
        scene.camera  = chosen_camera

        op = chosen_camera.RBTab_obj_Settings
        sp = scene.RBTab_Settings

        if chosen_camera not in selectedCams:
            selectedCams = []
            selectedCams.append(chosen_camera)

        bpy.context.view_layer.objects.active = chosen_camera
        targets = sorted([o for o in scene.objects if o.type == 'EMPTY'], key=lambda o: o.name)


    #TRACK TO SELECTED OBJECT

        # IF object selected = none OR = current camera THEN add empty and track to
        if len(object_to_track) == 0: #or chosen_camera.name == object_to_track[0].name:
            for cam in selectedCams:
                if len(cam.constraints) == 0:
                    chosen_camera = cam
                    #print(chosen_camera)
                    Active_Coll = bpy.context.view_layer.active_layer_collection
                    context.view_layer.active_layer_collection = context.view_layer.layer_collection

                    bpy.ops.object.empty_add(type='PLAIN_AXES')

                    bpy.context.view_layer.active_layer_collection = Active_Coll
                    bpy.context.object.name = "t_{0}".format(chosen_camera.name)

                    bpy.context.object.show_name = True
                    bpy.context.object.show_in_front = True
                    object_to_track = bpy.context.selected_objects

                    chosen_camera.select_set(state = True)
                    #scene.camera = chosen_camera

                    bpy.context.view_layer.objects.active = bpy.data.objects[object_to_track[0].name]
                    bpy.ops.object.track_set(type='TRACKTO')
                else:
                    print('NO')


        #If object selected THEN track to
        else :
            chosen_camera.select_set(state = True)
            scene.camera = chosen_camera

            bpy.context.view_layer.objects.active = bpy.data.objects[object_to_track[0].name]
            bpy.ops.object.track_set(type='TRACKTO')

        chosen_camera.RBTab_obj_Settings.Custom_Camtrack_prop = True

        bpy.context.view_layer.objects.active = bpy.data.objects[scene.camera.name]

        bpy.ops.object.select_all(action='DESELECT')

        if len(selectedCams) > 1:
            for cam in selectedCams:
                cam.select_set(state = True)

        SetCameraDimension(self, context)

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                context.area.spaces[0].region_3d.view_perspective = 'CAMERA'
                break
        return {'FINISHED'}




### REMOVE TRACK TO ################################################################################
class SCENECAMERA_OT_RemoveTrackTo(Operator):
    bl_idname      = "cameramanager.removetrackto_scene_camera"
    bl_label       = "Remove Track to Object : Clear Track"
    #bl_options = {'UNDO'}
    bl_description = (" \u2022 Shift : Clear and Keep Transformation")

    event_Shift: bpy.props.BoolProperty(default = False)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        if event.shift: self.event_Shift = True
        else: self.event_Shift = False

        return self.execute(context)

    def execute(self, context):
        scene  = context.scene
        render = scene.render

        selectedObj     = bpy.context.selected_objects
        cameras         = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)
        object_to_track = sorted([o for o in selectedObj if o.type != 'CAMERA'],key=lambda o: o.name)
        selectedCams    = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)

        targetedCams = []
        targetsName  = []
        tc_Append    = targetedCams.append
        tn_Append    = targetsName.append
        for o in cameras:
            if o.constraints is not None:
                for c in o.constraints:
                    if c.type == 'TRACK_TO':
                        tc_Append(o)
                        if c.target is not None:
                            tn_Append(c.target.name)


        chosen_camera = context.active_object

        op = chosen_camera.RBTab_obj_Settings
        sp = scene.RBTab_Settings

        if chosen_camera not in selectedCams:
            selectedCams = []
            selectedCams.append(chosen_camera)

        object_to_track = bpy.context.selected_objects
        bpy.context.view_layer.objects.active = chosen_camera

        targets = sorted([o for o in scene.objects if o.type == 'EMPTY'], key=lambda o: o.name)

    #REMOVE TRACK TO SELECTED OBJECT

        for cam in selectedCams:
            chosen_camera = cam
            if chosen_camera in targetedCams :
                CamTarget = chosen_camera.constraints[0].target
                bpy.ops.object.select_all(action='DESELECT')
                chosen_camera.select_set(state = True)
                if CamTarget is not None: targetsName.remove(CamTarget.name)
                print(len(targetsName))
                print(targetsName)

                # Shift Click = Clear Keep
                if self.event_Shift:
                    bpy.ops.object.track_clear(type='CLEAR_KEEP_TRANSFORM')

                # Click = Clear
                else:
                    bpy.ops.object.track_clear(type='CLEAR')

                # Remove Target after Clear Track IF Target Type = Empty and
                # name starts with = t_
                if CamTarget is not None and targetsName.count(CamTarget.name) == 0:
                    _tname = CamTarget.name[0:2]

                    if CamTarget.type == 'EMPTY' and _tname == "t_":
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.data.objects[CamTarget.name].select_set(state = True)
                        bpy.ops.object.delete(use_global=False, confirm=False)

                chosen_camera.RBTab_obj_Settings.Custom_Camtrack_prop = False

        bpy.ops.object.select_all(action='DESELECT')

        if len(selectedCams) > 1:
            for cam in selectedCams:
                cam.select_set(state = True)

        SetCameraDimension(self, context)

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                context.area.spaces[0].region_3d.view_perspective = 'CAMERA'
                break
        return {'FINISHED'}


# ADD CAMERA MARKER ##################################################################################
class SCENECAMERA_OT_AddMarker(Operator):
    bl_idname      = "cameramanager.add_camera_marker"
    bl_label       = "Add Camera Marker"
    bl_description = "Add a timeline marker bound to this camera"
    #bl_options = {'UNDO'}

    def execute(self, context):
        chosen_camera = context.active_object
        scene         = context.scene
        current_frame = scene.frame_current
        marker        = None

        for m in reversed(sorted(filter(lambda m: m.frame <= current_frame,scene.timeline_markers),key=lambda m: m.frame)):
            marker = m
            break

        marker_name = chosen_camera.name

        if marker and (marker.frame == current_frame):
            marker.name = marker_name
        else:
            marker = scene.timeline_markers.new(marker_name)

        marker.frame  = scene.frame_current
        marker.camera = chosen_camera
        marker.select = True

        chosen_camera.RBTab_obj_Settings.Custom_CamMarker_prop = True

        for other_marker in [m for m in scene.timeline_markers if m != marker]:
            other_marker.select = False

        return {'FINISHED'}


# REMOVE CAMERA MARKER ##################################################################################
class SCENECAMERA_OT_removeMarker(Operator):
    bl_idname = "cameramanager.remove_camera_marker"
    bl_label = "Remove Camera Marker"
    bl_description = (" \u2022 Shift : Remove all Camera marker")
    #bl_options = {'UNDO'}

    event_Shift: bpy.props.BoolProperty(default = False)


    def invoke(self, context, event):
        if event.shift: self.event_Shift = True
        else: self.event_Shift = False
        return self.execute(context)

    def execute(self, context):

    #def invoke(self, context, event):
        scene  = context.scene
        render = scene.render

        selectedObj     = bpy.context.selected_objects
        object_to_track = sorted([o for o in selectedObj if o.type != 'CAMERA'],key=lambda o: o.name)
        selectedCams    = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)

        chosen_camera  = context.active_object
        scene.camera   = chosen_camera
        marker_list    = context.scene.timeline_markers

        op = chosen_camera.RBTab_obj_Settings
        sp = scene.RBTab_Settings


        if chosen_camera not in selectedCams:
            if len(selectedCams) == 0:
                selectedCams = []
                selectedCams.append(chosen_camera)
            elif len(selectedCams) > 0:
                chosen_camera = selectedCams[0]


        # Shift Click = Remove All Marker
        if self.event_Shift:
            for marker in marker_list:
                scene.camera        = marker.camera
                scene.frame_current = marker.frame
                scene.timeline_markers.remove(marker)
        else:

            for cam in selectedCams:
                chosen_camera = cam
                for marker in marker_list:
                    if marker.camera == chosen_camera:
                        scene.camera        = marker.camera
                        scene.frame_current = marker.frame
                        scene.timeline_markers.remove(marker)

        chosen_camera.RBTab_obj_Settings.Custom_CamMarker_prop = False

        bpy.ops.object.select_all(action='DESELECT')

        if len(selectedCams) > 1:
            for cam in selectedCams:
                cam.select_set(state = True)

        SetCameraDimension(self, context)

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                context.area.spaces[0].region_3d.view_perspective = 'CAMERA'
                break

        return {'FINISHED'}


# REMOVE CAMERA ##################################################################################
class SCENECAMERA_OT_Remove(Operator):
    bl_idname      = "cameramanager.del_scene_camera"
    bl_label       = "Remove Scene Camera"
    bl_description = (" \u2022 shift + click: Remove All Cameras ")
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        chosen_camera = context.active_object
        scene         = context.scene
        marker_list   = context.scene.timeline_markers

        scene.camera = chosen_camera

        selectedObj = bpy.context.selected_objects
        selectedCam = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)

        cameras = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)

        if event.shift or len(selectedCam) == len(cameras):
            for camera in cameras:
                if len(camera.constraints) >0:
                    CamTarget = camera.constraints[0].target
                    if CamTarget is not None:
                        _tname = CamTarget.name[0:2]
                        if CamTarget.type == 'EMPTY' and _tname == "t_":
                            bpy.ops.object.select_all(action='DESELECT')
                            bpy.data.objects[CamTarget.name].select_set(state = True)
                            bpy.ops.object.delete(use_global=False, confirm=False)

                scene.camera = camera
                bpy.ops.object.select_all(action='DESELECT')
                camera.select_set(state = True)
                bpy.ops.object.delete(use_global=False, confirm=False)

            if len(marker_list)>0:
                for marker in marker_list:
                    scene.timeline_markers.remove(marker)

            return {'FINISHED'}

        elif chosen_camera in selectedCam and len(selectedCam) >1:
            for camera in cameras:
                if camera in selectedCam:
                    if len(camera.constraints) >0:
                        CamTarget = camera.constraints[0].target
                        if CamTarget is not None:
                            _tname = CamTarget.name[0:2]
                            if CamTarget.type == 'EMPTY' and _tname == "t_":
                                bpy.ops.object.select_all(action='DESELECT')
                                bpy.data.objects[CamTarget.name].select_set(state = True)
                                bpy.ops.object.delete(use_global=False, confirm=False)

                    scene.camera = camera
                    bpy.ops.object.select_all(action='DESELECT')
                    camera.select_set(state = True)
                    bpy.ops.object.delete(use_global=False, confirm=False)
            return {'FINISHED'}
        else:
            if len(marker_list)>0:
                for marker in marker_list:
                    if marker.camera == scene.camera:
                        scene.camera        = marker.camera
                        scene.frame_current = marker.frame
                        scene.timeline_markers.remove(marker)

            if len(chosen_camera.constraints) >0:
                CamTarget = chosen_camera.constraints[0].target
                if CamTarget is not None:
                    _tname = CamTarget.name[0:2]
                    if CamTarget.type == 'EMPTY' and _tname == "t_":
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.data.objects[CamTarget.name].select_set(state = True)
                        bpy.ops.object.delete(use_global=False, confirm=False)

            scene.camera = chosen_camera
            bpy.ops.object.select_all(action='DESELECT')
            chosen_camera.select_set(state = True)
            bpy.ops.object.delete(use_global=False, confirm=False)
            return {'FINISHED'}


# RENDER ANIMATION ##################################################################################
class SCENECAMERA_OT_RenderAnimation(Operator):
    bl_idname      = "cameramanager.render_scene_animation"
    bl_label       = "Render Camera"
    bl_description = "Render this camera"

    _timer          = None
    _finish         = None
    _stop           = None
    _autoSaveRender = None
    path            = "//"
    _cameras        = None

    renderFrom  : bpy.props.StringProperty(default ='')

    def renderComplete(self, dummy, thrd = None):
        self._finish = True

    def renderCancel(self, dummy, thrd = None):
        self._stop = True

    def execute(self, context):

        scene = bpy.context.scene
        rs    = scene.RBTab_Settings

        self._cameras = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)

        ### Check Sound File For Alarm[---
        if rs.playAfterRender == True:
            a,soundType = os.path.splitext(rs.soundToPlay)
            soundExt    = bpy.path.extensions_audio

            if str.lower(soundType) not in soundExt or os.path.exists(bpy.path.abspath(rs.soundToPlay)) == False:
                rs.soundToPlay = ''
                ShowMessageBox("Choose a sound file for alarm before !", "Wrong Sound File Type OR Not Exist", 'ERROR')
                self.report({"WARNING"}, 'Wrong Sound File Type OR Not Exist')
                return {"CANCELLED"}
        ### ]Check Sound File For Alarm

    ## Autosave & Render file path[---
        if len(bpy.context.scene.render.filepath) == 0:
            if rs.saveInBlendFolder == False: self._autoSaveRender = False
            else:
                self._autoSaveRender = True
                self.path = '//'
        else:
            self._autoSaveRender = True
            if rs.saveInBlendFolder == False:
                self.path = bpy.context.scene.render.filepath
            else: self.path = '//'
        ### ]Autosave

    ## Application handlers[---
        bpy.app.handlers.render_complete.append(self.renderComplete)
        bpy.app.handlers.render_cancel.append(self.renderCancel)
        self._timer = context.window_manager.event_timer_add(0.5, window=context.window) #Timer event
        context.window_manager.modal_handler_add(self)
        ## ]Application handlers

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        scene = context.scene
        rs    = scene.RBTab_Settings

    ### EXIT after render is done or canceled[---
        if self._finish or self._stop:

            if self._autoSaveRender == True: scene.render.filepath = self.path
            else: scene.render.filepath = ''
            #Remove handlers
            bpy.app.handlers.render_complete.remove(self.renderComplete)
            bpy.app.handlers.render_cancel.remove(self.renderCancel)
            context.window_manager.event_timer_remove(self._timer)
            #Alarm
            if rs.playAfterRender == True or rs.poweroffAfterRender == True: bpy.ops.renderevents.end_events("INVOKE_DEFAULT")

            return {'FINISHED'}
        ### ]EXIT

        scene.render.filepath = self.path

        if len(self._cameras) == 0:
            ShowMessageBox("No camera found in this scene !", "Render Error", 'ERROR')
            self.report({"ERROR"}, 'No camera found in this scene !')
            return {"FINISHED"}
        else:
            bpy.ops.render.render('INVOKE_DEFAULT',animation=True)

        return {"PASS_THROUGH"}


# BATCH RENDER All CAMERA ##################################################################################
class SCENECAMERA_OT_BatchRenderAll(Operator):
    bl_idname      = "cameramanager.render_all_camera"
    bl_label       = "Batch Render All Camera"
    bl_description = "Render All Cameras"

    _timer              = None
    cameras             = []
    _lenCameras         = 0
    _cameras            = None
    marker_list         = None
    marker_list_cameras = None
    stop                = None
    rendering           = None
    path                = "//"
    _autoSaveRender     = None
    _currentRenderFileFormat = ''

    tmarkers : bpy.props.BoolProperty(default = False)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None or context.scene.camera is not None

    def pre(self, dummy, thrd = None):
        self.rendering = True

    def post(self, dummy, thrd = None):
        scene   = bpy.context.scene
        rs      = scene.RBTab_Settings
        img     = bpy.data.images['Render Result']

        if scene.frame_current == 0:
            marker_list = scene.timeline_markers
            marker_list_cameras = [o for o in self.marker_list if o.camera != None]
            for m in marker_list_cameras:
                if m.camera == scene.camera:
                    scene.timeline_markers.remove(m)

        if rs.storeRenderInSlots == True and img.render_slots.active_index < (self._lenCameras - 1):
            img.render_slots.active_index += 1

        self.cameras.pop(0)
        self.rendering = False

    def cancelled(self, dummy, thrd = None):
        scene  = bpy.context.scene
        if scene.frame_current == 0:
            marker_list = scene.timeline_markers
            for m in marker_list:
                if m.camera == scene.camera:
                    scene.timeline_markers.remove(m)

        self.stop = True

    def execute(self, context):
        self.stop      = False
        self.rendering = False
        self._lenCameras = 0
        self.cameras     = []

        scene  = bpy.context.scene
        render = scene.render
        rs     = scene.RBTab_Settings
        img    = bpy.data.images['Render Result']
        
        if rs.saveInBlendFolder: render.filepath = '//'

#        rs.frameRenderType = "BATCH"

        selectedObj = bpy.context.selected_objects
        selectedCam = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)

        self.marker_list         = context.scene.timeline_markers
        self.marker_list_cameras = [o for o in self.marker_list if o.camera != None]


        ### Check render File Format[---
        imageFormat   = ['TIFF','BMP','IRIS','JPEG2000','TARGA','TARGA_RAW','CINEON','DPX','OPEN_EXR','OPEN_EXR_MULTILAYER','HDR','JPEG','PNG']
        if render.image_settings.file_format not in imageFormat:
            self.report({"WARNING"}, 'Cannot write a single file with an animation format selected')
            bpy.ops.render.renderformat("INVOKE_DEFAULT")
            return {"CANCELLED"}
        #]Check render File Format

        ### Check Sound File For Alarm[---
        if rs.playAfterRender == True:
            a,soundType = os.path.splitext(rs.soundToPlay)
            soundExt    = bpy.path.extensions_audio

            if str.lower(soundType) not in soundExt or os.path.exists(bpy.path.abspath(rs.soundToPlay)) == False:
                rs.soundToPlay = ''
                ShowMessageBox("Choose a sound file for alarm before !", "Wrong Sound File Type OR Not Exist", 'ERROR')
                self.report({"WARNING"}, 'Wrong Sound File Type OR Not Exist')
                return {"CANCELLED"}
        #]Check Sound File For Alarm

        #test to ignore markers without binded cameras
        if len(self.marker_list_cameras) == 0: self.marker_list = []

    ## Build cameras list[---
        if rs.switchRenderSelection == True :
            if self.tmarkers == True:
                self.cameras = sorted([o.name for o in self.marker_list_cameras])
                self.tmarkers = False
            else:
                for o in scene.objects:
                    cs = o.RBTab_obj_Settings
                    if o.type == 'CAMERA'and cs.Custom_CamRender_prop == True:
                        self.cameras += sorted([o.name])
        elif len(selectedCam) > 1:
            self.cameras = sorted([o.name for o in selectedCam])
        else:
            if self.tmarkers == True:
                self.cameras = sorted([o.name for o in self.marker_list_cameras])
                self.tmarkers = False
            else:
                self.cameras = sorted([o.name for o in scene.objects if o.type == 'CAMERA'])
        #]Build cameras list

        self._lenCameras = len(self.cameras)

    ## Initialise render slots[---
        if rs.storeRenderInSlots == True:
            if len(img.render_slots) < len(self.cameras):
                _slotToAdd = len(self.cameras)-len(img.render_slots) #+1
                i = 0
                while i < _slotToAdd:
                    i+=1
                    img.render_slots.new()

        bpy.data.images['Render Result'].render_slots.active_index = 0
        #]Initialise render slots

    ## Autosave & Render file path[---
        if len(bpy.context.scene.render.filepath) == 0:
            if rs.saveInBlendFolder == False: self._autoSaveRender = False
            else:
                self._autoSaveRender = True
                self.path = '//'
        else:
            self._autoSaveRender = True
            if rs.saveInBlendFolder == False:
                self.path = bpy.context.scene.render.filepath
            else: self.path = '//'
        #]Autosave

    ## Application handlers[---
        bpy.app.handlers.render_pre.append(self.pre)
        bpy.app.handlers.render_post.append(self.post)
        bpy.app.handlers.render_cancel.append(self.cancelled)
        self._timer = context.window_manager.event_timer_add(0.5, window=context.window) #timer Event
        context.window_manager.modal_handler_add(self)
        #]Application handlers

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        sc = bpy.context.scene
        render = sc.render
        cs = sc.camera.RBTab_obj_Settings
        rs = sc.RBTab_Settings

        if event.type == 'TIMER':
            KamRender = False

            #Test to avoid render display mode SCREEN.
            #If is active during this batch render mode, you lose your workspace layout!
            #if bpy.context.scene.render.display_mode not in ('AREA', 'NONE', 'WINDOW'):
            if bpy.context.preferences.view.render_display_type not in ('AREA', 'NONE', 'WINDOW'):
                #Force AREA mode if chosen.
                bpy.context.preferences.view.render_display_type ='AREA'

        ## Exit Batch Render[---
            if True in (not self.cameras, self.stop is True):
                bpy.app.handlers.render_pre.remove(self.pre)
                bpy.app.handlers.render_post.remove(self.post)
                bpy.app.handlers.render_cancel.remove(self.cancelled)
                context.window_manager.event_timer_remove(self._timer)

                sc.frame_current = 1

                rs.frameRenderType = ""
                    
                if rs.onlyForThisJob:
                    render.image_settings.file_format = rs.currentFormatRenderType
                    rs.onlyForThisJob = False

                if self._autoSaveRender == True:  sc.render.filepath = self.path
                else: sc.render.filepath = ''

                if self.stop == True: return {"FINISHED"}
                elif rs.playAfterRender == True or rs.poweroffAfterRender == True: bpy.ops.renderevents.end_events("INVOKE_DEFAULT")

                return {"FINISHED"}
            #]Exit Batch Render

            elif self.rendering is False:

            ## Batch Render without timeline marker[---
                if len(self.marker_list) == 0:
                    sc.camera = bpy.data.objects[self.cameras[0]]

                    cs = sc.camera.RBTab_obj_Settings
                    rs = sc.RBTab_Settings

                    if cs.Custom_CamRes_prop == True:
                        render.resolution_x   = cs.Custom_CamHRes_prop
                        render.resolution_y   = cs.Custom_CamVRes_prop
                        render.pixel_aspect_x = cs.Custom_CamHPixRes_prop
                        render.pixel_aspect_y = cs.Custom_CamVPixRes_prop
                    else :
                        render.resolution_x   = rs.Default_HRes_prop
                        render.resolution_y   = rs.Default_VRes_prop
                        render.pixel_aspect_x = rs.Default_HPixRes_prop
                        render.pixel_aspect_y = rs.Default_VPixRes_prop

                    sc.render.filepath = self.path + self.cameras[0]

                    bpy.ops.render.render("INVOKE_DEFAULT", write_still=self._autoSaveRender)
#                    bpy.ops.render.render('INVOKE_DEFAULT',animation=True)
                #]Batch Render with no timeline marker

            ## Batch Render with timeline marker[---
                elif len(self.marker_list) >0:

                ## Render camera with timeline marker[---
                    for marker in self.marker_list_cameras:
                        if self.cameras[0] == marker.camera.name :
                            sc.camera = bpy.data.objects[self.cameras[0]]
                            sc.frame_current = marker.frame

                            cs = sc.camera.RBTab_obj_Settings
                            rs = sc.RBTab_Settings

                            if cs.Custom_CamRes_prop == True:
                                render.resolution_x   = cs.Custom_CamHRes_prop
                                render.resolution_y   = cs.Custom_CamVRes_prop
                                render.pixel_aspect_x = cs.Custom_CamHPixRes_prop
                                render.pixel_aspect_y = cs.Custom_CamVPixRes_prop
                            else :
                                render.resolution_x   = rs.Default_HRes_prop
                                render.resolution_y   = rs.Default_VRes_prop
                                render.pixel_aspect_x = rs.Default_HPixRes_prop
                                render.pixel_aspect_y = rs.Default_VPixRes_prop

                            sc.render.filepath = self.path + self.cameras[0]

                            bpy.ops.render.render("INVOKE_DEFAULT", write_still= self._autoSaveRender)
#                            bpy.ops.render.render('INVOKE_DEFAULT',animation=True)

                            KamRender = True
                            break
                    #]Render with timeline marker

                ## Render camera without timeline marker[---
                    if KamRender == False:

                        sc.camera = bpy.data.objects[self.cameras[0]]
                        chosen_camera = sc.camera

                        cs = sc.camera.RBTab_obj_Settings
                        rs = sc.RBTab_Settings

                        if cs.Custom_CamRes_prop == True:
                            render.resolution_x   = cs.Custom_CamHRes_prop
                            render.resolution_y   = cs.Custom_CamVRes_prop
                            render.pixel_aspect_x = cs.Custom_CamHPixRes_prop
                            render.pixel_aspect_y = cs.Custom_CamVPixRes_prop
                        else :
                            render.resolution_x   = rs.Default_HRes_prop
                            render.resolution_y   = rs.Default_VRes_prop
                            render.pixel_aspect_x = rs.Default_HPixRes_prop
                            render.pixel_aspect_y = rs.Default_VPixRes_prop

                        sc.render.filepath = self.path + self.cameras[0]

                        marker = None
                        bpy.context.scene.frame_current = 0
                        current_frame = sc.frame_current
                        for m in reversed(sorted(filter(lambda m: m.frame <= current_frame,sc.timeline_markers),key=lambda m: m.frame)):
                            marker = m
                            break
                        marker_name = chosen_camera.name
                        if marker and (marker.frame == current_frame):
                            marker.name = marker_name
                        else:
                            marker = sc.timeline_markers.new(marker_name)
                        marker.frame = sc.frame_current
                        marker.camera = chosen_camera
                        marker.select = True
                        for other_marker in [m for m in sc.timeline_markers if m != marker]:
                            other_marker.select = False

                        bpy.ops.render.render("INVOKE_DEFAULT", write_still=self._autoSaveRender)
#                        bpy.ops.render.render('INVOKE_DEFAULT',animation=True)
                    #]Render camera without timeline marker

                #]Batch Render with timeline marker

        return {"PASS_THROUGH"}


# RENDER CHOSEN CAMERA ##################################################################################
class SCENECAMERA_OT_Render(Operator):
    bl_idname      = "cameramanager.render_scene_camera"
    bl_label       = "Render Camera"
    bl_description = "Render this camera"

    KamCurrent      = None
    _timer          = None
    finish         = None
    _stop           = None
    _chosenCamera   = None
    path            = "//"
    _autoSaveRender = None
    _rendering      = None
    _currentRenderFileFormat = ''

    renderFrom : bpy.props.StringProperty(default ='')

    def renderComplete(self, dummy, thrd = None):
        scene  = bpy.context.scene
        rs     = scene.RBTab_Settings
        render = scene.render
        self.finish = True

        if scene.frame_current == 0:
            marker_list = scene.timeline_markers
            for m in marker_list:
                if m.camera == scene.camera:
                    scene.timeline_markers.remove(m)

    def renderCancel(self, dummy, thrd = None):
        scene  = bpy.context.scene
        render = scene.render
        self._stop = True
        if scene.frame_current == 0:
            marker_list = scene.timeline_markers
            for m in marker_list:
                if m.camera == scene.camera:
                    scene.timeline_markers.remove(m)

    def execute(self, context):
        scene = context.scene
        rs    = scene.RBTab_Settings
        chosen_camera = context.active_object
        render        = scene.render
        KamCurrent    = None
        self._chosenCamera = context.active_object
        
        if rs.saveInBlendFolder: render.filepath = '//'
        
        ### Check render File Format[---
        imageFormat   = ['TIFF','BMP','IRIS','JPEG2000','TARGA','TARGA_RAW','CINEON','DPX','OPEN_EXR','OPEN_EXR_MULTILAYER','HDR','JPEG','PNG']
        if render.image_settings.file_format not in imageFormat and render.filepath != '':
            self.report({"WARNING"}, 'Cannot write a single file with an animation format selected')
            bpy.ops.render.renderformat("INVOKE_DEFAULT")
            return {"CANCELLED"}
        #]Check render File Format

        ### Check Sound File For Alarm[---
        if rs.playAfterRender == True:
            a,soundType = os.path.splitext(rs.soundToPlay)
            soundExt    = bpy.path.extensions_audio

            if str.lower(soundType) not in soundExt or os.path.exists(bpy.path.abspath(rs.soundToPlay)) == False:
                rs.soundToPlay = ''
                ShowMessageBox("Choose a sound file for alarm before !", "Wrong Sound File Type OR Not Exist", 'ERROR')
                self.report({"WARNING"}, 'Wrong Sound File Type OR Not Exist')
                return {"CANCELLED"}
        #]Check Sound File For Alarm

        ### Autosave & Render file path[---
        if len(bpy.context.scene.render.filepath) == 0:
            if rs.saveInBlendFolder == False: self._autoSaveRender = False
            else:
                self._autoSaveRender = True
                self.path = '//'
        else:
            self._autoSaveRender = True
            if rs.saveInBlendFolder == False:
                self.path = bpy.context.scene.render.filepath
            else: self.path = '//'
        #]Autosave

        bpy.app.handlers.render_complete.append(self.renderComplete)
        bpy.app.handlers.render_cancel.append(self.renderCancel)
        self._timer = context.window_manager.event_timer_add(0.5, window=context.window)
        context.window_manager.modal_handler_add(self)

        self._rendering = True

        return {"RUNNING_MODAL"}


    def modal(self, context, event):
        scene  = context.scene
        render = scene.render
        rs     = scene.RBTab_Settings

    ### EXIT after render is done or canceled[---
        if self.finish or self._stop:
            self._rendering = False

            bpy.app.handlers.render_complete.remove(self.renderComplete)
            bpy.app.handlers.render_cancel.remove(self.renderCancel)
            context.window_manager.event_timer_remove(self._timer)

            rs.frameRenderType = ""
            
            if rs.onlyForThisJob:
                render.image_settings.file_format = rs.currentFormatRenderType
                rs.onlyForThisJob = False

            if self._autoSaveRender == True:  scene.render.filepath = self.path
            else: scene.render.filepath = ''

            if self._stop == True: return {"FINISHED"}
            elif rs.playAfterRender == True or rs.poweroffAfterRender == True: bpy.ops.renderevents.end_events("INVOKE_DEFAULT")

            return {"FINISHED"}
        #]EXIT

        if self._rendering == True:
            self._rendering = False

            render        = scene.render
            KamCurrent    = None

            bpy.context.view_layer.objects.active = self._chosenCamera

            marker_list = context.scene.timeline_markers
            cameras     = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)


        ### Checklist for avoid some errors[---
            if context.active_object is None:
                if len(cameras) == 0:
                    ShowMessageBox("No camera found in this scene !", "Render Error", 'ERROR')
                    self.report({"ERROR"}, 'No camera found in this scene !')
                    return {"FINISHED"}
                elif len(cameras) > 0 and scene.camera is None:
                    bpy.ops.object.select_all(action='DESELECT')
                    self._chosenCamera = cameras[0]
                    self._chosenCamera.select_set(state = True)
                    scene.camera  = self._chosenCamera
                elif len(cameras) == 1 :
                    bpy.ops.object.select_all(action='DESELECT')
                    self._chosenCamera = cameras[0]
                    self._chosenCamera.select_set(state = True)
                    scene.camera  = self._chosenCamera
                elif len(cameras) > 1:
                    bpy.ops.object.select_all(action='DESELECT')
                    self._chosenCamera = scene.camera
                    self._chosenCamera.select_set(state = True)
                    bpy.context.view_layer.objects.active = self._chosenCamera
            else:
                if len(cameras) == 0:
                    ShowMessageBox("No Camera in this scene !", "Render", 'ERROR')
                    return {"FINISHED"}
                elif len(cameras) > 0 and scene.camera is None:
                    bpy.ops.object.select_all(action='DESELECT')
                    self._chosenCamera = cameras[0]
                    self._chosenCamera.select_set(state = True)
                    scene.camera  = self._chosenCamera
                elif len(cameras) == 1 :
                    if context.active_object.type != 'CAMERA':
                        #print("no camera active")
                        bpy.ops.object.select_all(action='DESELECT')
                        self._chosenCamera = cameras[0]
                        self._chosenCamera.select_set(state = True)
                        scene.camera  = self._chosenCamera
                elif len(cameras) > 1:
                    if context.active_object.type != 'CAMERA' :
                        bpy.ops.object.select_all(action='DESELECT')
                        self._chosenCamera = scene.camera
                        self._chosenCamera.select_set(state = True)
                        bpy.context.view_layer.objects.active = self._chosenCamera
            #]Checklist


            #if bpy.context.scene.render.display_mode not in ('AREA', 'NONE', 'WINDOW'):  self.renderFrom = 'PROPERTIES'
            if bpy.context.preferences.view.render_display_type not in ('AREA', 'NONE', 'WINDOW'):  self.renderFrom = 'PROPERTIES'

            if self.renderFrom == 'TAB':
                scene.camera  = bpy.context.space_data.camera
                self._chosenCamera = bpy.context.space_data.camera
            elif self.renderFrom in ('PROPERTIES','CAMANAGER'): scene.camera  = self._chosenCamera

            x  = render.resolution_x
            y  = render.resolution_y

            cs = self._chosenCamera.RBTab_obj_Settings
            rs = scene.RBTab_Settings

            if cs.Custom_CamRes_prop == True:
                render.resolution_x   = cs.Custom_CamHRes_prop
                render.resolution_y   = cs.Custom_CamVRes_prop
                render.pixel_aspect_x = cs.Custom_CamHPixRes_prop
                render.pixel_aspect_y = cs.Custom_CamVPixRes_prop
            else :
                render.resolution_x   = rs.Default_HRes_prop
                render.resolution_y   = rs.Default_VRes_prop
                render.pixel_aspect_x = rs.Default_HPixRes_prop
                render.pixel_aspect_y = rs.Default_VPixRes_prop

            if len(marker_list) > 0:
                bpy.ops.object.select_all(action='DESELECT')
                self._chosenCamera.select_set(state = True)
                bpy.context.view_layer.objects.active = scene.camera

                if self.renderFrom == 'TAB':

                    bpy.context.space_data.camera = bpy.data.objects[scene.camera.name]
                    for area in bpy.context.screen.areas:
                        if area.type == 'VIEW_3D':
                            context.area.spaces[0].region_3d.view_perspective = 'CAMERA'
                            break

                for marker in marker_list:
                    if self._chosenCamera == marker.camera:
                        scene.camera  = marker.camera
                        scene.frame_current = marker.frame

                        scene.render.filepath = self.path + scene.camera.name
                        bpy.ops.render.render("INVOKE_DEFAULT", write_still=self._autoSaveRender)

                        return {"PASS_THROUGH"}

                marker = None

                scene.frame_current = 0

                current_frame = scene.frame_current

                for m in reversed(sorted(filter(lambda m: m.frame <= current_frame,scene.timeline_markers),key=lambda m: m.frame)):
                    marker = m
                    break

                marker_name = scene.camera.name

                if marker and (marker.frame == current_frame):
                    marker.name = marker_name
                else:
                    marker = scene.timeline_markers.new(marker_name)

                marker.frame  = scene.frame_current
                marker.camera = scene.camera
                marker.select = True

                for other_marker in [m for m in scene.timeline_markers if m != marker]:
                    other_marker.select = False

                scene.render.filepath = self.path + scene.camera.name
                bpy.ops.render.render("INVOKE_DEFAULT", write_still=self._autoSaveRender)

            elif len(marker_list) == 0 :
                bpy.ops.object.select_all(action='DESELECT')
                self._chosenCamera.select_set(state = True)
                bpy.context.view_layer.objects.active = scene.camera

                if self.renderFrom in ('TAB', 'CAMANAGER'):
                    bpy.context.space_data.camera = bpy.data.objects[scene.camera.name]
                    for area in bpy.context.screen.areas:
                        if area.type == 'VIEW_3D':
                            context.area.spaces[0].region_3d.view_perspective = 'CAMERA'
                            break

                scene.render.filepath = self.path + scene.camera.name
                bpy.ops.render.render("INVOKE_DEFAULT", write_still=self._autoSaveRender)

        return {"PASS_THROUGH"}


# TOGGLE RENDER ORIENTATION ##################################################################################
class MYBIGBUTTONTAB_OT_toggle_orientation(Operator):
    bl_idname      = "render.toggle_orientation"
    bl_label       = "Toggle Orientation"
    bl_description = (" \u2022 shift + click: Square dimensions \n"
                     "    (H Dimension as reference)")
    #bl_options = {'UNDO'}}

    def invoke(self, context, event):
        scene  = context.scene
        rs     = scene.RBTab_Settings
        render = scene.render

        if event.shift:
            render.resolution_y   = render.resolution_x
            render.pixel_aspect_y = render.pixel_aspect_x
            return {'FINISHED'}

        if rs.switchRenderRotation_prop == False:
            x    = render.resolution_x
            y    = render.resolution_y
            pa_x = render.pixel_aspect_x
            pa_y = render.pixel_aspect_y

            render.resolution_x   = y
            render.resolution_y   = x
            render.pixel_aspect_x = pa_y
            render.pixel_aspect_y = pa_x

            rs.switchRenderRotation_prop = True

        elif rs.switchRenderRotation_prop == True:
            x    = render.resolution_y
            y    = render.resolution_x
            pa_x = render.pixel_aspect_y
            pa_y = render.pixel_aspect_x

            render.resolution_x   = x
            render.resolution_y   = y
            render.pixel_aspect_x = pa_x
            render.pixel_aspect_y = pa_y

            rs.switchRenderRotation_prop = False

        return {'FINISHED'}


# STORE DEFAULT DIMENSION ##################################################################################
class MYBIGBUTTONTAB_OT_store_defaultres(Operator):
    bl_idname      = "render.store_as_defaultres"
    bl_label       = "Set Current Resolution as Default"
    #bl_options = {'UNDO'}
    bl_description = (" \u2022 Shift + Click: Recover Last")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        scene = context.scene
        rs    = scene.RBTab_Settings
        rd    = scene.render

        if event.shift:
            rd.resolution_x   = rs.Default_HRes_prop
            rd.resolution_y   = rs.Default_VRes_prop
            rd.pixel_aspect_x = rs.Default_HPixRes_prop
            rd.pixel_aspect_y = rs.Default_VPixRes_prop

        else:
            rs.Default_HRes_prop    = rd.resolution_x
            rs.Default_VRes_prop    = rd.resolution_y
            rs.Default_HPixRes_prop = rd.pixel_aspect_x
            rs.Default_VPixRes_prop = rd.pixel_aspect_y

        return {'FINISHED'}


# CUSTOM CAMERA RESOLUTION ##################################################################################
class SCENECAMERA_OT_CustomResolution(Operator):
    bl_idname = "cameramanager.custom_resolution"
    bl_label = "Custom Resolution"
    bl_description = "Set current resolution as custom camera resolution"
    #bl_options = {'UNDO'}

    crrefresh : bpy.props.BoolProperty(default = False)
    crdel     : bpy.props.BoolProperty(default = False)

    def invoke(self, context, event):
        scene  = context.scene
        render = scene.render
        ob     = context.active_object
        rs     = scene.RBTab_Settings
        cs     = ob.RBTab_obj_Settings

        x      = render.resolution_x
        y      = render.resolution_y
        pa_x   = render.pixel_aspect_x
        pa_y   = render.pixel_aspect_y


        cameras      = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)
        selectedObj  = bpy.context.selected_objects
        selectedCam  = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)
        noCustomDimCam = sorted([o for o in cameras if o.RBTab_obj_Settings.Custom_CamRes_prop == False],key=lambda o: o.name)

        selectedCustomDimCam = list(set(selectedCam) - set(noCustomDimCam))
        _cameras = []

        if self.crdel == True:

            if event.alt: _cameras = selectedCustomDimCam
            else : _cameras.append(context.active_object)

            for camera in _cameras :
                cs = camera.RBTab_obj_Settings

                cs.Custom_CamRes_prop     = False

                cs.Custom_CamHRes_prop    = rs.Default_HRes_prop
                cs.Custom_CamVRes_prop    = rs.Default_VRes_prop
                cs.Custom_CamHPixRes_prop = rs.Default_HPixRes_prop
                cs.Custom_CamVPixRes_prop = rs.Default_VPixRes_prop

                render.resolution_x       = rs.Default_HRes_prop
                render.resolution_y       = rs.Default_VRes_prop
                render.pixel_aspect_x     = rs.Default_HPixRes_prop
                render.pixel_aspect_y     = rs.Default_VPixRes_prop

            self.crdel = False
            return {'FINISHED'}

        if cs.Custom_CamRes_prop == False:
            if event.alt: _cameras = selectedCam
            else : _cameras.append(context.active_object)
            for camera in _cameras :
                cs = camera.RBTab_obj_Settings

                cs.Custom_CamHRes_prop    = x
                cs.Custom_CamVRes_prop    = y
                cs.Custom_CamHPixRes_prop = pa_x
                cs.Custom_CamVPixRes_prop = pa_y
                cs.Custom_CamRes_prop     = True

            return {'FINISHED'}

        elif cs.Custom_CamRes_prop == True:
            if self.crrefresh == False:
               return {'FINISHED'}

            elif self.crrefresh == True:
                cs.Custom_CamHRes_prop    = x
                cs.Custom_CamVRes_prop    = y
                cs.Custom_CamHPixRes_prop = pa_x
                cs.Custom_CamVPixRes_prop = pa_y
                self.crrefresh            = False
                return {'FINISHED'}


#EVENTS AFTER RENDER##################################################################################
class RENDEREVENTS_OT_endEvents(Operator):
    bl_description = 'Play sound and/or Power Off'
    bl_idname      = 'renderevents.end_events'
    bl_label       = 'Events After Render'

    _stop    = False
    _play    = False
    _timer   = None
    _timeout = None
    handle   = None

    if platform.system().startswith('Win'): OS  ='WINDOWS'
    elif platform.system().startswith('Lin'):OS ='LINUX'
    else : OS ='MacOS'

    testSoundToPlay: bpy.props.BoolProperty(default = False)

#    @classmethod
#    def poll(cls, context):
#        return context.scene.RBTab_Settings.soundToPlay != ''

    def modal(self, context, event):
        scene  = context.scene
        rs     = scene.RBTab_Settings

        if event.type == 'ESC' or rs.abortAlarm == True:
            context.window_manager.event_timer_remove(self._timer)
            if rs.playAfterRender == True: self.handle.stop()
            rs.alarmInProgress = False
            rs.abortAlarm = False
            rs.countDownAfterRender = 0
            self.testSoundToPlay = False
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)
            #print("________________Abort")
            return {'FINISHED'}

        elif event.type =='TIMER':
            if self._play == True:
                if self._stop == False and self.handle.status == False:
                    context.window_manager.event_timer_remove(self._timer)
                    rs.alarmInProgress = False
                    rs.abortAlarm = False
                    self.testSoundToPlay = False
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)
                    #print("________________Abort")
                    return {'FINISHED'}
                elif self._stop == True and self.testSoundToPlay == False:
                    if self.handle.status == False:
                        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                        self._timeout -= 1
                        rs.countDownAfterRender = self._timeout
                        print(self._timeout)
                        if self._timeout == 0:
                            rs.countDownAfterRender = 0
                            rs.abortAlarm = False
                            if self.OS == 'WINDOWS':
                                print(self.OS)
                                subprocess.call('shutdown /s /f')
                            elif self.OS == 'LINUX':
                                print(self.OS)
#                                bpy.ops.wm.quit_blender()
                                os.system('shutdown -h now')
                            elif self.OS == 'MacOS':
                                print(self.OS)
                                subprocess.call(['osascript', '-e','tell app "System Events" to shut down'])

                            rs.alarmInProgress = False
                            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)
                            #rs.countDownAfterRender = 0
                            #print("________________STOP")
                            self.handle.stop()
                            context.window_manager.event_timer_remove(self._timer)
                            return {'FINISHED'}
            elif self._play == False and self.testSoundToPlay == False:
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                rs.countDownAfterRender = self._timeout
                self._timeout -= 1
                print(self._timeout)
                if self._timeout == 0:
                    rs.alarmInProgress = False
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)
                    rs.countDownAfterRender = 0
                    if self.OS == 'WINDOWS':
                        print(self.OS)
                        subprocess.call('shutdown /s /f')
                    elif self.OS == 'LINUX':
                        print(self.OS)
                        bpy.ops.wm.quit_blender()
                        #os.system('shutdown -h now')
                    elif self.OS == 'MacOS':
                        print(self.OS)
                        subprocess.call(['osascript', '-e','tell app "System Events" to shut down'])

                    #print("________________STOP")
                    context.window_manager.event_timer_remove(self._timer)
                    return {'FINISHED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        scene  = context.scene
        rs     = scene.RBTab_Settings
        self._timeout = rs.timeoutPowerOff

        if rs.soundToPlay !='':
            a,soundType = os.path.splitext(rs.soundToPlay)
            soundExt    = bpy.path.extensions_audio

        ### Save a Copy of current file with "_powerOff" suffix before shutdown IF is dirty[---
        if rs.poweroffAfterRender and bpy.data.is_dirty and self.testSoundToPlay == False:
            _name,_ext = os.path.splitext(bpy.path.basename(bpy.context.blend_data.filepath))
            _path      = os.path.dirname(bpy.data.filepath)
            _name      = _name + "_PowerOff" + _ext
            _pathName  = os.path.join(_path,_name)

            bpy.ops.wm.save_as_mainfile(filepath=_pathName,copy=True)
        #]Save a Copy

        if rs.playAfterRender == True:
            if (str.lower(soundType) in soundExt) and os.path.exists(bpy.path.abspath(rs.soundToPlay)) == True:
                soundToPlay = bpy.path.abspath(rs.soundToPlay)
                if self._play == False:
                    device = aud.Device()
                    sound  = aud.Sound(os.path.normpath(soundToPlay))
                    self.handle = device.play(sound.volume(80))
                    if rs.loopSoundToPlay == True and rs.poweroffAfterRender == True: rs.loopSoundToPlay = False
                    if rs.loopSoundToPlay == True and rs.poweroffAfterRender == False: self.handle.loop_count = -1
                    else: self.handle.loop_count = rs.repeatSoundToPlay
                    self._play = True
            else:
                rs.soundToPlay = ''
                self.testSoundToPlay == False
                ShowMessageBox("Choose a sound file before !", "Wrong Sound File Type OR Not Exist", 'ERROR')
                self.report({"WARNING"}, 'Wrong Sound File Type OR Not Exist')
                return {"CANCELLED"}

            if rs.poweroffAfterRender == True and self.testSoundToPlay == False: self._stop = True
        else: self._stop = True

        rs.alarmInProgress = True
        rs.countDownAfterRender = 0
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)
        self._timer = context.window_manager.event_timer_add(1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


#RENDER FILE FORMAT ##################################################################################
class RENDER_OT_Renderformat(Operator):
    bl_idname = "render.renderformat"
    bl_label = "WARNING !"
    
    imageFileFormat: EnumProperty(
        name        ="Image File Format",
        description ='Image File Format',
        items       =[('PNG','PNG','','IMAGE',1),
                      ('JPEG','JPEG','','IMAGE',2),
                      ('JPEG2000','JPEG2000','','IMAGE',5),
                      ('BMP','BMP','','IMAGE',3),
                      ('TIFF','TIFF','','IMAGE',4),
                      ('TARGA','TARGA','','IMAGE',6),
                      ('TARGA_RAW','TARGA_RAW','','IMAGE',7),
                      ('CINEON','CINEON','','IMAGE',8),
                      ('DPX','DPX','','IMAGE',9),
                      ('OPEN_EXR','OPEN_EXR','','IMAGE',10),
                      ('OPEN_EXR_MULTILAYER','OPEN_EXR_MULTILAYER','','IMAGE',11),
                      ('HDR','HDR','','IMAGE',12),
                      ],default='PNG')

    def draw(self, context):
        scene          = context.scene
        rs             = scene.RBTab_Settings
        rd             = scene.render
        image_settings = rd.image_settings

        box = self.layout.box()
        row = box.row(align=True)
        row.alignment='CENTER'
        row.alert = True
        row.label(text = "Animation format selected !", icon="ERROR")


        row = box.row(align=True)
        row.alignment='CENTER'
        row.alert = True
        row.scale_y = 0.25
        row.label(text = "     Cannot write a single file")
        
        row = box.row()
        row.alignment='CENTER'
        row.scale_y = 1.5
        row.label(text = "Please Choose an IMAGE File Format")

        row = box.row()
        row.prop(self,'imageFileFormat',icon='IMAGE',text="")

        box.use_property_split = True
        box.use_property_decorate = False
        row = box.row(align=True)
        row.prop(rs,'onlyForThisJob',text='only for this job')

        if rs.onlyForThisJob:
            row = box.row(align=True)
            row.active = False
            row.alignment='CENTER'
            row.label(text = "( After Render Reset to : {0} )".format(image_settings.file_format))


    def execute(self, context):
        scene  = bpy.context.scene
        rs     = scene.RBTab_Settings
        rd     = scene.render
        image_settings = rd.image_settings
        
        image_settings.file_format = self.imageFileFormat

        return {'FINISHED'}


    def invoke(self, context, event):
        
        scene  = bpy.context.scene
        rs     = scene.RBTab_Settings
        rd     = scene.render

        rs.onlyForThisJob = False
        rs.currentFormatRenderType = rd.image_settings.file_format

        wm = context.window_manager
        return wm.invoke_props_dialog(self)


# Null ##################################################################################
class SCENECAMERA_OT_Null(Operator):
    bl_idname      = "cameramanager.null_tool"
    bl_label       = ""
    bl_description = "Camera Manager"

    nullMode : bpy.props.StringProperty(name="tool", default="")

    def invoke(self, context, event):
        scene         = context.scene
        chosen_camera = context.active_object
        selectedObj   = context.selected_objects
        cameras       = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)
        selectedCam   = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)

        if self.nullMode == 'SELECT':
            if chosen_camera not in selectedCam:
                if event.alt:
                    bpy.ops.cameramanager.select_tool("INVOKE_DEFAULT",selectTool = "INVERT")
                elif event.shift:
                    bpy.ops.cameramanager.select_tool("INVOKE_DEFAULT",selectTool = "ALL")
                else:
                    bpy.ops.cameramanager.select_tool("INVOKE_DEFAULT",selectTool = "NONE")

        elif self.nullMode == 'NOTSELECTED':
            self.report({"INFO"}, 'Select Camera Before !')

        elif self.nullMode == 'NULL':
            self.nullMode == ''
            return {"FINISHED"}

        self.nullMode == ''

        return {"FINISHED"}


# CAMERA SELECT TOOLS ##################################################################################
class SCENECAMERA_OT_SelectCamera(Operator):
    bl_idname      = "cameramanager.select_tool"
    bl_label       = "Camera Select Tool"
    bl_description = "Camera Select Tool"

    selectTool : bpy.props.StringProperty(default = "")

    def invoke(self, context, event):
        scene  = context.scene
        rs     = scene.RBTab_Settings
        render = scene.render

        selectedObj     = context.selected_objects
        cameras         = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)
        selectedCam     = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)
        noneSelectedCam = sorted([o for o in list(set(cameras) - set(selectedCam))],key=lambda o: o.name)
        constraintsCam  = sorted([o for o in cameras if len(o.constraints) > 0],key=lambda o: o.name)
        customDimCam    = sorted([o for o in cameras if o.RBTab_obj_Settings.Custom_CamRes_prop == True],key=lambda o: o.name)
        animDataCam     = sorted([o for o in cameras
                                    if (o.animation_data is not None) or (o.data.animation_data is not None)
                                    ],key=lambda o: o.name)
        emptyAnimCam    = sorted([o for o in animDataCam
                                    if (o.animation_data is not None and o.animation_data.action is None)
                                    or (o.data.animation_data is not None and o.data.animation_data.action is None)
                                    ],key=lambda o: o.name)

        marker_list         = context.scene.timeline_markers
        list_marked_cameras = [o.camera for o in marker_list if o != None]


        if self.selectTool == "ALL":
            if not event.shift: bpy.ops.object.select_all(action='DESELECT')
            for camera in cameras:
                camera.select_set(state = True)

            if scene.camera is None : scene.camera = cameras[0]

        elif self.selectTool == "NONE":
            for camera in cameras:
                camera.select_set(state = False)

        elif self.selectTool == "INVERT":
            if len(noneSelectedCam) != 0:
                if not event.shift:
                    for camera in selectedCam:
                        camera.select_set(state = False)
                for camera in noneSelectedCam:
                    camera.select_set(state = True)

                if scene.camera not in noneSelectedCam:
                    scene.camera = noneSelectedCam[0]
            else:
                for camera in cameras:
                    camera.select_set(state = False)

        elif self.selectTool == "TRACKTO":
            if event.shift:
                for camera in constraintsCam :
                    camera.select_set(state = True)
                return {"FINISHED"}

            for camera in selectedCam:
                camera.select_set(state = False)
            for camera in constraintsCam:
                camera.select_set(state = True)

            if scene.camera not in constraintsCam:
                scene.camera = constraintsCam[0]

        elif self.selectTool == "MARKER":
            if event.shift:
                for camera in list_marked_cameras :
                    camera.select_set(state = True)
                return {"FINISHED"}

            for camera in selectedCam:
                camera.select_set(state = False)
            for camera in list_marked_cameras :
                camera.select_set(state = True)

            if scene.camera not in list_marked_cameras:
                scene.camera = list_marked_cameras[0]

        elif self.selectTool == "ANIMDATA":
            if event.shift:
                for camera in animDataCam :
                    camera.select_set(state = True)
                return {"FINISHED"}

            for camera in selectedCam:
                camera.select_set(state = False)
            for camera in animDataCam :
                camera.select_set(state = True)

            if scene.camera not in animDataCam:
                scene.camera = animDataCam[0]

        elif self.selectTool == "EMPTYANIMDATA":
            if event.shift:
                for camera in emptyAnimCam :
                    camera.select_set(state = True)
                return {"FINISHED"}

            for camera in selectedCam:
                camera.select_set(state = False)
            for camera in emptyAnimCam :
                camera.select_set(state = True)

            if scene.camera not in emptyAnimCam:
                scene.camera = emptyAnimCam[0]

        elif self.selectTool == "CUSTOMDIM":
            if event.shift:
                for camera in customDimCam :
                    camera.select_set(state = True)
                return {"FINISHED"}

            for camera in selectedCam:
                camera.select_set(state = False)
            for camera in customDimCam :
                camera.select_set(state = True)

            if scene.camera not in customDimCam:
                scene.camera = customDimCam[0]

        elif self.selectTool == "SCCAMERA":
            scene.camera.select_set(state = True)


        if bpy.context.active_object is None or bpy.context.active_object not in selectedCam:
            bpy.context.view_layer.objects.active = bpy.data.objects[scene.camera.name]

        return {"FINISHED"}


# CAMERA TOOLS ##################################################################################
class SCENECAMERA_OT_CamTools(Operator):
    bl_idname      = "cameramanager.camera_tools"
    bl_label       = "Camera Tools"
    bl_description = "Camera Tools"

    tool                    : bpy.props.StringProperty(name="tool", default="")

    rotx                    : bpy.props.BoolProperty(name="rotx", default=True)
    roty                    : bpy.props.BoolProperty(name="roty", default=True)
    rotz                    : bpy.props.BoolProperty(name="rotz", default=True)

    locx                    : bpy.props.BoolProperty(name="locx", default=True)
    locy                    : bpy.props.BoolProperty(name="locy", default=True)
    locz                    : bpy.props.BoolProperty(name="locz", default=True)

    clearKeep               : bpy.props.BoolProperty(name="Clear Track & Keep Transformation", default=False)

    AnimDat_CopySelect      : bpy.props.BoolProperty(name="Select Datas", default=False)
    AnimDat_CopyLinked      : bpy.props.BoolProperty(name="Copy linked", default=True)
    AnimDat_CopyLinkedCam   : bpy.props.BoolProperty(name="Copy linked", default=True)
    AnimDat_CopyLinkedLens  : bpy.props.BoolProperty(name="Copy linked", default=True)

    AnimDat_CopyCamAnim     : bpy.props.BoolProperty(name="Select Datas", default=True)
    AnimDat_CopyLensAnim    : bpy.props.BoolProperty(name="Copy linked", default=True)

    AnimDat_CopyLoc         : bpy.props.BoolProperty(name="locz", default=False)
    AnimDat_CopyRot         : bpy.props.BoolProperty(name="locz", default=False)
    AnimDat_CopyLens        : bpy.props.BoolProperty(name="locz", default=False)

    lensType                : bpy.props.BoolProperty(name="Focal", default=False)
    lensFocal               : bpy.props.BoolProperty(name="Focal", default=False)
    lensShift               : bpy.props.BoolProperty(name="Shift", default=False)
    lensClip                : bpy.props.BoolProperty(name="Clip", default=False)

    clearEmtyAnimData       : bpy.props.BoolProperty(name="Clip", default=False)

    fcurvesCam  = []
    fcurvesLens = []

    _cameras        = []
    _selectedCam    = []
    _constraintsCam = []
    _animDataCam    = []
    _emptyAnimCam   = []

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type =='CAMERA'

    def execute(self, context):
        scene          = context.scene
        render         = scene.render
        chosen_camera  = scene.camera
        ob             = context.active_object
        rs             = scene.RBTab_Settings
        cs             = ob.RBTab_obj_Settings

        selectedObj    = context.selected_objects

    ### Copy tools---------------------------------------------------------
        ## Copy location[ ---
        if self.tool == 'LOCATION':
            for camera in self._selectedCam:
                if self.locx == True :
                    camera.location[0] = chosen_camera.location[0]
                if self.locy == True :
                    camera.location[1] = chosen_camera.location[1]
                if self.locz == True :
                    camera.location[2] = chosen_camera.location[2]
            self.locx = False
            self.locy = False
            self.locz = False

            self.report({"INFO"}, 'Copy Location OK')
            ## ]Copy location

        ## Copy Rotation[ ---
        if self.tool == 'ROTATION':
            for camera in self._selectedCam:
                if self.rotx == True :
                    camera.rotation_euler[0] = chosen_camera.rotation_euler[0]
                if self.roty == True :
                    camera.rotation_euler[1] = chosen_camera.rotation_euler[1]
                if self.rotz == True :
                    camera.rotation_euler[2] = chosen_camera.rotation_euler[2]
            self.rotx = False
            self.roty = False
            self.rotz = False

            self.report({"INFO"}, 'Copy Rotation OK')
            ## ]Copy Rotation


        ## Copy Track To[ ---
        if self.tool == 'TRACKTO':

            self._constraintsCam.remove(chosen_camera)

            if len(self._constraintsCam) > 0:

                bpy.ops.object.select_all(action='DESELECT')

                for camera in self._constraintsCam:
                    camera.select_set(state = True)

                scene.camera = bpy.context.view_layer.objects.active = self._constraintsCam[0]

                bpy.ops.cameramanager.removetrackto_scene_camera("EXEC_DEFAULT",event_Shift = self.clearKeep)

                bpy.ops.object.select_all(action='DESELECT')

                for camera in self._selectedCam:
                    camera.RBTab_obj_Settings.Custom_Camtrack_prop = True
                    camera.select_set(state = True)

                scene.camera = bpy.context.view_layer.objects.active = chosen_camera

            bpy.ops.object.constraints_copy()

            self.report({"INFO"}, 'Track To Constraint Copied')
            ## ]Copy Track To


        ## Copy Custom resolution[ ---
        if self.tool == 'CUSTOMRESOL':
            x    = cs.Custom_CamHRes_prop
            y    = cs.Custom_CamVRes_prop
            pa_x = cs.Custom_CamHPixRes_prop
            pa_y = cs.Custom_CamVPixRes_prop

            for camera in self._selectedCam:
                print(camera.name)
                cs = camera.RBTab_obj_Settings
                cs.Custom_CamHRes_prop    = x
                cs.Custom_CamVRes_prop    = y
                cs.Custom_CamHPixRes_prop = pa_x
                cs.Custom_CamVPixRes_prop = pa_y
                cs.Custom_CamRes_prop     = True

            self.report({"INFO"}, 'Custom Resolution Copied')
            ## ]Copy Custom resolution

        ## Copy Animation Datas[ ---
        if self.tool == 'ANIMDATAS':
            self._selectedCam.remove(context.object)
            obj   = bpy.context.object
            adobj = obj.animation_data
            adcam = obj.data.animation_data

            if self.AnimDat_CopyCamAnim == self.AnimDat_CopyLensAnim == False:
                ShowMessageBox("No Animation Datas Selected !", "Nothing Copied", 'ERROR')
                self.report({"WARNING"}, 'No Animation Datas Selected !')
                return {"CANCELLED"}

            if self.AnimDat_CopyCamAnim and self.AnimDat_CopyLinkedCam == False:
                if self.AnimDat_CopyLoc == self.AnimDat_CopyRot == False:
                    self.report({"WARNING"}, 'No Camera Animation Datas Copied !')

            if adobj: propObj = [p.identifier for p in adobj.bl_rna.properties if not p.is_readonly]
            if adcam: propCam = [p.identifier for p in adcam.bl_rna.properties if not p.is_readonly]

            removeUAD_OC = ['sca']
            removeUAD_C  = []

            if not self.AnimDat_CopyLoc : removeUAD_OC.append('loc')
            if not self.AnimDat_CopyRot : removeUAD_OC.append('rot')

            if not self.lensType :removeUAD_C.append('typ')
            if not self.lensFocal:removeUAD_C.append('len')
            if not self.lensShift:removeUAD_C.append('shi')
            if not self.lensClip :removeUAD_C.append('cli')

           #Copy Camera Animation Datas[
            if self.AnimDat_CopyCamAnim == True:
                for camera in self._selectedCam : #copy animation datas
                    if adobj:
                        if camera.animation_data == None: camera.animation_data_create()
                        adobj2 = camera.animation_data

                        if self.AnimDat_CopyLinkedCam: ## copy animation data LOCROTSCA linked
                            for prop in propObj: setattr(adobj2, prop, getattr(adobj, prop))
                        else:adobj2.action = adobj.action.copy() ## copy animation data LOCROTSCA unlinked

                if self.AnimDat_CopyLinkedCam == False: #Remove Unwanted Datas
                    for camera in self._selectedCam :
                        action = camera.animation_data.action
                        fcurves = [fc for fc in action.fcurves for type in removeUAD_OC if fc.data_path.startswith(type)]
                        while(fcurves):
                            fc = fcurves.pop()
                            action.fcurves.remove(fc)
           # ]Copy Camera Animation Datas

           #Copy Lens Animation Datas[
            if self.AnimDat_CopyLensAnim == True:
                for camera in self._selectedCam : #copy animation datas
                    if adcam:
                        cam = camera.data
                        if cam.animation_data == None: cam.animation_data_create()
                        adcam2 = cam.animation_data

                        if self.AnimDat_CopyLinkedLens: ## copy animation data LENS linked
                            for prop in propCam: setattr(adcam2, prop, getattr(adcam, prop))
                        else: adcam2.action = adcam.action.copy() ## copy animation data LENS unlinked

                if self.AnimDat_CopyLinkedLens == False: #Remove Unwanted Datas
                    for camera in self._selectedCam :
                        action = camera.data.animation_data.action
                        fcurves = [fc for fc in action.fcurves for type in removeUAD_C if fc.data_path.startswith(type)]
                        print(fcurves)
                        while(fcurves):
                            fc = fcurves.pop()
                            action.fcurves.remove(fc)
           # ]Copy Lens Animation Datas

            #self.report({"INFO"}, 'Copy Animation Datas OK')
            return {"FINISHED"}
            ## ]Copy Animation Datas


        ## Copy Lens Datas[ ---
        if self.tool == 'LENS':
            for camera in self._selectedCam:
                cam = camera.data

                if self.lensType :
                    cam.type = chosen_camera.data.type

                if self.lensFocal:
                    if cam.type == 'PERSP':
                        cam.lens = chosen_camera.data.lens
                    elif cam.type == 'ORTHO':
                        cam.ortho_scale = chosen_camera.data.ortho_scale
                    #elif cam.type == 'PANO':

                if self.lensShift:
                    cam.shift_x = chosen_camera.data.shift_x
                    cam.shift_y = chosen_camera.data.shift_y

                if self.lensClip :
                    cam.clip_start = chosen_camera.data.clip_start
                    cam.clip_end   = chosen_camera.data.clip_end

            return {"FINISHED"}
        ## Copy Lens Datas[ ---
    ### ]Copy tools

    ### Clear tools---------------------------------------------------------

        # if active camera not in selection --> active the first in selection
        if scene.camera not in self._selectedCam or context.active_object not in self._selectedCam or context.active_object.type!='CAMERA':
            bpy.context.view_layer.objects.active = bpy.data.objects[self._selectedCam[0].name]

        ## Clear Animation data[ ---
        if self.tool in ('CLEARANIMDATA','CLEARALL'):
            for camera in self._selectedCam:
                if self.clearEmtyAnimData:
                    if camera.animation_data is not None and camera.animation_data.action is None:
                        camera.animation_data_clear()
                    if camera.data.animation_data is not None and camera.data.animation_data.action is None:
                        camera.data.animation_data_clear()
                else:
                    camera.animation_data_clear()
                    camera.data.animation_data_clear()

            if self.tool == 'CLEARANIMDATA': self.report({"INFO"}, 'Animation Datas Removed')
                ## ]Clear Animation data

        ## Clear Custom Resolution[ ---
        if self.tool in ('CLEARRESOLUTION','CLEARALL'):
            for camera in self._selectedCam :
                cs = camera.RBTab_obj_Settings
                cs.Custom_CamRes_prop     = False
                cs.Custom_CamHRes_prop    = rs.Default_HRes_prop
                cs.Custom_CamVRes_prop    = rs.Default_VRes_prop
                cs.Custom_CamHPixRes_prop = rs.Default_HPixRes_prop
                cs.Custom_CamVPixRes_prop = rs.Default_VPixRes_prop
                render.resolution_x       = rs.Default_HRes_prop
                render.resolution_y       = rs.Default_VRes_prop
                render.pixel_aspect_x     = rs.Default_HPixRes_prop
                render.pixel_aspect_y     = rs.Default_VPixRes_prop

            if self.tool == 'CLEARRESOLUTION': self.report({"INFO"}, 'Custom Resolution Removed')
                ## ]Clear Custom Resolution

        ## Clear Track To Constraint[ ---
        if self.tool in ('CLEARTRACKTO','CLEARALL'):
            bpy.ops.cameramanager.removetrackto_scene_camera("EXEC_DEFAULT",event_Shift = self.clearKeep)
            self.clearKeep = False
            if self.tool == 'CLEARTRACKTO': self.report({"INFO"}, 'Track To Constraint Removed')
            ## ]Clear Track To Constraint

        ## Clear Timeline Marker[ ---
        if self.tool in ('CLEARMARKER','CLEARALL'):
            bpy.ops.cameramanager.remove_camera_marker("EXEC_DEFAULT",event_Shift = True)

            if self.tool == 'CLEARMARKER': self.report({"INFO"}, 'Timeline Marker Removed')
            else: self.report({"INFO"}, 'Clear All OK')
            ## ]Clear Timeline Marker
    ### ]Clear tools

        return {'FINISHED'}


    def invoke(self, context, event):
        scene = context.scene
        obj   = context.object
        adobj = obj.animation_data
        adcam = obj.data.animation_data

        selectedObj          = context.selected_objects
        self._selectedCam    = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)
        self._cameras        = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)
        self._constraintsCam = sorted([o for o in self._selectedCam if len(o.constraints) > 0],key=lambda o: o.name)
        self._animDataCam    = sorted([o for o in self._cameras
                                    if (o.animation_data is not None) or (o.data.animation_data is not None)
                                    ],key=lambda o: o.name)
        self._emptyAnimCam   = sorted([o for o in self._animDataCam
                                    if (o.animation_data is not None and o.animation_data.action is None)
                                    or (o.data.animation_data is not None and o.data.animation_data.action is None)
                                    ],key=lambda o: o.name)

        self.fcurvesCam  = []
        self.fcurvesLens = []
        if adobj and adobj.action:
            _rot = ('rotation_euler','rotation_quaternion','rotation_axis_angle')
            for fc in adobj.action.fcurves:
                if fc.data_path in _rot: self.fcurvesCam.append('rotation')
                else: self.fcurvesCam.append(fc.data_path)
            self.fcurvesCam = list(dict.fromkeys(self.fcurvesCam))

        if adcam and adcam.action:
            self.fcurvesLens = [fc.data_path for fc in adcam.action.fcurves if adcam]

        self.AnimDat_CopyCamAnim    =True
        self.AnimDat_CopyCamLens    =True
        self.AnimDat_CopyLinkedCam  =True
        self.AnimDat_CopyLinkedLens =True
        self.AnimDat_CopyLoc        =False
        self.AnimDat_CopyRot        =False
        self.AnimDat_CopyLens       =False
        self.lensType               =False
        self.lensFocal              =False
        self.lensShift              =False
        self.lensClip               =False
        self.clearEmtyAnimData      = False


        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        scene  = context.scene
        layout = self.layout
        ob = context.active_object
        cs = ob.RBTab_obj_Settings

        obj   = context.object
        adobj = obj.animation_data
        adcam = obj.data.animation_data

        selectedObj  = bpy.context.selected_objects

        row = layout.row(align=True)
        row.alignment='CENTER'

    ### Tools confirmation dialog box---------------------------------------------------------

     ## Copy Tools[---------------------
        ## Copy location dialog box[ ---
        if self.tool == 'LOCATION':
            row.label(text='Copy Location')
            row = layout.row(align=True)
            row.alignment='CENTER'
            row.label(text='{0}  To Selected'.format(scene.camera.name))
            row = layout.row(align=True)
            row.alignment='CENTER'
            row.prop(self,'locx', text="X")
            row.prop(self,'locy', text="Y")
            row.prop(self,'locz', text="Z")
            ## ]Copy location dialog box

        ## Copy Rotation dialog box[ ---
        elif self.tool == 'ROTATION':
            row.label(text='Copy Rotation')
            row = layout.row(align=True)
            row.alignment='CENTER'
            row.label(text='{0}  To Selected'.format(scene.camera.name))
            row = layout.row(align=True)
            row.alignment='CENTER'
            row.prop(self,'rotx', text="X")
            row.prop(self,'roty', text="Y")
            row.prop(self,'rotz', text="Z")
            ## ]Copy Rotation dialog box

        ## Copy Animation Datas dialog box[ ---
        elif self.tool == 'ANIMDATAS':
            row = layout.row(align=True)
            row.alignment='CENTER'

            row.label(text='Copy Animation Datas To Selected')
            row = layout.row(align=True)

            if adobj:
                if adobj.action:
                    row.prop(self,'AnimDat_CopyCamAnim',text='Camera Animation',icon='NONE',toggle=1)
                    if self.AnimDat_CopyCamAnim == True:
                        if self.AnimDat_CopyLinkedCam == False:
                            row.prop(self,'AnimDat_CopyLinkedCam',text='Copy linked',icon='CHECKBOX_DEHLT')
                            row = layout.row(align=True)
                            row.alignment='CENTER'
                            if 'location' in self.fcurvesCam:
                                row.prop(self,'AnimDat_CopyLoc',text='Location')
                            if 'rotation' in self.fcurvesCam:
                                row.prop(self,'AnimDat_CopyRot',text='Rotation')
                        else: row.prop(self,'AnimDat_CopyLinkedCam',text='Copy linked',icon='CHECKBOX_HLT')

            row = layout.row(align=True)

            if adcam:
                if adcam.action:
                    row = layout.row(align=True)
                    row.prop(self,'AnimDat_CopyLensAnim',text='Lens Animation',icon='NONE',toggle=1)
                    if self.AnimDat_CopyLensAnim == True:
                        if self.AnimDat_CopyLinkedLens == False:
                            row.prop(self,'AnimDat_CopyLinkedLens',text='Copy linked',icon='CHECKBOX_DEHLT')
                            row = layout.row(align=True)
                            row.alignment='CENTER'
                            if 'type' in self.fcurvesLens:
                                row.prop(self,'lensType',text='Type')
                            if 'lens' in self.fcurvesLens:
                                row.prop(self,'lensFocal',text='Focal')
                            if 'shift_y' in self.fcurvesLens or 'shift_x' in self.fcurvesLens:
                                row.prop(self,'lensShift',text='Shift')
                            if 'clip_start' in self.fcurvesLens or 'clip_end' in self.fcurvesLens:
                                row.prop(self,'lensClip',text='Clip')
                        else: row.prop(self,'AnimDat_CopyLinkedLens',text='Copy linked',icon='CHECKBOX_HLT')

            row = layout.row(align=True)
            ## ]Copy Animation Datas dialog box

        ## Copy Track To dialog box[ ---
        elif self.tool == 'TRACKTO':
            row = layout.row(align=True)
            row.alignment='CENTER'
            row.label(text='Copy Constraints')
            row = layout.row(align=True)
            row.alignment='CENTER'
            row.label(text='{0}  To Selected'.format(scene.camera.name))
            ## ]Copy Track To dialog box

        ## Copy Resolution dialog box[ ---
        elif self.tool == 'CUSTOMRESOL':
            row.alignment='CENTER'
            row.label(text='Copy Custom Resolution')
            row = layout.row(align=True)
            row.alignment='CENTER'
            row.label(text='{0}  To Selected'.format(scene.camera.name))
            row = layout.row(align=True)
            row.alignment='CENTER'
            row.label(text="{0} x {1}".format(cs.Custom_CamHRes_prop,cs.Custom_CamVRes_prop))
            ## ]Copy Resolution dialog box

        ## Copy Lens Settings dialog box[ ---
        elif self.tool == 'LENS':
            row.alignment='CENTER'
            row.label(text='Copy Lens Settings to Selected')
            row = layout.row(align=True)
            row.alignment='CENTER'
            row.prop(self,'lensType',text='Type')
            row.prop(self,'lensFocal',text='Focal')
            row.prop(self,'lensShift',text='Shift')
            row.prop(self,'lensClip',text='Clip')
            ## ]Copy Lens Settings dialog box
     ## ]Copy Tools

    ##########################################################################

     ## Clear Tools[---------------------------
        ## Clear Animation Data dialog box[ ---
        elif self.tool == 'CLEARANIMDATA':
            camWithEmptyAnimSelected = len(list(set(self._selectedCam).intersection(self._emptyAnimCam)))
            if self.clearEmtyAnimData == False:
                row.alert = True
                row.label(text='Clear All Camera Animation Data ?',icon='ERROR')
            row = layout.row(align=True)
            row.alignment ='CENTER'
            if camWithEmptyAnimSelected > 0 :
                row.prop(self,'clearEmtyAnimData', text="Clear Empty Animation Datas")
            ## ]Clear Animation Data dialog box

        ## Clear Resolution dialog box[ ---
        elif self.tool =='CLEARRESOLUTION':
            row.alert = True
            row.label(text='Clear Custom Resolution ?',icon='ERROR')
            ## ]Clear Resolution dialog box

        ## Clear Track To dialog box[ ---
        elif self.tool =='CLEARTRACKTO':
            row.alert = True
            row.label(text='Clear Track To Constraint ?',icon='ERROR')
            row = layout.row(align=True)
            row.alignment ='CENTER'
            row.prop(self,'clearKeep', text="Keep Transformations")
            ## ]Clear Track To dialog box

        ## Clear Marker dialog box[ ---
        elif self.tool =='CLEARMARKER':
            row.alert = True
            row.label(text='Clear Camera Timeline Markers ?',icon='ERROR')
            ## ]Clear Marker dialog box

        ## Clear All dialog box[ ---
        elif self.tool =='CLEARALL':
            row.alert = True
            row.label(text='Clear Camera Datas ?',icon='ERROR')
            ## ]Clear All dialog box
     ## ]Clear Tools
    ### ]Tools confirmation dialog box


#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#UI-MENUS//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# TOOLS MENU CAMERA ##################################################################################
class SCENECAMERA_MT_ToolsMenu(Menu):
    bl_label       = "Select Camera"
    bl_idname      = "SCENECAMERA_MT_toolsmenu"
    bl_description = "Copy scene camera attribut to selected"

    def draw(self, context):
        scene  = context.scene
        rs     = scene.RBTab_Settings
        render = scene.render

        _cc   = False
        _adc  = False
        _mc   = False
        _cdc  = False
        _cAll = False

        cameras         = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)
        selectedObj     = context.selected_objects
        selectedCam     = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)
        noneSelectedCam = list(set(cameras) - set(selectedCam))
        constraintsCam  = sorted([o for o in cameras if len(o.constraints) > 0],key=lambda o: o.name)
        customDimCam    = sorted([o for o in cameras if o.RBTab_obj_Settings.Custom_CamRes_prop == True],key=lambda o: o.name)

        animDataCam     = sorted([o for o in cameras
                                    if (o.animation_data is not None) or (o.data.animation_data is not None)
                                    ],key=lambda o: o.name)
        emptyAnimCam   = sorted([o for o in animDataCam
                                    if (o.animation_data is not None and o.animation_data.action is None)
                                    or (o.data.animation_data is not None and o.data.animation_data.action is None)
                                    ],key=lambda o: o.name)

        marker_list         = context.scene.timeline_markers
        list_marked_cameras = [o.camera for o in marker_list if o != None]

        ## Test to activate only the relevant menu entries[ ---
        for o in selectedCam:
            if o in constraintsCam      : _cc   = True
            if o in animDataCam         : _adc  = True
            if o in list_marked_cameras : _mc   = True
            if o in customDimCam        : _cdc  = True

        if sum([_cc,_adc,_mc,_cdc]) > 1 : _cAll = True
        ## ]Test to activate only the relevant menu entries

    ## Copy menu entries[ ---
        layout  = self.layout
        row = layout.row(align=True)

        if len(selectedObj) <= 1: row.enabled = False
        else: row.enabled = True

        row.label(text='Copy Tools',icon='COPYDOWN')

        row = layout.row(align=True)
        if len(selectedObj) <= 1 or scene.camera not in selectedObj: row.enabled = False
        else: row.enabled = True
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator("cameramanager.camera_tools",text='copy Location').tool='LOCATION'

        row = layout.row(align=True)
        if len(selectedObj) <= 1 or scene.camera not in selectedObj: row.enabled = False
        else: row.enabled = True
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator("cameramanager.camera_tools",text='copy Rotation').tool='ROTATION'

        row = layout.row(align=True)
        row.enabled = False
        if len(selectedObj) <= 1 or scene.camera not in selectedObj: row.enabled = False
        elif scene.camera in constraintsCam and scene.camera in selectedCam: row.enabled = True
        row.operator("cameramanager.camera_tools",text="copy TrackTo Constraint").tool="TRACKTO"

        row = layout.row(align=True)
        row.enabled = False
        if len(selectedObj) <= 1 or scene.camera not in selectedObj: row.enabled = False
        elif scene.camera in animDataCam and scene.camera in selectedCam and scene.camera not in emptyAnimCam: row.enabled = True
        row.operator("cameramanager.camera_tools",text="copy Animation Datas").tool="ANIMDATAS"

        row = layout.row(align=True)
        row.enabled = False
        if len(selectedObj) <= 1 or scene.camera not in selectedObj: row.enabled = False
        elif scene.camera in customDimCam and scene.camera in selectedCam: row.enabled = True
        row.operator("cameramanager.camera_tools",text="copy Custom Resolution").tool="CUSTOMRESOL"

        row = layout.row(align=True)
        if len(selectedObj) <= 1 or scene.camera not in selectedObj: row.enabled = False
        else: row.enabled = True
        row.operator("cameramanager.camera_tools",text="copy Lens Settings").tool="LENS"
        ## ]Copy menu entries

        layout.separator()

    ## Clear menu entries[ ---
        row = layout.row(align=True)
        row.label(text='Clear Tools',icon='FILE_REFRESH')

        row = layout.row(align=True)
        row.enabled = False
        if _adc == False: row.enabled = False
        else: row.enabled = True
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator("cameramanager.camera_tools",text='Clear Animation Datas').tool='CLEARANIMDATA'

        row = layout.row(align=True)
        row.enabled = False
        if _cdc == False: row.enabled = False
        else: row.enabled = True
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator("cameramanager.camera_tools",text='Clear Custom Resolution').tool='CLEARRESOLUTION'

        row = layout.row(align=True)
        row.enabled = False
        if _cc == False: row.enabled = False
        else: row.enabled = True
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator("cameramanager.camera_tools",text='Clear Track To Constraint').tool='CLEARTRACKTO'

        row = layout.row(align=True)
        row.enabled = False
        if _mc == False: row.enabled = False
        else: row.enabled = True
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator("cameramanager.camera_tools",text='Clear Timeline Marker').tool='CLEARMARKER'

        row = layout.row(align=True)
        row.enabled = False
        if _cAll == False: row.enabled = False
        else: row.enabled = True
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator("cameramanager.camera_tools",text='Clear All').tool='CLEARALL'
        ## ]Clear menu entries


# SELECT MENU CAMERA ##################################################################################
class SCENECAMERA_MT_SelectMenu(Menu):
    bl_label       = "Select Camera"
    bl_idname      = "SCENECAMERA_MT_selectmenu"
    bl_description = "Camera Tools"

    def draw(self, context):
        scene  = context.scene
        rs     = scene.RBTab_Settings
        render = scene.render

        cameras         = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)
        selectedObj     = context.selected_objects
        selectedCam     = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)
        noneSelectedCam = list(set(cameras) - set(selectedCam))
        constraintsCam  = sorted([o for o in cameras if len(o.constraints) > 0],key=lambda o: o.name)
        customDimCam    = sorted([o for o in cameras if o.RBTab_obj_Settings.Custom_CamRes_prop == True],key=lambda o: o.name)

        animDataCam     = sorted([o for o in cameras
                                    if (o.animation_data is not None) or (o.data.animation_data is not None)
                                    ],key=lambda o: o.name)
        emptyAnimCam    = sorted([o for o in animDataCam
                                    if (o.animation_data is not None and o.animation_data.action is None)
                                    or (o.data.animation_data is not None and o.data.animation_data.action is None)
                                    ],key=lambda o: o.name)

        marker_list         = context.scene.timeline_markers
        list_marked_cameras = [o.camera for o in marker_list if o != None]

        layout  = self.layout
        row = layout.row(align=True)

        row.operator("cameramanager.select_tool",text="All").selectTool="ALL"
        row = layout.row(align=True)
        row.operator("cameramanager.select_tool",text="None").selectTool="NONE"
        row = layout.row(align=True)
        row.operator("cameramanager.select_tool",text="Invert").selectTool="INVERT"
        row = layout.row(align=True)
        row.operator("cameramanager.select_tool",text="Scene Camera").selectTool="SCCAMERA"


        layout.separator()

        row = layout.row(align=True)
        if len(constraintsCam)>0:row.enabled = True
        else: row.enabled = False
        row.operator("cameramanager.select_tool",text="With Tract to",icon='CON_FOLLOWTRACK').selectTool="TRACKTO"

        row = layout.row(align=True)
        if len(list_marked_cameras)>0:row.enabled = True
        else: row.enabled = False
        row.operator("cameramanager.select_tool",text="With Marker",icon='MARKER_HLT').selectTool="MARKER"

        row = layout.row(align=True)
        if len(animDataCam)>0:row.enabled = True
        else: row.enabled = False
        row.operator("cameramanager.select_tool",text="With Anim Datas",icon='KEYTYPE_KEYFRAME_VEC').selectTool="ANIMDATA"

        row = layout.row(align=True)
        if len(emptyAnimCam)>0:row.enabled = True
        else: row.enabled = False
        row.operator("cameramanager.select_tool",text="With Empty Anim Datas",icon='KEYFRAME').selectTool="EMPTYANIMDATA"

        row = layout.row(align=True)
        if len(customDimCam)>0:row.enabled = True
        else: row.enabled = False
        row.operator("cameramanager.select_tool",text="With Custom Resolution",icon='WORKSPACE').selectTool="CUSTOMDIM"


#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#UI-PANEL//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# RENDER BUTTON PROPERTIES ######################################################################################
class MYBIGBUTTON_PT_MyBigButton(Panel):
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context     = "render"
    bl_label       = "Render"
    bl_idname      = "MYBIGBUTTON_PT_MyBigButton"
    bl_options     = {'HIDE_HEADER'}


    @classmethod
    def poll(cls, context):
        return bpy.context.scene.RBTab_Settings.alarmInProgress == False

    def draw(self, context):
        scene  = context.scene
        rd     = context.scene.render

        layout = self.layout
        split  = layout.split()

        layout.use_property_split    = True
        layout.use_property_decorate = False

        row = layout.row(align=True)
        row.scale_y = 2.5

        if (context.active_object is not None) and (context.active_object.mode !='OBJECT'):
            row.enabled = False

        if (scene.RBTab_Settings.switchStillAnim_prop == True):
            row.operator("cameramanager.render_scene_animation", text="RENDER ANIMATION")

        else:
            row.operator("cameramanager.render_scene_camera", text="RENDER FRAME").renderFrom = 'PROPERTIES'

        row.prop(scene.RBTab_Settings, "switchStillAnim_prop", text="",icon='RENDER_ANIMATION')

        if (scene.RBTab_Settings.switchStillAnim_prop == True):
            row = layout.row(align=True)

            if (context.active_object is not None) and (context.active_object.mode !='OBJECT'):
                row.enabled = False

            if scene.show_subframe:
                row.prop(scene, "frame_float", text="")
            else:
                row.prop(scene, "frame_current", text="")

            row.separator()

            row.prop(scene, "use_preview_range", text="", toggle=True)

            sub = row.row(align=True)
            sub.scale_x = 0.95

            if not scene.use_preview_range:
                sub.prop(scene, "frame_start", text="")
                sub.prop(scene, "frame_end", text="")
            else:
                sub.prop(scene, "frame_preview_start", text="")
                sub.prop(scene, "frame_preview_end", text="")

        layout.separator()
        row = layout.row()

        if (context.active_object is not None) and (context.active_object.mode == 'EDIT'):
            row.enabled = False



        prefs = context.preferences
        view = prefs.view
        row.prop(view, "render_display_type")


       # row.prop(rd, "display_mode")
        row.prop(rd, "use_lock_interface", text="", emboss=False, icon='DECORATE_UNLOCKED')

        layout.separator()



# RENDER BUTTON TAB ######################################################################################
class MYBIGBUTTONTAB_PT_MyBigButton(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "Render"
    bl_context     = "objectmode"
    bl_label       = "Render"
    bl_idname      = "MYBIGBUTTONTAB_PT_MyBigButton"


    @classmethod
    def poll(cls, context):
        return bpy.context.scene.RBTab_Settings.alarmInProgress == False

    def draw_header_preset(self, context):
        scene = context.scene
        rs    = scene.RBTab_Settings

        layout        = self.layout
        layout.emboss = 'NONE'
        row           = layout.row(align=True)

        if rs.mbbOptions == False:

            row.operator("render.opengl", text="", icon='RENDER_STILL')
            row.operator("render.opengl", text="", icon='RENDER_ANIMATION').animation = True
            row.operator("screen.screen_full_area", text ="", icon = 'FULLSCREEN_ENTER').use_hide_panels=False
            row.separator()
            row.separator()
            row.separator()
            row.separator()

    def draw_header(self, context):
        scene  = context.scene
        render = scene.render
        rs     = scene.RBTab_Settings

        layout        = self.layout
        layout.emboss = 'NONE'
        row           = layout.row(align=True)

        if rs.mbbOptions == True:
            _emboss   = True
            row.alert = True
        else:
            _emboss   = False
            row.alert = False

        row.prop(rs,"mbbOptions", icon='SETTINGS', icon_only= True)#


    def draw(self, context):
        scene = context.scene
        rd    = scene.render
        rs    = scene.RBTab_Settings
        image_settings = rd.image_settings

        layout = self.layout

        if rs.mbbOptions == False:
            row = layout.row(align=True)
            row.scale_y = 2.5
            #row.alert = True

            if (scene.RBTab_Settings.switchStillAnim_prop == True):
                row.operator("cameramanager.render_scene_animation", text="RENDER ANIMATION")
            else:
                row.operator("cameramanager.render_scene_camera", text="RENDER FRAME").renderFrom = 'TAB'

            row.prop(scene.RBTab_Settings, "switchStillAnim_prop", text="",icon='RENDER_ANIMATION')

            # Frame Range
            if (scene.RBTab_Settings.switchStillAnim_prop == True):
                row = layout.row(align=True)

                if scene.show_subframe:
                    row.prop(scene, "frame_float", text="")
                else:
                    row.prop(scene, "frame_current", text="")

                row.separator()

                row.prop(scene, "use_preview_range", text="", toggle=True)

                sub = row.row(align=True)
                sub.scale_x = 0.95

                if not scene.use_preview_range:
                    sub.prop(scene, "frame_start", text="")
                    sub.prop(scene, "frame_end", text="")
                else:
                    sub.prop(scene, "frame_preview_start", text="")
                    sub.prop(scene, "frame_preview_end", text="")
            layout.separator()
            row = layout.row()

            if rd.has_multiple_engines:
                row.prop(rd, "engine", text="")

            prefs = context.preferences
            view = prefs.view
            row.prop(view, "render_display_type", text="")

            row.prop(rd, "use_lock_interface", text="", emboss=False, icon='DECORATE_UNLOCKED')


    ###RENDER SETTINGS[_____________________________________________________________________________
        else:
        ## if file not saved[---
            if bpy.data.is_saved == False:
                layout.use_property_split = False
                row = layout.row(align=True)
                row.alignment='CENTER'
                row.alert = True
                row.label(text=' Save Blend File First  --->', icon='INFO')
                row.operator('wm.save_mainfile', text='', icon='FILE_TICK')
                row.alert = False
            ## ]if file not saved

            else:
                row = layout.row(align=True)
                box = layout.box()
                row = box.row(align=True)
                row.alert = True
                row.alignment='CENTER'

                row.label(text='Output')

                row = box.row(align=True)

                row.prop(image_settings, 'file_format',icon='IMAGE',text="")
                row = box.row(align=True)
                if rs.saveInBlendFolder == False:
                    row.prop(rd, "filepath", text="")

                row = box.row(align=True)
                row.prop(rs,'saveInBlendFolder',text='In blend folder',icon='BLENDER')
                row.prop(rs,'storeRenderInSlots',text='In render slots',icon='RENDER_RESULT')
             ## ]Output settings


            ## Alarm settings[---
                row = layout.row(align=True)
                box = layout.box()
                row = box.row(align=True)
                row.alert     = True
                row.alignment ='CENTER'

                row.label(text='Alarm & Power Off')

                row = box.row(align=True)

                row.prop(rs,'playAfterRender',text='Play Sound', icon='FILE_SOUND')

                if rs.playAfterRender == True:
                    if (rs.loopSoundToPlay == False or rs.poweroffAfterRender == True) and rs.soundToPlay != '':
                        row.prop(rs,'repeatSoundToPlay', text='Repeat')

                    if rs.poweroffAfterRender == False and rs.soundToPlay != '':
                        row.prop(rs,"loopSoundToPlay",text='', icon='RECOVER_LAST')

                    row = box.row(align=True)
                    if rs.soundToPlay == '':
                        row.alert = True
                        row.prop(rs, "soundToPlay", text="")
                        row.alert = False
                    else:
                        row.prop(rs, "soundToPlay", text="")

                    if rs.soundToPlay != '':
                        row.operator("renderevents.end_events",text='', icon='PLAY_SOUND').testSoundToPlay = True

                row = box.row(align=True)
                row.prop(rs,'poweroffAfterRender', icon ='QUIT')

                if rs.poweroffAfterRender == True:
                    row.prop(rs,'timeoutPowerOff',text='Timeout')
            ## ]Alarm settings
     ### ]RENDER SETTINGS



# CAMERA MANAGER PANEL ######################################################################################
class CAMMANAGER_PT_Cammanager(Panel):
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context     = "objectmode"
    bl_category    = "Render"
    bl_label       = "Camera Manager"
    bl_idname      = "CAMMANAGER_PT_Cammanager"


    @classmethod
    def poll(cls, context):
        return bpy.context.scene.RBTab_Settings.alarmInProgress == False

    def draw_header_preset(self, context):
        scene  = context.scene
        render = scene.render
        rs     = scene.RBTab_Settings

        layout = self.layout
        row    = layout.row(align=True)

        if rs.cmOptions == False:
            layout.emboss = 'NORMAL'
            row.alert     = True

            if rs.playAfterRender == True:
                a,soundType = os.path.splitext(rs.soundToPlay)
                soundExt    = bpy.path.extensions_audio
                row.alert   = False
                row.enabled = False
                if rs.soundToPlay =='':
                    if rs.poweroffAfterRender == False:
                        row.label(text="", icon = 'FILE_SOUND')
                        row.separator()
                        row.separator()
                        row.separator()
                        row.separator()
                    else:
                        row.label(text="", icon = 'FILE_SOUND')

                elif str.lower(soundType) in soundExt or os.path.exists(bpy.path.abspath(rs.soundToPlay)) == True:
                    row.alert   = True
                    row.enabled = True
                    if rs.poweroffAfterRender == False:
                        row.label(text="", icon = 'FILE_SOUND')
                        row.separator()
                        row.separator()
                        row.separator()
                        row.separator()
                    else: row.label(text="", icon = 'FILE_SOUND')

            if rs.poweroffAfterRender == True:
                row.label(text="", icon = 'QUIT')
                row.separator()
                row.separator()
                row.separator()
                row.separator()

    def draw_header(self, context):
        scene  = context.scene
        render = scene.render
        rs     = scene.RBTab_Settings

        layout = self.layout
        row    = layout.row(align=True)

        if rs.cmOptions == True:
            _emboss   = True
            row.alert = True
        else:
            _emboss   = False
            row.alert = False

        row.prop(rs,"cmOptions",text='', icon='SETTINGS',emboss=_emboss)

    def draw(self, context):
        layout  = self.layout
        scene   = context.scene
        rs      = scene.RBTab_Settings
        render  = scene.render
        cameras = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)

        selectedObj    = bpy.context.selected_objects
        selectedCam    = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)
        constraintsCam = sorted([o for o in cameras if len(o.constraints) > 0],key=lambda o: o.name)

        animDataCam    = sorted([o for o in cameras
                                    if (o.animation_data is not None) or (o.data.animation_data is not None)
                                    ],key=lambda o: o.name)
        emptyAnimCam   = sorted([o for o in animDataCam
                                    if (o.animation_data is not None and o.animation_data.action is None)
                                    or (o.data.animation_data is not None and o.data.animation_data.action is None)
                                    ],key=lambda o: o.name)

        render_all_list = []

        if rs.cmOptions == False:
            for camera in cameras:
                rs_obj = camera.RBTab_obj_Settings
                if rs_obj.Custom_CamRender_prop == True:
                    render_all_list += sorted([cameras])

            marker_list         = context.scene.timeline_markers
            marker_list_camera  = [o for o in marker_list if o.camera != None]
            list_marked_cameras = [o.camera for o in marker_list if o != None]
            render_marker_list  = []

            for marker in marker_list_camera:
                rs_obj = marker.camera.RBTab_obj_Settings
                if rs_obj.Custom_CamRender_prop == True:
                    render_marker_list += sorted([marker])

    ###Buttons above Cameras List[ ________________________________________________________________________________
            #Add Camera to view button
            layout.operator("cameramanager.add_scene_camera",text='Add Camera To View', icon='ADD')

            view = context.space_data

            if len(cameras) > 0:
                row = layout.row(align=True)

                #Camera Lock view button
                _iconlockview=''
                if bpy.context.space_data.lock_camera == True: _iconlockview='LOCKED'
                else: _iconlockview='UNLOCKED'
                row.prop(view, "lock_camera", text="Lock Camera",icon=_iconlockview)

                row.separator()

                #Use as local Camera button
                _iconUseLocal=''
                if bpy.context.space_data.use_local_camera == True: _iconUseLocal='PINNED'
                else: _iconUseLocal='UNPINNED'
                row.prop(view, "use_local_camera", text="Use Local",icon=_iconUseLocal)
    ### ]Buttons above Cameras List

                layout.separator()

    ###Cameras List[ ______________________________________________________________________________________________

                if len(cameras) >1:
                    row = layout.row(align=True)
                    row.menu(SCENECAMERA_MT_SelectMenu.bl_idname,text="Selection",icon='BORDERMOVE')
                    if len(selectedCam)>0:
                        row.menu(SCENECAMERA_MT_ToolsMenu.bl_idname,text="Tools",icon='TOOL_SETTINGS')
                for camera in cameras:
                    rs_obj = camera.RBTab_obj_Settings
                    row    = layout.row(align=True)

                    row.context_pointer_set("active_object", camera)

                    if rs.Manager_ShowSelect == True:
                        if len(selectedCam)>0:

                            if rs.Manager_ShowSelect_Gray == True and len(selectedCam)>1: row.active = False

                            if camera in selectedObj:

                                if rs.Manager_ShowSelect_Pointer == True:
                                    row.operator("cameramanager.null_tool", text="", icon='RIGHTARROW_THIN',emboss=False).nullMode='SELECT'
                                    #row.label(text ="",icon='RIGHTARROW_THIN')

                                if rs.Manager_ShowSelect_Color == True:
                                    row.alert = True

                                row.active = True
                            else:
                                if rs.Manager_ShowSelect_Pointer == True:
                                    row.operator("cameramanager.null_tool", text="", icon='BLANK1',emboss=False).nullMode='SELECT'

                    elif len(selectedCam)>0 and camera in selectedObj: row.alert = True

                    #Preview Camera button
                    _iconPreview       = ''
                    _iconPreviewEmboss = None
                    if camera == bpy.context.space_data.camera:
                        _iconPreview       = 'RESTRICT_VIEW_OFF'
                        _iconPreviewEmboss = True
                    else:
                        if rs_obj.Custom_CamRes_prop == True:
                            if camera == scene.camera:
                                _iconPreview       = 'CAMERA_DATA'
                                _iconPreviewEmboss = False
                            else:
                                _iconPreview       = 'WORKSPACE'
                                _iconPreviewEmboss = False
                        else:
                            if camera == scene.camera:
                                _iconPreview       = 'CAMERA_DATA'
                                _iconPreviewEmboss = False
                            else:
                                _iconPreview       = 'RESTRICT_VIEW_ON'
                                _iconPreviewEmboss = False

                    if len(selectedCam) <=1:
                        row.operator("cameramanager.activpreview_scene_camera",text='', icon=_iconPreview, emboss=_iconPreviewEmboss)
                    elif len(selectedCam) >1 and camera in selectedObj: row.operator("cameramanager.activpreview_scene_camera",text='', icon=_iconPreview)
                    elif len(selectedCam) >1 and camera not in selectedObj:row.operator("cameramanager.activpreview_scene_camera",text='', icon=_iconPreview, emboss=_iconPreviewEmboss)
                    if rs.Manager_ShowSelect == False: row.alert = False

                    #Render button
                    if rs.cmBut_Render == True:
                        if len(selectedCam) <=1:
                            row.operator("cameramanager.render_scene_camera",text='', icon='SEQ_PREVIEW').renderFrom = 'CAMANAGER'
                        #elif len(selectedCam) >1 and camera in selectedObj:row.operator("cameramanager.null_tool", text="", icon='BLANK1',emboss=True).nullMode='SELECT'
                        elif camera not in selectedObj:row.operator("cameramanager.null_tool", text="", icon='SEQ_PREVIEW',emboss=True).nullMode='SELECT'


                    #Camera name          
                    if len(selectedCam) <=1 and camera not in selectedObj: row.prop(camera, "name", text="")
                    elif len(selectedCam) >=1 and camera in selectedObj: row.operator("cameramanager.null_tool", text="{0}".format(camera.name)).nullMode='SELECT'#row.prop(camera, "name", text="",emboss=False)                        
                    else: row.operator("cameramanager.null_tool", text="{0}".format(camera.name),emboss=False).nullMode='SELECT'


                    #Align View button
                    if rs.cmBut_AlignV == True:
                        if len(selectedCam)<=1:
                            row.operator("cameramanager.alignview_scene_camera", text="", icon='VIEW_PERSPECTIVE')
                        #elif len(selectedCam) >1 and camera in selectedObj:row.operator("cameramanager.null_tool", text="", icon='BLANK1',emboss=True).nullMode='SELECT'
                        elif camera not in selectedObj: row.operator("cameramanager.null_tool", text="", icon='VIEW_PERSPECTIVE',emboss=True).nullMode='SELECT'


                    #Align Obj button
                    if rs.cmBut_AlignO == True:
                        if len(selectedCam) <=1 or  camera in selectedCam:
                            row.operator("cameramanager.alignobj_scene_camera", text="", icon='CUBE')
                        else:row.operator("cameramanager.null_tool", text="", icon='CUBE',emboss=True).nullMode='SELECT'

                    #Track To button: Add/Remove
                    if rs.cmBut_Trackto == True:
                        if len(camera.constraints) == 0:
                            #Add TrackTo button
                            if camera in selectedObj or len(selectedCam) <=1:row.operator("cameramanager.trackto_scene_camera", text="", icon='TRACKER')
                            else:row.operator("cameramanager.null_tool", text="", icon='TRACKER',emboss=True).nullMode='SELECT'
                        else :
                            #Remove TrackTo button
                            if camera not in selectedCam and len(selectedCam) <=1:
                                row.operator("cameramanager.removetrackto_scene_camera", text="", icon='CON_FOLLOWTRACK', emboss=False)
                            elif camera in selectedCam and len(selectedCam) >= 1:
                                row.operator("cameramanager.removetrackto_scene_camera", text="", icon='CON_FOLLOWTRACK', emboss=True)
                            elif camera not in selectedCam and len(selectedCam) > 1:
                                row.operator("cameramanager.null_tool", text="", icon='CON_FOLLOWTRACK',emboss=True).nullMode='SELECT'

                    #Marker button
                    if rs.cmBut_Marker == True:
                        if camera in list_marked_cameras :
                            m = 0
                            for i,marker in enumerate(marker_list_camera):
                                if marker_list_camera[i].frame != 0:
                                    if marker.camera == camera and m < 1:#prevent adding button if multiple marker on same camera
                                        #Remove marker button
                                        if camera in selectedCam :#and len(selectedCam) <=1:
                                            row.operator("cameramanager.remove_camera_marker",text='', icon='MARKER_HLT', emboss=True)
                                        elif camera not in selectedCam and len(selectedCam) <=1:
                                            row.operator("cameramanager.remove_camera_marker",text='', icon='MARKER_HLT', emboss=False)
                                        elif camera not in selectedCam and len(selectedCam) > 1:
                                            row.operator("cameramanager.null_tool", text="", icon='MARKER_HLT',emboss=False).nullMode='SELECT'
                                        m += 1
                                elif marker_list_camera[i].frame == 0 and marker.camera == camera:
                                    if camera in selectedObj:
                                        row.operator("cameramanager.null_tool", text="", icon='BLANK1',emboss=False).nullMode='NULL'
                                    elif rs_obj.Custom_CamRender_prop == True and camera not in selectedObj:
                                        row.operator("cameramanager.add_camera_marker",text='', icon='MARKER')
                                    else:
                                        row.operator("cameramanager.add_camera_marker",text='', icon='MARKER')

                        #Add marker button
                        else:
                            if len(selectedCam)<=1:
                                row.operator("cameramanager.add_camera_marker",text='', icon='MARKER')
                            #elif len(list_marked_cameras)>0 and camera in selectedObj:
                            elif camera in selectedObj:
                                row.operator("cameramanager.null_tool", text="", icon='BLANK1',emboss=True).nullMode='SELECT'
                            elif camera not in selectedObj:
                                row.operator("cameramanager.null_tool", text="", icon='MARKER',emboss=True).nullMode='SELECT'


                    #Animation Data
                    if rs.cmBut_AnimData == True:
                        if len(animDataCam) >0:
                            #if bpy.data.cameras[camera.name].animation_data.action != None :
                            if camera in animDataCam:# or bpy.data.cameras[camera.name].animation_data != None :
                                if camera in emptyAnimCam :
                                    if camera in selectedObj and len(selectedCam) <=1:
                                        row.operator("cameramanager.null_tool", text="", icon='KEYFRAME',emboss=True).nullMode='NULL'
                                    elif camera in selectedCam and len(selectedCam) >1:
                                        row.operator("cameramanager.null_tool", text="", icon='KEYFRAME',emboss=True).nullMode='SELECT'
                                    else: row.operator("cameramanager.null_tool", text="", icon='KEYFRAME',emboss=False).nullMode='SELECT'
                                else:
                                    if camera not in selectedObj and len(selectedCam) <=1:
                                        row.operator("cameramanager.null_tool", text="", icon='KEYTYPE_KEYFRAME_VEC',emboss=False).nullMode='NULL'
                                    elif camera not in selectedObj and len(selectedCam) >1:
                                        row.operator("cameramanager.null_tool", text="", icon='KEYFRAME_HLT',emboss=False).nullMode='SELECT'
                                    elif camera in selectedObj or len(selectedCam) >1:
                                        row.operator("cameramanager.null_tool", text="", icon='KEYTYPE_KEYFRAME_VEC',emboss=True).nullMode='NULL'
                                    #else: row.operator("cameramanager.null_tool", text="", icon='KEYFRAME_HLT',emboss=False).nullMode='SELECT'
                            else:
                                if camera in selectedObj:
                                    row.operator("cameramanager.null_tool", text="", icon='BLANK1').nullMode='SELECT'
                                else:row.operator("cameramanager.null_tool", text="", icon='BLANK1',emboss=False).nullMode='SELECT'
                    if len(animDataCam) < 1:row.separator()

                    #Remove camera button
                    if camera not in selectedCam and len(selectedCam) <=1:
                        row.operator("cameramanager.del_scene_camera",text='', icon='PANEL_CLOSE', emboss=False)
                    elif camera in selectedCam and len(selectedCam) >=1:
                        row.operator("cameramanager.del_scene_camera",text='', icon='PANEL_CLOSE', emboss=True)
                    elif camera not in selectedCam and len(selectedCam) >1:
                        row.operator("cameramanager.null_tool", text="", icon='PANEL_CLOSE',emboss=False).nullMode='SELECT'

                    #Render Selection prop
                    if len(cameras) > 2 and rs.switchRenderSelection == True:
                        #row.active = True
                        row.alert = False
                        row.prop(rs_obj,'Custom_CamRender_prop',text='')

    ### ]Cameras List

                layout.separator()
                row = layout.row(align=True)

    ###Buttons below Cameras List[ _____________________________________________________________________________________
                #Render All buttons for batch rendering
                if len(cameras) > 1:
                    #row.prop(rs,'SwitchPropertiesBatch',text='', icon ='PROPERTIES')
                    if rs.switchRenderSelection == False:
                        if len(marker_list_camera) < 1 or len(selectedCam) >1:
                            if len(selectedCam) >1:
                                row.operator("cameramanager.render_all_camera",text='Render Selection: {0}'.format(len(selectedCam)), icon='RENDER_RESULT')
                            else:
                                row.operator("cameramanager.render_all_camera",text='Render All Cameras', icon='RENDER_RESULT')
                        if 1 <= len(marker_list_camera) < len(cameras) and len(selectedCam)<2:
                            row.operator("cameramanager.render_all_camera",text='Render All', icon='RENDER_RESULT')
                            row.operator("cameramanager.render_all_camera",text='Render Markers', icon='RENDER_RESULT').tmarkers = True
                        elif len(marker_list_camera) == len(cameras):
                            if scene.frame_current>0 :
                                row.operator("cameramanager.render_all_camera",text='Render All Cameras', icon='RENDER_RESULT')
                            else:
                                row.operator("cameramanager.render_all_camera",text='Render All', icon='RENDER_RESULT')
                                row.operator("cameramanager.render_all_camera",text='Render Markers', icon='RENDER_RESULT').tmarkers = True
                    else:
                        if len(render_all_list) <2:
                            row.label(text='Choose at least two Cameras', icon ='ERROR')
                        elif 1 < len(render_all_list) < len(cameras) :
                            row.operator("cameramanager.render_all_camera",text='Render Selection: {0}'.format(len(render_all_list)), icon='RENDER_RESULT')
                        elif len(render_all_list) == len(cameras) :
                            row.operator("cameramanager.render_all_camera",text='Render All Cameras', icon='RENDER_RESULT')
                elif len(cameras) > 2:
                    if rs.switchRenderSelection == True:
                        if len(render_all_list) <2:
                            row.label(text='Choose at least two Cameras', icon ='ERROR')

                #Switch button for cameras listing for batch rendering
                if len(cameras) > 2:
                    row.separator()
                    row.prop(rs,"switchRenderSelection",text='', icon='RESTRICT_SELECT_OFF')
    ### ]Buttons below Cameras List

                row = layout.row(align=True)

            else:
                ##
                row = layout.row(align=True)
                row.alignment='CENTER'
                row.alert = True
                row.label(text=" No cameras in this scene", icon ='ERROR')
                row.alert = False

    ###Camera Manager Settings[ _____________________________________________________________________________________
        else:

        ## Manager Options [-----------
            row = layout.row(align=True)
            box = layout.box()
            row = box.row(align=True)
            row.alert = True
            row.alignment='CENTER'

            row.label(text='Manager Options')

            row = box.row(align=True)

            row = row.box()
            row = row.row(align=True)

            row.label(text='Tools Toggles:')

            row.prop(rs,"cmBut_Render",text="",icon='SEQ_PREVIEW')
            row.prop(rs,"cmBut_AlignV",text="",icon='VIEW_PERSPECTIVE')
            row.prop(rs,"cmBut_AlignO",text="",icon='CUBE')
            row.prop(rs,"cmBut_Trackto",text="",icon='TRACKER')
            row.prop(rs,"cmBut_Marker",text="",icon='MARKER')
            row.prop(rs,"cmBut_AnimData",text="",icon='KEYTYPE_KEYFRAME_VEC')

            box.use_property_split = True
            box.use_property_decorate = False
            row = layout.row(align=True)
            row = box.row(align=True)
            row = row.box()
            row.prop(rs,'Manager_ShowSelect_Color',text='Selection Highlight')
        ## ]Manager Options


        ## New Camera Lens Settings [-----------
            row = layout.row(align=True)
            box = layout.box()
            row = box.row(align=True)
            row.alert = True
            row.alignment='CENTER'

            row.label(text='New Camera Lens Settings')

            row = box.row(align=True)

            row = row.box()
            row.label(text='Camera Perspective',icon='VIEW_PERSPECTIVE')

            row.prop(rs,"NewCam_lensPersp")
            row = row.row(align=True)

            row.prop(rs,"NewCam_ClipStart",text="Clip Start")
            row.prop(rs,"NewCam_ClipEnd",text="End")

            row = box.row(align=True)

            row = row.box()
            row.label(text='Camera Orthogaphic',icon='VIEW_ORTHO')
            row.prop(rs,"NewCam_lensOrtho",text="Scale")

            row = row.row(align=True)
            row.prop(rs,"NewCam_ClipStartOrtho",text="Clip Start")
            row.prop(rs,"NewCam_ClipEndOrtho",text="End")
        ## ]New Camera Lens Settings


# CAMERA QUICK SETTINGS ######################################################################################
class CAMMANAGER_PT_QuickSettings(Panel):
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context     = "objectmode"
    bl_category    = "Render"
    bl_label       = "Settings :"
    #bl_options     = {'DEFAULT_CLOSED'}
    bl_idname      = "CAMMANAGER_PT_QuickSettings"
    bl_parent_id   = "CAMMANAGER_PT_Cammanager"

    _selectedCam   = []

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and context.active_object==bpy.context.space_data.camera) and bpy.context.scene.RBTab_Settings.cmOptions == False


    def draw_header_preset(self, context):
        scene   = context.scene
        cameras = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)
        ob      = context.active_object

        selectedObj    = bpy.context.selected_objects
        selectedCam    = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)
        noCustomDimCam = sorted([o for o in cameras if o.RBTab_obj_Settings.Custom_CamRes_prop == False],key=lambda o: o.name)

        layout = self.layout
        row    = layout.row(align=True)

        if len(cameras) > 0 and (ob in cameras):
            if len(selectedCam) == 1 :
                if ob in selectedCam:
                    chosen_camera = context.active_object
                    row.label(text="{0}".format(chosen_camera .name))

            elif len(selectedCam) > 1:
                if ob in selectedCam:
                    row.alert = True
                    chosen_camera = context.active_object
                    row.label(text="[..{0}..]".format(chosen_camera .name))
                else:
                    row.active = False
                    chosen_camera = context.active_object
                    row.label(text="{0}".format(chosen_camera .name))
            else:
                chosen_camera = context.active_object
                row.label(text="{0}".format(chosen_camera .name))


    def draw(self, context):
        scene          = context.scene
        rs             = scene.RBTab_Settings
        ob             = context.active_object
        cs             = ob.RBTab_obj_Settings
        render         = scene.render
        cameras        = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)
        view           = context.space_data
        chosen_camera  = bpy.context.object.data
        cam            = chosen_camera

        selectedObj    = bpy.context.selected_objects
        selectedCam    = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)
        noCustomDimCam = sorted([o for o in cameras if o.RBTab_obj_Settings.Custom_CamRes_prop == False],key=lambda o: o.name)

        selectedCustomDimCam = list(set(selectedCam) - set(noCustomDimCam))
        self._selectedCam    = selectedCam

        layout = self.layout

        if len(cameras) > 0 and (ob in cameras):

            row = layout.row(align=True)

#            if len(selectedCam) > 1 and ob not in selectedCam:
#                row.enabled = False
#                layout.emboss = 'NONE'################

            row.prop(cam, "type", text="")
            row = layout.row(align=True)

            #if len(selectedCam) > 1 and ob not in selectedCam: row.enabled = False ################

            if cam.type == 'PERSP':
                row.prop(cam, "lens", text="Focal")

            elif cam.type == 'ORTHO':
                row.prop(cam, "ortho_scale", text="Scale")

            elif cam.type == 'PANO':
                engine = context.engine
                if engine == 'CYCLES':
                    ccam = cam.cycles
                    row  = box.row()
                    row.prop(ccam, "panorama_type", text="")
                    row  = box.row()

                    if ccam.panorama_type == 'FISHEYE_EQUIDISTANT':
                        row.prop(ccam, "fisheye_fov", text="FOV")

                    elif ccam.panorama_type == 'FISHEYE_EQUISOLID':
                        row.prop(ccam, "fisheye_lens", text="Lens")
                        row.prop(ccam, "fisheye_fov", text="FOV")

                    elif ccam.panorama_type == 'EQUIRECTANGULAR':
                        row = box.row()
                        row.label(text="Latitude:")
                        row = box.row()
                        row.prop(ccam, "latitude_min", text="Min")
                        row.prop(ccam, "latitude_max", text="Max")

                        row = box.row()
                        row.label(text="Longitude:")
                        row = box.row()
                        row.prop(ccam, "longitude_min", text="Min")
                        row.prop(ccam, "longitude_max", text="Max")

                elif engine in {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}:
                    if cam.lens_unit == 'MILLIMETERS':
                        row.prop(cam, "lens")

                    elif cam.lens_unit == 'FOV':
                        row.prop(cam, "angle")

                    row.prop(cam, "lens_unit")

            row = layout.row(align=True)

            #if len(selectedCam) > 1 and ob not in selectedCam: row.enabled = False ################

            row.prop(cam, "shift_x", text="Shift H")
            row.prop(cam, "shift_y", text="V")

            row = layout.row(align=True)

            #if len(selectedCam) > 1 and ob not in selectedCam: row.enabled = False ################

            row.prop(cam, "clip_start", text="Clip Start")
            row.prop(cam, "clip_end", text="End")

            layout.separator()
            row = layout.row(align=True)

            #if len(selectedCam) > 1 and ob not in selectedCam: row.enabled = False ################

            if cs.Custom_CamRes_prop == False:
                row.operator('cameramanager.custom_resolution',text="Save Custom Resolution",icon='FILE_TICK').crrefresh = False

            elif cs.Custom_CamRes_prop == True and (cs.Custom_CamHRes_prop == render.resolution_x) and (cs.Custom_CamVRes_prop == render.resolution_y):
                row.operator('cameramanager.custom_resolution',text="{0} x {1}".format(cs.Custom_CamHRes_prop,cs.Custom_CamVRes_prop), icon='LOCKED')
                row.operator('cameramanager.custom_resolution',text="", icon='PANEL_CLOSE',emboss=False).crdel = True

            elif cs.Custom_CamRes_prop == True and (cs.Custom_CamHRes_prop != render.resolution_x) or (cs.Custom_CamVRes_prop != render.resolution_y):
                row.operator('cameramanager.custom_resolution',text="{0} x {1}".format(cs.Custom_CamHRes_prop,cs.Custom_CamVRes_prop), icon='LOCKED').crrefresh = True
                row.operator('cameramanager.custom_resolution',text="", icon='PANEL_CLOSE',emboss=False).crdel = True




# CAMERA MANAGER FOOTER INFOS ######################################################################################
class CAMMANAGER_PT_InfosCamActiv(Panel):
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context     = "objectmode"
    bl_category    = "Render"
    bl_label       = "Camera Infos"
    bl_idname      = "CAMMANAGER_PT_InfosCamActiv"
    bl_options     = {'HIDE_HEADER'}
    bl_parent_id   = "CAMMANAGER_PT_Cammanager"

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
                and context.active_object==bpy.context.space_data.camera
                and bpy.context.scene.RBTab_Settings.cmOptions == False)

    def draw(self, context):
        scene         = context.scene
        ob            = context.active_object
        cs            = ob.RBTab_obj_Settings
        marker_list   = context.scene.timeline_markers
        chosen_camera = context.active_object
        render        = context.scene.render
        cameras       = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)

        layout = self.layout
        split  = layout.split()

        layout.use_property_split    = True
        layout.use_property_decorate = False

        row         = layout.row(align=True)
        row.scale_y = 0.7

        if (context.active_object is not None):

            if len(cameras) > 0 and (ob in cameras):

                _customDim   = ""
                _trackTo     = ""
                _markerName  = ""
                _markerFrame = ""
                _infos       = ""

                if cs.Custom_CamRes_prop == True: _customDim = "{0}x{1} ".format(cs.Custom_CamHRes_prop,cs.Custom_CamVRes_prop)

                if len(chosen_camera.constraints) > 0 and chosen_camera.constraints[0].target is not None: _trackTo = " [{0}] ".format(chosen_camera.constraints[0].target.name)


                for marker in marker_list:
                    if marker.camera == chosen_camera and scene.frame_current != 0:
                        _markerName  = " <{0}>".format(marker.camera.name)
                        _markerFrame = "({0})".format(marker.frame)

                _infos = _customDim + _trackTo + _markerName + _markerFrame

                if len(chosen_camera.constraints) > 0 and chosen_camera.constraints[0].target is None: _infos ="No Target"

                if _infos != "":
                    if _infos == "No Target":
                        row.alert = True
                        row.label(text = "Track To Error : " + _infos, icon ='ERROR')
                    else: row.label(text = _infos, icon ='INFO')


# RENDER PRESET ######################################################################################
class RENDER_PT_presets(PresetPanel, Panel):
    bl_label            = "Render Presets"
    preset_subdir       = "render"
    preset_operator     = "script.execute_preset"
    preset_add_operator = "render.preset_add"


# RENDER DIMENSIONS SUBPANEL ######################################################################################
class MYBIGBUTTONTAB_PT_RenderDimensions(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "Render"
    bl_label       = "Dimensions"
    bl_options     = {'DEFAULT_CLOSED'}
    bl_idname      = "MYBIGBUTTON_PT_RenderDimensions"
    bl_parent_id   = "MYBIGBUTTONTAB_PT_MyBigButton"

    @classmethod
    def poll(cls, context):
        return bpy.context.scene.RBTab_Settings.mbbOptions == False
        #return context.mode == 'OBJECT'

    def draw_header_preset(self, _context):
        RENDER_PT_presets.draw_panel_header(self.layout)


    def draw(self, context):
        scene  = context.scene
        rd     = scene.render
        rs     = scene.RBTab_Settings

        layout = self.layout
        row    = layout.row(align=True)

        row.prop(scene.render, 'resolution_x', text="H")
        row.operator("render.toggle_orientation", text="", icon='ARROW_LEFTRIGHT')
        row.prop(scene.render, 'resolution_y', text="V")

        if (rd.resolution_x != rs.Default_HRes_prop) or (rd.resolution_y != rs.Default_VRes_prop):
            row.operator("render.store_as_defaultres", text="", icon='FILE_TICK',emboss=False)

        layout.prop(context.scene.render, "resolution_percentage", text="")

        row  = layout.row(align=True)
        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')

        if area.spaces[0].region_3d.view_perspective == 'CAMERA':
            row.active  = True
            row.enabled = True
            row.prop(rd, "use_border", text="Render Region", icon='SHADING_BBOX')
            if rd.use_border == True:
                row.prop(rd, "use_crop_to_border", text="Crop Region", icon='IMAGE_PLANE')
        else:
            row.active  = False
            row.enabled = False
            row.prop(rd, "use_border", text="Render Region", icon='SHADING_BBOX')
            if rd.use_border == True:
                row.prop(rd, "use_crop_to_border", text="Crop Region", icon='IMAGE_PLANE')


# visual alarm ######################################################################################
class MYBIGBUTTONTAB_PT_VisualAlarm(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "Render"
    bl_label       = "ALARME - ESC to Abort"
    bl_options     = {'HIDE_HEADER'}
    bl_idname      = "MYBIGBUTTONTAB_PT_VisualAlarm"


    @classmethod
    def poll(cls, context):
        return bpy.context.scene.RBTab_Settings.alarmInProgress == True

    def draw(self, context):

        scene = context.scene
        rd    = scene.render
        rs    = scene.RBTab_Settings

        visualAlarm(self, context)


# visual alarm ######################################################################################
class IMAGE_PT_VisualAlarm(Panel):
    bl_space_type  = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category    = "Tool"
    bl_label       = "ALARME - ESC to Abort"
    bl_options     = {'HIDE_HEADER'}
    bl_idname      = "IMAGE_PT_VisualAlarm"


    @classmethod
    def poll(cls, context):
        return bpy.context.scene.RBTab_Settings.alarmInProgress == True

    def draw(self, context):
        scene = context.scene
        rd    = scene.render
        rs    = scene.RBTab_Settings

        visualAlarm(self, context)



 # visual alarm ######################################################################################
class PROPERTIES_PT_VisualAlarm(Panel):
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    #bl_category = "Alarm"
    bl_label       = "ALARME - ESC to Abort"
    bl_options     = {'HIDE_HEADER'}
    bl_idname      = "PROPERTIES_PT_VisualAlarm"


    @classmethod
    def poll(cls, context):
        return bpy.context.scene.RBTab_Settings.alarmInProgress == True

    def draw(self, context):
        scene = context.scene
        rd    = scene.render
        rs    = scene.RBTab_Settings

        visualAlarm(self, context)


#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
classes = (MYBIGBUTTON_Settings,
            MYBIGBUTTON_obj_Settings,

            SCENECAMERA_OT_Add,
            SCENECAMERA_OT_ActivPreview,
            SCENECAMERA_OT_AlignView,
            SCENECAMERA_OT_AlignObj,
            SCENECAMERA_OT_AddTrackTo,
            SCENECAMERA_OT_RemoveTrackTo,
            SCENECAMERA_OT_AddMarker,
            SCENECAMERA_OT_removeMarker,
            SCENECAMERA_OT_Remove,
            SCENECAMERA_OT_RenderAnimation,
            SCENECAMERA_OT_BatchRenderAll,
            SCENECAMERA_OT_Render,

            RENDER_OT_Renderformat,
            RENDEREVENTS_OT_endEvents,

            SCENECAMERA_OT_CustomResolution,
            SCENECAMERA_OT_Null,

            SCENECAMERA_OT_SelectCamera,
            SCENECAMERA_OT_CamTools,

            SCENECAMERA_MT_SelectMenu,
            SCENECAMERA_MT_ToolsMenu,


            MYBIGBUTTON_PT_MyBigButton,
            MYBIGBUTTONTAB_OT_toggle_orientation,
            MYBIGBUTTONTAB_OT_store_defaultres,
            MYBIGBUTTONTAB_PT_MyBigButton,
            MYBIGBUTTONTAB_PT_RenderDimensions,

            MYBIGBUTTONTAB_PT_VisualAlarm,
            IMAGE_PT_VisualAlarm,
            PROPERTIES_PT_VisualAlarm,

            CAMMANAGER_PT_Cammanager,
            CAMMANAGER_PT_QuickSettings,
            CAMMANAGER_PT_InfosCamActiv,
            RENDER_PT_presets,

            )

addon_keymaps = []

def register():
    for i in classes:
        register_class(i)

    Scene.RBTab_Settings = PointerProperty(type=MYBIGBUTTON_Settings)
    Object.RBTab_obj_Settings = PointerProperty(type=MYBIGBUTTON_obj_Settings)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is not None:
        km = kc.keymaps.new(name="Object Mode")
        kmi = km.keymap_items.new(SCENECAMERA_OT_Add.bl_idname, "C", "PRESS", alt=True)
        addon_keymaps.append((km, kmi))


def unregister():
    for i in classes:
        unregister_class(i)

    del Scene.RBTab_Settings
    del Object.RBTab_obj_Settings

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is not None:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)

    addon_keymaps.clear()

if __name__ == "__main__":
    try:
        unregister()
    except:
        pass
    register()
