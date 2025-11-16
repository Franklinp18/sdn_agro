sdn-agro Project
================

This project contains a simple prototype for integrating software-defined networking (SDN),
blockchain-inspired traceability, and IoT sensors for an agro-industrial supply chain use case
in Ecuador.  It includes:

- **mininet/**: Custom topologies for a field network (`topo_campo.py`) and an office network
  (`topo_oficina.py`).
- **services/**: Two Flask applications—a backend inventory/billing service (`backend_app.py`)
  and a simple in-memory ledger (`blockchain_service.py`).
- **pox/ext/sdn_agro.py**: A custom POX controller implementing IP-based access control
  policies for the Mininet topologies.  The rest of the POX framework is not included here;
  see `pox/README.md` for instructions on obtaining POX.
- **controller/**: Empty placeholder for any additional controller-related scripts.

To run the prototype:

1. Clone the official POX repository into `sdn-agro/pox/` (see `pox/README.md`).
2. Install Mininet and the Python dependencies (Flask and requests) on your host machine.
3. Start the POX controller with the `sdn_agro` module:

   ```bash
   cd sdn-agro/pox
   python3 pox.py log.level --DEBUG sdn_agro
   ```

4. In another terminal, launch the desired Mininet topology:

   ```bash
   # Field domain
   sudo mn --custom ../mininet/topo_campo.py --topo campo --controller=remote --switch ovsk,protocols=OpenFlow10

   # Office domain
   sudo mn --custom ../mininet/topo_oficina.py --topo oficina --controller=remote --switch ovsk,protocols=OpenFlow10
   ```

5. Run the services on the appropriate hosts within Mininet as described in the documentation.