from flask import Flask, jsonify, request
import docker


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, Docker Container API!'

@app.route('/containers', methods=['GET'])
def list_containers():
    client = docker.from_env()
    containers = client.containers.list()
    container_info = [{'id': c.id, 'name': c.name} for c in containers]
    return jsonify(container_info)

@app.route('/containers', methods=['POST'])
def create_container():
    try:
        client = docker.from_env()
        
        # Get container parameters from the request JSON
        data = request.get_json()
        image_name = data.get('image_name')
        container_name = data.get('container_name')
        
        # Additional container initialization options
        init_options = data.get('init_options', {})
        
        # Create the Docker container with initialization options
        container = client.containers.run(image=image_name, name=container_name, detach=True, **init_options)
        
        return jsonify({'message': 'Container created successfully', 'container_id': container.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/containers/<container_id>/stop', methods=['POST'])
def stop_container(container_id):
    try:
        client = docker.from_env()
        
        # Find the container by its ID
        container = client.containers.get(container_id)
        
        # Stop the container
        container.stop()
        
        return jsonify({'message': 'Container stopped successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/containers/<container_id>', methods=['DELETE'])
def delete_container(container_id):
    try:
        client = docker.from_env()
        
        # Find the container by its ID
        container = client.containers.get(container_id)
        
        # Remove the container (force removal if it's running)
        container.remove(force=True)
        
        return jsonify({'message': 'Container deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/images', methods=['GET'])
def list_images():
    try:
        client = docker.from_env()
        
        # Get query parameters for filtering by label
        label_filter = request.args.get('label')
        
        if label_filter:
            # Filter images by label if label parameter is provided
            images = client.images.list(filters={'label': label_filter})
        else:
            # List all images if no label filter is provided
            images = client.images.list()
        
        image_info = [{'id': image.id, 'tags': image.tags} for image in images]
        return jsonify(image_info), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/images/pull', methods=['POST'])
def pull_image():
    try:
        client = docker.from_env()
        
        # Get image parameters from the request JSON
        data = request.get_json()
        image_name = data.get('image_name')
        
        # Pull the Docker image from the registry
        client.images.pull(image_name)
        
        return jsonify({'message': 'Image pulled successfully', 'image_name': image_name}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/images/<image_id>', methods=['DELETE'])
def delete_image(image_id):
    try:
        client = docker.from_env()
        
        # Remove the image by its ID
        client.images.remove(image=image_id, force=True)
        
        return jsonify({'message': 'Image deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/volumes', methods=['GET'])
def list_volumes():
    try:
        client = docker.from_env()
        volumes = client.volumes.list()
        volume_info = [{'id': volume.id, 'name': volume.name} for volume in volumes]
        return jsonify(volume_info), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/volumes', methods=['POST'])
def create_volume():
    try:
        client = docker.from_env()
        
        # Get volume parameters from the request JSON
        data = request.get_json()
        volume_name = data.get('volume_name')
        
        # Create the Docker volume
        client.volumes.create(name=volume_name)
        
        return jsonify({'message': 'Volume created successfully', 'volume_name': volume_name}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/volumes/<volume_id>', methods=['DELETE'])
def delete_volume(volume_id):
    try:
        client = docker.from_env()
        
        # Remove the volume by its ID
        client.volumes.get(volume_id).remove(force=True)
        
        return jsonify({'message': 'Volume deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/networks', methods=['GET'])
def list_all_networks():
    try:
        client = docker.from_env()
        
        # Get query parameters for filtering by state
        state_filter = request.args.get('state')
        
        if state_filter:
            # Filter networks by state if state parameter is provided
            networks = client.networks.list(filters={'status': state_filter})
        else:
            # List all networks if no state filter is provided
            networks = client.networks.list()
        
        network_info = [{'id': network.id, 'name': network.name, 'state': network.status} for network in networks]
        return jsonify(network_info), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/networks', methods=['POST'])
def create_network():
    try:
        client = docker.from_env()
        
        # Get network parameters from the request JSON
        data = request.get_json()
        network_name = data.get('network_name')
        
        # Create the Docker network
        network = client.networks.create(network_name)
        
        return jsonify({'message': 'Network created successfully', 'network_id': network.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/networks/<network_id>', methods=['DELETE'])
def delete_network(network_id):
    try:
        client = docker.from_env()

        # Find the network by its ID
        network = client.networks.get(network_id)

        # Remove the network
        network.remove()

        return jsonify({'message': 'Network deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/containers/<container_id>/stats', methods=['GET'])
def get_container_stats(container_id):
    try:
        client = docker.from_env()
        
        # Find the container by its ID
        container = client.containers.get(container_id)
        
        # Get container statistics
        stats = container.stats(stream=False)
        
        # Extract CPU, memory, disk, and I/O metrics
        cpu_stats = stats['cpu_stats']
        memory_stats = stats['memory_stats']
        blkio_stats = stats['blkio_stats']
        
        container_stats = {
            'cpu_usage': cpu_stats['cpu_usage']['total_usage'],
            'memory_usage': memory_stats['usage'],
            'disk_stats': blkio_stats['io_service_bytes_recursive'],
        }
        
        return jsonify(container_stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
