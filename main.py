import pygame as pg
import OpenGL.GL as gl
import numpy as np
import ctypes
import OpenGL.GL.shaders as gls

import random

class App:
    
    def __init__(self):
        
        # Initilize pygame
        pg.init()
        pg.display.set_mode((640, 480), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        
        # Initilize OpenGL
        gl.glClearColor(0.6, 0.6, 0.9, 1)
        self.shader = self.create_shader("shaders/vertex.txt", "shaders/fragment.txt")
        gl.glUseProgram(self.shader)
        gl.glUniform1i(gl.glGetUniformLocation(self.shader, "imageTexture"), 0)
        
        # Add triangle and textures
        self.triangle = Triangle()
        self.wood_texture = Material("gfx/cat.png")
        
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
        
        running = True
        while running:
            # Check events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            
            # Refresh screen
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            
            # Update
            pg.display.set_caption(str(int(self.clock.get_fps())) + " fps")
            
            # Draw
            gl.glUseProgram(self.shader)
            self.wood_texture.use()
            gl.glBindVertexArray(self.triangle.vao)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.triangle.vertex_count)
            
            pg.display.flip()
            
            # Clock
            self.clock.tick(0)
            
        self.quit()
    
    def quit(self):
        
        # Remove allocated memory and quit pygame
        self.triangle.destroy()
        self.wood_texture.destroy()
        gl.glDeleteProgram(self.shader)
        pg.quit()


class Triangle:
    
    def __init__(self):
        
        # x, y, z, r, g, b, s, t
        self.vertices = (
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
             0.5, -0.5, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0,
             0.0,  0.5, 0.0, 0.0, 0.0, 1.0, 0.5, 0.0
        )
        
        self.vertices = np.array(self.vertices, dtype=np.float32)
        
        self.vertex_count = 3
        
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
        
        # Location 2 - rgb
        gl.glEnableVertexAttribArray(1)
        # Location, number of floats, format (float), gl.GL_FALSE, stride (total length of vertex, 4 bytes times number of floats), ctypes of starting position in bytes (void pointer expected)
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 32, ctypes.c_void_p(12))
        
        # Location 3 - rgb
        gl.glEnableVertexAttribArray(2)
        # Location, number of floats, format (float), gl.GL_FALSE, stride (total length of vertex, 4 bytes times number of floats), ctypes of starting position in bytes (void pointer expected)
        gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, gl.GL_FALSE, 32, ctypes.c_void_p(24))
        
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
        image = pg.image.load(filepath).convert()
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