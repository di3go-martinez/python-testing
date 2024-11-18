import dagger
from dagger import dag, function, object_type


@object_type
class PythonTesting:
    @function
    def container_echo(self, string_arg: str) -> dagger.Container:
        """Returns a container that echoes whatever string argument is provided"""
        return dag.container().from_("alpine:latest").with_exec(["echo", string_arg])

    @function
    async def grep_dir(self, directory_arg: dagger.Directory, pattern: str) -> str:
        """Returns lines that match a pattern in the files of the provided Directory"""
        return await (
            dag.container()
            .from_("alpine:latest")
            .with_mounted_directory("/mnt", directory_arg)
            .with_workdir("/mnt")
            .with_exec(["grep", "-R", pattern, "."])
            .stdout()
        )

    @function
    async def build_env(self, src: dagger.Directory):
        return (
            dag.container()
            .from_("ubuntu")
            .with_exec(["apt", "update"])
            .with_exec(["apt", "install", "--assume-yes", "curl"])
            .with_exec(["curl", "-LsSf", "https://astral.sh/uv/install.sh", "-o", "install.sh"])
            .with_exec(["bash", "install.sh"])
            .with_exec(["/root/.local/bin/uv", "--version"])
            .with_directory("/workdir", src)
            .with_workdir("/workdir")
            )

    @function
    async def test(self, src: dagger.Directory) -> str:
        uv_cache = dag.cache_volume("uv.lock")
        return await(
            (await self.build_env(src))
            .with_mounted_cache("/root/.cache/uv", uv_cache)
            .with_exec(["/root/.local/bin/uv", "sync", "--frozen", "--all-extras", "--dev", "--group", "test"])
            .with_exec(["/root/.local/bin/uv", "run", "pytest"])
            .stdout()
        )