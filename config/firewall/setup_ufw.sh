#!/bin/bash
# UFW (Uncomplicated Firewall) Configuration Script for VoIP Business Solution
# Based on VoIP Business Solution: Enhanced Deployment Guide (Version 2.0)
#
# This script applies firewall rules as specified in the deployment guide.
# Run this script with sudo privileges on each relevant server.
#
# IMPORTANT:
# - Review rules carefully before applying, especially SSH access.
# - Ensure you have console access or an alternative way to manage the server
#   in case SSH access is misconfigured and you get locked out.
# - These rules are general. Specific servers (e.g., DB server, App server)
#   might need only a subset of these rules. Apply relevant rules per server role.

echo "Applying UFW firewall rules for VoIP Business Solution..."

# Reset UFW to a clean state (optional, use with caution if rules already exist)
# echo "Disabling UFW and resetting rules..."
# sudo ufw --force disable # Disable first to prevent lockout during reset
# sudo ufw --force reset
# echo "UFW reset complete."

# Default policies: Deny all incoming, allow all outgoing
echo "Setting default policies: deny incoming, allow outgoing..."
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH Access
# Limit SSH access to specific trusted IP addresses or ranges for better security.
# Replace 203.0.113.0/24 and 198.51.100.0/24 with your actual admin/VPN IPs.
# If your IP is dynamic, this can be tricky. Consider a bastion host or VPN.
echo "Allowing SSH access from specific IPs..."
sudo ufw allow from 203.0.113.0/24 to any port 22 comment 'SSH from Office Network'
sudo ufw allow from 198.51.100.0/24 to any port 22 comment 'SSH from VPN Network'
# If you need to allow SSH from any IP (less secure, use strong passwords/keys & Fail2ban):
# sudo ufw allow ssh # This is equivalent to 'allow 22/tcp'

# HTTP and HTTPS (for Nginx frontend servers / load balancers)
echo "Allowing HTTP (port 80) and HTTPS (port 443)..."
sudo ufw allow http comment 'HTTP traffic for Nginx'  # Port 80/tcp
sudo ufw allow https comment 'HTTPS traffic for Nginx' # Port 443/tcp

# SIP Signaling (for Kamailio SIP Proxy servers)
# UDP is primary for SIP, TCP can be used for larger messages or transport preference.
# TLS for secure SIP.
echo "Allowing SIP signaling (ports 5060 UDP/TCP, 5061 TCP/TLS)..."
sudo ufw allow 5060/udp comment 'SIP UDP'
sudo ufw allow 5060/tcp comment 'SIP TCP'
sudo ufw allow 5061/tcp comment 'SIP TLS' # Kamailio listen=tls:0.0.0.0:5061

# RTP Media (for Asterisk Media Servers, RTPProxy)
# This is a wide range; narrow it down if possible based on rtp.conf (Asterisk)
# or RTPProxy configuration.
RTP_START_PORT=10000
RTP_END_PORT=20000
echo "Allowing RTP media (UDP ports ${RTP_START_PORT}-${RTP_END_PORT})..."
sudo ufw allow ${RTP_START_PORT}:${RTP_END_PORT}/udp comment 'RTP Media Traffic'

# WebSocket for WebRTC (for Nginx proxying to Kamailio/Backend, or direct to Kamailio)
# Kamailio listens on ws:0.0.0.0:8080 and wss:0.0.0.0:8443
# Nginx user app config proxies /ws/ to backend, which might then connect to Kamailio,
# or Nginx might proxy directly to Kamailio's WebSocket ports if they are exposed.
# Assuming these ports are on the server where Kamailio's WS/WSS listeners are (e.g. voip-proxy-01)
# or on Nginx if Nginx terminates WSS and proxies as WS.
echo "Allowing WebSocket for WebRTC (TCP ports 8080 for WS, 8443 for WSS)..."
sudo ufw allow 8080/tcp comment 'WebSocket WS for WebRTC (e.g., to Kamailio or Nginx)'
sudo ufw allow 8443/tcp comment 'WebSocket WSS for WebRTC (e.g., to Kamailio or Nginx)'

# Database (PostgreSQL - for Database Servers like db-server-01)
# Only allow access from application server IPs.
# Replace 10.0.1.0/24 with your actual application server network/IPs.
echo "Allowing PostgreSQL access (port 5432) from application server network..."
sudo ufw allow from 10.0.1.0/24 to any port 5432 proto tcp comment 'PostgreSQL from App Tier'

# Redis (for Redis Server)
# Only allow access from application server IPs.
echo "Allowing Redis access (port 6379) from application server network..."
sudo ufw allow from 10.0.1.0/24 to any port 6379 proto tcp comment 'Redis from App Tier'

# Monitoring (for Prometheus server, Node Exporters, etc.)
# Allow Prometheus server to scrape metrics from monitored hosts.
# Replace 10.0.2.0/24 with your actual monitoring network/Prometheus server IP.
echo "Allowing access for Prometheus monitoring (ports 9090, 9100, etc.)..."
# Prometheus server itself (if this machine is Prometheus)
# sudo ufw allow 9090/tcp comment 'Prometheus server UI'
# Node Exporter (on all monitored servers)
sudo ufw allow from 10.0.2.0/24 to any port 9100 proto tcp comment 'Node Exporter for Prometheus'
# Other exporter ports as needed (e.g., 9187 for postgres_exporter, 9113 for nginx_exporter)
sudo ufw allow from 10.0.2.0/24 to any port 9187 proto tcp comment 'Postgres Exporter'
sudo ufw allow from 10.0.2.0/24 to any port 9113 proto tcp comment 'Nginx Exporter'
sudo ufw allow from 10.0.2.0/24 to any port 9494 proto tcp comment 'Kamailio Exporter' # Kamailio exporter from doc
# Port 5000 for voip-backend /metrics if Prometheus scrapes Gunicorn directly on app servers
sudo ufw allow from 10.0.2.0/24 to any port 5000 proto tcp comment 'VoIP Backend Metrics'


# Rate limiting for SSH (helps prevent brute-force attacks)
echo "Enabling rate limiting for SSH..."
sudo ufw limit ssh # This is equivalent to 'limit 22/tcp'

# Enable UFW
echo "Enabling UFW firewall..."
sudo ufw enable # Use "sudo ufw --force enable" to bypass interactive prompt if needed

# Display firewall status
echo "UFW status:"
sudo ufw status verbose

echo "Firewall configuration applied."
echo "IMPORTANT: Verify connectivity, especially SSH, before disconnecting."
echo "You can check status with 'sudo ufw status numbered' and delete rules by number if needed."

# Notes:
# - This script is a template. Adjust IP addresses, networks, and ports based on your specific server roles and network architecture.
# - For servers with multiple roles (e.g., an app server also running Nginx), combine relevant rules.
# - Consider using UFW application profiles for easier management if you have many similar services.
# - For cloud environments, also leverage security groups (AWS EC2, Azure NSG) as an additional layer of network ACLs.
# - Logging: UFW logs to /var/log/ufw.log by default. The document mentions `sudo ufw logging on`.
#   Logging can be 'low', 'medium', 'high', or 'full'. 'on' usually defaults to 'low'.
sudo ufw logging on
echo "UFW logging enabled."
