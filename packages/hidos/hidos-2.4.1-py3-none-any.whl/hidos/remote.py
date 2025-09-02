from __future__ import annotations

import os, time
from dataclasses import field, dataclass
from datetime import datetime, timedelta
from typing import Iterable, MutableMapping, TYPE_CHECKING, cast
from warnings import warn

import requests
from requests_cache import CachedSession

from .archive import Succession
from .dsi import BaseDsi, EditionId
from .history import RevisionRecord
from .util import (
    JSON_get_dict,
    JSON_get_list,
    JSON_get_str,
    JSON_list,
    LOG,
)


if TYPE_CHECKING:
    from .util import JSONType

    HTTPOptions = MutableMapping[str, str] | None
    CrudeTable = list[list[str]]


class WebApiThrottle:
    def __init__(self, name: str) -> None:
        self.name = name
        self.reset = datetime.min
        self.remaining = 0
        self.limit = 1

    def sleep(self, url: str) -> bool:
        # add a few seconds for client-server clock logic differences
        time_left = self.reset - datetime.now() + timedelta(seconds=3)
        if time_left > timedelta(0) and self.remaining >= 0:
            delay = time_left.total_seconds() / (1.0 + self.remaining)
            if self.limit > 1 and self.limit >= self.remaining:
                frac_used = (self.limit - self.remaining) / self.limit
                delay *= frac_used
            if delay > 0:
                LOG.info(f"Pausing {delay:.1f} seconds for {url}")
                time.sleep(delay)
                return True
        return False

    def record_credit(self, resp: requests.Response) -> None:
        try:
            self.remaining = 0
            self.limit = 1
            reset = str(resp.headers.get('X-RateLimit-Reset'))
            self.reset = datetime.fromtimestamp(int(reset))
            self.remaining = int(str(resp.headers.get('X-RateLimit-Remaining')))
            self.limit = int(str(resp.headers.get('X-RateLimit-Limit')))
            resource = resp.headers.get('X-RateLimit-Resource')
            time_left = self.reset - datetime.now()
            msg = f"{self.name} API credit {self.remaining}/{self.limit} until {self.reset}Z"
            if time_left > timedelta(0):
                msg += " (in {:.1f} minutes)".format(time_left.total_seconds() / 60)
            if resource:
                msg += " for " + resource
            LOG.info(msg)
        except ValueError:
            warn("Unable to parse X-RateLimit response headers from Web API")


class WebApiSession:
    def __init__(
        self,
        session: CachedSession,
        offline: bool = False,
        api_name: str = "Web",
        headers: HTTPOptions = None,
    ):
        self.session = session
        self.offline = offline
        self._throttle = WebApiThrottle(api_name)
        self.headers = headers

    def get_table(
        self,
        url: str,
        params: HTTPOptions = None,
    ) -> CrudeTable | None:
        resp = self._get(url, params)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        lines = resp.content.decode().splitlines()
        return list(line.split() for line in lines)

    def get_json(
        self,
        url: str,
        params: HTTPOptions = None,
    ) -> JSONType:
        resp = self._get(url, params)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return cast('JSONType', resp.json())

    def _get(
        self,
        url: str,
        params: HTTPOptions,
    ) -> requests.Response:
        resp = self.session.get(
            url, params=params, headers=self.headers, only_if_cached=True
        )
        if not self.offline and resp.status_code == 504:  # not cached
            self._throttle.sleep(url)
            while True:
                resp = self.session.get(
                    url, params=params, headers=self.headers, only_if_cached=False
                )
                self._throttle.record_credit(resp)
                if resp.status_code == 429 and self._throttle.sleep(url):
                    # got "too many requests" HTTP response
                    # but have now slept per X-RateLimit guidance
                    continue
                break
        return resp


@dataclass(frozen=True)
class RemoteBranchId:
    origin: str
    name: str


class GitHubWebApiClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, session: CachedSession, offline: bool):
        headers = {
            "Accept": "application/vnd.github+json",
            "Accept-Encoding": "gzip, deflate",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "hidos",
        }
        self._core_api = WebApiSession(session, offline, "GitHub Core", headers)
        self._search_api = WebApiSession(session, offline, "GitHub Search", headers)

    def get_origins(self, sha1_git: str) -> set[str]:
        return {f"https://github.com/{fn}" for fn in self._search_commits(sha1_git)}

    def get_branches(self, init_sha1_git: str) -> set[RemoteBranchId]:
        ret = set()
        for full_name in self._search_commits(init_sha1_git):
            state = self._get_default_branch(full_name)
            if state:
                ret.add(state)
        return ret

    def _search_commits(self, init_sha1_git: str) -> set[str]:
        url = self.BASE_URL + "/search/commits"
        params = {"q": "hash:" + init_sha1_git}
        jresp = self._search_api.get_json(url, params)
        ret = set()
        for it in JSON_get_list(jresp, "items"):
            full_name = JSON_get_str(it, "repository", "full_name")
            if full_name:
                ret.add(full_name)
        return ret

    def _get_default_branch(self, repo_full_name: str) -> RemoteBranchId | None:
        url = self.BASE_URL + f"/repos/{repo_full_name}"
        jresp = self._core_api.get_json(url)
        origin = "https://github.com/" + repo_full_name
        branch_name = JSON_get_str(jresp, "default_branch")
        return RemoteBranchId(origin, branch_name) if branch_name else None


@dataclass
class SWHASubgraph:
    origin_snapshots: dict[str, set[str]] = field(default_factory=dict)
    snapshot_revisions: dict[str, set[str]] = field(default_factory=dict)
    child_parents: dict[str, set[str]] = field(default_factory=dict)

    def origins(self) -> set[str]:
        return set(self.origin_snapshots.keys())

    def parse_swha_graph_row(self, row: list[str]) -> None:
        if len(row) == 2:
            (field0, field1) = row
            if field0.startswith("swh:1:snp:"):
                snaps = self.origin_snapshots.setdefault(field1, set())
                snaps.add(field0[10:])
                return
            if field0.startswith("swh:1:rev:"):
                if field1.startswith("swh:1:snp:"):
                    revs = self.snapshot_revisions.setdefault(field1[10:], set())
                    revs.add(field0[10:])
                    return
                if field1.startswith("swh:1:rev:"):
                    parents = self.child_parents.setdefault(field1[10:], set())
                    parents.add(field0[10:])
                    return
        msg = "Ignoring unrecognized Software Heritage Graph API row: {}"
        warn(msg.format(row), SyntaxWarning)


def date_undated_parents(
    dated: dict[str, datetime],
    child: RevisionRecord,
    earliest: datetime | None = None,
) -> None:
    if earliest is None:
        if child.hexsha in dated:
            earliest = dated[child.hexsha]
    else:
        if child.hexsha in dated and dated[child.hexsha] < earliest:
            earliest = dated[child.hexsha]
        else:
            dated[child.hexsha] = earliest
    for p in child.parents:
        date_undated_parents(dated, p, earliest)


class SWHAClient:
    BASE_URL = "https://archive.softwareheritage.org/api/1"

    def __init__(self, session: CachedSession, offline: bool):
        token = os.environ.get("SWHA_BEARER_TOKEN")
        headers = {"Authorization": f"Bearer {token}"} if token else None
        self._api = WebApiSession(session, offline, "SWH", headers)
        self._graph_api = self._api if headers else None

    def get_branches(self, init_sha1_git: str) -> set[RemoteBranchId]:
        ret = set()
        subgraph = self.get_subgraph(init_sha1_git)
        for origin, snapshots in subgraph.origin_snapshots.items():
            for snp_hex in snapshots:
                subgraph_revs = subgraph.snapshot_revisions.get(snp_hex, set())
                branches = self.get_snapshot_branches(snp_hex)
                for branch_name, rev in branches.items():
                    if rev in subgraph_revs:
                        ret.add(RemoteBranchId(origin, branch_name))
        return ret

    def get_origin_snapshots(self, origin: str) -> dict[datetime, str]:
        url = self.BASE_URL + f"/origin/{origin}/visits/?per_page=1024"
        jresp = self._api.get_json(url)
        bad_date = None
        ret = dict()
        for visit in JSON_list(jresp):
            snp_hex = JSON_get_str(visit, "snapshot")
            date_str = JSON_get_str(visit, "date")
            try:
                dt = datetime.fromisoformat(date_str)
            except ValueError:
                dt = None
            if snp_hex and dt:
                if dt in ret:
                    bad_date = date_str
                else:
                    ret[dt] = snp_hex
            else:
                bad_date = date_str
        if bad_date:
            msg = "Unrecognized visit format with date '{}' for origin '{}'"
            warn(msg.format(bad_date, origin), SyntaxWarning)
        return ret

    def get_snapshot_branches(self, snp_hex: str) -> dict[str, str]:
        url = self.BASE_URL + f"/snapshot/{snp_hex}/"
        jresp = self._api.get_json(url)
        ret = dict()
        for ref, props in JSON_get_dict(jresp, "branches").items():
            if ref.startswith("refs/heads/"):
                branch_name = ref[11:]
                if JSON_get_str(props, "target_type") == "revision":
                    ret[branch_name] = JSON_get_str(props, "target")
        return ret

    def get_subgraph(self, init_sha1_git: str) -> SWHASubgraph:
        table = self._swh_graph_api(
            "/graph/visit/edges",
            init_sha1_git,
            "rev:rev,rev:snp,snp:ori",
        )
        ret = SWHASubgraph()
        for row in table or []:
            ret.parse_swha_graph_row(row)
        return ret

    def _swh_graph_api(
        self, endpoint: str, sha1_git: str, edges: str
    ) -> CrudeTable | None:
        if not self._graph_api:
            return None
        url = self.BASE_URL + f"{endpoint}/swh:1:rev:{sha1_git}/"
        params = dict(
            direction="backward",
            edges=edges,
            resolve_origins="true",
        )
        return self._graph_api.get_table(url, params)


class SuccessionProvenance:
    snapshot_revisions: dict[str, set[str]]
    origin_all_visits: dict[str, dict[datetime, str]]

    def __init__(self, client: SWHAClient, dsi: BaseDsi):
        swha_subgraph = client.get_subgraph(dsi.sha1_git)
        self.snapshot_revisions = swha_subgraph.snapshot_revisions
        self.origin_all_visits = dict()
        for origin in swha_subgraph.origin_snapshots.keys():
            visits = client.get_origin_snapshots(origin)
            self.origin_all_visits[origin] = visits

    def extend_revs(self, client: SWHAClient, more_revs: Iterable[str]) -> None:
        more_revs = set(more_revs)
        for origin, visits in self.origin_all_visits.items():
            old_snapshots = set(self.snapshot_revisions.keys())
            for when, snp_hex in reversed(sorted(visits.items())):
                if snp_hex in old_snapshots:
                    break
                branches = client.get_snapshot_branches(snp_hex)
                new_revs = more_revs & set(branches.values())
                if new_revs:
                    revs = self.snapshot_revisions.setdefault(snp_hex, set())
                    revs |= new_revs

    def add_origins(self, client: SWHAClient, origins: set[str]) -> None:
        for origin in origins:
            if origin not in self.origin_all_visits:
                visits = client.get_origin_snapshots(origin)
                self.origin_all_visits[origin] = visits

    def revision_archive_dates(self) -> dict[str, datetime]:
        ret: dict[str, datetime] = dict()
        for origin, visits in self.origin_all_visits.items():
            for when, snp_hex in visits.items():
                for rev in self.snapshot_revisions.get(snp_hex, set()):
                    if rev not in ret or when < ret[rev]:
                        ret[rev] = when
        return ret


class FederatedClient:
    def __init__(self, session: CachedSession, offline: bool):
        self._swha = SWHAClient(session, offline)
        self._github = GitHubWebApiClient(session, offline)

    def get_origins(self, dsi: BaseDsi) -> set[str]:
        subgraph = self._swha.get_subgraph(dsi.sha1_git)
        ret = subgraph.origins()
        ret.update(self._github.get_origins(dsi.sha1_git))
        return ret

    def lookup_remote_branches(self, dsi: BaseDsi) -> set[RemoteBranchId]:
        ret = self._swha.get_branches(dsi.sha1_git)
        ret.update(self._github.get_branches(dsi.sha1_git))
        return ret

    def _revision_archive_dates(self, succ: Succession) -> dict[str, datetime]:
        prov = SuccessionProvenance(self._swha, succ.dsi)
        prov.add_origins(self._swha, self._github.get_origins(succ.dsi.sha1_git))
        all_revs = {r.hexsha for r in succ.all_revisions()}
        prov.extend_revs(self._swha, all_revs)
        ret = prov.revision_archive_dates()
        date_undated_parents(ret, succ.tip_rev)
        return ret

    def edition_archive_dates(
        self, succ: Succession
    ) -> dict[EditionId, datetime | None]:
        dates = self._revision_archive_dates(succ)
        ret = dict()
        for e in succ.snapshot_editions():
            if e.revision:
                ret[e.edid] = dates.get(e.revision)
        return ret
