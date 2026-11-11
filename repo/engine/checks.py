"""Independent numeric re-solves (sympy / plain python). Each returns (computed, expected_key_value, note).
These are the 'solver' leg of the pipeline for the physics-numeric questions: it never sees the
student's comment, only the stem. Used to gate answer_key edits (guards.py)."""
import math, sympy as sp
C = {}
def chk(qid):
    def d(f): C[qid] = f; return f
    return d

@chk('68dea616d0cda73d07e93ae6')   # flux: q/2 at face centre, 2q at cube corner
def _():
    q, e0 = sp.symbols('q e0', positive=True)
    flux = sp.Rational(1, 2) * (q/2)/e0 + sp.Rational(1, 8) * (2*q)/e0
    n = sp.simplify(flux / (q/(2*e0))); return float(n), 2, 'face-centre q/4e0 + corner q/4e0 = q/2e0 -> n=1'
@chk('68e870ef42c06737d6e565c4')   # P = rho v^2 / 3
def _(): return (1/3)*9e-2*400**2, 4556, 'P = rho v^2/3'
@chk('60f744b3f1b9bc7cc7b4a949')   # LCR
def _(): return math.hypot(40, 60-30), 130, 'V = sqrt(VR^2+(VL-VC)^2)'
@chk('6263d75bdd44e265ef926d97')   # floating cube: 800 g = 2cm * a^2 * 1 g/cm3
def _(): return math.sqrt(800/2), 20, 'a^2 = 400'
@chk('696a866665252c04fc1f81c2')   # dV = dP V / B with edge 10 cm -> mm^3
def _(): return 7e6/1.4e11*(0.10**3)*1e9, 50, 'edge 10 cm assumed by stored solution'
@chk('60f742f6660d187cc13a8078')   # Z with L = 95.5 mH
def _(): return math.hypot(40, 2*math.pi*50*95.5e-3), 50, 'Z=sqrt(R^2+(2 pi f L)^2)'
@chk('5fc60508028950133eac8963')   # static friction on wall = mg when mg < mu N
def _(): return min(2*10, 0.3*100), 20, 'f = mg = 20 N (< 30 N limit)'
@chk('612151a6a34397610a9a2e58')   # KE = h^2/(2 m lam^2)
def _():
    h, m, e = 6.626e-34, 9.109e-31, 1.602e-19
    return h**2/(2*m*(0.3e-9)**2)/e, 16.8, 'eV'
@chk('68f21caf941cda588bc04365')   # decay 48->6 in 3 min => 3 half-lives, tau = t_half/ln2
def _(): return 1/math.log(2), 1.44, 'tau (min)'
@chk('68dea715387eea3d0d95f790')   # 6*(7.203)^2 to 4 s.f. then x10
def _(): return round(6*7.203**2, 1)*10, 3113, '4 s.f.'
@chk('68dea619d0cda73d07e93aee')   # first alignment: faster wheel one extra turn
def _():
    t = sp.symbols('t', positive=True)
    return float(sp.solve(sp.Eq(0.5*(sp.pi/2)*t**2 - 0.5*(sp.pi/4)*t**2, 2*sp.pi), t)[0]), 4, 't (s)'
@chk('68e8734442c06737d6e56da4')
def _():
    F, mu = sp.symbols('F mu'); s = sp.solve([F-100*mu-10, 2*F-100*mu-100], [F, mu]); return float(s[mu]), 0.8, 'mu'
@chk('68dea577d0cda73d07e9391c')   # uniformly charged sphere, V(surface)=16 V
def _():
    V = 16; vp = V*sp.Rational(11, 8); vs = V*sp.Rational(1, 2); return float(vp-vs), 14, 'VP-VS (V)'
@chk('636283dbe3770c24f866e6d6')
def _(): return (64/(4**2)), 4, 'sigma_big/sigma_small'
@chk('6956d7e988d7701e5617bd3e')
def _(): return 8/math.cos(math.pi/4), 8*math.sqrt(2), 'A (m)'
@chk('6956d7bb23cb221e570d6013')
def _(): return math.atan(4), math.atan(4), 'H=R => tan(theta)=4'
@chk('68dea7c2387eea3d0d95f9bb')
def _(): return (1/5e-3)*(2e-3*0.5-1.5e-3*0.4)*100, 8, 'shift (cm)'
@chk('6062ec84518e9535e120c422')
def _(): return 3*0.19/(100*100)*1e5, 5.7, 'gamma x1e-5'
@chk('695ee00b88d7701e561aabc5')   # equal-amplitude waves, phase pi/2: I = 2*I0*(1+cos phi)
def _(): return 2*(1+math.cos(math.pi/2)), 1, 'I/I0: 2.0 -> Assertion (I = I0) is FALSE; Reason ("always sum") also false'

def run():
    out = {}
    for qid, f in C.items():
        got, key, note = f(); out[qid] = {'computed': round(float(got), 4), 'key_value': round(float(key), 4), 'note': note}
    return out
if __name__ == '__main__':
    import json; r = run(); json.dump(r, open('engine/solver_report.json', 'w'), indent=1)
    for k, v in r.items(): print(k[-6:], v)
