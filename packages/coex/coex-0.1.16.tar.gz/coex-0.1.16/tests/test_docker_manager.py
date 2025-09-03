"""
Unit tests for the Docker manager module.
"""

import pytest
import unittest.mock as mock
from unittest.mock import Mock, MagicMock

from coex.core.docker_manager import DockerManager, get_docker_manager, rm_docker
from coex.exceptions import DockerError


class TestDockerManager:
    """Test cases for DockerManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with mock.patch('coex.core.docker_manager.docker.from_env'):
            self.manager = DockerManager()
    
    @mock.patch('coex.core.docker_manager.docker.from_env')
    def test_docker_connection(self, mock_docker):
        """Test Docker daemon connection."""
        mock_client = Mock()
        mock_docker.return_value = mock_client
        
        manager = DockerManager()
        
        mock_docker.assert_called_once()
        mock_client.ping.assert_called_once()
    
    @mock.patch('coex.core.docker_manager.docker.from_env')
    def test_docker_connection_failure(self, mock_docker):
        """Test Docker connection failure handling."""
        mock_docker.side_effect = Exception("Docker daemon not running")
        
        with pytest.raises(DockerError, match="Failed to connect to Docker daemon"):
            DockerManager()
    
    def test_get_or_create_container_cached(self):
        """Test getting container from cache."""
        # Mock existing container in cache
        mock_container = Mock()
        mock_container.status = "running"
        self.manager._container_cache["python:python:3.11-slim"] = mock_container
        
        result = self.manager.get_or_create_container("python")
        
        assert result == mock_container
        mock_container.reload.assert_called_once()
    
    def test_get_or_create_container_new(self):
        """Test creating new container when not cached."""
        mock_container = Mock()
        
        with mock.patch.object(self.manager, '_create_container') as mock_create:
            mock_create.return_value = mock_container
            
            result = self.manager.get_or_create_container("python")
            
            assert result == mock_container
            mock_create.assert_called_once_with("python", "python:3.11-slim")
    
    def test_get_or_create_container_dead_container(self):
        """Test handling of dead container in cache."""
        # Mock dead container in cache
        mock_dead_container = Mock()
        mock_dead_container.status = "exited"
        mock_dead_container.reload.return_value = None
        self.manager._container_cache["python:python:3.11-slim"] = mock_dead_container
        
        mock_new_container = Mock()
        
        with mock.patch.object(self.manager, '_create_container') as mock_create:
            mock_create.return_value = mock_new_container
            
            result = self.manager.get_or_create_container("python")
            
            assert result == mock_new_container
            # Dead container should be removed from cache
            assert "python:python:3.11-slim" not in self.manager._container_cache
    
    def test_create_container_success(self):
        """Test successful container creation."""
        mock_container = Mock()
        mock_image = Mock()
        
        with mock.patch.object(self.manager, '_ensure_image') as mock_ensure_image, \
             mock.patch.object(self.manager, '_wait_for_container_ready') as mock_wait, \
             mock.patch.object(self.manager, 'client') as mock_client:
            
            mock_ensure_image.return_value = mock_image
            mock_client.containers.run.return_value = mock_container
            
            result = self.manager._create_container("python", "python:3.11-slim")
            
            assert result == mock_container
            mock_ensure_image.assert_called_once_with("python:3.11-slim")
            mock_client.containers.run.assert_called_once()
            mock_wait.assert_called_once_with(mock_container)
    
    def test_ensure_image_cached(self):
        """Test getting image from cache."""
        mock_image = Mock()
        self.manager._image_cache["python:3.11-slim"] = mock_image
        
        result = self.manager._ensure_image("python:3.11-slim")
        
        assert result == mock_image
    
    def test_ensure_image_pull_needed(self):
        """Test pulling image when not available locally."""
        mock_image = Mock()
        
        with mock.patch.object(self.manager, 'client') as mock_client:
            # First call raises ImageNotFound, second call returns pulled image
            mock_client.images.get.side_effect = Exception("Image not found")
            mock_client.images.pull.return_value = mock_image
            
            result = self.manager._ensure_image("python:3.11-slim")
            
            assert result == mock_image
            mock_client.images.pull.assert_called_once_with("python:3.11-slim")
    
    def test_execute_in_container_success(self):
        """Test successful command execution in container."""
        mock_container = Mock()
        mock_result = Mock()
        mock_result.exit_code = 0
        mock_result.output = (b"stdout output", b"stderr output")
        mock_container.exec_run.return_value = mock_result
        
        exit_code, stdout, stderr = self.manager.execute_in_container(
            mock_container, ["python", "test.py"], timeout=30
        )
        
        assert exit_code == 0
        assert stdout == "stdout output"
        assert stderr == "stderr output"
        mock_container.exec_run.assert_called_once()
    
    def test_execute_in_container_failure(self):
        """Test command execution failure in container."""
        mock_container = Mock()
        mock_container.exec_run.side_effect = Exception("Execution failed")
        
        with pytest.raises(DockerError, match="Failed to execute command in container"):
            self.manager.execute_in_container(
                mock_container, ["python", "test.py"], timeout=30
            )
    
    def test_copy_to_container_success(self):
        """Test successful file copy to container."""
        mock_container = Mock()
        content = "print('Hello, World!')"
        file_path = "/workspace/test.py"
        
        # Should not raise exception
        self.manager.copy_to_container(mock_container, content, file_path)
        
        mock_container.put_archive.assert_called_once()
    
    def test_copy_to_container_failure(self):
        """Test file copy failure to container."""
        mock_container = Mock()
        mock_container.put_archive.side_effect = Exception("Copy failed")
        
        with pytest.raises(DockerError, match="Failed to copy file to container"):
            self.manager.copy_to_container(mock_container, "content", "/path")
    
    def test_cleanup_container(self):
        """Test container cleanup."""
        mock_container = Mock()
        mock_container.id = "container123"
        
        # Add container to cache
        self.manager._container_cache["test:image"] = mock_container
        
        self.manager.cleanup_container(mock_container)
        
        # Container should be removed from cache
        assert "test:image" not in self.manager._container_cache
        mock_container.stop.assert_called_once()
        mock_container.remove.assert_called_once()
    
    def test_cleanup_all_containers(self):
        """Test cleanup of all cached containers."""
        mock_container1 = Mock()
        mock_container1.id = "container1"
        mock_container2 = Mock()
        mock_container2.id = "container2"
        
        self.manager._container_cache = {
            "python:image1": mock_container1,
            "javascript:image2": mock_container2
        }
        
        with mock.patch.object(self.manager, 'cleanup_container') as mock_cleanup:
            self.manager.cleanup_all_containers()
            
            assert len(self.manager._container_cache) == 0
            assert mock_cleanup.call_count == 2
    
    def test_get_container_stats(self):
        """Test getting container statistics."""
        mock_container = Mock()
        mock_container.short_id = "abc123"
        mock_container.status = "running"
        mock_container.image.tags = ["python:3.11-slim"]
        
        self.manager._container_cache["python:image"] = mock_container
        self.manager._image_cache["python:3.11-slim"] = Mock()
        
        stats = self.manager.get_container_stats()
        
        assert stats["cached_containers"] == 1
        assert stats["cached_images"] == 1
        assert len(stats["containers"]) == 1
        assert stats["containers"][0]["id"] == "abc123"
        assert stats["containers"][0]["status"] == "running"
    
    def test_wait_for_container_ready_success(self):
        """Test waiting for container to become ready."""
        mock_container = Mock()
        mock_container.status = "running"
        mock_result = Mock()
        mock_result.exit_code = 0
        mock_container.exec_run.return_value = mock_result
        
        # Should not raise exception
        self.manager._wait_for_container_ready(mock_container, timeout=5)
        
        mock_container.reload.assert_called()
        mock_container.exec_run.assert_called()
    
    def test_wait_for_container_ready_timeout(self):
        """Test timeout when waiting for container to become ready."""
        mock_container = Mock()
        mock_container.status = "starting"  # Never becomes ready
        
        with pytest.raises(DockerError, match="Container failed to become ready"):
            self.manager._wait_for_container_ready(mock_container, timeout=1)


class TestDockerManagerFunctions:
    """Test cases for module-level Docker manager functions."""
    
    @mock.patch('coex.core.docker_manager.DockerManager')
    def test_get_docker_manager_singleton(self, mock_docker_manager_class):
        """Test that get_docker_manager returns singleton instance."""
        mock_instance = Mock()
        mock_docker_manager_class.return_value = mock_instance
        
        # Clear any existing instance
        import coex.core.docker_manager
        coex.core.docker_manager._docker_manager = None
        
        # First call should create instance
        result1 = get_docker_manager()
        assert result1 == mock_instance
        mock_docker_manager_class.assert_called_once()
        
        # Second call should return same instance
        result2 = get_docker_manager()
        assert result2 == mock_instance
        # Should not create new instance
        mock_docker_manager_class.assert_called_once()
    
    @mock.patch('coex.core.docker_manager.get_docker_manager')
    def test_rm_docker_function(self, mock_get_manager):
        """Test rm_docker function."""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager
        
        rm_docker()
        
        mock_get_manager.assert_called_once()
        mock_manager.cleanup_all_containers.assert_called_once()


class TestDockerManagerEdgeCases:
    """Test cases for Docker manager edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with mock.patch('coex.core.docker_manager.docker.from_env'):
            self.manager = DockerManager()
    
    def test_unsupported_language(self):
        """Test handling of unsupported language."""
        with pytest.raises(DockerError, match="Unsupported language"):
            self.manager.get_or_create_container("unsupported_language")
    
    def test_container_cache_corruption(self):
        """Test handling of corrupted container cache."""
        # Add invalid container to cache
        mock_container = Mock()
        mock_container.reload.side_effect = Exception("Container no longer exists")
        self.manager._container_cache["python:image"] = mock_container
        
        mock_new_container = Mock()
        with mock.patch.object(self.manager, '_create_container') as mock_create:
            mock_create.return_value = mock_new_container
            
            result = self.manager.get_or_create_container("python")
            
            # Should create new container and clean up cache
            assert result == mock_new_container
            assert "python:image" not in self.manager._container_cache
    
    def test_image_pull_failure(self):
        """Test handling of image pull failure."""
        with mock.patch.object(self.manager, 'client') as mock_client:
            mock_client.images.get.side_effect = Exception("Image not found")
            mock_client.images.pull.side_effect = Exception("Pull failed")
            
            with pytest.raises(DockerError, match="Failed to pull image"):
                self.manager._ensure_image("nonexistent:image")
    
    def test_container_creation_with_custom_image(self):
        """Test container creation with custom Docker image."""
        mock_container = Mock()
        
        with mock.patch.object(self.manager, '_create_container') as mock_create:
            mock_create.return_value = mock_container
            
            result = self.manager.get_or_create_container("python", "custom:image")
            
            assert result == mock_container
            mock_create.assert_called_once_with("python", "custom:image")


if __name__ == "__main__":
    pytest.main([__file__])
