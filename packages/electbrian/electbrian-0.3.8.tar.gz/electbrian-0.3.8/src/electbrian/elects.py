import numpy as np
from brian2 import defaultclock
from brian2.units.allunits import meter, umeter
from scipy.signal import square

class PointElectrode:
    """
    Implements the point electrode approximation for neural electrodes.
    Parameters
    ----------
    current_amp : 'Quantity'
        The amplitude of the current applied to the electrode
    rx : 'Quantity'
        x component of displacement between the electrode and the neuron
    ry : 'Quantity'
        y component of displacement between the electrode and the neuron
    rz : 'Quantity'
        z component of displacement between the electrode and the neuron
    sigma_ex: 'Quantity'
        The conductivity of the extracellular media (surrounding the electrode)
    frequency: 'Quantity', optional
        The frequency of the applied current signal
    pulse_width: 'Quantity', optional
        The pulse width of the applied current signal
    sine_wave: boolean
        If true then the current takes the form of a sine wave with a frequency.
        If false then the current takes the form of a square wave with a pulse width.
    duty_cycle: between 0 and 1, optional
        Refers to the time length of the square pulses
    morphology: 'Morphology'
        The morphology of the neuron.
    neuron_eqs: 'Equations'
        The equations defining the ion channels of the neuron (SpatialNeuron equations)
    origin: 'Quantity'
        The location (compartment number in the morphology) to which the electrode is closest.
    node_length: 'Quantity'
        The length of the nodes in the morphology
    internode_length: 'Quantity'
        The length of the internodes in the morphology
    paranode_length: 'Quantity'
        The length of the paranodes in the morphology
    node_diam: 'Quantity'
        The diameter of the nodes in the morphology
    internode_diam: 'Quantity'
        The diameter of the internodes in the morphology
    paranode_diam: 'Quantity'
        The diameter of the paranodes in the morphology
    axial_rho: 'Quantity'
        The resistivity of the neuron morphology

    """
    def __init__(self, current_amp, rx, ry, rz, sigma_ex, frequency=None, pulse_width=None, sine_wave=True,
                 duty_cycle=None, morphology=None, neuron_eqs=None, origin=None, node_length=None, internode_length=None
                 , paranode_length=None, node_diam=None, internode_diam=None, paranode_diam=None, axial_rho=None):

        self.v_applied, self.elect_dist, self.apply_mem_voltage = None, None, None

        if morphology is None:
            self.dictionary_of_lengths = None
        else:
            self.dictionary_of_lengths = {}
            if node_length is None or internode_length is None or paranode_length is None:
                raise TypeError("Please initialize a value for node length, paranode length, and internode length")
            if origin > morphology.total_compartments or origin < 0:
                raise ValueError("Such a compartment does not exist in the morphology")
            for j in np.arange(0, morphology.total_compartments, 1):
                if j % 4 == 0:
                    self.dictionary_of_lengths[j] = node_length
                elif j % 2 == 1:
                    self.dictionary_of_lengths[j] = paranode_length
                else:
                    self.dictionary_of_lengths[j] = internode_length

        self.rx, self.ry, self.rz, self.origin, self.morphology = rx, ry, rz, origin, morphology
        self.neuron_eqs, self.node_length, self.node_diam = neuron_eqs, node_diam, node_length
        self.paranode_diam, self.paranode_length, self.internode_diam = paranode_diam, paranode_length, internode_diam
        self.internode_length, self.axial_rho = internode_length, axial_rho

        if self.neuron_eqs is not None:
            eqs_list = self.neuron_eqs.splitlines()
            for i in range(len(eqs_list)):
                if eqs_list[i].endswith("(point current)"):
                    app_line_comps = eqs_list[i].split()
                    if app_line_comps[0] != "i_applied":
                        raise ValueError("The point current must be called i_applied")
                else:
                    pass

        self.current_amp, self.sigma_ex, self.sine_wave = current_amp, sigma_ex, sine_wave

        if sigma_ex <= 0:
            raise ValueError("Conductivity values should be greater than zero")
        if self.sine_wave:
            self.frequency, self.pw, self.duty_cycle = frequency, None, None
            if frequency <= 0:
                raise ValueError("Frequency should be greater than zero")
        else:
            self.frequency, self.pw, self.duty_cycle = None, pulse_width, duty_cycle
            if pulse_width <= 0:
                raise ValueError("The pulse width should be greater than zero")
            if duty_cycle < 0 or duty_cycle > 1:
                raise ValueError("Duty cycle must be between 0 and 1")

    def elect_mem_dist(self):
        self.elect_dist = np.sqrt((self.rx ** 2) + (self.ry ** 2) + (self.rz ** 2))
        return self.elect_dist

    def v_waveform(self, time_step):
        self.elect_mem_dist()
        if self.duty_cycle is None:
            self.apply_mem_voltage = ((self.current_amp * np.sin(2 * np.pi * self.frequency * time_step)) /
                                      (4 * np.pi * self.elect_dist * self.sigma_ex))
        else:
            self.apply_mem_voltage = ((self.current_amp * square(2 * np.pi * ((0.5 * time_step) / self.pw),
                                                                 self.duty_cycle)) / (4 * np.pi * self.elect_dist *
                                                                                      self.sigma_ex))
        return self.apply_mem_voltage

    def origin_to_mid(self, change, target_comp):
        if target_comp > self.morphology.total_compartments - 1 or target_comp < 0:
            raise ValueError ("The selected compartment is not in the morphology")
        if change > 1 or change < -1:
            raise ValueError("The only allowable values are 1 or -1")
        k, or_distance = self.origin, 0 * umeter
        while 1 <= k < self.morphology.total_compartments - 1:
            or_distance = or_distance + 0.5 * (self.dictionary_of_lengths[k] + self.dictionary_of_lengths[k + change])
            k = k + change
            if k == target_comp:
                break
        self.ry = or_distance
        return self.ry

    def v_morpho(self, end, change):
        v_applied = {}
        self.ry = 0 * meter
        v_applied[self.origin] = self.v_waveform(defaultclock.dt)
        for j in np.arange(self.origin + change, end, change):
            self.ry = self.origin_to_mid(change, j)
            v_applied[j] = self.v_waveform(defaultclock.dt)
        return v_applied

    def v_applied_spatial(self):
        self.v_applied = {}
        if self.origin < self.morphology.total_compartments:
            self.v_applied = self.v_morpho(-1, -1)
            v_applied_compartment1 = self.v_morpho(self.morphology.total_compartments, 1)
            self.v_applied.update(v_applied_compartment1)
        elif self.origin == 0:
            self.v_applied = self.v_morpho(self.morphology.total_compartments, 1)
        else:
            self.v_applied = self.v_morpho(-1, -1)
        return self.v_applied

    def i_applied_spatial(self, spatial_neuron):

        self.v_applied = self.v_applied_spatial()

        g_node = ((np.pi / 4) * (self.node_diam ** 2)) / (self.node_length * self.axial_rho)
        g_paranode = ((np.pi / 4) * (self.paranode_diam ** 2)) / (self.paranode_length * self.axial_rho)
        g_internode = ((np.pi / 4) * (self.internode_diam ** 2)) / (self.internode_length * self.axial_rho)

        g_node_to_paranode = (g_node + g_paranode) * 0.5
        g_paranode_to_internode = (g_internode + g_paranode) * 0.5

        for j in np.arange(0, self.morphology.total_compartments, 1):
            if j % 4 == 0:
                if j == 0:
                    spatial_neuron[j].i_applied = g_node_to_paranode * (-2 * self.v_applied[j] + self.v_applied[j + 1])
                elif j == self.morphology.total_compartments - 1:
                    spatial_neuron[j].i_applied = g_node_to_paranode * (self.v_applied[j - 1] - 2 * self.v_applied[j])
                else:
                    spatial_neuron[j].i_applied = g_node_to_paranode * (self.v_applied[j - 1] - 2 * self.v_applied[j] +
                                                                        self.v_applied[j + 1])
            # Right paranode
            elif j % 4 == 1 and j % 2 == 1:
                spatial_neuron[j].i_applied = (g_node_to_paranode * (self.v_applied[j - 1] - self.v_applied[j]) +
                                               g_paranode_to_internode * (self.v_applied[j + 1] - self.v_applied[j]))
            # Left paranode
            elif j % 4 != 1 and j % 2 == 1:
                spatial_neuron[j].i_applied = (g_paranode_to_internode * (self.v_applied[j - 1] - self.v_applied[j]) +
                                               g_node_to_paranode * (self.v_applied[j + 1] - self.v_applied[j]))
            else:
                spatial_neuron[j].i_applied = g_paranode_to_internode * (self.v_applied[j - 1] - 2 * self.v_applied[j] +
                                                                         self.v_applied[j + 1])