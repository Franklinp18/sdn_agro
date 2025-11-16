from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import ethernet, ipv4, arp
from pox.lib.addresses import IPAddr

log = core.getLogger()

# Pares de IP permitidos para tráfico IPv4
ALLOWED_IP_PAIRS = set([
    # Campo (10.0.1.0/24): sensores ↔ gateway
    ('10.0.1.11', '10.0.1.1'),
    ('10.0.1.1',  '10.0.1.11'),
    ('10.0.1.12', '10.0.1.1'),
    ('10.0.1.1',  '10.0.1.12'),
    ('10.0.1.13', '10.0.1.1'),
    ('10.0.1.1',  '10.0.1.13'),

    # Oficina (10.0.2.0/24): cliente ↔ servicios
    ('10.0.2.21', '10.0.2.11'),
    ('10.0.2.11', '10.0.2.21'),
    ('10.0.2.21', '10.0.2.12'),
    ('10.0.2.12', '10.0.2.21'),
    # Inventario ↔ blockchain
    ('10.0.2.11', '10.0.2.13'),
    ('10.0.2.13', '10.0.2.11'),
    # Inventario ↔ facturación
    ('10.0.2.11', '10.0.2.12'),
    ('10.0.2.12', '10.0.2.11'),
])


class SDNAgro(object):
    """Controlador SDN para las topologías de campo y oficina."""

    def __init__(self, connection):
        self.connection = connection
        self.mac_to_port = {}
        connection.addListeners(self)
        log.info("Nuevo switch conectado: %s", connection)

    def _flood(self, event):
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        event.connection.send(msg)

    def _install_and_forward(self, event, out_port):
        packet = event.parsed
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet, event.port)
        msg.idle_timeout = 20
        msg.hard_timeout = 60
        msg.actions.append(of.ofp_action_output(port=out_port))
        msg.data = event.ofp
        event.connection.send(msg)

    def _drop(self, event, idle_timeout=20, hard_timeout=60):
        packet = event.parsed
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet, event.port)
        msg.idle_timeout = idle_timeout
        msg.hard_timeout = hard_timeout
        event.connection.send(msg)
        log.debug("Instalando DROP para flujo bloqueado")

    def _is_ipv4_allowed(self, src_ip, dst_ip):
        pair = (str(src_ip), str(dst_ip))
        return pair in ALLOWED_IP_PAIRS

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed:
            return
        in_port = event.port
        self.mac_to_port[packet.src] = in_port
        # Manejar ARP
        if packet.type == ethernet.ARP_TYPE:
            dst_port = self.mac_to_port.get(packet.dst)
            if dst_port is None:
                self._flood(event)
            else:
                self._install_and_forward(event, dst_port)
            return
        # Manejar IPv4
        if packet.type == ethernet.IP_TYPE:
            ip_packet = packet.payload
            src_ip = ip_packet.srcip
            dst_ip = ip_packet.dstip
            if not self._is_ipv4_allowed(src_ip, dst_ip):
                log.info("BLOQUEADO IPv4 %s -> %s", src_ip, dst_ip)
                self._drop(event)
                return
            dst_port = self.mac_to_port.get(packet.dst)
            if dst_port is None:
                self._flood(event)
            else:
                self._install_and_forward(event, dst_port)
            return
        # Otros tipos
        dst_port = self.mac_to_port.get(packet.dst)
        if dst_port is None:
            self._flood(event)
        else:
            self._install_and_forward(event, dst_port)


def launch():
    def start_switch(event):
        log.info("Controlando nuevo switch: %s", event.connection)
        SDNAgro(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
    log.info("Controlador SDNAgro cargado")