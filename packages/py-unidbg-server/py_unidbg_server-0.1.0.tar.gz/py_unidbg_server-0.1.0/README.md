## py_unidbg_server

`py_unidbg_server` is a Python-based JVM microservice that uses **jpype1** to invoke Java methods from `.jar` files. It runs a **FastAPI** service via **Gunicorn + Uvicorn** for local calls.
The architecture is designed as a **per-machine self-contained deployment**, intended to be configured and run on the same machine as the client. By default, it does **not rely on message queues (MQ)—clients** can directly call the service locally.
In this way, the service can be combined with the machine’s original program as a **single complete project**, supporting **one-click packaging and easy deployment** without the extra configuration required by MQ-based solutions.

**Advantages over the GitHub `unidbg-server` project:**
1.Pure **Python** code – no need to dive into **Java Spring Boot**. You only need to build your unidbg project and expose the interfaces; the microservice can integrate directly.
2.**Infinite scalability** per launch – once the core unidbg libraries are loaded, new project interfaces only need their own JARs. You do not need to restart the service.

## 📦 Installation
#### From PyPI

```bash
pip install py_unidbg_server
```

#### From source
```bash
git clone https://github.com/aFunnyStrange/py_unidbg_server.git
cd py_unidbg_server
pip install -e .
```

## 🚀 Quick Start
The CLI script `unidbg-server` allows easy startup without needing underscores:
```bash
unidbg-server start
```

**Notes:**
- JAR dependencies are loaded lazily: only on the first method call.
- Once loaded, they are reused indefinitely.
- To avoid memory growth, ensure your Java code calls .destroy() after each execution if necessary.

## ⚙️ Advanced Usage
If you want to customize the microservice, you can copy the core server code to your current directory:
```bash
unidbg-server edit
```
You can then modify the code freely for your local deployment.

## 🧪 Demo Project
See [`demo/`](https://github.com/aFunnyStrange/py_unidbg_server/tree/main/tests/demo) for an example project.

**CLI Parameters:**
When starting the server, the following arguments control where JARs are loaded from:

`-c, --core:` Directory containing **core JAR files** (default: `unidbg_core`, relative to current directory). These are the core libraries needed for unidbg execution.

`-p, --projects:` Directory containing **project JAR files** (default: `projects`, relative to current directory). Any subdirectory inside this folder will be recursively loaded, so you do not need to place all JARs in the root.

**Behavior:**
The service **does not load JARs immediately** upon startup.
JARs are loaded **lazily on first method invocation**, and then **cached and reused** for all subsequent calls.

**Recommended workflow:**
1.Download and package all unidbg core JARs.

2.(Optional) Download additional dependencies such as **Gson** if your Java methods require JSON serialization/deserialization.

- **GitHub repository:** https://github.com/google/gson

- **Maven Central:** https://mvnrepository.com/artifact/com.google.code.gson/gson

- **How to get the JAR:**
    1.Check the GitHub releases to find the latest version.

    2.Go to the Maven Central page and select the desired version.

    3.If the version is not listed on the page, you can directly modify the URL to download it, e.g.:
    ```bash
    https://repo1.maven.org/maven2/com/google/code/gson/gson/<version>/gson-<version>.jar
    ```

    4.Download the JAR and place it in your project folder.

    5.Add Gson to your project (Maven example):
    ``` xml
    <dependencies>
        <dependency>
            <groupId>com.google.code.gson</groupId>
            <artifactId>gson</artifactId>
            <version>2.10.1</version>
        </dependency>
    </dependencies>
    ```

- **Purpose:** Gson is used for serializing and deserializing data when making requests to the microservice.

- If your data contains raw bytes, you can encode them with Base64 or other encoding methods.

- JSON is optional – you may choose another request format as long as the client and server agree on it.

3.Create your own project, implement Java methods, and package your JAR (without core dependencies).

4.Start the server via the CLI and make requests.

**Notes:**
The microservice is intentionally simple – it only provides a JVM execution environment and HTTP API for Java method calls.

Documentation is minimal; for building Java projects, simply follow your IDE's packaging workflow (e.g., IntelliJ IDEA). 

For reference on packaging steps, you can also check the [`docs/`](https://github.com/aFunnyStrange/py_unidbg_server/tree/main/docs/) directory included in this repository.

## 📄 License
This project is licensed under the **BSD 3-Clause License**. 