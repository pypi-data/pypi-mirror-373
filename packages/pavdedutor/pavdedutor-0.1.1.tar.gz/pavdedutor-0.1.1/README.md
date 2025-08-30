# PavDedutor 

## Descrição
### O que é?
A `pavdedutor` é biblioteca python voltada para otimização do cálculo de valores deduzíveis de patologias de pavimentos **rígidos** com base nas disposições normativas da [DNIT 062/2004 PRO](https://www.gov.br/dnit/pt-br/assuntos/planejamento-e-pesquisa/ipr/coletanea-de-normas/coletanea-de-normas/procedimento-pro/dnit_062_2004_pro.pdf).

### Por que?
Entendendo a necessidade de automação dos processos manuais presentes na norma [DNIT 062/2004 PRO](https://www.gov.br/dnit/pt-br/assuntos/planejamento-e-pesquisa/ipr/coletanea-de-normas/coletanea-de-normas/procedimento-pro/dnit_062_2004_pro.pdf), a `pavdedutor` propõe a substituição da consulta manual aos *ábacos de valores de deduzíveis* pelo uso de funções rápidas e simples, a fim de reduzir drasticamente o tempo de análise de patologias. Assim, a `pavdedutor` encontra utilidade não só em trabalhos de engenharia ou geotecnologia, mas também nos campos de visão computacional e inteligência artificial, agindo como um molde normativo para as catalogações e, assim, oferecendo maior aderência aos critérios técnicos vigentes, garantindo que as análises automatizadas mantenham o rigor exigido em norma sem perder velocidade nas coletas.

![Exemplificação de fluxo](https://imgur.com/uPNOufj.png)

A biblioteca possibilita:
- Cálculo direto dos valores deduzíveis por tipo de patologia e tipo de pavimento;
- Cálculo de valor deduzível corrigido total automático por tipo de pavimento.

## Instalação

#### Instalação com pip
```bash
pip install pavdedutor
```

## Uso
#### Cálculo de valor deduzível unitário
```python
import pavdedutor as pav  # Importa a biblioteca

# Cálculo de valor deduzível
exemplo = pav.deduzivel(1, 'a', 30, 'rígido')  # Chama a função deduzivel passando: patologia 1, severidade 'a', densidade 30 e pavimento rígido
print(exemplo)  # Imprime o valor deduzível calculado
```

#### Cálculo de valor deduzível em lote
```python
import pavdedutor as pav  # Importa a biblioteca
import pandas as pd  # Importa a biblioteca pandas

# Criação de um dicionário com dados genéricos de patologias
dic_patologias = {
    'Patologias': [1, 2, 3, 4, 5, 6, 7, 8, 9],  # Lista de códigos de patologias
    'Severidades': ['a','b','m','a','b','m','a','b','m'],  # Severidades correspondentes
    'Densidades': [10, 20, 30, 10, 20, 30, 10, 20, 30],  # Densidades para cada patologia
    'Tipo de pavimento': ['rígido']*9,  # Tipo de pavimento (todos rígidos)
    'Número da amostra': [1, 1, 1, 2, 2, 2, 3, 3, 3]  # Identifica a qual amostra cada linha pertence
}

df = pd.DataFrame(dic_patologias)  # Cria um DataFrame a partir do dicionário

resultado = []  # Lista para armazenar os resultados

# Loop para calcular o valor deduzível de cada linha
for i in range(len(df)):
    resultado.append(pav.deduzivel(
        df.loc[i, 'Patologias'], # Nome da coluna com as patologias
        df.loc[i, 'Severidades'], # Nome da coluna com as severidades correspondentes
        df.loc[i, 'Densidades'], # Nome da coluna com as densidades correspondentes
        df.loc[i, 'Tipo de pavimento'] # Nome da coluna com os tipos de pavimentos
    )
)

df['Valores deduziveis'] = resultado  # Adiciona os valores deduzíveis calculados ao DataFrame

df  # Exibe o DataFrame final
```

#### Cálculo de valor deduzível corrigido total 
```python
import pavdedutor as pav  # Importa a biblioteca pavdedutor
import pandas as pd  # Importa a biblioteca pandas

# Criação de um dicionário com dados genéricos
dic_patologias = {
    'Patologias': [1, 2, 3],  # Códigos das patologias
    'Severidades': ['a','b','m'],  # Severidades correspondentes
    'Densidades': [10, 20, 30],  # Densidades para cada patologia
    'Tipo de pavimento': ['rígido']*3,  # Tipo de pavimento (todos rígidos)
    'Valores deduziveis': [54, 17, 39]  # Valores deduzíveis previamente calculados
}

df = pd.DataFrame(dic_patologias)  # Converte o dicionário em DataFrame

# Cálculo de valor deduzível total com correção por diversidade de patologias
exemplo = pav.deduzivel_total(
    df, # DataFrame com os dados genéricos
    'Patologias',  # Nome da coluna com os códigos das patologias
    'Valores deduziveis',  # Nome da coluna com os valores deduzíveis
    'rígido'  # Tipo de pavimento
)

print(exemplo)  # Exibe o valor deduzível total corrigido

```

#### Cálculo de valor deduzível corrigido total em lote
```python
import pavdedutor as pav  # Importa a biblioteca pavdedutor
import pandas as pd  # Importa a biblioteca pandas

# Criação do dicionário com dados simulados de patologias por amostra
dic_patologias = {
    'Patologias': [1, 2, 3, 4, 5, 6, 7, 8, 9],  # Códigos das patologias
    'Severidades': ['a','b','m','a','b','m','a','b','m'],  # Severidades correspondentes
    'Densidades': [10,20,30,10,20,30,10,20,30],  # Densidades para cada patologia
    'Tipo de pavimento': ['rígido']*9,  # Tipo de pavimento (todos rígidos)
    'Número da amostra': [1,1,1,2,2,2,3,3,3],  # Identificador da amostra
    'Valores deduzíveis': [54,17,39,16,2,10,18,7,7]  # Valores deduzíveis previamente calculados
}

df = pd.DataFrame(dic_patologias)  # Cria o DataFrame com os dados

resultado = []  # Lista para armazenar os resultados corrigidos

# Loop para calcular o valor deduzível total corrigido por amostra
for amostra in df['Número da amostra'].unique():
    
    resultado.append(pav.deduzivel_corrigido_total(
        df[df['Número da amostra'] == amostra],  # Filtra os dados da amostra atual
        'Patologias',  # Nome da coluna de patologias
        'Valores deduzíveis',  # Nome da coluna com os valores deduzíveis
        'rígido'  # Tipo de pavimento
    )
)

resultado  # Exibe os resultados finais corrigidos por amostra

```
#### Com os valores deduzíveis corrigidos, o usuário já pode obter o **ICP/IPC**
```python
import pandas as pd  # Importa a biblioteca pandas

amostras = [1, 2, 3]  # Lista com os números das amostras
resultado = [66, 22, 20]  # Lista com os valores deduzíveis corrigidos por amostra

tabela_final = dict(zip(amostras, resultado))  # Cria um dicionário associando cada amostra ao seu resultado

df_final = pd.DataFrame(tabela_final.items(), columns=['Amostra', 'VDC'])  # Converte em DataFrame com colunas Amostra e VDC
df_final['ICP'] = 100 - df_final['VDC']  # Calcula o ICP como 100 - VDC

df_final  # Exibe a tabela final com VDC e ICP por amostra
```

#### Desenvolvimento do projeto/Próximos passos
A biblioteca ainda está em processo de desenvolvimento, com novas funcionalidades a serem implementadas, assim como a aplicabilidade para **pavimentos flexíveis** também. Fique a vontade para me contatar e dar sua opnião sobre o projeto no meu [Linkedin](www.linkedin.com/in/wmoural), [GitHub](https://github.com/wmoural) ou [Email](pro.wmoura@gmail.com).


#### Licença
Copyright (c) 2025 Wellington Moura

O uso é fornecido sob a Licença do MIT.