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


class App:
    
    def __init__(self):
        
        # Initilize pygame
        pg.init()
        pg.display.set_mode((640, 480), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        
        # Initilize OpenGL
        gl.glClearColor(0.6, 0.6, 0.9, 1)
        gl.glEnable(gl.GL_BLEND)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        self.shader = self.create_shader("shaders/vertex.txt", "shaders/fragment.txt")
        gl.glUseProgram(self.shader)
        gl.glUniform1i(gl.glGetUniformLocation(self.shader, "imageTexture"), 0)
        
        # Add cube and textures. Eulers - pitch, roll, yaw
        self.cube = Cube(
            position = [0, 0, -90],
            eulers = [0, 0, 0]
        )
        
        self.cube_mesh = CubeMesh()
        
        self.wood_texture = Material("gfx/wood.jpg")
        
        # Generate perspective projection
        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = 640/480,
            near = 0.1, far = 100, dtype=np.float32
        )
        
        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self.shader, "projection"),
            1, gl.GL_FALSE, projection_transform
        )
        
        self.modelMatrixLocation = gl.glGetUniformLocation(self.shader, "model")
        
        # Start main
        self.main_loop()
        
    def create_shader(self, vertexFilepath, fragmentFilepath):
        
        with open(vertexFilepath, 'r') as f:
            vertex_src = f.readlines()
        
        with open(fragmentFilepath, 'r') as f:
            fragment_src = f.readlines()
        
        shader = gls.compileProgram(
            gls.compileShader(vertex_src, gl.GL_VERTEX_SHADER),
            gls.compileShader(fragment_src, gl.GL_FRAGMENT_SHADER)
        )
        
        return shader
        
    def main_loop(self):
        
        distance_change = -0.1
        
        running = True
        while running:
            # Check events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            
            # Update
            self.cube.eulers[2] += 0.8
            if self.cube.eulers[2] > 360:
                self.cube.eulers[2] = 0
                
            self.cube.eulers[1] += 0.4
            if self.cube.eulers[1] > 360:
                self.cube.eulers[1] = 0
                
            self.cube.eulers[0] += 0.1
            if self.cube.eulers[0] > 360:
                self.cube.eulers[0] = 0
                
            self.cube.position[2] += distance_change
            if self.cube.position[2] < -90:
                distance_change *= -1
            if self.cube.position[2] > -3:
                distance_change = 0
            
            pg.display.set_caption(str(int(self.clock.get_fps())) + " fps")
            
            # Refresh screen
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            
            # Draw
            gl.glUseProgram(self.shader)
            
            self.wood_texture.use()
            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            
            # Eulers - pitch, roll, yaw
            model_transform = pyrr.matrix44.multiply(
                m1 = model_transform,
                m2 = pyrr.matrix44.create_from_eulers(
                    eulers=np.radians(self.cube.eulers),
                    dtype=np.float32
                )
            )
            
            model_transform = pyrr.matrix44.multiply(
                m1 = model_transform,
                m2 = pyrr.matrix44.create_from_translation(
                    vec=self.cube.position,
                    dtype=np.float32
                )
            )
            
            gl.glUniformMatrix4fv(self.modelMatrixLocation, 1, gl.GL_FALSE, model_transform)
            gl.glBindVertexArray(self.cube_mesh.vao)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.cube_mesh.vertex_count)
            
            pg.display.flip()
            
            # Clock
            self.clock.tick(120)
            
        self.quit()
    
    def quit(self):
        
        # Remove allocated memory and quit pygame
        self.cube_mesh.destroy()
        self.wood_texture.destroy()
        gl.glDeleteProgram(self.shader)
        pg.quit()


class CubeMesh:
    
    def __init__(self):
        
        # x, y, z, s, t
        self.vertices = (
           -0.5, -0.5, -0.5, 0, 0,
            0.5, -0.5, -0.5, 1, 0,
            0.5,  0.5, -0.5, 1, 1,

            0.5,  0.5, -0.5, 1, 1,
           -0.5,  0.5, -0.5, 0, 1,
           -0.5, -0.5, -0.5, 0, 0,

           -0.5, -0.5,  0.5, 0, 0,
            0.5, -0.5,  0.5, 1, 0,
            0.5,  0.5,  0.5, 1, 1,

            0.5,  0.5,  0.5, 1, 1,
           -0.5,  0.5,  0.5, 0, 1,
           -0.5, -0.5,  0.5, 0, 0,

           -0.5,  0.5,  0.5, 1, 0,
           -0.5,  0.5, -0.5, 1, 1,
           -0.5, -0.5, -0.5, 0, 1,

           -0.5, -0.5, -0.5, 0, 1,
           -0.5, -0.5,  0.5, 0, 0,
           -0.5,  0.5,  0.5, 1, 0,

            0.5,  0.5,  0.5, 1, 0,
            0.5,  0.5, -0.5, 1, 1,
            0.5, -0.5, -0.5, 0, 1,

            0.5, -0.5, -0.5, 0, 1,
            0.5, -0.5,  0.5, 0, 0,
            0.5,  0.5,  0.5, 1, 0,

           -0.5, -0.5, -0.5, 0, 1,
            0.5, -0.5, -0.5, 1, 1,
            0.5, -0.5,  0.5, 1, 0,

            0.5, -0.5,  0.5, 1, 0,
           -0.5, -0.5,  0.5, 0, 0,
           -0.5, -0.5, -0.5, 0, 1,

           -0.5,  0.5, -0.5, 0, 1,
            0.5,  0.5, -0.5, 1, 1,
            0.5,  0.5,  0.5, 1, 0,

            0.5,  0.5,  0.5, 1, 0,
           -0.5,  0.5,  0.5, 0, 0,
           -0.5,  0.5, -0.5, 0, 1
            )
        
        # // is integer division
        self.vertex_count = len(self.vertices) // 5
        
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
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 20, ctypes.c_void_p(0))
        
        # Location 2 - ST
        gl.glEnableVertexAttribArray(1)
        # Location, number of floats, format (float), gl.GL_FALSE, stride (total length of vertex, 4 bytes times number of floats), ctypes of starting position in bytes (void pointer expected)
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 20, ctypes.c_void_p(12))
        
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
    myApp = App()