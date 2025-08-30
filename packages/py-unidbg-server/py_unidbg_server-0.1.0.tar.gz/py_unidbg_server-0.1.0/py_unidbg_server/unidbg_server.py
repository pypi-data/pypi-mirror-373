from pathlib import Path
import os
import json
import jpype
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

logger = logging.getLogger("unidbg-server")

# ------------------ JVM Management ------------------
class JVMManager:
    _jvm_started = False
    _loaded_projects = set() # Set of loaded JAR paths (absolute paths)

    CORE_DIR = None
    PROJECTS_DIR = None

    @classmethod
    def start_jvm(cls):
        """Start the JVM and load core JAR files."""
        if not cls._jvm_started:
            core_jars = list(cls.CORE_DIR.glob("*.jar"))
            if not core_jars:
                raise RuntimeError(f"No core JARs found. Please ensure {cls.CORE_DIR} contains JAR files.")

            classpath = [str(j) for j in core_jars]

            jvm_args = [
                "-ea",
                # Ensure JVM loads correctly on JDK9+
                "--add-opens=java.base/java.util=ALL-UNNAMED",
                "--add-opens=java.base/java.lang=ALL-UNNAMED",
                "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED",
                "--add-opens=java.base/java.io=ALL-UNNAMED",
                "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED",
            ]
            jpype.startJVM(
                jpype.getDefaultJVMPath(),
                *jvm_args,
                classpath=classpath
            )
            cls._jvm_started = True
            logger.debug(f"✅ JVM started. {len(core_jars)} core JAR(s) loaded.")

    @classmethod
    def load_project_jar(cls, project_name: str):
        """Dynamically load project dependency JARs and main JAR."""
        project_dir = cls.PROJECTS_DIR / project_name
        if project_dir.exists() and project_dir.is_dir():
            for dep in project_dir.rglob("*.jar"):
                if str(dep) not in cls._loaded_projects:
                    jpype.addClassPath(str(dep))
                    cls._loaded_projects.add(str(dep))
                    logger.debug(f"🔗 Loaded project dependency JAR: {dep}")
        else:
            raise FileNotFoundError(f"Project not found: {project_dir}")

# ------------------ Java Method Invocation ------------------
def call_java_method(project_name: str, class_name: str, data_dict_json: str):
    """Call a Java method in the specified project."""
    JVMManager.start_jvm()
    JVMManager.load_project_jar(project_name)
    project_dir = JVMManager.PROJECTS_DIR / project_name
    os.chdir(project_dir) # Ensure relative paths work
    Java_class = jpype.JClass(class_name)
    return str(Java_class.start(data_dict_json))

# ------------------ ASGI App Factory ------------------
def create_app(base_dir=None, core_dir=None, projects_dir=None):
    # Determine the base directory: CLI uses cwd(), direct script uses file path
    base_dir = Path(base_dir or Path.cwd())

    app = FastAPI(title="Unidbg JVM Microservice")
    app.state.CORE_DIR = base_dir / (core_dir or "unidbg_core")
    app.state.PROJECTS_DIR = base_dir / (projects_dir or "projects")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        JVMManager.CORE_DIR = app.state.CORE_DIR
        JVMManager.PROJECTS_DIR = app.state.PROJECTS_DIR
        logger.info("🚀 FastAPI service started")
        try:
            yield
        finally:
            if JVMManager._jvm_started:
                jpype.shutdownJVM()
                logger.info("🛑 JVM safely shutdown")

    app.router.lifespan_context = lifespan

    class JavaRequest(BaseModel):
        project: str
        class_name: str
        data: dict

    @app.post("/call-java")
    def call_java(req: JavaRequest):
        try:
            result = call_java_method(
                req.project,
                req.class_name,
                json.dumps(req.data, ensure_ascii=False),
            )
            logger.debug(result)
            return {"result": result}
        except Exception as e:
            logger.exception("Error calling Java method")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/health")
    def health_check():
        data = {
            "status": "ok",
            "jvm_started": JVMManager._jvm_started,
            "loaded_projects": list(JVMManager._loaded_projects),
        }
        logger.debug(data)
        return data

    return app

if __name__ == "__main__":
    import subprocess

    host = "0.0.0.0"
    port = 8888
    workers = 1

    log_file = ""
    log_level = "DEBUG"

    if os.name == "nt":
        # Windows: use Uvicorn single-process
        import uvicorn
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        uvicorn.run("py_unidbg_server.unidbg_server:create_app", host=host, port=port, workers=1, factory=True)
    else:
        # Gunicorn 命令
        gunicorn_cmd = [
            "gunicorn",
            "-k", "uvicorn.workers.UvicornWorker",
            "-w", str(workers),
            "-b", f"{host}:{port}",
            "--log-level", log_level.lower(),
            "--access-logfile", "-",                   # stdout
            "--error-logfile", log_file if log_file else "-",  # error log
            "py_unidbg_server.unidbg_server:create_app"
        ]
        subprocess.run(gunicorn_cmd)
