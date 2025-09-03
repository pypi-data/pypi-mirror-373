import os
import glob
from PIL import Image
import numpy as np

def load_image(image_path, as_array=False):
    """
    Carrega uma imagem do disco.
    
    Args:
        image_path (str): Caminho da imagem a ser carregada
        as_array (bool): Se True, retorna como array numpy; se False, retorna objeto PIL.Image
    
    Returns:
        PIL.Image ou numpy.ndarray: A imagem carregada
    
    Raises:
        FileNotFoundError: Se o arquivo não existir
        ValueError: Se o arquivo não for uma imagem válida
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {image_path}")
    
    try:
        img = Image.open(image_path)
        if as_array:
            return np.array(img)
        return img
    except Exception as e:
        raise ValueError(f"Erro ao carregar imagem: {e}")

def save_image(image, output_path, format=None, quality=95):
    """
    Salva uma imagem no disco.
    
    Args:
        image (PIL.Image ou numpy.ndarray): Imagem a ser salva
        output_path (str): Caminho onde a imagem será salva
        format (str, optional): Formato da imagem (jpg, png, etc). Se None, será inferido da extensão
        quality (int): Qualidade para formatos com compressão (0-100)
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        # Criar diretório de saída se não existir
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Converter array numpy para imagem PIL se necessário
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image.astype('uint8'))
        
        # Inferir formato da extensão se não especificado
        if format is None:
            format = os.path.splitext(output_path)[1][1:].upper()
            if not format:
                format = 'PNG'
        
        # Salvar a imagem
        image.save(output_path, format=format, quality=quality)
        return True
    except Exception as e:
        print(f"Erro ao salvar imagem: {e}")
        return False

def list_images(directory, extensions=None, recursive=False):
    """
    Lista todos os arquivos de imagem em um diretório.
    
    Args:
        directory (str): Diretório a ser pesquisado
        extensions (list, optional): Lista de extensões a serem incluídas (ex: ['.jpg', '.png'])
        recursive (bool): Se True, pesquisa em subdiretórios
    
    Returns:
        list: Lista de caminhos de arquivos de imagem
    """
    if not os.path.isdir(directory):
        raise ValueError(f"Diretório não encontrado: {directory}")
    
    # Extensões padrão se não especificadas
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
    
    # Garantir que as extensões começam com ponto
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
    
    # Padrão de busca
    pattern = os.path.join(directory, '**' if recursive else '', '*')
    
    # Listar todos os arquivos
    all_files = glob.glob(pattern, recursive=recursive)
    
    # Filtrar por extensão
    image_files = [f for f in all_files if os.path.isfile(f) and 
                  any(f.lower().endswith(ext.lower()) for ext in extensions)]
    
    return sorted(image_files)

def batch_process(input_files, output_dir, process_func, **kwargs):
    """
    Processa um lote de imagens usando uma função de processamento.
    
    Args:
        input_files (list): Lista de caminhos de arquivos de entrada
        output_dir (str): Diretório onde as imagens processadas serão salvas
        process_func (callable): Função de processamento a ser aplicada em cada imagem
        **kwargs: Argumentos adicionais para a função de processamento
    
    Returns:
        dict: Dicionário com resultados do processamento (sucesso/falha para cada arquivo)
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    results = {}
    
    for input_file in input_files:
        try:
            # Obter nome do arquivo sem o caminho
            filename = os.path.basename(input_file)
            output_path = os.path.join(output_dir, filename)
            
            # Aplicar função de processamento
            success = process_func(input_file, output_path, **kwargs)
            results[input_file] = success
        except Exception as e:
            print(f"Erro ao processar {input_file}: {e}")
            results[input_file] = False
    
    return results

def create_image_grid(images, output_path, grid_size=None, padding=5, background_color=(255, 255, 255)):
    """
    Cria uma grade de imagens a partir de uma lista de imagens.
    
    Args:
        images (list): Lista de caminhos de imagens ou objetos PIL.Image
        output_path (str): Caminho onde a grade será salva
        grid_size (tuple, optional): Tamanho da grade (linhas, colunas). Se None, será calculado automaticamente
        padding (int): Espaçamento entre as imagens em pixels
        background_color (tuple): Cor de fundo da grade (R, G, B)
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        # Carregar imagens se forem caminhos
        loaded_images = []
        for img in images:
            if isinstance(img, str):
                loaded_images.append(Image.open(img))
            else:
                loaded_images.append(img)
        
        # Determinar tamanho da grade se não especificado
        if grid_size is None:
            cols = int(np.ceil(np.sqrt(len(loaded_images))))
            rows = int(np.ceil(len(loaded_images) / cols))
        else:
            rows, cols = grid_size
        
        # Encontrar o tamanho máximo das imagens
        max_width = max(img.width for img in loaded_images)
        max_height = max(img.height for img in loaded_images)
        
        # Criar imagem de fundo
        grid_width = cols * max_width + (cols + 1) * padding
        grid_height = rows * max_height + (rows + 1) * padding
        grid = Image.new('RGB', (grid_width, grid_height), background_color)
        
        # Posicionar imagens na grade
        for idx, img in enumerate(loaded_images):
            if idx >= rows * cols:
                break
                
            row = idx // cols
            col = idx % cols
            
            x = col * max_width + (col + 1) * padding
            y = row * max_height + (row + 1) * padding
            
            grid.paste(img, (x, y))
        
        # Salvar a grade
        grid.save(output_path)
        return True
    except Exception as e:
        print(f"Erro ao criar grade de imagens: {e}")
        return False