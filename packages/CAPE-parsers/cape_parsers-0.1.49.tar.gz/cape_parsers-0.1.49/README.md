# CAPE-parsers
CAPE core and community parsers

[![PyPI version](https://img.shields.io/pypi/v/CAPE-parsers)](https://pypi.org/project/CAPE-parsers/)

### Configs structure
```
CNCs: []
campaign: str
botnet: str
dga_seed: hex str
version: str
mutex: str
user_agent: str
build: str
cryptokey: str
cryptokey_type: str (algorithm). Ex: RC4, RSA public key. salsa20, (x)chacha20
raw: {any other data goes here}
```
* All CNC entries should be in URL format. aka `<schema>://<hostname>:<port>/<uri>`
    * Schema examples: `tcp://`, `ftp://`, `udp://`, `http(s)`, etc.
    * Old CAPE configs still have lack of this structures as most of them are dead families.
    * This CNC simplification make it easier to parse with tools like `tldextract` or `urlparse`
