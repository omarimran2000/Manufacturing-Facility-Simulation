import random

import simpy


class Component:

    def __init__(self, name: str):
        """
        Constructor for component
        :param name: of the component
        """
        self.name = name


class Product:

    def __init__(self, name: str, required_components: list[Component]):
        """
        Constructor for product
        :param name: of the product
        :param required_components: components required to build the product
        """
        self.name = name
        self.required_components = required_components


class Workstation:

    def __init__(self, env: simpy.Environment, name: str, product: Product, processing_times: list):
        """
        Constructor for workstation
        :param env: the environment the workstation will be
        :param name:  of the workstation
        :param product:  the product that the workstation is building
        :param processing_times: the processing times generated in the .dat file
        """
        self.name = name
        self.product = product
        self.buffers = {}
        for i in product.required_components:
            self.buffers[i] = 0
        self.env = env
        self.processing_times = processing_times
        self.products_made = 0
        env.process(self.workstation_process())
        self.wait_time = 0

    def add_to_buffer(self, component: Component) -> None:
        """
        Adds component to the buffer
        :param component: the component to be added
        :return: None
        """
        self.buffers[component] += 1

    def buffer_full(self, component: Component) -> bool:
        """
        Checks to see if the buffer for a particular component is full

        :param component: the component to be checked
        :return: if it is full or not
        """
        return self.buffers[component] >= 2

    def all_components_available(self) -> bool:
        """
        Checks to see if all the components are available to build the product
        :return: if product is ready to be built
        """
        for i in self.buffers.keys():
            if self.buffers[i] == 0:
                return False
        return True

    def produce(self) -> None:
        """
        Creates one product after all the components are available
        :return: None
        """
        for i in self.buffers.keys():
            self.buffers[i] -= 1

        self.products_made += 1

    def workstation_process(self):
        """
        Process to be run by SimPy environment
        :return: None
        """
        while True:
            if self.all_components_available():  # wait for all components to be available
                process_time = self.processing_times.pop(0)
                yield self.env.timeout(process_time)
                print(self.name, " created ", self.product.name, " at ", round(self.env.now, 2),
                      " minutes")
                self.produce()
            else:
                yield self.env.timeout(0.001)
                self.wait_time += 0.001


class Inspector:

    def __init__(self, env: simpy.Environment, name: str, components: list[Component], processing_times: list[list],
                 workstations: list[Workstation]):
        """
        Constructor for an inspector
        :param env: the environment the inspector will be
        :param name: of the inspector
        :param components: the components the inspector will build
        :param processing_times: the processing times generated in the .dat file
        :param workstations: the workstations that the inspector can send components to
        """
        self.name = name
        self.components = components
        self.env = env
        self.processing_times = {}

        count = 0
        for i in components:
            self.processing_times[i] = processing_times[count]
            count += 1

        self.workstations = workstations
        self.env.process(self.inspector_process())
        self.blocked_time = 0

    def is_blocked(self, component: Component) -> bool:
        """
        Checks to see if an inspector is blocked
        :param component: the component the inspector needs to send to the workstation
        :return: blocked or not
        """
        for workstation in self.workstations:
            if component in workstation.buffers.keys():
                if not workstation.buffer_full(component):
                    return False
        return True

    def send_component(self, component: Component) -> Workstation:
        """
        Used to send a component to the workstation

        :param component: sends component to an available workstation
        :return: the workstation where it is sent
        """
        min_buffer = 2
        for workstation in self.workstations:
            if component in workstation.buffers.keys() and workstation.buffers[component] < min_buffer:
                min_buffer = workstation.buffers[component]
        for workstation in self.workstations:
            if component in workstation.buffers.keys() and not workstation.buffer_full(component) and \
                    workstation.buffers[component] == min_buffer:
                workstation.add_to_buffer(component)
                return workstation

    def choose_random_component(self) -> Component:
        """
        Returns a randomly chosen component for the inspector
        :return: a component
        """
        return self.components[random.randint(0, len(self.components) - 1)]

    def inspector_process(self):
        """
        Process to be run by SimPy environment
        :return: None
        """
        while True:
            component = self.choose_random_component()
            delay = self.processing_times[component].pop(0)
            yield self.env.timeout(delay)  # allow delay for processing times

            while self.is_blocked(component):  # waits for buffers to free
                yield self.env.timeout(0.001)
                self.blocked_time += 0.001
            destination = self.send_component(component)
            print(self.name, " sent ", component.name, " to ", destination.name, " at ", round(self.env.now, 2),
                  " minutes")
