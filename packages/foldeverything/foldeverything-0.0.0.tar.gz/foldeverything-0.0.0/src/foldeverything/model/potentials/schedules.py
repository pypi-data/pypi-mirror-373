import math
from abc import ABC

class ParameterSchedule(ABC):
    def __init__(self, parameters=None):
        self.parameters = parameters

    def compute_parameters(self, t, parameters=None):
        if parameters is None:
            if self.parameters is None:
                return None
            parameters = self.parameters
              
        computed_parameters = {}
        for key, value in parameters.items():
            if isinstance(value, dict):
                computed_parameters[key] = {k: self.compute_parameters(v, t) for k, v in value.items()}
            if isinstance(value, list):
                computed_parameters[key] = [self.compute_parameters(item, t) for item in value]
            elif isinstance(value, ParameterSchedule):
                computed_parameters[key] = value.compute(t)
            else:
                computed_parameters[key] = value
        return computed_parameters

    def compute(self, t):
        raise NotImplementedError

class ExponentialInterpolation(ParameterSchedule):
    def compute(self, t):
        parameters = self.compute_parameters(t)
        start, end, alpha = parameters['start'], parameters['end'], parameters['alpha']

        if alpha != 0:
            return start + (end - start) * (math.exp(alpha * t) - 1) / (math.exp(alpha) - 1)
        else:
            return start + (end - start) * t

class PiecewiseStepFunction(ParameterSchedule):
    def compute(self, t):
        parameters = self.compute_parameters(t)
        thresholds, values = parameters['thresholds'], parameters['values']
        assert len(thresholds) > 0
        assert len(values) == len(thresholds) + 1

        idx = 0
        while idx < len(thresholds) and t > thresholds[idx]:
            idx += 1
        return values[idx]