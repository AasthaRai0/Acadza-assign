"""Turn Acadza production HTML (+inline MathML) into compact plain text an LLM can read.
Also exposes helpers to split option lines out of the question stem."""
import re, html
from bs4 import BeautifulSoup

def _m(node):
    """Recursive MathML -> linear text."""
    if node is None: return ''
    if isinstance(node, str): return node
    n = node.name
    kids = [c for c in node.children if getattr(c, 'name', None) or str(c).strip()]
    t = lambda i: _m(kids[i]) if i < len(kids) else ''
    allk = lambda: ''.join(_m(c) for c in kids)
    if n in ('mn', 'mi', 'mo', 'mtext', 'ms'): return node.get_text()
    if n == 'mfrac': return f'({t(0)})/({t(1)})'
    if n == 'msup': return f'{t(0)}^({t(1)})'
    if n == 'msub': return f'{t(0)}_({t(1)})'
    if n == 'msubsup': return f'{t(0)}_({t(1)})^({t(2)})'
    if n == 'msqrt': return f'sqrt({allk()})'
    if n == 'mroot': return f'root[{t(1)}]({t(0)})'
    if n == 'mover': return f'{t(0)}[over {t(1)}]'
    if n == 'munder': return f'{t(0)}[under {t(1)}]'
    if n == 'munderover': return f'{t(0)}[{t(1)}..{t(2)}]'
    if n == 'mtable': return ' ; '.join(_m(c) for c in kids)
    if n == 'mtr': return ' | '.join(_m(c) for c in kids)
    if n == 'mtd': return allk()
    return allk()

def to_text(h):
    if h is None: return ''
    soup = BeautifulSoup(h, 'html.parser')
    for m in soup.find_all('math'):
        m.replace_with(' ' + _m(m) + ' ')
    for img in soup.find_all('img'):
        img.replace_with(f' [IMG {img.get("src","")[-30:]}] ')
    for sp in soup.find_all('sup'): sp.replace_with('^(' + sp.get_text() + ')')
    for sb in soup.find_all('sub'): sb.replace_with('_(' + sb.get_text() + ')')
    for br in soup.find_all('br'): br.replace_with('\n')
    for blk in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'li']): blk.append('\n')
    txt = soup.get_text()
    txt = txt.replace('\xa0', ' ')
    txt = re.sub(r'[ \t]+', ' ', txt)
    txt = re.sub(r'\n\s*\n+', '\n', txt)
    return txt.strip()

def body(q):
    t = q['questionType']
    return q['scq'] if t == 'scq' else q['mcq'] if t == 'mcq' else q['integerQuestion']
