from shared_kernel.messaging.nats_databus import NATSDataBus
from shared_kernel.messaging.http_databus import HTTPDataBus
from shared_kernel.messaging.aws_databus import AWSDataBus
from shared_kernel.messaging.azure_databus import AzureDataBus
from shared_kernel.interfaces import DataBus


# create an enum for the buses available
class DataBusFactory:
    data_bus_classes = {
        "NATS": NATSDataBus,
        "HTTP": HTTPDataBus,
        "AWS": AWSDataBus,
        "AZURE": AzureDataBus
    }

    @staticmethod
    def create_data_bus(bus_type: str, config: dict) -> DataBus:
        data_bus_class = DataBusFactory.data_bus_classes.get(bus_type)
        if data_bus_class is None:
            raise ValueError(f"Unknown data bus type: {bus_type}")
        return data_bus_class(config)
