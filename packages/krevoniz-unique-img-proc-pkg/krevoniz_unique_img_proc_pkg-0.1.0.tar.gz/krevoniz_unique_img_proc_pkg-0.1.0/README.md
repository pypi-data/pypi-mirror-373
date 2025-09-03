# Image Processing Package

## Descrição
O pacote `image_processing_pkg` é uma biblioteca Python para processamento de imagens que oferece:
- Processamento básico: redimensionamento, rotação, corte e conversão entre formatos
- Aplicação de filtros: blur, sharpen, grayscale, sepia, etc.
- Processamento avançado: detecção de bordas, segmentação, histograma
- Utilitários para manipulação de metadados de imagens

## Instalação

Use o gerenciador de pacotes [pip](https://pip.pypa.io/en/stable/) para instalar o pacote:

```bash
pip install image_processing_pkg
```

## Uso

### Processamento Básico
```python
from image_processing_pkg.processing import basic

# Redimensionar uma imagem
basic.resize("input.jpg", "output.jpg", width=800, height=600)

# Converter para escala de cinza
basic.to_grayscale("input.jpg", "output_gray.jpg")

# Aplicar rotação
basic.rotate("input.jpg", "output_rotated.jpg", angle=90)
```

### Aplicação de Filtros
```python
from image_processing_pkg.processing import filters

# Aplicar filtro de desfoque
filters.blur("input.jpg", "output_blur.jpg", radius=5)

# Aplicar filtro de nitidez
filters.sharpen("input.jpg", "output_sharp.jpg", amount=1.5)

# Aplicar filtro sépia
filters.sepia("input.jpg", "output_sepia.jpg")
```

### Processamento Avançado
```python
from image_processing_pkg.processing import advanced

# Detectar bordas
advanced.detect_edges("input.jpg", "output_edges.jpg", method="canny")

# Segmentação de imagem
advanced.segment("input.jpg", "output_segmented.jpg", clusters=5)

# Gerar histograma
histogram = advanced.histogram("input.jpg")
```

## Autor
Python Developer

## Licença
[MIT](https://choosealicense.com/licenses/mit/)