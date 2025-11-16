from mininet.topo import Topo


class CampoTopo(Topo):
    """
    Topología SDN en CAMPO:
      - s1: switch SDN
      - h_gw: gateway IoT
      - h_s1, h_s2, h_s3: sensores simulados
      Red: 10.0.1.0/24
    """

    def build(self, **opts):
        # Switch SDN en campo
        s1 = self.addSwitch('s1')

        # Gateway IoT
        h_gw = self.addHost('h_gw', ip='10.0.1.1/24')

        # Sensores simulados
        h_s1 = self.addHost('h_s1', ip='10.0.1.11/24')
        h_s2 = self.addHost('h_s2', ip='10.0.1.12/24')
        h_s3 = self.addHost('h_s3', ip='10.0.1.13/24')

        # Enlaces
        self.addLink(h_gw, s1)
        self.addLink(h_s1, s1)
        self.addLink(h_s2, s1)
        self.addLink(h_s3, s1)

# Registro para mn --custom
topos = {
    'campo': (lambda: CampoTopo())
}