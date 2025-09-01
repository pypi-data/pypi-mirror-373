# Copyright (c) 2025 Patricio Cubillos
# Gen TSO is open-source software under the GPL-2.0 license (see LICENSE)

import gen_tso.pandeia_io as jwst
from pandeia.engine.calc_utils import get_instrument_config
import pytest
import numpy as np


@pytest.mark.skip(reason='TBD')
def test_work_with_run_pandeia_outputs():
    import pickle

    # TSO
    tso_file = 'tso_nircam_1251.pickle'
    with open(tso_file, 'rb') as f:
        tso = pickle.load(f)
    report_tso = tso['tso']

    # TA
    tso_file = 'tso_nircam_ta.pickle'
    with open(tso_file, 'rb') as f:
        tso = pickle.load(f)
    report_ta = tso['tso']

    # Warning
    tso_file = 'tso_nircam_ta2.pickle'
    with open(tso_file, 'rb') as f:
        tso = pickle.load(f)
    report_warn = tso['tso']

    warnings = report['warnings']

    # Extracted S/N ratio: {x}
    # Max. fraction of saturation: {X}%



@pytest.mark.skip(reason='TBD')
def test_set_scene_phoenix():
    pass


@pytest.mark.skip(reason='TBD')
def test_set_scene_kurucz():
    pass


@pytest.mark.skip(reason='TBD')
def test_set_scene_blackbody():
    pass


@pytest.mark.skip(reason='TBD')
def test_set_scene_background():
    pass


def test_extract_sed_no_normalization():
    # Lets look directly at the sun:

    # 'G5V 5700K log(g)=4.5'
    sed_type = 'phoenix'
    sed_model = 'g5v'
    norm_band = '2mass,ks'
    norm_magnitude = 8.637
    scene = jwst.make_scene(sed_type, sed_model, norm_band, norm_magnitude)
    scene['spectrum']['normalization'] = dict(type="none")
    wl, flux_no = jwst.extract_sed(scene)

    # 'G5V 5770K log(g)=4.5'
    sed_type = 'k93models'
    sed_model = 'g5v'
    scene2 = jwst.make_scene(sed_type, sed_model, norm_band, norm_magnitude)
    scene2['spectrum']['normalization'] = dict(type="none")
    k_wl, k_flux_no = jwst.extract_sed(scene2)

    sed_type = 'blackbody'
    sed_model = 5770.0
    scene3 = jwst.make_scene(sed_type, sed_model, norm_band, norm_magnitude)
    scene3['spectrum']['normalization'] = dict(type="none")
    b_wl, b_flux_no = jwst.extract_sed(scene3)

    # Raw outputs
    plt.figure(0)
    plt.clf()
    plt.plot(wl, flux_no, c='orange', alpha=0.5)
    plt.plot(k_wl, k_flux_no, c='r')
    plt.plot(b_wl, b_flux_no, c='b')
    plt.xlim(0.1, 30)
    plt.xscale('log')


def test_acquisition_calculation():

    pando = jwst.PandeiaCalculation('nircam', 'target_acq')
    pando.set_scene('phoenix', 'k5v', '2mass,ks', 8.351)
    result = pando.perform_calculation(ngroup=3, nint=1)

    pando = jwst.PandeiaCalculation('nircam', 'lw_tsgrism')
    pando.set_scene('phoenix', 'k5v', '2mass,ks', 8.351)
    result = pando.perform_calculation(
        ngroup=92, nint=683,
        readout='rapid', filter='f444w',
    )
    output = result['scalar']

    # Exposure time: 0.06 s (0.00 h)
    # Max. fraction of saturation: 32.0%
    # ngroup below 80% saturation: 7
    # ngroup below 100% saturation: 9
    print(print_pandeia_report(output))


def test_report_acquisition():
    import gen_tso.pandeia_io as jwst
    pando = jwst.PandeiaCalculation('nircam', 'target_acq')
    pando.set_scene('phoenix', 'k5v', '2mass,ks', 8.351)
    tso = pando.perform_calculation(ngroup=3, nint=1)

    if isinstance(tso, list):
        report_in = [report['report_in']['scalar'] for report in tso]
        report_out = [report['report_out']['scalar'] for report in tso]
        reports = report_in, report_out
    else:
        reports = tso['report_in']['scalar'], tso['report_out']['scalar']

    report_in = tso['scalar']
    tso_report = print_pandeia_report(report_in)
    print(tso_report)


def test_report_single_tso():
    import gen_tso.pandeia_io as jwst
    wl = np.logspace(0, 2, 1000)
    depth = [wl, np.tile(0.03, len(wl))]

    pando = jwst.PandeiaCalculation('nircam', 'lw_tsgrism')
    pando.set_scene('phoenix', 'k5v', '2mass,ks', 8.351)
    tso = pando.tso_calculation(
        'transit', transit_dur=2.1, obs_dur=6.0, depth_model=depth,
        ngroup=90, readout='rapid', filter='f444w',
    )

    if isinstance(tso, list):
        report_in = [report['report_in']['scalar'] for report in tso]
        report_out = [report['report_out']['scalar'] for report in tso]
        reports = report_in, report_out
    else:
        reports = tso['report_in']['scalar'], tso['report_out']['scalar']

    report_in, report_out = reports
    tso_report = print_pandeia_report(report_in, report_out)
    print(tso_report)


def test_report_tso_list():
    import gen_tso.pandeia_io as jwst
    wl = np.logspace(0, 2, 1000)
    depth = [wl, np.tile(0.03, len(wl))]

    pando = jwst.PandeiaCalculation('miri', 'mrs_ts')
    pando.set_scene('phoenix', 'k5v', '2mass,ks', 8.351)
    aperture = ['ch1', 'ch2', 'ch3', 'ch4']
    tso = pando.tso_calculation(
        'transit', transit_dur=2.1, obs_dur=6.0, depth_model=depth,
        ngroup=250, aperture=aperture,
    )

    pixel_rate, full_well = jwst.saturation_level(tso)

    if isinstance(tso, list):
        report_in = [report['report_in']['scalar'] for report in tso]
        report_out = [report['report_out']['scalar'] for report in tso]
        reports = report_in, report_out
    else:
        reports = tso['report_in']['scalar'], tso['report_out']['scalar']

    report_in, report_out = reports
    tso_report = print_pandeia_report(report_in, report_out)
    print(tso_report)


def test_tso_calculation():
    import pandeia_interface as jwst
    from pandeia_interface import set_depth_scene

    # With NIRCam
    instrument = 'nircam'
    mode = 'lw_tsgrism'
    self = pando = jwst.PandeiaCalculation(instrument, mode)

    pando.set_scene(
        sed_type='phoenix', sed_model='k5v',
        norm_band='2mass,ks', norm_magnitude=8.637,
    )
    disperser='grismr'
    filter='f444w'
    readout='rapid'
    subarray='subgrism64'
    ngroup = 127

    # With NIRSpec
    instrument = 'nirspec'
    mode = 'bots'
    self = pando = jwst.PandeiaCalculation(instrument, mode)

    pando.set_scene(
        sed_type='phoenix', sed_model='k5v',
        norm_band='2mass,ks', norm_magnitude=18.637,
    )
    disperser='g395h'
    filter='f290lp'
    readout='nrsrapid'
    subarray='sub2048'
    ngroup = 16


    transit_dur = 2.753
    obs_dur = 6.0
    obs_type = 'transit'

    depth_model = np.loadtxt(
        '../planet_spectra/WASP80b_transit.dat', unpack=True)

    figure(0)
    clf()
    plot(wl, var_in, c='b')
    plot(wl, in_transit_shot_var, c='orange')
    plot(wl, in_transit_shot_var*5/6, c='0.5')
    plot(wl, in_transit_flux, c='xkcd:green')
    plot(wl, in_transit_background_var, c='black')
    axhline(in_transit_rn_var, c='red')

    sed_type = 'k93models'
    sed_model = 'k7v'
    norm_band = '2mass,ks'
    norm_magnitude = 8.637
    scene = jwst.make_scene(sed_type, sed_model, norm_band, norm_magnitude)
    wl2, kur = jwst.extract_sed(scene)

    plt.clf()
    plt.plot(wl1, phoenix)
    plt.plot(wl2, kur)
    plt.xlim(0.5, 50)
    plt.xscale('log')

    plt.clf()
    plt.plot(wl1[1:], wl1[1:]/np.ediff1d(wl1))
    plt.plot(wl2[1:], wl2[1:]/np.ediff1d(wl2))
    plt.xlim(0.5, 15)
    plt.yscale('log')


    # # Check flux rates are OK
    # plt.figure(1)
    # plt.clf()
    # plt.plot(wl, flux_in/dt_in, c='orange', label='in transit')
    # plt.plot(wl, flux_out/dt_out, c='b', alpha=0.7, label='out transit')
    # plt.legend(loc='best')

    # # Check output depth spectrum matches input depth spectrum
    # wl_depth, depth = depth_model
    # lw = 1.0
    # plt.figure(4)
    # plt.clf()
    # plt.plot()
    # plt.plot(wl_depth, 100*depth, c='orange', lw=lw, label='model depth')
    # plt.plot(wl, 100*obs_depth, c='b', alpha=0.7, lw=lw, label='obs depth')
    # plt.legend(loc='best')
    # plt.xlim(2.7, 5.2)
    # plt.ylim(2.8, 3.2)

    # # Check flux rates are OK
    # plt.figure(4)
    # plt.clf()
    # plt.plot(wl, flux_in/dt_in, c='orange', label='in transit')
    # plt.plot(wl, var_in/dt_in, c='xkcd:green', label='in transit')
    # plt.legend(loc='best')

    #plt.plot(wl, in_transit_shot_var, c='orange')
    #plt.plot(wl, in_transit_shot_var*5/6, c='0.5')
    #plt.plot(wl, in_transit_flux, c='xkcd:green')
    #plt.plot(wl, in_transit_background_var, c='black')
    #plt.axhline(in_transit_rn_var, c='red')

    #'e_rate_out':photon_out_bin/to,
    #'e_rate_in':photon_in_bin/ti,
    #'error_no_floor':error_spec,
    #'rn[out,in]': result['rn[out,in]'],
    #'bkg[out,in]': result['bkg[out,in]']

