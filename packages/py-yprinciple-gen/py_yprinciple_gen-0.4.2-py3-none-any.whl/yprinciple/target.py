"""
Created on 2022-11-25

@author: wf
"""
from meta.metamodel import Topic

class Target:
    """
    a generator Target on the technical side of the Y-Principle
    """

    def __init__(
        self,
        name: str,
        icon_name: str = "bullseye",
        is_multi: bool = False,
        is_subtarget: bool = False,
        showInGrid: bool = True,
    ):
        """
        constructor
        name (str): the name of the target
        icon_name (str): the icon_name of the target
        is_multi(bool): if True this target creates a list of results (has subtargets)
        showInGrid (bool): if True this target is to be shown in the generator Grid

        """
        self.name = name
        self.icon_name = icon_name
        self.is_multi = is_multi
        self.is_subtarget = is_subtarget
        self.showInGrid = showInGrid
        self.subTarget = None

    def getLabelText(self, modelElement) -> str:
        return self.getPageTitle(modelElement)

    def getPageTitle(self, modelElement) -> str:
        pageTitle = f"{self.name}:{modelElement.name}"
        return pageTitle

    def getFileName(self, modelElement, purpose: str, fixcolon: bool = False) -> str:
        """
        get the filename for the given modelElement and purpose

        Args:
            modelElement:
            purpose (str): the purpose e.g. Help/Category ...

        Returns:
            str: a file name
        """
        prefix = self.getPageTitle(modelElement)
        # workaround for macos
        # https://apple.stackexchange.com/questions/173529/when-did-the-colon-character-become-an-allowed-character-in-the-filesystem
        if fixcolon:
            prefix = prefix.replace(":", "｜")
        prefix = prefix.replace(" ", "_")
        filename = f"{prefix}{purpose}.wiki"
        return filename

    def generate(self, topic: "Topic") -> str:
        raise Exception(f"No generator available for target {self.name}")
