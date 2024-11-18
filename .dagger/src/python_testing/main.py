import dagger
from dagger import dag, function, object_type


@object_type
class PythonTesting:
    @function
    async def build_env(self, src: dagger.Directory):
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
            .with_mounted_cache("/root/.cache/uv", dag.cache_volume("uv.lock"))
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
    def spin_pg(self) -> dagger.Service:
        return (
            dag.container()
            .from_("postgres:17.1-alpine")
            .with_exposed_port(5432)
            .with_env_variable("POSTGRES_PASSWORD", "test")
            .as_service()
        )

    @function
    async def test_dagger_way(self, src: dagger.Directory) -> str:
        """Runs tests with preconfigured services (like db). Turn off test containers inside the target configuration"""
        return await (
            (await self.build_env(src))
            .with_service_binding("pg", self.spin_pg())
            .with_env_variable("DB_HOST", "pg")
            .with_env_variable("DB_USERNAME", "postgres")
            .with_env_variable("DB_PASSWORD", "test")
            .with_env_variable("DB_NAME", "postgres")
            .with_env_variable("USE_TESTCONTAINERS", "False")
            .with_exec(["/root/.local/bin/uv", "run", "pytest"])
            .stdout()
        )

    @function
    async def test_testcontainers_way(self, src: dagger.Directory) -> str:
        """Runs tests with testcontainers compatibility """
        built_container : dagger.Container = await self.build_env(src)
        return await (
            dag.testcontainers().setup(built_container)
            #.with_env_variable("USE_TESTCONTAINERS", "True")
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
