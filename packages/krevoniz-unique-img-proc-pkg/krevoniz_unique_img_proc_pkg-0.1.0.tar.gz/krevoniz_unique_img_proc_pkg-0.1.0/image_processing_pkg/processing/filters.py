import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

def blur(input_path, output_path, radius=2):
    """
    Aplica um filtro de desfoque (blur) na imagem.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho para salvar a imagem com filtro
        radius (int): Raio do desfoque (quanto maior, mais intenso)
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        img = Image.open(input_path)
        blurred_img = img.filter(ImageFilter.GaussianBlur(radius=radius))
        blurred_img.save(output_path)
        return True
    except Exception as e:
        print(f"Erro ao aplicar filtro de desfoque: {e}")
        return False

def sharpen(input_path, output_path, amount=1.5):
    """
    Aplica um filtro de nitidez (sharpen) na imagem.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho para salvar a imagem com filtro
        amount (float): Intensidade do filtro (1.0 é normal, valores maiores aumentam a nitidez)
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        img = Image.open(input_path)
        enhancer = ImageEnhance.Sharpness(img)
        sharpened_img = enhancer.enhance(amount)
        sharpened_img.save(output_path)
        return True
    except Exception as e:
        print(f"Erro ao aplicar filtro de nitidez: {e}")
        return False

def adjust_brightness(input_path, output_path, factor=1.5):
    """
    Ajusta o brilho da imagem.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho para salvar a imagem com brilho ajustado
        factor (float): Fator de ajuste (1.0 é normal, <1.0 escurece, >1.0 clareia)
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        img = Image.open(input_path)
        enhancer = ImageEnhance.Brightness(img)
        brightened_img = enhancer.enhance(factor)
        brightened_img.save(output_path)
        return True
    except Exception as e:
        print(f"Erro ao ajustar brilho: {e}")
        return False

def adjust_contrast(input_path, output_path, factor=1.5):
    """
    Ajusta o contraste da imagem.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho para salvar a imagem com contraste ajustado
        factor (float): Fator de ajuste (1.0 é normal, <1.0 diminui, >1.0 aumenta)
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        img = Image.open(input_path)
        enhancer = ImageEnhance.Contrast(img)
        contrasted_img = enhancer.enhance(factor)
        contrasted_img.save(output_path)
        return True
    except Exception as e:
        print(f"Erro ao ajustar contraste: {e}")
        return False

def sepia(input_path, output_path, intensity=1.0):
    """
    Aplica um filtro sépia na imagem.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho para salvar a imagem com filtro sépia
        intensity (float): Intensidade do efeito (0.0 a 1.0)
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        img = Image.open(input_path).convert('RGB')
        img_array = np.array(img)
        
        # Matriz de transformação para efeito sépia
        sepia_matrix = np.array([
            [0.393 + 0.607 * (1 - intensity), 0.769 - 0.769 * (1 - intensity), 0.189 - 0.189 * (1 - intensity)],
            [0.349 - 0.349 * (1 - intensity), 0.686 + 0.314 * (1 - intensity), 0.168 - 0.168 * (1 - intensity)],
            [0.272 - 0.272 * (1 - intensity), 0.534 - 0.534 * (1 - intensity), 0.131 + 0.869 * (1 - intensity)]
        ])
        
        # Aplicar a transformação
        sepia_array = np.dot(img_array, sepia_matrix.T)
        sepia_array = np.clip(sepia_array, 0, 255).astype(np.uint8)
        
        sepia_img = Image.fromarray(sepia_array)
        sepia_img.save(output_path)
        return True
    except Exception as e:
        print(f"Erro ao aplicar filtro sépia: {e}")
        return False

def emboss(input_path, output_path):
    """
    Aplica um filtro de relevo (emboss) na imagem.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho para salvar a imagem com filtro de relevo
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        img = Image.open(input_path)
        embossed_img = img.filter(ImageFilter.EMBOSS)
        embossed_img.save(output_path)
        return True
    except Exception as e:
        print(f"Erro ao aplicar filtro de relevo: {e}")
        return False

def find_edges(input_path, output_path):
    """
    Aplica um filtro de detecção de bordas simples na imagem.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho para salvar a imagem com bordas detectadas
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        img = Image.open(input_path)
        edges_img = img.filter(ImageFilter.FIND_EDGES)
        edges_img.save(output_path)
        return True
    except Exception as e:
        print(f"Erro ao aplicar filtro de detecção de bordas: {e}")
        return False

def apply_custom_filter(input_path, output_path, kernel):
    """
    Aplica um filtro personalizado usando um kernel definido pelo usuário.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho para salvar a imagem com filtro personalizado
        kernel: Matriz de convolução (kernel) para o filtro
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        img = Image.open(input_path)
        custom_filter = ImageFilter.Kernel(
            size=tuple(np.array(kernel).shape),
            kernel=np.array(kernel).flatten(),
            scale=None,
            offset=0
        )
        filtered_img = img.filter(custom_filter)
        filtered_img.save(output_path)
        return True
    except Exception as e:
        print(f"Erro ao aplicar filtro personalizado: {e}")
        return False