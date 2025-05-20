import pandas as pd

class HeaderArquivo:
    def __init__(self, df):
        self.output = []
        for i in range(0, 24):
            valor = df['_c2'].iloc[i]
            tamanho = int(df['_c3'].iloc[i])
            self.output.append(self._formatar(valor, tamanho))

    def _formatar(self, valor, tamanho):
        if valor in ["BRANCOS", "Brancos"]:
            return ' ' * tamanho
        return f"{valor:0{tamanho}}"

    def __str__(self):
        return ''.join(self.output)


class HeaderLote:
    def __init__(self, df):
        self.output = []
        for i in range(0, 23):
            valor = df['_c8'].iloc[i]
            tamanho = int(df['_c9'].iloc[i])
            self.output.append(self._formatar(valor, tamanho))

    def _formatar(self, valor, tamanho):
        if valor in ["BRANCOS", "Brancos"]:
            return ' ' * tamanho
        return f"{valor:0{tamanho}}"

    def __str__(self):
        return ''.join(self.output)


class TrailerLote:
    def __init__(self, df):
        self.output = []
        for i in range(0, 15):
            valor = df['_c26'].iloc[i]
            tamanho = int(df['_c27'].iloc[i])
            self.output.append(self._formatar(valor, tamanho))

    def _formatar(self, valor, tamanho):
        if valor in ["BRANCOS", "Brancos"]:
            return ' ' * tamanho
        return f"{valor:0{tamanho}}"

    def __str__(self):
        return ''.join(self.output)


class TrailerArquivo:
    def __init__(self, df):
        self.output = []
        for i in range(0, 8):
            valor = df['_c32'].iloc[i]
            tamanho = int(df['_c33'].iloc[i])
            self.output.append(self._formatar(valor, tamanho))

    def _formatar(self, valor, tamanho):
        if valor in ["BRANCOS", "Brancos"]:
            return ' ' * tamanho
        return f"{valor:0{tamanho}}"

    def __str__(self):
        return ''.join(self.output)


class Segmento:
    def __init__(self, df, col_valor, col_tamanho):
        self.output = []
        for i in range(len(df)):
            valor = df[col_valor].iloc[i]
            raw_tamanho = df[col_tamanho].iloc[i]
            tamanho = 0 if raw_tamanho is None or pd.isna(raw_tamanho) else int(raw_tamanho)

            if valor in ["BRANCOS", "Brancos"]:
                formatted = ' ' * tamanho
            elif valor is None or pd.isna(valor):
                formatted = '0' * tamanho
            else:
                formatted = f"{valor:0{tamanho}}"

            self.output.append(formatted)

    def __str__(self):
        return ''.join(self.output)


def gerar_segmentos_pq(df2):
    colunas = df2.columns.tolist()
    bloco_tamanho = 12
    num_operacoes = len(colunas) // bloco_tamanho
    linhas = []

    for op in range(num_operacoes):
        base = op * bloco_tamanho
        col_valor_P = colunas[base + 2]
        col_tamanho_P = colunas[base + 3]
        col_valor_Q = colunas[base + 8]
        col_tamanho_Q = colunas[base + 9]

        segmento_P = Segmento(df2, col_valor_P, col_tamanho_P)
        segmento_Q = Segmento(df2, col_valor_Q, col_tamanho_Q)

        total = len(str(segmento_P)) + len(str(segmento_Q))
        if total < 240:
            segmento_P.output.append(' ' * (240 - total))  # completa a linha

        linhas.append(str(segmento_P))
        linhas.append(str(segmento_Q))

    return linhas


def gerar_header_e_lote(df1):
    return [
        str(HeaderArquivo(df1)),
        str(HeaderLote(df1))
    ]


def gerar_trailers(df1):
    return [
        str(TrailerLote(df1)),
        str(TrailerArquivo(df1))
    ]


def gerar_cnab(df1, df2):
    header_lote = gerar_header_e_lote(df1)
    segmentos = gerar_segmentos_pq(df2)
    trailers = gerar_trailers(df1)
    
    todas_linhas = header_lote + segmentos + trailers
    return '\n'.join(todas_linhas)
