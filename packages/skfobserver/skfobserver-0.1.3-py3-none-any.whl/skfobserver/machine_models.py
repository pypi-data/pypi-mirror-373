from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class KeyValue:
    """Represents a key-value pair with an optional unit."""
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get('id', '')
        self.value: Any = data.get('value')
        self.unit: Optional[str] = data.get('unit')

    def to_dict(self) -> Dict[str, Any]:
        """Converts a KeyValue object back to a dictionary."""
        return {
            'id': self.id,
            'value': self.value,
            'unit': self.unit
        }
    
    def __repr__(self) -> str:
        return f"KeyValue(id='{self.id}', value={self.value}, unit='{self.unit}')"

class Machine:
    """Represents a machine or equipment object."""
    def __init__(self, data: Dict[str, Any]):
        self.id: int = data.get('id', 0)
        self.name: Optional[str] = data.get('name')
        self.description: Optional[str] = data.get('description')
        self.path: Optional[str] = data.get('path')
        self.machineCode: Optional[str] = data.get('machineCode')
        self.power: Optional[str] = data.get('power')
        self.gear: Optional[str] = data.get('gear')
        self.isoClass: int = data.get('isoClass', 0)
        self.idContact: int = data.get('idContact', 0)
        self.conditionalPoint: int = data.get('conditionalPoint', 0)
        self.conditionalPointSrc: Any = data.get('conditionalPointSrc')
        
        self.driving: List[KeyValue] = [KeyValue(item) for item in data.get('driving', [])]
        self.driven: List[KeyValue] = [KeyValue(item) for item in data.get('driven', [])]
        self.transmission: List[KeyValue] = [KeyValue(item) for item in data.get('transmission', [])]
        self.coordinates: List[KeyValue] = [KeyValue(item) for item in data.get('coordinates', [])]
        self.conditionalPointTag: List[KeyValue] = [KeyValue(item) for item in data.get('conditionalPointTag', [])]

 
    def to_dict(self) -> Dict[str, Any]:
        """Converts a Machine object back to a dictionary."""
        machine_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'path': self.path,
            'machineCode': self.machineCode,
            'power': self.power,
            'gear': self.gear,
            'isoClass': self.isoClass,
            'idContact': self.idContact,
            'conditionalPoint': self.conditionalPoint,
            'conditionalPointSrc': self.conditionalPointSrc,
            
            # Convert lists of KeyValue objects
            'driving': [item.to_dict() for item in self.driving],
            'driven': [item.to_dict() for item in self.driven],
            'transmission': [item.to_dict() for item in self.transmission],
            'coordinates': [item.to_dict() for item in self.coordinates],
            'conditionalPointTag': [item.to_dict() for item in self.conditionalPointTag]
        }
        return machine_dict
    
    def __repr__(self) -> str:
        return f"Machine(name='{self.name}', id={self.id}, path='{self.path}')"

class MachineCollection:
    """A container class to hold a collection of Machine objects."""
    def __init__(self, data_list: List[Dict[str, Any]]):
        self.machines: List[Machine] = []
        for item in data_list: 
            if isinstance(item, dict) and 'id' in item:
                self.machines.append(Machine(item))


    def to_list(self) -> List[Dict[str, Any]]:
        """Exports all machines in the collection to a list of dictionaries."""
        return [machine.to_dict() for machine in self.machines]
    
    
    def count(self) -> int:
        """Returns the number of machines in the collection."""
        return len(self.machines)
    
    
    def all_paths(self) -> List[str]:
        """Returns the list of all paths of machines in the collection."""
        return [[machine.id , machine.path] for machine in self.machines]
    
    @property
    def all_names(self) -> List[str]:
        """Returns the list of all paths of machines in the collection."""
        return [[machine.id , machine.name] for machine in self.machines]
    
    @property
    def all_ids(self) -> List[int]:
        """Returns the list of all macine id's of machines in the collection."""
        return [machine.id for machine in self.machines]
    
    def __repr__(self) -> str:
        return f"MachineCollection(count={self.count()})"

    def __iter__(self):
        """Allows the collection to be iterated over directly."""
        return iter(self.machines)