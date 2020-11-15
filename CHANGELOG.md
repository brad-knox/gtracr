# CHANGELOG

Presents the version history of the package.

### Version 1.0.0

Initial release of the gtracr package.
Major bugs are now fixed and is now ready for initial release.

- Examples are cleaned up and are ready to be used with users.
- Plotter now plots multiple trajectories
- Created a new class for array storage / operator overloading in replace to std::array
- Bug fixes for compatibility with UNIX systems and Windows

### version 0.10.0

Refactoring of the code was performed:

- Evaluation of the geomagnetic cutoffs are now done by class-level objects
- Plotters are separated with the package / evaluation process

### version 0.7.0

The initial pre-release of the beta version.

- The code evaluates the cosmic ray trajectories and the geomagnetic cutoff rigidities.
- It does _not_ support any sort of parallelization (GPU / CPU).
