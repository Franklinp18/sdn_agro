from mininet.topo import Topo


class OficinaTopo(Topo):
    """
    Topología SDN en OFICINA:
      - s1: switch SDN
      - h_inv : servidor de inventario
      - h_fact: servidor de facturación
      - h_bc  : nodo blockchain
      - h_cli : cliente de oficina
      Red: 10.0.2.0/24
    """

    def build(self, **opts):
        # Switch SDN en oficina
        s1 = self.addSwitch('s1')

        # Servidores
        h_inv  = self.addHost('h_inv',  ip='10.0.2.11/24')
        h_fact = self.addHost('h_fact', ip='10.0.2.12/24')
        h_bc   = self.addHost('h_bc',   ip='10.0.2.13/24')

        # Cliente de oficina
        h_cli  = self.addHost('h_cli',  ip='10.0.2.21/24')

        # Enlaces
        self.addLink(h_inv,  s1)
        self.addLink(h_fact, s1)
        self.addLink(h_bc,   s1)
        self.addLink(h_cli,  s1)

# Registro para mn --custom
topos = {
    'oficina': (lambda: OficinaTopo())
}