#!/bin/bash

# Script to move the strands-mcp-server project out of dotfiles repo
# and set up as its own git repository

echo "Moving strands-mcp-server to ~/dev/python/strands-mcp-server..."

# Create target directory
mkdir -p ~/dev/python

# Copy project files (excluding .git)
rsync -av --exclude='.git' . ~/dev/python/strands-mcp-server/

echo "Project copied to ~/dev/python/strands-mcp-server"
echo ""
echo "Next steps:"
echo "1. cd ~/dev/python/strands-mcp-server"
echo "2. git init"
echo "3. git add ."
echo "4. git commit -m 'Initial commit: Strands MCP Server'"
echo "5. gh repo create strands-mcp-server --private"
echo "6. git remote add origin git@github.com:robpaterson/strands-mcp-server.git"
echo "7. git push -u origin main"
echo ""
echo "The .kiro/ folder will be preserved as part of the source code."