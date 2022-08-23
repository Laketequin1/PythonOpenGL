import pygame as pg
import OpenGL.GL as gl
import numpy as np
import ctypes

class App:
    
    def __init__(self):
        
        # Initilize pygame
        pg.init()
        pg.display.set_mode((640, 480), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        
        #Initilize OpenGL
        gl.glClearColor(0.6, 0.6, 0.9, 1)
        
        #Start main
        self.main_loop()
        
    def create_shader(self, vertexFilepath, fragmentFilepath):
        
        with open(vertexFilepath, 'r') as f:
            vertex_src = f.readlines()
        
        with open(fragmentFilepath, 'r') as f:
            fragment_src = f.readlines()
        
        shader = gl.shaders.compileProgram()
        
    def main_loop(self):
        
        running = True
        while running:
            # Check events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            
            # Refresh screen
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            pg.display.flip()
            
            # Clock
            self.clock.tick(60)
            
        self.quit()
    
    @staticmethod
    def quit():
        
        pg.quit()


class Tryangle:
    
    def __init__(self):
        
        # x, y, z, r, g, b
        self.vertices = {
           -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
            0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
            0.0,  0.5, 0.0, 0.0, 0.0, 1.0
        }
        
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