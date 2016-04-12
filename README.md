NeSSUs - Navier-Stokes Simulator Utilities
==========================================

Configure
---------
1. modify `launch_scripts/_conf/configuration.conf`
2. modify `launch_scripts/_conf/job_settings.conf`
3. `./create_job.py`
4. Finally you can launch your jobs from `launch_scripts/_conf/__job/`

Utilities:
----------
- Grids:
  - 2D:
    - rectagle with circular hole
    - rectagle with two circular holes
  - 3D:
    - hyper-rectagle with cylinder hole
- prm files:
  - fluid-dynamics:
    - ALE flow past a cylinder
    - flow past a cylinder 2D
    - flow past a cylinder 3D
    - lid cavity 2D
    - lid cavity 3D
  - turbulence:
    - k-omega



Requirements
------------

- [deal.II](https://github.com/dealii/dealii.git)
- [deal2lkit](https://github.com/mathLab/deal2lkit.git)
- [pi-DoMUS](https://github.com/mathLab/pi-DoMUS)

`.gitignore`
------------

- `__simulations/`
- `__jobs/`
