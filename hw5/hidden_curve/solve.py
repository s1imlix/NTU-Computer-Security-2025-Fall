from sage.all import *
from Crypto.Cipher import AES
from hashlib import sha256

p = 4841047389180898603681931927457617059503902228730507908664290636151379891432791293908610651130515418602997696101151879025398834332236351079293832887262591
G = b'\x0e\xdf`\xba1\xb7\xc3\xb3\xe0!"\'{\xfe\xafe\xc3\xa9\xc4\x06\xf2\x06\x9b\xb1\x1b\x1e\x19\xfbs\xf0$\xe6B*)[\x97\xd2G\x82-i\xa4S\x91\x16\xd4\xdeB\x1b\x1cZE(dp\xa1U\x14\x99\xfb<\xb2e$U\xfe\xe7G)\x06\x07\xd9\x7f7\x9eS$m#[\xabt\xb8tL\x9b\x1a\x9a\xc3\xc3\x02\xfd[.\xc3A\x14k\xdd\x88F\x8d\x84i\xa5\x18\xdd\x89\x8d)\xf4\xafeQ\xf29\x18\xda\xbc\xfb\xd5\x8d\xec\xe2Q>T'
Y = b'MHz\xcf\x11\xb7q,eB\xdf\xa6\x1b\xe7\x18\xab\xe5v\xd8\xb2\x02\x0b\x9f\xddOf\xd6_\x8d\x8a\xdb\xce\xdeH#xC\xb8\xec1\xb1E\xb7\xc2Wk\xa3S\xfc[\xfb\xddM\xc6{\xd6\x1f\xb8\xb8\x88\x04\xcaM\xdf6\xe87mM_\xce\x7f\xcd\xac\xa0\x9e\x85h\x8a\xd6X\xe4\xb9\xc6\xc5\xb6\xe1\xcf\xb1\x02.\xc6\x1eh\xb3\x9fVhk{\xcc\x8fSv\n\xc2\x96\x96L\x98\xf0\x150\xfa\xa5\x04\x95S+\xd2\xd5\xd4\x9bK\x85c<x'
enc = b'Z8\xd0\xeeN\x0cq\x13\xc0\xf0Jw\x9a\xf9T:\xcdu7\xdb"|TM\xf3\xf4\xbb?;\'\xf2\xd3fI\xea7\xd5\xce\x0e\xbf\x07{\x01Rn\n^"d\x95(do\x1c}x\x8cH\x80\x87I\r\x0b\xda*\xf9z\x08\xf0A\x9d\xfd\xf95qI\xd6\xb7\xf4cG\xf6 \xef\xc9"\xc9U\x03o\xed]Y\x156\x83o\xbe\x14#\xc2\xdd\xb4]\x02\xc5\x0e\xa3\xb6\x1cP\xc4\xf9D\xc5\xf6\xaee0q\x9be\x80j\x8eRg\xe5\x8al\x8a\xe8\xe3\xd0\x1e\x81P\xb5\xeel\xd7\xd0\xe7\x85[\x8b\xf8\x9b\xa7\xf0\xca\xcfK\xe7^\xd83\x88W\x17\x85_\x04\xda\xd9\x92\xba\xadn[\t\x12\xc4\xe9\xb8\xcb-\xe0{\xbb\xf0\x93\xeb\x8c\xef\xfc*\xb8s\xf6\x1f\xc6\x87\x93\xc6'
sig = (2716688094616399939274833074837775476648435724371746214947810380566325684961208164099195902630001977318105613119810459945970571988469808928608989836336830, 4634230343637456184412048452788872457250483559635357762416211847178834986764316099603188013493637695868658679696509945981813044637993502052867328877909335)


def point_add(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None  # point at infinity
    if P == Q:
        m = (3*x1*x1 + a) * pow(2*y1, -1, p) % p
    else:
        m = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (m*m - x1 - x2) % p
    y3 = (m*(x1 - x3) - y1) % p
    return (x3, y3)

def scalar_mult(k, P, a, p):
    R = None
    Q = P
    while k:
        # print(k)
        if k & 1:
            R = point_add(R, Q, a, p)
        Q = point_add(Q, Q, a, p)
        k >>= 1
    return R

def bytes_to_point(b):
    x = int.from_bytes(b[:64], 'big')
    y = int.from_bytes(b[64:], 'big')
    return x, y

def solve():
    Gx, Gy = bytes_to_point(G)
    Yx, Yy = bytes_to_point(Y)

    # FactorDB
    p1 = 50328431029706963590066788904589636229306167394320135221224893949690750996743
    p2 = 96189117962437811316056177337022322304400484589113136985607890679543273441737
    assert p1 * p2 == p

    R = Integers(p)
    g_x, g_y = R(Gx), R(Gy)
    y_x, y_y = R(Yx), R(Yy)

    # Gy^2 = Gx^3 + a*Gx + b mod p
    # Yy^2 = Yx^3 + a*Yx + b mod p
    # a = ((Gy^2 - Yy^2) - (Gx^3 - Yx^3)) * (Gx - Yx)^-1 mod p
    a = ((g_y**2 - y_y**2) - (g_x**3 - y_x**3)) * (g_x - y_x).inverse()
    b = g_y**2 - g_x**3 - a * g_x

    print(f'Curve parameters:\na = {a}\nb = {b}')
    # check singular on both curves
    delta_1 = (4 * a**3 + 27 * b**2) % p1
    delta_2 = (4 * a**3 + 27 * b**2) % p2
    print(f'Delta mod p1: {delta_1}\nDelta mod p2: {delta_2}')

    # First curve is singular (node) 
    # (x - r)^2 * (x - s) = x^3 - (2r + s)x^2 + (r^2 + 2rs)x - r^2s
    # r = -3b * (2a)^-1 mod p1, s = -2r 

    F1 = GF(p1)

    x = F1["x"].gen()
    f = x**3 + a * x + b
    roots = f.roots()
    print(f'Roots over F1: {roots}') # alpha, beta
    if roots[0][1] == 2:
        alpha = roots[0][0]
        beta = roots[1][0]
    else:
        alpha = roots[1][0]
        beta = roots[0][0]

    # homomorphism
    def phi(x, y):
        t = (alpha - beta).sqrt()
        return (y + t * (x - alpha)) / (y - t * (x - alpha))
    
    F1_G = phi(Gx, Gy)
    F1_Y = phi(Yx, Yy)
    F1_G_ord = F1_G.multiplicative_order()

    print(f'Computing discrete log in group of size {F1_G_ord.bit_length()} bits ({F1_G_ord})')
    print(f'Use CADO-NFS to compute discrete log: {F1_G}^x = {F1_Y} mod {p1}')
    # F1_n = int(F1_Y.log(F1_G)) too slow. CADO-NFS discrete log
    # ./cado-nfs.py -dlp -ell <F1_G_ord> target=<F1_Y> <p>
    # ./cado-nfs.py -dlp -ell <F1_G_ord> target=<F1_G> <p>
    # and divide the two numbers

    F1_Y_n = 1228144487186139510923662539096265408920356780452156249662427068835639125896
    F1_G_n = 12909583811405021869722521969874084876324586974534525257235344464346852184341

    F1_n = (F1_Y_n * inverse_mod(F1_G_n, F1_G_ord)) % F1_G_ord
    print(f'Discrete log over F1: {F1_n}')
    F1_mult = F1_G.parent()
    
    assert scalar_mult(F1_n, (g_x, g_y), a, p1) == (y_x, y_y)

    # Second curve: Check order first
    F2 = GF(p2)
    E2 = EllipticCurve(F2, [a, b])
    E2_order = E2.order()
    print(f'Curve order over F2: {E2_order}') # same as p2, smart's attack
    
    # ref: https://crypto.stackexchange.com/questions/70454/why-smarts-attack-doesnt-work-on-this-ecdlp
    def SmartAttack(P,Q,p):
        E = P.curve()
        Eqp = EllipticCurve(Qp(p, 2), [ ZZ(t) + randint(0,p)*p for t in E.a_invariants() ])
        # invariants = [a, b] lift to a + kp, b + k'p

        P_Qps = Eqp.lift_x(ZZ(P.xy()[0]), all=True)
        for P_Qp in P_Qps:
            if GF(p)(P_Qp.xy()[1]) == P.xy()[1]:
                break

        Q_Qps = Eqp.lift_x(ZZ(Q.xy()[0]), all=True) 
        for Q_Qp in Q_Qps:
            if GF(p)(Q_Qp.xy()[1]) == Q.xy()[1]:
                break # Choose (x, y) based on lifted x


        # phi(P) = slope(p[P, 0]) = -x/y
        p_times_P = p*P_Qp
        p_times_Q = p*Q_Qp

        x_P,y_P = p_times_P.xy()
        x_Q,y_Q = p_times_Q.xy()

        phi_P = -(x_P/y_P)
        phi_Q = -(x_Q/y_Q)
        k = phi_Q/phi_P
        return ZZ(k)
    
    E2_G = E2(Gx, Gy)
    E2_Y = E2(Yx, Yy)
    F2_n = SmartAttack(E2_G, E2_Y, p2)
    print(f'Discrete log over F2: {F2_n}')

    E2 = EllipticCurve(F2, [a, b])
    assert (F2_n * E2(Gx, Gy)) == E2(Yx, Yy)

    # Combine via CRT
    sk = crt([F1_n, F2_n], [F1_G_ord, p2])

    print(f'Private key mod l: {sk}')
    
    E = EllipticCurve(R, [a, b])

    tpk_bytes = enc[:128]
    nonce = enc[128:136]
    ct = enc[136:]

    Tx = int.from_bytes(tpk_bytes[:64], "big")
    Ty = int.from_bytes(tpk_bytes[64:], "big")
    T = E(Tx, Ty)

    S = sk * T
    S_bytes = int(S[0]).to_bytes(64, "big") + int(S[1]).to_bytes(64, "big")

    key = sha256(S_bytes).digest()
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    m = cipher.decrypt(ct)
    print(m.decode())




if __name__ == '__main__':
    solve()

