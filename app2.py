from flask import Flask, render_template, request, send_file
import pandas as pd
from gerador_cnab import gerar_cnab  # A função que gera o CNAB240
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gerar', methods=['POST'])
def gerar():
    # Recebe os dois arquivos CSV
    arquivo_csv_1 = request.files['arquivo_csv_1']
    arquivo_csv_2 = request.files['arquivo_csv_2']
    
    if not arquivo_csv_1 or not arquivo_csv_2:
        return 'Ambos os arquivos CSV são necessários', 400

    # Processa os dois CSVs
    df1 = pd.read_csv(arquivo_csv_1) if arquivo_csv_1 and arquivo_csv_1.filename else None  # O arquivo com os Segmentos P/Q
    df2 = pd.read_csv(arquivo_csv_2)  # O arquivo com os dados CNAB

    # Chama a função que gera o CNAB240
    conteudo_cnab = gerar_cnab(df1, df2)

    # Cria um buffer para armazenar o arquivo gerado
    buffer = io.BytesIO()
    buffer.write(conteudo_cnab.encode('utf-8'))
    buffer.seek(0)

    # Retorna o arquivo gerado para o download
    return send_file(
        buffer,
        as_attachment=True,
        download_name='cnab240_combinado.txt',
        mimetype='text/plain'
    )

if __name__ == '__main__':
    app.run(debug=True)
