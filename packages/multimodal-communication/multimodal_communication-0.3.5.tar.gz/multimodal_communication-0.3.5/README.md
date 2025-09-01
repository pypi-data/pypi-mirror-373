# Multimodal Communication

`multimodal_communication` provides utilities for sending text messages through email-to-SMS gateways and managing files in Google Cloud Storage. This package is designed to simplify communication and data management across different platforms.

## Features

- **SMS Messaging**: Send text messages via email-to-SMS gateways (supports multiple carriers)
- **Asynchronous Support**: Utilizes `asyncio` for non-blocking message sending
- **Batch Messaging**: Send messages to multiple recipients simultaneously
- **Google Cloud Storage**: Easy file upload, download, and deletion operations
- **Multiple Data Format Support**: Work with CSV, JSON, and pickled objects

## Components

### SMS Messaging Module

This module allows you to send text messages through email-to-SMS gateways, supporting various carriers including Verizon, T-Mobile, Sprint, AT&T, and more.

```python
from multimodal_communication.python_texting import send_text_message

# Send a simple text message
send_text_message(
    message="Hello from Python!",
    subject="Notification",
    phone_number="1234567890",
    carrier="tmobile",
    email="your-email@gmail.com",
    email_password="your-app-password"
)
```

### CloudHelper

The `CloudHelper` class provides an interface for interacting with Google Cloud Storage:

```python
from multimodal_communication.cloud_functions import CloudHelper

# Upload a local file to Google Cloud Storage
cloud = CloudHelper(path="path/to/local/file.csv")
cloud.upload_to_cloud(bucket_name="my-bucket", file_name="cloud-file.csv")

# Upload an object from memory
import pandas as pd
df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
cloud = CloudHelper(obj=df)
cloud.upload_to_cloud(bucket_name="my-bucket", file_name="dataframe.csv")

# Download a file from Google Cloud Storage
cloud = CloudHelper()
df = cloud.download_from_cloud("my-bucket/path/to/file.csv")

# Delete a file from Google Cloud Storage
cloud = CloudHelper()
cloud.delete_from_cloud(bucket_name="my-bucket", file_name="file-to-delete.csv")
```

## Installation (with local project download)

```bash
pip install . -e
```

## Requirements

- Python 3.6+
- pandas
- google-cloud-storage
- aiosmtplib

## Setup

### Google Cloud Authentication

To use the `CloudHelper` class:

1. Set up Application Default Credentials (ADC) as described in the [Google Cloud documentation](https://cloud.google.com/docs/authentication/external/set-up-adc)
2. Ensure your user account or service account has the required permissions (e.g., "storage.buckets.list")

### Gmail Authentication for SMS

To use the SMS messaging functionality with Gmail:

1. Create an App Password for your Google account (if you have 2FA enabled)
2. Or enable "Less secure app access" (not recommended for production)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.