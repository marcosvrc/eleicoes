#!/usr/bin/env python3
"""Servidor local: entrega o index.html e repassa as chamadas ao TSE (evita bloqueio de CORS).

Uso:  python3 servidor.py      depois abra http://localhost:8000

Por padrão acompanha o 2º turno de Presidente. O código da eleição é descoberto
automaticamente no arquivo de configuração do TSE (ele-c.json). Para forçar um código:
    ELEICAO=6258 python3 servidor.py       (substitua pelo código correto)
Para voltar ao 1º turno:
    TURNO=1 python3 servidor.py
"""
import http.server
import json
import os
import time
import urllib.request

ANO = os.environ.get("ANO", "2026")
TURNO = os.environ.get("TURNO", "2")
ELEICAO_FIXA = os.environ.get("ELEICAO", "").strip()
CARGO_PRESIDENTE = "1"
CONFIG_URL = "https://resultados.tse.jus.br/oficial/comum/config/ele-c.json"
PORTA = int(os.environ.get("PORTA", "8000"))
PASTA = os.path.dirname(os.path.abspath(__file__))
HEADERS = {"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"}

_cache = {"cd": None, "t": 0}
_fotos = {}


def baixar(url, timeout=15):
    req = urllib.request.Request(f"{url}?nocache={int(time.time() * 1000)}", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.status


def _eleicoes(obj):
    """Percorre o JSON de configuração e devolve todos os objetos de eleição (com 'cd' e 't')."""
    if isinstance(obj, list):
        for o in obj:
            yield from _eleicoes(o)
    elif isinstance(obj, dict):
        if "cd" in obj and "t" in obj:
            yield obj
        for v in obj.values():
            yield from _eleicoes(v)


def _tem_presidente(e):
    """True se a eleição tem o cargo Presidente (código 1) ou não informa cargos."""
    cargos = e.get("cp") or e.get("cargos")
    if not cargos:
        return True
    for c in cargos:
        if isinstance(c, dict) and (str(c.get("cd")) == CARGO_PRESIDENTE or "PRESIDENTE" == str(c.get("ds", "")).upper()):
            return True
    return False


def codigo_eleicao():
    """Código da eleição do turno escolhido (variável ELEICAO ou descoberto no ele-c.json, com cache de 10 min)."""
    if ELEICAO_FIXA:
        return ELEICAO_FIXA
    if _cache["cd"] and time.time() - _cache["t"] < 600:
        return _cache["cd"]
    corpo, _ = baixar(CONFIG_URL)
    config = json.loads(corpo)
    candidatas = [
        e for e in _eleicoes(config)
        if str(e.get("t")) == TURNO and ANO in json.dumps(e) and _tem_presidente(e)
    ]
    if not candidatas:
        raise RuntimeError(f"Eleição do {TURNO}º turno de {ANO} não encontrada em ele-c.json; "
                           f"defina o código com ELEICAO=<código> python3 servidor.py")
    # Eleição federal (Presidente) costuma ter o menor código entre as do turno
    cd = str(min(candidatas, key=lambda e: int(str(e["cd"])) if str(e["cd"]).isdigit() else 10**9)["cd"])
    _cache.update(cd=cd, t=time.time())
    print(time.strftime("%H:%M:%S"), f"Eleição do {TURNO}º turno encontrada: código {cd}")
    return cd


def url_resultado(cd):
    return f"https://resultados.tse.jus.br/oficial/ele{ANO}/{cd}/dados/br/br-c000{CARGO_PRESIDENTE}-e{int(cd):06d}-u.jws"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PASTA, **kwargs)

    def do_GET(self):
        if self.path.startswith("/foto/"):
            return self.foto()
        if not self.path.startswith("/tse"):
            return super().do_GET()
        cd = ""
        try:
            cd = codigo_eleicao()
            corpo, status = baixar(url_resultado(cd))
        except urllib.error.HTTPError as e:
            corpo, status = e.read() or f"TSE respondeu HTTP {e.code}".encode(), e.code
        except Exception as e:
            corpo, status = str(e).encode(), 502
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Eleicao", cd)
        self.send_header("X-Turno", TURNO)
        self.end_headers()
        self.wfile.write(corpo)

    def foto(self):
        """Foto do candidato no TSE: /foto/<sqcand> (guardada em memória depois da 1ª busca)."""
        sq = self.path.split("/foto/", 1)[1].split("?")[0]
        if not sq.isdigit():
            return self.send_error(400)
        try:
            if sq not in _fotos:
                cd = codigo_eleicao()
                req = urllib.request.Request(f"https://resultados.tse.jus.br/oficial/ele{ANO}/{cd}/fotos/br/{sq}.jpeg", headers=HEADERS)
                with urllib.request.urlopen(req, timeout=15) as r:
                    _fotos[sq] = r.read()
            corpo = _fotos[sq]
        except Exception:
            return self.send_error(404)
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Cache-Control", "max-age=3600")
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, fmt, *args):
        if args and "/tse" in str(args[0]):
            print(time.strftime("%H:%M:%S"), "TSE ->", args[1] if len(args) > 1 else "")


if __name__ == "__main__":
    origem = f"código fixo {ELEICAO_FIXA}" if ELEICAO_FIXA else "código descoberto no TSE"
    print(f"Presidente {ANO} · {TURNO}º turno ({origem})")
    print(f"Abra http://localhost:{PORTA} no navegador (Ctrl+C para parar)")
    http.server.ThreadingHTTPServer(("", PORTA), Handler).serve_forever()
