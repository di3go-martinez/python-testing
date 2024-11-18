import dagger
from dagger import dag, function, object_type


@object_type
class PythonTesting:
    @function
    async def build_env(self, src: dagger.Directory):
        uv_cache = dag.cache_volume("uv.lock")
        return (
            dag.container()
            .from_("ubuntu")
            .with_exec(["apt", "update"])
            .with_exec(["apt", "install", "--assume-yes", "curl"])
            .with_exec(
                ["curl", "-LsSf", "https://astral.sh/uv/install.sh", "-o", "install.sh"]
            )
            .with_exec(["bash", "install.sh"])
            .with_exec(["/root/.local/bin/uv", "--version"])
            .with_mounted_cache("/root/.cache/uv", uv_cache)
            # TODO copy only pyproject.toml y uv.lock for honoring cache
            .with_directory("/workdir", src)
            .with_workdir("/workdir")
            .with_exec(
                [
                    "/root/.local/bin/uv",
                    "sync",
                    "--frozen",
                    "--all-extras",
                    "--dev",
                    "--group",
                    "lint",
                    "--group",
                    "test"
                ]
            )
        )

    @function
    async def test(self, src: dagger.Directory) -> str:
        return await (
            (await self.build_env(src))
            .with_exec(["/root/.local/bin/uv", "run", "pytest"])
            .stdout()
        )

    @function
    async def lint(self, src: dagger.Directory) -> str:
        return await (
            (await self.build_env(src))
            .with_exec(["/root/.local/bin/uv", "run", "ruff", "check", "."])
            .stdout()
        )
