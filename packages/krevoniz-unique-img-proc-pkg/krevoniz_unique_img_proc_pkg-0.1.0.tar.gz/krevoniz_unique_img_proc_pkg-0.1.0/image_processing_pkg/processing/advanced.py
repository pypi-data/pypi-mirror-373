import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt
from skimage import feature, segmentation, color

def detect_edges(input_path, output_path, method="canny", **kwargs):
    """
    Detecta bordas em uma imagem usando diferentes métodos.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho para salvar a imagem com bordas detectadas
        method (str): Método de detecção ('canny', 'sobel', 'prewitt')
        **kwargs: Parâmetros específicos para cada método
            - Para 'canny': low_threshold, high_threshold
            - Para 'sobel': ksize, scale, delta
            - Para 'prewitt': não requer parâmetros adicionais
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        # Carregar imagem com OpenCV
        img = cv2.imread(input_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        if method.lower() == "canny":
            low_threshold = kwargs.get('low_threshold', 100)
            high_threshold = kwargs.get('high_threshold', 200)
            edges = cv2.Canny(gray, low_threshold, high_threshold)
        
        elif method.lower() == "sobel":
            ksize = kwargs.get('ksize', 3)
            scale = kwargs.get('scale', 1)
            delta = kwargs.get('delta', 0)
            
            grad_x = cv2.Sobel(gray, cv2.CV_16S, 1, 0, ksize=ksize, scale=scale, delta=delta)
            grad_y = cv2.Sobel(gray, cv2.CV_16S, 0, 1, ksize=ksize, scale=scale, delta=delta)
            
            abs_grad_x = cv2.convertScaleAbs(grad_x)
            abs_grad_y = cv2.convertScaleAbs(grad_y)
            
            edges = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
        
        elif method.lower() == "prewitt":
            # Implementação do operador Prewitt usando kernels
            kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
            kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
            
            prewitt_x = cv2.filter2D(gray, -1, kernelx)
            prewitt_y = cv2.filter2D(gray, -1, kernely)
            
            edges = cv2.addWeighted(prewitt_x, 0.5, prewitt_y, 0.5, 0)
        
        else:
            raise ValueError(f"Método de detecção de bordas '{method}' não suportado")
        
        cv2.imwrite(output_path, edges)
        return True
    
    except Exception as e:
        print(f"Erro ao detectar bordas: {e}")
        return False

def segment(input_path, output_path, method="kmeans", **kwargs):
    """
    Segmenta uma imagem usando diferentes métodos.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho para salvar a imagem segmentada
        method (str): Método de segmentação ('kmeans', 'watershed', 'felzenszwalb')
        **kwargs: Parâmetros específicos para cada método
            - Para 'kmeans': clusters (número de clusters)
            - Para 'watershed': markers (número de marcadores)
            - Para 'felzenszwalb': scale, sigma, min_size
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        if method.lower() == "kmeans":
            # Segmentação usando K-means
            clusters = kwargs.get('clusters', 5)
            
            img = cv2.imread(input_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Reshape para aplicar K-means
            pixels = img.reshape((-1, 3)).astype(np.float32)
            
            # Critério de parada
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
            
            # Aplicar K-means
            _, labels, centers = cv2.kmeans(pixels, clusters, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Converter de volta para uint8
            centers = np.uint8(centers)
            segmented_img = centers[labels.flatten()]
            segmented_img = segmented_img.reshape(img.shape)
            
            # Salvar resultado
            plt.imsave(output_path, segmented_img)
        
        elif method.lower() == "watershed":
            # Segmentação usando Watershed
            markers = kwargs.get('markers', 8)
            
            img = cv2.imread(input_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Aplicar threshold
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Ruído de fundo
            kernel = np.ones((3, 3), np.uint8)
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
            
            # Área de fundo certa
            sure_bg = cv2.dilate(opening, kernel, iterations=3)
            
            # Encontrar área de primeiro plano
            dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
            _, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
            
            # Encontrar região desconhecida
            sure_fg = np.uint8(sure_fg)
            unknown = cv2.subtract(sure_bg, sure_fg)
            
            # Marcação
            _, markers_img = cv2.connectedComponents(sure_fg)
            markers_img = markers_img + 1
            markers_img[unknown == 255] = 0
            
            # Aplicar watershed
            markers_img = cv2.watershed(img, markers_img)
            img[markers_img == -1] = [0, 0, 255]  # Marcar bordas em vermelho
            
            cv2.imwrite(output_path, img)
        
        elif method.lower() == "felzenszwalb":
            # Segmentação usando algoritmo de Felzenszwalb
            scale = kwargs.get('scale', 100)
            sigma = kwargs.get('sigma', 0.5)
            min_size = kwargs.get('min_size', 50)
            
            img = np.array(Image.open(input_path))
            segments = segmentation.felzenszwalb(img, scale=scale, sigma=sigma, min_size=min_size)
            
            # Criar imagem segmentada
            segmented_img = color.label2rgb(segments, img, kind='avg')
            
            # Salvar resultado
            plt.imsave(output_path, segmented_img)
        
        else:
            raise ValueError(f"Método de segmentação '{method}' não suportado")
        
        return True
    
    except Exception as e:
        print(f"Erro ao segmentar imagem: {e}")
        return False

def histogram(input_path, output_path=None, channels=True):
    """
    Gera um histograma da imagem.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str, optional): Caminho para salvar o histograma como imagem
        channels (bool): Se True, gera histograma para cada canal de cor; se False, apenas para luminosidade
    
    Returns:
        dict: Dicionário com os dados do histograma ou None em caso de erro
    """
    try:
        img = cv2.imread(input_path)
        
        if channels and len(img.shape) == 3:  # Imagem colorida
            hist_data = {}
            color = ('b', 'g', 'r')
            
            plt.figure(figsize=(10, 6))
            for i, col in enumerate(color):
                hist = cv2.calcHist([img], [i], None, [256], [0, 256])
                hist_data[col] = hist.flatten().tolist()
                plt.plot(hist, color=col)
                plt.xlim([0, 256])
            
            plt.title('Histograma de Cores')
            plt.xlabel('Intensidade de Pixel')
            plt.ylabel('Número de Pixels')
            
        else:  # Imagem em escala de cinza ou forçar histograma de luminosidade
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img
                
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist_data = {'gray': hist.flatten().tolist()}
            
            plt.figure(figsize=(10, 6))
            plt.plot(hist, color='gray')
            plt.xlim([0, 256])
            plt.title('Histograma de Luminosidade')
            plt.xlabel('Intensidade de Pixel')
            plt.ylabel('Número de Pixels')
        
        if output_path:
            plt.savefig(output_path)
            plt.close()
        
        return hist_data
    
    except Exception as e:
        print(f"Erro ao gerar histograma: {e}")
        return None

def feature_detection(input_path, output_path, method="sift", **kwargs):
    """
    Detecta características (features) em uma imagem.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho para salvar a imagem com características detectadas
        method (str): Método de detecção ('sift', 'orb', 'harris')
        **kwargs: Parâmetros específicos para cada método
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        img = cv2.imread(input_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        result_img = img.copy()
        
        if method.lower() == "sift":
            # Detecção de características usando SIFT
            sift = cv2.SIFT_create()
            keypoints = sift.detect(gray, None)
            result_img = cv2.drawKeypoints(img, keypoints, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        
        elif method.lower() == "orb":
            # Detecção de características usando ORB
            orb = cv2.ORB_create()
            keypoints = orb.detect(gray, None)
            result_img = cv2.drawKeypoints(img, keypoints, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        
        elif method.lower() == "harris":
            # Detecção de cantos usando Harris
            block_size = kwargs.get('block_size', 2)
            aperture_size = kwargs.get('aperture_size', 3)
            k = kwargs.get('k', 0.04)
            
            # Detectar cantos
            corners = cv2.cornerHarris(gray, block_size, aperture_size, k)
            
            # Dilatar o resultado para marcar os cantos
            corners = cv2.dilate(corners, None)
            
            # Limiar para encontrar cantos
            threshold = 0.01 * corners.max()
            result_img[corners > threshold] = [0, 0, 255]
        
        else:
            raise ValueError(f"Método de detecção de características '{method}' não suportado")
        
        cv2.imwrite(output_path, result_img)
        return True
    
    except Exception as e:
        print(f"Erro ao detectar características: {e}")
        return False