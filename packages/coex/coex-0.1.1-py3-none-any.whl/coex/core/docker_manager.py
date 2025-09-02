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
        self._container_cache: Dict[str, Container] = {}
        self._image_cache: Dict[str, Image] = {}
        self._lock = threading.Lock()
        self._connect()
    
    def _connect(self) -> None:
        """Connect to Docker daemon."""
        try:
            self._client = docker.from_env(
                base_url=settings.docker["base_url"],
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
    
    def get_or_create_container(self, language: str, image_name: Optional[str] = None) -> Container:
        """
        Get existing container from cache or create a new one.
        
        Args:
            language: Programming language
            image_name: Optional custom Docker image name
            
        Returns:
            Docker container ready for code execution
        """
        with self._lock:
            # Determine image name
            if image_name is None:
                lang_config = settings.languages.get(language.lower())
                if not lang_config:
                    raise DockerError(f"Unsupported language: {language}")
                image_name = lang_config["image"]
            
            # Check cache for existing container
            cache_key = f"{language}:{image_name}"
            if cache_key in self._container_cache:
                container = self._container_cache[cache_key]
                try:
                    # Check if container is still running
                    container.reload()
                    if container.status == "running":
                        logger.debug(f"Using cached container for {language}")
                        return container
                    else:
                        # Remove dead container from cache
                        del self._container_cache[cache_key]
                        try:
                            container.remove(force=True)
                        except:
                            pass
                except:
                    # Container no longer exists
                    del self._container_cache[cache_key]
            
            # Create new container
            container = self._create_container(language, image_name)
            self._container_cache[cache_key] = container
            
            return container
    
    def _create_container(self, language: str, image_name: str) -> Container:
        """
        Create a new Docker container.
        
        Args:
            language: Programming language
            image_name: Docker image name
            
        Returns:
            New Docker container
        """
        try:
            # Ensure image exists
            self._ensure_image(image_name)
            
            # Container configuration
            container_config = {
                "image": image_name,
                "detach": True,
                "tty": True,
                "stdin_open": True,
                "working_dir": "/workspace",
                "command": "/bin/bash",
                "mem_limit": settings.docker["memory_limit"],
                "cpu_quota": int(float(settings.docker["cpu_limit"]) * 100000),
                "cpu_period": 100000,
                "network_disabled": settings.docker["network_disabled"],
                "security_opt": ["no-new-privileges:true"],
                "cap_drop": ["ALL"],
                "cap_add": ["CHOWN", "DAC_OVERRIDE", "FOWNER", "SETGID", "SETUID"],
                "read_only": False,
                "tmpfs": {"/tmp": "noexec,nosuid,size=100m"},
                "volumes": {
                    "/workspace": {"bind": "/workspace", "mode": "rw"}
                }
            }
            
            logger.info(f"Creating new container for {language} with image {image_name}")
            container = self.client.containers.run(**container_config)
            
            # Wait for container to be ready
            self._wait_for_container_ready(container)
            
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
    
    def _wait_for_container_ready(self, container: Container, timeout: int = 30) -> None:
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
                    # Test if we can execute commands
                    result = container.exec_run("echo 'ready'", timeout=5)
                    if result.exit_code == 0:
                        logger.debug("Container is ready")
                        return
            except Exception:
                pass
            
            time.sleep(0.5)
        
        raise DockerError(f"Container failed to become ready within {timeout} seconds")
    
    def execute_in_container(self, container: Container, command: List[str], 
                           timeout: Optional[int] = None) -> Tuple[int, str, str]:
        """
        Execute command in Docker container.
        
        Args:
            container: Docker container
            command: Command to execute
            timeout: Execution timeout in seconds
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if timeout is None:
            timeout = settings.execution["timeout"]
        
        try:
            logger.debug(f"Executing command in container: {' '.join(command)}")
            
            # Execute command
            result = container.exec_run(
                command,
                timeout=timeout,
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
    
    def cleanup_container(self, container: Container) -> None:
        """
        Clean up container resources.
        
        Args:
            container: Docker container to cleanup
        """
        try:
            # Remove from cache
            cache_key_to_remove = None
            for key, cached_container in self._container_cache.items():
                if cached_container.id == container.id:
                    cache_key_to_remove = key
                    break
            
            if cache_key_to_remove:
                del self._container_cache[cache_key_to_remove]
            
            # Stop and remove container
            if settings.docker["remove_containers"]:
                container.stop(timeout=5)
                container.remove(force=True)
                logger.debug("Container cleaned up and removed")
            
        except Exception as e:
            logger.warning(f"Failed to cleanup container: {e}")
    
    def cleanup_all_containers(self) -> None:
        """Clean up all cached containers."""
        with self._lock:
            containers_to_cleanup = list(self._container_cache.values())
            self._container_cache.clear()
            
            for container in containers_to_cleanup:
                try:
                    self.cleanup_container(container)
                except Exception as e:
                    logger.warning(f"Failed to cleanup container {container.id}: {e}")
            
            logger.info("All containers cleaned up")
    
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
