"""
awsd - movement
space - jump
mouse - look around
"""
import numpy as np
import os

import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.gui.OnscreenText import OnscreenText
import sys

floorraise = 0.01 # step every smaller scene up by a tiny amount to make floors separate
x_separation = 50
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
        self.current_folder = ['/', 'home', 'daniel']
        self.init_collision()
        self.load_level()
        self.init_player()
        base.accept( "escape" , sys.exit)
        base.accept( "arrow_up" , self.scale_player_up)
        base.accept( "arrow_down" , self.scale_player_down)
        base.disableMouse()

        # hide mouse cursor, comment these 3 lines to see the cursor
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)

        self.scaletext = OnscreenText(text="Fileworld", style=1, fg=(1,1,1,1),
                    pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)
        OnscreenText(text=__doc__, style=1, fg=(1,1,1,1),
            pos=(-1.3, 0.95), align=TextNode.ALeft, scale = .05)

    def init_collision(self):
        """ create the collision system """
        base.cTrav = CollisionTraverser()
        base.pusher = CollisionHandlerPusher()

    def load_level(self):
        """ load the self.level
            must have
            <Group> *something* {
              <Collide> { Polyset keep descend }
            in the egg file
        """
        self.scenes = [None for i in range(20)]


        self.parent_scale = 10.
        self.siblings_scale = 1.
        self.children_scale = 0.1

        # parent room scene, larger
        c = self.current_folder[-2]
        scale = self.parent_scale
        z_offset = - floorraise
        self.parent_room_scene = loader.loadModel('house.bam')
        self.parent_room_scene.reparentTo(render)
        self.parent_room_scene.setTwoSided(True)
        self.parent_room_scene.setScale(scale, scale, scale)
        self.parent_room_scene.setPos(0, 0, z_offset)
        text = TextNode(c)
        text.setText(c)
        text3d = NodePath(text)
        text3d.reparentTo(self.parent_room_scene)
        text3d.setScale(-1,1,1)
        text3d.setPos(0,11,5)
        text3d.setTwoSided(True)

        # sibling room scenes (children of parent)
        # current room is one of those (I am the child of my parents)

        parentdir = '/'.join(self.current_folder[:-1])
        siblingdirs = [f.name for f in os.scandir(parentdir) if f.is_dir()]
        siblings = siblingdirs[:3]
        if len(siblings) >= 2 and self.current_folder[-1] not in siblings:
            siblings[1] = self.current_folder[-1]
        self.siblings_room_scenes = {c: None for c in siblings}
        for i, c in enumerate(siblings):
            scale = self.siblings_scale
            z_offset = 0
            x_separation_index = i - len(siblings) // 2
            self.siblings_room_scenes[c] = loader.loadModel('house.bam')
            self.siblings_room_scenes[c].reparentTo(render)
            self.siblings_room_scenes[c].setTwoSided(True)
            self.siblings_room_scenes[c].setScale(scale, scale, scale)
            self.siblings_room_scenes[c].setPos(scale * x_separation* x_separation_index, 0, z_offset)
            text = TextNode(c)
            text.setText(c)
            text3d = NodePath(text)
            text3d.reparentTo(self.siblings_room_scenes[c])
            text3d.setScale(-1,1,1)
            text3d.setPos(0,11,5)
            text3d.setTwoSided(True)

        # child room scenes, smaller
        currentdir = '/'.join(self.current_folder)
        childrendir = [f.name for f in os.scandir(currentdir) if f.is_dir()]
        children = childrendir[:3]
        self.children_room_scenes = {c: None for c in children}
        for i, c in enumerate(children):
            scale = self.children_scale
            z_offset = + floorraise
            x_separation_index = i - len(children) // 2
            self.children_room_scenes[c] = loader.loadModel('house.bam')
            self.children_room_scenes[c].reparentTo(render)
            self.children_room_scenes[c].setTwoSided(True)
            self.children_room_scenes[c].setScale(scale, scale, scale)
            self.children_room_scenes[c].setPos(scale * x_separation* x_separation_index, 0, z_offset)
            text = TextNode(c)
            text.setText(c)
            text3d = NodePath(text)
            text3d.reparentTo(self.children_room_scenes[c])
            text3d.setScale(-1,1,1)
            text3d.setPos(0,11,5)
            text3d.setTwoSided(True)


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

    def init_player(self):
        """ loads the player and creates all the controls for him"""
        self.player = Player()

    def get_current_room_depth(self):
        return len(self.current_folder)

    def scale_player_down(self):
        current_room_name = self.current_folder[-1]
        if len(list(self.children_room_scenes.keys())) >= 2:
            children_enter_index = list(self.children_room_scenes.keys())[1]
        else:
            children_enter_index = list(self.children_room_scenes.keys())[0]
        scale_anim = np.linspace(1., 10., 10)
        player_pos = self.player.node.getPos()
        for s in scale_anim:
            # parents become grandparents (later disappear)
            self.parent_room_scene.setScale(self.parent_scale * s, self.parent_scale * s, self.parent_scale * s)
            # siblings become parents
            for i, scene in enumerate(self.siblings_room_scenes.values()):
                z_offset = -floorraise
                x_separation_index = i - len(self.siblings_room_scenes.values()) // 2
                scene.setScale(self.siblings_scale * s, self.siblings_scale * s, self.siblings_scale * s)
                scene.setPos(self.siblings_scale * s * x_separation * x_separation_index, 0, z_offset)
            # children become siblings
            for i, scene in enumerate(self.children_room_scenes.values()):
                z_offset = 0
                x_separation_index = i - len(self.children_room_scenes.values()) // 2
                scene.setScale(self.children_scale * s, self.children_scale * s, self.children_scale * s)
                scene.setPos(self.children_scale * s * x_separation * x_separation_index, 0, z_offset)
            # scale player position in world
            self.player.node.setPos(player_pos * s)
            import time
            time.sleep(0.1)

        # delete parent room scene
        self.parent_room_scene.removeNode()
        # delete siblings that are now parents
        for c, v in self.siblings_room_scenes.items():
            v.removeNode()

        # create parent
        c = current_room_name
        z_offset = - floorraise
        self.parent_room_scene = loader.loadModel('house.bam')
        self.parent_room_scene.reparentTo(render)
        self.parent_room_scene.setTwoSided(True)
        self.parent_room_scene.setScale(self.parent_scale, self.parent_scale, self.parent_scale)
        self.parent_room_scene.setPos(0, 0, z_offset)
        text = TextNode(c)
        text.setText(c)
        text3d = NodePath(text)
        text3d.reparentTo(self.parent_room_scene)
        text3d.setScale(-1,1,1)
        text3d.setPos(0,11,5)
        text3d.setTwoSided(True)

        # siblings are parents
        self.siblings_room_scenes = self.children_room_scenes
        self.current_folder.append(children_enter_index)

        currentdir = '/'.join(self.current_folder)
        childrendir = [f.name for f in os.scandir(currentdir) if f.is_dir()]
        children = childrendir[:3]
        self.children_room_scenes = {c: None for c in children}
        for i, c in enumerate(children):
            scale = self.children_scale
            z_offset = + floorraise
            x_separation_index = i - len(children) // 2
            self.children_room_scenes[c] = loader.loadModel('house.bam')
            self.children_room_scenes[c].reparentTo(render)
            self.children_room_scenes[c].setTwoSided(True)
            self.children_room_scenes[c].setScale(scale, scale, scale)
            self.children_room_scenes[c].setPos(self.children_scale * x_separation* x_separation_index, 0, z_offset)
            text = TextNode(c)
            text.setText(c)
            text3d = NodePath(text)
            text3d.reparentTo(self.children_room_scenes[c])
            text3d.setScale(-1,1,1)
            text3d.setPos(0,11,5)
            text3d.setTwoSided(True)


        self.scaletext.setText('/'.join(self.current_folder)[1:])

    def scale_player_up(self):
        if len(self.current_folder) == 1:
            return
        current_room_name = self.current_folder[-1]
        parent_room_name = self.current_folder[-2]
        if len(self.current_folder) == 2:
            grandparent_room_name = None
            grandparentdir = None
        else:
            grandparent_room_name = self.current_folder[-3]
            grandparentdir = '/'.join(self.current_folder[:-2])
        scale_anim = np.linspace(1., 0.1, 10)
        player_pos = self.player.node.getPos()
        for s in scale_anim:
            # parents shrink to one of siblings (later add siblings)
            self.parent_room_scene.setScale(self.parent_scale * s, self.parent_scale * s, self.parent_scale * s)
            # siblings shrink to children
            for i, scene in enumerate(self.siblings_room_scenes.values()):
                z_offset = +floorraise
                x_separation_index = i - len(self.siblings_room_scenes.values()) // 2
                scene.setScale(self.siblings_scale * s, self.siblings_scale * s, self.siblings_scale * s)
                scene.setPos(self.siblings_scale * s * x_separation * x_separation_index, 0, z_offset)
            # children shrink to grandchildren
            for i, scene in enumerate(self.children_room_scenes.values()):
                z_offset = 0
                x_separation_index = i - len(self.children_room_scenes.values()) // 2
                scene.setScale(self.children_scale * s, self.children_scale * s, self.children_scale * s)
                scene.setPos(self.children_scale * s * x_separation * x_separation_index, 0, z_offset)
            # scale player position in world
            self.player.node.setPos(player_pos * s)
            import time
            time.sleep(0.1)

        # TODO delete children which are now grandchildren
        for c, v in self.children_room_scenes.items():
            v.removeNode()
        # TODO delete parent which is now duplicate sibling
        self.parent_room_scene.removeNode()

        # TODO create parent
        if grandparent_room_name is None:
            # can't create parent, as there is nothing above '/'
            z_offset = - floorraise
            self.parent_room_scene = loader.loadModel('models/environment')
            self.parent_room_scene.reparentTo(render)
            self.parent_room_scene.setTwoSided(True)
            self.parent_room_scene.setScale(self.parent_scale, self.parent_scale, self.parent_scale)
            self.parent_room_scene.setPos(0, 0, z_offset - 1)
        else:
            c = grandparent_room_name
            z_offset = - floorraise
            self.parent_room_scene = loader.loadModel('house.bam')
            self.parent_room_scene.reparentTo(render)
            self.parent_room_scene.setTwoSided(True)
            self.parent_room_scene.setScale(self.parent_scale, self.parent_scale, self.parent_scale)
            self.parent_room_scene.setPos(0, 0, z_offset)
            text = TextNode(c)
            text.setText(c)
            text3d = NodePath(text)
            text3d.reparentTo(self.parent_room_scene)
            text3d.setScale(-1,1,1)
            text3d.setPos(0,11,5)
            text3d.setTwoSided(True)

        self.children_room_scenes = self.siblings_room_scenes
        self.current_folder.pop(-1)

        # create missing siblings
        if grandparentdir is None:
            siblings = [parent_room_name]
        else:
            siblingdirs = [f.name for f in os.scandir(grandparentdir) if f.is_dir()]
            siblings = siblingdirs[:3]
            if len(siblings) >= 2 and parent_room_name not in siblings:
                siblings[1] = parent_room_name
        self.siblings_room_scenes = {c: None for c in siblings}
        for i, c in enumerate(siblings):
            scale = self.siblings_scale
            z_offset = 0
            x_separation_index = i - len(siblings) // 2
            self.siblings_room_scenes[c] = loader.loadModel('house.bam')
            self.siblings_room_scenes[c].reparentTo(render)
            self.siblings_room_scenes[c].setTwoSided(True)
            self.siblings_room_scenes[c].setScale(scale, scale, scale)
            self.siblings_room_scenes[c].setPos(scale * x_separation* x_separation_index, 0, z_offset)
            text = TextNode(c)
            text.setText(c)
            text3d = NodePath(text)
            text3d.reparentTo(self.siblings_room_scenes[c])
            text3d.setScale(-1,1,1)
            text3d.setPos(0,11,5)
            text3d.setTwoSided(True)

        self.scaletext.setText('/'.join(self.current_folder)[1:])


class Player(object):
    """
        Player is the main actor in the fps game
    """
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
    boost = 1
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
        self.node.setPos(0,5,5)
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
        base.accept( "lshift-up" , self.__setattr__,["boost",1] )
        base.accept( "lshift" , self.__setattr__,["boost",2] )

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
        self.node.setPos(self.node,self.walk*globalClock.getDt()*self.speed*self.boost)
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
        floorZ = 0
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
