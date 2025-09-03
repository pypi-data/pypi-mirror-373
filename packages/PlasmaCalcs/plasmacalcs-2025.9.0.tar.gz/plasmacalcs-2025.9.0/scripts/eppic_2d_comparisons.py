import PlasmaCalcs as pc
import matplotlib.pyplot as plt


dirs = {
    'EPPIC-2a': 'tfbi2a_prod1_n400',
    #'EPPIC-2a_n900': 'tfbi2a_prod1_n900',
    'EPPIC-2b': 'tfbi2_c3prod1_v2',
    '1 nscale, 4 $m_e$': 'tfbi2_eff_RUNS/tfbi2_eff08_A_fw=9_me4_nu4',
    '1 nscale, 16 $m_e$': 'tfbi2_eff_RUNS/tfbi2_eff09_nscale01_me16',
    '1 nscale, 64 $m_e$': 'tfbi2_eff_RUNS/tfbi2_eff09_nscale01_me64',
    '4 nscale, 1 $m_e$': 'tfbi2_eff_RUNS/tfbi2_eff07_A_fw=9_nscale004_nx=256',
    '4 nscale, 4 $m_e$': 'tfbi2_eff_RUNS/tfbi2_eff09_nscale04_me04',
    '4 nscale, 16 $m_e$': 'tfbi2_eff_RUNS/tfbi2_eff09_nscale04_me16',
    '4 nscale, 64 $m_e$': 'tfbi2_eff_RUNS/tfbi2_eff09_nscale04_me64',
    '16 nscale, 1 $m_e$': 'tfbi2_eff_RUNS/tfbi2_eff07_A_fw=9_nscale016_nx=128',
}

default_styles = dict(linewidth=2, alpha=0.7)
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
nscale_styles = {  # vary color for each nscale
    1: dict(color=colors[0]),
    4: dict(color=colors[1]),
    16: dict(color=colors[2]),
}
linestyles = ['-', '--', '-.', ':']
me_styles = {  # vary linestyle for each me
    1: dict(linestyle=linestyles[0]),
    4: dict(linestyle=linestyles[1]),
    16: dict(linestyle=linestyles[2]),
    64: dict(linestyle=linestyles[3]),
}

styles = {
    'EPPIC-2a': dict(color='black', linestyle='-', linewidth=4),
    'EPPIC-2b': dict(color='red', linestyle='-', linewidth=4, alpha=0.7),
    '1 nscale, 4 $m_e$': dict(**nscale_styles[1], **me_styles[4], **default_styles),
    '1 nscale, 16 $m_e$': dict(**nscale_styles[1], **me_styles[16], **default_styles),
    '1 nscale, 64 $m_e$': dict(**nscale_styles[1], **me_styles[64], **default_styles),
    '4 nscale, 1 $m_e$': dict(**nscale_styles[4], **me_styles[1], **default_styles),
    '4 nscale, 4 $m_e$': dict(**nscale_styles[4], **me_styles[4], **default_styles),
    '4 nscale, 16 $m_e$': dict(**nscale_styles[4], **me_styles[16], **default_styles),
    '4 nscale, 64 $m_e$': dict(**nscale_styles[4], **me_styles[64], **default_styles),
    '16 nscale, 1 $m_e$': dict(**nscale_styles[16], **me_styles[1], **default_styles),
}


calcs = dict()
for key, d in dirs.items():
    e_chdir(os.path.join('runs', d))
    ec = pc.EppicCalculator.from_here(snaps_from='timers', kw_units=dict(M=1))
    calcs[key] = ec

for key, cc in calcs.items():
    cc('rmscomps_Ta_from_moment2', component=[0,1,2], fluid=0, snap=cc.snaps.select_between(0, 0.015)).pc.timelines(label=key)
