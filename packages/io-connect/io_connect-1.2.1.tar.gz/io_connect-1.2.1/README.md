# io_connect
`io_connect` is a Python package designed for system monitoring and data management. It includes components for handling alerts, MQTT messaging, data access, and event management.


## Components

### Alerts Handler

The `AlertsHandler` class is a critical component for system monitoring and maintenance. It enables the seamless dissemination of alerts through email and Microsoft Teams, ensuring timely and effective communication of important notifications.

#### Features
- **Email Alerts**: Send alerts directly to email addresses.
- **Microsoft Teams Notifications**: Integrate with Microsoft Teams for notifications.
  
### MQTT Handler

The `MQTTHandler` class provides an interface for publishing data to an MQTT broker. It supports reliable and efficient message sending, whether you're transmitting individual payloads or managing data streams.

#### Features
- **Flexible Publishing**: Send single or multiple messages.
- **Reliable Transmission**: Ensure data reaches its destination reliably.

### Data Access

The `DataAccess` class offers a comprehensive set of methods for various data retrieval tasks. It supports operations such as retrieving device metadata and querying databases for precise information, optimizing data access workflows.

#### Features
- **Device Metadata Retrieval**: Access information about devices.
- **Database Queries**: Perform queries for accurate data retrieval.

### Events Handler

The `EventsHandler` class provides a versatile interface for interacting with an API dedicated to event and notification management. It facilitates event publishing, data retrieval, category fetching, and event analysis.

#### Features
- **Event Publishing**: Publish events efficiently.
- **Data Retrieval**: Retrieve event data within specified intervals.
- **Category Fetching**: Get detailed event categories.
- **Event Analysis**: Analyze events comprehensively.

## Installation

To install `io_connect`, you can use pip:

```bash
pip install io_connect 
```


## Documentation
[Documentation](https://wiki.iosense.io/en/Data_Science/io-connect)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


# Reach us
For usage questions, please reach out to us at reachus@faclon.com