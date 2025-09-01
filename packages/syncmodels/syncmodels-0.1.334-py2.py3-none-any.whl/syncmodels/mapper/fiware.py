from agptools.helpers import I

from .mapper import Mapper


class FIWAREMapper(Mapper):
    "FIWAREMapper"

    PYDANTIC = None
    id = "deviceName", I

    ts = I, I  # 1712818589000,
    entity_ts = I, I  # 1712818589000
    entity_location = I, I  # [0.0, 0.0],
    entity_id = I, I  # 'MAL023_water_consumption_01',
    entity_type = I, I  # 'WaterConsumption',
    validity_ts = I, I  # None ?
    fiware_service = I, I  #  fs_ccoc
    fiware_servicepath = I, I  #  '/centesimal/system12',
    wave__ = "wave_.*", I
