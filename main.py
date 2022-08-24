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
        
        # Add triangle
        self.triangle = Triangle((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)), (random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)), (random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)))
        
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
            self.triangle = Triangle((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)), (random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)), (random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)))
            
            # Draw
            gl.glUseProgram(self.shader)
            gl.glBindVertexArray(self.triangle.vao)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.triangle.vertex_count)
            
            pg.display.flip()
            
            # Clock
            self.clock.tick(60)
            
        self.quit()
    
    def quit(self):
        
        self.triangle.destroy()
        gl.glDeleteProgram(self.shader)
        pg.quit()


class Triangle:
    
    def __init__(self, point1, point2, point3):
        
        # x, y, z, r, g, b
        self.vertices = (
            *point1, 1.0, 0.0, 0.0,
            *point2, 0.0, 1.0, 0.0,
            *point3, 0.0, 0.0, 1.0
        )
        
        self.vertices = np.array(self.vertices, dtype=np.float32)
        
        self.vertex_count = 3
        
        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)
        self.vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, gl.GL_STATIC_DRAW)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 24, ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 24, ctypes.c_void_p(12))
        
    def destroy(self):
        
        gl.glDeleteVertexArrays(1, (self.vao, ))
        gl.glDeleteBuffers(1, (self.vbo, ))
        

if __name__ == "__main__":
    myApp = App()