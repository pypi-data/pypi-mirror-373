"""
  femagtools.machine.utils

  auxiliary module
"""
import numpy as np
import numpy.linalg as la
import scipy.interpolate as ip
import logging
from .. import parstudy, windings
from ..model import MachineModel

logger = logging.getLogger(__name__)

loss_models = {
    "modified steinmetz": 10,
    "bertotti": 11,
    "jordan": 1,
    "steinmetz": 1
}

def K(d):
    """space phasor transformation matrix
    (Inverse Park Transformation) T-1 * dq --> abc
    arguments:
      d: rotation angle

    returns transformation matrix
    """
    return np.array((
        (np.cos(d), -np.sin(d)),
        (np.cos(d-2*np.pi/3), -np.sin(d-2*np.pi/3)),
        (np.cos(d+2*np.pi/3), -np.sin(d+2*np.pi/3))))


def T(d):
    """space phasor transformation matrix
    (Park Transformation) T * abc --> dq
    arguments:
      d: rotation angle

    returns transformation matrix
    """
    return 2/3*np.array((
        (np.cos(d), np.cos(d-2*np.pi/3), np.cos(d+2*np.pi/3)),
        (-np.sin(d), -np.sin(d-2*np.pi/3), -np.sin(d+2*np.pi/3))))


def invpark(a, q, d):
    """ convert a dq vector to the abc reference frame
    (inverse park transformation)

    Args:
        a: rotation angle
        d: value in direct axis
        q: value in quadrature axis
    """
    if np.isscalar(a) and np.isscalar(q) and np.isscalar(d):
        return np.dot(K(a), (d, q))
    if np.isscalar(q) and np.isscalar(d):
        return np.array([K(x).dot((d, q)) for x in a]).T
    return np.array([K(x).dot((y, z)) for x, y, z in zip(a, d, q)]).T


KTH = 0.0039  # temperature coefficient of resistance
TREF = 20.0  # reference temperature of resistance
EPS = 1e-13


def xiskin(w, temp, zeta, kth=KTH):
    return zeta*np.sqrt(abs(w)/(2*np.pi)/(50*(1+kth*(temp-TREF))))


def kskinl(xi, nl):
    xi2 = 2*xi
    nl2 = nl*nl
    if np.isscalar(xi):
        if xi < EPS:
            k = 1
        else:
            k = (3 / (nl2*xi2)*(np.sinh(xi2) - np.sin(xi2)) /
                 (np.cosh(xi2)-np.cos(xi2)) +
                 ((nl2-1)/(nl2*xi)*(np.sinh(xi)+np.sin(xi)) /
                          (np.cosh(xi)+np.cos(xi))))
    else:
        xi2 = xi2[xi > EPS]
        k = np.ones(np.asarray(xi).shape)
        k[xi > 1e-12] = (3 / (nl2*xi2)*(np.sinh(xi2) - np.sin(xi2)) /
                         (np.cosh(xi2)-np.cos(xi2)) +
                         ((nl2-1)/(nl2*xi)*(np.sinh(xi)+np.sin(xi)) /
                          (np.cosh(xi)+np.cos(xi))))
    return k


def kskinr(xi, nl):
    xi2 = 2*xi
    nl2 = nl*nl
    return xi*((np.sinh(xi2)+np.sin(xi2))/(np.cosh(xi2)-np.cos(xi2))) + \
        ((nl2-1) / 3 * xi2*((np.sinh(xi)-np.sin(xi)) /
                            (np.cosh(xi)+np.cos(xi))))


def wdg_resistance(wdg, n, g, aw, da1, hs, lfe, sigma=56e6):
    """return winding resistance per phase in Ohm
    Arguments:
    wdg: (Winding) winding
    n: (int) number of wires per coil side
    g: (int) number of parallel coil groups
    lfe: length of stator lamination stack in m
    aw: wire cross section area m2
    da1: bore diameter m
    hs: slot height
    sigma: (float) conductivity of wire material 1/Ohm m
    """
    # mean length of one turn
    lt = 2.8*(da1+hs)/2*wdg.yd*2*np.pi/wdg.Q + 16e-3 + 2*lfe
    return wdg.turns_per_phase(n, g)*lt/sigma/aw/g


def wdg_inductance(wdg, n, g, da1, lfe, ag):
    """return winding inductance per phase in H
    Arguments:
    wdg: (Winding) winding
    n: (int) number of wires per coil side
    g: (int) number of parallel coil groups
    da1: bore diameter in m
    lfe: length of stator lamination stack in m
    ag: length of airgap in m
    """
    return wdg.inductance(n, g, da1, lfe, ag)


def skin_resistance(r0, w, temp, zeta, gam=0, nh=1, kth=KTH):
    """return eddy current resistance of winding or rotor bar
    Arguments:
    r0: (float) dc resistance
    w: (float) current frequency in rad
    temp: (float) conductor temperature in deg Celsius
    zeta: (float) skin effect coefficient (penetration depth)
    gam: (float) ratio of length of end winding and length of slot (0..1)
    nh: (int) number of vertical conductors in slot
    kth: (float) temperature coefficient (Default = 0.0039, Cu)"""
    xi = xiskin(w, temp, zeta)
    if np.isscalar(xi):
        if xi < 1e-12:
            k = 1
        else:
            k = (gam + kskinr(xi, nh)) / (1. + gam)
    else:
        k = np.ones(np.asarray(w).shape)
        k[xi > 1e-12] = (gam + kskinr(xi[xi > 1e-12], nh)) / (1. + gam)
    return r0*(1.+kth*(temp - TREF))*k
# return r0*(1.+KTH*(temp - TREF))*(gam + kskinr(xi, nh)) / (1. + gam)


def skin_leakage_inductance(l0, w, temp, zeta, nl=1, pl2v=0.5, kth=KTH):
    """return eddy current leakage inductance of rotor bar
    Arguments:
    l0: (float) dc inductance
    w: (float) current frequency in rad
    temp: (float) conductor temperature in deg Celsius
    zeta: (float) skin effect coefficient (penetration depth)
    nl: (int) number of vertical conductors in slot
    pl2v: (float) variable coefficient (0..1)
    kth: (float) temperature coefficient (Default = 0.0039, Cu)"""
    return l0*(1.0+pl2v*(kskinl(
        xiskin(w, temp, zeta, kth), nl)-1))


def wdg_leakage_inductances(machine):
    """calculate slot leakage and end winding inductances
    ref: Design of Rotating Electrical Machines
    Juha Pyrhönen, Tapani Jokinen, Valeria Hrabovcova
    (Ed. 2008) page 236ff
    """
    wdgk = 'windings' if 'windings' in machine else 'winding'
    wdg = windings.Winding(
        {'Q': machine['stator']['num_slots'],
         'm': machine[wdgk]['num_phases'],
         'p': machine['poles']//2,
         'l': machine[wdgk]['num_layers'],
         'yd': machine[wdgk]['coil_span']})
    n1 = wdg.turns_per_phase(machine[wdgk]['num_wires'],
                             machine[wdgk]['num_par_wdgs'])
    m = wdg.m
    p = wdg.p
    Q = wdg.Q
    D = machine['bore_diam']
    W = wdg.yd
    taup = Q/2/p
    eps = 1 - W/taup
    slotmodel = [k for k in machine['stator'] if isinstance(
        machine['stator'][k], dict)][-1]
    hs = machine['stator'][slotmodel].get('slot_height',
                                          (machine['outer_diam']-D)/2)
    taus = (D+hs)*np.pi/Q

    b1 = machine['stator'][slotmodel]['slot_width']
    h1 = machine['stator'][slotmodel]['slot_h1']
    h2 = machine['stator'][slotmodel]['slot_h2']
    h3 = 0
    hd = 0
    if machine['stator'][slotmodel].get('tooth_width', 0):
        b4 = taus-machine['stator'][slotmodel]['tooth_width'] + \
            2*machine['stator'][slotmodel].get('slot_r1', 0)
    else:
        b4 = machine['stator'][slotmodel].get('wedge_width1', taus/2) + \
            2*machine['stator'][slotmodel].get('slot_r1', 0)
    h41 = 0
    h42 = h41
    h4 = hs - h1 - h2
    lfe = machine['lfe']
    k1 = 1-9*eps/16
    k2 = 1-3*eps/4
    lbda = k1*(h4-hd)/3/b4 + k2*(h3/b4+h1/b1+h2/(b4-b1)*np.log(b4/b1))+hd/4/b4
    mue0 = 4*np.pi*1e-7
    Lu = 4*m/Q*mue0*lfe*n1**2*lbda
    q = wdg.q
    wew = (1-eps)*(D + h4)*np.pi/2/p
    lew = (lfe-wew)/2
    lmdew = 0.55
    lmw0 = 0.35
    lmdw = 2*lew*lmdew + wew*lmw0
    Lew = 4*m/Q*q*n1**2*mue0*lmdw
    return Lu, Lew


def create_wdg(machine):
    """create winding from machine parameters"""
    wdgk = 'windings' if 'windings' in machine else 'winding'
    wpar = {'Q': machine['stator']['num_slots'],
            'm': machine[wdgk]['num_phases'],
            'p': machine['poles']//2}

    if 'coil_span' in machine[wdgk]:
        wpar['yd'] = machine[wdgk]['coil_span']
    if 'num_layers' in machine[wdgk]:
        wpar['l'] = machine[wdgk]['num_layers']
    return windings.Winding(wpar)


def betai1(iq, id):
    """return beta and amplitude of dq currents"""
    return (np.arctan2(id, iq),
            la.norm((id, iq), axis=0)/np.sqrt(2.0))


def iqd(beta, i1):
    """return qd currents of beta and amplitude"""
    return np.sqrt(2.0)*i1*np.array([np.cos(beta),
                                     np.sin(beta)])


def puconv(dqpar, p, NR, UR, IR):
    """convert dqpar to per unit
    arguments:
    dqpar: dict from ld-iq or psid-psiq identification
    p: pole pairs
    NR: ref speed in 1/s
    UR: ref voltage per phase in V
    IR: ref current per phase in A
    """
    WR = 2*np.pi*NR*p
    PSIR = UR/WR
    SR = 3*UR*IR
    if 'beta' in dqpar:
        dqp = dict(beta=dqpar['beta'], losses=dict())
        dqp['i1'] = np.array(dqpar['i1'])/IR
    elif 'iq' in dqpar:
        dqp = dict(iq=np.array(dqpar['iq)'])/IR*np.sqrt(2), losses=dict())
        dqp['id'] = np.array(dqpar['id'])/IR*np.sqrt(2)
    else:
        raise ValueError('invalid dqpar')
    for k in 'psid', 'psiq':
        dqp[k] = np.array(dqpar[k])/PSIR
    if 'losses' in dqpar:
        for k in ('magnet', 'styoke_hyst', 'styoke_eddy',
                  'stteeth_hyst', 'stteeth_eddy', 'rotor_hyst', 'rotor_eddy'):
            dqp['losses'][k] = np.array(dqpar['losses'][k])/SR
        dqp['losses']['speed'] = p*dqpar['losses']['speed']/WR
        dqp['losses']['ef'] = dqpar['losses']['ef']
        dqp['losses']['hf'] = dqpar['losses']['hf']
    return dqp


def dqpar_interpol(xfit, dqpars, ipkey='temperature'):
    """return interpolated parameters at temperature or exc_current

    Arguments:
      xfit -- temperature or exc_current to fit dqpars
      dqpars -- list of dict with id, iq (or i1, beta), Psid and Psiq values
      ipkey -- key (string) to interpolate
    """
    dqtype = ''
    if set(('i1', 'beta')).issubset(dqpars[0]):
        dqtype = 'ldq'
    elif set(('id', 'iq')).issubset(dqpars[0]):
        dqtype = 'psidq'
    else:
        raise ValueError("missing current in dqpars parameter")
    ckeys = ('i1', 'beta') if dqtype == 'ldq' else ('id', 'iq')
    fpip = {k: dqpars[0][k] for k in ckeys}
    fpip['losses'] = dict()
    for k in ckeys:
        curr = np.array([f[k] for f in dqpars], dtype=object)
        shape = curr.shape
        if curr.shape != (len(dqpars), len(curr[0])):
            raise ValueError("current range conflict")
        curr = curr.astype(float)
        if not np.array([np.allclose(curr[0], c)
                         for c in curr[1:]]).all():
            raise ValueError("current range conflict")

    try:
        speed = np.array([d['losses']['speed'] for d in dqpars])
        if (np.max(speed) - np.min(speed))/np.mean(speed) > 1e-3:
            raise ValueError("losses: speed conflict")
    except KeyError:
        pass

    sorted_dqpars = sorted(dqpars, key=lambda d: d[ipkey])
    x = [f[ipkey] for f in sorted_dqpars]
    for k in ('psid', 'psiq'):
        m = np.array([f[k] for f in sorted_dqpars]).T
        if len(x) > 2:
            fpip[k] = np.array(
                [[ip.UnivariateSpline(x, y, k=2)(xfit)
                  for y in row] for row in m]).T
        else:
            fpip[k] = ip.interp1d(
                x, m, fill_value='extrapolate')(xfit).T

    for k in ('styoke_hyst', 'stteeth_hyst',
              'styoke_eddy', 'stteeth_eddy',
              'rotor_hyst', 'rotor_eddy',
              'magnet'):
        try:
            m = np.array([f['losses'][k] for f in sorted_dqpars]).T
            if len(x) > 2:
                fpip['losses'][k] = np.array(
                    [[ip.UnivariateSpline(x, y, k=2)(xfit)
                      for y in row] for row in m]).T
            else:
                fpip['losses'][k] = ip.interp1d(
                    x, m, fill_value='extrapolate')(xfit).T
        except KeyError:
            pass

    fpip['losses']['speed'] = dqpars[0]['losses']['speed']
    for f in ('hf', 'ef'):
        if f in dqpars[0]['losses']:
            fpip['losses'][f] = dqpars[0]['losses'][f]
    return x, fpip


def dqparident(workdir, engine, temp, machine,
               magnetizingCurves, magnetMat=[], condMat=[],
               **kwargs):
    """return list of parameters of equivalent circuit for PM machines

    arguments:
    workdir -- directory for intermediate files
    engine -- calculation driver (multiproc, docker, condor)

    temp -- list of magnet temperatures in degree Celsius
    machine -- dict() with machine parameters
    magnetizingCurves -- list of dict() with BH curves
    magnetMat -- list of dict() with magnet material properties
    condMat -- list of dict() with conductor material properties

    optional arguments:
    num_cur_steps: number of current steps (default 5)
    num_beta_steps: number of current steps (default 7 per quadrant)
    speed: rotor speed in 1/s (default 160/p)
    i1_max: maximum current in A rms (default approx 3*i1nom)
    period_frac: (int) fraction of rotating angle (default 6)
    dqtype: (str) type of identification: 'ldq' (default), 'psidq'
    cmd: femag executable
    feloss: jordan, steinmetz, modified steinmetz, bertotti
    """
    import pathlib

    try:
        defspeed = 160/machine['poles']
    except KeyError:
        if kwargs.get('speed', 0) == 0:
            raise ValueError('rated speed missing')
        defspeed = kwargs['speed']

    lfe = machine['lfe']
    wdgk = 'windings' if 'windings' in machine else 'winding'
    g = machine[wdgk].get('num_par_wdgs', 1)
    N = machine[wdgk]['num_wires']
    if 'cufilfact' in machine[wdgk]:
        fcu = machine[wdgk]['cufilfact']
    elif 'fillfac' in machine[wdgk]:
        fcu = machine[wdgk]['fillfac']
    else:
        fcu = 0.42

    try:
        wdg = create_wdg(machine)
    except KeyError:
        pass
    model = MachineModel(machine)
    if kwargs.get('i1_max', 0):
        i1_max = kwargs['i1_max']
    else:
        try: # calc basic dimensions if not fsl or dxf model
            Jmax = 30e6  # max current density in A/m2
            Acu = fcu*model.slot_area()  # approx. copper area of one slot
            i1_max = round(g*Acu/wdg.l/N*Jmax/10)*10
        except KeyError:
            raise ValueError('i1_max missing')

    # winding resistance
    try:
        da1 = machine['bore_diam']
        hs = model.slot_height()
        if 'wire_gauge' in machine[wdgk]:
            aw = machine[wdgk]['wire_gauge']
        elif 'dia_wire' in machine[wdgk]:
            aw = np.pi*machine[wdgk].get('dia_wire', 1e-3)**2/4
        elif ('wire_width' in machine[wdgk]) and ('wire_height' in machine[wdgk]):
            aw = machine[wdgk]['wire_width']*machine[wdgk]['wire_height']
        else:  # wire diameter from slot area
            Q1 = wdg.Q
            aw = 0.75 * fcu * np.pi*da1*hs/Q1/wdg.l/N
        r1 = float(wdg_resistance(wdg, N, g, aw, da1, hs, lfe))
    except (NameError, KeyError) as ex:
        r1 = 0  # cannot calc winding resistance

    n = len(temp)
    dqtype = kwargs.get('dqtype', 'ldq')
    num_cur_steps = kwargs.get('num_cur_steps', 5)
    if dqtype == 'ldq':
        parvardef = {
            "decision_vars": [
                {"values": sorted(2*temp), "name": "magn_temp"},
                {"values": n*[0, -90], "name": "beta_max"},
                {"values": n*[-90, -180], "name": "beta_min"}
            ]
        }
    else:
        delta = round(i1_max*np.sqrt(2)/num_cur_steps)
        iqmax = num_cur_steps*delta
        idmin = -iqmax
        parvardef = {
            "decision_vars": [
                {"values": sorted(2*temp), "name": "magn_temp"},
                {"values": n*[0, -iqmax], "name": "miniq"},
                {"values": n*[iqmax, 0], "name": "maxiq"}
            ]
        }

    parvar = parstudy.List(
        workdir, condMat=condMat,
        magnetizingCurves=magnetizingCurves,
        magnets=magnetMat, cmd=kwargs.get('cmd', None))

    leakfile = pathlib.Path(workdir) / 'end_wind_leak.dat'
    leakfile.unlink(missing_ok=True)

    period_frac = kwargs.get('period_frac', 6)
    if machine.get('external_rotor', False) and period_frac > 1:
        logger.warning("period frac for external rotor requires GT femag version >= 2024")

    if dqtype == 'ldq':
        simulation = dict(
            calculationMode='ld_lq_fast',
            i1_max=kwargs.get('i1_max', i1_max),
            magn_temp=20,
            wind_temp=20,
            beta_max=0,
            beta_min=-90,
            num_move_steps=kwargs.get('num_move_steps', 26),
            num_par_wdgs=machine[wdgk].get('num_par_wdgs', 1),
            num_cur_steps=num_cur_steps,
            num_beta_steps=kwargs.get('num_beta_steps', 7),
            speed=kwargs.get('speed', defspeed),
            period_frac=period_frac)
    else:
        simulation = dict(
            calculationMode='psd_psq_fast',
            magn_temp=20,
            wind_temp=20,
            maxiq=0,
            miniq=0,
            maxid=0,
            minid=idmin,
            num_move_steps=kwargs.get('num_move_steps', 26),
            num_par_wdgs=machine[wdgk].get('num_par_wdgs', 1),
            delta_id=delta,
            delta_iq=delta,
            speed=kwargs.get('speed', defspeed),
            period_frac=period_frac)

    if kwargs.get("feloss", 0):
        simulation["feloss"] = kwargs["feloss"]
        machine["calc_fe_loss"] = loss_models[kwargs["feloss"].lower()]

    # TODO: cleanup()  # remove previously created files in workdir
    # start calculation
    results = parvar(parvardef, machine, simulation, engine)

    if 'poles' not in machine:  # dxf model?
        machine['poles'] = 2*results['f'][0]['machine']['p']
        da1 = 2*results['f'][0]['machine']['fc_radius']
    if 'bore_diam' in machine:
        da1 = machine['bore_diam']
    ls1 = 0
    try:
        leakages = [float(x)
                    for x in leakfile.read_text().split()]
        ls1 += leakages[1]  # TODO: np.linalg.norm(leakages[1:])
    except:
        logger.warning("No end winding leakage")

    try:
        rotor_mass = sum(results['f'][-1]['weights'][-1])
    except KeyError:
        rotor_mass = 0  # need femag classic > rel-9.3.x-48-gca42bbd0

    if rotor_mass == 0:
        try:
            nc = parvar.femag.read_nc()
            rotor_mass = float(sum(nc.get_mass()[1].values()))
            logger.info("rotor mass from nc-file: %.1f kg", rotor_mass)
        except StopIteration:
            logger.warning("Could not read nc-file. Setting rotor_mass = 0!")

    dq = []
    if dqtype == 'ldq':
        for i in range(0, len(results['f']), 2):
            d = dict(i1=results['f'][i]['ldq']['i1'],
                     beta=(results['f'][i+1]['ldq']['beta'][:-1]
                           + results['f'][i]['ldq']['beta']))
            d.update(
                {k: np.vstack((np.array(results['f'][i+1]['ldq'][k])[:-1, :],
                               np.array(results['f'][i]['ldq'][k]))).tolist()
                 for k in ('psid', 'psiq', 'torque', 'ld', 'lq', 'psim')})
            dq.append(d)
    else:
        for i in range(0, len(results['f']), 2):
            d = dict(id=results['f'][i]['psidq']['id'],
                     iq=(results['f'][i+1]['psidq']['iq'][:-1]
                         + results['f'][i]['psidq']['iq']))
            d.update(
                {k: np.vstack((np.array(results['f'][i+1]['psidq'][k])[:-1, :],
                               np.array(results['f'][i]['psidq'][k]))).tolist()
                 for k in ('psid', 'psiq', 'torque')})
            d.update(
                {k: np.vstack((np.array(results['f'][i+1]['psidq_ldq'][k])[:-1, :],
                               np.array(results['f'][i]['psidq_ldq'][k]))).tolist()
                 for k in ('ld', 'lq', 'psim')})
            dq.append(d)
    # collect existing losses only
    losskeymap = {'magnet': 'magnet'}
    losskeys = [k for k in results['f'][0][dqtype]['losses']
                if len(k.split('_')) > 1] + ['magnet']
    for k in losskeys:
        if k.find('_') > -1:
            pref, post = k.split('_')
            if pref.lower() == 'stza':
                losskeymap[k] = 'stteeth_'+post
            elif pref.lower() == 'stjo':
                losskeymap[k] = 'styoke_'+post
            else:
                losskeymap[k] = k
    for i in range(0, len(results['f']), 2):
        j = i//2
        dq[j]['temperature'] = results['x'][0][i]
        if dqtype == 'ldq':
            dq[j]['losses'] = {losskeymap[k]: np.vstack(
                (np.array(results['f'][i+1][dqtype]['losses'][k])[:-1, :],
                 np.array(results['f'][i][dqtype]['losses'][k]))).tolist()
                               for k in losskeys}
        else:
            dq[j]['losses'] = {losskeymap[k]: np.hstack(
                (np.array(results['f'][i+1][dqtype]['losses'][k])[:, :-1],
                 np.array(results['f'][i][dqtype]['losses'][k]))).T.tolist()
                               for k in losskeys}
        dq[j]['losses']['speed'] = results['f'][i][dqtype]['losses']['speed']
        for k in ('hf', 'ef'):
            dq[j]['losses'][k] = results['f'][i]['lossPar'][k]

    dqpars = {
        'm': machine[wdgk]['num_phases'],
        'p': machine['poles']//2,
        'ls1': ls1,
        "rotor_mass": rotor_mass, "kfric_b": 1,
        dqtype: dq}
    if 'resistance' in machine[wdgk]:
        dqpars['r1'] = machine[wdgk]['resistance']
    else:
        if r1:
            dqpars['r1'] = r1
        else:
            model = parvar.femag.read_nc()
            try:
                nlayers = wdg.l
            except UnboundLocalError:
                wdg = create_wdg(machine)
                nlayers = wdg.l
            Q1 = wdg.Q
            istat = 0 if model.get_areas()[0]['slots'] else 1
            asl = model.get_areas()[istat]['slots']
            # diameter of wires
            aw = fcu*asl/Q1/nlayers/N
            hs = asl/(np.pi*da1/3)
            dqpars['r1'] = float(wdg_resistance(wdg, N, g, aw, da1, hs, lfe))

    if 'current_angles' in results['f'][0]:
        dqpars['current_angles'] = results['f'][0]['current_angles']
    return dqpars
