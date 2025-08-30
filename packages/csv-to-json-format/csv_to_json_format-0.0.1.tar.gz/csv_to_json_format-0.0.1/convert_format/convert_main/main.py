from csv_to_json.csv_to_json import convert_csv_to_json

if __name__ == "__main__":
    # Exemplo de uso: crie um arquivo CSV de teste para usar aqui
    # Ex: 'data.csv'
    # nome;idade;cidade
    # Maria;30;São Paulo
    # João;25;Rio de Janeiro

    # Defina os caminhos dos arquivos
    input_csv = "csv_to_json\data.csv"
    output_json = "data.json"
    
    # Chama a função de conversão
    convert_csv_to_json(input_csv, output_json)