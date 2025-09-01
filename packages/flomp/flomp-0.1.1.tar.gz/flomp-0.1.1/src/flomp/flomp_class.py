
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
from flomp_plot import plot_signals

@dataclass
class Signal:
    tag: Optional[str] = None
    t: Optional[np.ndarray] = None
    vel: Optional[np.ndarray] = None

    def plot_vel(self, dpi = 300):
        plot_signals(
            [self.t],
            [self.vel],
            [self.tag],
            dpi = dpi)

@dataclass
class CompareSignal:
    case: Optional[str] = None
    signal: List[Signal] = field(default_factory=list)

    def plot_vel(self, dpi = 300):
        plot_signals(
            [s.t for s in self.signal],
            [s.vel for s in self.signal],
            [s.tag for s in self.signal],
            self.case, dpi=dpi)

@dataclass
class Surface:
    x_pos: Optional[np.ndarray] = None
    y_pos: Optional[np.ndarray] = None
    z_pos: Optional[np.ndarray] = None
    vel: Optional[np.ndarray] = None
