"""
Docker management module for creating, managing, and cleaning up Docker containers.
"""

import docker
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Tuple
from docker.models.containers import Container
from docker.models.images import Image
from ..config.settings import settings
from ..exceptions import DockerError

logger = logging.getLogger(__name__)


class DockerManager:
    """Manages Docker containers for code execution."""
    
    def __init__(self):
        """Initialize the Docker manager."""
        self._client: Optional[docker.DockerClient] = None
        self._container: Optional[Container] = None  # Single persistent container
        self._image_cache: Dict[str, Image] = {}
        self._lock = threading.Lock()
        self._connect()
    
    def _connect(self) -> None:
        """Connect to Docker daemon."""
        try:
            # Use docker.from_env() without base_url parameter
            # The docker library will automatically detect the Docker daemon
            self._client = docker.from_env(
                timeout=settings.docker["timeout"]
            )
            # Test connection
            self._client.ping()
            logger.info("Connected to Docker daemon")
        except Exception as e:
            raise DockerError(f"Failed to connect to Docker daemon: {e}")
    
    @property
    def client(self) -> docker.DockerClient:
        """Get Docker client, reconnecting if necessary."""
        if self._client is None:
            self._connect()
        return self._client
    
    def get_or_create_container(self) -> Container:
        """
        Get or create the single persistent container with all language tools.

        Returns:
            Docker container ready for code execution
        """
        with self._lock:
            # Check if container exists and is running
            if self._container is not None:
                try:
                    self._container.reload()
                    if self._container.status == "running":
                        logger.debug("Using existing persistent container")
                        return self._container
                    else:
                        # Container is not running, create new one
                        logger.info("Container stopped, creating new one")
                        self._container = None
                except Exception:
                    # Container no longer exists, create new one
                    logger.info("Container no longer exists, creating new one")
                    self._container = None

            # Create new container with all language tools
            logger.info("Creating new persistent multi-language container")
            self._container = self._create_multi_language_container()

            return self._container
    
    def _create_multi_language_container(self) -> Container:
        """
        Create a new Docker container with all language tools installed.

        Returns:
            New Docker container with multi-language support
        """
        try:
            # Use the configured image
            image_name = settings.docker["image"]

            # Ensure image exists
            self._ensure_image(image_name)

            # Simplified container configuration
            container_config = {
                "image": image_name,
                "detach": True,
                "tty": True,
                "stdin_open": True,
                "working_dir": "/workspace",
                "command": "tail -f /dev/null",  # Keep container running
                "mem_limit": settings.docker["memory_limit"],
                "network_disabled": settings.docker["network_disabled"],
                "volumes": {
                    "/workspace": {"bind": "/workspace", "mode": "rw"}
                }
            }

            print("[INFO] Creating Docker container for code execution...")
            print("[INFO] This process only happens once and may take a moment...")
            logger.info(f"Creating new lightweight container with image {image_name}")

            container = self.client.containers.run(**container_config)
            print("[SUCCESS] Container created successfully")

            # Wait for container to be ready
            print("[INFO] Waiting for container to be ready...")
            self._wait_for_container_ready(container)
            print("[SUCCESS] Container is ready")

            print("[SUCCESS] Docker container setup completed")
            return container
            
        except Exception as e:
            raise DockerError(f"Failed to create container: {e}")



    def _ensure_image(self, image_name: str) -> Image:
        """
        Ensure Docker image exists, pulling if necessary.
        
        Args:
            image_name: Docker image name
            
        Returns:
            Docker image
        """
        if image_name in self._image_cache:
            return self._image_cache[image_name]
        
        try:
            # Try to get existing image
            image = self.client.images.get(image_name)
            logger.debug(f"Found existing image: {image_name}")
        except docker.errors.ImageNotFound:
            # Pull image
            logger.info(f"Pulling Docker image: {image_name}")
            try:
                image = self.client.images.pull(image_name)
                logger.info(f"Successfully pulled image: {image_name}")
            except Exception as e:
                raise DockerError(f"Failed to pull image {image_name}: {e}")
        
        self._image_cache[image_name] = image
        return image
    
    def _wait_for_container_ready(self, container: Container, timeout: int = 60) -> None:
        """
        Wait for container to be ready for execution.

        Args:
            container: Docker container
            timeout: Maximum time to wait in seconds
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                container.reload()
                if container.status == "running":
                    # Test if we can execute commands (without timeout parameter)
                    result = container.exec_run("echo 'ready'")
                    if result.exit_code == 0:
                        logger.debug("Container is ready")
                        return
            except Exception as e:
                logger.debug(f"Container not ready yet: {e}")

            time.sleep(1.0)  # Wait a bit longer between checks

        raise DockerError(f"Container failed to become ready within {timeout} seconds")
    
    def execute_in_container(self, container: Container, command: List[str],
                           timeout: Optional[int] = None) -> Tuple[int, str, str]:
        """
        Execute command in Docker container.

        Args:
            container: Docker container
            command: Command to execute
            timeout: Execution timeout in seconds (not used in exec_run)

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        try:
            logger.debug(f"Executing command in container: {' '.join(command)}")

            # Execute command (without timeout parameter)
            result = container.exec_run(
                command,
                demux=True,
                workdir="/workspace"
            )

            exit_code = result.exit_code
            stdout = result.output[0].decode('utf-8') if result.output[0] else ""
            stderr = result.output[1].decode('utf-8') if result.output[1] else ""

            logger.debug(f"Command completed with exit code: {exit_code}")

            return exit_code, stdout, stderr

        except Exception as e:
            raise DockerError(f"Failed to execute command in container: {e}")
    
    def copy_to_container(self, container: Container, content: str, 
                         file_path: str) -> None:
        """
        Copy content to file in container.
        
        Args:
            container: Docker container
            content: File content
            file_path: Path to file in container
        """
        try:
            import tarfile
            import io
            
            # Create tar archive with file content
            tar_stream = io.BytesIO()
            tar = tarfile.TarFile(fileobj=tar_stream, mode='w')
            
            file_data = content.encode('utf-8')
            tarinfo = tarfile.TarInfo(name=file_path.lstrip('/'))
            tarinfo.size = len(file_data)
            tarinfo.mode = 0o644
            
            tar.addfile(tarinfo, io.BytesIO(file_data))
            tar.close()
            
            tar_stream.seek(0)
            
            # Copy to container
            container.put_archive("/", tar_stream.getvalue())
            
            logger.debug(f"Copied content to {file_path} in container")
            
        except Exception as e:
            raise DockerError(f"Failed to copy file to container: {e}")
    
    def cleanup_container(self) -> None:
        """Clean up the persistent container."""
        try:
            if self._container is not None:
                # Stop and remove container
                self._container.stop(timeout=5)
                self._container.remove(force=True)
                logger.info(f"Cleaned up persistent container {self._container.short_id}")
                self._container = None

        except Exception as e:
            logger.warning(f"Failed to cleanup container: {e}")
            self._container = None
    
    def cleanup_all_containers(self) -> None:
        """Clean up the persistent container (same as cleanup_container)."""
        self.cleanup_container()
    
    def get_container_stats(self) -> Dict[str, Any]:
        """Get statistics about cached containers."""
        with self._lock:
            stats = {
                "cached_containers": len(self._container_cache),
                "cached_images": len(self._image_cache),
                "containers": []
            }
            
            for key, container in self._container_cache.items():
                try:
                    container.reload()
                    stats["containers"].append({
                        "key": key,
                        "id": container.short_id,
                        "status": container.status,
                        "image": container.image.tags[0] if container.image.tags else "unknown"
                    })
                except:
                    stats["containers"].append({
                        "key": key,
                        "id": "unknown",
                        "status": "error",
                        "image": "unknown"
                    })
            
            return stats


# Global Docker manager instance
_docker_manager: Optional[DockerManager] = None


def get_docker_manager() -> DockerManager:
    """Get global Docker manager instance."""
    global _docker_manager
    if _docker_manager is None:
        _docker_manager = DockerManager()
    return _docker_manager


def rm_docker() -> None:
    """Remove all cached Docker containers."""
    manager = get_docker_manager()
    manager.cleanup_all_containers()
    logger.info("All Docker containers removed")
