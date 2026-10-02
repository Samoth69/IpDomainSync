import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
import ovh
import requests

load_dotenv()

ovh_client = ovh.Client()
zone = os.getenv("OVH_ZONE_NAME")
subDomain = os.getenv("OVH_SUBDOMAIN")


def get_zone_subdomain_ip() -> tuple(int, str):
    res: List[str] = ovh_client.get(
        f"/domain/zone/{zone}/record?fieldType=A&subDomain={subDomain}"
    )
    if len(res) <= 0:
        raise RuntimeError(f"No record found for {zone}")

    record_id = res[0]
    res: Dict[str, Any] = ovh_client.get(f"/domain/zone/{zone}/record/{record_id}")
    return record_id, str(res["target"]).strip()


def get_current_ipv4() -> str:
    requests.packages.urllib3.util.connection.HAS_IPV6 = False

    res = requests.get("https://ifconfig.co/ip")
    res.raise_for_status()
    return str(res.text).strip()


def update_zone_subdomain_ip(record_id: int, new_ip: str):
    ovh.put(
        f"/domain/zone/{zone}/record/{record_id}",
        subDomain=subDomain,
        target=new_ip,
        ttl=int(os.getenv("OVH_SUBDOMAIN_TTL")),
    )
    ovh.post(f"/domain/zone/{zone}/refresh")


def main():
    record_id, subdomain = get_zone_subdomain_ip()
    current = get_current_ipv4()
    print(f"current ip for {os.getenv("OVH_SUBDOMAIN")}.{zone}: {subdomain}")
    print(f"current internet ip: {current}")
    if subdomain != current:
        print("update is needed")
        update_zone_subdomain_ip(record_id, current)
    else:
        print("domain is up to date, nothing to be done here")
    print("good bye")


if __name__ == "__main__":
    main()
