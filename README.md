# The MAGNETAR* Pipeline;

*Magnetic-field Analysis and Generation of Noise-filtered Emission from Time-ordered Astronomical Records

An End-to-End Polarimetric Data Reduction Framework.



Core Ideas to implement for testing error:

Signal model per sample (per detector):

$$
d_t = g[I(\hat n)]+ \rho \{Q(\hat n_t)\cos2\gamma_t+U(\hat n_t)\sin 2\gamma_t\}]+n_t
$$
where:
* $ \gamma_t$: detector + HWP angle in sky frame
* $\rho$: polatization efficiency
* Noise $n_t$: white +1/f

Demod / solve per pixel:
For each pixel, solve a tiny linear regression from all samples hitting that pixel:

$$d=aI+bQ+cU,\;a=1, \;b=ρcos2\gamma,\; c=ρsin2_gamma$$
d=aI+bQ+cU,a=1,b=ρcos2γ,c=ρsin2γ

weighted by inverse noise variance → gives I,Q,U and their $3\times3$ covariance.

Debias (simple Wardle–Kronberg):
$$
p_{meas}=\sqrt{\frac{Q^2+U^2}{I}},\;\; p_{deb}=\sqrt{max(p^2_{meas}−\sigma_p^2,\;0)} $$



# Night Sky Selection

The following constraints were used in the HAWC+ polarization data from SOFIA
Spatial Constraints: All-Sky
Observation Constraints: AOR ID 06_0119_1
Data Product Constraints: Level 0 



