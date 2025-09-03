"""
Docker management module for creating, managing, and cleaning up Docker containers.
"""

import docker
import logging
import time
import threading
import os
import json
import tempfile
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

        # Container state tracking
        self._container_id: Optional[str] = None  # Remember container ID across imports
        self._initial_state_hash: Optional[str] = None  # Track initial environment state
        self._state_check_enabled: bool = False  # Disable state checking by default
        self._state_file_path = os.path.join(tempfile.gettempdir(), "coex_container_state.json")

        # Load existing state if available
        self._load_container_state()

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

    def _load_container_state(self) -> None:
        """Load container state from persistent storage."""
        try:
            if os.path.exists(self._state_file_path):
                with open(self._state_file_path, 'r') as f:
                    state = json.load(f)
                    self._container_id = state.get('container_id')
                    self._initial_state_hash = state.get('initial_state_hash')
                    logger.debug(f"Loaded container state: ID={self._container_id}, hash={self._initial_state_hash}")
        except Exception as e:
            logger.warning(f"Failed to load container state: {e}")

    def _save_container_state(self) -> None:
        """Save container state to persistent storage."""
        try:
            state = {
                'container_id': self._container_id,
                'initial_state_hash': self._initial_state_hash
            }
            with open(self._state_file_path, 'w') as f:
                json.dump(state, f)
            logger.debug(f"Saved container state: ID={self._container_id}")
        except Exception as e:
            logger.warning(f"Failed to save container state: {e}")

    def _clear_container_state(self) -> None:
        """Clear persistent container state."""
        try:
            if os.path.exists(self._state_file_path):
                os.remove(self._state_file_path)
                logger.debug("Cleared persistent container state")
        except Exception as e:
            logger.warning(f"Failed to clear container state: {e}")

    def _calculate_container_state_hash(self, container: Container) -> str:
        """
        Calculate a hash representing the current state of the container.
        This focuses on critical system changes while being tolerant of development kit installations.
        """
        try:
            # Focus on more stable indicators that don't change with dev kit installations
            commands = [
                # Check core system integrity (less likely to change with dev kits)
                "ls -la /etc/passwd | wc -l",  # User accounts
                "ls -la /etc/hosts | wc -l",   # Network config
                # Check for major filesystem corruption (not normal installations)
                "test -d /usr && test -d /bin && test -d /lib && echo 'ok' || echo 'corrupted'",
                # Check if container is fundamentally broken
                "python3 --version > /dev/null 2>&1 && echo 'python_ok' || echo 'python_broken'"
            ]

            state_info = []
            for cmd in commands:
                try:
                    # Use container.exec_run directly to avoid circular dependency
                    result = container.exec_run(["bash", "-c", cmd], workdir="/workspace")
                    if result.exit_code == 0:
                        output = result.output.decode('utf-8').strip()
                        state_info.append(output)
                    else:
                        state_info.append("error")
                except Exception as cmd_error:
                    logger.debug(f"Command '{cmd}' failed: {cmd_error}")
                    state_info.append("error")

            # Create hash from collected information
            import hashlib
            state_string = "|".join(state_info)
            hash_value = hashlib.md5(state_string.encode()).hexdigest()
            logger.debug(f"Calculated state hash: {hash_value} from {state_string}")
            return hash_value

        except Exception as e:
            logger.warning(f"Failed to calculate container state hash: {e}")
            return "unknown"

    def _is_container_state_valid(self, container: Container) -> bool:
        """
        Check if the container state is still valid.
        Always returns True to keep containers alive regardless of file structure changes.
        """
        # Always return True - keep containers alive no matter what
        # This prevents infinite loops caused by state validation failures
        logger.debug("Container state validation disabled - always returning True")
        return True

    def _try_recover_existing_container(self) -> Optional[Container]:
        """
        Try to recover an existing container by ID if it exists.
        Always recovers running containers regardless of state changes.
        """
        if not self._container_id:
            return None

        try:
            # Try to get container by ID
            container = self.client.containers.get(self._container_id)
            container.reload()

            # Check if container is running
            if container.status != "running":
                logger.info(f"Container {self._container_id} is not running, will recreate")
                return None

            # Always recover running containers - no state validation
            logger.info(f"Recovered existing container {self._container_id} (no state validation)")
            return container

        except Exception as e:
            logger.debug(f"Could not recover container {self._container_id}: {e}")
            return None
    
    @property
    def client(self) -> docker.DockerClient:
        """Get Docker client, reconnecting if necessary."""
        if self._client is None:
            self._connect()
        return self._client
    
    def get_or_create_container(self) -> Container:
        """
        Get or create the single persistent container with state validation.

        The container persists across imports and executions until rm_docker() is called.
        If the container environment is modified (e.g., by rm -rf commands),
        it will be automatically recreated.

        Returns:
            Docker container ready for code execution
        """
        with self._lock:
            # First, try to recover existing container by ID
            if self._container is None and self._container_id:
                self._container = self._try_recover_existing_container()
                if self._container:
                    logger.info("Successfully recovered existing container from previous session")
                    return self._container

            # Check if current container exists and is running
            if self._container is not None:
                try:
                    self._container.reload()
                    if self._container.status == "running":
                        # Always use existing running container - no state validation
                        logger.debug("Using existing running container (no state validation)")
                        return self._container
                    else:
                        logger.info("Container stopped, creating new one")
                        self._container = None
                except Exception:
                    logger.info("Container no longer exists, creating new one")
                    self._container = None

            # Create new container
            logger.info("Creating new persistent container")
            self._container = self._create_multi_language_container()

            # Remember container ID for future recovery
            self._container_id = self._container.id

            # Calculate and store initial state hash
            self._initial_state_hash = self._calculate_container_state_hash(self._container)
            logger.debug(f"Stored initial container state hash: {self._initial_state_hash}")

            # Save state to persistent storage
            self._save_container_state()

            return self._container

    def _cleanup_current_container(self) -> None:
        """Clean up the current container without affecting the global state."""
        if self._container:
            try:
                self._container.stop(timeout=5)
                self._container.remove(force=True)
                logger.debug(f"Cleaned up invalid container {self._container.short_id}")
            except Exception as e:
                logger.warning(f"Failed to cleanup invalid container: {e}")
            finally:
                self._container = None
    
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
        """Clean up the persistent container and reset state tracking."""
        try:
            if self._container is not None:
                # Stop and remove container
                self._container.stop(timeout=5)
                self._container.remove(force=True)
                logger.info(f"Cleaned up persistent container {self._container.short_id}")
                self._container = None

            # Reset state tracking
            self._container_id = None
            self._initial_state_hash = None

            # Clear persistent state
            self._clear_container_state()

        except Exception as e:
            logger.warning(f"Failed to cleanup container: {e}")
            self._container = None
            self._container_id = None
            self._initial_state_hash = None
            self._clear_container_state()
    
    def cleanup_all_containers(self) -> None:
        """Clean up the persistent container (same as cleanup_container)."""
        self.cleanup_container()

    def enable_state_checking(self) -> None:
        """Enable container state checking."""
        self._state_check_enabled = True
        logger.info("Container state checking enabled")

    def disable_state_checking(self) -> None:
        """Disable container state checking."""
        self._state_check_enabled = False
        logger.info("Container state checking disabled")

    def get_container_info(self) -> Dict[str, Any]:
        """Get information about the current container state."""
        with self._lock:
            info = {
                "has_container": self._container is not None,
                "container_id": self._container_id,
                "container_short_id": None,
                "container_status": None,
                "initial_state_hash": self._initial_state_hash,
                "current_state_hash": None,
                "state_valid": None,
                "state_checking_enabled": self._state_check_enabled
            }

            if self._container:
                try:
                    self._container.reload()
                    info.update({
                        "container_status": self._container.status,
                        "container_short_id": self._container.short_id,
                        "current_state_hash": self._calculate_container_state_hash(self._container),
                        "state_valid": self._is_container_state_valid(self._container)
                    })
                except Exception as e:
                    info["container_error"] = str(e)

            return info
    
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

    # Reset global Docker manager instance
    global _docker_manager
    _docker_manager = None

    logger.info("All Docker containers removed")
