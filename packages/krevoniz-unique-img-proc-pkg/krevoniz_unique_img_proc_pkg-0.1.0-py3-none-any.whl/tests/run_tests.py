import unittest
import os
import sys

# Adicionar o diretório pai ao path para importar o pacote
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Descobrir e executar todos os testes
if __name__ == '__main__':
    # Descobrir todos os testes no diretório atual
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(os.path.dirname(__file__))
    
    # Executar os testes
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Sair com código de erro se algum teste falhar
    sys.exit(not result.wasSuccessful())