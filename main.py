import pygame as pg
import OpenGL.GL as gl
import numpy as np
import ctypes
import OpenGL.GL.shaders as gls
import pyrr

class Cube:
    
    def __init__(self, position, eulers):
        
        # Eulers - pitch, roll, yaw
        self.eulers = np.array(eulers, dtype=np.float32)
        self.position = np.array(position, dtype=np.float32)


class Player:

    def __init__(self, position):

        self.position = np.array(position, dtype = np.float32)
        self.theta = 0
        self.phi = 0
        self.update_vectors()
    
    def update_vectors(self):

        self.forwards = np.array(
            [
                np.cos(np.deg2rad(self.theta)) * np.cos(np.deg2rad(self.phi)),
                np.sin(np.deg2rad(self.phi)),
                np.sin(np.deg2rad(self.theta)) * np.cos(np.deg2rad(self.phi))
            ],
            dtype = np.float32
        )

        global_up = np.array([0, 1, 0], dtype=np.float32)

        self.right = np.cross(self.forwards, global_up)

        self.up = np.cross(self.right, self.forwards)


class Scene:

    def __init__(self):

        self.cubes = [
            Cube(
                position = [6, 0, 0],
                eulers = [0, 0, 0]
            ),
        ]

        self.player = Player(
            position = [0, 2, 0]
        )

    def update(self, rate):

        for cube in self.cubes:
            cube.eulers[1] += 0.25 * rate
            if cube.eulers[1] > 360:
                cube.eulers[1] -= 360

    def move_player(self, d_pos):

        d_pos = np.array(d_pos, dtype = np.float32)
        self.player.position += d_pos
    
    def spin_player(self, d_theta, d_phi):

        self.player.theta += d_theta
        if self.player.theta > 360:
            self.player.theta -= 360
        elif self.player.theta < 0:
            self.player.theta += 360
        
        self.player.phi = min(
            89, max(-89, self.player.phi + d_phi)
        )
        
        self.player.update_vectors()


class App:
    
    def __init__(self, screen_width, screen_height):
        
        # Set variables
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.renderer = GraphicsEngine(screen_width, screen_height)
        
        self.scene = Scene()
        
        self.last_time = pg.time.get_ticks()
        self.current_time = 0
        self.num_frames = 0
        self.frame_time = 0
        
        self.main_loop()
    
    def main_loop(self):
        
        running = True
        while running:
            # Check events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False
            
            self.handle_keys()
            self.handle_mouse()
            
            self.scene.update(self.frame_time * 0.05)
            self.renderer.render(self.scene)
            
            # Timing
            self.calculate_framerate()
            
        self.quit()
    
    def handle_keys(self):

        keys = pg.key.get_pressed()
        combo = 0
        direction_modifier = 0
        
        d_pos = [0, 0, 0]
        
        up = 0
        down = 0
        
        """
        w: 1 -> 0 degrees
        a: 2 -> 90 degrees
        w & a: 3 -> 45 degrees
        s: 4 -> 180 degrees
        w & s: 5 -> x
        a & s: 6 -> 135 degrees
        w & a & s: 7 -> 90 degrees
        d: 8 -> 270 degrees
        w & d: 9 -> 315 degrees
        a & d: 10 -> x
        w & a & d: 11 -> 0 degrees
        s & d: 12 -> 225 degrees
        w & s & d: 13 -> 270 degrees
        a & s & d: 14 -> 180 degrees
        w & a & s & d: 15 -> x
        """

        if keys[pg.K_w]:
            combo += 1
        if keys[pg.K_d]:
            combo += 2
        if keys[pg.K_s]:
            combo += 4
        if keys[pg.K_a]:
            combo += 8
        
        if combo > 0:
            if combo == 3:
                direction_modifier = 45
            elif combo == 2 or combo == 7:
                direction_modifier = 90
            elif combo == 6:
                direction_modifier = 135
            elif combo == 4 or combo == 14:
                direction_modifier = 180
            elif combo == 12:
                direction_modifier = 225
            elif combo == 8 or combo == 13:
                direction_modifier = 270
            elif combo == 9:
                direction_modifier = 315
            
            d_pos[0] = self.frame_time * 0.02 * np.cos(np.deg2rad(self.scene.player.theta + direction_modifier))
            d_pos[2] = self.frame_time * 0.02 * np.sin(np.deg2rad(self.scene.player.theta + direction_modifier))
        
        if keys[pg.K_SPACE]:
            up = 1
        if keys[pg.K_LCTRL]:
            down = 1
        
        d_pos[1] = self.frame_time * 0.02 * (up - down)

        self.scene.move_player(d_pos)
    
    def handle_mouse(self):

        (x, y) = pg.mouse.get_pos()
        theta_increment = self.frame_time * 0.05 * ((self.screen_width // 2) - x)
        phi_increment = self.frame_time * 0.05 * ((self.screen_height // 2) - y)
        self.scene.spin_player(-theta_increment, phi_increment)
        pg.mouse.set_pos((self.screen_width // 2,self.screen_height // 2))

    def calculate_framerate(self):

        self.current_time = pg.time.get_ticks()
        delta = self.current_time - self.last_time
        if (delta >= 1000):
            framerate = max(1,int(1000.0 * self.num_frames/delta))
            pg.display.set_caption(f"Running at {framerate} fps.")
            self.last_time = self.current_time
            self.num_frames = -1
            self.frame_time = float(1000.0 / max(1,framerate))
        self.num_frames += 1

    def quit(self):
        
        self.renderer.destroy()


class GraphicsEngine:
    
    def __init__(self, screen_width, screen_height):
        
        # Initilize pygame
        pg.init()
        pg.mouse.set_visible(False)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((screen_width, screen_height), pg.OPENGL|pg.DOUBLEBUF)
        
        self.wood_texture = Material("gfx/wood.jpeg")
        self.cube_mesh = Mesh("models/cube.obj")

        #initialise opengl
        gl.glClearColor(0.9, 0.5, 0.8, 1)
        self.shader = self.create_shader("shaders/vertex.txt", "shaders/fragment.txt")
        gl.glUseProgram(self.shader)
        gl.glUniform1i(gl.glGetUniformLocation(self.shader, "imageTexture"), 0)
        gl.glEnable(gl.GL_DEPTH_TEST)

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = 640/480, 
            near = 0.1, far = 50, dtype=np.float32
        )
        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self.shader,"projection"),
            1, gl.GL_FALSE, projection_transform
        )
        self.model_matrix_location = gl.glGetUniformLocation(self.shader, "model")
        self.view_matrix_location = gl.glGetUniformLocation(self.shader, "view")
        
    def create_shader(self, vertex_filepath, fragment_filepath):
        
        with open(vertex_filepath, 'r') as f:
            vertex_src = f.readlines()
        
        with open(fragment_filepath, 'r') as f:
            fragment_src = f.readlines()
        
        shader = gls.compileProgram(
            gls.compileShader(vertex_src, gl.GL_VERTEX_SHADER),
            gls.compileShader(fragment_src, gl.GL_FRAGMENT_SHADER)
        )
        
        return shader
        
    def render(self, scene):

        #refresh screen
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glUseProgram(self.shader)

        view_transform = pyrr.matrix44.create_look_at(
            eye = scene.player.position,
            target = scene.player.position + scene.player.forwards,
            up = scene.player.up, dtype = np.float32
        )
        gl.glUniformMatrix4fv(self.view_matrix_location, 1, gl.GL_FALSE, view_transform)

        for cube in scene.cubes:

            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_eulers(
                    eulers=np.radians(cube.eulers), dtype=np.float32
                )
            )
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform, 
                m2=pyrr.matrix44.create_from_translation(
                    vec=np.array(cube.position),dtype=np.float32
                )
            )
            gl.glUniformMatrix4fv(self.model_matrix_location, 1, gl.GL_FALSE, model_transform)
            self.wood_texture.use()
            gl.glBindVertexArray(self.cube_mesh.vao)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.cube_mesh.vertex_count)

            pg.display.flip()
    
    def destroy(self):

        self.cube_mesh.destroy()
        self.wood_texture.destroy()
        gl.glDeleteProgram(self.shader)
        pg.quit()


class Mesh:
    
    def __init__(self, filepath):
        
        # x, y, z, s, t, nx, ny, nz
        self.vertices = self.load_mesh(filepath)
        
        # // is integer division
        self.vertex_count = len(self.vertices) // 8
        
        self.vertices = np.array(self.vertices, dtype=np.float32)
        
        # Create a vertex array where attributes for buffer are going to be stored, bind to make active, needs done before buffer
        self.vao = gl.glGenVertexArrays(1) 
        gl.glBindVertexArray(self.vao)
        
        # Create a vertex buffer where the raw data is stored, bind to make active, then store the raw data at the location
        self.vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, gl.GL_STATIC_DRAW)
        
        # Enable attributes for buffer. Add attribute pointer for buffer so gpu knows what data is which. Vertex shader.
        # Location 1 - Postion
        gl.glEnableVertexAttribArray(0)
        # Location, number of floats, format (float), gl.GL_FALSE, stride (total length of vertex, 4 bytes times number of floats), ctypes of starting position in bytes (void pointer expected)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 32, ctypes.c_void_p(0))
        
        # Location 2 - ST
        gl.glEnableVertexAttribArray(1)
        # Location, number of floats, format (float), gl.GL_FALSE, stride (total length of vertex, 4 bytes times number of floats), ctypes of starting position in bytes (void pointer expected)
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 32, ctypes.c_void_p(12))
    
    @staticmethod
    def load_mesh(filepath):
    
        vertices = []
        
        flags = {"v": [], "vt": [], "vn": []}
        
        with open(filepath, 'r') as f:
            lines = f.readlines()
            
            for line in lines:
                line.replace("\n", "")
                
                first_space = line.find(" ")
                flag = line[0:first_space]
                
                if flag in flags.keys():
                    line = line.replace(flag + " ", "")
                    line = line.split(" ")
                    flags[flag].append([float(x) for x in line])
                elif flag == "f":
                    line = line.replace(flag + " ", "")
                    line = line.split(" ")
                    
                    face_vertices = []
                    face_textures = []
                    face_normals = []
                    for vertex in line:
                        l = vertex.split("/")
                        face_vertices.append(flags["v"][int(l[0]) - 1])
                        face_textures.append(flags["vt"][int(l[1]) - 1])
                        face_normals.append(flags["vn"][int(l[2]) - 1])
                    triangles_in_face = len(line) - 2
                    vertex_order = []
                    for x in range(triangles_in_face):
                        vertex_order.extend((0, x + 1, x + 2))
                    for x in vertex_order:
                        vertices.extend((*face_vertices[x], *face_textures[x], *face_normals[x]))
        
        return vertices
    
    def destroy(self):
        
        # Remove allocated memory
        gl.glDeleteVertexArrays(1, (self.vao, ))
        gl.glDeleteBuffers(1, (self.vbo, ))
        

class Material:
    
    def __init__(self, filepath):
        
        # Allocate space where texture will be stored, then bind
        self.texture = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        
        # S is horizontal of a texture, T is the vertical of a texture, GL_REPEAT means image will loop if S or T over/under 1. MIN_FILTER is downsizing. MAG_FILTER is enlarging.
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        
        # Load image, then get height, and the images data
        image = pg.image.load(filepath).convert_alpha()
        image_width, image_height = image.get_rect().size
        image_data = pg.image.tostring(image, "RGBA")
        
        # Get data for image, then generate the mipmap
        # Texture location, mipmap level, format image is stored as, width, height, border color, input image format, data format, image data
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, image_width, image_height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image_data)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)        
        
    def use(self):
        
        # Select active texture 0, then bind texture
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        
    def destroy(self):
        
        # Remove allocated memory
        gl.glDeleteTextures(1, (self.texture, ))


if __name__ == "__main__":
    myApp = App(1200, 900)