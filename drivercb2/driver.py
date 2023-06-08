from drivercb2.fixation import show_fixation
from py_client.remote_client import RemoteClient

if __name__ == "__main__":
    show_fixation(1)

    url = "0.0.0.0:8080"
    client = RemoteClient(url=url, lobby_name="scenario-lobby")

    connected, reason = client.Connect()
    assert connected, f"Unable to connect: {reason}"
