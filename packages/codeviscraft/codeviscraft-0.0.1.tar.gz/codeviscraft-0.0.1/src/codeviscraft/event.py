from .vec3 import Vec3

class BlockEvent:
    """An Event related to blocks (e.g. placed, removed, hit)"""

    def __init__(self, entityId, material, x, y, z, face):
        self.entityId = entityId
        self.material = material
        self.x = x
        self.y = y
        self.z = z
        self.face = face

    def __repr__(self):
        return "BlockEvent(%d, %s, %d, %d, %d, %d)"%(self.entityId, self.material, self.x, self.y, self.z, self.face);

class EntityDeathEvent:
    def __init__(self, killerId, killerName, entityId, entityType, x, y, z):
        self.killerId = killerId
        self.killerName = killerName
        self.entityId = entityId
        self.entityType = entityType
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "EntityDeathEvent(%d, %s, %d, %s, %d, %d, %d)"%(self.killerId, self.killerName, self.entityId, self.entityType, self.x, self.y, self.z);


class EntitySpawnEvent:
    def __init__(self, entityId, entityType, x, y, z):
        self.entityId = entityId
        self.entityType = entityType
        self.x = x
        self.y = y
        self.z = z
    def __repr__(self):
        return "EntitySpawnEvent(%d, %s, %d, %d, %d)"%(self.entityId, self.entityType, self.x, self.y, self.z);

class EntityDamageEvent:
    def __init__(self, entityId, entityType, cause, damage, x, y, z):
        self.entityId = entityId
        self.entityType = entityType
        self.cause = cause
        self.damage = damage
        self.x = x
        self.y = y
        self.z = z
    def __repr__(self):
        return "EntityDamageEvent(%d, %s, %s, %d, %d, %d, %d)"%(self.entityId, self.entityType, self.cause, self.damage, self.x, self.y, self.z);

class BlockBreakEvent:
    def __init__(self, material, entityId, name, x, y, z):
        self.material = material
        self.entityId = entityId
        self.name = name
        self.x = x
        self.y = y
        self.z = z
    #return "BlockBreakEvent(%d, %s, %d, %d, %d)"%(self.entityId, self.name, self.x, self.y, self.z);
    def __repr__(self):
        return "BlockBreakEvent(%s, %d, %s, %d, %d, %d)"%(self.material, self.entityId, self.name, self.x, self.y, self.z);

class PlayerHarvestBlockEvent:
    def __init__(self, playerId, name, material, x, y, z):
        self.playerId = playerId
        self.name = name
        self.material = material
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "BlockBreakEvent(%d, %s, %s, %d, %d, %d)"%(self.playerId, self.name, self.material, self.x, self.y, self.z);

class ArrowHitEvent:
    """An Event related to blocks (e.g. placed, removed, hit)"""

    def __init__(self, entityId, x, y, z):
        self.entityId = entityId
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "ArrowHitEvent(%s, %d, %d, %d)"%(self.entityId, self.x, self.y, self.z);

class EntityPickupItemEvent:
    def __init__(self, entityId, entityName, material, amount):
        self.entityId = entityId
        self.entityName = entityName
        self.material = material
        self.amount = amount

    def __repr__(self):
        return "EntityPickupItemEvent(%d, %s, %s, %d)"%(self.entityId, self.entityName, self.material, self.amount);

class PlayerFishEvent:
    def __init__(self, playerId, entityName, state, caught):
        self.playerId = playerId
        self.entityName = entityName
        self.state = state
        self.caught = caught

    def __repr__(self):
        return "PlayerFishEvent(%d, %s, %s, %s)"%(self.playerId, self.entityName, self.state, self.caught);

class InteractEntityEvent:
    def __init__(self, playerId, playerName, entityId, entityType, x, y, z):
        self.playerId = playerId
        self.playerName = playerName
        self.entityId = entityId
        self.entityType = entityType
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "InteractEntityEvent(%d, %s, %d, %s, %d, %d, %d)"%(self.playerId, self.playerName, self.entityId, self.entityType, self.x, self.y, self.z);

class ChatEvent:
    """An Event related to chat (e.g. posts)"""
    POST = 0

    def __init__(self, type, entityId, message):
        self.type = type
        self.entityId = entityId
        self.message = message

    def __repr__(self):
        sType = {
            ChatEvent.POST: "ChatEvent.POST"
        }.get(self.type, "???")

        return "ChatEvent(%s, %d, %s)"%(
            sType,self.entityId,self.message);

    @staticmethod
    def Post(entityId, message):
        return ChatEvent(ChatEvent.POST, entityId, message)
