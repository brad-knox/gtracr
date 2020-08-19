// Runge Kutta integrator class

#include "uTrajectoryTracer.h"

#include <cmath>

#include <algorithm>
#include <array>
#include <functional>
#include <iostream>
#include <map>
#include <string>
#include <vector>

#include "MagneticField.h"
#include "constants.h"

// TrajectoryTracer class

// Constructor for TrajectoryTracer
// default: proton
uTrajectoryTracer::uTrajectoryTracer()
    : bfield_{MagneticField()}, charge_{1. * constants::ELEMENTARY_CHARGE},
      mass_{0.938 * constants::KG_PER_GEVC2}, escape_radius_{10. *
                                                             constants::RE},
      stepsize_{1e-5}, max_iter_{10000}, particle_escaped_{false} {}

// Requires the charge and mass of the particle
uTrajectoryTracer::uTrajectoryTracer(const int charge, const double &mass,
                                     const double &escape_radius = 10. *
                                                                   constants::RE,
                                     const double &stepsize = 1e-5,
                                     const int max_iter = 10000,
                                     const char bfield_type = 'd')
    : charge_{charge * constants::ELEMENTARY_CHARGE},
      mass_{mass * constants::KG_PER_GEVC2}, escape_radius_{escape_radius},
      stepsize_{stepsize}, max_iter_{max_iter}, particle_escaped_{false}
{
    switch (bfield_type)
    {
    case 'd':
        bfield_ = MagneticField();
    case 'i':
        // bfield = IGRF13();
        bfield_ = MagneticField();
    }
}

/* Evaluates the trajectory of the particle using a 4th-order Runge Kutta
algorithm.

Parameters
-----------
- t0 (double) :
    the initial time in seconds
- vec0 (std::array<double, 6>) :
      the initial six-vector (r0, theta0, phi0, pr0, ptheta0, pphi0) at time t0

Returns
--------
None

*/

void uTrajectoryTracer::evaluate(double &t0, std::array<double, 6> &vec0)
{
    // std::array<double, 7> traj_vector = vec0;
    // assign initial values from array to trajectory vector structure
    traj_vector_.t = t0;
    traj_vector_.r = vec0[1];
    traj_vector_.theta = vec0[2];
    traj_vector_.phi = vec0[3];
    traj_vector_.pr = vec0[4];
    traj_vector_.ptheta = vec0[5];
    traj_vector_.pphi = vec0[6];

    // start the integration process
    for (int i = 0; i < max_iter_; ++i)
    {
        // append to arrays first
        // to do this we need to convert spherical to cartesian

        // first rename the variables for readability
        // these can probably be const but lets leave that for now
        // double t = traj_vector[0];
        // double r = traj_vector[1];
        // double theta = traj_vector[2];
        // double phi = traj_vector[3];
        // double pr = traj_vector[4];
        // double ptheta = traj_vector[5];
        // double pphi = traj_vector[6];

        // evaluate a runge kutta step
        // return the next iteration of values
        // traj_vector = rk_step(traj_vector);
        perform_rkstep();
        // break condition depending on value of r
        // this is set based on if particle has "escaped"
        // or if the particle has reached back to earth
        // i.e. an allowed or forbidden trajectory

        // const double &radius = traj_vector[1];

        // an allowed trajectory
        if (traj_vector_.r > constants::RE + escape_radius_)
        {
            particle_escaped_ = true;
            // std::cout << "Allowed Trajectory!" << std::endl;
            break;
        }

        // a forbidden trajectory
        if (traj_vector_.r < constants::RE)
        {
            // std::cout << "Forbidden Trajectory!" << std::endl;
            break;
        }
    }
}

/* Evaluates the trajectory of the particle using a 4th-order Runge Kutta
algorithm and return a map that contains the information of the particle
trajectory. This will most often be used for debugging purposes to see the
actual trajectory.

Parameters
-----------
- t0 (double) :
    the initial time in seconds
- vec0 (std::array<double, 6>) :
     the initial six-vector (r0, theta0, phi0, pr0, ptheta0, pphi0) at time t0

Returns
--------
- trajectory_data (std::map<std::string, std::vector<double> >) :
    the trajectory information, that is, the time array of the trajectory
    and the six-vector of the trajectory in std::vectors.
    Notes:
    - keys are ["t", "r", "theta", "phi", "pr", "ptheta", "pphi"]
    - the final point of the trajectory is also contained in the map
    - std::vectors (dynamic arrays) are used since the length of each
      trajectory is not known at compile time.

*/

std::map<std::string, std::vector<double>>
uTrajectoryTracer::evaluate_and_get_trajectory(double &t0,
                                                 std::array<double, 6> &vec0)
{

    // a container that holds the variables throughout each step
    // variables are given in the order [t, r, theta, phi, pr, ptheta,
    //   pphi]
    // this can also be replaced with 7 doubles by moving the function
    //   rk_step
    // directly into the for loop
    traj_vector_.t = t0;
    traj_vector_.r = vec0[1];
    traj_vector_.theta = vec0[2];
    traj_vector_.phi = vec0[3];
    traj_vector_.pr = vec0[4];
    traj_vector_.ptheta = vec0[5];
    traj_vector_.pphi = vec0[6];

    // set up the vectors for the values on trajectory
    // in spherical coordinates
    std::vector<double> time_arr;
    std::vector<double> r_arr;
    std::vector<double> theta_arr;
    std::vector<double> phi_arr;
    std::vector<double> pr_arr;
    std::vector<double> ptheta_arr;
    std::vector<double> pphi_arr;

    // start the integration process
    for (int i = 0; i < max_iter_; ++i)
    {
        // append to arrays first
        // to do this we need to convert spherical to cartesian

        // first rename the variables for readability
        // these can probably be const but lets leave that for now
        double t = traj_vector_.t;
        double r = traj_vector_.r;
        double theta = traj_vector_.theta;
        double phi = traj_vector_.phi;
        double pr = traj_vector_.pr;
        double ptheta = traj_vector_.ptheta;
        double pphi = traj_vector_.pphi;

        time_arr.push_back(t);
        r_arr.push_back(r);
        theta_arr.push_back(theta);
        phi_arr.push_back(phi);
        pr_arr.push_back(pr);
        ptheta_arr.push_back(ptheta);
        pphi_arr.push_back(pphi);

        // evaluate a runge kutta step
        // return the next iteration of values
        // traj_vector = rk_step(traj_vector);
        perform_rkstep();

        // break condition depending on value of r
        // this is set based on if particle has "escaped"
        // or if the particle has reached back to earth
        // i.e. an allowed or forbidden trajectory

        // const double &radius = traj_vector[1];

        // an allowed trajectory
        if (traj_vector_.r > constants::RE + escape_radius_)
        {
            particle_escaped_ = true;
            // std::cout << "Allowed Trajectory!" << std::endl;
            break;
        }

        // a forbidden trajectory
        if (traj_vector_.r < constants::RE)
        {
            // std::cout << "Forbidden Trajectory!" << std::endl;
            break;
        }
    }

    // std::cout << "Total Number of iterations: " << i << std::endl;

    // convert the final values of the trajectory into a std::vector
    // to put this into our map
    // dont want the time component, so start from 2nd component of
    // trajectory vector
    // std::vector<double> final_values(traj_vector.begin() + 1,
    // traj_vector.end());
    std::vector<double> final_values{traj_vector_.r, traj_vector_.theta,
                                     traj_vector_.phi, traj_vector_.pr,
                                     traj_vector_.ptheta,
                                     traj_vector_.pphi};

    std::map<std::string, std::vector<double>> trajectory_data = {
        {"t", time_arr}, {"r", r_arr}, {"theta", theta_arr}, {"phi", phi_arr}, {"pr", pr_arr}, {"ptheta", ptheta_arr}, {"pphi", pphi_arr}, {"final_values", final_values}};

    return trajectory_data;
}

// ODEs based on relativistic Lorentz force equation with auxiliary terms
// acceleration in spherical coordinates drdt
inline double uTrajectoryTracer::dr_dt(double pr)
{
    return pr;
}

// dtheta dt
inline double uTrajectoryTracer::dtheta_dt(double r, double ptheta)
{
    return ptheta / r;
}
// dphidt
inline double uTrajectoryTracer::dphi_dt(double r, double theta, double pphi)
{
    return pphi / (r * sin(theta));
}
// dvrdt
inline double uTrajectoryTracer::dpr_dt(double r, double theta, double phi,
                                        double pr, double ptheta, double pphi)
{
    double lorentz_term = (-1. * charge_ * constants::ELEMENTARY_CHARGE) *
                          (ptheta * bfield_.Bphi(r, theta, phi) -
                           bfield_.Btheta(r, theta, phi) * pphi);
    double auxiliary_terms = ((ptheta * ptheta) / r) + ((pphi * pphi) / r);
    double dpr_dt = lorentz_term + auxiliary_terms;
    return dpr_dt;
}

// dpthetadt
inline double uTrajectoryTracer::dptheta_dt(double r, double theta, double phi,
                                            double pr, double ptheta,
                                            double pphi)
{
    double lorentz_term =
        (charge_ * constants::ELEMENTARY_CHARGE) *
        (bfield_.Bphi(r, theta, phi) * pr - pphi * bfield_.Br(r, theta, phi));
    double auxiliary_terms =
        ((pphi * pphi * cos(theta)) / (r * sin(theta))) - ((pr * ptheta) / r);
    double dptheta_dt = lorentz_term + auxiliary_terms;
    return dptheta_dt;
}

// dpphidt
inline double uTrajectoryTracer::dpphi_dt(double r, double theta, double phi,
                                          double pr, double ptheta,
                                          double pphi)
{
    double lorentz_term =
        (-1. * charge_ * constants::ELEMENTARY_CHARGE) *
        (pr * bfield_.Btheta(r, theta, phi) - bfield_.Br(r, theta, phi) *
                                                  ptheta);
    double auxiliary_terms =
        ((pr * pphi) / r) + ((ptheta * pphi * cos(theta)) / (r * sin(theta)));
    double dpphi_dt = lorentz_term - auxiliary_terms;
    return dpphi_dt;
}

// lorentz factor
inline double uTrajectoryTracer::gamma(double pr, double ptheta, double pphi)
{
    double momentum =
        sqrt((pr * pr) + (ptheta * ptheta) + (pphi * pphi)); // momentum
    double momentum_ratio =
        momentum / (mass_ * constants::SPEED_OF_LIGHT); // p / mc
    double gamma = sqrt(1. + (momentum_ratio * momentum_ratio));
    return gamma;
}

void uTrajectoryTracer::perform_rkstep()
{
    double t = traj_vector_.t;
    double r = traj_vector_.r;
    double theta = traj_vector_.theta;
    double phi = traj_vector_.phi;
    double pr = traj_vector_.pr;
    double ptheta = traj_vector_.ptheta;
    double pphi = traj_vector_.pphi;

    // evaluate relativistic mass here
    double rel_mass = mass_ * gamma(pr, ptheta, pphi) *
                      constants::KG_PER_GEVC2;

    double r_k1 = stepsize_ * dr_dt(pr);
    double theta_k1 = stepsize_ * dtheta_dt(r, ptheta);
    double phi_k1 = stepsize_ * dphi_dt(r, theta, pphi);
    double pr_k1 = stepsize_ * dpr_dt(r, theta, phi, pr, ptheta, pphi);
    double ptheta_k1 = stepsize_ * dptheta_dt(r, theta, phi, pr, ptheta, pphi);
    double pphi_k1 = stepsize_ * dpphi_dt(r, theta, phi, pr, ptheta, pphi);

    double r_k2 = stepsize_ * dr_dt(pr + 0.5 * pr_k1);
    double theta_k2 =
        stepsize_ * dtheta_dt(r + 0.5 * r_k1, ptheta + 0.5 * ptheta_k1);
    double phi_k2 = stepsize_ * dphi_dt(r + 0.5 * r_k1, theta + 0.5 * theta_k1,
                                        pphi + 0.5 * pphi_k1);
    double pr_k2 =
        stepsize_ * dpr_dt(r + 0.5 * r_k1, theta + 0.5 * theta_k1,
                           phi + 0.5 * phi_k1, pr + 0.5 * pr_k1,
                           ptheta + 0.5 * ptheta_k1, pphi + 0.5 * pphi_k1);
    double ptheta_k2 =
        stepsize_ * dptheta_dt(r + 0.5 * r_k1, theta + 0.5 * theta_k1,
                               phi + 0.5 * phi_k1, pr + 0.5 * pr_k1,
                               ptheta + 0.5 * ptheta_k1, pphi + 0.5 * pphi_k1);
    double pphi_k2 =
        stepsize_ * dpphi_dt(r + 0.5 * r_k1, theta + 0.5 * theta_k1,
                             phi + 0.5 * phi_k1, pr + 0.5 * pr_k1,
                             ptheta + 0.5 * ptheta_k1, pphi + 0.5 * pphi_k1);

    double r_k3 = stepsize_ * dr_dt(pr + 0.5 * pr_k2);
    double theta_k3 =
        stepsize_ * dtheta_dt(r + 0.5 * r_k2, ptheta + 0.5 * ptheta_k2);
    double phi_k3 = stepsize_ * dphi_dt(r + 0.5 * r_k2, theta + 0.5 * theta_k2,
                                        pphi + 0.5 * pphi_k2);
    double pr_k3 =
        stepsize_ * dpr_dt(r + 0.5 * r_k2, theta + 0.5 * theta_k2,
                           phi + 0.5 * phi_k2, pr + 0.5 * pr_k2,
                           ptheta + 0.5 * ptheta_k2, pphi + 0.5 * pphi_k2);
    double ptheta_k3 =
        stepsize_ * dptheta_dt(r + 0.5 * r_k2, theta + 0.5 * theta_k2,
                               phi + 0.5 * phi_k2, pr + 0.5 * pr_k2,
                               ptheta + 0.5 * ptheta_k2, pphi + 0.5 * pphi_k2);
    double pphi_k3 =
        stepsize_ * dpphi_dt(r + 0.5 * r_k2, theta + 0.5 * theta_k2,
                             phi + 0.5 * phi_k2, pr + 0.5 * pr_k2,
                             ptheta + 0.5 * ptheta_k2, pphi + 0.5 * pphi_k2);

    double r_k4 = stepsize_ * dr_dt(pr + pr_k3);
    double theta_k4 = stepsize_ * dtheta_dt(r + r_k3, ptheta + ptheta_k3);
    double phi_k4 =
        stepsize_ * dphi_dt(r + r_k3, theta + theta_k3, pphi + pphi_k3);
    double pr_k4 =
        stepsize_ * dpr_dt(r + r_k3, theta + theta_k3, phi + phi_k3, pr + pr_k3,
                           ptheta + ptheta_k3, pphi + pphi_k3);
    double ptheta_k4 =
        stepsize_ * dptheta_dt(r + r_k3, theta + theta_k3, phi + phi_k3,
                               pr + pr_k3, ptheta + ptheta_k3, pphi + pphi_k3);
    double pphi_k4 =
        stepsize_ * dpphi_dt(r + r_k3, theta + theta_k3, phi + phi_k3, pr + pr_k3,
                             ptheta + ptheta_k3, pphi + pphi_k3);

    traj_vector_.r +=
        (1. / (6. * rel_mass)) * (r_k1 + 2. * r_k2 + 2. * r_k3 + r_k4);
    traj_vector_.theta += (1. / (6. * rel_mass)) *
                          (theta_k1 + 2. * theta_k2 + 2. * theta_k3 +
                           theta_k4);
    traj_vector_.phi +=
        (1. / (6. * rel_mass)) * (phi_k1 + 2. * phi_k2 + 2. * phi_k3 + phi_k4);
    traj_vector_.pr +=
        (1. / (6. * rel_mass)) * (pr_k1 + 2. * pr_k2 + 2. * pr_k3 + pr_k4);
    traj_vector_.ptheta += (1. / (6. * rel_mass)) * (ptheta_k1 + 2. * ptheta_k2 +
                                                     2. * ptheta_k3 +
                                                     ptheta_k4);
    traj_vector_.pphi += (1. / (6. * rel_mass)) *
                         (pphi_k1 + 2. * pphi_k2 + 2. * pphi_k3 + pphi_k4);
    traj_vector_.t += stepsize_;

    // for (double val:vec) {
    //     std::cout << val << ' ';
    // }
    // std::cout << std::endl;

    // return vec;
}

/* Element-wise addition between itself and another
    std::array.
    Used for compact notations when evaluating the ODE

    Example: vec += vec1 is the same thing as:
    for (int i=0; i<vec.size(); ++i) {
      vec[i] = vec[i] + vec1[i];
    }

  Parameters
  ------------
  - lh_vec (std::array<double, 6>) : the array being summed to
  - rh_vec (std::array<double, 6>) : the array that will sum
  Returns
  --------
  - lh_vec (std::array<double, 6>) : the array being summed to
*/
// inline std::array<double, 6> operator+=(std::array<double, 6> lh_vec,
//                                         std::array<double, 6> rh_vec) {
//   std::transform(lh_vec.begin(), lh_vec.end(), rh_vec.begin(),
//   lh_vec.begin(),
//                  std::plus<double>());
//   // for (int i = 0; i < 6; ++i) {
//   //   vec[i] = vec[i] + vec1[i];
//   // }
//   return lh_vec;
// }

// // copy constructor
// uTrajectoryTracer::TrajectoryTracer(const TrajectoryTracer &traj_tracer)
//     : bfield_{traj_tracer.bfield_},
//       charge_{traj_tracer.charge_},
//       mass_{traj_tracer.mass_},
//       escape_radius_{traj_tracer.escape_radius_},
//       stepsize_{traj_tracer.stepsize_},
//       max_iter_{traj_tracer.max_iter_},
//       particle_escaped_{false} {}

// // copy assignment operator
// TrajectoryTracer &TrajectoryTracer::operator=(
//     const TrajectoryTracer &traj_tracer)
// {
//   bfield_ = traj_tracer.bfield_;
//   charge_ = traj_tracer.charge_;
//   mass_ = traj_tracer.mass_;
//   escape_radius_ = traj_tracer.escape_radius_;
//   stepsize_ = traj_tracer.stepsize_;
//   max_iter_ = traj_tracer.max_iter_;
//   particle_escaped_ = false;
//   return *this;
// }
