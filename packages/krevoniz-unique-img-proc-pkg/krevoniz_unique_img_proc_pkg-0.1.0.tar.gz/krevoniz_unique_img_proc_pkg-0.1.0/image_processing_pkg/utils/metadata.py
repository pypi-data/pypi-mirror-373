import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import datetime

def get_image_info(image_path):
    """
    Obtém informações básicas sobre uma imagem.
    
    Args:
        image_path (str): Caminho da imagem
    
    Returns:
        dict: Dicionário com informações da imagem (formato, tamanho, modo)
    """
    try:
        with Image.open(image_path) as img:
            info = {
                'filename': os.path.basename(image_path),
                'format': img.format,
                'mode': img.mode,
                'width': img.width,
                'height': img.height,
                'size_bytes': os.path.getsize(image_path),
                'size_mb': os.path.getsize(image_path) / (1024 * 1024),
                'created': datetime.datetime.fromtimestamp(
                    os.path.getctime(image_path)).strftime('%Y-%m-%d %H:%M:%S'),
                'modified': datetime.datetime.fromtimestamp(
                    os.path.getmtime(image_path)).strftime('%Y-%m-%d %H:%M:%S')
            }
            return info
    except Exception as e:
        print(f"Erro ao obter informações da imagem: {e}")
        return None

def get_exif_data(image_path):
    """
    Extrai dados EXIF de uma imagem.
    
    Args:
        image_path (str): Caminho da imagem
    
    Returns:
        dict: Dicionário com dados EXIF
    """
    try:
        with Image.open(image_path) as img:
            exif_data = {}
            
            # Verificar se a imagem tem dados EXIF
            if hasattr(img, '_getexif') and img._getexif() is not None:
                exif_info = img._getexif()
                
                # Processar dados EXIF
                for tag, value in exif_info.items():
                    decoded = TAGS.get(tag, tag)
                    
                    # Processar dados GPS separadamente
                    if decoded == 'GPSInfo':
                        gps_data = {}
                        for gps_tag in value:
                            sub_decoded = GPSTAGS.get(gps_tag, gps_tag)
                            gps_data[sub_decoded] = value[gps_tag]
                        exif_data[decoded] = gps_data
                    else:
                        exif_data[decoded] = value
            
            return exif_data
    except Exception as e:
        print(f"Erro ao extrair dados EXIF: {e}")
        return {}

def extract_gps_coordinates(exif_data):
    """
    Extrai coordenadas GPS dos dados EXIF.
    
    Args:
        exif_data (dict): Dicionário com dados EXIF
    
    Returns:
        tuple: (latitude, longitude) ou None se não houver dados GPS
    """
    try:
        if 'GPSInfo' not in exif_data:
            return None
        
        gps_info = exif_data['GPSInfo']
        
        # Verificar se temos as informações necessárias
        if 'GPSLatitude' not in gps_info or 'GPSLongitude' not in gps_info:
            return None
        
        # Extrair latitude
        lat_data = gps_info['GPSLatitude']
        lat_ref = gps_info.get('GPSLatitudeRef', 'N')
        
        lat = lat_data[0] + (lat_data[1] / 60.0) + (lat_data[2] / 3600.0)
        if lat_ref == 'S':
            lat = -lat
        
        # Extrair longitude
        lon_data = gps_info['GPSLongitude']
        lon_ref = gps_info.get('GPSLongitudeRef', 'E')
        
        lon = lon_data[0] + (lon_data[1] / 60.0) + (lon_data[2] / 3600.0)
        if lon_ref == 'W':
            lon = -lon
        
        return (lat, lon)
    except Exception as e:
        print(f"Erro ao extrair coordenadas GPS: {e}")
        return None

def set_image_description(image_path, description, output_path=None):
    """
    Define a descrição de uma imagem nos metadados.
    
    Args:
        image_path (str): Caminho da imagem original
        description (str): Descrição a ser adicionada
        output_path (str, optional): Caminho para salvar a imagem modificada. Se None, sobrescreve a original
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        # Se output_path não for especificado, sobrescreve a imagem original
        if output_path is None:
            output_path = image_path
        
        with Image.open(image_path) as img:
            # Obter formato da imagem
            img_format = img.format
            
            # Definir informações EXIF
            exif_dict = {}
            if hasattr(img, '_getexif') and img._getexif() is not None:
                exif_dict = dict(img._getexif())
            
            # Adicionar descrição
            exif_dict[0x010e] = description  # 0x010e é o código para ImageDescription
            
            # Salvar imagem com novos metadados
            img.save(output_path, format=img_format, exif=exif_dict)
        
        return True
    except Exception as e:
        print(f"Erro ao definir descrição da imagem: {e}")
        return False

def copy_metadata(source_path, target_path, output_path=None):
    """
    Copia metadados de uma imagem para outra.
    
    Args:
        source_path (str): Caminho da imagem fonte (com metadados)
        target_path (str): Caminho da imagem alvo (que receberá os metadados)
        output_path (str, optional): Caminho para salvar a imagem modificada. Se None, sobrescreve a alvo
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        # Se output_path não for especificado, sobrescreve a imagem alvo
        if output_path is None:
            output_path = target_path
        
        # Abrir imagens
        with Image.open(source_path) as source_img:
            with Image.open(target_path) as target_img:
                # Obter formato da imagem alvo
                target_format = target_img.format
                
                # Obter metadados da imagem fonte
                exif_data = None
                if hasattr(source_img, '_getexif') and source_img._getexif() is not None:
                    exif_data = source_img._getexif()
                
                # Salvar imagem alvo com metadados da fonte
                target_img.save(output_path, format=target_format, exif=exif_data)
        
        return True
    except Exception as e:
        print(f"Erro ao copiar metadados: {e}")
        return False

def remove_metadata(image_path, output_path=None):
    """
    Remove todos os metadados de uma imagem.
    
    Args:
        image_path (str): Caminho da imagem
        output_path (str, optional): Caminho para salvar a imagem sem metadados. Se None, sobrescreve a original
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        # Se output_path não for especificado, sobrescreve a imagem original
        if output_path is None:
            output_path = image_path
        
        with Image.open(image_path) as img:
            # Obter formato da imagem
            img_format = img.format
            
            # Criar uma nova imagem sem metadados
            data = list(img.getdata())
            new_img = Image.new(img.mode, img.size)
            new_img.putdata(data)
            
            # Salvar nova imagem sem metadados
            new_img.save(output_path, format=img_format)
        
        return True
    except Exception as e:
        print(f"Erro ao remover metadados: {e}")
        return False