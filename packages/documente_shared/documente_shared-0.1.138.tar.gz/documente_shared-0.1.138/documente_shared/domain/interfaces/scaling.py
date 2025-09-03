from abc import ABC, abstractmethod

from documente_shared.domain.entities.scaling import ScalingRequirements


class ScalingService(ABC):

    @abstractmethod
    def get_requirements(self) -> ScalingRequirements:
        raise NotImplementedError
