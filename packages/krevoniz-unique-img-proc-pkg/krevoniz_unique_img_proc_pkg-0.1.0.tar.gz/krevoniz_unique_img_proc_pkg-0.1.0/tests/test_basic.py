import os
import sys
import unittest
from PIL import Image
import numpy as np

# Adicionar o diretório pai ao path para importar o pacote
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from image_processing_pkg.processing import basic

class TestBasicProcessing(unittest.TestCase):
    
    def setUp(self):
        # Criar diretório para testes
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_images')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Criar uma imagem de teste
        self.test_image = os.path.join(self.test_dir, 'test.jpg')
        img = Image.new('RGB', (100, 100), color=(73, 109, 137))
        img.save(self.test_image)
        
        # Definir caminho para imagem de saída
        self.output_image = os.path.join(self.test_dir, 'output.jpg')
    
    def tearDown(self):
        # Remover arquivos de teste
        if os.path.exists(self.output_image):
            os.remove(self.output_image)
    
    def test_resize(self):
        # Testar redimensionamento
        result = basic.resize(self.test_image, self.output_image, width=50, height=50)
        self.assertTrue(result)
        
        # Verificar dimensões da imagem redimensionada
        with Image.open(self.output_image) as img:
            self.assertEqual(img.width, 50)
            self.assertEqual(img.height, 50)
    
    def test_resize_keep_aspect_ratio(self):
        # Testar redimensionamento mantendo proporção
        result = basic.resize(self.test_image, self.output_image, width=50, keep_aspect_ratio=True)
        self.assertTrue(result)
        
        # Verificar dimensões da imagem redimensionada
        with Image.open(self.output_image) as img:
            self.assertEqual(img.width, 50)
            self.assertEqual(img.height, 50)  # Como a imagem original é quadrada, altura = largura
    
    def test_rotate(self):
        # Testar rotação
        result = basic.rotate(self.test_image, self.output_image, angle=90)
        self.assertTrue(result)
        
        # Verificar se a imagem foi criada
        self.assertTrue(os.path.exists(self.output_image))
    
    def test_crop(self):
        # Testar recorte
        result = basic.crop(self.test_image, self.output_image, left=25, top=25, right=75, bottom=75)
        self.assertTrue(result)
        
        # Verificar dimensões da imagem recortada
        with Image.open(self.output_image) as img:
            self.assertEqual(img.width, 50)
            self.assertEqual(img.height, 50)
    
    def test_to_grayscale(self):
        # Testar conversão para escala de cinza
        result = basic.to_grayscale(self.test_image, self.output_image)
        self.assertTrue(result)
        
        # Verificar modo da imagem
        with Image.open(self.output_image) as img:
            self.assertEqual(img.mode, 'L')
    
    def test_flip(self):
        # Testar espelhamento horizontal
        result = basic.flip(self.test_image, self.output_image, horizontal=True)
        self.assertTrue(result)
        
        # Verificar se a imagem foi criada
        self.assertTrue(os.path.exists(self.output_image))
        
        # Testar espelhamento vertical
        result = basic.flip(self.test_image, self.output_image, horizontal=False)
        self.assertTrue(result)
        
        # Verificar se a imagem foi criada
        self.assertTrue(os.path.exists(self.output_image))
    
    def test_convert_format(self):
        # Testar conversão de formato para PNG
        output_png = os.path.join(self.test_dir, 'output.png')
        result = basic.convert_format(self.test_image, output_png)
        self.assertTrue(result)
        
        # Verificar formato da imagem
        with Image.open(output_png) as img:
            self.assertEqual(img.format, 'PNG')
        
        # Limpar
        if os.path.exists(output_png):
            os.remove(output_png)

if __name__ == '__main__':
    unittest.main()