"""
Network Iterated Prisoner's Dilemma Framework

A comprehensive framework for simulating and analyzing multi-agent learning
in network-structured environments using the Iterated Prisoner's Dilemma.
"""

__version__ = "1.0.0"
__author__ = "maximusjwl"
__email__ = "max.lams99@gmail.com"

# Main imports
from .agent_simulator import AgentSimulator
from .network_environment import initialise_network
from .round import simulate_round
from .network_tops import make_fc_net, make_ring_net, make_sw_net

# Version info
__all__ = [
    "AgentSimulator",
    "initialise_network", 
    "simulate_round",
    "make_fc_net",
    "make_ring_net", 
    "make_sw_net",
    "__version__",
    "__author__",
    "__email__"
]

