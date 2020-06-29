import os, sys
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "gtracr"))
# sys.path.append(os.path.join(os.getcwd(), "..", "gtracr"))

# from gtracr.trajectory import ParticleTrajectory
# from gtracr.utils import spherical_to_cartesian
from gtracr.constants import EARTH_RADIUS, DEG_TO_RAD, RAD_TO_DEG
from gtracr.utils import *
from gtracr.runge_kutta import runge_kutta, euler
from gtracr.add_particle import particle_dict

def func(latitude, longitude, start_altitude, stop_altitude, zenith, azimuth, particle, energy):
     

    # transform the variables into ECEF coordinates

    r0 = EARTH_RADIUS + start_altitude
    # longitude and latitude to (r0, theta0, phi0)
    theta0 = ((90. -  latitude) * DEG_TO_RAD)  # theta defined in [0, pi], theta = 0 at equator
    # phi = ((180. + longitude) * DEG_TO_RAD)  
    phi0 = ((longitude) * DEG_TO_RAD)  # phi defined in [-pi, pi], phi = 0 at prime meridian

    x0 = r0*np.sin(theta0)*np.cos(phi0)
    y0 = r0*np.sin(theta0)*np.sin(phi0)
    z0 = r0*np.cos(theta0)

    # print(r0, theta0, phi0)

    # RK variables
    maxStep = 10000
    stepSize = 0.1
    key_list = ["t", "r", "theta", "phi", "pr", "ptheta", "pphi"]
    results = {key: np.zeros(maxStep) for key in key_list}

    # now specify some zenith and azimuthal angle
    # zenith = 160.
    # azimuth = 270.

    # Rotation matrix from tangent plane coordinate system to geocentric coordinate system
    # source: http://archive.psas.pdx.edu/CoordinateSystem/Latitude_to_LocalTangent.pdf 
    row1 = np.array([-np.sin(longitude*DEG_TO_RAD), -np.cos(longitude*DEG_TO_RAD)*np.sin(latitude*DEG_TO_RAD), np.cos(latitude*DEG_TO_RAD)*np.cos(longitude*DEG_TO_RAD)])
    row2 = np.array([np.cos(longitude*DEG_TO_RAD), -np.sin(latitude*DEG_TO_RAD)*np.sin(longitude*DEG_TO_RAD), np.cos(latitude*DEG_TO_RAD)*np.sin(longitude*DEG_TO_RAD)])
    row3 = np.array([0., np.cos(latitude*DEG_TO_RAD), np.sin(latitude*DEG_TO_RAD)])

    # row1 = np.array([np.sin(latitude+90)*np.cos(), -np.cos(longitude)*np.sin(latitude), np.cos(latitude)*np.cos(longitude)])
    # row2 = np.array([np.cos(longitude), -np.sin(latitude)*np.sin(longitude), np.cos(latitude)*np.sin(longitude)])
    # row3 = np.array([0., np.cos(latitude), np.sin(latitude)])

    tf_matrix = np.array([row1, row2, row3])

    # get the cartesian coordinates in the local tangent plane coordinate system from zenith and azimuth
    l = stepSize
    xi = zenith * DEG_TO_RAD
    alpha = azimuth * DEG_TO_RAD

    xt = l*np.sin(xi)*np.cos(alpha)
    yt = l*np.sin(xi)*np.sin(alpha)
    zt = l*np.cos(xi)


    # transform zenith and azimuthal vector coordinates to ECEF
    # print(np.shape(np.dot(tf_matrix, np.array([xt, yt, zt]))), np.dot(tf_matrix, np.array([xt, yt, zt])))
    ecef_coords = np.array([x0, y0, z0]) + np.dot(tf_matrix, np.array([xt, yt, zt]))

    x = ecef_coords[0]
    y = ecef_coords[1]
    z = ecef_coords[2]
    # print(EARTH_RADIUS)
    print(ecef_coords)

    r = np.sqrt(x**2. + y**2. + z**2.)
    # theta = np.arctan((np.sqrt(x**2. + y**2.)) / z)
    theta = np.arccos(z / r)
    phi = np.arctan(y / x)
    

    # then r1, the next part of the integration step, would be the transformed coordinate
    # d = np.sin(xi) * np.cos(alpha)

    # print(d, l, xi, alpha)

    # phi = phi0 - np.arctan2(d, r0 * np.tan(theta0))
    # # rcos(phi), obtained from cosine law
    # rcosphi = np.sqrt((r0 * np.cos(phi0))**2. +
    #                   (np.cos(alpha))**2. +
    #                   2. * r0 * np.cos(alpha) * np.cos(phi0)*np.cos(xi))
    # r = rcosphi / np.cos(phi)
    # theta = theta0 - (d / rcosphi)

    # r1 = np.sqrt(r0**2. + 1. + 2.*r0*np.cos(xi))
    # theta1 = theta0 - np.arcsin(np.sin(xi) / r1)
    # phi1 = phi0

    # rtest = np.sqrt(r0**2. + 1.)
    # thetatest = theta0 - np.arccos(r0 / r1)
    # print(r0, theta0)
    # print(r1, theta1)
    # print(rtest, thetatest)
    # l = 1.
    # # if xi > (-np.pi / 2.) and xi < (np.pi / 2.):
    # #     sign = 1.
    # # elif xi > (np.pi / 2.) and xi < ((3.*np.pi) / 2.):
    # #     sign = -1.
    # # r = sign*np.sqrt(r0**2. + l**2. + 2.*r0*np.cos(xi))

    # r = np.sqrt(r0**2. + l**2. + 2.*r0*np.cos(xi))
    
    # theta = theta0 - np.arcsin((l*np.sin(xi)) / r)

    # phi = phi0

    
    # cos_ag = ((r*np.sin(theta))**2. - (r0*np.sin(theta0))**2. - (l*np.sin(xi)**2.)**2.) / (-2.*r0*np.sin(theta0)*l*np.sin(theta)**2.)
    # while np.isnan(np.arccos(cos_ag)):
    #     if cos_ag > 1:
    #         cos_ag -= 1
    #     elif cos_ag < -1:
    #         cos_ag += 1
    #     print(cos_ag)
    # gmma = np.arccos(cos_ag) - alpha

    # phi = phi0 + np.arcsin((l*np.sin(xi)**2.*np.sin(alpha+gmma)) / (r*np.sin(theta)))
    # if np.sin(theta0) < 1e-10 or np.sin(theta) < 1e-10:
    #     phi = 0.
    # else:
    #     # side1 = np.hypot(r0*np.sin(theta0), r*np.sin(theta))
    #     # side2 = np.hypot(l*np.sin(xi)*np.sin(theta0), r*np.sin(theta))
    #     # side3 = np.hypot(l*np.sin(xi)*np.sin(theta0), r0*np.sin(theta0))
    #     # cos_delphi = (-(side1)**2. + (side2)**2. + (side3)**2.) / (2.*side2*side3)
    #     cos_delphi = ((-l*np.sin(xi)*np.sin(theta0))**2. + (r0*np.sin(theta0))**2. + (r*np.sin(theta))**2.) / (2.*r0*np.sin(theta0)*l*np.sin(theta))
    #     print(cos_delphi)
    #     delphi = np.arccos(cos_delphi)
    #     while np.isnan(np.arccos(cos_delphi)):
    #         if cos_delphi > 1:
    #             cos_delphi -= 1
    #         elif cos_delphi < -1:
    #             cos_delphi += 1
    #     print(cos_delphi)
    #     delphi = np.arccos(cos_delphi)
    #     phi = phi0 + delphi



    print(r, theta, phi)
    # print(phi)

    # print(r, theta, phi, rcosphi)

    # set particle momenta and get their spherical coordinate equivalents
    particle.set_momentum_from_energy(energy)
    # # print(particle.momentum)


    # particle momentum is known in local tangent plane coordinates
    # so we should transform this into ECEF coordinates

    # components in local tangent plane coordinates
    # (pr0, ptheta0, pphi0) = vp_components_spherical(particle.momentum, r, theta)

    # particle.set_velocity()

    # (vr0, vtheta0, vphi0) = vp_components_spherical(particle.velocity, r, theta)


    # vx0 = vr0*np.sin(theta0)*np.cos(phi0) + r0*vtheta0*np.cos(theta0)*np.cos(phi0) - r0*vphi0*np.sin(theta0)*np.sin(phi0)
    # vy0 = vr0*np.sin(theta0)*np.sin(phi0) + r0*vtheta0*np.cos(theta0)*np.sin(phi0) +r0*vphi0*np.sin(theta0)*np.cos(phi0)
    # vz0 = vr0*np.cos(theta0) - r0*vtheta0*np.sin(theta0)


    # # transform zenith and azimuthal vector coordinates to ECEF
    # ecef_coords = np.array([x0, y0, z0]) + np.dot(tf_matrix, np.array([vx0, vy0, vz0]))

    # vx = ecef_coords[0]
    # vy = ecef_coords[1]
    # vz = ecef_coords[2]

    # # r = np.sqrt(vx**2. + vy**2. + vz**2.)
    # # theta = np.arctan((np.sqrt(vx**2. + vy**2.)) / vz)
    # # phi = np.arctan(vy / vx)
    
    # vr = vx*np.sin(theta)*np.cos(phi) + vy*np.sin(theta)*np.sin(phi) + vz*np.cos(theta)
    # vtheta = (vx*np.cos(theta)*np.cos(phi) + vy*np.cos(theta)*np.sin(phi) - vz*np.sin(theta)) / r
    # vphi = (-vx*np.sin(phi) + vy*np.cos(phi)) / (r*np.sin(theta))









    
    # print(particle.velocity)
    # (pr0, ptheta0, pphi0) = vp_components_spherical(particle.momentum, r0,
    #                                                 theta0)
    (pr0, ptheta0, pphi0) = (0., 0., 0.)
    (pr, ptheta, pphi) = vp_components_spherical(particle.momentum, r, theta)
    # # (vr, vtheta, vphi) = vp_components_spherical(particle.velocity, r, theta)
    # l = 1.
    # pr = np.sqrt(pr0**2. + l**2. + 2.*pr0*np.cos(xi))
    # ptheta = ptheta0 - np.arcsin((l*np.sin(xi)) / pr)
    # cos_ag = ((pr*np.sin(theta))**2. - (pr0*np.sin(theta0))**2. - (l*np.sin(xi)**2.)**2.) / (-2.*pr0*np.sin(theta0)*l*np.sin(theta)**2.)
    # # print(cos_ag-2)
    # ag = np.arccos(cos_ag)
    # # print(ag)
    # if np.isneginf(ag):
    #     ag = 0.
    # elif np.isneginf(ag):
    #     ag = np.pi
    # elif np.isnan(ag):
    #     while np.isnan(np.arccos(cos_ag)):
    #         if cos_ag > 1:
    #             cos_ag -= 1
    #         elif cos_ag < -1:
    #             cos_ag += 1
    #         # print(cos_ag)
    #     ag = np.arccos(cos_ag)
    # gmma = ag - alpha

    # pphi = pphi0 + np.arcsin((l*np.sin(xi)**2.*np.sin(alpha+gmma)) / (pr*np.sin(theta)))

    # print(pr, ptheta, pphi)



    # particle.set_velocity()
    # (vr0, vtheta0, vphi0) = vp_components_spherical(particle.velocity, r0,
    #                                                 theta0)

    # (vr, vtheta, vphi) = vp_components_spherical(particle.velocity, r,
    #                                                 theta)


    particle.set_velocity()

    print(particle.velocity)

    # vr0 = particle.velocity
    # vtheta0 = particle.velocity / l
    # vphi0 = particle.velocity / (l*np.sin(xi)) if np.abs(xi) < 1e-10 else 0.

    # # vx0 = vr0*np.sin(theta0)*np.cos(phi0)
    # # vy0 = vr0*np.sin(theta0)*np.sin(phi0)
    # # vz0 = vr0*np.cos(theta0)

    # vx0 = vr0*np.sin(theta0)*np.cos(phi0) + r0*vtheta0*np.cos(theta0)*np.cos(phi0) - r0*vphi0*np.sin(theta0)*np.sin(phi0)
    # vy0 = vr0*np.sin(theta0)*np.sin(phi0) + r0*vtheta0*np.cos(theta0)*np.sin(phi0) +r0*vphi0*np.sin(theta0)*np.cos(phi0)
    # vz0 = vr0*np.cos(theta0) - r0*vtheta0*np.sin(theta0)

    vxt = particle.velocity*np.sin(xi)*np.cos(alpha)
    vyt = particle.velocity*np.sin(xi)*np.sin(alpha)
    vzt = particle.velocity*np.cos(xi)


    print(np.sqrt(vxt**2. + vyt**2. + vzt**2.))



    # l = np.sqrt(vx0**2. + vy0**2. + vz0**2.)
    # xi = zenith * DEG_TO_RAD
    # alpha = azimuth * DEG_TO_RAD

    # vxt = l*np.sin(xi)*np.cos(alpha)
    # vyt = l*np.sin(xi)*np.sin(alpha)
    # vzt = l*np.cos(xi)


    # transform zenith and azimuthal vector coordinates to ECEF
    ecef_coords = np.dot(tf_matrix, np.array([vxt, vyt, vzt]))

    print(tf_matrix)

    # the thing above needs fixing, there should be some consideration between the local tangent plane velocities
    # with them being velocities themselves, some time derivative stuff should be considered
    # this could also resolve the translation issue

    print(ecef_coords)

    vx = ecef_coords[0]
    vy = ecef_coords[1]
    vz = ecef_coords[2]

    # r = np.sqrt(vx**2. + vy**2. + vz**2.)
    # theta = np.arctan((np.sqrt(vx**2. + vy**2.)) / vz)
    # phi = np.arctan(vy / vx)
    
    vr = vx*np.sin(theta)*np.cos(phi) + vy*np.sin(theta)*np.sin(phi) + vz*np.cos(theta)
    vtheta = (vx*np.cos(theta)*np.cos(phi) + vy*np.cos(theta)*np.sin(phi) - vz*np.sin(theta)) / r
    vphi = (-vx*np.sin(phi) + vy*np.cos(phi)) / (r*np.sin(theta))

    print(vr, vtheta, vphi)

    (pr, ptheta, pphi) = gamma(vmag_spherical(vr, vtheta, vphi, r, theta))*particle.mass*np.array([vr, vtheta, vphi])

    particle.set_momentum_from_velocity()

    # (pr, ptheta, pphi) = vp_components_spherical(particle.momentum, r, theta)

    
    # (vr, vtheta, vphi) = vp_components_spherical(particle.velocity, r, theta)
    # (vr, vtheta, vphi) = vp_components_spherical(particle.velocity, r, theta)
    # l = 1.
    # vr = np.sqrt(vr0**2. + l**2. + 2.*vr0*np.cos(xi))
    # # vr = sign*np.sqrt(vr0**2. + l**2. + 2.*vr0*np.cos(xi))
    # vtheta = vtheta0 - np.arcsin((l*np.sin(xi)) / vr)

    # vphi = vphi0

    # cos_ag = ((vr*np.sin(theta))**2. - (vr0*np.sin(theta0))**2. - (l*np.sin(xi)**2.)**2.) / (2.*vr0*np.sin(theta0)*l*np.sin(theta)**2.)
    # # print(cos_ag-2)
    # ag = np.arccos(cos_ag)
    # print(ag)
    # if np.isneginf(ag):
    #     ag = 0.
    # elif np.isneginf(ag):
    #     ag = np.pi
    # elif np.isnan(ag):
    #     while np.isnan(np.arccos(cos_ag)):
    #         if cos_ag > 1:
    #             cos_ag -= 1
    #         elif cos_ag < -1:
    #             cos_ag += 1
    #         # print(cos_ag)
    #     ag = np.arccos(cos_ag)
    
    # # print(ag)
    # # while np.isnan(np.arccos(cos_ag)):
    # #     if cos_ag > 1:
    # #         cos_ag -= 1
    # #     elif cos_ag < -1:
    # #         cos_ag += 1
    # #     print(cos_ag)
    # gmma = ag - alpha

    # vphi = vphi0 + np.arcsin(-(l*np.sin(xi)**2.*np.sin(alpha+gmma)) / (vr*np.sin(theta)))

    # if np.sin(theta0) < 1e-10 or np.sin(theta) < 1e-10:
    #     vphi = 0.
    # else:
    #     # side1 = np.hypot(vr0*np.sin(theta0), vr*np.sin(theta))
    #     # side2 = np.hypot(l*np.sin(xi)*np.sin(theta0), vr*np.sin(theta))
    #     # side3 = np.hypot(l*np.sin(xi)*np.sin(theta0), vr0*np.sin(theta0))
    #     # cos_delphi = (-(side1)**2. + (side2)**2. + (side3)**2.) / (2.*side2*side3)
    #     cos_delphi = (-(l*np.sin(xi)*np.sin(theta0))**2. + (vr0*np.sin(theta0))**2. + (vr*np.sin(theta))**2.) / (2.*vr0*np.sin(theta0)*l*np.sin(theta))
    #     print(cos_delphi)
    #     delphi = np.arccos(cos_delphi)
    #     while np.isnan(np.arccos(cos_delphi)):
    #         if cos_delphi > 1:
    #             cos_delphi -= 1
    #         elif cos_delphi < -1:
    #             cos_delphi += 1
    #     delphi = np.arccos(cos_delphi)
    #     vphi = vphi0 + delphi

    print(vr, vtheta, vphi)
    # (pr0, pth0, pph0) = get_sphcomp_momentum(p0, r0, theta0)
    # (vr, vtheta, vphi) = vp_components_spherical(particle.velocity, r, theta)
    
    # initial time
    t0 = 0.
    t = t0 + stepSize
    # print(pr0, ptheta0, pphi0)
    # print(pr, ptheta, pphi)
    # print(vr, vtheta, vphi)

    

    # append the initial value (the origin in local reference frame) and the first value after zenith / azimuth transformation
    results["t"][0:2] = [t0, t]
    results["r"][0:2] = [r0, r]
    results["theta"][0:2] = [theta0, theta]
    results["phi"][0:2] = [phi0, phi]
    results["pr"][0:2] = [pr0, pr]
    results["ptheta"][0:2] = [ptheta0, ptheta]
    results["pphi"][0:2] = [pphi0, pphi]

    # perform the integration
    initial_values = (t, r, theta, phi, vr, vtheta, vphi)

    # initial_values = (t, r0, theta0, phi0, vr0, vtheta0,
    #         vphi0)

    # print(initial_values)

    i = 2
    while i < maxStep - 2:

        # # get the RK variables
        (t, r, theta, phi, vr, vtheta,
         vphi) = runge_kutta(particle, stepSize, initial_values)

        # get the RK variables
        # (t, r, theta, phi, vr, vtheta,
        #  vphi) = euler(particle, stepSize, initial_values)

        # convert velocities to momenta
        vmag = vmag_spherical(vr, vtheta, vphi, r, theta)
        particle.momentum = gamma(vmag) * particle.mass * vmag
        # particle.momentum = vmag_spherical(pr, ptheta, pphi, r, theta)
        particle.set_rigidity_from_momentum()
        # print(particle.rigidity)

        # (pr, ptheta, pphi) = vp_components_spherical(particle.momentum, r, theta)
        (pr, ptheta, pphi) = gamma(vmag)*particle.mass*np.array([vr, vtheta, vphi])

        # print(pr, ptheta, pphi)

        # append
        results["t"][i] = t
        results["r"][i] = r
        results["theta"][i] = theta
        results["phi"][i] = phi
        results["pr"][i] = pr
        results["ptheta"][i] = ptheta
        results["pphi"][i] = pphi

        # if particle has escaped
        if r > EARTH_RADIUS + stop_altitude:
            break

        # if particle touched Earth again
        if r < EARTH_RADIUS:
            break

        # initial_values = (t, r1, theta1, phi1, vr1, vtheta1,
        #     vphi1)

        initial_values = (t, r, theta, phi, vr, vtheta, vphi)

        i += 1

    # trim all zeros
    for key, arr in list(results.items()):
        results.update({key: np.trim_zeros(arr, 'b')})

    # plot
    t = results["t"]
    (x, y, z) = spherical_to_cartesian(results["r"] / EARTH_RADIUS,
                                       results["theta"], results["phi"])
    return results

if __name__ == "__main__":

    # some initial variables
    latitude = 0.
    longitude = -60.
    start_altitude = 20.
    stop_altitude = 565.

    particle = particle_dict["p-"]
    energy = 12.

    result = func(latitude, longitude, start_altitude, stop_altitude, 0., 0., particle, energy)
    # result2 = func(0., 0., 20., 565., 70., 90., particle, energy)

    # plot
    t = result["t"]
    (x, y, z) = spherical_to_cartesian(result["r"] / EARTH_RADIUS,
                                       result["theta"], result["phi"])

    # t2 = result2["t"]
    # (x2, y2, z2) = spherical_to_cartesian(result2["r"] / EARTH_RADIUS,
    #                                    result2["theta"], result2["phi"])
    

    plt.scatter(x, y, c="k")
    # plt.scatter(x2, y2, c="r")
    # plt.xlim([-.5, .5])
    # plt.ylim([-.5, .5])
    plt.show()

    plt.scatter(x, z, c="k")
    # plt.scatter(x2, z2, c="r")
    # plt.xlim([-.5, .5])
    # plt.ylim([-.5, .5])
    plt.show()

    plt.scatter(y, z, c="k")
    # plt.scatter(y2, z2, c="r")
    # plt.xlim([-.5, 1.5])
    # plt.ylim([-1.5, 1.5])
    plt.show()

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    cm = ax.scatter(x, y, z, c="k", marker='o')
    # cm = ax.scatter(x2, y2, z2, c="r", marker='o')
    fig.colorbar(cm, ax=ax)
    # plt.colorbar()
    # plt.savefig("test.png")
    plt.show()





    result1 = func(0., 0., 20., 565., 90., 0., particle_dict["p+"], 30.)
    result2 = func(0., 0., 20., 565., 90., 180., particle_dict["p+"], 30.)

    # plot
    t1 = result1["t"]
    (x1, y1, z1) = spherical_to_cartesian(result1["r"] / EARTH_RADIUS,
                                       result1["theta"], result1["phi"])

    t2 = result2["t"]
    (x2, y2, z2) = spherical_to_cartesian(result2["r"] / EARTH_RADIUS,
                                       result2["theta"], result2["phi"])
    

    plt.scatter(x1, y1, c="k")
    plt.scatter(x2, y2, c="r")
    # plt.xlim([-1.5, 1.5])
    # plt.ylim([-1.5, 1.5])
    plt.show()

    plt.scatter(x1, z1, c="k")
    plt.scatter(x2, z2, c="r")
    # plt.xlim([-1.5, 1.5])
    # plt.ylim([-1.5, 1.5])
    plt.show()

    plt.scatter(y1, z1, c="k")
    plt.scatter(y2, z2, c="r")
    # plt.xlim([-1.5, 1.5])
    # plt.ylim([-1.5, 1.5])
    plt.show()

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    cm = ax.scatter(x1, y1, z1, c="k", marker='o')
    cm = ax.scatter(x2, y2, z2, c="r", marker='o')
    fig.colorbar(cm, ax=ax)
    # plt.colorbar()
    # plt.savefig("test.png")
    plt.show()




'''
        # print(pr, ptheta, pphi)

        # particle.set_velocity()

        # # set particle momenta and get their spherical coordinate equivalents
        # # particle.set_momentum(energy)
        # # particle.set_velocity()
        # (pr1, ptheta1,pphi1) = vp_components_spherical(particle.momentum, r1, theta1)
        # # (pr, ptheta,pphi) = vp_components_spherical(particle.momentum, r, theta)
        # # (pr0, pth0, pph0) = get_sphcomp_momentum(p0, r0, theta0)
        # (vr1, vtheta1, vphi1) = vp_components_spherical(particle.velocity, r1, theta1)
        # # initial time
        # # t0 = 0.
        # t = t + stepSize

        # print(vr1, vtheta1, vphi1)

        # # convert velocities to momenta
        # vmag = vmag_spherical(vr, vtheta, vphi, r, theta)
        # particle.momentum = gamma(vmag) * particle.mass * vmag
        # # particle.momentum = vmag_spherical(pr, ptheta, pphi, r, theta)
        # particle.set_rigidity_from_momentum()
        # # print(particle.rigidity)

        # (pr, ptheta,
        #     pphi) = vp_components_spherical(particle.momentum, r, theta)

        # print(pr, ptheta, pphi)

        # (t, r, theta, phi, vr, vtheta,
        #     vphi) = euler(particle, stepSize, initial_values)

        # print((t, r, theta, phi, vr, vtheta, vphi))

        # # xi = np.arccos((r-EARTH_RADIUS))
        # xi = (np.pi / 2.) - np.sin(theta0 - theta)

        # r1 = np.sqrt(r**2. + 10.**2. + 2.*r*np.cos(xi))
        # theta1 = theta - np.arcsin((10.*np.sin(xi)) / r)
        # phi1 = phi

        # print(r1, theta1, phi1)

        # print(r, theta, phi, rcosphi)
'''