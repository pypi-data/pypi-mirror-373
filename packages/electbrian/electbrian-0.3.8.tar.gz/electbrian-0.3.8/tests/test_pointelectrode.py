import pytest
from src.electbrian.elects import PointElectrode
import brian2.numpy_ as np
from brian2 import SpatialNeuron, Morphology, Cylinder, defaultclock, run
from brian2.units.allunits import uampere, hertz, umeter, siemens, meter, msecond, ohm, cmeter, second, mvolt, ufarad
from numpy.testing import assert_array_equal, assert_allclose
from scipy.signal import square

@pytest.fixture
def sine_elect() -> PointElectrode:
    return PointElectrode(current_amp=-11 * uampere, frequency=200 * hertz, rx=1000 * umeter, ry=1000 * umeter,
                          rz=500 * umeter, sigma_ex=0.2 * siemens / meter)

@pytest.fixture
def pulse_elect() -> PointElectrode:
    return PointElectrode(current_amp=-11 * uampere, rx=-1000 * umeter, ry=1000 * umeter, rz=-500 * umeter,
                          pulse_width=0.3 * msecond, sine_wave=False, sigma_ex=0.2 * siemens / meter, duty_cycle=0.5)

@pytest.fixture
def elect_for_testing (axon_morpho: Morphology) -> PointElectrode:
    return PointElectrode(current_amp=-11 * uampere, frequency=200 * hertz, rx=1000 * umeter, ry=1000 * umeter,
                          rz=500 * umeter,
                          sigma_ex=0.2 * siemens / meter, origin=2, morphology=axon_morpho, node_length=1 * umeter,
                          internode_length=110 * umeter, paranode_length=3 * umeter, node_diam = 2 * umeter,
                          internode_diam=1.4 * umeter,
                          paranode_diam=1.4 * umeter, axial_rho=70 * ohm * cmeter)

@pytest.fixture
def axon_morpho() -> Morphology:
    internode_length, paranode_length, node_length = 110 * umeter, 3 * umeter, 1 * umeter
    internode_diam, paranode_diam, node_diam = 2 * umeter, 1.4 * umeter, 1.4 * umeter

    axon_morpho = Cylinder(diameter=node_diam, length=node_length)
    axon_morpho.p1 = Cylinder(diameter=paranode_diam, length=paranode_length)
    axon_morpho.p1.i1 = Cylinder(diameter=internode_diam, length=internode_length)
    axon_morpho.p1.i1.p2 = Cylinder(diameter=paranode_diam, length=paranode_length)
    axon_morpho.p1.i1.p2.n2 = Cylinder(diameter=node_diam, length=node_length)
    return axon_morpho


def test_init_exceptions(axon_morpho: Morphology) -> None:
    with pytest.raises(ValueError):
        PointElectrode(current_amp=-11 * uampere, frequency=0, rx=1000 * umeter,
                       ry=1000 * umeter, rz=500 * umeter, sigma_ex=0.2 * siemens / meter)
    with pytest.raises(ValueError):
        PointElectrode(current_amp=-11 * uampere, pulse_width=0, rx=1000 * umeter,
                       ry=1000 * umeter, rz=500 * umeter, sine_wave=False,
                       sigma_ex=0.2 * siemens / meter)
    with pytest.raises(ValueError):
        PointElectrode(current_amp=-11 * uampere, frequency=200 * hertz, rx=1000 * umeter,
                       ry=1000 * umeter, rz=500 * umeter, sigma_ex=0 * siemens / meter)
    with pytest.raises(TypeError):
        PointElectrode(current_amp=-11 * uampere, frequency=200 * hertz, rx=1000 * umeter, ry=1000 * umeter, rz=500 * umeter,
                       sigma_ex=0.2 * siemens / meter, origin=1, morphology=axon_morpho, node_length=1 * umeter,
                       internode_length=110 * umeter, paranode_length=None, node_diam = 2 * umeter, internode_diam=1.4 * umeter,
                       paranode_diam=1.4 * umeter, axial_rho=70 * ohm * cmeter)
    with pytest.raises(TypeError):
        PointElectrode(current_amp=-11 * uampere, rx=-1000 * umeter, ry=1000 * umeter, rz=-500 * umeter,
                       pulse_width=0.3 * msecond, sine_wave=False, sigma_ex=0.2 * siemens / meter, duty_cycle=0.5,
                       origin=1, morphology=axon_morpho, node_length=1 * umeter, internode_length=110 * umeter,
                       paranode_length=None, node_diam = 2 * umeter, internode_diam=1.4 * umeter, paranode_diam=1.4 * umeter,
                       axial_rho=70 * ohm * cmeter)
    with pytest.raises(ValueError):
        PointElectrode(current_amp=-11 * uampere, frequency=200 * hertz, rx=1000 * umeter, ry=1000 * umeter, rz=500 * umeter,
                       sigma_ex=0.2 * siemens / meter, origin=6, morphology=axon_morpho, node_length=1 * umeter,
                       internode_length=110 * umeter, paranode_length=3 * umeter, node_diam = 2 * umeter, internode_diam=1.4 * umeter,
                       paranode_diam=1.4 * umeter, axial_rho=70 * ohm * cmeter)
    with pytest.raises(ValueError):
        PointElectrode(current_amp=-11 * uampere, rx=-1000 * umeter, ry=1000 * umeter, rz=-500 * umeter,
                       pulse_width=0.3 * msecond, sine_wave=False, sigma_ex=0.2 * siemens / meter, duty_cycle=0.5,
                       origin=6, morphology=axon_morpho, node_length=1 * umeter, internode_length=110 * umeter,
                       paranode_length=3 * umeter, node_diam = 2 * umeter, internode_diam=1.4 * umeter, paranode_diam=1.4 * umeter,
                       axial_rho=70 * ohm * cmeter)
    with pytest.raises(ValueError):
        PointElectrode(current_amp=-11 * uampere, rx=-1000 * umeter, ry=1000 * umeter, rz=-500 * umeter,
                       pulse_width=0.3 * msecond, sine_wave=False, sigma_ex=0.2 * siemens / meter, duty_cycle=-0.5,
                       origin=1, morphology=axon_morpho, node_length=1 * umeter, internode_length=110 * umeter,
                       paranode_length=3 * umeter, node_diam = 2 * umeter, internode_diam=1.4 * umeter, paranode_diam=1.4 * umeter,
                       axial_rho=70 * ohm * cmeter)
    with pytest.raises(ValueError):
        PointElectrode(current_amp=-11 * uampere, rx=-1000 * umeter, ry=1000 * umeter, rz=-500 * umeter,
                       pulse_width=0.3 * msecond, sine_wave=False, sigma_ex=0.2 * siemens / meter, duty_cycle=2,
                       origin=1, morphology=axon_morpho, node_length=1 * umeter, internode_length=110 * umeter,
                       paranode_length=3 * umeter, node_diam = 2 * umeter, internode_diam=1.4 * umeter, paranode_diam=1.4 * umeter,
                       axial_rho=70 * ohm * cmeter)
    eqs = '''
            gL : siemens/meter**2

            Im = gL * (EL-v) : amp/meter**2
            i_appl : amp (point current)
            '''
    with pytest.raises(ValueError):
        PointElectrode(current_amp=-11 * uampere, frequency=200 * hertz, rx=1000 * umeter, ry=1000 * umeter, rz=500 * umeter,
                       sigma_ex=0.2 * siemens / meter, origin=1, morphology=axon_morpho, neuron_eqs=eqs,
                       node_length=1 * umeter, internode_length=110 * umeter, paranode_length=3 * umeter, node_diam = 2 * umeter,
                       internode_diam=1.4 * umeter, paranode_diam=1.4 * umeter)

def test_elect_mem_distance(sine_elect: PointElectrode, pulse_elect: PointElectrode) -> None:
    assert sine_elect.elect_mem_dist() == 1500 * umeter
    assert pulse_elect.elect_mem_dist() == 1500 * umeter


def test_v_waveform(sine_elect: PointElectrode, pulse_elect: PointElectrode) -> None:
    t = np.arange(0, 3.1e-3, 1e-4) * second

    sine_actual = sine_elect.v_waveform(t)
    sine_desired = ((sine_elect.current_amp * np.sin(2 * np.pi * sine_elect.frequency * t)) /
                    (4 * np.pi * sine_elect.elect_mem_dist() * sine_elect.sigma_ex))

    pulse_actual = pulse_elect.v_waveform(t)
    pulse_desired = ((pulse_elect.current_amp * square(2 * np.pi * ((pulse_elect.duty_cycle * t) / pulse_elect.pw),
                                                       pulse_elect.duty_cycle)) / (4 * np.pi *
                                                                                   pulse_elect.elect_mem_dist() *
                                                                                   pulse_elect.sigma_ex))
    assert_array_equal(sine_actual, sine_desired)
    assert_array_equal(pulse_actual, pulse_desired)


def test_origin_to_mid(elect_for_testing: PointElectrode) -> None:
    internode_length, paranode_length, node_length = 110 * umeter, 3 * umeter, 1 * umeter

    assert_allclose(elect_for_testing.origin_to_mid(-1, 1),
                    (0.5 * (paranode_length + internode_length)))
    assert_allclose(elect_for_testing.origin_to_mid(1, 3),
                    (0.5 * (paranode_length + internode_length)))

    assert_allclose(elect_for_testing.origin_to_mid(-1, 0),
                    (0.5 * (2 * paranode_length + internode_length + node_length)))
    assert_allclose(elect_for_testing.origin_to_mid(1, 4),
                    (0.5 * (2 * paranode_length + internode_length + node_length)))

    with pytest.raises(ValueError):
        elect_for_testing.origin_to_mid(1, 5)

    with pytest.raises(ValueError):
        elect_for_testing.origin_to_mid(-1, -1)

    with pytest.raises(ValueError):
        elect_for_testing.origin_to_mid(2, 4)

    with pytest.raises(ValueError):
        elect_for_testing.origin_to_mid(-2, 4)

    elect_for_testing.origin = 0
    assert_allclose(elect_for_testing.origin_to_mid(-1, 0), 0)


def test_v_morpho(elect_for_testing: PointElectrode) -> None:
    v_actual1 = elect_for_testing.v_morpho(end = -1, change = -1)
    v_actual2 = elect_for_testing.v_morpho(end = 5, change = 1)
    v_actual = {**v_actual1, **v_actual2}
    assert v_actual[1] == v_actual[3]
    assert v_actual[0] == v_actual[4]

def test_v_applied_spatial(elect_for_testing: PointElectrode) -> None:
    v_actual = elect_for_testing.v_applied_spatial()
    assert v_actual[1] == v_actual[3]
    assert v_actual[0] == v_actual[4]

    elect_for_testing.origin = 4
    v_test1 = elect_for_testing.v_applied_spatial()

    elect_for_testing.origin = 0
    v_test2 = elect_for_testing.v_applied_spatial()

    assert v_test1[0] == v_test2[4]
    assert v_test1[1] == v_test2[3]
    assert v_test1[2] == v_test2[2]

def test_i_applied_spatial() -> None:
    internode_length, paranode_length, node_length = 110 * umeter, 3 * umeter, 1 * umeter
    internode_diam, paranode_diam, node_diam = 2 * umeter, 1.4 * umeter, 1.4 * umeter

    my_morpho = Cylinder(diameter=node_diam, length=node_length)
    my_morpho.p1 = Cylinder(diameter=paranode_diam, length=paranode_length)
    my_morpho.p1.i1 = Cylinder(diameter=internode_diam, length=internode_length)
    my_morpho.p1.i1.p2 = Cylinder(diameter=paranode_diam, length=paranode_length)
    my_morpho.p1.i1.p2.n2 = Cylinder(diameter=node_diam, length=node_length)
    my_morpho.p1.i1.p2.n2.p3 = Cylinder(diameter=paranode_diam, length=paranode_length)
    my_morpho.p1.i1.p2.n2.p3.i2 = Cylinder(diameter=internode_diam, length=internode_length)
    my_morpho.p1.i1.p2.n2.p3.i2.p4 = Cylinder(diameter=paranode_diam, length=paranode_length)
    my_morpho.p1.i1.p2.n2.p3.i2.p4.n3 = Cylinder(diameter=node_diam, length=node_length)
    my_morpho.p1.i1.p2.n2.p3.i2.p4.n3.p5 = Cylinder(diameter=paranode_diam, length=paranode_length)
    my_morpho.p1.i1.p2.n2.p3.i2.p4.n3.p5.i3 = Cylinder(diameter=internode_diam, length=internode_length)
    my_morpho.p1.i1.p2.n2.p3.i2.p4.n3.p5.i3.p6 = Cylinder(diameter=paranode_diam, length=paranode_length)
    my_morpho.p1.i1.p2.n2.p3.i2.p4.n3.p5.i3.p6.n4 = Cylinder(diameter=node_diam, length=node_length)

    leak_potential, rest_potential = -90 * mvolt, -90 * mvolt
    g_l_node = 0.007 * siemens / cmeter ** 2
    g_l_inter, inter_c, para_c = 0.7e-4 * siemens / cmeter ** 2, 1.6 * ufarad / cmeter ** 2, 1.6 * ufarad / cmeter ** 2
    membrane_c, axial_rho = 2 * ufarad / cmeter ** 2, 70 * ohm * cmeter

    eqs = '''
        gL : siemens/meter**2
        
        Im = gL * (EL-v) : amp/meter**2
        i_applied : amp (point current)
        '''
    const_potentials = {'EL': leak_potential, 'ER': rest_potential}
    myelinated = SpatialNeuron(morphology=my_morpho, model=eqs, Cm=membrane_c, Ri=axial_rho,
                               method='exponential_euler', namespace=const_potentials)
    myelinated.v = 'ER'
    myelinated.main.gL = g_l_node
    myelinated.p1.gL, myelinated.p1.Cm = g_l_inter, para_c
    myelinated.p1.i1.gL, myelinated.p1.i1.Cm = g_l_inter, inter_c
    myelinated.p1.i1.p2.gL, myelinated.p1.i1.p2.Cm = g_l_inter, para_c
    myelinated.p1.i1.p2.n2.gL = g_l_node
    myelinated.p1.i1.p2.n2.p3.gL, myelinated.p1.i1.p2.n2.p3.Cm = g_l_inter, para_c
    myelinated.p1.i1.p2.n2.p3.i2.gL, myelinated.p1.i1.p2.n2.p3.i2.Cm = g_l_inter, inter_c
    myelinated.p1.i1.p2.n2.p3.i2.p4.gL, myelinated.p1.i1.p2.n2.p3.i2.p4.Cm = g_l_inter, para_c
    myelinated.p1.i1.p2.n2.p3.i2.p4.n3.gL = g_l_node
    myelinated.p1.i1.p2.n2.p3.i2.p4.n3.p5.gL, myelinated.p1.i1.p2.n2.p3.i2.p4.n3.p5.Cm = g_l_inter, para_c
    myelinated.p1.i1.p2.n2.p3.i2.p4.n3.p5.i3.gL, myelinated.p1.i1.p2.n2.p3.i2.p4.n3.p5.i3.Cm = g_l_inter, inter_c
    myelinated.p1.i1.p2.n2.p3.i2.p4.n3.p5.i3.p6.gL, myelinated.p1.i1.p2.n2.p3.i2.p4.n3.p5.i3.p6.Cm = g_l_inter, para_c
    myelinated.p1.i1.p2.n2.p3.i2.p4.n3.p5.i3.p6.n4.gL = g_l_node

    elect = PointElectrode(current_amp=-11 * uampere, frequency=200 * hertz, rx=1000 * umeter, ry=1000 * umeter, rz=500 * umeter,
                           sigma_ex=0.2 * siemens / meter, morphology=my_morpho, neuron_eqs=eqs, origin=6,
                           node_length=node_length, internode_length=internode_length, paranode_length=paranode_length,
                           node_diam=node_diam, internode_diam=internode_diam, paranode_diam=paranode_diam,
                           axial_rho=axial_rho)

    defaultclock.dt = 0.005 * msecond
    elect.i_applied_spatial(myelinated)
    run(10 * msecond, report='text')
    assert abs(myelinated.i_applied[0]) == abs(myelinated.i_applied[12])
    assert abs(myelinated.i_applied[5]) == abs(myelinated.i_applied[7])
    assert abs(myelinated.i_applied[3]) == abs(myelinated.i_applied[9])
    assert abs(myelinated.i_applied[1]) == abs(myelinated.i_applied[11])
    assert myelinated.i_applied[4] == myelinated.i_applied[8]
    assert myelinated.i_applied[2] == myelinated.i_applied[10]



