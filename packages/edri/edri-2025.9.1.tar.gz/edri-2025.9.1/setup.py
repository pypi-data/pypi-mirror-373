from setuptools import setup, find_packages

long_description = """
# Event Driven Routing Infrastructure (EDRI)

EDRI is a framework designed to simplify the development of parallel and distributed applications. It allows developers to efficiently run code across multiple threads, processes, or even machines by leveraging an event-driven architecture. EDRI emphasizes flexibility and scalability, enabling the development of systems that can handle complex workflows with ease.

The framework is ideal for applications that require high throughput, low latency, and the ability to scale horizontally across distributed systems. It is designed to handle dynamic, real-time data processing and communication through the use of well-defined events.

## Key Features

- **Event-Driven Architecture**: EDRI uses events as data packets to enable communication between multiple senders and recipients. Events can be notifications, requests, or tunnels, each serving a specific communication purpose.

- **Routing Infrastructure**: The exchange and delivery of events are managed similarly to TCP/IP in computer networks. The router directs events to appropriate recipients based on event types, ensuring efficient communication.

- **Scalable Architecture**: The framework supports running tasks as methods, threads, and processes, allowing for scalable and parallel execution of tasks across multiple computing nodes.

- **Flexible Components**: EDRI includes various components such as Router, Manager, Worker, Scheduler, and Key-Value Store, each designed to handle specific responsibilities within the system.

## Components

### Event

Events are data packets created using Python data classes to enable communication between multiple senders and recipients. They serve as the core communication mechanism within EDRI and can be categorized into:

- **Notifications**: Events that announce actions or changes in the system.
- **Requests**: Events that solicit a response or action from another component.
- **Tunnels**: Events that facilitate continuous data transfer between components.

Events are strictly defined to ensure clarity and consistency across the system. They can carry responses or simply announce actions, depending on their type.

### Router

The Router is the central component responsible for forwarding events between different parts of the framework, typically managers. It ensures that events are delivered to the appropriate recipients based on their event types.

Key responsibilities of the Router include:

- Directing events to the appropriate managers or workers.
- Managing connections to external systems via the Connector.
- Caching connections to handle short-term network outages without disrupting operations.

#### Connector

The Connector is a specialized part of the Router that manages the connection between the Router and external systems (referred to as the Switch). It handles:

- Bridging internal communication with external networks using TCP/IP sockets.
- Distributing routed events to other routers and vice versa.
- Ensuring continuity of events to prevent loss or duplication during connection interruptions.

### Manager

The Manager distributes tasks contained in the transmitted events to individual workers. It supports running tasks in various modes:

- **Methods**: Tasks executed as regular function calls within the same process.
- **Threads**: Tasks executed in separate threads for parallelism within the same process.
- **Processes**: Tasks executed in separate processes for true parallelism across CPU cores.

The Manager also handles data transfer for tunnels and subscribes to the event types it needs to receive.

### Scheduler

The Scheduler is a special type of Manager used for time-defined event sending. It enables scheduling tasks or events at specific times, such as:

- Performing backups during off-peak hours.
- Sending regular updates or heartbeat signals.

### Key-Value Store

The Key-Value Store is another specialized Manager that provides a built-in storage mechanism for caching and retrieving data. It is useful for:

- Caching data during processes like data downloads.
- Periodically updating stored data using the Scheduler.
- Sharing state or configuration data between components.

### Worker

Workers are classes defined by the programmer to perform specific tasks or operations. They are the execution units in the EDRI framework and can be customized to handle a wide range of functionalities.

### API

The API serves as the interface between clients and the EDRI system. It handles:

- Converting incoming client requests into events.
- Processing events through the system.
- Returning responses back to the clients.

**Features of the API include:**

- Support for dynamic content generation.
- Management of event-based interactions, including both request-type and notification-type events.
- Real-time communication capabilities between the server and clients.

## Use Cases

EDRI is suitable for applications that require:

- **High Throughput and Low Latency**: Efficient handling of a large number of events with minimal delay.
- **Real-Time Data Processing**: Immediate processing and response to incoming data.
- **Horizontal Scalability**: Ability to scale across multiple machines or nodes.
- **Complex Workflows**: Management of intricate processes that benefit from an event-driven approach.

## Getting Started

To start using EDRI:

1. **Define Your Events**: Use Python data classes to define the events that will be used for communication between components.

2. **Set Up Your Router and Managers**: Initialize the Router and any necessary Managers (including Scheduler and Key-Value Store if needed).

3. **Implement Your Workers**: Create Worker classes that perform the specific tasks required by your application.

4. **Use the API**: Utilize the API to interact with the system, handle client requests, and facilitate communication.

5. **Run and Monitor Your Application**: Execute your application and monitor the event flow to ensure everything operates as expected.

## Conclusion

EDRI provides a robust framework for developing scalable, parallel, and distributed applications using an event-driven architecture. By abstracting the complexities of inter-process and network communication, it allows developers to focus on implementing the core logic of their applications.

Whether you're building a real-time data processing system, a distributed service, or any application that benefits from parallel execution, EDRI offers the tools and structure to make development more manageable and efficient.
"""

setup(
    name='edri',
    version='2025.09.01',
    packages=find_packages(),
    description='Event Driven Routing Infrastructure',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Marek Olšan',
    author_email='marek.olsan@gmail.com',
    package_data={'': ['api/static_pages/*.j2']},
    install_requires=[
        "typeguard>=4.0",
        "requests>=2.0",
        "validators>=0.22.0",
        "typing_extensions>=4.0",
        "multipart>=1.0",
        "jinja2>=3.1",
        "watchdog>=6",
        "websockets>=14",
        "posix-ipc>=1.2.0",
    ],
    extras_require={
        "uvicorn": ["uvicorn[standard]>=0.32.0"],
        "hypercorn": ["hypercorn>=0.17.0"],
        "dev": [
            "uvicorn>=0.32.0",
            "hypercorn>=0.17.0",
            "sphinx>=8.0.0",
            "sphinx-autodoc-typehints>=3.0.0",
            "sphinx_rtd_theme>=2.0.0",
            "wheel",
            "coverage",
            "setuptools",
            "twine",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Typing :: Typed",
    ],
)
