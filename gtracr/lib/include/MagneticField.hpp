// header file for Magnetic Field
#ifndef __MAGNETICFIELD_HPP_
#define __MAGNETICFIELD_HPP_

#include <math.h>

#include <array>

#include "constants.hpp"

class MagneticField {
 private:
  // double* gcoeffs;
  // double* hcoeffs;
  double B0;  // mean value of the magnetic field at the magnetic
              //   equator

 public:
  // Constructor
  MagneticField() : B0{-29404.8 * (1e-9)} {}
  // Destructor
  // ~MagneticField() {delete[] gcoeffs; delete[] hcoeffs;}
  // MagneticField();
  inline std::array<double, 3> values(const double &r, const double &theta,
                                      const double &phi) {
    std::array<double, 3> val;
    val[0] = 2. * (constants::RE / r) * (constants::RE / r) *
             (constants::RE / r) * B0 * cos(theta);
    val[1] = (constants::RE / r) * (constants::RE / r) * (constants::RE / r) *
             B0 * sin(theta);
    val[2] = 0.;
    return val;
  }
  // // the radial component of the Earth's magnetic field
  // inline const double Br(const double &r, const double &theta,
  //                        const double &phi) {
  //   return 2. * (constants::RE / r) * (constants::RE / r) *
  //          (constants::RE / r) * B0 * cos(theta);
  // }
  // // the polar component of the Earth's magnetic field
  // inline const double Btheta(const double &r, const double &theta,
  //                            const double &phi) {
  //   return (constants::RE / r) * (constants::RE / r) * (constants::RE / r) *
  //          B0 * sin(theta);
  // }
  // // the azimuthal-component of the Earth's magnetic field
  // inline const double Bphi(const double &r, const double &theta,
  //                          const double &phi) {
  //   return 0.;
  // }
};

#endif  // __MAGNETICFIELD_HPP_