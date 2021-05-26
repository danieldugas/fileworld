"""
awsd - movement
space - jump
mouse - look around
"""
import numpy as np

import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.gui.OnscreenText import OnscreenText
import sys

floorraise = 0.01 # step every smaller scene up by a tiny amount to make floors separate
scale_level_of_1m_world = 3

def scene_scale_from_scale_level(scale_level):
    """ 0: 1000, 1: 100, 2: 10, 3: 1, 4: 0.1, ... """
    return np.power(0.1, scale_level-scale_level_of_1m_world)

def floorz_from_scale_level(scale_level):
    if scale_level < 0:
        return 0
    else:
        scene_scale = scene_scale_from_scale_level(scale_level)
        return floorz_from_scale_level(scale_level - 1) + scale_level * floorraise * scene_scale

class FPS(object):
    """
        This is a very simple FPS like -
         a building block of any game i guess
    """
    def __init__(self):
        """ create a FPS type game """
        self.initCollision()
        self.loadLevel()
        self.initPlayer()
        base.accept( "escape" , sys.exit)
        base.accept( "arrow_up" , self.scalePlayerUp)
        base.accept( "arrow_down" , self.scalePlayerDown)
        base.disableMouse()

        # hide mouse cursor, comment these 3 lines to see the cursor
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)

        self.scaletext = OnscreenText(text="Fileworld", style=1, fg=(1,1,1,1),
                    pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)
        OnscreenText(text=__doc__, style=1, fg=(1,1,1,1),
            pos=(-1.3, 0.95), align=TextNode.ALeft, scale = .05)

    def initCollision(self):
        """ create the collision system """
        base.cTrav = CollisionTraverser()
        base.pusher = CollisionHandlerPusher()

    def loadLevel(self):
        """ load the self.level
            must have
            <Group> *something* {
              <Collide> { Polyset keep descend }
            in the egg file
        """
        self.scenes = [None for i in range(20)]

        # Bigger scenes
        for i in range(1, 4):
            scale_level = scale_level_of_1m_world - i
            if scale_level < 0:
                continue
            scene_scale = scene_scale_from_scale_level(scale_level)
            self.scenes[scale_level] = loader.loadModel('house.bam')
            self.scenes[scale_level].reparentTo(render)
            self.scenes[scale_level].setTwoSided(True)
            self.scenes[scale_level].setScale(scene_scale, scene_scale, scene_scale)
            self.scenes[scale_level].setPos(0, 0, floorz_from_scale_level(scale_level))

        # 1m scene
        scale_level = scale_level_of_1m_world
        scene_scale = scene_scale_from_scale_level(scale_level)
        self.scenes[scale_level] = loader.loadModel('house.bam')
        self.scenes[scale_level].reparentTo(render)
        self.scenes[scale_level].setTwoSided(True)
        self.scenes[scale_level].setScale(scene_scale, scene_scale, scene_scale)
        self.scenes[scale_level].setPos(0, 0, floorz_from_scale_level(scale_level))

        # Smaller scenes
        for i in range(1, 4):
            scale_level = scale_level_of_1m_world + i
            scene_scale = scene_scale_from_scale_level(scale_level)
            self.scenes[scale_level] = loader.loadModel('house.bam')
            self.scenes[scale_level].reparentTo(render)
            self.scenes[scale_level].setTwoSided(True)
            self.scenes[scale_level].setScale(scene_scale, scene_scale, scene_scale)
            self.scenes[scale_level].setPos(0, 0, floorz_from_scale_level(scale_level))


        ambientLight = AmbientLight('ambientLight')
        ambientLight.setColor((0.3, 0.3, 0.3, 1))
        ambientLightNP = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNP)
        render.set_shader_auto()

        # light
        ambientLight = AmbientLight('ambientLight')
        ambientLight.setColor((0.3, 0.3, 0.3, 1))
        ambientLightNP = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNP)
        render.set_shader_auto()

    def initPlayer(self):
        """ loads the player and creates all the controls for him"""
        self.player = Player()

    def getCurrentRoomDepth(self):
        return len(self.current_folder)

    def getPlayerScale(self):
        depth = self.getCurrentRoomDepth()
        # player shrinks to one tenth of their size with every level
        scale = np.power(0.1, depth)
        return scale

    def getPlayerSpeed(self):
        return self.base_player_speed * self.getPlayerScale()

    def scalePlayerUp(self):
        self.player.scale_level -= 1
        self.player.speed = self.player.speed * 10.
        self.player.height = self.player.height * 10.
        self.player.node.setZ(self.player.node.getZ() + self.player.height)
        self.player.gravity = self.player.gravity * 10.
        self.player.initialjumpvel = self.player.initialjumpvel * 10.
        self.player.terminalzvel = self.player.terminalzvel * 10.
        self.player.lensneardist = self.player.lensneardist * 10.
        pl =  base.cam.node().getLens()
        pl.setFov(70)
        pl.setNear(self.player.lensneardist)
        base.cam.node().setLens(pl)

        self.scaletext.setText("Scale level: {}".format(self.player.scale_level))

    def scalePlayerDown(self):
        self.player.scale_level += 1
        self.player.speed = self.player.speed / 10.
        self.player.height = self.player.height / 10.
        self.player.gravity = self.player.gravity / 10.
        self.player.node.setZ(self.player.node.getZ() - self.player.height * 8)
        self.player.initialjumpvel = self.player.initialjumpvel / 10.
        self.player.terminalzvel = self.player.terminalzvel / 10.
        self.player.lensneardist = self.player.lensneardist / 10.
        pl =  base.cam.node().getLens()
        pl.setFov(70)
        pl.setNear(self.player.lensneardist)
        base.cam.node().setLens(pl)

        self.scaletext.setText("Scale level: {}".format(self.player.scale_level))


class Player(object):
    """
        Player is the main actor in the fps game
    """
    scale_level = scale_level_of_1m_world
    speed = 50
    height = 1.8
    initialjumpvel = 5
    FORWARD = Vec3(0,2,0)
    BACK = Vec3(0,-1,0)
    LEFT = Vec3(-1,0,0)
    RIGHT = Vec3(1,0,0)
    STOP = Vec3(0)
    walk = STOP
    strafe = STOP
    readyToJump = False
    zvel = 0
    terminalzvel = -10
    gravity = -10
    lensneardist = 1

    def __init__(self):
        """ inits the player """
        self.loadModel()
        self.setUpCamera()
        self.createCollisions()
        self.attachControls()
        # init mouse update task
        taskMgr.add(self.mouseUpdate, 'mouse-task')
        taskMgr.add(self.moveUpdate, 'move-task')
        taskMgr.add(self.jumpUpdate, 'jump-task')

    def loadModel(self):
        """ make the nodepath for player """
        self.node = NodePath('player')
        self.node.reparentTo(render)
        self.node.setPos(0,0,5)
        self.node.setScale(.05)

    def setUpCamera(self):
        """ puts camera at the players node """
        pl =  base.cam.node().getLens()
        pl.setFov(70)
        base.cam.node().setLens(pl)
        base.camera.reparentTo(self.node)

    def createCollisions(self):
        """ create a collision solid and ray for the player """
        cn = CollisionNode('player')
#         cn.addSolid(CollisionSphere(0,0,0,3))
        solid = self.node.attachNewNode(cn)
        base.cTrav.addCollider(solid,base.pusher)
        base.pusher.addCollider(solid,self.node, base.drive.node())
        # init players floor collisions
        ray = CollisionRay()
        ray.setOrigin(0,0,0)
        ray.setDirection(0,0,-1)
        cn = CollisionNode('playerRay')
        cn.addSolid(ray)
        cn.setFromCollideMask(BitMask32.bit(0))
        cn.setIntoCollideMask(BitMask32.allOff())
        solid = self.node.attachNewNode(cn)
        self.nodeGroundHandler = CollisionHandlerQueue()
        base.cTrav.addCollider(solid, self.nodeGroundHandler)

    def attachControls(self):
        """ attach key events """
        base.accept( "space" , self.__setattr__,["readyToJump",True])
        base.accept( "space-up" , self.__setattr__,["readyToJump",False])
        base.accept( "s" , self.__setattr__,["walk",self.STOP] )
        base.accept( "w" , self.__setattr__,["walk",self.FORWARD])
        base.accept( "s" , self.__setattr__,["walk",self.BACK] )
        base.accept( "s-up" , self.__setattr__,["walk",self.STOP] )
        base.accept( "w-up" , self.__setattr__,["walk",self.STOP] )
        base.accept( "a" , self.__setattr__,["strafe",self.LEFT])
        base.accept( "d" , self.__setattr__,["strafe",self.RIGHT] )
        base.accept( "a-up" , self.__setattr__,["strafe",self.STOP] )
        base.accept( "d-up" , self.__setattr__,["strafe",self.STOP] )

    def mouseUpdate(self,task):
        """ this task updates the mouse """
        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if base.win.movePointer(0, base.win.getXSize()//2, base.win.getYSize()//2):
            self.node.setH(self.node.getH() -  (x - base.win.getXSize()//2)*0.1)
            base.camera.setP(base.camera.getP() - (y - base.win.getYSize()//2)*0.1)
        return task.cont

    def moveUpdate(self,task):
        """ this task makes the player move """
        # move where the keys set it
        self.node.setPos(self.node,self.walk*globalClock.getDt()*self.speed)
        self.node.setPos(self.node,self.strafe*globalClock.getDt()*self.speed)
        return task.cont

    def jumpUpdate(self,task):
        """ this task simulates gravity and makes the player jump """
        # get the highest Z from the down casting ray
        floorZ = -100
        for i in range(self.nodeGroundHandler.getNumEntries()):
            entry = self.nodeGroundHandler.getEntry(i)
            z = entry.getSurfacePoint(render).getZ()
            if z > floorZ and entry.getIntoNode().getName() != "player":
                floorZ = z
        floorZ = floorz_from_scale_level(self.scale_level)  # don't know why the regular floor method doesn't work
        floorPadding = self.height * 0.1
        feetZ = self.node.getZ() - self.height
        # feet above padded ground (floating)
        if floorZ + floorPadding < feetZ:
            # apply gravity
            if self.zvel > self.terminalzvel:
                self.zvel = self.zvel + self.gravity * globalClock.getDt()
        # feet below ground -> 
        if floorZ > feetZ:
            self.zvel = 0
            self.node.setZ(floorZ+self.height)
        # feet below paddedground
        if floorZ + floorPadding > feetZ:
            # enable jump again
            if self.readyToJump:
#                 self.node.setZ(floorZ+floorPadding)
                self.zvel = self.initialjumpvel
        print("{:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}".format(
            self.node.getZ(), self.height, feetZ, floorZ, self.zvel))
        # apply velocity
        self.node.setZ(self.node.getZ()+self.zvel*globalClock.getDt())
        return task.cont

FPS()
run()
