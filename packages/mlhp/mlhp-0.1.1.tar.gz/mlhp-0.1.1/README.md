## About

Mlhp is a C++ library with python bindings that implements multi-level _hp_- and other finite element methods efficiently also for dimensions > 3. The project is still very much work in progress and therefore does not have an extensive documentation.

## Submodules

The header-only libraries [pybind11](https://pybind11.readthedocs.io/en/stable/), [Catch2](https://github.com/catchorg/Catch2), and [vtu11](https://github.com/phmkopp/vtu11) are included as git submodules. To clone them resursively, use: 
```
git clone --recursive https://gitlab.com/hpfem/code/mlhp.git
```

## Getting started
- [Compiler and platform support](https://gitlab.com/hpfem/code/mlhp/-/wikis/Compiler%20and%20platform%20support) 
- [Setting up an executable that uses mlhp](https://gitlab.com/hpfem/code/mlhp/-/wikis/Setting%20up%20an%20executable%20that%20uses%20mlhp).
- [Core class structure](https://gitlab.com/hpfem/code/mlhp/-/wikis/Core%20class%20structure)
- [Doxygen documentation](https://hpfem/code.gitlab.io/mlhp)

## References and publications

If you use our code for your scientific research, please acknowledge this by referring to the following publication:

P. Kopp, E. Rank, V. M. Calo, S. Kollmannsberger, 2022: Efficient multi-level hp-finite elements in arbitrary dimensions, Computer Methods in Applied Mechanics and Engineering, Volume 401, Part B, 115575, DOI: [10.1016/j.cma.2022.115575](https://doi.org/10.1016/j.cma.2022.115575)

Here are some of the publications using this project:

- V. Holla, P. Kopp, J. Grünewald; P. Praegla, C. Meier, K. Wudy, S. Kollmannsberger, 2023: Laser beam shape optimization: Exploring alternative profiles to Gaussian-shaped laser beams in powder bed fusion of metals, 2023 International Solid Freeform Fabrication Symposium, 
DOI: [10.26153/TSW/50986](https://doi.org/10.26153/TSW/50986)
- V. Holla, P. Kopp, J. Grünewald, K. Wudy, S. Kollmannsberger, 2023: Laser beam shape optimization in powder bed fusion of metals, Additive Manufacturing, Volume 72, 103609, DOI: [10.1016/j.addma.2023.103609](https://doi.org/10.1016/j.addma.2023.103609)
- P. Kopp, V. M. Calo, E. Rank, S. Kollmannsberger, 2022: Space-time hp-finite elements for heat evolution in laser powder bed fusion additive manufacturing, Engineering with Computers, Volume 38, pages 4879–4893, DOI: [10.1007/s00366-022-01719-1](https://doi.org/10.1007/s00366-022-01719-1)
- S. Kollmannsberger; P. Kopp, 2021: On accurate time integration for temperature evolutions in additive manufacturing, GAMM-Mitteilungen, Volume 44, Issue 4, DOI: [10.1002/gamm.202100019](https://doi.org/10.1002/gamm.202100019)
