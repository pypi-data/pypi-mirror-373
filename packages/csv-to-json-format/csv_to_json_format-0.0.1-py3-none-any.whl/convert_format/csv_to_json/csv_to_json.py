import pandas as pd
import json

def convert_csv_to_json(csv_file_path, json_file_path):
    """
    Converte um arquivo CSV (UTF-8, delimitador ';') para JSON.

    Args:
        csv_file_path (str): O caminho para o arquivo CSV de entrada.
        json_file_path (str): O caminho para o arquivo JSON de saída.
    """
    try:
        # Lê o arquivo CSV com as especificações fornecidas
        df = pd.read_csv(csv_file_path, sep=';', encoding='utf-8')
        
        # Converte o DataFrame para uma lista de dicionários
        data = df.to_dict(orient='records')
        
        # Salva a lista de dicionários em um arquivo JSON
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"Conversão concluída! O arquivo JSON foi salvo em: {json_file_path}")
        
    except FileNotFoundError:
        print(f"Erro: O arquivo CSV não foi encontrado em '{csv_file_path}'.")
    except Exception as e:
        print(f"Ocorreu um erro durante a conversão: {e}")