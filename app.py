from flask import Flask, request, send_file, Response, render_template
import pandas as pd
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/')
def home():
    return '''
    <h2>Atualizar Layout CNAB240</h2>
    <form method="POST" action="/atualizar" enctype="multipart/form-data">
        <label>Arquivo Layout Técnico CSV:</label><br>
        <input type="file" name="layout" accept=".csv" required><br><br>

        <label>Arquivo Atualizações CSV:</label><br>
        <input type="file" name="atualizacoes" accept=".csv" required><br><br>

        <button type="submit">Enviar e Atualizar</button>
    </form>
    '''

@app.route('/atualizar', methods=['POST'])
def atualizar():
    # Recebe os arquivos
    layout_file = request.files.get('layout')
    atualizacoes_file = request.files.get('atualizacoes')

    if not layout_file or not atualizacoes_file:
        return "Erro: arquivos não enviados corretamente", 400

    # Lê CSVs para DataFrames
    try:
        df_layout = pd.read_csv(layout_file)
        df_atualizacoes = pd.read_csv(atualizacoes_file)
    except Exception as e:
        return f"Erro ao ler arquivos CSV: {e}", 400

    # Verifica se as colunas necessárias estão presentes no df_atualizacoes
    col_necessarias = ['nova_data_vencimento', 'novo_valor_nominal']
    for c in col_necessarias:
        if c not in df_atualizacoes.columns:
            return f"Erro: arquivo de atualizações precisa conter a coluna '{c}'", 400

    # Número de operações
    num_operacoes = df_atualizacoes.shape[0]

    # Para cada operação (bloco de 12 colunas no layout)
    # iterar pelo df_layout atualizando C012 e C013 na posição correta

    # Encontrar as linhas do layout que contêm C012 e C013
    # considerando a coluna que identifica o campo (ex: 'Código')
    # e as colunas que representam dados para cada operação:
    # Exemplo: se layout horizontal, as colunas de dados são após as colunas iniciais

    # Assumindo que no df_layout:
    # - coluna 'Código' identifica o campo (C012 e C013)
    # - dados começam na coluna de índice 2 (posição 3 na planilha)
    # - cada operação ocupa 12 colunas sequenciais de dados

    codigo_col = '_c1'  # ajuste se necessário
    if codigo_col not in df_layout.columns:
        return f"Erro: layout não contém a coluna '{codigo_col}'", 400

    # Colunas que contém dados (começa na terceira coluna)
    col_data_start = 2

    for i in range(num_operacoes):
        # índice da coluna para a operação i (bloco de 12 colunas)
        start_col = col_data_start + i * 12

        # Atualizar linhas com Código == 'C012' e 'C013'
        mask_c012 = df_layout[codigo_col] == 'C012'
        mask_c013 = df_layout[codigo_col] == 'C013'

        # Atualiza campo Data de Vencimento (C012)
        if mask_c012.any():
            df_layout.loc[mask_c012, df_layout.columns[start_col]] = df_atualizacoes.loc[i, 'nova_data_vencimento']

        # Atualiza campo Valor Nominal (C013)
        if mask_c013.any():
            df_layout.loc[mask_c013, df_layout.columns[start_col]] = df_atualizacoes.loc[i, 'novo_valor_nominal']

    # Gera CSV atualizado em memória
    output = io.StringIO()
    df_layout.to_csv(output, index=False)
    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=layout_atualizado.csv"}
    )

if __name__ == "__main__":
    app.run(debug=True)
