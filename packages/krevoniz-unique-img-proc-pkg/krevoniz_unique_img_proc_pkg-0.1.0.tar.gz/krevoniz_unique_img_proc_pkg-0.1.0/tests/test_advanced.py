import os
import sys
import unittest
from PIL import Image
import numpy as np

# Adicionar o diretório pai ao path para importar o pacote
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from image_processing_pkg.processing import advanced

class TestAdvancedProcessing(unittest.TestCase):
    
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
    
    def test_detect_edges_canny(self):
        # Testar detecção de bordas com método Canny
        result = advanced.detect_edges(self.test_image, self.output_image, method='canny')
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
    
    def test_detect_edges_sobel(self):
        # Testar detecção de bordas com método Sobel
        result = advanced.detect_edges(self.test_image, self.output_image, method='sobel')
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
    
    def test_detect_edges_prewitt(self):
        # Testar detecção de bordas com método Prewitt
        result = advanced.detect_edges(self.test_image, self.output_image, method='prewitt')
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
    
    def test_segment_kmeans(self):
        # Testar segmentação com K-means
        result = advanced.segment(self.test_image, self.output_image, method='kmeans', n_segments=3)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
    
    def test_segment_watershed(self):
        # Testar segmentação com Watershed
        result = advanced.segment(self.test_image, self.output_image, method='watershed')
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
    
    def test_segment_felzenszwalb(self):
        # Testar segmentação com Felzenszwalb
        result = advanced.segment(self.test_image, self.output_image, method='felzenszwalb')
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
    
    def test_histogram(self):
        # Testar histograma para imagem colorida
        result = advanced.histogram(self.test_image, self.output_image)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
        
        # Testar histograma para imagem em escala de cinza
        grayscale_image = os.path.join(self.test_dir, 'grayscale.jpg')
        img = Image.new('L', (100, 100), color=128)
        img.save(grayscale_image)
        
        result = advanced.histogram(grayscale_image, self.output_image)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
        
        # Limpar
        if os.path.exists(grayscale_image):
            os.remove(grayscale_image)
    
    def test_feature_detection_sift(self):
        # Testar detecção de características com SIFT
        result = advanced.feature_detection(self.test_image, self.output_image, method='sift')
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
    
    def test_feature_detection_orb(self):
        # Testar detecção de características com ORB
        result = advanced.feature_detection(self.test_image, self.output_image, method='orb')
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))
    
    def test_feature_detection_harris(self):
        # Testar detecção de características com Harris
        result = advanced.feature_detection(self.test_image, self.output_image, method='harris')
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.output_image))

if __name__ == '__main__':
    unittest.main()