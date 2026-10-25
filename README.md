# Apuração Presidente 2026 · 2º turno

Página para acompanhar ao vivo a apuração do 2º turno da eleição para Presidente de 2026
(Lula x Flávio Bolsonaro), com os dados oficiais do TSE.

## O que a página mostra

- Nome, foto, percentual e votos de cada candidato
- Diferença de votos e de pontos percentuais entre os dois
- Percentual de urnas apuradas
- Gráfico da evolução da apuração, com histórico salvo no navegador (botão "Limpar histórico" zera o gráfico)
- Botão "Atualizar agora" para consultar na hora, sem esperar o intervalo

## Como funciona

```
navegador (index.html)  --a cada 10 s-->  servidor.py (localhost:8000)  -->  resultados.tse.jus.br
```

- `index.html`: a página. Consulta o servidor local, decodifica o resultado e desenha os números e o gráfico (Chart.js).
- `servidor.py`: servidor local em Python, só com a biblioteca padrão. Entrega a página e repassa as chamadas ao TSE,
  contornando o bloqueio de CORS do navegador. Descobre sozinho o código da eleição no arquivo de configuração
  do TSE (`ele-c.json`, guardado por 10 minutos) e guarda as fotos dos candidatos em memória.

## Como rodar

Requisito: Python 3.

```bash
git clone https://github.com/marcosvrc/eleicoes.git
cd eleicoes
python3 servidor.py
```

Abra http://localhost:8000 no navegador. Para parar, use Ctrl+C.

A página precisa ser aberta pelo servidor; abrir o `index.html` direto do arquivo não funciona.

### Opções do servidor (variáveis de ambiente)

| Variável  | Padrão              | Exemplo                          | Para que serve                                   |
|-----------|---------------------|----------------------------------|--------------------------------------------------|
| `PORTA`   | `8000`              | `PORTA=8080 python3 servidor.py` | Usa outra porta                                  |
| `TURNO`   | `2`                 | `TURNO=1 python3 servidor.py`    | Acompanha o 1º turno                             |
| `ELEICAO` | descoberto no TSE   | `ELEICAO=6258 python3 servidor.py` | Força o código da eleição, se a descoberta falhar |
| `ANO`     | `2026`              | `ANO=2026 python3 servidor.py`   | Ano da eleição                                   |

O código da eleição em uso aparece no terminal e no rodapé da página.

## Ajustar o tempo entre as chamadas

Por padrão a página consulta o TSE a cada **10 segundos**. Para mudar, edite a constante
`INTERVALO_MS` no início do `<script>` do `index.html` (valor em milissegundos):

```js
const INTERVALO_MS = 10000;            // 10 segundos (padrão)
const INTERVALO_MS = 30 * 1000;        // 30 segundos
const INTERVALO_MS = 5 * 60 * 1000;    // 5 minutos (ex.: apuração suspensa)
```

Atualize também o texto do rodapé, logo acima, para não ficar desatualizado:

```html
<span>Fonte: TSE<span id="eleicao-txt"></span>. Atualiza sozinho a cada 10 segundos.</span>
```

Depois é só recarregar a página no navegador (F5); não precisa reiniciar o `servidor.py`.

Dicas:
- O TSE atualiza os dados mais ou menos a cada 10 segundos; intervalos menores não trazem dados mais novos
  e só aumentam o número de chamadas.
- Cada aba aberta faz suas próprias chamadas. Com duas abas abertas, o terminal mostra duas linhas `TSE -> 200`
  a cada intervalo; mantenha só uma aberta.

## Problemas comuns

- **Erro no rodapé da página**: a mensagem explica o que falhou, e o JSON completo sai no console do navegador (F12).
- **"Eleição não encontrada em ele-c.json"**: o TSE ainda não publicou a eleição ou mudou o formato;
  rode com `ELEICAO=<código> python3 servidor.py`.
- **Porta em uso**: rode com outra porta, por exemplo `PORTA=8080 python3 servidor.py`.

## Arquivos

| Arquivo        | Descrição                                   |
|----------------|---------------------------------------------|
| `index.html`   | Página da apuração                          |
| `servidor.py`  | Servidor local e repasse das chamadas ao TSE |
| `LEIAME.md`    | Instruções rápidas de uso e de git          |
| `.gitignore`   | Deixa de fora `__pycache__/` e as cópias `*.backup-*` |
