"""
MOCK FILE - Do not use in production!!!
"""
import numpy as np
print("\033[91m Warning - NOT FOR PRODUCTION!!! \033[0m")


class DHT11:
    humidity = np.random.randint(0, 10)
    temperature = np.random.randint(0, 10)

    def __init__(self, pin):
        pass
