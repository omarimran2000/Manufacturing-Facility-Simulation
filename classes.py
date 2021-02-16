import simpy


class Component:

    def __init__(self, name: str):
        self.name = name


class Product:

    def __init__(self, name: str, required_components: list[Component]):
        self.name = name
        self.required_components = required_components


class Workstation:

    def __init__(self, env: simpy.Environment, name: str, product: Product, processing_times: list):
        self.name = name
        self.product = product
        self.buffers = {}
        for i in product.required_components:
            self.buffers[i] = []
        self.env = env
        self.processing_times = processing_times


class Inspector:

    def __init__(self, env: simpy.Environment, name: str, components: list[Component], processing_times: list[list],
                 workstations: list[Workstation]):
        self.name = name
        self.components = components
        self.env = env
        self.processing_times = {}

        count = 0
        for i in components:
            self.processing_times[i] = processing_times[count]
            count += 1

        self.workstations = workstations
