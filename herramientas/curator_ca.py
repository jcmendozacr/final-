"""Lanza un script con una lista de CA = certifi + almacén de Windows (Avast intercepta TLS).
Uso: python curator_ca.py <bundle.pem> <script.py> [args...]"""
import runpy, ssl, sys
from pathlib import Path
import certifi
bundle = Path(sys.argv[1])
if not bundle.exists():
    ctx = ssl.create_default_context()
    pems = [ssl.DER_cert_to_PEM_cert(c) for c in ctx.get_ca_certs(binary_form=True)]
    bundle.write_text(Path(certifi.where()).read_text(encoding="ascii") + "\n" + "".join(pems), encoding="ascii")
certifi.where = lambda: str(bundle)
import certifi.core
certifi.core.where = certifi.where
sys.argv = sys.argv[2:]
runpy.run_path(sys.argv[0], run_name="__main__")
