import os
import sys
import numpy as np
from PIL import Image

# Adicionar o diretório pai ao path para importar o pacote
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from image_processing_pkg.processing import basic, filters, advanced
from image_processing_pkg.utils import io, metadata

def main():
    # Definir caminhos de exemplo
    input_dir = "input_images"
    output_dir = "output_images/advanced"
    
    # Criar diretórios se não existirem
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Verificar se há imagens de exemplo
    sample_images = io.list_images(input_dir)
    
    if not sample_images:
        print(f"Nenhuma imagem encontrada em '{input_dir}'. Por favor, adicione algumas imagens para testar.")
        return
    
    # Processar a primeira imagem encontrada
    sample_image = sample_images[0]
    filename = os.path.basename(sample_image)
    name, ext = os.path.splitext(filename)
    
    print(f"Processando imagem: {filename}")
    
    # Extrair e exibir metadados EXIF
    exif_data = metadata.get_exif_data(sample_image)
    if exif_data:
        print("\nDados EXIF encontrados:")
        for key, value in list(exif_data.items())[:10]:  # Mostrar apenas os primeiros 10 itens
            print(f"  {key}: {value}")
        
        # Extrair coordenadas GPS se disponíveis
        gps_coords = metadata.extract_gps_coordinates(exif_data)
        if gps_coords:
            print(f"\nCoordenadas GPS: {gps_coords}")
    else:
        print("\nNenhum dado EXIF encontrado na imagem.")
    
    # Segmentação de imagem
    print("\nAplicando segmentação de imagem...")
    segmentation_methods = ["kmeans", "felzenszwalb"]
    
    for method in segmentation_methods:
        segment_output = os.path.join(output_dir, f"{name}_segment_{method}{ext}")
        if method == "kmeans":
            advanced.segment(sample_image, segment_output, method=method, clusters=5)
        else:
            advanced.segment(sample_image, segment_output, method=method, scale=100, sigma=0.5, min_size=50)
        print(f"  Segmentação usando {method} salva em: {segment_output}")
    
    # Detecção de características
    print("\nAplicando detecção de características...")
    feature_methods = ["sift", "orb", "harris"]
    
    for method in feature_methods:
        feature_output = os.path.join(output_dir, f"{name}_features_{method}{ext}")
        advanced.feature_detection(sample_image, feature_output, method=method)
        print(f"  Detecção de características usando {method} salva em: {feature_output}")
    
    # Aplicar filtros personalizados
    print("\nAplicando filtros personalizados...")
    
    # Kernel para detecção de bordas (Sobel horizontal)
    sobel_h_kernel = [[-1, -2, -1],
                      [0, 0, 0],
                      [1, 2, 1]]
    
    custom_filter_output = os.path.join(output_dir, f"{name}_custom_filter{ext}")
    filters.apply_custom_filter(sample_image, custom_filter_output, sobel_h_kernel)
    print(f"  Filtro personalizado aplicado e salvo em: {custom_filter_output}")
    
    # Processamento em lote
    if len(sample_images) > 1:
        print("\nRealizando processamento em lote...")
        batch_output_dir = os.path.join(output_dir, "batch")
        os.makedirs(batch_output_dir, exist_ok=True)
        
        # Aplicar o mesmo filtro em todas as imagens
        batch_results = io.batch_process(
            sample_images[:5],  # Limitar a 5 imagens para o exemplo
            batch_output_dir,
            filters.to_grayscale
        )
        
        print(f"  Processamento em lote concluído. Resultados:")
        for img, success in batch_results.items():
            status = "Sucesso" if success else "Falha"
            print(f"    {os.path.basename(img)}: {status}")
    
    # Criar uma imagem composta
    print("\nCriando imagem composta...")
    
    # Carregar a imagem original
    original_img = Image.open(sample_image)
    
    # Criar uma versão em escala de cinza
    gray_img = Image.open(sample_image).convert('L').convert('RGB')
    
    # Criar uma versão com bordas detectadas
    edges_temp = os.path.join(output_dir, "temp_edges.jpg")
    advanced.detect_edges(sample_image, edges_temp)
    edges_img = Image.open(edges_temp)
    
    # Criar uma versão com filtro sépia
    sepia_temp = os.path.join(output_dir, "temp_sepia.jpg")
    filters.sepia(sample_image, sepia_temp)
    sepia_img = Image.open(sepia_temp)
    
    # Criar uma grade 2x2 com as diferentes versões
    composite_images = [original_img, gray_img, edges_img, sepia_img]
    composite_output = os.path.join(output_dir, f"{name}_composite.jpg")
    io.create_image_grid(composite_images, composite_output, grid_size=(2, 2))
    print(f"  Imagem composta salva em: {composite_output}")
    
    # Limpar arquivos temporários
    for temp_file in [edges_temp, sepia_temp]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    print("\nProcessamento avançado concluído com sucesso!")

if __name__ == "__main__":
    main()