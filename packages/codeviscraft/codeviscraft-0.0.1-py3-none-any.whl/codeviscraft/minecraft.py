import logging
import random
import typing

from .potionEffectType import PotionEffectType
from .treetype import TreeType
from .equipmentslot import EquipmentSlot
from .entityeffect import EntityEffect
from .displayslot import DisplaySlot
from .criteria import Criteria
from .barflag import BarFlag
from .barstyle import BarStyle
from .color import Color
from .statistic import Statistic
from .enchantments import Enchantment
from .attributes import Attribute
from .sound import Sound
from .particle import Particle
from .instrument import Instrument
from .effect import Effect
from .connection import Connection
from .block import Block
from .vec3 import Vec3
from .event import * #BlockEvent, ChatEvent, ArrowHitEvent, BlockBreakEvent, EntityDeathEvent, InteractEntityEvent
from .entity import Entity
from .material import Material
from .itemrarity import ItemRarity
from .util import flatten
from warnings import warn
from .logger import *
import sys

""" Minecraft PI low level api v0.1_1
    @author: Sergey Vysokov """


def intFloor(*args):
    return [int(x) for x in flatten(args)]


class CmdPositioner:
    """Methods for setting and getting positions"""

    def __init__(self, connection, packagePrefix):
        self.conn = connection
        self.pkg = packagePrefix

    def getPos(self, ID) -> Vec3:
        """Get entity position (entityId:int) => Vec3"""
        s = self.conn.sendReceive(self.pkg + b".getPos", ID)
        return Vec3(*list(map(float, s.split(","))))

    def setPos(self, ID, x: float, y: float, z: float) -> None:
        """Set entity position (entityId:int, x,y,z)"""
        self.conn.send(self.pkg + b".setPos", ID, x, y, z)

    def getTilePos(self, ID) -> Vec3:
        """Get entity tile position (entityId:int) => Vec3"""
        s = self.conn.sendReceive(self.pkg + b".getTile", ID)
        return Vec3(*list(map(int, s.split(","))))

    def setTilePos(self, ID, x: int, y: int, z: int) -> None:
        """Set entity tile position (entityId:int) => Vec3"""
        self.conn.send(self.pkg + b".setTile", ID, x, y, z)

    def getDirection(self, ID) -> Vec3:
        """Get direction of the entity"""
        s = self.conn.sendReceive(self.pkg + b".getDirection", id)
        return Vec3(*list(s.split(",")))

    def setDirection(self, ID, x: float, y: float, z: float) -> None:
        """Set direction of the entity"""
        self.conn.send(self.pkg + b".setDirection", ID, x, y, z)

    def getRotation(self, ID) -> float:
        """Get rotation if the entity"""
        s = self.conn.sendReceive(self.pkg + b".getRotation", ID)
        return float(s)

    def setRotation(self, ID, yaw) -> float:
        """Set rotation if the entity"""
        self.conn.send(self.pkg + b".setRotation", ID, yaw)

    def getPitch(self, ID) -> float:
        """Get pitch if the entity"""
        s = self.conn.sendReceive(self.pkg + b".getPitch", ID)
        return float(s)

    def setPitch(self, ID, pitch) -> None:
        """Set pitch if the entity"""
        self.conn.send(self.pkg + b".setPitch", ID, pitch)

    def setting(self, setting, status) -> None:
        """Set a player setting (setting, status). keys: autojump"""
        self.conn.send(self.pkg + b".setting", setting, 1 if bool(status) else 0)





class CmdEntity(CmdPositioner):
    """Methods for entities"""

    def __init__(self, connection):
        CmdPositioner.__init__(self, connection, b"entity")

    def addPotionEffect(self, entityId: int, potionEffectType: str, duration: int, amplifier: int, ambient: bool = True, particles: bool = True, icon: bool = True) -> None:
        """
        Применяет эффект зелья к игроку
        :param entityId: id-игрока
        :param potionEffectType: тип эффекта PotionEffectType.
        :param duration: продолжительность сек.
        :param amplifier: уровень эффекта
        :param ambient: звук True/False
        :param particles: чатицы True/False
        :param icon: иконца True/False
        """
        self.conn.send(self.pkg + b".addPotionEffect", entityId, potionEffectType.upper(), duration * 20, amplifier, ambient, particles, icon)

    def removePotionEffects(self, entityId: int):
        """ Снимает все эффекты зелий с игрока """
        self.conn.send(self.pkg + b".removePotionEffects", entityId)

    def hasPotionEffect(self, entityId: int, potionEffectType: str) -> bool:
        """
        Возвращает True, если существо имеет примененный эффект зелья
        :param entityId: id-существа
        :param potionEffectType: тип эффектс PotionEffectType.
        :return: bool
        """
        result = self.conn.sendReceive(self.pkg + b".hasPotionEffect", entityId, potionEffectType)
        return eval(result[0].upper() + result[1:])

    def setPlayerListHeaderFooter(self, playerId: int, header: str, footer: str) -> None:
        self.conn.send(self.pkg + b".setPlayerListHeaderFooter", playerId, header, footer)

    def getName(self, entityId):
        """Возвращает список игроков => [name:str]"""
        return self.conn.sendReceive(b"entity.getName", entityId)

    def getFoodLevel(self, entityId: int) -> int:
        """Возвращает уровень пищи игрока"""
        return int(self.conn.sendReceive(self.pkg + b".getFoodLevel", entityId))

    def setFoodLevel(self, foodLevel: int, entityId: int) -> None:
        """ Устанавливает уровень пищи игрока """
        self.conn.send(self.pkg + b".setFoodLevel", foodLevel, entityId)

    def getHealth(self, entityId) -> float:
        """:return Возвращает значение здоровья объекта."""
        return float(self.conn.sendReceive(self.pkg + b".getHealth", entityId))

    def getPing(self, entityId) -> float:
        """:return Возвращает расчетный пинг игрока в миллисекундах."""
        return float(self.conn.sendReceive(self.pkg + b".getPing", entityId))

    def getExp(self, entityId) -> float:
        """:return Возвращает текущие очки опыта игрока для перехода на следующий уровень."""
        return float(self.conn.sendReceive(self.pkg + b".getExp", entityId))

    def getTotalExp(self, entityId) -> int:
        """:return  Возвращает общее количество очков опыта игроков."""
        return int(self.conn.sendReceive(self.pkg + b".getTotalExp", entityId))

    def getLevel(self, entityId) -> float:
        """:return Возвращает текущий уровень опыта игроков."""
        return float(self.conn.sendReceive(self.pkg + b".getLevel", entityId))

    def getWalkSpeed(self, entityId) -> float:
        """:return Возвращает скорость бега."""
        return float(self.conn.sendReceive(self.pkg + b".getWalkSpeed", entityId))

    def getPlayerTime(self, entityId) -> float:
        """:return Возвращает текущую временную метку игрока."""
        return float(self.conn.sendReceive(self.pkg + b".getPlayerTime", entityId))

    def getAddress(self, entityId) -> str:
        """:return Возвращает адрес пользователя."""
        return self.conn.sendReceive(self.pkg + b".getAddress", entityId)

    def getGamemode(self, entityId) -> str:
        """ :return: CREATIVE SURVIVAL HARDCORE SPECTATOR ADVENTURE """
        return self.conn.sendReceive(self.pkg + b".getGamemode", entityId)

    def getHealthScale(self, entityId) -> float:
        """ :return: Получает число, до которого масштабируется здоровье существа. """
        return float(self.conn.sendReceive(self.pkg + b".getHealthScale", entityId))

    def getFlySpeed(self, entityId) -> float:
        """ :return: Возвращает скорость полета. """
        return float(self.conn.sendReceive(self.pkg + b".getFlySpeed", entityId))

    def setStatistic(self, *args) -> None:
        """
        Устанавливает значение указанной статистики игрока
        :param args: playerId, statistic, amount
        :param args: playerId, statistic, entity, amount
        :param args: playerId, statistic, material, amount
        """
        self.conn.send(self.pkg + b".setStatistic", args)

    def getStatistic(self, *args) -> int:
        """
        Возвращает значение статистики игрока
        :param args: playerId, statistic
        :param args: playerId, statistic, entity
        :param args: playerId, statistic, material
        """
        return int(self.conn.sendReceive(self.pkg + b".getStatistic", args))

    def getAllStatistics(self, playerId) -> dict:
        """ Возвращает словарь полной статистики игрока -> {Statistic:amount}"""
        statistic = self.conn.sendReceive(self.pkg + b".getAllStatistics", playerId)
        statistic_dict = statistic.split("|")
        statistic_dict.pop()
        return dict([[s.split(":")[0], int(s.split(":")[1])] for s in statistic_dict])

    def giveExp(self, entityId, exp: int) -> None:
        """
        Дает игроку указанное количество опыта.
        :param exp: количество опыта.
        """
        self.conn.send(self.pkg + b".giveExp", entityId, exp)

    def giveExpLevels(self, entityId, exp: int) -> None:
        """
        Дает игроку указанное количество уровней опыта.
        :param exp: количество опыта.
        """
        self.conn.send(self.pkg + b".giveExpLevels", entityId, exp)

    def isFlying(self, entityId) -> bool:
        """ :return Проверяет, летает ли этот игрок в данный момент или нет. """
        result = (self.conn.sendReceive(self.pkg + b".isFlying", entityId))
        return eval(result[0].upper() + result[1:])

    def isHealthScaled(self, entityId) -> bool:
        """ :return Получает значение, если клиенту отображается «масштабированное» состояние здоровья,
         то есть состояние здоровья по шкале от 0 до getHealthScale(). """
        result = (self.conn.sendReceive(self.pkg + b".isHealthScaled", entityId))
        return eval(result[0].upper() + result[1:])

    def isSneaking(self, entityId) -> bool:
        """ :return Возвращает, если игрок находится в режиме подкрадывания. """
        result = (self.conn.sendReceive(self.pkg + b".isSneaking", entityId))
        return eval(result[0].upper() + result[1:])

    def isSprinting(self, entityId) -> bool:
        """ :return Получает информацию о том, бежит игрок или нет. """
        result = (self.conn.sendReceive(self.pkg + b".isSprinting", entityId))
        return eval(result[0].upper() + result[1:])

    def isCollidable(self, entityId) -> bool:
        """ :return Возвращает True, если этот объект подвержен коллизиям с другими объектами. """
        result = (self.conn.sendReceive(self.pkg + b".isCollidable", entityId))
        return eval(result[0].upper() + result[1:])

    def isOnline(self, entityId) -> bool:
        """ :return Проверяет, находится ли этот игрок в данный момент онлайн. """
        result = (self.conn.sendReceive(self.pkg + b".isOnline", entityId))
        return eval(result[0].upper() + result[1:])

    def isOnGround(self, entityId) -> bool:
        """ :return Возвращает true, если сущность поддерживается блоком """
        result = (self.conn.sendReceive(self.pkg + b".isOnGround", entityId))
        return eval(result[0].upper() + result[1:])


    def isOp(self, entityId) -> bool:
        """ :return Проверяет, является ли этот объект оператором сервера. """
        result = (self.conn.sendReceive(self.pkg + b".isOp", entityId))
        return eval(result[0].upper() + result[1:])

    def isDead(self, entityId) -> bool:
        """ :return Возвращает true, если эта сущность мертва. """
        result = (self.conn.sendReceive(self.pkg + b".isDead", entityId))
        return eval(result[0].upper() + result[1:])

    def isInvulnerable(self, entityId) -> bool:
        """ :return Получает информацию о том, является ли объект неуязвимым или нет. """
        result = (self.conn.sendReceive(self.pkg + b".isInvulnerable", entityId))
        return eval(result[0].upper() + result[1:])

    def setGamemode(self, entityId, gameMode: str) -> None:
        """
        Установить игровой режим для объекта.
        :param entityId: playerId -> mc.getPlayerEntityId("PLAYER_NAME")
        :param gameMode: CREATIVE SURVIVAL HARDCORE SPECTATOR ADVENTURE
        """
        self.conn.send(self.pkg + b".setGamemode", entityId, gameMode)

    def setHealth(self, entityId, health: float) -> None:
        """
        Установить текущее здоровье существа.
        :param entityId: playerId -> mc.getPlayerEntityId("PLAYER_NAME")
        :param health: 0, 1 ... 20
        """
        self.conn.send(self.pkg + b".setHealth", entityId, health)

    def setExp(self, entityId, exp: float) -> None:
        """
        Установить значение опыта.
        :param entityId: playerId -> mc.getPlayerEntityId("PLAYER_NAME")
        :param exp: 0, 0.1 ... 1
        """
        self.conn.send(self.pkg + b".setExp", entityId, exp)

    def setAttribute(self, entityId, attribute, amount):
        """
        Добавить атрибут существу
        :param entityId: id-существа
        :param attribute: Attribute.
        :param amount: величина атрибута
        """
        self.conn.send(self.pkg + b".setAttribute", entityId, attribute, amount)

    def getAttributeValue(self, entityId, attribute):
        """
        Возвращает значение указанного атрибута
        :param entityId: id-существа
        :param attribute: Attribute.
        """
        return float(self.conn.sendReceive(self.pkg + b".getAttributeValue", entityId, attribute))

    def setAllowFlight(self, entityId, flight: bool) -> None:
        """ Устанавливает, разрешено ли игроку летать с помощью двойного нажатия клавиши прыжка,
         как в творческом режиме. """
        self.conn.send(self.pkg + b".setAllowFlight", entityId, flight)

    def setFlySpeed(self, entityId, flySpeed: float) -> None:
        """
        Устанавливает скорость полета игрока.
        defalut: 0.1
        :param flySpeed: 0, 0.1 ... 1
        """
        self.conn.send(self.pkg + b".setFlySpeed", entityId, flySpeed)

    def setLevel(self, entityId, level: int) -> None:
        """ Устанавливает уровень игрока. """
        self.conn.send(self.pkg + b".setLevel", entityId, level)

    def setTotalExperience(self, entityId, experience: int) -> None:
        """
        Устанавливает текущие очки опыта игрока.
        Это относится к общему количеству опыта, который игрок накопил с течением времени
        и в настоящее время не отображается клиенту.
        """
        self.conn.send(self.pkg + b".setTotalExperience", entityId, experience)

    def setWalkSpeed(self, entityId, walkspeed: float) -> None:
        """
        Устанавливает скорость бега игрока.
        default walkspeed: 0.2
        :param walkspeed: 0, 0.1 ... 1
        """
        self.conn.send(self.pkg + b".setWalkSpeed", entityId, walkspeed)

    def setInvulnerable(self, entityId, invulnerable: bool) -> None:
        """ Устанавливает неуязвимость. """
        self.conn.send(self.pkg + b".setInvulnerable", entityId, invulnerable)

    def setOp(self, entityId, op: bool) -> None:
        """ Устанавливает статус оператора этого объекта. """
        self.conn.send(self.pkg + b".setOp", entityId, op)

    def spawnParticle(self, playerId, particle: str, amount: int) -> None:
        """
        Создает частицу (количество раз, указанное в счетчике) в целевом месте.
        Particle.
        :param particleName: CLOUD DAMAGE_INDICATOR GLOW HEART ...
        :param amount: 0, 1 ...
        """
        self.conn.send(self.pkg + b".spawnParticle", playerId, particle, amount)

    def setItemInMainHand(self, *args):
        """
        Устанавливает предмет в основной руке игрока
        :param args: ItemStack
        :param args: Material, количество
        :return:
        """
        if len(args) == 1:
            self.conn.send(self.pkg + b".setItemInMainHand", args[0], args[1].name)
        else:
            self.conn.send(self.pkg + b".setItemInMainHand", args)

    def getItemInMainHand(self, playerId) -> str:
        """ :return: вощвращает предмет в основной руке. """
        material = self.conn.sendReceive(self.pkg + b".getItemInOffHand", playerId)
        if material == "":
            return None
        else:
            return self.conn.sendReceive(self.pkg + b".getItemInOffHand", playerId)


    def getItemInOffHand(self, playerId) -> str:
        """ :return: вощвращает предмет во второстепенной руке. """
        material = self.conn.sendReceive(self.pkg + b".getItemInOffHand", playerId)
        if material == "":
            return None
        else:
            return self.conn.sendReceive(self.pkg + b".getItemInOffHand", playerId)

    def setItemInOffHand(self, *args) -> None:
        """
        Устанавливает предмет во второстепенной руке игрока
        :param args: ItemStack
        :param args: Material, количество
        """
        if len(args) == 1:
            self.conn.send(self.pkg + b".setItemInOffHand", self.playerId, args[0].name)
        else:
            self.conn.send(self.pkg + b".setItemInOffHand", self.playerId, args)

    def getHelmet(self, playerId):
        material = self.conn.sendReceive(self.pkg + b".getHelmet", playerId)
        if material == "":
            return None
        else:
            return self.conn.sendReceive(self.pkg + b".getHelmet", playerId)

    def getChestplate(self, playerId):
        material = self.conn.sendReceive(self.pkg + b".getChestplate", playerId)
        if material == "":
            return None
        else:
            return self.conn.sendReceive(self.pkg + b".getChestplate", playerId)

    def getLeggings(self, playerId):
        material = self.conn.sendReceive(self.pkg + b".getLeggings", playerId)
        if material == "":
            return None
        else:
            return self.conn.sendReceive(self.pkg + b".getLeggings", self.playerId)

    def getBoots(self, playerId):
        material = self.conn.sendReceive(self.pkg + b".getBoots", playerId)
        if material == "":
            return None
        else:
            return self.conn.sendReceive(self.pkg + b".getBoots", playerId)

    def setItemInOffHand(self, *args):
        """
        Устанавливает предмет во второстепенной руке игрока
        :param args: ItemStack
        :param args: Material, количество
        :return:
        """
        if len(args) == 1:
            self.conn.send(self.pkg + b".setItemInOffHand", args[0], args[1].name)
        else:
            self.conn.send(self.pkg + b".setItemInOffHand", args)


    def getItemAmount(self, playerId: int, index: int) -> int:
        """
        Возвращает количество предментов в ячейке инвентаря
        :param index: ячейка инвентаря
        """
        return int(self.conn.sendReceive(self.pkg + b".getItemAmount", playerId, index))

    def getItemType(self, playerId: int, index: int) -> str:
        """
        Возвращает тип предмета в ячейке инвентаря
        :param index: ячейка инвентаря
        """
        return self.conn.sendReceive(self.pkg + b".getItemType", playerId, index)

    def getInventoryContents(self, playerId) -> list:
        """
        Возвращает контент инвентаря игрока.
        :returns [[index, type, amount]]
        """
        s = self.conn.sendReceive(self.pkg + b".getInventory", playerId)
        inventory = [i for i in s.split("|") if i]
        return [[int(n.split(",")[0]), n.split(",")[1], int(n.split(",")[2])] for n in inventory]

    def getInventoryArmorContents(self, playerId) -> list:
        """
        Возвращает контент слоты брони игрока.
        :returns [[index, type, amount]]
        """
        s = self.conn.sendReceive(self.pkg + b".getArmorContents", playerId)
        inventory = [i for i in s.split("|") if i]
        return [[int(n.split(",")[0]), n.split(",")[1], int(n.split(",")[2])] for n in inventory]

    def clearInventory(self, playerId) -> None:
        """ Очищает инвентарь игрока. """
        self.conn.send(self.pkg + b".clearInventory", playerId)

    def removeItem(self, playerId, index: int) -> None:
        """ Удаляет предмет из инвентаря по индексу """
        self.conn.send(self.pkg + b".removeItem", playerId, index)

    def containsItem(self, playerId, material: str) -> bool:
        """ Проверяет наличие предмета в инвентаре игрока. """
        result = bool(self.conn.sendReceive(self.pkg + b".containsItem", playerId, material))
        return eval(result[0].upper() + result[1:])

    def containsItemStack(self, playerId, itemStack) -> bool:
        """ Проверяет наличие ItemStack в инвентаре игрока. """
        return bool(self.conn.sendReceive(self.pkg + b".containsItemStack", playerId, itemStack.name))

    def findItemStack(self, playerId, itemStack):
        """
        Поиск предмета ItemStack в инвентаре
        :param playerId: id-игрока
        :param itemStack: объект ItemStack
        :return: индекс ячейки предмета, -1 в случае отсутствия
        """
        try:
            return int(self.conn.sendReceive(self.pkg + b".findItemStack", playerId, itemStack.name))
        except:
            return -1

    def setItemStack(self, playerId, index, itemStack):
        self.conn.send(self.pkg + b".setItemStack", playerId, index, itemStack.name)


    def addItem(self, playerId, material: str, amount: int = 1) -> None:
        """
        Добавляет предмент игроку в инвентарь.
        :param material: DIAMOND_AXE IRON_SWORD DIRT COBBLESTONE
        :param amount: 0, 1 ... stackSize
        """
        self.conn.send(self.pkg + b".addItem", playerId,  material, amount)

    def setItem(self, playerId: int, index: int, material: str, amount: int):
        """
        Устанавливает предмет в ячейке инвентаря
        :param playerId: id игрока
        :param index: номер ячейки
        :param material: материал
        :param amount: количество
        """
        self.conn.send(self.pkg + b".setItem", playerId, index, material, amount)

    def addItemStack(self, playerId, itemStack) -> None:
        """
        Добавляет ItemStack игроку в инвентарь.
        :param itemStack: ItemStack object
        """
        if not isinstance(itemStack, ItemStack):
            logging.warning("itemStack не является объектом класса ItemStack")
        else:
            self.conn.send(self.pkg + b".addItemStack", playerId, itemStack.name)


    def playEffect(self, playerId, effectName: str, data: int = 1) -> None:
        """
        Воспроизводит эффект в координатах игрока
        :param effectName: END_GATEWAY_SPAWN ENDER_SIGNAL POTION_BREAK ...
        :param data: 1-10
        """
        self.conn.send(self.pkg + b".playEffect", playerId, effectName, data)

    def playNote(self, playerId, instrument: str, octave: int, note: str):
        """
        Воспроизводит ноту заданного инструмента у игрока.
        :param instrument: BANJO BASS_DRUM BASS_GUITAR ...
        :param octave: 0 1
        :param note: A B C D E F G
        """
        self.conn.send(self.pkg + b".playNote", playerId, instrument, octave, note)

    def playSound(self, playerId, sound: str, volume: float = 1, pitch: float = 1):
        """
        Воспроизводит звук у игрока.
        https://hub.spigotmc.org/javadocs/bukkit/org/bukkit/Sound.html
        :param sound: MUSIC_DISC_CAT MUSIC_DISC_MELLOHI MUSIC_DRAGON MUSIC_DISC_CHIRP ENTITY_WOLF_AMBIENT
        :param volume: 0, 0.1 ... 1
        :param pitch: 0, 0.1 ... 3
        :return:
        """
        self.conn.send(self.pkg + b".playSound", playerId, sound, volume, pitch)

    def stopAllSound(self, playerId):
        """ Останавливает все звуки у игрока. """
        self.conn.send(self.pkg + b".stopAllSounds", playerId)

    def sendTitle(self, playerId, title: str, subTitle: str = "", fadeIn: int = 10, stay: int = 70, fadeOut: int = 20) -> None:
        """ Отправляет игроку заголовок с субтитрами. """
        self.conn.send(self.pkg + b".sendTitle", playerId, title, subTitle, fadeIn, stay, fadeOut)

class Mob():
    def __init__(self, connection):
        self.conn = connection

    def spawnMob(self, x: int, y: int, z: int, entity: str) -> int:
        """
        Создать существо в указанных координатах
        :param entity: Entity.
        :return возвращает id существа
        """
        return int(self.conn.sendReceive(b"mob.spawnMob", x, y, z, entity))

    def setPos(self, mob_id: int, x: int, y: int, z: int) -> None:
        """ Установить позицию существу """
        self.conn.send(b"mob.setPos", mob_id, x, y, z)

    def getPos(self, mob_id) -> Vec3:
        return Vec3(*list(map(float, self.conn.sendReceive(b"mob.getPos", mob_id).split(","))))

    def moveTo(self, mob_id, x, y, z):
        self.conn.send(b"mob.moveTo", mob_id, x, y, z)

    def remove(self, mob_id: int) -> None:
        """ Удалить существо """
        self.conn.send(b"mob.remove", mob_id)

    def setInvulnerable(self, mob_id: int, invulnerable: bool) -> None:
        """
        Устанавливает, является ли сущность неуязвимой или нет.
        Когда сущность неуязвима, нанести ей урон могут только игроки в творческом режиме.
        """
        self.conn.send(b"mob.setInvul", mob_id, invulnerable)

    def setCollidable(self, mob_id: int, collidable: bool):
        """ Установка коллизии существа. """
        self.conn.send(b"mob.setCollidable", mob_id, collidable)

    def setGravity(self, mob_id: int, gravity: bool) -> None:
        """ Устанавливает, применяется ли гравитация к данному объекту. """
        self.conn.send(b"mob.setGravity", mob_id, gravity)

    def setInvisible(self, mob_id: int, invisible: bool) -> None:
        """ Устанавливает невидимость. """
        self.conn.send(b"mob.setInvisible", mob_id, invisible)

    def setAI(self, mob_id, ai):
        self.conn.send(b"mob.setAi", mob_id, ai)

    def setName(self, mob_id: int, name: str) -> None:
        """ Устанавливает имя существа """
        self.conn.send(b"mob.setName", mob_id, name)

    def setPassenger(self, mob_id, entity_id) -> None:
        """
        Назначает пассажира текущему объекту.
        :param mob_id: id-существа
        :param entity_id: id-существа или игрока как пассажира
        """
        self.conn.send(b"mob.setPassenger", mob_id, entity_id)

    def setAttribute(self, mob_id: int, attribute: str, amount: int) -> None:
        """
        Добавить атрибут существу
        :param mob_id: id-существа
        :param attribute: Attribute.
        :param amount: величина атрибута
        """
        self.conn.send(b"mob.setAttribute", mob_id, attribute, amount)

    def setHealth(self, mob_id: int, amount: float) -> None:
        """
        Установить уровень здоровья существа
        :param amount: 0, 0.1 ... 20.0
        """
        self.conn.send(b"mob.setHealth", mob_id, amount)

    def getHealth(self, mob_id: int) -> float:
        """ :return возвращает текущее здоровье сущеста """
        return float(self.conn.sendReceive(b"mob.getHealth", mob_id))

    def setFireTicks(self, mob_id: int, amount: int) -> None:
        """ Установить текущие такты возгорания существа """
        self.conn.send(b"mob.setFireTicks", mob_id, amount)

    def playEffect(self, mob_id: int, entityEffect: str) -> None:
        """ Воспроизвести эффект существа """
        self.conn.send(b"mob.playEffect", mob_id, entityEffect)

    def getLastDamage(self, mob_id: int) -> float:
        """ :return Возвращает последний полученный урон """
        return float(self.conn.sendReceive(b"mob.getLastDamage", mob_id))

    def setEquipment(self, mob_id: int, equipment_slot: str, material: str) -> None:
        """
        Добавить экипировку существу
        :param mob_id: id-существа
        :param equipmentSlot: .EquipmentSlot
        :param material: .Material
        """
        self.conn.send(b"mob.setEquipment", mob_id, equipment_slot, material)

    def getEquipment(self, mob_id: int):
        return self.conn.sendReceive(b"mob.getEquipment", mob_id)

    def getKillerName(self, mob_id):
        return self.conn.sendReceive(b"mob.getKillerName", mob_id)

    def attackTarget(self, mob_id: int, target_id: int) -> None:
        self.conn.send(b"mob.attackTarget", mob_id, target_id)

    def addPotionEffect(self, entityId: int, potionEffectType: str, duration: int, amplifier: int, ambient: bool = True, particles: bool = True, icon: bool = True) -> None:
        """
        Применяет эффект зелья к игроку
        :param entityId: id-существа
        :param potionEffectType: тип эффекта PotionEffectType.
        :param duration: продолжительность сек.
        :param amplifier: уровень эффекта
        :param ambient: звук True/False
        :param particles: чатицы True/False
        :param icon: иконца True/False
        """
        self.conn.send(b"mob.addPotionEffect", entityId, potionEffectType.upper(), duration * 20, amplifier, ambient, particles, icon)





class CmdPlayer(CmdPositioner):
    """Методы для хоста-игрока"""
    def __init__(self, connection, playerId):
        CmdPositioner.__init__(self, connection, b"player")
        self.conn = connection
        self.playerId = playerId

    def addPotionEffect(self, potionEffectType: str, duration: int, amplifier: int, ambient: bool = True, particles: bool = True, icon: bool = True) -> None:
        """
        Применяет эффект зелья к игроку
        :param potionEffectType: тип эффекта PotionEffectType.
        :param duration: продолжительность сек.
        :param amplifier: уровень эффекта
        :param ambient: звук True/False
        :param particles: чатицы True/False
        :param icon: иконца True/False
        """
        self.conn.send(self.pkg + b".addPotionEffect", potionEffectType.upper(), duration * 20, amplifier, ambient, particles, icon)

    def removePotionEffects(self):
        """ Снимает все эффекты зелий с игрока """
        self.conn.send(self.pkg + b".removePotionEffects")

    def book(self):
        self.conn.send(self.pkg + b".book")

    def hasPotionEffect(self, potionEffectType: str) -> bool:
        """
        Возвращает True, если существо имеет примененный эффект зелья
        :param entityId: id-существа
        :param potionEffectType: тип эффектс PotionEffectType.
        :return: bool
        """
        result = self.conn.sendReceive(self.pkg + b".hasPotionEffect", self.playerId, potionEffectType)
        return eval(result[0].upper() + result[1:])


    def setPlayerListHeaderFooter(self, header: str, footer: str) -> None:
        self.conn.send(self.pkg + b".setPlayerListHeaderFooter", header, footer)

    def getPos(self) -> Vec3:
        return CmdPositioner.getPos(self, self.playerId)

    def setPos(self, x: float, y: float, z: float) -> None:
        """Установка позиции игрока"""
        return CmdPositioner.setPos(self, self.playerId, x, y, z)

    def getTilePos(self) -> Vec3:
        return CmdPositioner.getTilePos(self, self.playerId)

    def setTilePos(self, x: int, y: int, z: int) -> None:
        return CmdPositioner.setTilePos(self, self.playerId, x, y, z)

    def getDirection(self) -> Vec3:
        return CmdPositioner.getDirection(self, self.playerId)

    def setDirection(self, x: float, y: float, z: float) -> None:
        return CmdPositioner.setDirection(self, self.playerId, x, y, z)

    def getRotation(self) -> float:
        return CmdPositioner.getRotation(self, self.playerId)

    def setRotation(self, yaw) -> None:
        return CmdPositioner.setRotation(self, self.playerId, yaw)

    def getPitch(self) -> float:
        return CmdPositioner.getPitch(self, self.playerId)

    def setPitch(self, pitch) -> None:
        return CmdPositioner.setPitch(self, self.playerId, pitch)

    def getFoodLevel(self) -> int:
        """ :return Получает уровень пищи игрока """
        return int(self.conn.sendReceive(self.pkg + b".getFoodLevel", self.playerId))

    def setFoodLevel(self, foodLevel: int) -> None:
        """ Устанавливает уровень пищи игрока """
        self.conn.send(self.pkg + b".setFoodLevel", foodLevel)

    def getFirstPlayed(self) -> str:
        """Возвращает дату и время первого посещения сервера игроком %H:%M %d:%m:%Y"""
        return self.conn.sendReceive(self.pkg + b".getFirstPlayed", self.playerId)

    def getItemOnCursor(self):
        return self.conn.sendReceive(self.pkg + b".getItemOnCursor", self.playerId)

    def getName(self) -> str:
        return self.conn.sendReceive(self.pkg + b".getName", self.playerId)

    def getHealth(self) -> float:
        """ :return Возвращает значение здоровья объекта."""
        return float(self.conn.sendReceive(self.pkg + b".getHealth", self.playerId))

    def getPing(self) -> float:
        """:return Возвращает расчетный пинг игрока в миллисекундах."""
        return float(self.conn.sendReceive(self.pkg + b".getPing", self.playerId))

    def getExp(self) -> float:
        """:return Возвращает текущие очки опыта игрока для перехода на следующий уровень."""
        return float(self.conn.sendReceive(self.pkg + b".getExp", self.playerId))

    def getTotalExp(self) -> int:
        """:return  Возвращает общее количество очков опыта игроков."""
        return int(self.conn.sendReceive(self.pkg + b".getTotalExp", self.playerId))

    def getLevel(self):
        """:return Возвращает текущий уровень опыта игроков."""
        return int(self.conn.sendReceive(self.pkg + b".getLevel", self.playerId))

    def getWalkSpeed(self) -> float:
        """:return Возвращает скорость бега."""
        return float(self.conn.sendReceive(self.pkg + b".getWalkSpeed", self.playerId))

    # def getPlayerTime(self):
    #     """:return Возвращает текущую временную метку игрока."""
    #     return (self.conn.sendReceive(self.pkg + b".getPlayerTime", self.playerId))
    #
    # def getPlayerTimeOffset(self):
    #     """:return Возвращает текущую временную метку игрока."""
    #     return (self.conn.sendReceive(self.pkg + b".getPlayerTimeOffset", self.playerId))

    def getAddress(self) -> str:
        """:return Возвращает адрес пользователя."""
        return self.conn.sendReceive(self.pkg + b".getAddress")

    def getGamemode(self) -> str:
        """ :return: CREATIVE SURVIVAL HARDCORE SPECTATOR ADVENTURE """
        return self.conn.sendReceive(self.pkg + b".getGamemode")

    def getHealthScale(self) -> float:
        """ :return: Получает число, до которого масштабируется здоровье существа. """
        return float(self.conn.sendReceive(self.pkg + b".getHealthScale"))

    def getFlySpeed(self) -> float:
        """ :return: Возвращает скорость полета. """
        return float(self.conn.sendReceive(self.pkg + b".getFlySpeed"))

    def setGravity(self, gravity: bool):
        self.conn.send(self.pkg + b".setGravity", gravity)

    def setViewDistance(self, distance: int):
        self.conn.send(self.pkg + b".setViewDistance", distance)

    def setStatistic(self, *args) -> None:
        """
        Устанавливает значение указанной статистики игрока
        :param args: statistic, amount
        :param args: statistic, entity, amount
        :param args: statistic, material, amount
        """
        self.conn.send(self.pkg + b".setStatistic", args)

    def getStatistic(self, *args) -> int:
        """
        Возвращает значение статистики игрока
        :param args: statistic
        :param args: statistic, entity
        :param args: statistic, material
        """
        return int(self.conn.sendReceive(self.pkg + b".getStatistic", args))

    def getAllStatistics(self) -> dict:
        """ Возвращает словарь полной статистики игрока -> {Statistic:amount}"""
        statistic = self.conn.sendReceive(self.pkg + b".getAllStatistics")
        statistic_dict = statistic.split("|")
        statistic_dict.pop()
        return dict([[s.split(":")[0], int(s.split(":")[1])] for s in statistic_dict])

    def giveExp(self, exp: int) -> None:
        """
        Дает игроку указанное количество опыта.
        :param exp: количество опыта.
        """
        self.conn.send(self.pkg + b".giveExp", exp)

    def giveExpLevels(self, exp: int) -> None:
        """
        Дает игроку указанное количество уровней опыта.
        :param exp: количество опыта.
        """
        self.conn.send(self.pkg + b".giveExpLevels", exp)

    def isFlying(self) -> bool:
        """ :return Проверяет, летает ли этот игрок в данный момент или нет. """
        result = (self.conn.sendReceive(self.pkg + b".isFlying"))
        return eval(result[0].upper() + result[1:])

    def isHealthScaled(self) -> bool:
        """ :return Получает значение, если клиенту отображается «масштабированное» состояние здоровья,
         то есть состояние здоровья по шкале от 0 до getHealthScale(). """
        result = (self.conn.sendReceive(self.pkg + b".isHealthScaled"))
        return eval(result[0].upper() + result[1:])

    def isSneaking(self) -> bool:
        """ :return Возвращает, если игрок находится в режиме подкрадывания. """
        result = (self.conn.sendReceive(self.pkg + b".isSneaking"))
        return eval(result[0].upper() + result[1:])

    def isSprinting(self):
        """ :return Получает информацию о том, бежит игрок или нет. """
        result = (self.conn.sendReceive(self.pkg + b".isSprinting"))
        return eval(result[0].upper() + result[1:])

    def isCollidable(self) -> bool:
        """ :return Возвращает True, если этот объект подвержен коллизиям с другими объектами. """
        result = (self.conn.sendReceive(self.pkg + b".isCollidable"))
        return eval(result[0].upper() + result[1:])

    def isOnline(self) -> bool:
        """ :return Проверяет, находится ли этот игрок в данный момент онлайн. """
        result = (self.conn.sendReceive(self.pkg + b".isOnline"))
        return eval(result[0].upper() + result[1:])


    def isOnGround(self) -> bool:
        """ :return Возвращает true, если сущность поддерживается блоком """
        result = (self.conn.sendReceive(self.pkg + b".isOnGround"))
        return eval(result[0].upper() + result[1:])

    def isOp(self) -> bool:
        """ :return Проверяет, является ли этот объект оператором сервера. """
        result = (self.conn.sendReceive(self.pkg + b".isOp"))
        return eval(result[0].upper() + result[1:])


    def isDead(self) -> bool:
        """ :return Возвращает true, если эта сущность мертва. """
        result = (self.conn.sendReceive(self.pkg + b".isDead"))
        return eval(result[0].upper() + result[1:])

    def isInvulnerable(self) -> bool:
        """ :return Получает информацию о том, является ли объект неуязвимым или нет. """
        result = (self.conn.sendReceive(self.pkg + b".isInvulnerable"))
        return eval(result[0].upper() + result[1:])

    def setGamemode(self, gameMode: str) -> None:
        """
        Установить игровой режим для объекта.
        :param entityId: playerId -> mc.getPlayerEntityId("PLAYER_NAME")
        :param gameMode: CREATIVE SURVIVAL HARDCORE SPECTATOR ADVENTURE
        """
        self.conn.send(self.pkg + b".setGamemode", self.playerId, gameMode)

    def setAttribute(self, attribute, amount):
        """
        Устанавливает игроку указанный атрибут
        :param attribute: Attribute.
        :param amount: величина
        """
        self.conn.send(self.pkg + b".setAttribute", self.playerId, attribute, amount)

    def getAttributeValue(self, attribute):
        """
        Возвращает значение указанного атрибута
        :param entityId: id-существа
        :param attribute: Attribute.
        """
        return float(self.conn.sendReceive(self.pkg + b".getAttributeValue", self.playerId, attribute))

    def setHealth(self, health: float) -> None:
        """
        Установить текущее здоровье существа.
        :param entityId: playerId -> mc.getPlayerEntityId("PLAYER_NAME")
        :param health: 0, 1 ... 20
        """
        self.conn.send(self.pkg + b".setHealth", self.playerId, health)

    def setExp(self, exp: float) -> None:
        """
        Установить значение опыта.
        :param entityId: playerId -> mc.getPlayerEntityId("PLAYER_NAME")
        :param exp: 0, 0.1 ... 1
        """
        self.conn.send(self.pkg + b".setExp", self.playerId, exp)

    def setAllowFlight(self, flight: bool) -> None:
        """ Устанавливает, разрешено ли игроку летать с помощью двойного нажатия клавиши прыжка,
         как в творческом режиме. """
        self.conn.send(self.pkg + b".setAllowFlight", self.playerId, flight)

    def setFlySpeed(self, flySpeed: float) -> None:
        """
        Устанавливает скорость полета игрока.
        defalut: 0.1
        :param flySpeed: 0, 0.1 ... 1
        """
        self.conn.send(self.pkg + b".setFlySpeed", self.playerId, flySpeed)

    def setLevel(self, level: int) -> None:
        """ Устанавливает уровень игрока. """
        self.conn.send(self.pkg + b".setLevel", self.playerId, level)

    def setTotalExperience(self, experience: int) -> None:
        """
        Устанавливает текущие очки опыта игрока.
        Это относится к общему количеству опыта, который игрок накопил с течением времени
        и в настоящее время не отображается клиенту.
        """
        self.conn.send(self.pkg + b".setTotalExperience", self.playerId, experience)

    def setWalkSpeed(self, walkspeed: float) -> None:
        """
        Устанавливает скорость бега игрока.
        default walkspeed: 0.2
        :param walkspeed: 0, 0.1 ... 1
        """
        self.conn.send(self.pkg + b".setWalkSpeed", self.playerId, walkspeed)

    def setInvulnerable(self, invulnerable: bool) -> None:
        """ Устанавливает неуязвимость. """
        self.conn.send(self.pkg + b".setInvulnerable", self.playerId, invulnerable)

    def setOp(self, op: bool) -> None:
        """ Устанавливает статус оператора этого объекта. """
        self.conn.send(self.pkg + b".setOp", self.playerId, op)


    def spawnParticle(self, particleName: str, amount: int):
        """
        Создает частицу (количество раз, указанное в счетчике) в целевом месте.
        Particle.
        :param particleName: CLOUD DAMAGE_INDICATOR GLOW HEART ...
        :param amount: 0, 1 ...
        """
        self.conn.send(self.pkg + b".spawnParticle", self.playerId, particleName, amount)

    def setItemInMainHand(self, *args) -> None:
        """
        Устанавливает предмет в основной руке игрока
        :param args: ItemStack
        :param args: Material, количество
        """
        if len(args) == 1:
            self.conn.send(self.pkg + b".setItemInMainHand", self.playerId, args[0].name)
        else:
            self.conn.send(self.pkg + b".setItemInMainHand", self.playerId, args[0], args[1])

    def getItemInMainHand(self) -> str:
        """ :return: вощвращает предмет в основной руке. """
        material = self.conn.sendReceive(self.pkg + b".getItemInMainHand", self.playerId)
        if material == "":
            return None
        else:
            return self.conn.sendReceive(self.pkg + b".getItemInMainHand", self.playerId)

    def getItemInOffHand(self) -> str:
        """ :return: вощвращает предмет во второстепенной руке. """
        material = self.conn.sendReceive(self.pkg + b".getItemInOffHand", self.playerId)
        if material == "":
            return None
        else:
            return self.conn.sendReceive(self.pkg + b".getItemInOffHand", self.playerId)

    def setItemInOffHand(self, *args) -> None:
        """
        Устанавливает предмет во второстепенной руке игрока
        :param args: ItemStack
        :param args: Material, количество
        """
        if len(args) == 1:
            self.conn.send(self.pkg + b".setItemInOffHand", self.playerId, args[0].name)
        else:
            self.conn.send(self.pkg + b".setItemInOffHand", self.playerId, args)

    def getHelmet(self):
        material = self.conn.sendReceive(self.pkg + b".getHelmet", self.playerId)
        if material == "":
            return None
        else:
            return self.conn.sendReceive(self.pkg + b".getHelmet", self.playerId)

    def getChestplate(self):
        material = self.conn.sendReceive(self.pkg + b".getChestplate", self.playerId)
        if material == "":
            return None
        else:
            return self.conn.sendReceive(self.pkg + b".getChestplate", self.playerId)

    def getLeggings(self):
        material = self.conn.sendReceive(self.pkg + b".getLeggings", self.playerId)
        if material == "":
            return None
        else:
            return self.conn.sendReceive(self.pkg + b".getLeggings", self.playerId)

    def getBoots(self):
        material = self.conn.sendReceive(self.pkg + b".getBoots", self.playerId)
        if material == "":
            return None
        else:
            return self.conn.sendReceive(self.pkg + b".getBoots", self.playerId)


    def getInventoryContents(self):
        """
        Возвращает контент инвентаря игрока.
        :returns [[index, type, amount]]
        """
        s = self.conn.sendReceive(self.pkg + b".getInventory", self.playerId)

        inventory = [i for i in s.split("|") if i]

        # inv = []
        # for i in inventory:
        #     i = i.split(",")
        #     print(i)
        #     for n in i:
        #         print(n)
            #inv.append(i.split(","))
        #inv = []
        #print(inv)
        #print(inventory)
        # s = s.split("|")

                #inv.append(a.split(","))
        #print(inv)
        return [[int(n.split(",")[0]), n.split(",")[1], int(n.split(",")[2])] for n in inventory if n.split(",")[1] != "None"]

    def getInventoryArmorContents(self):
        """
        Возвращает контент слоты брони игрока.
        :returns [[index, type, amount]]
        """
        s = self.conn.sendReceive(self.pkg + b".getArmorContents", self.playerId)
        inventory = [i for i in s.split("|") if i]
        return [[int(n.split(",")[0]), n.split(",")[1], int(n.split(",")[2])] for n in inventory]

    def addItem(self, item: str, amount: int = 1) -> None:
        """
        Добавляет предмент игроку в инвентарь.
        :param material: DIAMOND_AXE IRON_SWORD DIRT COBBLESTONE
        :param amount: 0, 1 ... stackSize
        """
        self.conn.send(self.pkg + b".addItem", self.playerId, item, amount)

    def setItem(self, index: int, material: str, amount: int):
        """
        Устанавливает предмет в ячейке инвентаря
        :param index: номер ячейки
        :param material: материал
        :param amount: количество
        """
        self.conn.send(self.pkg + b".setItem", self.playerId, index, material, amount)

    def addItemStack(self, itemStack):
        """
        Добавляет ItemStack игроку в инвентарь.
        :param itemStack: ItemStack object
        """
        if not isinstance(itemStack, ItemStack):
            logging.warning("itemStack не является объектом класса ItemStack")
        else:
            self.conn.send(self.pkg + b".addItemStack", self.playerId, itemStack.name)


    def setItemStack(self, index, itemStack):
        self.conn.send(self.pkg + b".setItemStack", self.playerId, index, itemStack.name)

    def clearInventory(self):
        """ Очищает инвентарь игрока. """
        self.conn.send(self.pkg + b".clearInventory", self.playerId)

    def getItemAmount(self, index: int) -> int:
        """
        Возвращает количество предментов в ячейке инвентаря
        :param index: ячейка инвентаря
        """
        amount = int(self.conn.sendReceive(self.pkg + b".getItemAmount", index))
        return amount if amount != "0" else None

    def getItemType(self, index: int) -> str:
        """
        Возвращает тип предмета в ячейке инвентаря
        :param index: ячейка инвентаря
        """
        item = self.conn.sendReceive(self.pkg + b".getItemType", index)
        return item if item != "0" else None

    def removeItem(self, index: int):
        """ Удаляет предмет из инвентаря по индексу. """
        self.conn.send(self.pkg + b".removeItem", self.playerId, index)

    def containsItem(self, material: str) -> bool:
        """ Проверяет наличие предмета в инвентаре игрока. """
        result = self.conn.sendReceive(self.pkg + b".containsItem", self.playerId, material)
        return eval(result[0].upper() + result[1:])

    def containsItemStack(self, itemStack) -> bool:
        """ Проверяет наличие ItemStack в инвентаре игрока. """
        result = self.conn.sendReceive(self.pkg + b".containsItemStack", itemStack.name)
        return eval(result[0].upper() + result[1:])

    def findItemStack(self, itemStack):
        """
        Поиск предмета ItemStack в инвентаре
        :param playerId: id-игрока
        :param itemStack: объект ItemStack
        :return: индекс ячейки предмета, -1 в случае отсутствия
        """
        try:
            return int(self.conn.sendReceive(self.pkg + b".findItemStack", self.playerId, itemStack.name))
        except:
            return -1

    def playEffect(self, effectName: str, data: int = 1):
        """
        Воспроизводит эффект в координатах игрока
        :param effectName: END_GATEWAY_SPAWN ENDER_SIGNAL POTION_BREAK ...
        :param data: 1-10
        """
        self.conn.send(self.pkg + b".playEffect", self.playerId, effectName, data)

    def playNote(self, instrument: str, octave: int, note: str):
        """
        Воспроизводит ноту заданного инструмента у игрока.
        :param instrument: BANJO BASS_DRUM BASS_GUITAR ...
        :param octave: 0 1
        :param note: A B C D E F G
        """
        self.conn.send(self.pkg + b".playNote", self.playerId, instrument, octave, note)

    def playSound(self, sound: str, volume: float = 1, pitch: float = 1):
        """
        Воспроизводит звук у игрока.
        :param sound: Sound.НАЗВАНИЕ_ЗВУКА
        :param volume: 0, 0.1 ... 1
        :param pitch: 0, 0.1 ... 3
        :return:
        """
        self.conn.send(self.pkg + b".playSound", self.playerId, sound, volume, pitch)

    def stopAllSound(self):
        """ Останавливает все звуки у игрока. """
        self.conn.send(self.pkg + b".stopAllSounds", self.playerId)

    def sendTitle(self, title: str, subTitle: str = "", fadeIn: int = 10, stay: int = 70, fadeOut: int = 20) -> None:
        """ Отправляет игроку заголовок с субтитрами. """
        self.conn.send(self.pkg + b".sendTitle", title, subTitle, fadeIn, stay, fadeOut)

    def getTargetBlock(self, distance: int):
        result = self.conn.sendReceive(self.pkg + b".getTargetBlock", self.playerId, distance).split("|")

        return Block(result[0], float(result[1]), float(result[2]), float(result[3]))

    def giveRod(self):
        rod = ItemStack("Зачарованная удочка", Material.FISHING_ROD, 1)
        rod.addEnchant(Enchantment.LURE, 3)
        self.setItemInMainHand(rod)


class CmdPlayerEntity(CmdPlayer):
    def __init__(self, connection, playerId):
        CmdPositioner.__init__(self, connection, b"entity")
        self.conn = connection
        self.playerId = playerId

    def getPos(self):
        return CmdPositioner.getPos(self, self.playerId)




class CmdEvents:
    """Events"""

    def __init__(self, connection):
        self.conn = connection

    def clearAll(self):
        """Clear all old events"""
        self.conn.send(b"events.clear")

    def pollBlockHits(self):
        """Only triggered by sword => [BlockEvent]"""
        s = self.conn.sendReceive(b"events.block.hits")
        events = [e for e in s.split("|") if e]
        events = [e for e in s.split(",") if e]
        if events:
            return BlockEvent(int(events[0]), events[1], int(events[2]), int(events[3]), int(events[4]), int(events[5]))
        #return [BlockEvent(*list(map(int, e.split(",")))) for e in events]

    # def pollArrowHits(self):
    #     """Only triggered by sword => [BlockEvent]"""
    #     s = self.conn.sendReceive(b"events.arrow.hits")
    #     events = [e for e in s.split("|") if e]
    #     return [ArrowHitEvent.Hit(*list(map(int, e.split(",")))) for e in events]

    def pollArrowHits(self):
        s = self.conn.sendReceive(b"events.arrow.hits")
        events = [e for e in s.split("|") if e]
        events = [e for e in s.split(",") if e]
        if events:
            return ArrowHitEvent(entityId=int(events[3]), x=int(events[0]), y=int(events[1]), z=int(events[2]))

    def entityPickupItem(self):
        s = self.conn.sendReceive(b"events.entityPickupItem")
        if s:
            e = s.split("|")[0].split(",")
            return EntityPickupItemEvent(entityId=int(e[0]), entityName=e[1], material=e[2], amount=int(e[3]))

    def entityPickupItemById(self, entityId):
        s = self.conn.sendReceive(b"events.entityPickupItemById", entityId)
        if s:
            e = s.split("|")[0].split(",")
            return EntityPickupItemEvent(entityId=int(e[0]), entityName=e[1], material=e[2], amount=int(e[3]))

    def playerFishEvent(self):
        s = self.conn.sendReceive(b"events.playerFish")
        if s:
            e = s.split("|")[0].split(",")
            _caught = None if e[3] == "AIR" else e[2]
            return PlayerFishEvent(playerId=int(e[0]), entityName=e[1], state=e[2], caught=_caught)

    def playerHarvestBlockEvent(self):
        s = self.conn.sendReceive(b"events.playerHarvestBlockEvent")
        if s:
            e = s.split("|")[0].split(",")
            return PlayerHarvestBlockEvent(playerId=int(e[0]), name=e[1], material=e[2], x=int(e[3]), y=int(e[4]), z=int(e[5]))

    def pollChatPosts(self):
        """Triggered by posts to chat => [ChatEvent]"""
        s = self.conn.sendReceive(b"events.chat.posts")
        events = [e for e in s.split("|") if e]
        return [ChatEvent.Post(int(e[:e.find(",")]), e[e.find(",") + 1:]) for e in events]

    def playerInteractEntity(self) -> InteractEntityEvent:
        """
        Событие нажатия ПКМ игрока по любому существу
        """
        events = self.conn.sendReceive(b"events.playerInteractEntity")
        if len(events) > 0:
            events = events.split("|")[0].split(",")
            return InteractEntityEvent(playerId=int(events[0]), playerName=events[1], entityId=int(events[2]), entityType=events[3], x=int(events[4]), y=int(events[5]), z=int(events[6]))
            #return {"player_id": int(events[0]), "player_name": events[1], "entity_id": int(events[2]), "position": (int(events[3]), int(events[4]), int(events[5]))}


    def playerInteractEntityById(self, entityId) -> dict:
        """
        Событие нажатия ПКМ игрока по конкретному существу
        :param entityId: id существа
        :return: dict{player_id, player_name, entity_id, position}
        """
        events = self.conn.sendReceive(b"events.playerInteractEntityById", entityId)
        if len(events) > 0:
            events = events.split("|")[0].split(",")
            return {"player_id": int(events[0]), "player_name": events[1], "entity_id": int(events[2]), "position": (int(events[3]), int(events[4]), int(events[5]))}

    def blockBreak(self):
        s = self.conn.sendReceive(b"events.blockBreak")
        events = [e for e in s.split(",") if e]
        if events:
            return BlockBreakEvent(events[0], int(events[1]), events[2], int(events[3]), int(events[4]), int(events[5]))
            #return {"player_id": int(events[0]), "player_name": events[1], "x": int(events[2]), "y": (int(events[3])), "z": (int(events[4]))}
        #return BlockBreakEvent.Hit(int(events[0]), event[1], int(events[2]), int(events[3]), int(events[4]))
    def entityDamage(self):
        s = self.conn.sendReceive(b"events.entityDamage")
        if s:
            e = s.split("|")[0].split(",")
            return EntityDamageEvent(int(e[0]), e[1], e[2], float(e[3]), float(e[4]), float(e[5]), float(e[6]))

    def entitySpawn(self):
        s = self.conn.sendReceive(b"events.entitySpawn")
        if s:
            e = s.split("|")[0].split(",")
            return EntitySpawnEvent(int(e[0]), e[1], float(e[2]), float(e[3]), float(e[4]))

    def entityDeath(self):
        e = self.conn.sendReceive(b"events.EntityDeath")
        if len(e) > 0:
            e = e.split("|")[0].split(",")
            return EntityDeathEvent(killerId=int(e[0]), killerName=e[1], entityId=int(e[2]), entityType=e[3], x=float(e[4]), y=float(e[5]), z=float(e[6]))


class Inventory():
    title = ""
    def __init__(self, size, title):
        """
        :param size: размер инвентаря 9, 18, 27, 36, 46, 54
        :param title: название инвентаря
        """
        self.size = size
        self.title = title
        CmdPositioner.__init__(self, self.conn, b"customInventory")
        if size in [9, 18, 27, 36, 46, 54]:
            self.conn.send(self.pkg + b".createInv", self.size, self.title)
        else:
            logging.warning(f"Неверное значение размера, size должен быть в пределах [9, 18, 27, 36, 46, 54]")

    def addItemStack(self, itemStack):
        """
        Добавляет ItemStack в инвентарь Inventory.
        :param itemStack: ItemStack object
        """
        self.conn.send(self.pkg + b".addItemStack", self.title, itemStack.name)

    def setItemStack(self, index, itemStack):
        """ Устанавливает ItemStack по индексу ячейки инвентаря """
        self.conn.send(self.pkg + b".setItemStack", self.title, index, itemStack.name)

    def open(self, playerId):
        """ Открывает инвентарь у игрока PlayerId """
        self.conn.send(self.pkg + b".open", playerId, self.title)

    def addItem(self, material, amount):
        """ Добавляет предмет в инвентарь """
        self.conn.send(self.pkg + b".addItem", material, amount, self.title)

    def setItem(self, material, amount, index):
        """ Устанавливает предмет по индексу ячейки инвентаря """
        self.conn.send(self.pkg + b".setItem", index, material, amount, self.title)

    def clear(self):
        """ Очищает инвентарь """
        self.conn.send(self.pkg + b".clear", self.title)

    def remove(self, index):
        """ Удаляет предмет по индексу ячейки инвентаря """
        self.conn.send(self.pkg + b".remove", self.title, index)

    def getContents(self):
        """ :return Возвращает контент инвентаря """
        inventory = self.conn.sendReceive(self.pkg + b".getContents", self.title)
        inventory = [i for i in inventory.split("|") if i]
        return [[int(n.split(",")[0]), n.split(",")[1], int(n.split(",")[2])] for n in inventory]

    def getSize(self):
        """ :return Возвращает размер инвентаря """
        return self.conn.sendReceive(self.pkg + b".getSize", self.title)


class BossBar():
    def __init__(self, title, color, barStyle, barFlag):
        """
        Инициализация босс-бара (полоса босса)
        :param title: заголовок
        :param color: цвет текста Color.
        :param barStyle: стиль полосы .BarStyle
        :param barFlag: флаг полосы .BarFlag
        """
        self.title = title
        self.color = color
        self.barStyle = barStyle
        self.barFlag = barFlag
        CmdPositioner.__init__(self, self.conn, b"world")
        self.conn.send(self.pkg + b".createBossBar", self.title, self.color, self.barStyle, self.barFlag)

    def getPlayers(self):
        """
        :return: возвращает всех игроков с активным босс-баром.
        """
        return self.conn.sendReceive(self.pkg + b".bossBarGetPlayers", self.title)

    def setProgress(self, progress):
        """
        :param progress: устанавливает значение прогресса 0, 0.1 ... 1
        """
        self.conn.send(self.pkg + b".setProgress", self.title, progress)

    def getProgress(self) -> float:
        """
        :return: возвращает текущий прогресс.
        """
        return float(self.conn.sendReceive(self.pkg + b".getProgress", self.title))

    def setVisible(self, visible: bool):
        """
        :param visible: устанавливает прозрачность.
        """
        self.visible = visible
        self.conn.send(self.pkg + b".removeAll", self.title, visible)

    def removeAll(self):
        """
        Удаляет прогресс-бар (необходимо перезайти для обновления GUI).
        """
        self.conn.send(self.pkg + b".removeAll", self.title)

    def removePlayer(self, playerId):
        """
        Удаляет игрока из босс-бара.
        :param playerId: id-игрока.
        """
        self.conn.send(self.pkg + b".removePlayer", self.title, playerId)

    def addPlayer(self, playerId):
        """
        Добавляет игрока в босс-бар.
        :param playerId: id-игрока.
        """
        self.conn.send(self.pkg + b".addPlayer", self.title, playerId)


class Scoreboard():
    def __init__(self, name):
        """
        Инициализация табло.
        :param name: название.
        """
        self.name = name
        CmdPositioner.__init__(self, self.conn, b"world")
        self.conn.send(self.pkg + b".scoreBoard", self.name)

    def setScoreboard(self, playerId):
        """
        Устанавливает табло для игрока.
        :param playerId: id-игрока.
        """
        self.conn.send(self.pkg + b".setScoreboard", self.name, playerId)

    def removeScoreboard(self, playerId):
        """
        Удаляет игрока из табло.
        :param playerId: id-игрока.
        """
        self.conn.send(self.pkg + b".removeScoreboard", playerId)

    def getObjective(self):
        """
        :return: возвращает объект задачи.
        """
        return self.conn.sendReceive(self.pkg + b".getObjective", self.name)

    def registerNewObjective(self, criteria):
        """
        Регистрация новой задачи
        :param criteria: критерий задачи .Criteria
        :return: возвращает объект задачи Objective
        """
        objective = Objective(self.name, criteria, self.conn, self.pkg)
        self.conn.send(self.pkg + b".registerNewObjective", self.name, criteria)
        return objective

class Objective(Scoreboard):
    def __init__(self, name, criteria, conn, pkg):
        self.name = name
        self.criteria = criteria
        self.pkg = pkg
        self.conn = conn

    def setDisplaySlot(self, display_slot):
        """
        Установить отображаемый слот для задачи
        :param display_slot: слот .DisplaySlot
        """
        self.display_slot = display_slot
        self.conn.send(self.pkg + b".setDisplaySlot", self.name, display_slot)

    def getDisplaySlot(self):
        """
        :return: возвращает отображаемый слот
        """
        return self.conn.sendReceive(self.pkg + b".getDisplaySlot", self.name)

    def setDisplayName(self, display_name):
        """
        Установить отображаемое имя задачи
        :param display_name: имя задачи
        """
        self.displayName = display_name
        self.conn.send(self.pkg + b".setDisplayName", self.name, display_name)

    def getDisplayName(self):
        """
        :return: возвращает отображаемое имя задачи
        """
        return self.conn.sendReceive(self.pkg + b".getDisplayName", self.name)

    def getScore(self, entry):
        """
        Инициализирует оценку записи для цели на этом табло
        :param entry: Заголовок оценки записи
        :return: возвращает объект оценки записи Score
        """
        score = Score(self.name, entry, self.criteria, self.conn, self.pkg)
        self.conn.send(self.pkg + b".getScore", self.name, entry)
        return score


class Score(Objective):
    def __init__(self, name, entry, criteria, conn, pkg):
        self.name = name
        self.entry = entry
        self.criteria = criteria
        self.conn = conn
        self.pkg = pkg

    def getScorePoints(self) -> int:
        """
        :return: возвращает текущие очки
        """
        return int(self.conn.sendReceive(self.pkg + b".getScorePoints", self.name, self.entry))

    def resetScore(self):
        """
        Сбросить текущие очки
        """
        self.conn.send(self.pkg + b".resetScore", self.name, self.entry)

    def getEntry(self):
        """
        :return: возвращает заголовок оценки записи
        """
        self.conn.send(self.pkg + b".getEntry", self.name, self.entry)

    def setScorePoints(self, score: int):
        """
        Установить очки
        :param score: очки
        """
        self.score = score
        self.conn.send(self.pkg + b".setScore", self.name, self.entry, score)


class Merchant:
    def __init__(self, title: str):
        """
        Инициализация торговца
        :param title: заголовок
        """
        self.title = title
        CmdPositioner.__init__(self, self.conn, b"world")

        self.conn.send(b"world.createMerchant", self.title)

    def setRecipes(self, merchantRecipe) -> None:
        """
        Установка рецептов предложения обмена
        :param recipes: рецепты
        """
        if type(merchantRecipe) == list:
            items = ""
            for i in merchantRecipe:
                items += i.item + str(i.amount) + "|"
            self.conn.send(b"world.setRecipes", self.title, items)
        else:
            self.conn.send(b"world.setRecipes", self.title, merchantRecipe.item + str(merchantRecipe.amount))

    def openMerchant(self, playerId: int) -> None:
        """ Открыть у игрока """
        self.conn.send(b"world.openMerchant", self.title, playerId)

class Book():
    def __init__(self, title: str, author: str):
        self.title = title
        self.author = author
        CmdPositioner.__init__(self, self.conn, b"world")
        self.conn.send(b"world.createBook", self.title, self.author)

    def addPage(self, text: str):
        text = text.replace("\n", ";")
        self.conn.send(b"world.bookAddPage", self.title, text)

    # def append(self, page: int, text: str):
    #     self.conn.send(b"world.appendText", self.title, page, text)

    def giveTo(self, playerId: int):
        self.conn.send(b"world.giveBook", self.title, playerId)

class MerchantRecipe():
    def __init__(self, item: str, amount: int):
        """
        Инициализация рецепта предложения обмена
        :param item: предмет, который хотим получить при обмене
        :param amount: количество
        """
        CmdPositioner.__init__(self, self.conn, b"world")
        self.item = item
        self.amount = amount
        self.conn.send(b"world.createRecipe", item, amount)

    def addIngredient(self, item: str, amount: int) -> None:
        """
        Добавление
        :param item: предмет, которым мы платим при обмене
        :param amount: количество
        """
        self.conn.send(b"world.addIngredient", self.item, self.amount, item, amount)


class ItemStack:
    def __init__(self, name, material, amount):
        """
        Создание кастомного предмета
        :param name: название
        :param material: материал
        :param amount: количество
        """
        self.name = name
        self.material = material
        self.amount = amount
        CmdPositioner.__init__(self, self.conn, b"customItem")
        self.conn.send(self.pkg + b".createCustomItem", self.name, self.material, self.amount)

    def setLore(self, lore):
        if type(lore) is list:
            loreString = ""
            for lo in lore:
                loreString += lo + "|"
            self.conn.send(self.pkg + b".setLore", self.name, loreString)
        else:
            self.conn.send(self.pkg + b".setLore", self.name, lore)

    def setDisplayName(self, display_name: str):
        """ Устанавливает отображаемое название ItemStack. """
        self.conn.send(self.pkg + b".setDisplayName", self.name, display_name)

    def setRarity(self, itemRarity):
        """ Устанавливает цвет в названии предмета ItemRarity """
        self.conn.send(self.pkg + b".setRarity", self.name, itemRarity)

    def setUnbreakable(self, unbreak: bool):
        """ Устанавливает неразрушимый тег.  """
        self.conn.send(self.pkg + b".setUnbreakable", self.name, unbreak)

    def addAttribute(self, attribute: str, level):
        """ Добавляет атрибуты ItemStack """
        self.conn.send(self.pkg + b".addAttribute", attribute, level, self.name)

    def addEnchant(self, enchant: str, level: int):
        """ Добавляет зачарование ItemStack """
        self.conn.send(self.pkg + b".addEnchant", enchant, level, self.name)

    def getType(self):
        """ Получить тип ItemStack. """
        return self.conn.sendReceive(self.pkg + b".getType", self.name)

    def getAmount(self):
        """ Получить количество ItemStack. """
        return self.conn.sendReceive(self.pkg + b".getAmount", self.name)

    def getRarity(self):
        """ Получить редкость ItemStack. """
        return self.conn.sendReceive(self.pkg + b".getRarity", self.name)

    def getEnchantments(self):
        """ Получить зачарования """
        return self.conn.sendReceive(self.pkg + b".getEnchantments", self.name)

    def getAttributes(self):
        """ Получить информацию о атрибутах ItemStack """
        return self.conn.sendReceive(self.pkg + b".getAttributes", self.name)

    def getItem(self):
        """ Получить всю информацию о ItemStack """
        return self.conn.sendReceive(self.pkg + b".getItem", self.name)

    def getItemMeta(self):
        """ Получить метаданные о ItemStack """
        return self.conn.sendReceive(self.pkg + b".getItemMeta", self.name)

    def add(self, playerId: int) -> None:
        self.conn.send(self.pkg + b".add", playerId, self.name)


class Minecraft:
    def __init__(self, connection, playerId):
        self.conn = connection
        self.entity = CmdEntity(connection)
        self.mob = Mob(connection)
        self.cmdplayer = CmdPlayer(connection, playerId)
        self.player = CmdPlayer(connection, playerId)
        self.events = CmdEvents(connection)
        self.edu = Edu(connection)
        self.playerId = playerId
        self.settings = settings


    def setEntityName(self, entityId, name):
        self.conn.send(b"world.entitySetName", entityId, name)

    def getBlock(self, x: int, y: int, z: int) -> str:
        """Get block (x,y,z) => id:int"""
        return self.conn.sendReceive(b"world.getBlock", x, y, z)

    def getBlocks(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int) -> list:
        """Get a cuboid of blocks (x0,y0,z0,x1,y1,z1) => [id:int]"""
        blocks = self.conn.sendReceive(b"world.getBlocks", x1, y1, z1, x2, y2, z2)
        arr1d = blocks.split(',')

        xSize = abs(x1 - x2) + 1
        ySize = abs(y1 - y2) + 1
        zSize = abs(z1 - z2) + 1
        totalSize = xSize * ySize * zSize
        arr3d = []

        if len(arr1d) != totalSize:
            warn('Get number of blocks is incomplete')

        for i in range(0, totalSize, xSize * ySize):
            curArr = []
            for j in range(0, xSize * ySize, xSize):
                curArr.append(arr1d[i + j:i + j + xSize])
            arr3d.append(curArr)
        return arr3d

    def generateTree(self, x: int, y: int, z: int, treeType: str):
        self.conn.send(b"world.generateTree", x, y, z, treeType)

    def setJoinMessage(self, msg: str):
        self.conn.send(b"world.setJoinMessage", msg)
 
    def setBlock(self, x: int, y: int, z: int, block: str) -> None:
        """Установка блока в указанных координатах"""
        self.conn.send(b"world.setBlock", x, y, z, block.upper())

    def setBlocks(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, block: str) -> None:
        """Установка кубоида блоков (x1,y1,z1,x2,y2,z2,id,[data])"""
        self.conn.send(b"world.setBlocks", x1, y1, z1, x2, y2, z2, block.upper())

    def getHeight(self, x: int, z: int) -> int:
        """Возвращает y-координату самого высокого блока в x, z"""
        return int(self.conn.sendReceive(b"world.getHeight", x, z))

    def getTPS(self):
        return float(self.conn.sendReceive(b"world.getTps"))

    def getLoadedChunks(self):
        return int(self.conn.sendReceive(b"world.getLoadedChunks"))

    def getServerMaxMemory(self):
        return int(self.conn.sendReceive(b"world.getServerMaxMemory"))

    def getServerUsedMemory(self):
        return int(self.conn.sendReceive(b"world.getServerUsedMemory"))

    def getPlayerEntityIds(self) -> list:
        """Возвращает id игроков подключенных к серверу"""
        ids = self.conn.sendReceive(b"world.getPlayerIds")
        return list(map(int, ids.split("|")))

    def saveCheckpoint(self):
        """Save a checkpoint that can be used for restoring the world"""
        self.conn.send(b"world.checkpoint.save")

    def restoreCheckpoint(self):
        """Restore the world state to the checkpoint"""
        self.conn.send(b"world.checkpoint.restore")

    def postToChat(self, *msg) -> None:
        """Отправка сообщения в игровой чат"""
        self.conn.send(b"chat.post", msg)

    def setSign(self, x: int, y: int, z: int, signType: str, signDir: int, line1: str = "", line2: str = "",
                line3: str = "", line4: str = "") -> None:
        minecraftSignsType = ["SPRUCE_SIGN", "ACACIA_SIGN", "BIRCH_SIGN", "DARK_OAK_SIGN", "JUNGLE_SIGN", "OAK_SIGN"]

        # ["SPRUCE_WALL_SIGN","ACACIA_WALL_SIGN","BIRCH_WALL_SIGN","DARK_OAK_WALL_SIGN","JUNGLE_WALL_SIGN","OAK_WALL_SIGN"]
        minecraftSignsDir = {0: 'SOUTH',
                             1: 'SOUTH_SOUTH_WEST',
                             2: 'SOUTH_WEST',
                             3: 'WEST_SOUTH_WEST',
                             4: 'WEST',
                             5: 'WEST_NORTH_WEST',
                             6: 'NORTH_WEST',
                             7: 'NORTH_NORTH_WEST',
                             8: 'NORTH',
                             9: 'NORTH_NORTH_EAST',
                             10: 'NORTH_EAST',
                             11: 'EAST_NORTH_EAST',
                             12: 'EAST',
                             13: 'EAST_SOUTH_EAST',
                             14: 'SOUTH_EAST',
                             15: 'SOUTH_SOUTH_EAST'
                             }

        if type(signDir) == int:
            if 0 <= signDir < 16:
                signDir = minecraftSignsDir.get(signDir)
        elif type(signDir) == str:
            for k, v in minecraftSignsDir.items():
                if signDir == v:
                    break
            else:
                signDir = minecraftSignsDir.get(0)

        signType = signType.upper()
        if signType not in minecraftSignsType: raise Exception("Sign name error")
        self.conn.send(b"world.setSign", x, y, z, signType, signDir, line1, line2, line3, line4)

    def setWallSign(self, x: int, y: int, z: int, signType: str, signDir: int, line1="", line2="", line3="",
                    line4="") -> None:
        minecraftSignsType = ["SPRUCE_WALL_SIGN", "ACACIA_WALL_SIGN", "BIRCH_WALL_SIGN", "DARK_OAK_WALL_SIGN",
                              "JUNGLE_WALL_SIGN", "OAK_WALL_SIGN"]

        minecraftSignsDir = {0: 'SOUTH',
                             1: 'WEST',
                             2: 'NORTH',
                             3: 'EAST'}

        if type(signDir) == int:
            if 0 <= signDir < 4:
                signDir = minecraftSignsDir.get(signDir)
        elif type(signDir) == str:
            for k, v in minecraftSignsDir.items():
                if signDir == v:
                    break
            else:
                signDir = minecraftSignsDir.get(0)

        signType = signType.upper()
        if signType not in minecraftSignsType: raise Exception("Sign name error")
        self.conn.send(b"world.setWallSign", x, y, z, signType, signDir, line1, line2, line3, line4)

    def spawnEntity(self, x: int, y: int, z: int, entityID: int) -> int:
        """Spawn entity (x,y,z,id,[data])"""
        return int(self.conn.sendReceive(b"world.spawnEntity", int(x), int(y), int(z), entityID))

    def getEntities(self, typeId=-1):
        """Return a list of all currently loaded entities (EntityType:int) => [[entityId:int,entityTypeId:int,entityTypeName:str,posX:float,posY:float,posZ:float]]"""
        s = self.conn.sendReceive(b"world.getEntities")
        entities = [e for e in s.split("|") if e]
        #return entities
        return [[int(n.split(",")[0]), (n.split(",")[1]), round(float(n.split(",")[2])), round(float(n.split(",")[3])),
                 round(float(n.split(",")[4]))] for n in entities]

    def getNearbyEntities(self, x: int, y: int, z: int, radius: int):
        s = self.conn.sendReceive(b"world.getNearbyEntities", x, y, z, radius)
        entities = [e for e in s.split("|") if e]
        return [[int(n.split(",")[0]), (n.split(",")[1]), round(float(n.split(",")[2])), round(float(n.split(",")[3])),
                 round(float(n.split(",")[4]))] for n in entities]


    def removeEntity(self, id):
        """Remove entity by id (entityId:int) => (removedEntitiesCount:int)"""
        return int(self.conn.sendReceive(b"world.removeEntity", int(id)))

    def playEffect(self, x: int, y: int, z: int, effectName: str, data: int = 1):
        self.conn.send(b"world.playEffect", int(x), int(y), int(z), effectName, int(data))

    def playSound(self, x: int, y: int, z: int, sound: str, volume: float = 1, pitch: float = 1):
        """
        https://hub.spigotmc.org/javadocs/bukkit/org/bukkit/Sound.html
        :param soundName: MUSIC_DISC_CAT MUSIC_DISC_MELLOHI MUSIC_DRAGON MUSIC_DISC_CHIRP ENTITY_WOLF_AMBIENT
        :param volume: 0, 0.1 ... 1
        :param pitch: 0, 0.1 ... 3
        """
        self.conn.send(b"world.playSound", int(x), int(y), int(z), sound, volume, pitch)

    def getPlayers(self) -> list:
        """ :return: возвращает список всех игрооков в мире. """
        return (self.conn.sendReceive(b"world.getPlayers"))

    def getOnlinePlayers(self) -> list:
        """ :return: возвращает список игроков в онлайн. """
        return self.conn.sendReceive(b"world.getOnlinePlayers").split("|")[:-1]

    def getOfflinePlayers(self) -> list:
        return (self.conn.sendReceive(b"world.getOfflinePlayers")).split("|")[:-1]

    def getMaxPlayers(self) -> list:
        """ :return: возвращает максимальное количество игроков, которые смогут войти на этот сервер. """
        return (self.conn.sendReceive(b"world.getMaxPlayers"))

    def setTime(self, time: int):
        """
        Устанавливает относительное игровое время на сервере.
        day	1000
        midnight 18000
        night 13000
        noon 6000
        """
        self.conn.send(b"world.setTime", time)

    def setFullTime(self, time: int):
        """
        Устанавливает внутриигровое время на сервере.
        day	1000
        midnight 18000
        night 13000
        noon 6000
        """
        self.conn.send(b"world.setFullTime", time)

    def setWeather(self, weather: str):
        """
        Устанавливает погоду на сервере.
        :param weather: clear storm thunder
        """
        self.conn.send(b"world.setWeather", str(weather))

    def spawnParticle(self, x: int, y: int, z: int, particle: str, amount: int):
        """
        Создает частицу (количество раз, указанное в счетчике) в целевом месте.
        Particle.
        :param particle: Particle. CLOUD DAMAGE_INDICATOR GLOW HEART ...
        :param amount: 0, 1 ...
        """
        self.conn.send(b"world.spawnParticle", int(x), int(y), int(z), particle, amount)

    def getEntityTypes(self):
        types = self.conn.sendReceive(b"world.getEntityTypes")
        return types.split("|")

    def createExplosion(self, x: int, y: int, z: int, power: int = 4) -> None:
        """ Создает взрыв в указанных координатах с мощностью power. """
        self.conn.send(b"world.createExplosion", int(x), int(y), int(z), int(power))

    def abc(self, idd):
        self.conn.send(b"world.abc", idd)


    def getPlayerEntityId(self, name: str) -> int:
        """ Получает ID игрока по его имени => [id:int]"""
        return int(self.conn.sendReceive(b"world.getPlayerId", name))

    def getTemperature(self, x: int, y: int, z: int) -> float:
        """ Получает температуру в указанных координатах. """
        return float((self.conn.sendReceive(b"world.getTemperature", int(x), int(y), int(z))))
    
    def getBiome(self, x: int, y: int, z: int):
        """ Возвращает тип биома в точке """
        return self.conn.sendReceive(b"world.getBiome", x, y, z)

    def getHumidity(self, x: int, y: int, z: int) -> float:
        """ Получает уровень влажность в указанных координатаъ. """
        return float((self.conn.sendReceive(b"world.getHumidity", int(x), int(y), int(z))))

    def getWeatherDuration(self):
        """ Получает оставшееся время в тиках текущих условий. """
        return (self.conn.sendReceive(b"world.getWeatherDuration"))

    def getFullTime(self):
        return self.conn.sendReceive(b"world.getFullTime")
    #
    def getTime(self):
        return int(self.conn.sendReceive(b"world.getTime"))

    def getNearestStructure(self, x, y, z, structureType, radius):
        structures = self.conn.sendReceive(b"world.locateNearestStructure", x, y, z, structureType, radius)
        if structures != "0":
            struct = structures.split(",")
            return [struct[0].split("minecraft:")[1], float(struct[1]), float(struct[2]), float(struct[3])]

    def getStructureTypes(self):
        return ['pillager_outpost', 'mineshaft', 'mineshaft_mesa', 'mansion', 'jungle_pyramid', 'desert_pyramid', 'igloo', 'shipwreck', 'shipwreck_beached', 'swamp_hut', 'stronghold', 'monument', 'ocean_ruin_cold', 'ocean_ruin_warm', 'fortress', 'nether_fossil', 'end_city', 'buried_treasure', 'bastion_remnant', 'village_plains', 'village_desert', 'village_savanna', 'village_snowy', 'village_taiga', 'ruined_portal', 'ruined_portal_desert', 'ruined_portal_jungle', 'ruined_portal_swamp', 'ruined_portal_mountain', 'ruined_portal_ocean', 'ruined_portal_nether', 'ancient_city']
    #
    # def getGameTime(self):
    #     return self.conn.sendReceive(b"world.getGameTime")

    def isThundering(self) -> bool:
        """ Возвращает, есть ли гром. """
        result = self.conn.sendReceive(b"world.isThundering")
        return eval(result[0].upper() + result[1:])

    def isClearWeather(self) -> bool:
        """ Возвращает, есть ли в мире ясная погода. """
        result = self.conn.sendReceive(b"world.isClearWeather")
        return eval(result[0].upper() + result[1:])

    def strikeLightning(self, x: int, y: int, z: int):
        """ Ударяет молнией в указанных координатах. """
        self.conn.send(b"world.strikeLightning", int(x), int(y), int(z))

    def scoreBoard(self, playerId, t):
        self.conn.send(b"world.scoreBoard", playerId, t)

    def dropItemStack(self, x: int, y: int, z: int, itemStack):
        if not isinstance(itemStack, ItemStack):
            logging.warning("itemStack не является объектом класса ItemStack")
        else:
            lore = ""
            for lo in itemStack.lore:
                lore += lo + "|"

            attr = ""
            attr_level = ""
            for k, v in itemStack.attribute.items():
                attr += k + "|"
                attr_level += str(v) + "|"

            ench = ""
            ench_level = ""
            for k, v in itemStack.enchant.items():
                ench += k + "|"
                ench_level += str(v) + "|"
        self.conn.send(b"world.dropItemStack", x, y, z, itemStack.material, itemStack.amount, itemStack.unbreak, lore, itemStack.displayName, attr, attr_level, ench, ench_level, "empty")

    def dropItem(self, x: int, y: int, z: int, material: str, amount: int):
        self.conn.send(b"world.dropItem", x, y, z, material, amount)


    @staticmethod
    def create(address="localhost", port=4711, playerName=""):
        # return Minecraft(Connection(address, port))

        log("Running Python version:" + sys.version)
        conn = Connection(address, port)
        ItemStack.conn = conn
        Inventory.conn = conn
        Scoreboard.conn = conn
        Book.conn = conn
        Objective.conn = conn
        Merchant.conn = conn
        MerchantRecipe.conn = conn
        Score.conn = conn
        BossBar.conn = conn
        Mob.conn = conn
        Edu.conn = conn
        playerId = []
        if playerName != "":
            playerId = int(conn.sendReceive(b"world.getPlayerId", playerName))
            log("get {} playerid={}".format(playerName, playerId))

        return Minecraft(conn, playerId)

class Edu(Minecraft, Mob):
    def __init__(self, connection):
        self.conn = connection

    def generateMobs(self):
        mobs = []
        for m in range(random.randint(2, 4)):
            randxz = random.randint(10, 99)
            self.setBlocks(10, 180, 10, 99, 200, 99, Material.AIR)
            self.setBlocks(10, 180, 10, 99, 180, 99, Material.STONE)
            y = self.getHeight(randxz, randxz)
            a = self.spawnMob(randxz, y, randxz, Entity.SHEEP)
            mobs.append(Entity.SHEEP)
            mobs.append(randxz)
            mobs.append(y)
            mobs.append(randxz)
        return mobs

if __name__ == "__main__":
    mc = Minecraft.create()
    mc.postToChat("Hello, Minecraft!")
