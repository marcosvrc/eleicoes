# Apuração Presidente 2026 · 2º turno (Lula x Flávio Bolsonaro)

1. Deixe `index.html` e `servidor.py` na mesma pasta.
2. No terminal, dentro da pasta: `python3 servidor.py` (no Windows: `python servidor.py`).
3. Abra http://localhost:8000 no navegador.

O servidor descobre sozinho o código da eleição do 2º turno no arquivo de configuração do TSE
(`ele-c.json`) e repassa os resultados para a página, contornando o bloqueio de CORS.
O código em uso aparece no terminal e no rodapé da página.

Opções (variáveis de ambiente):
- `ELEICAO=<código> python3 servidor.py` força um código de eleição, caso a descoberta falhe.
- `TURNO=1 python3 servidor.py` volta a acompanhar o 1º turno.
- `PORTA=8080 python3 servidor.py` usa outra porta.

A página consulta o TSE a cada 10 segundos e mostra nome (`nmu`), percentual (`pvap`) e votos (`vap`)
dos dois candidatos, a diferença entre eles, as urnas apuradas e o gráfico da evolução.
O histórico do 2º turno fica salvo no navegador, separado do 1º; o botão "Limpar histórico" zera o gráfico.
Se algo falhar, a mensagem de erro aparece no rodapé e o JSON completo sai no console (F12).
