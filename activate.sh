#!/bin/bash
# Unified Automation Suite - Environment Activation
echo "🚀 Activating Unified Automation Suite Environment..."
source "/home/nike/Desktop/TELEGRAM MAIN/unified_automation_suite/venv/bin/activate"
export PYTHONPATH="$PYTHONPATH:/home/nike/Desktop/TELEGRAM MAIN/unified_automation_suite"
echo "✅ Environment activated. You can now run:"
echo "   python main.py --gui    # Launch full GUI"
echo "   python main.py --test   # Run tests"
echo "   python main.py --info   # Show information"
