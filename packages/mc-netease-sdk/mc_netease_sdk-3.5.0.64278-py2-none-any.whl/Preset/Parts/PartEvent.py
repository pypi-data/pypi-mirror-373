# -*- coding: utf-8 -*-

from Preset.Model.PartBase import PartBase
from typing import List

def OnTriggerEntityEnter(TriggerPart, EnterEntityIds):
    # type: (PartBase, List[str]) -> 'None'
    """
    触发器范围有实体进入时触发，只适用于TriggerPart
    """
    pass

def OnTriggerEntityExit(TriggerPart, ExitEntityIds):
    # type: (PartBase, List[str]) -> 'None'
    """
    触发器范围有实体离开时触发，只适用于TriggerPart
    """
    pass

def OnTriggerEntityStay(TriggerPart, StayEntityIds):
    # type: (PartBase, List[str]) -> 'None'
    """
    触发器范围有实体停留时触发，只适用于TriggerPart
    """
    pass

