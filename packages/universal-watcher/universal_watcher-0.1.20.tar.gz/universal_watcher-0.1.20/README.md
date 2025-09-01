# Universal Watcher

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

**Universal Watcher** is a versatile and extendable Python package designed to monitor various data sources and notify users about new data through multiple notification platforms. Easily add support for new data sources and notification methods without modifying the core package.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Creating a Watcher](#creating-a-watcher)
  - [Checking Watchers](#checking-watchers)
  - [Using a Custom Formatter](#using-a-custom-formatter)
- [Extending Universal Watcher](#extending-universal-watcher)
  - [Adding a New Data Source](#adding-a-new-data-source)
  - [Adding a New Formatter](#adding-a-new-formatter)
  - [Adding a New Notification Platform](#adding-a-new-notification-platform)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Installation

<a id="installation"></a>

Install via pip:

```bash
pip install universal_watcher
```

Or install from source:

```bash
git clone https://github.com/simon-ne/universal-watcher.git
cd universal-watcher
pip install .
```

## Usage

<a id="usage"></a>

Universal Watcher provides methods to create new watchers, check existing watchers for new data, and check all watchers at once.

### Creating a Watcher

<a id="creating-a-watcher"></a>

To create a new watcher, define the data source and notification platform parameters and register the watcher in the database. This setup allows you to monitor specific data sources and receive notifications through your chosen platforms.

```python
from universal_watcher import Watcher

watcher = Watcher()
watcher.create(
    watcher_name="my_watcher",
    data_source_data={
        "name": "bazos_sk",
        "formatter": "email_formatter",
        "parameters": {
            "category": "auto",
            "location": "12345",
            "search": "sedan",
            "min_price": 5000,
            "max_price": 20000,
            "radius": 50
        }
    },
    notification_platform_data={
        "name": "email",
        "parameters": {
            "to": "recipient@example.com"
        }
    }
)
```

### Checking Watchers

<a id="checking-watchers"></a>

- **Check a Specific Watcher**: Looks for new data and notifies the user if any new items are found.

  ```python
  watcher.check("my_watcher")
  ```

- **Check All Watchers**: Iterates through all registered watchers, checking for new data and sending notifications as needed.

  ```python
  watcher.check_all()
  ```

### Using a Custom Formatter

<a id="using-a-custom-formatter"></a>

- **Create a custom formatter**: Inherit from `Formatter` class, implement `format_items` method.

  ```python
  # your_formatter.py
  from universal_watcher.core.classes.formatter.formatter import Formatter
  from universal_watcher.core.classes.data_source.data_source_item import (
      DataSourceItem,
  )
  from universal_watcher.core.classes.notification_platform.notification_platform_input import (
      NotificationPlatformInput,
  )


  class YourCustomFormatter(Formatter):
      def format_items(
          self, items: list[DataSourceItem]
      ) -> NotificationPlatformInput:
          # Implement formatting logic
          pass
  ```

- **Use the custom formatter**: Instead of using `watcher.check()` method, do the following.

  ```python
  # main.py
  from universal_watcher import Watcher
  from your_formatter import YourCustomFormatter

  watcher = Watcher()
  new_items = watcher.get_new_data(watcher_name)
  notif_input = YourCustomFormatter().format_items(new_items)
  watcher.send_notification(watcher_name, notif_input)
  ```

## Extending Universal Watcher

<a id="extending-universal-watcher"></a>

Universal Watcher is designed to be easily extensible. You can add new data sources, formatters, and notification platforms without altering the core package.

### Adding a New Data Source

<a id="adding-a-new-data-source"></a>

1. **Create the Data Source Class**: Inherit from `DataSource` and implement the required abstract methods.

2. **Add Formatters**: Each data source can have multiple formatters. Create formatter classes inheriting from `Formatter`.

3. **Register the Data Source**: Place your data source in the `data_sources` package and ensure it's discoverable via the `setup.py` script.

**Example Structure:**

```
universal_watcher/
  data_sources/
    your_data_source/
      __init__.py
      your_data_source.py
      formatters/
        your_formatter.py
      models/
        your_item.py
      services/
        your_service.py
```

### Adding a New Formatter

<a id="adding-a-new-formatter"></a>

1. **Create Formatter Class**: Inherit from `Formatter` and implement the `format_items` method.

2. **Register Formatter**: Add the formatter to the data source's `config.py` under the `FORMATTERS` dictionary.

```python
# your_formatter.py
from universal_watcher.core.classes.formatter.formatter import Formatter

class YourFormatter(Formatter):
    def format_items(self, items):
        # Implement formatting logic
        pass
```

```python
# config.py
from .your_formatter import YourFormatter

FORMATTERS = {
    'your_formatter': YourFormatter
}
```

### Adding a New Notification Platform

<a id="adding-a-new-notification-platform"></a>

1. **Create Notification Platform Class**: Inherit from `NotificationPlatform` and implement the required methods.

2. **Register the Notification Platform**: Place your platform in the `notification_platforms` package and ensure it's discoverable via the `setup.py` script.

**Example Structure:**

```
universal_watcher/
  notification_platforms/
    your_platform/
      __init__.py
      your_platform.py
      models/
        your_input.py
      services/
        your_service.py
```

## Configuration

<a id="configuration"></a>

Use environment variables to manage sensitive configurations such as SMTP credentials. This ensures that sensitive information is not hard-coded and can be easily managed across different environments.

**Example Environment Variables for Email Notification Platform:**

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_ENCRYPTION`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_SENDER_EMAIL`

You can set these variables in your environment or use a `.env` file. Ensure that your environment variables are loaded before running the application.

## Contributing

<a id="contributing"></a>

Contributions are welcome! Please open issues or submit pull requests for enhancements or bug fixes.

## License

<a id="license"></a>

This project is licensed under the [MIT License](LICENSE).