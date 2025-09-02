from sshtunnel import SSHTunnelForwarder


def create_server_tunnel(source_credentials):
    print("Passing through SSH tunnel")
    server = SSHTunnelForwarder(
        (source_credentials["host_tunnel"], source_credentials["port_tunnel"]),
        ssh_username=source_credentials["user_tunnel"],
        ssh_pkey="data/kp-bastion-prod-pem.pem",
        remote_bind_address=(
            source_credentials["host"],
            source_credentials["port"],
        ),
        local_bind_address=("localhost", 47017),
    )

    server.start()
    print("SSH tunnel started")

    source_credentials["host"] = "localhost"
    source_credentials["port"] = 47017

    return server, source_credentials


def stop_server_tunnel(server):
    server.stop()
    print("SSH tunnel stopped")
