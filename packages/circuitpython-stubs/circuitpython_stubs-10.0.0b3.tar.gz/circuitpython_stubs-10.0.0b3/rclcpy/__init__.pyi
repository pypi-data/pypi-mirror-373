"""Robot Operating System (ROS2) connectivity through micro-ROS

The `rclcpy` module contains basic classes and connectivity options for
communicating with a ROS network running on a linux machine, using the
eProsima's `micro-ROS client API <https://micro.ros.org/>`_.

The underlying micro-ROS system uses a resource-constrained middleware layer
(XRCE-DDS) that must be connected to an agent running within ROS2 on a host
Linux computer. The API exposed by Circuitpython aims to be close to the
standard Python API for ROS2, ``rclpy`` with minor additions to support
connecting to this agent.

Wifi must be connected before calling any `rclcpy` functions. As with
``rclpy``, the `rclcpy.init()` function must be run before creating any ROS
objects. Child objects, such as publishers, must be created by their parent
objects. For example::

  import os, wifi, time
  import rclcpy
  wifi.radio.connect(ssid=os.getenv('CIRCUITPY_WIFI_SSID'),
                     password=os.getenv('CIRCUITPY_WIFI_PASSWORD'))
  rclcpy.init("192.168.10.111","8888")
  mynode = rclcpy.Node("foo")
  mypub = mynode.create_publisher("bar")
  mypub.publish_int32(42)
"""

from __future__ import annotations

def init(
    agent_ip: str,
    agent_port: str,
    *,
    domain_id: int = 0,
) -> None:
    """Initialize micro-ROS and connect to a micro-ROS agent.

    This function starts ROS communications and connects to the micro-ROS agent
    on a linux computer. It must be called before creating ROS objects.

    :param str agent_ip: The IP address of the micro-ROS agent
    :param str agent_port: The port number of the micro-ROS agent as a string
    :param int domain_id: The ROS 2 domain ID for network isolation and organization.
        Devices with the same domain ID can communicate with each other.
    """
    ...

def create_node(node_name: str, *, namespace: str | None = None) -> Node:
    """Create a Node.

    Creates an instance of a ROS2 Node. Nodes can be used to create other ROS
    entities like publishers or subscribers. Nodes must have a unique name, and
    may also be constructed from their class.

    :param str node_name: The name of the node. Must be a valid ROS 2 node name.
    :param str namespace: The namespace for the node. If None, the node will be
        created in the root namespace.
    :return: A new Node object
    :rtype: Node
    """
    ...

class Node:
    """A ROS2 Node"""

    def __init__(
        self,
        node_name: str,
        *,
        namespace: str | None = None,
    ) -> None:
        """Create a Node.

        Creates an instance of a ROS2 Node. Nodes can be used to create other ROS
        entities like publishers or subscribers. Nodes must have a unique name, and
        may also be constructed from their class.

        :param str node_name: The name of the node. Must be a valid ROS 2 node name
        :param str namespace: The namespace for the node. If None, the node will be
            created in the root namespace
        """
        ...

    def deinit(self) -> None:
        """Deinitializes the node and frees any hardware or remote agent resources
        used by it. Deinitialized nodes cannot be used again.
        """
        ...

    def create_publisher(self, topic: str) -> Publisher:
        """Create a publisher for a given topic string.

        Creates an instance of a ROS2 Publisher.

        :param str topic: The name of the topic
        :return: A new Publisher object for the specified topic
        :rtype: Publisher
        """
        ...

    def get_name(self) -> str:
        """Get the name of the node.

        :return: The node's name
        :rtype: str
        """
        ...

    def get_namespace(self) -> str:
        """Get the namespace of the node.

        :return: The node's namespace
        :rtype: str
        """
        ...

class Publisher:
    """A ROS2 publisher"""

    def __init__(self) -> None:
        """Publishers cannot be created directly.

        Use :meth:`Node.create_publisher` to create a publisher from a node.

        :raises NotImplementedError: Always, as direct instantiation is not supported
        """
        ...

    def deinit(self) -> None:
        """Deinitializes the publisher and frees any hardware or remote agent resources
        used by it. Deinitialized publishers cannot be used again.
        """
        ...

    def publish_int32(self, message: int) -> None:
        """Publish a 32-bit signed integer message to the topic.

        :param int message: The integer value to publish. Must be within the range
            of a 32-bit signed integer (-2,147,483,648 to 2,147,483,647)
        """
        ...

    def get_topic_name(self) -> str:
        """Get the name of the topic this publisher publishes to.

        :return: The topic name as specified when the publisher was created
        :rtype: str
        """
        ...
