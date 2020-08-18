'''
Performs Runge-Kutta integration to the 6 coupled differential equations for
the Lorenz Force equation.

Edit (June 9th, 2020): I feel like there should be a much nicer implementation...
'''

import os, sys
import numpy as np

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "gtracr"))

from gtracr.magnetic_field import MagneticField
from gtracr.constants import SPEED_OF_LIGHT


class RungeKutta:
    def __init__(self, mass, charge, stepsize):
        self.bfield = MagneticField()
        self.charge = charge
        self.mass = mass
        # self.coeff = charge / mass
        self.stepSize = stepsize

    # obtained from D.F.Smart, M.A.Shea, Sept. 1, 2004
    # radial velocity DE
    def dprdt(self, t, r, theta, phi, pr, ptheta, pphi, gamma):
        term1 = (self.charge / (self.mass * gamma)) * (
            ptheta * self.bfield.Bphi(r, theta, phi) -
            self.bfield.Btheta(r, theta, phi) * pphi)
        term2 = ptheta**2. / r
        term3 = pphi**2. / r

        return term1 + term2 + term3
        # lor_term = (ptheta * self.bfield.Bphi(r, theta, phi) -
        #             self.bfield.Btheta(r, theta, phi) * pphi)
        # accel_term = r * (ptheta**2. + pphi**2. * np.sin(theta)**2.)

        # return (self.coeff / gamma) * lor_term + accel_term

    # theta component velocity DE
    def dpthetadt(self, t, r, theta, phi, pr, ptheta, pphi, gamma):
        term1 = (self.charge /
                 (self.mass * gamma)) * (pphi * self.bfield.Br(r, theta, phi) -
                                         self.bfield.Bphi(r, theta, phi) * pr)
        term2 = (pr * ptheta) / r
        term3 = pphi**2. / (r * np.tan(theta))
        return term1 - term2 + term3

        # lor_term = (pphi * self.bfield.Br(r, theta, phi) -
        #             self.bfield.Bphi(r, theta, phi) * pr)
        # accel_term = r * pphi**2. * np.sin(theta) * np.cos(
        #     theta) - 2. * pr * ptheta

        # return ((self.coeff / gamma) * lor_term + accel_term) / r

    # phi comp vel/. DE
    def dpphidt(self, t, r, theta, phi, pr, ptheta, pphi, gamma):
        term1 = (self.charge / (self.mass * gamma)) * (
            self.bfield.Btheta(r, theta, phi) * pr -
            self.bfield.Br(r, theta, phi) * ptheta)
        term2 = (pr * pphi) / r
        term3 = (ptheta * pphi) / (r * np.tan(theta))
        return term1 - term2 - term3

        # lor_term = (self.bfield.Btheta(r, theta, phi) * vr -
        #             self.bfield.Br(r, theta, phi) * vtheta)
        # accel_term = 2. * vphi * (vr * np.sin(theta) +
        #                           r * vtheta * np.cos(theta))

        # return (
        #     (self.coeff / gamma) * lor_term - accel_term) / (r * np.sin(theta))

    # evaluate 4th-order Runge Kutta with 6 coupled differential equations
    # this code can be reduced greatly by removing certain arguments, however by
    # making the code more general those arguments have to stay there.
    # Edit 2: this only performs one iteration of RK
    # the position DEs are replaced with the spherical definition for velocity
    def evaluate(self, ival):

        #set initial conditions to array
        t = ival[0]
        r = ival[1]
        th = ival[2]
        ph = ival[3]
        pr = ival[4]
        pth = ival[5]
        pph = ival[6]

        pmag = np.sqrt(pr**2. + pth**2. + pph**2.)
        gamma = np.sqrt(1 + (pmag / (self.mass * SPEED_OF_LIGHT))**2.)

        # get the RK terms
        # k,l,m are for drdt, dthdt, dphdt
        # p,q,s are for momenta
        k1 = self.stepSize * pr
        l1 = self.stepSize * (pth / r)
        m1 = self.stepSize * (pph / (r * np.sin(th)))

        # coeff1 = particle.charge / (gamma1 * particle.mass)
        a1 = self.stepSize * self.dprdt(t, r, th, ph, pr, pth, pph, gamma)
        b1 = self.stepSize * self.dpthetadt(t, r, th, ph, pr, pth, pph, gamma)
        c1 = self.stepSize * self.dpphidt(t, r, th, ph, pr, pth, pph, gamma)

        k2 = self.stepSize * (pr + 0.5 * a1)
        l2 = self.stepSize * ((pth + 0.5 * b1) / (r + 0.5 * k1))
        m2 = self.stepSize * ((pph + 0.5 * c1) / ((r + 0.5 * k1) *
                                                  (np.sin(th + 0.5 * l1))))
        pmag2 = np.sqrt((pr + 0.5 * a1)**2. + (pth + 0.5 * b1)**2. +
                        (pph + 0.5 * c1)**2.)
        gamma2 = np.reciprocal(np.sqrt(1 - (pmag2 / SPEED_OF_LIGHT)**2.))
        # coeff2 = particle.charge / (gamma2 * particle.mass)
        a2 = self.stepSize * self.dprdt(
            t + 0.5 * self.stepSize, r + 0.5 * k1, th + 0.5 * l1, ph +
            0.5 * m1, pr + 0.5 * a1, pth + 0.5 * b1, pph + 0.5 * c1, gamma)
        b2 = self.stepSize * self.dpthetadt(
            t + 0.5 * self.stepSize, r + 0.5 * k1, th + 0.5 * l1, ph +
            0.5 * m1, pr + 0.5 * a1, pth + 0.5 * b1, pph + 0.5 * c1, gamma)
        c2 = self.stepSize * self.dpphidt(
            t + 0.5 * self.stepSize, r + 0.5 * k1, th + 0.5 * l1, ph +
            0.5 * m1, pr + 0.5 * a1, pth + 0.5 * b1, pph + 0.5 * c1, gamma)

        k3 = self.stepSize * (pr + 0.5 * a2)
        l3 = self.stepSize * ((pth + 0.5 * b2) / (r + 0.5 * k2))
        m3 = self.stepSize * ((pph + 0.5 * c2) / ((r + 0.5 * k2) *
                                                  (np.sin(th + 0.5 * l2))))
        pmag3 = np.sqrt((pr + 0.5 * a2)**2. + (pth + 0.5 * b2)**2. +
                        (pph + 0.5 * c2)**2.)
        gamma3 = np.reciprocal(np.sqrt(1 - (pmag3 / SPEED_OF_LIGHT)**2.))
        # coeff3 = particle.charge / (gamma3 * particle.mass)
        a3 = self.stepSize * self.dprdt(
            t + 0.5 * self.stepSize, r + 0.5 * k2, th + 0.5 * l2, ph +
            0.5 * m2, pr + 0.5 * a2, pth + 0.5 * b2, pph + 0.5 * c2, gamma)
        b3 = self.stepSize * self.dpthetadt(
            t + 0.5 * self.stepSize, r + 0.5 * k2, th + 0.5 * l2, ph +
            0.5 * m2, pr + 0.5 * a2, pth + 0.5 * b2, pph + 0.5 * c2, gamma)
        c3 = self.stepSize * self.dpphidt(
            t + 0.5 * self.stepSize, r + 0.5 * k2, th + 0.5 * l2, ph +
            0.5 * m2, pr + 0.5 * a2, pth + 0.5 * b2, pph + 0.5 * c2, gamma)

        k4 = self.stepSize * (pr + a3)
        l4 = self.stepSize * ((pth + b3) / (r + k3))
        m4 = self.stepSize * ((pph + c3) / ((r + k3) * (np.sin(th + l3))))
        pmag4 = np.sqrt((pr + a3)**2. + (pth + b3)**2. + (pph + c3)**2.)
        gamma4 = np.reciprocal(np.sqrt(1 - (pmag4 / SPEED_OF_LIGHT)**2.))
        # coeff4 = particle.charge / (gamma4 * particle.mass)
        a4 = self.stepSize * self.dprdt(t + self.stepSize, r + k3, th + l3,
                                        ph + m3, pr + a3, pth + b3, pph + c3,
                                        gamma)
        b4 = self.stepSize * self.dpthetadt(t + self.stepSize, r + k3, th + l3,
                                            ph + m3, pr + a3, pth + b3,
                                            pph + c3, gamma)
        c4 = self.stepSize * self.dpphidt(t + self.stepSize, r + k3, th + l3,
                                          ph + m3, pr + a3, pth + b3, pph + c3,
                                          gamma)

        # get the weighted sum of each component
        k = (1. / 6.) * k1 + (1. / 3.) * k2 + (1. / 3.) * k3 + (1. / 6.) * k4
        l = (1. / 6.) * l1 + (1. / 3.) * l2 + (1. / 3.) * l3 + (1. / 6.) * l4
        m = (1. / 6.) * m1 + (1. / 3.) * m2 + (1. / 3.) * m3 + (1. / 6.) * m4
        a = (1. / 6.) * a1 + (1. / 3.) * a2 + (1. / 3.) * a3 + (1. / 6.) * a4
        b = (1. / 6.) * b1 + (1. / 3.) * b2 + (1. / 3.) * b3 + (1. / 6.) * b4
        c = (1. / 6.) * c1 + (1. / 3.) * c2 + (1. / 3.) * c3 + (1. / 6.) * c4
        # iterate by weighted sum of stepsize
        r = r + k
        th = th + l
        ph = ph + m
        pr = pr + a
        pth = pth + b
        pph = pph + c
        t = t + self.stepSize

        return np.array([t, r, th, ph, pr, pth, pph])


'''
# from gtracr.utils import gamma, vmag_spherical
from gtracr.magnetic_field import B_r, B_theta, B_phi
from gtracr.constants import SPEED_OF_LIGHT


# obtained from D.F.Smart, M.A.Shea, Sept. 1, 2004
# radial velocity DE
def dvrdt(t, r, theta, phi, vr, vtheta, vphi, coeff):
    term1 = coeff * (vtheta * B_phi(r, theta, phi) -
                     B_theta(r, theta, phi) * vphi)
    term2 = vtheta**2. / r
    term3 = vphi**2. / r

    return term1 + term2 + term3


# theta component velocity DE
def dvthetadt(t, r, theta, phi, vr, vtheta, vphi, coeff):
    term1 = coeff * (vphi * B_r(r, theta, phi) - B_phi(r, theta, phi) * vr)
    term2 = (vr * vtheta) / r
    term3 = vphi**2. / (r * np.tan(theta))
    return term1 - term2 + term3


# phi comp vel/. DE
def dvphidt(t, r, theta, phi, vr, vtheta, vphi, coeff):
    term1 = coeff * (B_theta(r, theta, phi) * vr - B_r(r, theta, phi) * vtheta)
    term2 = (vr * vphi) / r
    term3 = (vtheta * vphi) / (r * np.tan(theta))
    return term1 - term2 - term3


# evaluate 4th-order Runge Kutta with 6 coupled differential equations
# this code can be reduced greatly by removing certain arguments, however by
# making the code more general those arguments have to stay there.
# Edit 2: this only performs one iteration of RK
# the position DEs are replaced with the spherical definition for velocity
def runge_kutta(particle, h, ival):

    #set initial conditions to array
    t = ival[0]
    r = ival[1]
    th = ival[2]
    ph = ival[3]
    vr = ival[4]
    vth = ival[5]
    vph = ival[6]

    # get the RK terms
    # k,l,m are for drdt, dthdt, dphdt
    # p,q,s are for momenta
    k1 = h * vr
    l1 = h * vth / r
    m1 = h * vph / (r * np.sin(th))

    vel1 = np.sqrt(vr**2. + (r * vth)**2. + (r * np.sin(th) * vph)**2.)
    gamma1 = np.reciprocal(np.sqrt(1 - (vel1 / SPEED_OF_LIGHT)**2.))
    coeff1 = particle.charge / (gamma1 * particle.mass)
    a1 = h * dvrdt(t, r, th, ph, vr, vth, vph, coeff1)
    b1 = h * dvthetadt(t, r, th, ph, vr, vth, vph, coeff1)
    c1 = h * dvphidt(t, r, th, ph, vr, vth, vph, coeff1)

    k2 = h * vr + 0.5 * a1
    l2 = h * vth + 0.5 * b1 / (r + 0.5 * k1)
    m2 = h * vph + 0.5 * c1 / ((r + 0.5 * k1) * (np.sin(th + 0.5 * l1)))
    vel2 = np.sqrt((vr + 0.5 * a1)**2. + ((r + 0.5 * k1) *
                                          (vth + 0.5 * b1))**2. +
                   ((r + 0.5 * k1) * np.sin(th + 0.5 * l1) *
                    (vph + 0.5 * c1))**2.)
    gamma2 = np.reciprocal(np.sqrt(1 - (vel2 / SPEED_OF_LIGHT)**2.))
    coeff2 = particle.charge / (gamma2 * particle.mass)
    a2 = h * dvrdt(t + 0.5 * h, r + 0.5 * k1, th + 0.5 * l1, ph + 0.5 * m1,
                   vr + 0.5 * a1, vth + 0.5 * b1, vph + 0.5 * c1, coeff2)
    b2 = h * dvthetadt(t + 0.5 * h, r + 0.5 * k1, th + 0.5 * l1, ph + 0.5 * m1,
                       vr + 0.5 * a1, vth + 0.5 * b1, vph + 0.5 * c1, coeff2)
    c2 = h * dvphidt(t + 0.5 * h, r + 0.5 * k1, th + 0.5 * l1, ph + 0.5 * m1,
                     vr + 0.5 * a1, vth + 0.5 * b1, vph + 0.5 * c1, coeff2)

    k3 = h * vr + 0.5 * a2
    l3 = h * vth + 0.5 * b2 / (r + 0.5 * k2)
    m3 = h * vph + 0.5 * c2 / ((r + 0.5 * k2) * (np.sin(th + 0.5 * l2)))
    vel3 = np.sqrt((vr + 0.5 * a2)**2. + ((r + 0.5 * k2) *
                                          (vth + 0.5 * b2))**2. +
                   ((r + 0.5 * k2) * np.sin(th + 0.5 * l2) *
                    (vph + 0.5 * c2))**2.)
    gamma3 = np.reciprocal(np.sqrt(1 - (vel3 / SPEED_OF_LIGHT)**2.))
    coeff3 = particle.charge / (gamma3 * particle.mass)
    a3 = h * dvrdt(t + 0.5 * h, r + 0.5 * k2, th + 0.5 * l2, ph + 0.5 * m2,
                   vr + 0.5 * a2, vth + 0.5 * b2, vph + 0.5 * c2, coeff3)
    b3 = h * dvthetadt(t + 0.5 * h, r + 0.5 * k2, th + 0.5 * l2, ph + 0.5 * m2,
                       vr + 0.5 * a2, vth + 0.5 * b2, vph + 0.5 * c2, coeff3)
    c3 = h * dvphidt(t + 0.5 * h, r + 0.5 * k2, th + 0.5 * l2, ph + 0.5 * m2,
                     vr + 0.5 * a2, vth + 0.5 * b2, vph + 0.5 * c2, coeff3)

    k4 = h * vr + a3
    l4 = h * vth + b3 / (r + k3)
    m4 = h * vph + c3 / ((r + k3) * (np.sin(th + l3)))
    vel4 = np.sqrt((vr + a3)**2. + ((r + k3) * (vth + b3))**2. +
                   ((r + k3) * np.sin(th + l3) * (vph + c3))**2.)
    gamma4 = np.reciprocal(np.sqrt(1 - (vel4 / SPEED_OF_LIGHT)**2.))
    coeff4 = particle.charge / (gamma4 * particle.mass)
    a4 = h * dvrdt(t + h, r + k3, th + l3, ph + m3, vr + a3, vth + b3,
                   vph + c3, coeff4)
    b4 = h * dvthetadt(t + h, r + k3, th + l3, ph + m3, vr + a3, vth + b3,
                       vph + c3, coeff4)
    c4 = h * dvphidt(t + h, r + k3, th + l3, ph + m3, vr + a3, vth + b3,
                     vph + c3, coeff4)

    # get the weighted sum of each component
    k = (1. / 6.) * k1 + (1. / 3.) * k2 + (1. / 3.) * k3 + (1. / 6.) * k4
    l = (1. / 6.) * l1 + (1. / 3.) * l2 + (1. / 3.) * l3 + (1. / 6.) * l4
    m = (1. / 6.) * m1 + (1. / 3.) * m2 + (1. / 3.) * m3 + (1. / 6.) * m4
    a = (1. / 6.) * a1 + (1. / 3.) * a2 + (1. / 3.) * a3 + (1. / 6.) * a4
    b = (1. / 6.) * b1 + (1. / 3.) * b2 + (1. / 3.) * b3 + (1. / 6.) * b4
    c = (1. / 6.) * c1 + (1. / 3.) * c2 + (1. / 3.) * c3 + (1. / 6.) * c4
    # iterate by weighted sum of stepsize
    r = r + k
    th = th + l
    ph = ph + m
    vr = vr + a
    vth = vth + b
    vph = vph + c
    t = t + h

    return np.array([t, r, th, ph, vr, vth, vph])
'''
# def wsum(n1, n2, n3, n4):
#     return (1. / 6.) * n1 + (1. / 3.) * n2 + (1. / 3.) * n3 + (1. / 6.) * n4

# # obtained from D.F.Smart, M.A.Shea, Sept. 1, 2004
# # radial velocity DE
# def dvrdt(t, r, theta, phi, vr, vtheta, vphi, particle):
#     term1 = particle.charge * (
#         vtheta * B_phi(r, theta, phi) - B_theta(r, theta, phi) * vphi) / (
#             particle.mass * gamma(vmag_spherical(vr, vtheta, vphi, r, theta)))
#     term2 = vtheta**2. / r
#     term3 = vphi**2. / r

#     return term1 + term2 + term3

#     # lorenz_const = particle.charge / (particle.mass*gamma(vmag_spherical(vr, vtheta, vphi, r, theta)))
#     # lor_term = (vtheta * B_phi(r, theta, phi) - B_theta(r, theta, phi) * vphi)
#     # accel_term = r*(vtheta**2. - vphi**2.*np.sin(theta))

#     # return lorenz_const*lor_term + accel_term

#     # gam = gamma(vmag_spherical(vr, vtheta, vphi, r, theta))
#     # lor_consts = particle.charge / (particle.mass*gam*SPEED_OF_LIGHT**2.)
#     # # term1 = particle.charge * (
#     # #     vtheta * B_phi(r, theta, phi) - B_theta(r, theta, phi) * vphi) / (
#     # #         particle.mass * gam)

#     # lor_term1 = (vtheta * B_phi(r, theta, phi) - B_theta(r, theta, phi) * vphi) * (SPEED_OF_LIGHT**2. - vr**2.)
#     # lor_term2 = r*vr*vtheta*(B_phi(r, theta, phi) * vr - vphi * B_r(r, theta, phi))
#     # lor_term3 = r*vr*vphi*np.sin(theta)*(B_theta(r, theta, phi) * vr - B_r(r, theta, phi) * vtheta)

#     # accel_term1 = r*vtheta**2.
#     # accel_term2 = r*np.sin(theta)**2.*vphi**2.

#     # return accel_term1 + accel_term2 + lor_consts*(lor_term1 - lor_term2 + lor_term3)

# # theta component velocity DE
# def dvthetadt(t, r, theta, phi, vr, vtheta, vphi, particle):
#     term1 = particle.charge * (vphi * B_r(r, theta, phi) - B_phi(r, theta, phi) * vr) / (
#         particle.mass * gamma(vmag_spherical(vr, vtheta, vphi, r, theta)))
#     term2 = (vr * vtheta) / r
#     term3 = vphi**2. / (r * np.tan(theta))
#     return term1 - term2 + term3

#     # lorenz_const = particle.charge / (particle.mass*gamma(vmag_spherical(vr, vtheta, vphi, r, theta)))
#     # lor_term = (vphi * B_r(r, theta, phi) - B_phi(r, theta, phi) * vr)
#     # accel_term = r*vphi**2.*np.sin(theta)*np.cos(theta) - 2.*vr*vtheta

#     # return (lorenz_const*lor_term + accel_term) / r

#     # gam = gamma(vmag_spherical(vr, vtheta, vphi, r, theta))
#     # lor_consts = particle.charge / (particle.mass*gam*SPEED_OF_LIGHT**2.)

#     # lor_term1 = r*vr*vtheta*(vtheta * B_phi(r, theta, phi) - B_theta(r, theta, phi) * vphi)
#     # lor_term2 = (B_phi(r, theta, phi) * vr - vphi * B_r(r, theta, phi))*(SPEED_OF_LIGHT**2. - (r*vtheta)**2.)
#     # lor_term3 = r**2.*vtheta*vphi*np.sin(theta)*(B_theta(r, theta, phi) * vr - B_r(r, theta, phi) * vtheta)

#     # accel_term1 = 2.*vr*vtheta
#     # accel_term2 = r*vphi**2.*np.sin(theta)*np.cos(theta)

#     # return (accel_term2 - accel_term1 + lor_consts*(lor_term1 - lor_term2 + lor_term3)) / r

# # phi comp vel/. DE
# def dvphidt(t, r, theta, phi, vr, vtheta, vphi, particle):
#     term1 = particle.charge * (
#         B_theta(r, theta, phi) * vr - B_r(r, theta, phi) * vtheta) / (
#             particle.mass * gamma(vmag_spherical(vr, vtheta, vphi, r, theta)))
#     term2 = (vr * vphi) / r
#     term3 = (vtheta * vphi) / (r * np.tan(theta))
#     return term1 - term2 - term3

#     # lorenz_const = particle.charge / (particle.mass*gamma(vmag_spherical(vr, vtheta, vphi, r, theta)))
#     # lor_term = (B_theta(r, theta, phi) * vr - B_r(r, theta, phi) * vtheta)
#     # accel_term = 2.*vphi*(vr*np.sin(theta) + r*vtheta*np.cos(theta))

#     # return (lorenz_const*lor_term - accel_term) / (r*np.sin(theta))

#     # gam = gamma(vmag_spherical(vr, vtheta, vphi, r, theta))
#     # lor_consts = particle.charge / (particle.mass*gam*SPEED_OF_LIGHT**2.)

#     # lor_term1 = r*vr*vphi*np.sin(theta)*(vtheta * B_phi(r, theta, phi) - B_theta(r, theta, phi) * vphi)
#     # lor_term2 = r**2.*vphi*vtheta*np.sin(theta)*(B_phi(r, theta, phi) * vr - vphi * B_r(r, theta, phi))
#     # lor_term3 = (B_theta(r, theta, phi) * vr - B_r(r, theta, phi) * vtheta)*(SPEED_OF_LIGHT**2. - (r*vphi*np.sin(theta))**2.)

#     # accel_term1 = 2.*vr*vphi*np.sin(theta)
#     # accel_term2 = 2.*r*vtheta*vphi*np.cos(theta)

#     # return (- accel_term2 - accel_term1 + lor_consts*(lor_term1 - lor_term2 + lor_term3)) / (r*np.sin(theta))

# evaluate 4th-order Runge Kutta with 6 coupled differential equations
# this code can be reduced greatly by removing certain arguments, however by
# making the code more general those arguments have to stay there.
# Edit 2: this only performs one iteration of RK
# the position DEs are replaced with the spherical definition for velocity
# def euler(particle, h, ival):

#set initial conditions to array
# t = ival[0]
# r = ival[1]
# th = ival[2]
# ph = ival[3]
# vr = ival[4]
# vth = ival[5]
# vph = ival[6]

# vrn = vr + h * dvrdt(t, r, th, ph, vr, vth, vph, particle)
# vthn = vth + h * dvthetadt(t, r, th, ph, vr, vth, vph, particle)
# vphn = vph + h * dvphidt(t, r, th, ph, vr, vth, vph, particle)

# r += h * vr
# th += h * vth
# ph += h * vph

# vr = vrn
# vth = vthn
# vph = vphn

# t += h

# return np.array([t, r, th, ph, vr, vth, vph])
