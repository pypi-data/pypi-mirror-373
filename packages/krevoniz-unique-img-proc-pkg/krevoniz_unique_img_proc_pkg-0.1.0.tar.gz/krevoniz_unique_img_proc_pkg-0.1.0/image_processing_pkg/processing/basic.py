import os
import numpy as np
from PIL import Image

def resize(input_path, output_path, width=None, height=None, keep_aspect_ratio=True):
    """
    Redimensiona uma imagem para as dimensões especificadas.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho para salvar a imagem redimensionada
        width (int, optional): Largura desejada. Se None, será calculada a partir da altura
        height (int, optional): Altura desejada. Se None, será calculada a partir da largura
        keep_aspect_ratio (bool): Mantém a proporção original da imagem
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        img = Image.open(input_path)
        original_width, original_height = img.size
        
        if width is None and height is None:
            # Se nenhuma dimensão for especificada, mantém o tamanho original
            new_width, new_height = original_width, original_height
        elif width is None:
            # Calcula a largura mantendo a proporção
            ratio = height / original_height
            new_width = int(original_width * ratio)
            new_height = height
        elif height is None:
            # Calcula a altura mantendo a proporção
            ratio = width / original_width
            new_height = int(original_height * ratio)
            new_width = width
        elif keep_aspect_ratio:
            # Redimensiona mantendo a proporção, usando a menor dimensão como referência
            ratio_width = width / original_width
            ratio_height = height / original_height
            ratio = min(ratio_width, ratio_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
        else:
            # Redimensiona para as dimensões exatas especificadas
            new_width, new_height = width, height
        
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        resized_img.save(output_path)
        return True
    except Exception as e:
        print(f"Erro ao redimensionar imagem: {e}")
        return False

def rotate(input_path, output_path, angle=90, expand=True):
    """
    Rotaciona uma imagem pelo ângulo especificado.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho para salvar a imagem rotacionada
        angle (float): Ângulo de rotação em graus
        expand (bool): Se True, expande a imagem para acomodar a rotação
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        img = Image.open(input_path)
        rotated_img = img.rotate(angle, expand=expand, resample=Image.BICUBIC)
        rotated_img.save(output_path)
        return True
    except Exception as e:
        print(f"Erro ao rotacionar imagem: {e}")
        return False

def crop(input_path, output_path, left, top, right, bottom):
    """
    Recorta uma região da imagem.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho para salvar a imagem recortada
        left (int): Coordenada X do ponto superior esquerdo
        top (int): Coordenada Y do ponto superior esquerdo
        right (int): Coordenada X do ponto inferior direito
        bottom (int): Coordenada Y do ponto inferior direito
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        img = Image.open(input_path)
        cropped_img = img.crop((left, top, right, bottom))
        cropped_img.save(output_path)
        return True
    except Exception as e:
        print(f"Erro ao recortar imagem: {e}")
        return False

def to_grayscale(input_path, output_path):
    """
    Converte uma imagem para escala de cinza.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho para salvar a imagem em escala de cinza
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        img = Image.open(input_path).convert('L')
        img.save(output_path)
        return True
    except Exception as e:
        print(f"Erro ao converter para escala de cinza: {e}")
        return False

def flip(input_path, output_path, horizontal=True):
    """
    Espelha uma imagem horizontalmente ou verticalmente.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho para salvar a imagem espelhada
        horizontal (bool): Se True, espelha horizontalmente; se False, verticalmente
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        img = Image.open(input_path)
        if horizontal:
            flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)
        else:
            flipped_img = img.transpose(Image.FLIP_TOP_BOTTOM)
        flipped_img.save(output_path)
        return True
    except Exception as e:
        print(f"Erro ao espelhar imagem: {e}")
        return False

def convert_format(input_path, output_path, format=None):
    """
    Converte uma imagem para outro formato.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho para salvar a imagem convertida
        format (str, optional): Formato de saída (jpg, png, etc). Se None, será inferido da extensão
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        img = Image.open(input_path)
        
        # Se o formato não for especificado, tenta inferir da extensão do arquivo de saída
        if format is None:
            format = os.path.splitext(output_path)[1][1:].upper()
            if not format:
                format = img.format
        
        # Converte para RGB se estiver salvando como JPG
        if format.upper() == 'JPEG' or format.upper() == 'JPG':
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                img = img.convert('RGB')
        
        img.save(output_path, format=format)
        return True
    except Exception as e:
        print(f"Erro ao converter formato: {e}")
        return False