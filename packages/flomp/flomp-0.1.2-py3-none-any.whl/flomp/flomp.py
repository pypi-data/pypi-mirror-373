
from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np


from flomp_plot import plot_signals
from flomp_plot import plot_plane
from src.flomp.flomp_plot import animate_temporal_plane


@dataclass
class Signal:
    tag: Optional[str] = None
    t: Optional[np.ndarray] = None
    vel: Optional[np.ndarray] = None

    def plot_vel(self,exp_dir: str | None = None, dpi = 300):
        plot_signals(
            [self.t],
            [self.vel],
            [self.tag],
            exp_dir=exp_dir, dpi = dpi)

@dataclass
class CompareSignal:
    tag: Optional[str] = None
    signal: List[Signal] = field(default_factory=list)

    def plot_vel(self, exp_dir: str | None = None, dpi = 300):
        plot_signals(
            [s.t for s in self.signal],
            [s.vel for s in self.signal],
            [s.tag for s in self.signal],
            self.tag,
            exp_dir=exp_dir, dpi=dpi)

@dataclass
class Plane:
    tag: Optional[str] = None
    pos: Optional[np.ndarray] = None
    vel: Optional[np.ndarray] = None

    def plot_surf(self, exp_dir: str | None = None, index = 0, dpi = 300):
        plot_plane(pos=self.pos, vel=self.vel, tag=self.tag,
                   exp_dir=exp_dir, dpi=dpi)

@dataclass
class ComparePlane:
    tag: Optional[str] = None
    plane: List[Signal] = field(default_factory=list)

@dataclass
class TimePlaneList:
    tag: Optional[str] = None
    plane: List[Plane] = field(default_factory=list)

    def plot_frame(self, exp_dir: str | None = None, frame_index = 0, dpi = 300):
        plot_plane(self.plane[frame_index].pos,
                   self.plane[frame_index].vel,
                   self.plane[frame_index].tag,
                   exp_dir=exp_dir, dpi=dpi)

    def animate_time(self, exp_dir: str | None = None,
                     frame_index_range = None, dpi = 300):
        animate_temporal_plane(
                    [p.pos for p in self.plane],
                    [p.vel for p in self.plane],
                    [p.tag for p in self.plane],
                    exp_dir=exp_dir, dpi=dpi)
