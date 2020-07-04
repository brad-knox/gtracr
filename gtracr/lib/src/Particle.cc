/*
Utility class for cosmic ray particles
Members:
- name: the name of the particle (char*)
- pid: the particle id as in pdg (int)
- mass: the particle rest mass (double) [units of GeV / c^2]
- charge: particle's charge Z (int) [units of elementary charge]
- label: the shorthand name for the particle (char*)

The below members require the particle energy or one of the below members as additional information
- momentum: Particle momentum
- velocity: particle velocity
- rigidity: particle rigidity

*Default is set to Proton

Notes:
- PDGID obtained from here: http://pdg.lbl.gov/2007/reviews/montecarlorpp.pdf
- The mass of the particles are also obtained from PDG

Example:
proton: proton = Particle("Proton", 2212, 0.938272, "p+")
*/
#include <string>
#include <stdexcept>
#include <iostream>
#include <math.h>
#include "constants.h"
#include "Particle.h"

// Constructors
// Default constructor, set to proton
// Default energy set to 1GeV
Particle::Particle()
    : nm{"Proton"}, pid{2212}, m{0.938272}, ch{1}, lbl{"p+"}
{
    p = sqrt(m * m + 1.);
    v = (p * constants::sc) /
        sqrt(
            (p * p) + (m * constants::sc) * (m * constants::sc));
    R = p / abs(ch);
}

// Construct with given initial configurations
// default energy set to 1GeV
Particle::Particle(const std::string &name, const int pdgid, const double &mass, const int charge, const std::string &label)
    : nm{name}, pid{pdgid}, m{mass}, ch{charge}, lbl{label}
{
    p = sqrt(m * m + 1.);
    v = (p * constants::sc) /
        sqrt(
            (p * p) + (m * constants::sc) * (m * constants::sc));
    R = p / abs(ch);
}

// Constructor with some provided energy
Particle::Particle(const std::string &name, const int pdgid, const double &mass, const int charge, const std::string &label, const double &energy = 0., const double &rigidity = 0.)
    : nm{name}, pid{pdgid}, m{mass}, ch{charge}, lbl{label}
{
    // set kinematical variables if energy xor rigidity is given
    if (abs(energy) < 1e-10)
    {
        set_from_energy(energy);
    }
    else if (abs(rigidity) < 1e-10)
    {
        set_from_rigidity(rigidity);
    }
    else
    {
        throw std::runtime_error("Input energy or rigidity, but not both or none!");
    }
}

// Destructor
Particle::~Particle()
{
}

// copy constructor
Particle::Particle(const Particle &part)
    : nm{part.nm}, pid{part.pid}, m{part.m}, ch{part.ch}, lbl{part.lbl}
{
    p = part.p;
    v = part.v;
    R = part.R;
}

// copy assignment operator
Particle &Particle::operator=(const Particle &part)
{
    nm = part.nm;
    pid = part.pid;
    m = part.m;
    ch = part.ch;
    lbl = part.lbl;

    p = part.p;
    v = part.v;
    R = part.R;
    return *this;
}

// Lorentz factor
const double &Particle::gamma()
{
    return 1. / sqrt(1. - (v / constants::sc) * (v / constants::sc));
}

const double &Particle::gamma(const double &vel)
{
    return 1. / sqrt(1. - (vel / constants::sc) * (vel / constants::sc));
}

// setters
void Particle::set_from_energy(const double &energy)
{
    p = sqrt(energy * energy - mass() * mass());
    v = ((momentum() * constants::sc) /
         sqrt(
             momentum() * momentum() +
             (mass() * constants::sc) * (mass() * constants::sc)));
    R = momentum() / abs(charge());
}

void Particle::set_from_momentum(const double &mmtum)
{
    p = mmtum;
    v = ((momentum() * constants::sc) /
         sqrt(
             momentum() * momentum() +
             (mass() * constants::sc) * (mass() * constants::sc)));
    R = momentum() / abs(charge());
}

void Particle::set_from_rigidity(const double &rgdty)
{
    p = rgdty * abs(charge());
    v = ((momentum() * constants::sc) /
         sqrt(
             momentum() * momentum() +
             (mass() * constants::sc) * (mass() * constants::sc)));
    R = rgdty;
}

void Particle::set_from_velocity(const double &vel)
{
    p = gamma(vel) * mass() * vel;
    v = vel;
    R = momentum() / abs(charge());
}

// other member functions
// obtain energy from rigidity
const double &Particle::get_energy_rigidity()
{
    return sqrt(momentum() * momentum() + mass() * mass()) * rigidity() * abs(charge());
}

// print contents
void Particle::print()
{
    std::cout << "Particle: " << nm << " (" << lbl << "), "
              << "PDG ID: " << pid << ", "
              << "Mass [GeV]: " << m << ", "
              << "Charge [e]: " << ch << std::endl;
    std::cout << "Current Momentum [GeV]: " << p << ", "
              << "Current Velocity: " << v << ", "
              << "Current Rigidity: " << R << std::endl;
}