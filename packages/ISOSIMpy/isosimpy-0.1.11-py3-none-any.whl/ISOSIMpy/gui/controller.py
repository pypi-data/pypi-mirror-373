import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal

from ..model import model as mm
from ..model import solver as ms
from ..model.registry import UNIT_REGISTRY


class Controller(QObject):
    simulated = pyqtSignal(np.ndarray)
    calibrated = pyqtSignal(np.ndarray)
    status = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, state):
        super().__init__()
        self.state = state
        self.ml = None

    def _lambda(self) -> float:
        if self.state.tracer == "Tritium":
            return 0.693 / (12.33 * (12.0 if self.state.is_monthly else 1.0))
        return 0.693 / (5700.0 * (12.0 if self.state.is_monthly else 1.0))

    def build_model(self):
        try:
            # We usually work in months (dt = 1.0); for yearly calculations
            # We therefore have to use dt = 12.0
            dt = 1.0 if self.state.is_monthly else 12.0
            lam = self._lambda()

            x = self.state.input_series
            y = self.state.target_series
            self.ml = mm.Model(
                dt,
                lam,
                input_series=x[1] if x else None,
                target_series=y[1] if y else None,
                steady_state_input=self.state.steady_state_input,
                n_warmup_half_lives=self.state.n_warmup_half_lives,
            )

            # Build per-instance units based on the detailed design
            instances = getattr(self.state, "design_instances", [])
            for inst in instances:
                unit_name: str = inst["name"]
                prefix: str = inst["prefix"]
                frac: float = float(inst.get("fraction", 0.0))

                cls = UNIT_REGISTRY[unit_name]
                spec = getattr(cls, "PARAMS", [])

                # Parameter values with safe defaults
                kwargs = {}
                for p in spec:
                    key = p["key"]
                    default_val = p.get("default")
                    rec = self.state.params.get(prefix, {}).get(key)
                    kwargs[key] = rec["val"] if rec is not None else default_val

                unit = cls(**kwargs)

                # Bounds with safe defaults
                bounds = []
                for p in spec:
                    key = p["key"]
                    default_lb, default_ub = p.get("bounds", (None, None))
                    rec = self.state.params.get(prefix, {}).get(key)
                    lb = rec["lb"] if rec is not None else default_lb
                    ub = rec["ub"] if rec is not None else default_ub
                    bounds.append((lb, ub))

                self.ml.add_unit(
                    unit=unit,
                    fraction=frac,
                    prefix=prefix,
                    bounds=bounds,
                )

                # Fixed flags
                for p in spec:
                    key = p["key"]
                    rec = self.state.params.get(prefix, {}).get(key)
                    if rec is not None and rec.get("fixed", False):
                        self.ml.set_fixed(f"{prefix}.{key}", True)

        except Exception as e:
            self.error.emit(str(e))
            self.ml = None

    def simulate(self):
        try:
            self.build_model()
            if self.ml is None:
                return
            sim = self.ml.simulate()
            self.state.last_simulation = sim
            self.simulated.emit(sim)
            self.status.emit("Simulation finished.")
        except Exception as e:
            self.error.emit(str(e))

    def calibrate(self):
        try:
            self.build_model()
            if self.ml is None:
                return
            # This currently only includes the Differential Evolution solver
            solver = ms.Solver(model=self.ml)
            _, sim = solver.differential_evolution()
            self.state.last_simulation = sim
            self.calibrated.emit(sim)
            self.status.emit("Calibration finished.")
        except Exception as e:
            self.error.emit(str(e))

    def write_report(self, filename):
        if self.ml is None:
            return
        if self.state.is_monthly:
            frequency = "1 month"
        else:
            frequency = "1 year"
        self.ml.write_report(filename=filename, frequency=frequency)
