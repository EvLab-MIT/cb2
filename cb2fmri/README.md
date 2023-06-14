# EXPT_CerealBar2

This experiment integrates CerealBar2 (or CB2), found at [`cb2.ai`](http://cb2.ai) with an fMRI experiment 
about the language and working memory/multiple-demand systems. In this directory we house code specifically 
pertaining to running the experiment in an fMRI scanner. The parent directory is a fork of the 
[cb2 repository](https://github.com/lil-lab/cb2), also found at https://github.com/EvLab-MIT/cb2.


# Usage

The experiment driver program is run as a module from the parent directory like so:
```bash
    python -m cb2fmri.main
```
