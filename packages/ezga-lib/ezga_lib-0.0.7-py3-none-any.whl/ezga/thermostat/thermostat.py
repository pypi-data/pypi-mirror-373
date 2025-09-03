from typing import Tuple, List, Optional
import numpy as np

from ..utils.helper_functions import (
    oscillation_factor,
    decay_factor,
)

from ..core.interfaces import (
    IThermostat,
    IPopulation,
)

_EPS = 1e-12

class Thermostat(IThermostat):
    """
    The Thermostat class manages and updates a "temperature" parameter
    within a genetic algorithm (GA). It supports periodic oscillations,
    exponential decay, and adaptive adjustments based on performance metrics
    or consecutive failures. It also includes functionality to clamp the
    temperature within predefined bounds.

    Attributes
    ----------
    initial_temperature : float
        Base temperature used for initialization and resets.
    current_temperature : float
        The most recently computed temperature value.
    decay_rate : float
        Rate at which the temperature decays over generations.
    period : float
        Period for oscillatory temperature adjustments.
    increase_factor : float
        Scaling factor for temperature increases when performance is below a threshold.
    decrease_factor : float
        Scaling factor for temperature decreases when performance is above a threshold.
    threshold : float
        Performance threshold controlling whether to increase or decrease the temperature.
    temperature_bounds : tuple of float
        Lower and upper limits on the temperature (inclusive).
    consecutive_failures : int
        Tracks the number of consecutive failures, used to adapt the temperature.
    reset_count : int
        Tracks how many times the thermostat has been reset.
    """

    def __init__(
        self,
        initial_temperature: float,
        decay_rate: float = 0.01,
        period: float = 40.0,
        temperature_bounds: Tuple[float, float] = (0.0, 1.1),
        max_stall_offset:float=1.0,
        stall_growth_rate=0.05, 
        constant_temperature: bool = False, 
    ):
        """
        Initializes the Thermostat with default parameters for decay, oscillation,
        adaptive updates, and clamping.

        Parameters
        ----------
        initial_temperature : float
            The starting temperature of the system.
        decay_rate : float, optional
            Exponential decay rate applied to temperature over generations (default=0.01).
        period : float, optional
            Period for oscillatory adjustments (default=40.0).
        cooling_rate : float, optional
            Amount to subtract from the temperature if there are no failures (default=0.01).
        failure_increment : float, optional
            Base amount to add (per failure) to the temperature if there are consecutive 
            failures (default=0.05).
        temperature_bounds : Tuple[float, float], optional
            Lower and upper bounds for clamping the temperature (default=(0.0, 2.0)).
        """
        if temperature_bounds[0] > temperature_bounds[1]:
            raise ValueError("Lower bound of temperature cannot exceed upper bound.")

        self.initial_temperature = initial_temperature
        self.current_temperature = initial_temperature

        self.decay_rate = decay_rate
        self.period = period
        self.temperature_bounds = temperature_bounds

        self.consecutive_stall = 0
        self.reset_count = 0

        self.max_stall_offset = max_stall_offset
        self.stall_growth_rate = stall_growth_rate

        self.constant_temperature = constant_temperature

    def get_temperature(self, ) -> float:
        """
        """
        return self.current_temperature
        
    def update(self, generation: int, stall:int = 0) -> float:
        r"""
        Compute and update the GA “temperature” combining decay, oscillation, and adaptive stall.

        This method calculates a new temperature for generation \\(g\\) by composing three effects:
        
        1. **Exponential decay**  
           Temperature decays from the initial value \\(T_0\\) as  
           .. math::
              D(g) = \exp\bigl(-\,\alpha\,g\bigr),
           where \\(\alpha=\texttt{self.decay_rate}\\).  
        
        2. **Periodic oscillation**  
           Introduce a sinusoidal fluctuation with period \\(P\\):  
           .. math::
              O(g) = \sin\!\bigl(2\pi\,g/P\bigr),
           implemented by the helper `oscillation_factor(period, generation)`.  
        
        3. **Stall‐adaptive offset**  
           If the GA experiences consecutive “stalls” (no improvement), add a bounded offset  
           .. math::
              S(c) = 
              \begin{cases}
                M_{\max}\,\frac{c}{c_{\mathrm{half}}}, & 0 \le c \le c_{\mathrm{half}},\\[6pt]
                M_{\max}\,\bigl(1 - \tfrac{c - c_{\mathrm{half}}}{c_{\mathrm{half}}}\bigr), & c_{\mathrm{half}} < c \le 2c_{\mathrm{half}},
              \end{cases}
           where \\(c=\texttt{self.consecutive_stall}\\),  
           \\(M_{\max}=\texttt{self.max_stall_offset}\\), and \\(c_{\mathrm{half}}=1/\texttt{self.stall_growth_rate}\\).  
        
        The combined (raw) temperature is then  
        .. math::
           T_{\text{raw}}(g) = T_0 \,D(g)\;+\;O(g)\;+\;S\bigl(\texttt{self.consecutive_stall}\bigr).
        
        Finally, the result is clamped to the user‐specified bounds  
        .. math::
           T(g) = \min\bigl(\max(T_{\text{raw}},\,T_{\min}),\,T_{\max}\bigr),
        with \\((T_{\min},T_{\max})=\texttt{self.temperature_bounds}\\).

        :param generation:
            Current generation index \\(g\\).
        :type generation: int
        :param stall:
            Indicator of stall (non‐improvement) for this generation.  
            If \\(stall>0\\), increments the internal stall counter; otherwise, it decays.
        :type stall: int
        :returns:
            The updated, clamped temperature \\(T(g)\\).
        :rtype: float

        :raises ValueError:
            If `constant_temperature` is False but temperature bounds are invalid.
        """
        # Example: first compute a base decay, then an oscillation, 
        # then optionally combine with some other factors.

        # If “constant” mode is on, skip all update logic:
        if self.constant_temperature:
            return self.current_temperature

        decay_temperature_factor = decay_factor(
            decay_rate=self.decay_rate,
            generation=generation
        )
        oscillation_temperature_factor = oscillation_factor(
            period=self.period,
            generation=generation
        )

        max_cycles = int(1.0 / (self.stall_growth_rate + _EPS)  )

        if stall > 0:
            self.consecutive_stall += 1
            if self.consecutive_stall > 2 * max_cycles:
                self.consecutive_stall = 2 * max_cycles
        else:
            self.consecutive_stall = max(0, self.consecutive_stall-1)

            if self.consecutive_stall > max_cycles:
                self.consecutive_stall = max(
                   1, max_cycles - (self.consecutive_stall - max_cycles)
                )
            
        #self.consecutive_stall += 1 if stall > 0 else -1
        #self.consecutive_stall = max(0, min( float(1.0)/float(self.stall_growth_rate) , self.consecutive_stall))

        # Combine them (this is just an example, adapt to your actual logic).
        # E.g., if combined_rate is your function to merge these two values:
        new_temp = decay_temperature_factor * oscillation_temperature_factor + self.stall_coefficient() 

        # Update current_temperature and clamp it
        self.current_temperature = new_temp
        self.clamp_temperature()

        return self.current_temperature

    actualizate_temperature = update

    def stall_coefficient(self, function: str = '') -> float:
        r"""
        Compute a bounded stall offset that oscillates with consecutive failures.

        This method produces an additive offset \\(S(c)\\) that grows from zero up to
        a maximum \\(M_{\max}\\) as the internal stall counter \\(c = \texttt{self.consecutive_stall}\\)
        increases, and then symmetrically decays, forming a triangular wave over two
        “stall‐growth” cycles.

        Let  
        - \\(c\\) be the current stall count (an integer),  
        - \\(\gamma = \texttt{self.stall_growth_rate}\\) be the stall growth rate,  
        - \\(M_{\max} = \texttt{self.max_stall_offset}\\) be the maximum offset,  
        - \\(C = \frac{2}{\gamma}\\) be the full cycle length (number of stalls for a full rise+fall),  
        - \\(H = C/2\\) be the half‐cycle (rise or fall).

        Define the **phase** within the cycle as  
        .. math::
           \phi = c \bmod C,\quad \phi\in[0,\,C).

        Then the stall coefficient is  
        .. math::
           S(c) =
           \begin{cases}
              M_{\max}\,\dfrac{\phi}{H}, & 0 \le \phi \le H,\\[8pt]
              M_{\max}\,\Bigl(1 - \dfrac{\phi - H}{H}\Bigr), & H < \phi < 2H.
           \end{cases}

        This triangular waveform ensures that \\(0 \le S(c)\le M_{\max}\\)
        and resets after every \\(2H\\) stalls.

        :returns:
            A float stall coefficient \\(S(c)\\) bounded in \\([0,\,M_{\max}]\\).
        :rtype: float
        """

        # Use an exponential saturation function.
        full_cycle = int(2.0 / (self.stall_growth_rate + _EPS))  
        phase = self.consecutive_stall % full_cycle
        half_cycle = full_cycle // 2

        if phase <= half_cycle:
            coef = self.max_stall_offset * (phase / half_cycle)
        else:
            coef = self.max_stall_offset * (1 - ((phase - half_cycle) / half_cycle))

        return coef
        #return self.max_stall_offset * (1 - np.exp(-self.stall_growth_rate * self.consecutive_stall))

    def clamp_temperature(self):
        """
        Ensures the current temperature remains within the predefined bounds.
        If it falls outside, it is clamped to the min or max limit.
        """
        lower, upper = self.temperature_bounds
        if self.current_temperature < lower:
            self.current_temperature = lower
        elif self.current_temperature > upper:
            self.current_temperature = upper

    def force_max_temperature(self) -> float:
        """
        Forces the temperature to the maximum allowed bound, useful if the GA
        is stuck and an aggressive exploration phase is needed.

        Returns
        -------
        float
            The temperature after forcing it to the upper bound.
        """
        _, upper = self.temperature_bounds
        self.current_temperature = upper
        return self.current_temperature

    def force_min_temperature(self) -> float:
        """
        Forces the temperature to the minimum allowed bound, useful if 
        the system is moving too randomly and needs to be reined in.

        Returns
        -------
        float
            The temperature after forcing it to the lower bound.
        """
        lower, _ = self.temperature_bounds
        self.current_temperature = lower
        return self.current_temperature

    def reset(self):
        """
        Resets the current temperature and consecutive failure count to the
        initial conditions. Additionally, increments an internal counter that
        tracks how many resets have been performed.
        """
        self.current_temperature = self.initial_temperature
        self.consecutive_stall = 0
        self.reset_count += 1

    def evaluate_temperature_over_generations(self, max_generations: int=1000) -> List[float]:
        """
        Predicts how the temperature would evolve over a specified number
        of generations. This is useful for plotting or debugging to see how
        oscillation and decay would behave in isolation (i.e., ignoring real-time
        performance-based updates).

        Parameters
        ----------
        max_generations : int
            Number of generations to simulate.

        Returns
        -------
        List[float]
            A list of temperature values for each generation from 0 to max_generations-1.
        """
        import matplotlib.pyplot as plt
        import numpy as np
        import random

        generations_array = np.arange(1, max_generations, 1)
        #temperature_array = np.array([ self.actualizate_temperature(g, random.choice([1,1,1,1,1,1,1,1,])  ) for g in generations_array], dtype=np.float64)
        
        temperature_array = []
        stall_c = []
        for g in generations_array:
            if g < 500:
                temperature_array.append( self.actualizate_temperature(g, random.choice([0,0,0,1,1]) ) )
                stall_c.append( self.consecutive_stall )
            else:
                temperature_array.append( self.actualizate_temperature(g, random.choice([0,1,1,]) ) )
                stall_c.append( self.consecutive_stall )
        temperature_array = np.array(temperature_array)

        #plt.plot( generations_array, temperature_array )
        #plt.plot( generations_array, stall_c )
        #plt.show()

        temperature_array = []
        for g in generations_array:
            if g < 500:
                temperature_array.append( self.actualizate_temperature(g, 0) )
                stall_c.append( self.consecutive_stall )
            else:
                temperature_array.append( self.actualizate_temperature(g, 1) )
                stall_c.append( self.consecutive_stall )
        temperature_array = np.array(temperature_array)

        #plt.plot( generations_array, temperature_array )
        #plt.plot( generations_array, stall_c )
        #plt.show()

        temperature_array = []
        for g in generations_array:
            if g < 500:
                temperature_array.append( self.actualizate_temperature(g, 1) )
                stall_c.append( self.consecutive_stall )
            else:
                temperature_array.append( self.actualizate_temperature(g, 1) )
                stall_c.append( self.consecutive_stall )
        temperature_array = np.array(temperature_array)

        #plt.plot( generations_array, temperature_array )
        #plt.plot( generations_array, stall_c )
        #plt.show()

        return generations_array, temperature_array

    def record_temperature_evolution(
        self, 
        generations: int, 
        performance_metrics: Optional[List[float]] = None
    ) -> List[float]:
        """
        Records the evolution of the temperature over the specified number of generations,
        optionally factoring in a list of performance metrics for each generation
        (thus simulating more realistic adaptive behavior).

        Parameters
        ----------
        generations : int
            How many generations to simulate.
        performance_metrics : list of float, optional
            Performance metrics to consider each generation. If None or shorter than
            `generations`, the thermostat will assume a neutral performance metric.

        Returns
        -------
        List[float]
            The sequence of temperature values for each generation.
        """
        temp_evolution = []
        for gen in range(generations):
            # 1) Get baseline temperature from decay + oscillation
            baseline_temp = self.get_temperature(generation=gen)
            # 2) If a performance metric is provided, adapt accordingly
            if performance_metrics is not None and gen < len(performance_metrics):
                self.update_by_performance(performance_metrics[gen])

            temp_evolution.append(self.current_temperature)

        return temp_evolution
