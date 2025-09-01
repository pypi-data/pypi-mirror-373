import hashlib

class BlocksState:
    def __init__(self):
        self._automations = []
    
    def add_automation(self, automation_data):
        """Add an automation to the internal list"""
        function_source_code = automation_data.get("function_source_code", "")
        function_hash = hashlib.sha256(function_source_code.encode()).hexdigest()
        self._automations.append({**automation_data, "function_hash": function_hash})
    
    @property
    def automations(self):
        """Getter property for automations - allows for post-processing if needed"""
        automations = self._automations
        return automations
        
