#!/bin/bash
# cleanup_reasoning_kernel.sh

echo "🧹 Cleaning up legacy files from reasoning_kernel..."

# Services cleanup
echo "Removing unused services..."
rm -f reasoning_kernel/services/daytona_*.py
rm -f reasoning_kernel/services/hierarchical_world_model_manager.py
rm -f reasoning_kernel/services/langcache_service.py

# Cloud cleanup
echo "Removing unused cloud connectors..."
rm -f reasoning_kernel/cloud/daytona_cloud_connector.py
rm -f reasoning_kernel/cloud/redis_cloud_connector.py

# Empty directories
echo "Removing empty directories..."
rm -rf reasoning_kernel/scenarios/data/
rm -rf reasoning_kernel/monitoring/

# Prompts cleanup
echo "Removing unused prompt utilities..."
rm -f reasoning_kernel/prompts/performance_optimizer.py
rm -f reasoning_kernel/prompts/template_versioning.py

# Utils cleanup
echo "Removing unused utilities..."
rm -f reasoning_kernel/utils/reasoning_chains.py

# Models cleanup (optional - review first)
echo "Removing unused models..."
rm -f reasoning_kernel/models/annotations.py
rm -f reasoning_kernel/models/plugins.py

# Python cache cleanup
echo "Removing Python cache files..."
find reasoning_kernel -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find reasoning_kernel -name "*.pyc" -delete 2>/dev/null
find reasoning_kernel -name "*.pyo" -delete 2>/dev/null

echo "✅ Cleanup complete!"

# Show remaining structure
echo -e "\n📁 Remaining structure:"
tree -d -L 2 reasoning_kernel/ 2>/dev/null || ls -la reasoning_kernel/
