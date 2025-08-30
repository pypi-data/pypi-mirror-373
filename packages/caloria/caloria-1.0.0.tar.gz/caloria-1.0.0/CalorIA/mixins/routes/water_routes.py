from flask import Blueprint, jsonify, request
from uuid import UUID
from datetime import date
from werkzeug.local import LocalProxy
import sys
import os

# Add the parent directory to the Python path to import CalorIA modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the get_db function and types
from CalorIA.backend.app import get_client
from CalorIA import types as Type

# Create the water routes blueprint
water_bp = Blueprint('water', __name__)

# Use LocalProxy to defer client resolution until request context
client = LocalProxy(get_client)

@water_bp.route('/api/water/<user_id>', methods=['GET'])
def get_water_entries(user_id):
    """Get water entries for a user.
    
    Supports pagination and date range filtering.
    """
    try:
        # Parse UUID from string
        try:
            user_id = UUID(user_id)
        except ValueError:
            return jsonify({"error": "Invalid user ID format"}), 400
            
        # Get query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', type=int)
        
        # Parse date parameters if provided
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = date.fromisoformat(start_date_str)
            except ValueError:
                return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD"}), 400
                
        if end_date_str:
            try:
                end_date = date.fromisoformat(end_date_str)
            except ValueError:
                return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD"}), 400
        
        # Get water entries
        entries = client.get_user_water_entries(user_id, start_date, end_date, skip, limit)
        
        # Convert entries to dictionaries for JSON response
        entries_dict = [entry.to_dict() for entry in entries]
        
        return jsonify({
            "user_id": str(user_id),
            "entries": entries_dict,
            "count": len(entries_dict)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch water entries: {str(e)}"}), 500

@water_bp.route('/api/water', methods=['POST'])
def add_water_entry():
    """Add a new water entry for a user"""
    try:
        # Parse JSON request body
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400
        
        # Validate required fields
        if 'user_id' not in data:
            return jsonify({"error": "Missing required field: user_id"}), 400
            
        if 'amount' not in data:
            return jsonify({"error": "Missing required field: amount"}), 400
        
        # Parse UUID from string
        try:
            user_id = UUID(data['user_id'])
        except ValueError:
            return jsonify({"error": "Invalid user ID format"}), 400
            
        # Get date from request or use today
        entry_date = data.get('on_date')
        if entry_date:
            try:
                entry_date = date.fromisoformat(entry_date)
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        else:
            entry_date = date.today()
        
        # Validate numeric fields
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({"error": "Amount must be positive"}), 400
        except ValueError:
            return jsonify({"error": "Amount must be a valid number"}), 400
        
        # Get unit or use default
        unit = data.get('unit', Type.WaterUnit.ML)
        
        # Validate unit
        try:
            unit = Type.WaterUnit(unit)
        except ValueError:
            return jsonify({
                "error": f"Invalid unit. Must be one of: {', '.join([u.value for u in Type.WaterUnit])}"
            }), 400
        
        # Create water entry
        water_entry = Type.WaterEntry(
            user_id=user_id,
            amount=amount,
            unit=unit,
            on_date=entry_date
        )
        
        # Add to database
        result = client.add_water_entry(water_entry)
        
        if result is None:
            return jsonify({"error": "Failed to save water entry"}), 500
            
        return jsonify({
            "message": "Water entry added successfully",
            "entry": water_entry.to_dict(),
            "amount_ml": water_entry.amount_ml  # Include converted amount in ml
        }), 201
        
    except ValueError as e:
        return jsonify({"error": f"Invalid value: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to add water entry: {str(e)}"}), 500

@water_bp.route('/api/water/<entry_id>', methods=['PUT'])
def update_water_entry(entry_id):
    """Update an existing water entry"""
    try:
        # Parse UUID from string
        try:
            entry_id = UUID(entry_id)
        except ValueError:
            return jsonify({"error": "Invalid entry ID format"}), 400
        
        # Parse JSON request body
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400
        
        # Get the existing entry to validate it exists
        existing_entry = client.get_water_entry_by_id(entry_id)
        if existing_entry is None:
            return jsonify({"error": "Water entry not found"}), 404
        
        # Prepare update data
        update_data = {}
        
        # Handle amount update
        if 'amount' in data:
            try:
                amount = float(data['amount'])
                if amount <= 0:
                    return jsonify({"error": "Amount must be positive"}), 400
                update_data['amount'] = amount
            except ValueError:
                return jsonify({"error": "Invalid amount value"}), 400
        
        # Handle unit update
        if 'unit' in data:
            try:
                unit = Type.WaterUnit(data['unit'])
                update_data['unit'] = unit.value
            except ValueError:
                return jsonify({
                    "error": f"Invalid unit. Must be one of: {', '.join([u.value for u in Type.WaterUnit])}"
                }), 400
        
        # Handle on_date update
        if 'on_date' in data:
            try:
                # Store as ISO format string for MongoDB
                update_data['on_date'] = date.fromisoformat(data['on_date']).isoformat()
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # If no fields to update, return error
        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400
        
        # Update the entry
        success = client.update_water_entry(entry_id, update_data)
        
        if not success:
            return jsonify({"error": "Failed to update water entry"}), 500
        
        # Get updated entry
        updated_entry = client.get_water_entry_by_id(entry_id)
        
        return jsonify({
            "message": "Water entry updated successfully",
            "entry": updated_entry.to_dict() if updated_entry else None,
            "amount_ml": updated_entry.amount_ml if updated_entry else None  # Include converted amount in ml
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to update water entry: {str(e)}"}), 500

@water_bp.route('/api/water/<entry_id>', methods=['DELETE'])
def delete_water_entry(entry_id):
    """Delete a water entry"""
    try:
        # Parse UUID from string
        try:
            entry_id = UUID(entry_id)
        except ValueError:
            return jsonify({"error": "Invalid entry ID format"}), 400
        
        # Get the existing entry to validate it exists
        existing_entry = client.get_water_entry_by_id(entry_id)
        if existing_entry is None:
            return jsonify({"error": "Water entry not found"}), 404
        
        # Delete the entry
        success = client.delete_water_entry(entry_id)
        
        if not success:
            return jsonify({"error": "Failed to delete water entry"}), 500
        
        return jsonify({
            "message": "Water entry deleted successfully",
            "id": str(entry_id)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to delete water entry: {str(e)}"}), 500