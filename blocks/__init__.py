'''
Dictionary of all block types in a dictionary with their type ID as 
the key

This list will be used to instantiate a class of the same name as a
decoder of the blocks found in a Stars! game file 
'''
import traceback

from blocks.Block import Block


BLOCKS = {
    0: "FileFooterBlock",
    1: "ManualSmallLoadUnloadTaskBlock",
    2: "ManualMediumLoadUnloadTaskBlock",
    3: "WaypointDeleteBlock",
    4: "WaypointAddBlock",
    5: "WaypointChangeTaskBlock",
    6: "PlayerBlock",
    7: "PlanetsBlock",
    8: "FileHeaderBlock",
    9: "FileHashBlock",
    10: "WaypointRepeatOrdersBlock",
    11: "UnknownBlock11Block",
    12: "EventsBlock",
    13: "PlanetBlock",
    14: "PartialPlanetBlock",
    15: "UnknownBlock15Block",
    16: "FleetBlock",
    17: "PartialFleetBlock",
    18: "UnknownBlock18Block",
    19: "WaypointTaskBlock",
    20: "WaypointBlock",
    21: "FleetNameBlock",
    22: "UnknownBlock22Block",
    23: "MoveShipsBlock",
    24: "FleetSplitBlock",
    25: "ManualLargeLoadUnloadTaskBlock",
    26: "DesignBlock",
    27: "DesignChangeBlock",
    28: "ProductionQueueBlock",
    29: "ProductionQueueChangeBlock",
    30: "BattlePlanBlock",
    31: "BattleBlock",
    32: "CountersBlock",
    33: "MessagesFilterBlock",
    34: "ResearchChangeBlock",
    35: "PlanetChangeBlock",
    36: "ChangePasswordBlock",
    37: "FleetsMergeBlock",
    38: "PlayersRelationChangeBlock",
    39: "BattleContinuationBlock",
    40: "MessageBlock",
    41: "AiHFileRecordBlock",
    42: "SetFleetBattlePlanBlock",
    43: "ObjectBlock",
    44: "RenameFleetBlock",
    45: "PlayerScoresBlock",
    46: "SaveAndSubmitBlock",
}


def createBlock(typeId, size, data):
    '''
    This method will create a block from the typeId
    '''
    className = BLOCKS[typeId]
    path = "blocks." + className + "." + className
    block = None
    
    try:
        clazz = import_class(path)
        block = clazz(typeId, size, data)
    except:
        print "Block type not implemented. typeId: %s; Class: %s" % (str(typeId), className)
        
        # Return generic block for now
        block = Block(typeId, size, data)
    
    return block



def import_class(clazz):
    (moduleName, className) = clazz.rsplit('.', 1) 

    module = __import__(moduleName, globals(), locals(), [className])
    
    return getattr(module, className)

