import os
import sys
import unittest
from PIL import Image
import numpy as np

# Adicionar o diretório pai ao path para importar o pacote
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from image_processing_pkg.processing import filters

class TestFilters(unittest.TestCase):
    
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
    
    def test_blur(self):
        # Testar desfoque
        result = filters.blur(self.test_image, self.output_image, radius=2)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
    
    def test_sharpen(self):
        # Testar nitidez
        result = filters.sharpen(self.test_image, self.output_image, factor=2.0)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
    
    def test_adjust_brightness(self):
        # Testar ajuste de brilho
        result = filters.adjust_brightness(self.test_image, self.output_image, factor=1.5)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
        
        # Testar redução de brilho
        result = filters.adjust_brightness(self.test_image, self.output_image, factor=0.5)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
    
    def test_adjust_contrast(self):
        # Testar ajuste de contraste
        result = filters.adjust_contrast(self.test_image, self.output_image, factor=1.5)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
        
        # Testar redução de contraste
        result = filters.adjust_contrast(self.test_image, self.output_image, factor=0.5)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
    
    def test_sepia(self):
        # Testar filtro sépia
        result = filters.sepia(self.test_image, self.output_image)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
    
    def test_emboss(self):
        # Testar efeito de relevo
        result = filters.emboss(self.test_image, self.output_image)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
    
    def test_find_edges(self):
        # Testar detecção de bordas
        result = filters.find_edges(self.test_image, self.output_image)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
    
    def test_apply_custom_filter(self):
        # Testar aplicação de filtro personalizado
        # Kernel de desfoque
        kernel = np.ones((3, 3), np.float32) / 9
        result = filters.apply_custom_filter(self.test_image, self.output_image, kernel)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))

if __name__ == '__main__':
    unittest.main()