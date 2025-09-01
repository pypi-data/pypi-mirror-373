from abc import ABC, abstractmethod

class BaseClassifier(ABC):
    @abstractmethod
    def process(self, image, context: dict) -> dict:
        """Process an image and return classification results."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique name of the classifier."""
        pass
