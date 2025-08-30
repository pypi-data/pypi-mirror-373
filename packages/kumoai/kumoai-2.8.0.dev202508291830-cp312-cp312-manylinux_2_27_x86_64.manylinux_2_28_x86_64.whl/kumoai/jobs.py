from abc import ABC, abstractmethod
from typing import Generic, Mapping, Optional, TypeVar

from kumoapi.jobs import JobStatusReport

from kumoai.client.jobs import CommonJobAPI, JobRequestType, JobResourceType

IDType = TypeVar('IDType', bound=str)


class JobInterface(ABC, Generic[IDType, JobRequestType, JobResourceType]):
    r"""Defines a standard interface for job objects"""
    @staticmethod
    @abstractmethod
    def _api() -> CommonJobAPI[JobRequestType, JobResourceType]:
        pass

    @property
    @abstractmethod
    def id(self) -> IDType:
        pass

    @abstractmethod
    def status(self) -> JobStatusReport:
        pass

    def get_tags(self) -> dict[str, str]:
        r"""Returns the tags of the job."""
        return self._api().get(self.id).tags

    def delete_tags(self, tags: list[str]) -> bool:
        r"""Removes the tags from the job.

        Args:
            tags (list[str]): The tags to remove.
        """
        return self._api().delete_tags(self.id, tags)

    def update_tags(self, tags: Mapping[str, Optional[str]]) -> bool:
        r"""Updates the tags of the job.

        Args:
            tags (Mapping[str, Optional[str]]): The tags to update.
                Note that the value 'none' will remove the tag. If the tag is
                not present, it will be added.
        """
        return self._api().update_tags(self.id, tags)

    @abstractmethod
    def load_config(self) -> JobRequestType:
        pass

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(job_id={self.id})'
