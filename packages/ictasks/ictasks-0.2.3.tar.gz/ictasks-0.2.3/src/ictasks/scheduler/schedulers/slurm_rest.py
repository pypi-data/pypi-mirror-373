import argparse
import urllib.request


class SlurmRestClient:
    def __init__(self, username: str, endpoint: str, token: str) -> None:
        self.username = username
        self.endpoint = endpoint
        self.token = token

    def ping(self):
        print("hitting: ", self.endpoint)
        req = urllib.request.Request(url=f"{self.endpoint}/ping", method="GET")
        req.add_header("X-SLURM-USER-NAME", self.username)
        req.add_header("X-SLURM-USER-TOKEN", self.token)

        try:
            response = urllib.request.urlopen(req)
            content = response.read()
            content = content.decode("utf-8")
            print(content)
        except urllib.error.HTTPError as e:
            print(e)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--username", type=str)
    parser.add_argument("--endpoint", type=str)
    parser.add_argument("--token", type=str)

    args = parser.parse_args()
    client = SlurmRestClient(args.username, args.endpoint, args.token)
    client.ping()
