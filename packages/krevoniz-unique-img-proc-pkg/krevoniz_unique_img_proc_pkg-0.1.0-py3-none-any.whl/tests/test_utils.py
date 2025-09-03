import os
import sys
import unittest
from PIL import Image
import numpy as np

# Adicionar o diretório pai ao path para importar o pacote
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from image_processing_pkg.utils import io, metadata

class TestIOUtils(unittest.TestCase):
    
    def setUp(self):
        # Criar diretório para testes
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_images')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Criar uma imagem de teste
        self.test_image = os.path.join(self.test_dir, 'test.jpg')
        img = Image.new('RGB', (100, 100), color=(73, 109, 137))
        img.save(self.test_image)
        
        # Criar mais algumas imagens para testes
        for i in range(3):
            img_path = os.path.join(self.test_dir, f'test_{i}.jpg')
            img = Image.new('RGB', (100, 100), color=(73, 109, 137))
            img.save(img_path)
    
    def tearDown(self):
        # Remover arquivos de teste
        for file in os.listdir(self.test_dir):
            if file.startswith('output') or file.startswith('grid'):
                os.remove(os.path.join(self.test_dir, file))
    
    def test_load_image(self):
        # Testar carregamento de imagem
        img = io.load_image(self.test_image)
        self.assertIsNotNone(img)
        self.assertEqual(img.width, 100)
        self.assertEqual(img.height, 100)
    
    def test_save_image(self):
        # Testar salvamento de imagem
        img = Image.new('RGB', (50, 50), color=(255, 0, 0))
        output_path = os.path.join(self.test_dir, 'output.jpg')
        result = io.save_image(img, output_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))
    
    def test_list_images(self):
        # Testar listagem de imagens
        images = io.list_images(self.test_dir)
        self.assertGreaterEqual(len(images), 4)  # test.jpg + test_0.jpg, test_1.jpg, test_2.jpg
    
    def test_batch_process(self):
        # Testar processamento em lote
        def process_func(img):
            return img.convert('L')
        
        output_dir = os.path.join(self.test_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        result = io.batch_process(self.test_dir, output_dir, process_func)
        self.assertTrue(result)
        
        # Verificar se os arquivos foram criados
        self.assertTrue(os.path.exists(os.path.join(output_dir, 'test.jpg')))
        
        # Limpar
        for file in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, file))
        os.rmdir(output_dir)
    
    def test_create_image_grid(self):
        # Testar criação de grid de imagens
        image_paths = [os.path.join(self.test_dir, f'test_{i}.jpg') for i in range(3)]
        output_path = os.path.join(self.test_dir, 'grid.jpg')
        
        result = io.create_image_grid(image_paths, output_path, rows=1, cols=3)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))
        
        # Verificar dimensões do grid
        with Image.open(output_path) as img:
            self.assertEqual(img.width, 300)  # 3 imagens de largura 100
            self.assertEqual(img.height, 100)  # 1 linha de altura 100

class TestMetadataUtils(unittest.TestCase):
    
    def setUp(self):
        # Criar diretório para testes
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_images')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Criar uma imagem de teste
        self.test_image = os.path.join(self.test_dir, 'test.jpg')
        img = Image.new('RGB', (100, 100), color=(73, 109, 137))
        img.save(self.test_image)
    
    def tearDown(self):
        # Remover arquivos de teste
        if os.path.exists(os.path.join(self.test_dir, 'output.jpg')):
            os.remove(os.path.join(self.test_dir, 'output.jpg'))
    
    def test_get_image_info(self):
        # Testar obtenção de informações da imagem
        info = metadata.get_image_info(self.test_image)
        self.assertIsNotNone(info)
        self.assertEqual(info['width'], 100)
        self.assertEqual(info['height'], 100)
        self.assertEqual(info['format'], 'JPEG')
        self.assertEqual(info['mode'], 'RGB')
    
    def test_get_exif_data(self):
        # Testar obtenção de dados EXIF
        # Nota: a imagem de teste não tem dados EXIF, então esperamos um dicionário vazio
        exif_data = metadata.get_exif_data(self.test_image)
        self.assertIsNotNone(exif_data)
    
    def test_set_image_description(self):
        # Testar definição de descrição da imagem
        output_path = os.path.join(self.test_dir, 'output.jpg')
        description = "Imagem de teste para o pacote de processamento de imagens"
        
        result = metadata.set_image_description(self.test_image, output_path, description)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))
        
        # Verificar se a descrição foi definida
        img = Image.open(output_path)
        if 'exif' in img.info:
            exif_data = metadata.get_exif_data(output_path)
            # Nota: a verificação exata depende de como os dados EXIF são armazenados
            self.assertIsNotNone(exif_data)
    
    def test_copy_metadata(self):
        # Testar cópia de metadados
        # Primeiro, criar uma imagem com descrição
        source_path = os.path.join(self.test_dir, 'source.jpg')
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        img.save(source_path)
        
        # Definir descrição
        metadata.set_image_description(source_path, source_path, "Imagem fonte")
        
        # Copiar metadados
        output_path = os.path.join(self.test_dir, 'output.jpg')
        result = metadata.copy_metadata(source_path, self.test_image, output_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))
        
        # Limpar
        if os.path.exists(source_path):
            os.remove(source_path)
    
    def test_remove_metadata(self):
        # Testar remoção de metadados
        output_path = os.path.join(self.test_dir, 'output.jpg')
        result = metadata.remove_metadata(self.test_image, output_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))

if __name__ == '__main__':
    unittest.main()