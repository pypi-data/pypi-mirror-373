# -*- coding: utf-8 -*-
"""analyze windings

 Conventions

 Number of slots: Q
 Numper of pole pairs: p
 Number of phases: m
 Number of layers: l
 Number of wires per slot side: n
 Number of slots per pole and phase: q = Q/p/2/m
 Number of coils per phase: c = Q * l/2/m
 Number of parallel circuits (coil groups): g
 Number of turns per phase: w1 = Q * n * l/2/m/g

Refs:
odd number of phases
 doi:10.1007/s00502-021-00873-6
even number of phases
 doi:10.1049/iet-epa.2020.0553
"""
import numpy as np
import femagtools.bch
from xml.etree import ElementTree as ET

coil_color = ['lime', 'gold', 'magenta',
              'blue', 'brown', 'blueviolet']


def num_basic_windings(Q, p, l):
    """return number of basic windings"""
    if l == 1:  # single layer
        return np.gcd(Q//2, p)
    return np.gcd(Q, p)


def q1q2yk(Q, p, m, l=1):
    """returns q1, q2, Yk, Qb"""
    t = num_basic_windings(Q, p, l)
    Qb = Q//t
    qbb = Qb if l==2 else Qb//2
    pb = p//t
    if qbb//m % 2:  # odd
        q2 = (qbb + m)//(2*m) - 1
        q1 = q2 + 1
    else:
        q2 = (qbb)//(2*m)
        q1 = q2
    n = 1
    while (n*qbb + 1) % pb:
        n += 1
    Yk = (n*qbb + 1)//pb
    return q1, q2, Yk, Qb

def end_wdg_length_round_wires(layers, Rp, Rb, r_wire, h, coil_span, Q, bore_diam, slot_h1, slot_height):
    '''return length of a single winding head for 1 coil turn.
    Multiply by 2 to get length for both winding heads'''
    if layers == 2:
        R_inner_lyr = bore_diam/2 + slot_h1 + slot_height/4
        R_outer_lyr = bore_diam/2 + slot_h1 + 3*slot_height/4
    elif layers == 1:
        R_inner_lyr = bore_diam/2 + slot_h1 + slot_height/2
        R_outer_lyr = bore_diam/2 + slot_h1 + slot_height/2
    else:
        raise ValueError("Round wire windings can only have 1 or 2 layers")

    if Rb < 2*r_wire:
        Rb = 2*r_wire
    if Rp < R_outer_lyr + 2*(Rb + r_wire):
        Rp = R_outer_lyr + 2*(Rb + r_wire) + 1e-5
    if h < 2*(Rb + r_wire):
        h = 2*(Rb + r_wire) + 0.002

    l = np.pi*coil_span/Q * (Rp + R_inner_lyr)
    z = Rp - R_outer_lyr - 2*(Rb + r_wire)
    l_ew = 2*h + l + z + (Rb + r_wire)*(np.pi - 2)
    return l_ew, h, Rp, Rb

def end_wdg_hairpin_check(alpha, h, dmin, l_h, wire_w, tooth_wmin, h_conn):
    alpha = alpha*np.pi/180     # ensure alpha is in radians
    dmin_new = 0
    alpha_new = 0
    h_new = 0

    if dmin < 0.0015:
        dmin = 0.0015
    if h_conn < 0.005:
        h_conn = 0.005

    if alpha == 0 and h == 0: # end wdg parameters not set
        alpha_new = np.arcsin((dmin + wire_w)/(tooth_wmin + wire_w))
        h_new = np.tan(alpha_new)*l_h/2

    elif h > 0: # imposed end wdg height
        alpha_new = np.arctan(h/l_h)
        dmin_new = np.sin(alpha_new)*(tooth_wmin + wire_w) - wire_w
        if dmin_new < dmin: # imposed end wdg height is not feasible - calculate min end wdg parameters
            dmin_new = dmin
            alpha_new = np.arcsin((dmin_new + wire_w)/(tooth_wmin + wire_w))
            h_new = np.tan(alpha_new)*l_h/2

    elif alpha > 0: # imposed end wdg angle
        dmin_new = np.sin(alpha)*(tooth_wmin + wire_w) - wire_w
        if dmin_new < dmin: # imposed end wdg angle is not feasible - calculate min end wdg parameters
            dmin_new = dmin
            alpha_new = np.arcsin((dmin_new + wire_w)/(tooth_wmin + wire_w))
            h_new = np.tan(alpha_new)*l_h/2

    if dmin_new > dmin:
        dmin = dmin_new
    if alpha_new > alpha:
        alpha = alpha_new
    if h_new > h:
        h = h_new

    return h, alpha, dmin, h_conn

def end_wdg_length_hairpins(wire_h, wire_w, wire_th, wire_gap,
                                 layers, coil_pitch, Q, bore_diam, slot_w, slot_h,
                                 h_bent=0, h_welded=0, h_conn=0.005, alpha_bent=0, alpha_welded=0, dmin=0.0015): # needs to be validated
    '''return end wdg length of single pin for bent and welded side, average end wdg length,
     bent and welded side end wdg heights, bending angles and min distances between pins'''

    R_avg = bore_diam/2 + wire_th + layers/2*(wire_h + wire_gap) + wire_h/2
    l_h = R_avg*coil_pitch/Q*2*np.pi
    tooth_wmin = (bore_diam + 2*wire_th)*np.pi/Q - slot_w

    h_bent, alpha_bent, dmin, h_conn = end_wdg_hairpin_check(alpha_bent, h_bent, dmin, l_h, wire_w, tooth_wmin, h_conn)
    h_welded = h_welded - h_conn if h_welded - h_conn > 0 else 0
    h_welded, alpha_welded, dmin, h_conn = end_wdg_hairpin_check(alpha_welded, h_welded, dmin, l_h, wire_w, tooth_wmin, h_conn)

    l_bent = 2*(0.003 + wire_w/2*alpha_bent + wire_w*(np.pi/2 - alpha_bent) + np.sqrt((l_h/2)**2 + h_bent**2))
    l_welded = 2*(0.003 + wire_w/2*alpha_bent + wire_w*(np.pi/2 - alpha_bent) + np.sqrt((l_h/2)**2 + h_welded**2)) + h_conn
    l_ew = (l_bent + l_welded)/2
    h_welded = h_welded + h_conn
    return l_bent, l_welded, l_ew, h_bent, h_welded, h_conn, alpha_bent*180/np.pi, alpha_welded*180/np.pi, dmin


class Winding(object):
    def __init__(self, arg):
        """create winding either from bch winding section or winding dict()

        Arguments:
          arg: (object) femagtools.bch.Reader
            or dict Q: number of slots, m: number of phases, p: pole pairs, l: num layers, yd: coils span (slots)
       """
        if isinstance(arg, femagtools.bch.Reader):
            self.m = arg.machine['m']
            self.Q = arg.machine['Q']
            self.p = arg.machine['p']
            self.windings = arg.windings
        else:
            for k in arg.keys():
                setattr(self, k, arg[k])
        # balanced winding check
        if np.mod(self.Q, self.m*np.gcd(self.Q, self.p)):
            raise ValueError(
                f"Unbalanced winding: Q={self.Q}, p={self.p}, m={self.m}")
        self.q = self.Q/2/self.p/self.m  # number of coils per pole and phase

        if hasattr(self, 'windings'):
            # calculate coil width yd and num layers l
            taus = 360/self.Q
            try:
                ngen = arg.machine.get('qs_sim', 0)
            except AttributeError:
                ngen = 0
            if 'slots' in self.windings[1]:  # custom winding def
                for k in self.windings:
                    w = self.windings[k]
                    ngen = max(max(w['slots']), ngen)
                    w['dir'] = [1 if s > 0 else -1 for s in w['slots']]
                    w['PHI'] = [(2*abs(s)-1)*taus/2 for s in w['slots']]
                    w['R'] = [0 if l == 1 else 1 for l in w['layer']]

            self.yd = max(self.Q//self.p//2, 1)
            w = 1
            try:
                k = self.windings[w]['dir'].index(
                    -self.windings[w]['dir'][0])
                dphi = (self.windings[w]['PHI'][k] -
                        self.windings[w]['PHI'][0])
                self.yd = abs(round(dphi/taus))
            except ValueError:
                pass

            slots = [round((x-taus/2)/taus)
                     for x in self.windings[1]['PHI']]
            self.l = 1
            if len(slots) > ngen//self.m:
                self.l = 2
            return

        layers = 1
        if hasattr(self, 'l'):
            layers = self.l
        else:
            self.l = layers
        coilwidth = max(self.Q//self.p//2, 1)
        if hasattr(self, 'coilwidth'):   # obsolete, use yd instead
            coilwidth = self.coilwidth
        elif hasattr(self, 'yd'):
            coilwidth = self.yd

        self.yd = coilwidth
        if self.m % 2:  # odd number of phases
            q1, q2, Yk, Qb = q1q2yk(self.Q, self.p, self.m, self.l)
            j = 2 if layers == 1 else 1
            k1 = [(q1 + q2)*i for i in range(self.m)]
            k2 = (q1*(self.m+1) + q2*(self.m-1))//2
            pos = [[(j*Yk*(k + n)) % Qb
                    for n in range(q1)] for k in k1]
            neg = [[j*Yk*(k + n + k2) % Qb
                    for n in range(q2)] for k in k1]
        else:  # even number of phases
            if np.mod(self.Q, 4/self.l*self.m*np.gcd(self.Q, self.p)):
                raise ValueError(
                    f"Unbalanced winding: Q={self.Q}, p={self.p}, m={self.m}")
            t = np.gcd(self.Q, self.p)
            Qb = self.Q//t
            seq = np.array([i for j in range(Qb)
                            for i in range(Qb) if (j*self.p//t - i) % Qb == 0])
            if self.l == 1:
                seq = seq[::2]
            seq = np.array(seq).reshape((-1, 6))
            pos = seq[::2].T
            neg = seq[1::2].T

        if self.l > 1:
            slots = [sorted([(k, 1, 1)
                             for k in p] + [(k, -1, 1)
                                            for k in n])
                     for n, p in zip(neg, pos)]
            for i, p in enumerate(slots):
                slots[i] = sorted(slots[i] +
                                  [((k[0]+self.yd) % Qb, -k[1], 0)
                                   for k in slots[i]])
        else:
            if (coilwidth + 1) % 2:
                coilwidth += 1
            xneg = [sorted([s for s in n if s+1 % 2] +
                           [(s + coilwidth) % Qb for s in p if s+1 % 2])
                    for n, p in zip(neg, pos)]
            xpos = [sorted([s for s in p if s+1 % 2] +
                           [(s + coilwidth) % Qb for s in n if s+1 % 2])
                    for n, p in zip(neg, pos)]

            slots = [sorted([(k, 1, 1) for k in p] + [(k, -1, 1) for k in n])
                     for n, p in zip(xneg, xpos)]

        taus = 360/self.Q
        self.windings = {
            i+1:  dict(dir=[k[1] for k in s],
                       N=[1]*len(s), R=[k[2] for k in s],
                       PHI=[taus/2+k[0]*taus for k in s])
            for i, s in enumerate(slots)}

    def kw_order(self, n):
        """return winding factor harmonics"""
        if np.isscalar(n):
            if n == 0:
                return self.p
            g = np.arange(-n, n, 1)
            t = num_basic_windings(self.Q, self.p, self.l)
            return self.p + g * self.m*t
        return n

    def kwp(self, n=0):
        """pitch factor"""
        if np.asarray(n).any() and not np.isscalar(n):
            nue = n
        else:
            nue = self.kw_order(n)
        return np.sin(nue*self.yd*np.pi/self.Q)

    def kwd(self, n=0):
        """zone (distribution) factor"""
        q1, q2, Yk, Qb = q1q2yk(self.Q, self.p, self.m, self.l)
        if np.asarray(n).any() and not np.isscalar(n):
            nue = n
        else:
            nue = self.kw_order(n)
        if q1 == q2:  # integral slot winding
            q = self.Q/2/self.m/self.p
            nuep = nue/self.p
            return np.sin(nuep*np.pi/2/self.m)/q/np.sin(nuep*np.pi/2/self.m/q)
        k = 2 if self.l == 1 else 1
        a = nue*k*np.pi/self.Q*Yk
        t = self.Q//Qb
        return ((np.sin(a*q1) - np.cos(np.pi/t*Yk*nue)*np.sin(a*q2))
                /((q1+q2)*np.sin(a)))

    def kw(self, n=0):
        """return winding factor"""
        return np.abs(self.kwp(n) * self.kwd(n))

    def harmleakcoeff(self, n=4000):
        """return harmonic leakage coefficient
        Arguments:
        n: (int) maximum number of harmonics"""
        nue = self.p * (1 + np.arange(1-n, n)*2*self.m)
        kw1 = self.kwd()*self.kwp()
        kwn = self.kwd(nue)*self.kwp(nue)
        return np.sum((self.p*kwn/nue/kw1)**2) - 1

    def coils_per_phase(self):
        """return number of coils per phase"""
        return self.Q * self.l/2/self.m

    def turns_per_phase(self, n, g):
        """return number of turns per phase
        Arguments:
        n: (int) number of wires per slot side
        g: (int) number of parallel coil groups
        """
        return n*self.coils_per_phase()//g

    def inductance(self, nwires, g, da1, lfe, ag, sw=0):
        """return main inductance / phase
        Arguments:
        nwires: number of wires in slot side
        g: (int) number of parallel groups
        da1: (float) bore diameter / m
        lfe: (float) length of lamination /m
        ag: (float) length of airgap / m
        sw: (float) slot opening width / m
        """
        mue0 = 4*np.pi*1e-7
        # carter factor
        tauq = np.pi*da1/self.Q
        h = sw/ag
        xic = 2/np.pi*(h*np.arctan(h/2) - np.log(1+(h/2)**2))
        kc = tauq/(tauq-xic*ag)  # Carter factor
        de = kc * ag

        N1 = self.turns_per_phase(nwires, g)
        return 3*mue0*da1*lfe*((self.kw()*N1)**2 /
                               (np.pi*self.p**2*de))

    def sequence(self):
        """returns sequence of winding keys"""
        return list(zip(*sorted([(k, self.windings[k]['PHI'][0])
                                 for k in self.windings.keys()],
                                key=lambda wdg: wdg[1])))[0]

    def slots(self, key):
        """returns slot indexes of winding key"""
        taus = 360/self.Q
        t = num_basic_windings(self.Q, self.p, self.l)
        Qb = self.Q//t
        dim = self.l*Qb//self.m
        ngen = t
        qgen = Qb
        if dim > len(self.windings[key]['PHI']):
            qgen = qgen//2
            ngen = 2*t
        slots = [(round((x-taus/2)/taus) + qgen*n) % self.Q + 1
                 for n in range(ngen)
                 for x in self.windings[key]['PHI'][:dim]]
        return np.array(slots).reshape(t, -1)

    def axis(self, k=1):
        """returns axis angle of winding 1 in mechanical system"""
        return self.mmf(k=k)['alfa0']

    def currdist(self, k=1, phi=0):
        """return the current density of slots
        Arguments:
          k: (int) winding key (all if 0 or 'all')
          phi: (float) current angle (default 0)
        """
        if k == 0 or k == 'all':
            keys = self.windings.keys()
        elif np.isscalar(k):
            keys = [k]
        else:
            keys = k
        m = len(self.windings)
        t = num_basic_windings(self.Q, self.p, self.l)
        cdist = {k: np.zeros(self.Q//t) for k in keys}
        for z in self.zoneplan():
            if z:
                for j in keys:
                    a = np.zeros(self.Q//t)
                    curr = np.cos((j-1)*2*np.pi/m - phi)
                    for s in z[j-1]:
                        d = -1 if s < 0 else 1
                        a[abs(s)-1] = d*curr
                    cdist[j] += a
        return cdist

    def mmf(self, k=1, nmax=21, phi=0):
        """returns the dimensionless magnetomotive force
        (ampere-turns/turns/ampere) and winding angle of phase k (rad)
        Arguments:
        k: (int) winding key (all if 0 or 'all')
        nmax: (int) max order of harmonic (in electrical system)
        phi: (float) current angle (default 0)
        """
        cdist = self.currdist(k, phi)
        num_slots = len(cdist[list(cdist.keys())[0]])
        t = self.Q//num_slots
        clink = np.zeros(num_slots)
        for j in cdist:
            a = cdist[j]
            ap = np.zeros(len(a))
            l = 0
            v = 0
            for n in np.nonzero(a>0)[0]:
                ap[l:n] = v
                v += cdist[j][n]
                l = n
            ap[n:] = v
            an = np.zeros(len(a))
            l = 0
            v = 0
            for n in np.nonzero(a<0)[0]:
                an[l:n] = v
                v += cdist[j][n]
                l = n
            an[n:] = v
            clink += an + ap

        NY = 4096  # number of samples per slot
        y = [[c]*NY for c in (clink-np.mean(clink))]
        yy = np.tile(np.hstack(
            (y[-1][-NY//2:], np.ravel(y[:-1]), y[-1][:-NY//2])), t)
        yy /= np.max(yy)

        # calc spectrum
        pb = self.p//t
        N = len(yy)
        Y = np.fft.fft(yy)
        if self.q < 1:
            imax = pb
        else:
            imax = np.argmax(np.abs(Y[:N//2]))
        a = 2*np.abs(Y[imax])/N
        taus = 2*np.pi/self.Q
        freq = np.fft.fftfreq(N, d=taus/NY)
        T0 = np.abs(1/freq[imax])
        alfa0 = np.angle(Y[imax])
        pos_fft = np.linspace(0, 2*np.pi/t, 20*pb)
        D = (a*np.cos(2*np.pi*pos_fft/T0+alfa0))
        nue, mmf_nue = np.array(
            [(n, f) for n, f in zip(
                np.arange(0, nmax),
                2*np.abs(Y)/N) if f > 0]).T

        if alfa0 > 0:
            alfa0 -= 2*np.pi

        return dict(
            pos=(taus/NY*np.arange(NY*self.Q//t)).tolist(),
            mmf=yy[:NY*self.Q//t].tolist(),
            alfa0=-alfa0/self.p,
            nue=nue.tolist(),
            currdist={k: cdist[k].tolist() for k in cdist},
            mmf_nue=mmf_nue.tolist(),
            pos_fft=pos_fft.tolist(),
            mmf_fft=D.tolist())

    def zoneplan(self):
        taus = 360/self.Q
        dphi = 1e-3
        slots = {k: [s-1 for s in self.slots(k)[0]]
                 for k in self.windings}
        layers = 1
        avgr = 0
        maxr, minr = max(self.windings[1]['R']), min(self.windings[1]['R'])
        if maxr-minr > 1e-6:
            layers = 2
            avgr = (maxr+minr)/2

            def is_upper(r, phi):
                return r > avgr
        elif len(slots[1]) > len(set(slots[1])):
            layers = 2

            def is_upper(r, phi):
                return phi < -dphi
        else:
            def is_upper(r, phi):
                return True

        upper = [[s+1 for s, x, r in zip(
            slots[key],
            self.windings[key]['PHI'],
            self.windings[key]['R'])
            if is_upper(r, s*taus - (x-taus/2))]
            for key in self.windings]
        udirs = [[d for s, d, x, r in zip(
            slots[key],
            self.windings[key]['dir'],
            self.windings[key]['PHI'],
            self.windings[key]['R'])
            if is_upper(r, s*taus - (x-taus/2))]
            for key in self.windings]
        lower = []
        ldirs = []
        if layers > 1:
            lower = [[s+1 for s, x, r in zip(
                slots[key],
                self.windings[key]['PHI'],
                self.windings[key]['R'])
                if not is_upper(r, s*taus - (x-taus/2))]
                for key in self.windings]
            ldirs = [[d for s, d, x, r in zip(
                slots[key],
                self.windings[key]['dir'],
                self.windings[key]['PHI'],
                self.windings[key]['R'])
                if not is_upper(r, s*taus - (x-taus/2))]
                for key in self.windings]

        z = ([[int(d*s) for s, d in zip(u, ud)] for u, ud in zip(upper, udirs)],
             [[int(d*s) for s, d in zip(l, ld)] for l, ld in zip(lower, ldirs)])
        # complete if not  basic winding:
        Qb = self.Q//num_basic_windings(self.Q, self.p, self.l)

        if not np.asarray(upper).size or not np.asarray(lower).size:
            layers = 1
        if layers == 1 and z[1]:
            z = ([[int(d*s) for s, d in zip(l, ld)] for l, ld in zip(lower, ldirs)],
                 [[int(d*s) for s, d in zip(u, ud)] for u, ud in zip(upper, udirs)])

        if max([abs(n) for m in z[0] for n in m]) < Qb:
            return [[k + [-n+Qb//2 if n < 0 else -(n+Qb//2) for n in k]
                     for k in m] for m in z]
        return z

    def diagram(self) -> ET.Element:
        """return winding diagram as svg element"""
        coil_len = 25
        coil_height = 4
        dslot = 8
        arrow_head_length = 2
        arrow_head_width = 2
        strokewidth = [f"{w}px" for w in [0.25, 0.5]]

        z = self.zoneplan()
        xoff = 0
        if z[-1]:
            xoff = 0.75
        yd = dslot*self.yd
        mh = 2*coil_height/yd
        slots = sorted([abs(n) for m in z[0] for n in m])
        smax = slots[-1]*dslot
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        svg = ET.Element("svg", dict(
            version="1.1", xmlns="http://www.w3.org/2000/svg",
            viewBox=f"0, -30, {slots[-1] * dslot + 15}, 40"))
        g = ET.SubElement(svg, "g", {"id": "teeth", "fill": "lightblue"})
        for n in slots:
            e = ET.SubElement(g, "rect", {
                "x": f"{n * dslot + dslot/4}",
                "y": f"{-coil_len + 1}",
                "width": f"{dslot/2}",
                "height": f"{coil_len - 2}"})

        g = ET.SubElement(svg, "g",
                          {"id": "labels",
                           "text-anchor": "middle",
                           "dominant-baseline": "middle",
                           "style": "font-size: 0.15em; font-family: sans-serif;"})
        for n in slots:
            t = ET.SubElement(g, "text", {
                "x": f"{n*dslot}",
                "y": f"{-coil_len / 2}"}).text = str(n)

        g = ET.SubElement(svg, "g", {"id": "coils",
                                     "fill": "none",
                                     "stroke-linejoin": "round",
                                     "stroke-linecap": "round"})

        direction = ['right', 'left']
        nl = 2 if z[1] else 1
        for i, layer in enumerate(z):
            b = -xoff if i else xoff
            w = i if self.yd > 1 else 0
            for m, mslots in enumerate(layer):
                for k in mslots:
                    slotpos = abs(k) * dslot + b
                    pc = [f"L {slotpos} {-coil_len//2+2} M {slotpos} {-coil_len//2-1}",
                          f"L {slotpos} {-coil_len}"]

                    if nl == 2:
                        if k > 0:
                            d = 0 if i == 0 else 1
                        else:
                            d = 1 if i == 1 else 0
                    else:
                        d = 0 if k > 0 else 1

                    if direction[d] == 'right':
                        # first layer, positive dir or neg. dir and 2-layers:
                        #   from right bottom
                        if slotpos + yd > smax+b:
                            dx = dslot if yd > dslot else yd/4
                            ph = [f"M {slotpos+yd//2-xoff+dx} {coil_height-mh*dx}",
                                  f"L {slotpos+yd//2-xoff} {coil_height} L {slotpos} 0"]
                            pt = [f"L {slotpos+yd//2-xoff} {-coil_len-coil_height}",
                                  f"L {slotpos+yd//2-xoff+dx} {-coil_len-coil_height+mh*dx}"]
                        else:
                            ph = [
                                f"M {slotpos+yd//2-xoff} {coil_height} L {slotpos} 0"]
                            pt = [
                                f"L {slotpos+yd//2-xoff} {-coil_len-coil_height}"]
                    else:
                        # from left bottom
                        if slotpos - yd < 0:  # and slotpos - yd > -3*dslot:
                            dx = dslot if yd > dslot else yd/4
                            ph = [f"M {slotpos-yd//2+xoff-dx} {coil_height-mh*dx}",
                                  f"L {slotpos-yd//2+xoff} {coil_height} L {slotpos} 0"]
                            pt = [f"L {slotpos-yd//2+xoff} {-coil_len-coil_height}",
                                  f"L {slotpos-yd//2+xoff-dx} {-coil_len-coil_height+mh*dx}"]
                        else:
                            ph = [
                                f"M {slotpos-yd//2+xoff} {coil_height} L {slotpos} 0"]
                            pt = [
                                f"L {slotpos-yd//2+xoff} {-coil_len-coil_height}"]
                    e = ET.SubElement(g, "path", {
                        "d": ' '.join(ph + pc + pt),
                        "stroke-width": strokewidth[w],
                        "stroke": coil_color[m]})

        for i, layer in enumerate(z):
            for m, mslots in enumerate(layer):
                for k in mslots:
                    x = abs(k) * dslot
                    if i:
                        x -= xoff
                    else:
                        x += xoff
                    if k > 0:
                        y = coil_len * .88
                        points = [
                            (x, -y),
                            (x - arrow_head_width / 2, -y + arrow_head_length),
                            (x + arrow_head_width / 2, -y + arrow_head_length)]
                    else:
                        y = coil_len * .12
                        points = [
                            (x, -y),
                            (x - arrow_head_width / 2, -y - arrow_head_length),
                            (x + arrow_head_width / 2, -y - arrow_head_length)]
                    ET.SubElement(svg, "polygon", {
                        "points": " ".join([f"{x},{y}" for (x, y) in points]),
                        "fill": f"{coil_color[m]}",
                        "stroke": "none"})

        return ET.tostring(svg, encoding='unicode')

    def write(self, name, workdir='.'):
        """creates WID file"""
        import pathlib
        with open(pathlib.Path(workdir) / (name + '.WID'), 'w') as fp:
            if 'slots' in self.windings[1]:
                inp = sorted([(k if s > 0 else -k, abs(s), l, n)
                              for k in self.windings
                              for s, l, n in zip(
                    self.windings[k]['slots'],
                    self.windings[k]['layer'],
                    self.windings[k]['N'])],
                    key=lambda x: (x[1], x[2]))
                fp.write('\n'.join([
                    f'Windings input data: {name}',
                    ' Number of coil sides:',
                    f'          {len(inp)}',
                    'Type of machine: 1 = Rot, 21 = Lin-x, 22 = Lin-y',
                    '           1',
                    'Index  w-keys     N-turns         Layer', '']))

                for i, t in enumerate(inp):
                    fp.write(f'{i+1:5d} {t[0]:8d} {t[3]:10.3f} {t[2]:10d}\n')
            else:
                inp = sorted([(k if d > 0 else -k, r, phi, n)
                              for k in self.windings
                              for d, r, phi, n in zip(
                    self.windings[k]['dir'],
                    self.windings[k]['R'],
                    self.windings[k]['PHI'],
                    self.windings[k]['N'])],
                    key=lambda x: (x[1], x[2]))
                fp.write('\n'.join([
                    f'Windings input data: {name}',
                    ' Number of coil sides:',
                    f'          {len(inp)}',
                    'Type of machine: 1 = Rot, 21 = Lin-x, 22 = Lin-y',
                    '           1',
                    'Index  w-keys     N-turns         R[mm]     PHI[deg]', '']))
                for i, t in enumerate(inp):
                    fp.write(
                        f'{i+1:5d} {t[0]:8d} {t[3]:10.3f} {t[1]:8.3f} {t[2]:8.3f}\n')
            fp.write('\n'.join([
                'Number of windings saved :',
                f'         {len(self.windings)}',
                'W-Key Coil-Current [A]   W-Types: (=1 :wire&cur)'
            ] + [
                f'   {k}          0.00000000       0.00000000                            1'
                for k in self.windings
            ] + ['   0', '']))


if __name__ == "__main__":
    import sys
    import matplotlib.pyplot as plt
    from xml.etree import ElementTree as ET

    if sys.argv[1:]:
        bch = femagtools.bch.read(sys.argv[1])
        wdgs = Winding(bch)
    else:
        testdata = [
            dict(Q=90, p=12, m=3, l=2, coilwidth=1),
            dict(Q=54, p=6, m=3, l=2, coilwidth=5),
            dict(Q=168, p=7, m=3, l=2, coilwidth=10)]

        wdgs = Winding(testdata[1])

    c = wdgs.mmf()
    # print('alfa0={0:6.3f}'.format(wdgs.axis()/np.pi*180))

    plt.title('Q={0}, p={1}, alfa0={2:6.3f}'.format(
        wdgs.Q, wdgs.p, c['alfa0']/np.pi*180))
    plt.plot(np.array(c['pos'])/np.pi*180, c['mmf'])
    plt.plot(np.array(c['pos_fft'])/np.pi*180, c['mmf_fft'])

    phi = [c['alfa0']/np.pi*180, c['alfa0']/np.pi*180]
    y = [min(c['mmf_fft']), 1.1*max(c['mmf_fft'])]
    plt.plot(phi, y, '--')
    plt.annotate("", xy=(phi[0], y[0]),
                 xytext=(0, y[0]), arrowprops=dict(arrowstyle="->"))

    plt.grid()
    plt.show()

    svg = wdgs.diagram()
    tree = ET.ElementTree(ET.fromstring(svg))
    tree.write('wind.svg')
    print('SVG file "wind.svg" created')
