FROM ubuntu:20.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Samba and dependencies
RUN apt-get update && \
    apt-get install -y \
        samba \
        samba-dsdb-modules \
        samba-vfs-modules \
        winbind \
        libpam-winbind \
        libnss-winbind \
        krb5-kdc \
        libpam-krb5 \
        dnsutils \
        netcat \
        ldap-utils \
        coreutils \
        supervisor && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create directories
RUN mkdir -p /var/log/supervisor /var/run/supervisor /var/lib/samba /etc/samba

# Copy configuration files
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose LDAP ports
EXPOSE 389 636

VOLUME ["/var/lib/samba", "/etc/samba"]

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]