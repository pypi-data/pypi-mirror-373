from abc import ABC


class BaseMapping(ABC):
    """Base mapping

    Parameters
    ----------
    ABC : AbstractBaseClass
        Abstract base class

    Raises
    ------
    NotImplementedError
        add not implemented
    NotImplementedError
        edit not implemented
    NotImplementedError
        get_all not implemented
    NotImplementedError
        get not implemented
    NotImplementedError
        delete not implemented
    NotImplementedError
        download not implemented
    """

    URL = None
    RESOURCE_TYPE = None

    def __init__(self, session):
        self.session = session

    def add(self):
        """Abstract method for add

        Raises
        ------
        NotImplementedError
            Not implemented
        """
        raise NotImplementedError

    def edit(self):
        """Abstract method for edit

        Raises
        ------
        NotImplementedError
            Not implemented
        """
        raise NotImplementedError

    def get_all(self):
        """Abstract method for get_all

        Raises
        ------
        NotImplementedError
            Not implemented
        """
        raise NotImplementedError

    def get(self):
        """Abstract method for get

        Raises
        ------
        NotImplementedError
            Not implemented
        """
        raise NotImplementedError

    def delete(self):
        """Abstract method for delete

        Raises
        ------
        NotImplementedError
            Not implemented
        """
        raise NotImplementedError

    def download(self):
        """Abstract method for download

        Raises
        ------
        NotImplementedError
            Not implemented
        """
        raise NotImplementedError
