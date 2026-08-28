# ============================================================
# SERVIDOR LOCAL PARA TESTAR O JOGO
# ============================================================
#
# O index.html deste projeto roda o PyScript no MAIN THREAD
# (sem "worker"), então na maioria dos casos basta usar:
#
#     python -m http.server 8000
#
# Este servidor.py é um extra: ele adiciona os cabeçalhos
# Cross-Origin-Opener-Policy e Cross-Origin-Embedder-Policy,
# necessários apenas se você decidir trocar para o modo
# "worker" no <script type="py" ... worker>. Ele também
# funciona perfeitamente para o modo padrão (main thread).
#
# Como usar:
#     python servidor.py
#
# Depois abra no navegador:
#     http://localhost:8000
# ============================================================

import http.server
import socketserver

PORTA = 8000


class HandlerComIsolamento(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        super().end_headers()

    def log_message(self, formato, *args):
        # Log mais limpo no terminal
        print("[servidor] " + (formato % args))


def iniciar():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORTA), HandlerComIsolamento) as httpd:
        print("=" * 56)
        print(" O ENIGMA DA MANSÃO ABANDONADA — servidor local")
        print("=" * 56)
        print(f" Acesse em: http://localhost:{PORTA}")
        print(" Pressione CTRL+C para encerrar o servidor.")
        print("=" * 56)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[servidor] Encerrado.")


if __name__ == "__main__":
    iniciar()
