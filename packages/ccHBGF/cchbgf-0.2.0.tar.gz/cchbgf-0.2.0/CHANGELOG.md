# ccHBGF CHANGELOG

## 31-08-2025: ccHBGF v0.2.0

- **Changed** name of `ccHBGF.ccHBGF` function to `ccHBGF.find_consensus`
- **Updated** logging framework:
    - **removed** `verbose` argument functionality from `ccHBGF.ccHBGF` (*now deprecated*)
    - logging now defined at a package level by `ccHBGF.config.LOG_LEVEL = 2` with log level 0 = silent, 1 = warnings and 2 = info.
- **Minimum** python version **requirement** updates to `3.10` was `3.9`
- **Added** `ccHBGF.ccHBGF` for backward compatability with 0.1.0

## 07-07-2024: ccHBGF v0.1.0

- Package created
- Documentation created
- Tests created