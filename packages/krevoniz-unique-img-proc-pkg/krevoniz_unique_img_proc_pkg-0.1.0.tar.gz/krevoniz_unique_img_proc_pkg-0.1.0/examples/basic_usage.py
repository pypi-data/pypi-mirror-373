import os
import sys

# Adicionar o diretório pai ao path para importar o pacote
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from image_processing_pkg.processing import basic, filters, advanced
from image_processing_pkg.utils import io, metadata

def main():
    # Definir caminhos de exemplo
    input_dir = "input_images"
    output_dir = "output_images"
    
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
    
    # Obter informações da imagem
    info = metadata.get_image_info(sample_image)
    print("\nInformações da imagem:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Processamento básico
    print("\nAplicando processamento básico...")
    
    # Redimensionar
    resize_output = os.path.join(output_dir, f"{name}_resized{ext}")
    basic.resize(sample_image, resize_output, width=800)
    print(f"  Imagem redimensionada salva em: {resize_output}")
    
    # Converter para escala de cinza
    gray_output = os.path.join(output_dir, f"{name}_gray{ext}")
    basic.to_grayscale(sample_image, gray_output)
    print(f"  Imagem em escala de cinza salva em: {gray_output}")
    
    # Rotacionar
    rotate_output = os.path.join(output_dir, f"{name}_rotated{ext}")
    basic.rotate(sample_image, rotate_output, angle=45)
    print(f"  Imagem rotacionada salva em: {rotate_output}")
    
    # Aplicar filtros
    print("\nAplicando filtros...")
    
    # Desfoque
    blur_output = os.path.join(output_dir, f"{name}_blur{ext}")
    filters.blur(sample_image, blur_output, radius=3)
    print(f"  Imagem com desfoque salva em: {blur_output}")
    
    # Nitidez
    sharpen_output = os.path.join(output_dir, f"{name}_sharp{ext}")
    filters.sharpen(sample_image, sharpen_output, amount=2.0)
    print(f"  Imagem com nitidez aumentada salva em: {sharpen_output}")
    
    # Sépia
    sepia_output = os.path.join(output_dir, f"{name}_sepia{ext}")
    filters.sepia(sample_image, sepia_output)
    print(f"  Imagem com filtro sépia salva em: {sepia_output}")
    
    # Processamento avançado
    print("\nAplicando processamento avançado...")
    
    # Detecção de bordas
    edges_output = os.path.join(output_dir, f"{name}_edges{ext}")
    advanced.detect_edges(sample_image, edges_output, method="canny")
    print(f"  Imagem com bordas detectadas salva em: {edges_output}")
    
    # Histograma
    histogram_output = os.path.join(output_dir, f"{name}_histogram.png")
    advanced.histogram(sample_image, histogram_output)
    print(f"  Histograma salvo em: {histogram_output}")
    
    # Criar grade de imagens processadas
    print("\nCriando grade de imagens processadas...")
    processed_images = io.list_images(output_dir)
    grid_output = os.path.join(output_dir, "image_grid.jpg")
    io.create_image_grid(processed_images, grid_output)
    print(f"  Grade de imagens salva em: {grid_output}")
    
    print("\nProcessamento concluído com sucesso!")

if __name__ == "__main__":
    main()