from math import pi, sin, cos
import sys
import numpy as np

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3, AmbientLight

from pandac.PandaModules import WindowProperties, CompassEffect
# import direct.directbase.DirectStart
# from direct.task import Task

default_base_player_speed = 1 # the subjective speed from the player

class MyApp(ShowBase):
    def __init__(self):

        self.current_folder = ["home", "daniel"]

        self.god_mode = True # DEBUG
        self.base_player_speed = default_base_player_speed

        ShowBase.__init__(self)

        self.disableMouse()

        # hide mouse cursor, comment these 3 lines to see the cursor
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)

        # dummy node for camera, attach player to it
        self.camparent = self.render.attachNewNode('camparent')
        self.camparent.reparentTo(self.render) # inherit transforms
        self.camparent.setEffect(CompassEffect.make(self.render)) # NOT inherit rotation

        # the camera
        self.camera.reparentTo(self.camparent)
        self.camera.lookAt(self.camparent)
        self.camera.setY(0) # camera distance from model

        # vars for camera rotation
        self.cam_heading = 0
        self.cam_pitch = 0


        self.taskMgr.add(self.cameraTask, 'cameraTask')

        # movement
        self.forward_flag = False
        self.reverse_flag = False
        self.left_flag = False
        self.right_flag = False

        def forward():
            self.forward_flag = True

        def stopForward():
            self.forward_flag = False

        def reverse():
            self.reverse_flag = True

        def stopReverse():
            self.reverse_flag = False

        def left():
            self.left_flag = True

        def stopLeft():
            self.left_flag = False

        def right():
            self.right_flag = True

        def stopRight():
            self.right_flag = False

        def boost():
            self.base_player_speed *= 10

        def unboost():
            self.base_player_speed *= 0.1

        self.accept("mouse3", forward)
        self.accept("mouse3-up", forward)
        self.accept("w", forward)
        self.accept("w-up", stopForward)
        self.accept("s", reverse)
        self.accept("s-up", stopReverse)
        self.accept("a", left)
        self.accept("a-up", stopLeft)
        self.accept("d", right)
        self.accept("d-up", stopRight)
        self.accept("escape", sys.exit)
        self.accept("lshift", boost)
        self.accept("lcontrol", unboost)

        # Disable the camera trackball controls.
#         self.disableMouse()
#         self.useDrive()

        # Load the environment model.
        self.scene = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)

        self.scene2 = self.loader.loadModel("/home/daniel/Code/fileworld/house.bam")
        # Reparent the model to render.
        self.scene2.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.scene2.setScale(1., 1., 1.)
        self.scene2.setPos(0, 0, 0)
        ambientLight = AmbientLight('ambientLight')
        ambientLight.setColor((0.3, 0.3, 0.3, 1))
        ambientLightNP = self.render.attachNewNode(ambientLight)
        self.render.setLight(ambientLightNP)
        self.render.set_shader_auto()

        # Add the spinCameraTask procedure to the task manager.
#         self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

        # Load and transform the panda actor.
        self.pandaActor = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})
        self.pandaActor.setScale(0.005, 0.005, 0.005)
        self.pandaActor.reparentTo(self.render)
        # Loop its animation.
        self.pandaActor.loop("walk")

        # Create the four lerp intervals needed for the panda to
        # walk back and forth.
        posInterval1 = self.pandaActor.posInterval(13,
                                                   Point3(0, -10, 0),
                                                   startPos=Point3(0, 10, 0))
        posInterval2 = self.pandaActor.posInterval(13,
                                                   Point3(0, 10, 0),
                                                   startPos=Point3(0, -10, 0))
        hprInterval1 = self.pandaActor.hprInterval(3,
                                                   Point3(180, 0, 0),
                                                   startHpr=Point3(0, 0, 0))
        hprInterval2 = self.pandaActor.hprInterval(3,
                                                   Point3(0, 0, 0),
                                                   startHpr=Point3(180, 0, 0))

        # Create and play the sequence that coordinates the intervals.
        self.pandaPace = Sequence(posInterval1, hprInterval1,
                                  posInterval2, hprInterval2,
                                  name="pandaPace")
        self.pandaPace.loop()

    def getCurrentRoomDepth(self):
        return len(self.current_folder)

    def getPlayerScale(self):
        depth = self.getCurrentRoomDepth()
        # player shrinks to one tenth of their size with every level
        scale = np.power(0.1, depth)
        return scale

    def getPlayerSpeed(self):
        return self.base_player_speed * self.getPlayerScale()

    # camera rotation task
    def cameraTask(self, task):
        md = self.win.getPointer(0)
        speed = self.getPlayerSpeed()

        x = md.getX()
        y = md.getY()

        if self.win.movePointer(0, 300, 300):
            self.cam_heading = self.cam_heading - (x - 300) * 0.2
            self.cam_pitch = self.cam_pitch - (y - 300) * 0.2

        self.camparent.setHpr(self.cam_heading, self.cam_pitch, 0)

        if self.forward_flag == True:
            self.camparent.setY(self.cam, self.camparent.getY(self.cam) + speed)
        if self.reverse_flag == True:
            self.camparent.setY(self.cam, self.camparent.getY(self.cam) - speed)
        if self.left_flag == True:
            self.camparent.setX(self.cam, self.camparent.getX(self.cam) - speed)
        if self.right_flag == True:
            self.camparent.setX(self.cam, self.camparent.getX(self.cam) + speed)

        return task.cont

app = MyApp()
app.run()
