from ... import auth

try:
    from langchain_core.runnables import RunnableConfig
    from langgraph.pregel.remote import RemoteGraph  # type: ignore
except ModuleNotFoundError as err:
    import textwrap

    note = textwrap.dedent("""
        Install imandra with the optional 'universe' dependency to enable imandra.u.agents

            pip install 'imandra[universe]>=2.0.0'
        """)
    raise ModuleNotFoundError(note) from err


def get_remote_graph(
    agent_name: str,
    api_key=None,
    scheme=None,
    host=None,
    api_version=None,
) -> RemoteGraph:
    """Create a RemoteGraph via Imandra Universe."""
    c = auth.Config(api_key=api_key, scheme=scheme, host=host, api_version=api_version)
    url = f"{c.get_url()}/agents/{agent_name}"

    config = RunnableConfig(configurable={})

    remote_graph = RemoteGraph(
        agent_name,
        url=url,
        headers=c.get_headers(),
        config=config,
    )

    return remote_graph


def create_thread_sync(remote_graph: RemoteGraph):
    """Create a thread and configure the RemoteGraph to use it."""
    if remote_graph.sync_client is not None and remote_graph.config is not None:
        thread = remote_graph.sync_client.threads.create()
        remote_graph.config.setdefault("configurable", {})["thread_id"] = thread[
            "thread_id"
        ]
