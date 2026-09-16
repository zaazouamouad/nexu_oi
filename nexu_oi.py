#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║                     NEXU CODE  v3.0                          ║
║             Ultimate Encrypt / Decrypt Suite                 ║
║             Developed by: zaazouamouad                       ║
╚══════════════════════════════════════════════════════════════╝
"""

import argparse
import base64
import datetime
import hashlib
import os
import re
import socket
import subprocess
import sys
import zlib

# ── Optional deps ─────────────────────────────────────────────
try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

try:
    import qrcode
    HAS_QRGEN = True
except ImportError:
    HAS_QRGEN = False

try:
    from pyzbar.pyzbar import decode as qr_decode
    from PIL import Image
    HAS_QRREAD = True
except ImportError:
    HAS_QRREAD = False

try:
    import readline
    HAS_READLINE = True
except ImportError:
    HAS_READLINE = False

# ═══════════════════════════════════════════════════════════════
#  THEMES
# ═══════════════════════════════════════════════════════════════
THEMES = {
    "default": {"main": "\033[38;5;214m", "accent": "\033[93m"},
    "matrix":  {"main": "\033[92m",       "accent": "\033[32m"},
    "hacker":  {"main": "\033[91m",       "accent": "\033[31m"},
    "ice":     {"main": "\033[96m",       "accent": "\033[36m"},
    "purple":  {"main": "\033[95m",       "accent": "\033[35m"},
}
CURRENT_THEME = "default"

GREEN = "\033[92m"; RED = "\033[91m"; YELLOW = "\033[93m"
DIM   = "\033[2m";  BOLD = "\033[1m"; RESET  = "\033[0m"


def _c():
    return THEMES.get(CURRENT_THEME, THEMES["default"])


# ═══════════════════════════════════════════════════════════════
#  CODEBOOK
# ═══════════════════════════════════════════════════════════════
_BASE_CODEBOOK = {
    'A': '6755858833636', 'B': '85885858',      'C': '85858585',
    'D': '77676555',      'E': '8760021445',    'F': '0865789765',
    'G': '0008765',       'H': '668986444',     'I': '754332789',
    'J': '752100754',     'K': '875433478',     'L': '09644446754',
    'M': '09544987',      'N': '97656899600',   'O': '765567887655',
    'P': '8765548998655', 'Q': '7765688865667', 'R': '8768766787655',
    'S': '76458765444',   'T': '8654677899',    'U': '77554321100',
    'V': '7644478888',    'W': '76112363648040','X': '661337480404',
    'Y': '61782929200000','Z': '6363647849449949',

    'a': '9081726354453', 'b': '1122334455668', 'c': '7766554433221',
    'd': '3141592653589', 'e': '2718281828459', 'f': '1618033988749',
    'g': '1414213562373', 'h': '1732050807568', 'i': '2236067977499',
    'j': '5772156649015', 'k': '1234567890123', 'l': '9876543210987',
    'm': '5555555555555', 'n': '2468135790246', 'o': '1357924680135',
    'p': '1928374655647', 'q': '7584936201849', 'r': '3029184756392',
    's': '6473829105647', 't': '8172635445362', 'u': '9182736455463',
    'v': '5647382910645', 'w': '1231231231231', 'x': '4564564564564',
    'y': '7897897897897', 'z': '3213213213213',

    'أ': '4674480202938366363',   'ب': '747484020929233773',
    'ت': '7379200237636364738383','ث': '373839200293837764646447',
    'ج': '1102983737476474737364663','ح': '83736464744774467464774',
    'خ': '747747474477474744774477','د': '47477474747447477474477474',
    'ذ': '4747747474747447474747747474',
    'ر': '47474748488484848484858585857585',
    'ز': '577585855858558858585756363535352',
    'س': '12837467400193737646688','ش': '26263537833993633903',
    'ص': '112838490450857447474774','ض': '6474940209283744443828',
    'ط': '737484930302923837737373','ظ': '3774489493992827263636363737',
    'ع': '73747483833873373737373777337','غ': '373737373773727272723763366363',
    'ف': '7373737472772010283747464646464','ق': '12737749404019283636373938373737',
    'ك': '276363748394774748829293938373','ل': '733763637372827272636363636363',
    'م': '27728383837336638282376363','ن': '27269100182626372929282727',
    'ه': '263663737383837373737383838','و': '7447839392837363636288283766',
    'ي': '2737637192827626262627282827262',

    '1': '@@@$#+(#()#','2': '++@$@&#-#?:;:;"','3': '!"!"!-#-#-$-+#+#+#;',
    '4': '@#&&#-#-$-$?";:$:','5': '+#-#-$;$;$+$-#;#;;#-##',
    '6': '-#+$+$-$&#&#-#-$:-$-$-$;$','7': '#-#-#-+#+#-#&#&#&$+$;$-$-$;',
    '8': '#&#&#-#$-*--$-$+$$-$;$$-";$+($+++#',
    '9': '#-#--&#&#&#&$--$$--*-$-$-$-$--$-$',
    '0': '@&#--#+@;#-$+$;-_"+$:$-$+_-"-"+""',

    '!': '~P01P~','@': '~P02P~','#': '~P03P~','$': '~P04P~',
    '%': '~P05P~','^': '~P06P~','&': '~P07P~','*': '~P08P~',
    '(': '~P09P~',')': '~P10P~','-': '~P11P~','_': '~P12P~',
    '+': '~P13P~','=': '~P14P~','[': '~P15P~',']': '~P16P~',
    '{': '~P17P~','}': '~P18P~','\\': '~P19P~','|': '~P20P~',
    ';': '~P21P~',':': '~P22P~',"'": '~P23P~','"': '~P24P~',
    ',': '~P25P~','.': '~P26P~','<': '~P27P~','>': '~P28P~',
    '/': '~P29P~','?': '~P30P~','`': '~P31P~','~': '~P32P~',

    ' ': '|'
}


# ═══════════════════════════════════════════════════════════════
#  PASSWORD-BASED CODEBOOK ROTATION
# ═══════════════════════════════════════════════════════════════
def get_codebook(password=None):
    if not password:
        return dict(_BASE_CODEBOOK)
    h = int(hashlib.sha256(password.encode('utf-8')).hexdigest(), 16)
    items = sorted(_BASE_CODEBOOK.items())
    shift = h % len(items)
    rotated = items[shift:] + items[:shift]
    return dict(rotated)


def build_reverse(codebook):
    rev = {}
    for k, v in codebook.items():
        if v in rev:
            raise ValueError(f"Collision: {v!r}")
        rev[v] = k
    return rev


# ═══════════════════════════════════════════════════════════════
#  CORE NEXU
# ═══════════════════════════════════════════════════════════════
def nexu_encrypt(text, password=None):
    cb = get_codebook(password)
    return ' '.join(cb.get(ch, ch) for ch in text)


def nexu_decrypt(cipher, password=None, strict=False):
    cb = get_codebook(password)
    rev = build_reverse(cb)
    out = []
    for tok in cipher.split():
        if tok in rev:
            out.append(rev[tok])
        elif strict:
            raise ValueError(f"Unknown token: {tok!r}")
        else:
            out.append(tok)
    return ''.join(out)


# ═══════════════════════════════════════════════════════════════
#  AES LAYER (Optional)
# ═══════════════════════════════════════════════════════════════
def aes_encrypt(text, password):
    if not HAS_CRYPTO:
        raise RuntimeError("cryptography not installed")
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                     salt=salt, iterations=390000)
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    token = Fernet(key).encrypt(text.encode())
    return base64.urlsafe_b64encode(salt + token).decode()


def aes_decrypt(payload, password):
    if not HAS_CRYPTO:
        raise RuntimeError("cryptography not installed")
    raw = base64.urlsafe_b64decode(payload.encode())
    salt, token = raw[:16], raw[16:]
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                     salt=salt, iterations=390000)
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    try:
        return Fernet(key).decrypt(token).decode()
    except InvalidToken:
        raise ValueError("Wrong password or corrupted data")


# ═══════════════════════════════════════════════════════════════
#  BASE64 + COMPRESS + CHECKSUM
# ═══════════════════════════════════════════════════════════════
def b64_enc(text):
    return base64.b64encode(text.encode('utf-8')).decode('ascii')


def b64_dec(text):
    return base64.b64decode(text, validate=True).decode('utf-8')


def compress(text):
    return base64.b64encode(zlib.compress(text.encode('utf-8'))).decode()


def decompress(text):
    return zlib.decompress(base64.b64decode(text)).decode('utf-8')


def checksum(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


# ═══════════════════════════════════════════════════════════════
#  FILE I/O
# ═══════════════════════════════════════════════════════════════
def encrypt_file(inp, out=None, password=None, use_b64=False,
                 use_compress=False, use_checksum=True):
    with open(inp, 'r', encoding='utf-8') as f:
        data = f.read()

    payload = nexu_encrypt(data, password)
    if use_compress:
        payload = compress(payload)
    if use_b64:
        payload = b64_enc(payload)

    header = ""
    if use_checksum:
        header = f"#NEXU:v3:sha256={checksum(data)}\n"

    out = out or (inp + ".nexu")
    with open(out, 'w', encoding='utf-8') as f:
        f.write(header + payload)
    return out


def decrypt_file(inp, out=None, password=None, use_b64=False,
                 use_compress=False, verify=True):
    with open(inp, 'r', encoding='utf-8') as f:
        raw = f.read()

    expected_hash = None
    if raw.startswith("#NEXU:v3:"):
        line, raw = raw.split('\n', 1)
        m = re.search(r'sha256=([0-9a-f]+)', line)
        if m:
            expected_hash = m.group(1)

    payload = raw.strip()
    if use_b64:
        payload = b64_dec(payload)
    if use_compress:
        payload = decompress(payload)

    plain = nexu_decrypt(payload, password, strict=True)

    if verify and expected_hash and checksum(plain) != expected_hash:
        raise ValueError("Checksum mismatch — file tampered!")

    if out is None:
        out = inp[:-5] if inp.endswith(".nexu") else (inp + ".dec")
    with open(out, 'w', encoding='utf-8') as f:
        f.write(plain)
    return out


def batch_encrypt(folder, password=None):
    count = 0
    for root, _, files in os.walk(folder):
        for name in files:
            if name.endswith(".nexu"):
                continue
            path = os.path.join(root, name)
            try:
                encrypt_file(path, password=password)
                count += 1
            except Exception as e:
                print(f"{RED}[!] {path}: {e}{RESET}")
    return count


# ═══════════════════════════════════════════════════════════════
#  CLIPBOARD
# ═══════════════════════════════════════════════════════════════
def to_clipboard(text):
    for tool in (['termux-clipboard-set'], ['xclip', '-selection', 'clipboard'],
                 ['xsel', '--clipboard', '--input'], ['pbcopy']):
        try:
            subprocess.run(tool, input=text.encode(), check=True,
                           timeout=2, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            return True
        except Exception:
            continue
    return False


# ═══════════════════════════════════════════════════════════════
#  LOGGING
# ═══════════════════════════════════════════════════════════════
LOG_FILE = "nexu.log"


def log_op(action, inp, out):
    try:
        ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        i = inp[:60] + ('…' if len(inp) > 60 else '')
        o = out[:60] + ('…' if len(out) > 60 else '')
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{ts}] {action:12s} | IN: {i!r} | OUT: {o!r}\n")
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════
#  QR CODE
# ═══════════════════════════════════════════════════════════════
def qr_encode(text, out="nexu_qr.png"):
    if not HAS_QRGEN:
        raise RuntimeError("qrcode not installed: pip install qrcode[pil]")
    img = qrcode.make(text)
    img.save(out)
    return out


def qr_decode(path):
    if not HAS_QRREAD:
        raise RuntimeError("pyzbar/Pillow not installed")
    results = qr_decode(Image.open(path))
    if not results:
        raise ValueError("No QR found")
    return results[0].data.decode()


# ═══════════════════════════════════════════════════════════════
#  STEGANOGRAPHY
# ═══════════════════════════════════════════════════════════════
def hide_in_image(image_path, secret, out="stego.png"):
    if not HAS_QRREAD:
        raise RuntimeError("Pillow not installed: pip install pillow")
    img = Image.open(image_path).convert('RGB')
    data = secret.encode() + b'\x00\x00\x00'
    bits = ''.join(f'{b:08b}' for b in data)
    pixels = list(img.getdata())
    if len(bits) > len(pixels):
        raise ValueError("Image too small for payload")
    new = []
    for i, (r, g, b) in enumerate(pixels):
        if i < len(bits):
            r = (r & ~1) | int(bits[i])
        new.append((r, g, b))
    img.putdata(new)
    img.save(out)
    return out


def reveal_from_image(image_path):
    if not HAS_QRREAD:
        raise RuntimeError("Pillow not installed")
    img = Image.open(image_path).convert('RGB')
    bits = ''.join(str(p[0] & 1) for p in img.getdata())
    chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits) - 7, 8)]
    text = ''.join(chars)
    return text.split('\x00\x00\x00', 1)[0]


# ═══════════════════════════════════════════════════════════════
#  NETWORK
# ═══════════════════════════════════════════════════════════════
def net_send(host, port, message, password=None):
    payload = nexu_encrypt(message, password).encode()
    s = socket.socket()
    s.connect((host, port))
    s.sendall(payload)
    s.close()


def net_recv(port, password=None):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', port))
    s.listen(1)
    print(f"{GREEN}[+] Listening on :{port}...{RESET}")
    conn, addr = s.accept()
    data = conn.recv(1 << 20).decode()
    conn.close()
    s.close()
    return addr, nexu_decrypt(data, password, strict=False)


# ═══════════════════════════════════════════════════════════════
#  BANNER
# ═══════════════════════════════════════════════════════════════
def show():
    th = _c()
    logo = r"""
 ███╗   ██╗███████╗██╗  ██╗██╗   ██╗      ██████╗ ██╗
 ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║     ██╔═══██╗██║
 ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║     ██║   ██║██║
 ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║     ██║   ██║██║
 ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝     ╚██████╔╝██║
 ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝       ╚═════╝ ╚═╝
"""
    print(f"{th['main']}{BOLD}{logo}{RESET}")
    print(f"{th['accent']}{BOLD}     Developed by: zaazouamouad{RESET}")
    print(f"{DIM}     v3.0 | Nexu · AES · QR · Stego · Net · GUI · Batch{RESET}")


# ═══════════════════════════════════════════════════════════════
#  INTERACTIVE
# ═══════════════════════════════════════════════════════════════
def interactive(password=None):
    if HAS_READLINE:
        hist = os.path.expanduser("~/.nexu_history")
        try:
            readline.read_history_file(hist)
        except Exception:
            pass

    th = _c()
    print(f"{th['accent']}{'-' * 60}{RESET}")
    print(f"  {YELLOW}.pass <pw>{RESET} set password   {YELLOW}.pass off{RESET} clear")
    print(f"  {YELLOW}.b64 on/off{RESET}   {YELLOW}.clip on/off{RESET}   "
          f"{YELLOW}.theme <name>{RESET}")
    print(f"  {YELLOW}exit{RESET} quit")
    print(f"{th['accent']}{'-' * 60}{RESET}")

    b64, clip = False, False
    while True:
        try:
            ui = input(f"\n{th['main']}{BOLD}NEXU{RESET} {DIM}>{RESET} ")
        except (EOFError, KeyboardInterrupt):
            print(f"\n{YELLOW}[!] Bye.{RESET}")
            break

        cmd = ui.strip()
        if not cmd:
            continue
        low = cmd.lower()

        if low in ('exit', 'quit', 'q'):
            if HAS_READLINE:
                try:
                    readline.write_history_file(hist)
                except Exception:
                    pass
            print(f"{GREEN}[+] Goodbye.{RESET}")
            break
        if low.startswith('.pass '):
            v = cmd[6:].strip()
            password = None if v == 'off' else v
            print(f"{GREEN}[+] password: {'set' if password else 'cleared'}{RESET}")
            continue
        if low == '.b64 on':  b64 = True;  print(f"{GREEN}[+] b64 ON{RESET}"); continue
        if low == '.b64 off': b64 = False; print(f"{YELLOW}[+] b64 OFF{RESET}"); continue
        if low == '.clip on': clip = True; print(f"{GREEN}[+] clip ON{RESET}"); continue
        if low == '.clip off':clip = False;print(f"{YELLOW}[+] clip OFF{RESET}"); continue
        if low.startswith('.theme '):
            t = cmd[7:].strip()
            if t in THEMES:
                globals()['CURRENT_THEME'] = t
                print(f"{GREEN}[+] theme: {t}{RESET}")
            else:
                print(f"{RED}[!] available: {', '.join(THEMES)}{RESET}")
            continue

        try:
            tokens = cmd.split()
            hits = sum(1 for t in tokens if t in build_reverse(get_codebook(password)))
            if hits / max(len(tokens), 1) > 0.5:
                out = nexu_decrypt(cmd, password)
                act = 'DECRYPT'
            else:
                out = nexu_encrypt(cmd, password)
                act = 'ENCRYPT'
            if b64:
                out = b64_enc(out) if act == 'ENCRYPT' else b64_dec(out)
            print(f"{GREEN}[OUT]{RESET} {out}")
            log_op(act, cmd, out)
            if clip and to_clipboard(out):
                print(f"{DIM}      (copied){RESET}")
        except Exception as e:
            print(f"{RED}[ERR]{RESET} {e}")


# ═══════════════════════════════════════════════════════════════
#  GUI
# ═══════════════════════════════════════════════════════════════
def gui():
    import tkinter as tk
    from tkinter import scrolledtext, messagebox

    root = tk.Tk()
    root.title("NEXU CODE v3.0")
    root.geometry("700x520")
    root.configure(bg="#111")

    tk.Label(root, text="NEXU CODE", font=("Courier", 20, "bold"),
             fg="#ffb84d", bg="#111").pack(pady=8)

    tk.Label(root, text="Password (optional):", fg="#eee", bg="#111").pack()
    pw = tk.Entry(root, show="*", width=40)
    pw.pack(pady=4)

    txt = scrolledtext.ScrolledText(root, height=10, bg="#1a1a1a",
                                    fg="#0f0", insertbackground="#0f0")
    txt.pack(fill="both", expand=True, padx=10, pady=8)

    out = scrolledtext.ScrolledText(root, height=8, bg="#1a1a1a",
                                    fg="#ffb84d", insertbackground="#ffb84d")
    out.pack(fill="both", expand=True, padx=10)

    def do_enc():
        try:
            out.delete("1.0", "end")
            out.insert("end", nexu_encrypt(txt.get("1.0", "end-1c").strip(),
                                           pw.get() or None))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def do_dec():
        try:
            out.delete("1.0", "end")
            out.insert("end", nexu_decrypt(txt.get("1.0", "end-1c").strip(),
                                           pw.get() or None))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def do_copy():
        root.clipboard_clear()
        root.clipboard_append(out.get("1.0", "end-1c"))

    bar = tk.Frame(root, bg="#111"); bar.pack(pady=6)
    for label, cmd, color in (("Encrypt", do_enc, "#ffb84d"),
                              ("Decrypt", do_dec, "#4dff88"),
                              ("Copy",    do_copy,"#4db8ff")):
        tk.Button(bar, text=label, command=cmd, bg=color, fg="#000",
                  width=10, font=("Courier", 10, "bold")).pack(side="left", padx=4)

    root.mainloop()


# ═══════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════
def build_parser():
    p = argparse.ArgumentParser(
        prog='nexu',
        description=f'NEXU CODE v3.0 — Ultimate Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nexu                                   Interactive
  nexu enc "Hello World"                 Encrypt text
  nexu dec "<cipher>"                    Decrypt text
  nexu enc "text" -p secret              With password
  nexu enc -f notes.txt                  Encrypt file -> notes.txt.nexu
  nexu dec -f notes.txt.nexu             Decrypt file
  nexu aes-enc "text" -p pw              AES-256 layer
  nexu aes-dec "<payload>" -p pw
  nexu batch ./docs -p pw                Encrypt all files in folder
  nexu qr-enc "cipher" -o out.png        QR encode
  nexu qr-dec out.png                    QR decode
  nexu hide cover.png "secret" -o st.png Hide text in image
  nexu reveal st.png                     Reveal text from image
  nexu send 192.168.1.5:9999 "msg"       Send over network
  nexu recv 9999                         Receive over network
  nexu gui                               Launch GUI
  nexu test                              Run self-tests
""")

    p.add_argument('-p', '--password', default=None, help='Password')
    p.add_argument('-q', '--quiet', action='store_true', help='No banner')
    p.add_argument('-t', '--theme', choices=list(THEMES), default='default')
    p.add_argument('--b64', action='store_true', help='Base64 wrapper')
    p.add_argument('--compress', action='store_true', help='zlib compress')
    p.add_argument('-c', '--clipboard', action='store_true', help='Copy result')
    p.add_argument('-v', '--version', action='version',
                   version='NEXU CODE v3.0')

    sub = p.add_subparsers(dest='cmd')

    # enc / dec
    for name, help_ in (('enc', 'Encrypt'), ('dec', 'Decrypt')):
        sp = sub.add_parser(name, help=help_)
        sp.add_argument('text', nargs='?', default=None)
        sp.add_argument('-f', '--file')
        sp.add_argument('-o', '--output')

    # aes
    sub.add_parser('aes-enc', help='AES-256 encrypt').add_argument('text')
    sub.add_parser('aes-dec', help='AES-256 decrypt').add_argument('text')

    # batch
    b = sub.add_parser('batch', help='Encrypt folder')
    b.add_argument('folder')

    # QR
    qr_e = sub.add_parser('qr-enc'); qr_e.add_argument('text'); qr_e.add_argument('-o', '--output', default='nexu_qr.png')
    qr_d = sub.add_parser('qr-dec'); qr_d.add_argument('image')

    # Stego
    h = sub.add_parser('hide')
    h.add_argument('image'); h.add_argument('secret'); h.add_argument('-o', '--output', default='stego.png')
    r = sub.add_parser('reveal'); r.add_argument('image')

    # Network
    s = sub.add_parser('send'); s.add_argument('target'); s.add_argument('message')
    rc = sub.add_parser('recv'); rc.add_argument('port', type=int)

    # Extra
    sub.add_parser('gui')
    sub.add_parser('test')
    sub.add_parser('interactive')

    return p


# ═══════════════════════════════════════════════════════════════
#  SELF-TESTS
# ═══════════════════════════════════════════════════════════════
def run_tests():
    tests = []

    def t(name, fn):
        try:
            fn(); tests.append((name, True, None))
        except Exception as e:
            tests.append((name, False, str(e)))

    t("roundtrip upper",   lambda: (_ for _ in ()).throw(AssertionError())
        if nexu_decrypt(nexu_encrypt("HELLO")) != "HELLO" else None)
    t("roundtrip lower",   lambda: None if nexu_decrypt(nexu_encrypt("hello")) == "hello" else (_ for _ in ()).throw(AssertionError()))
    t("roundtrip arabic",  lambda: None if nexu_decrypt(nexu_encrypt("سلام")) == "سلام" else (_ for _ in ()).throw(AssertionError()))
    t("roundtrip punct",   lambda: None if nexu_decrypt(nexu_encrypt("Hi, World!")) == "Hi, World!" else (_ for _ in ()).throw(AssertionError()))
    t("password differs",  lambda: None if nexu_encrypt("A") != nexu_encrypt("A", "pw") else (_ for _ in ()).throw(AssertionError()))
    t("password roundtrip",lambda: None if nexu_decrypt(nexu_encrypt("Secret", "pw"), "pw") == "Secret" else (_ for _ in ()).throw(AssertionError()))
    t("b64 roundtrip",     lambda: None if b64_dec(b64_enc("abc")) == "abc" else (_ for _ in ()).throw(AssertionError()))
    t("compress roundtrip",lambda: None if decompress(compress("hello" * 100)) == "hello" * 100 else (_ for _ in ()).throw(AssertionError()))
    t("checksum stable",   lambda: None if checksum("x") == checksum("x") else (_ for _ in ()).throw(AssertionError()))

    if HAS_CRYPTO:
        t("aes roundtrip", lambda: None if aes_decrypt(aes_encrypt("top secret", "pw"), "pw") == "top secret" else (_ for _ in ()).throw(AssertionError()))

    print(f"\n{BOLD}NEXU CODE Self-Tests{RESET}\n" + "-" * 40)
    ok = 0
    for name, passed, err in tests:
        if passed:
            print(f"{GREEN}  ✓ {name}{RESET}"); ok += 1
        else:
            print(f"{RED}  ✗ {name} — {err}{RESET}")
    print("-" * 40)
    print(f"{BOLD}{ok}/{len(tests)} passed{RESET}")
    return 0 if ok == len(tests) else 1


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    global CURRENT_THEME
    parser = build_parser()
    args = parser.parse_args()
    CURRENT_THEME = args.theme

    if not args.quiet:
        show()

    pw = args.password
    b64 = args.b64
    comp = args.compress
    clip = args.clipboard

    # ── No subcommand → interactive ───────────────────────────
    if not args.cmd:
        interactive(password=pw)
        return

    c = args.cmd

    # ── enc / dec ─────────────────────────────────────────────
    if c in ('enc', 'dec'):
        if args.file:
            try:
                if c == 'enc':
                    out = encrypt_file(args.file, args.output, pw, b64, comp)
                    print(f"{GREEN}[+] Encrypted →{RESET} {out}")
                else:
                    out = decrypt_file(args.file, args.output, pw, b64, comp)
                    print(f"{GREEN}[+] Decrypted →{RESET} {out}")
                if clip:
                    with open(out, encoding='utf-8') as f:
                        to_clipboard(f.read())
            except Exception as e:
                print(f"{RED}[ERR]{RESET} {e}"); sys.exit(1)
        elif args.text:
            try:
                if c == 'enc':
                    out = nexu_encrypt(args.text, pw)
                    if comp: out = compress(out)
                    if b64:  out = b64_enc(out)
                else:
                    tmp = args.text
                    if b64:  tmp = b64_dec(tmp)
                    if comp: tmp = decompress(tmp)
                    out = nexu_decrypt(tmp, pw)
                print(f"{GREEN}[OUT]{RESET} {out}")
                log_op(c.upper(), args.text, out)
                if clip and to_clipboard(out):
                    print(f"{DIM}[+] Copied{RESET}")
            except Exception as e:
                print(f"{RED}[ERR]{RESET} {e}"); sys.exit(1)
        else:
            parser.error("Provide text or -f file")
        return

    # ── AES ───────────────────────────────────────────────────
    if c == 'aes-enc':
        if not pw:
            print(f"{RED}[ERR]{RESET} -p password required"); sys.exit(1)
        print(f"{GREEN}[OUT]{RESET} {aes_encrypt(args.text, pw)}"); return
    if c == 'aes-dec':
        if not pw:
            print(f"{RED}[ERR]{RESET} -p password required"); sys.exit(1)
        print(f"{GREEN}[OUT]{RESET} {aes_decrypt(args.text, pw)}"); return

    # ── Batch ─────────────────────────────────────────────────
    if c == 'batch':
        n = batch_encrypt(args.folder, pw)
        print(f"{GREEN}[+] Encrypted {n} files{RESET}"); return

    # ── QR ────────────────────────────────────────────────────
    if c == 'qr-enc':
        out = qr_encode(args.text, args.output)
        print(f"{GREEN}[+] QR saved →{RESET} {out}"); return
    if c == 'qr-dec':
        print(f"{GREEN}[OUT]{RESET} {qr_decode(args.image)}"); return

    # ── Stego ─────────────────────────────────────────────────
    if c == 'hide':
        out = hide_in_image(args.image, args.secret, args.output)
        print(f"{GREEN}[+] Hidden →{RESET} {out}"); return
    if c == 'reveal':
        print(f"{GREEN}[OUT]{RESET} {reveal_from_image(args.image)}"); return

    # ── Network ───────────────────────────────────────────────
    if c == 'send':
        host, port = args.target.rsplit(':', 1)
        net_send(host, int(port), args.message, pw)
        print(f"{GREEN}[+] Sent{RESET}"); return
    if c == 'recv':
        addr, msg = net_recv(args.port, pw)
        print(f"{GREEN}[FROM {addr[0]}:{addr[1]}]{RESET} {msg}"); return

    # ── Extra ─────────────────────────────────────────────────
    if c == 'gui':  gui(); return
    if c == 'test': sys.exit(run_tests())
    if c == 'interactive': interactive(password=pw); return


if __name__ == "__main__":
    main()
