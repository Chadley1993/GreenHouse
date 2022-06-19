import json


class SSSConstants:
    port = 8100
    num_expect_conn = 2


class SensorData:
    def __init__(self):
        self.outside_temp = None
        self.outside_humidity = None
        self.inside_temp = None
        self.inside_humidity = None
        self.timestamp = None
        self.comp_temp = None
        self.comp_humidty = None
    
    def set_comp_temp(self, x):
        self.comp_temp = x

    def get_comp_temp(self):
        return self.comp_temp
    
    def set_comp_humidity(self, x):
        self.set_comp_humidity = x

    def get_comp_humidity(self):
        return self.comp_humidity

    def set_outside_temp(self, x):
        self.outside_temp = x

    def get_outside_temp(self):
        return self.outside_temp

    def set_outside_humidity(self, x):
        self.outside_humidity = x

    def get_outside_humidity(self):
        return self.outside_humidity

    def set_inside_temp(self, x):
        self.inside_temp = x

    def get_inside_temp(self):
        return self.inside_temp

    def set_inside_humidity(self, x):
        self.inside_humidity = x

    def get_inside_humidity(self):
        return self.inside_humidity

    def set_timestamp(self, x):
        self.timestamp = x

    def get_timestamp(self):
        return self.timestamp

    def toJSON(self):
        return self.__dict__


class SignedObject:
    def __init__(self, og_object, signature):
        self.og_object = og_object
        self.signature = signature

    def get_og_object(self) -> SensorData:
        return self.og_object

    def get_signature(self):
        return self.signature
