from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .constants import nodetype_mapping


from typing import List, Dict, Any, Optional

class Node:
    """Represents a single node in a hierarchical structure."""
    
    def __init__(self, data: Dict[str, Any], parent: Optional[int] = 0):
          
        # Dynamically assign all key-value pairs from the input dictionary
        for key, value in data.items():
            setattr(self, key, value)
        
        # New: Store a reference to the paren
        self.parent: Optional[int] = parent
        
        # Get children and handle the None case
        children_data = data.get("children", [])
        if children_data is None:
            children_data = []

        node_id = getattr(self, "id", None)
        self.children: List['Node'] = [
            Node(child_data, parent=node_id) for child_data in children_data
        ]

    def __repr__(self) -> str:
        return f"Node(name='{self.name}', id={self.id}, parentId={self.parent}, nodeType='{self.typeName}')"


    def to_dict(self) -> Dict[str, Any]:
        """
        Converts a Node object and its children back into a dictionary,
        including any dynamically added attributes.
        """ 
        node_dict = self.__dict__.copy()
        # Recursively convert children to dictionaries
        if self.children:
            node_dict["children"] = [child.to_dict() for child in self.children]
        else:
            node_dict["children"] = None
            
        return node_dict
    
        
    def count_nodes(self, node_type: Optional[str] = '', is_active: Optional[bool] = None) -> int:
        """Calculates the total number of machines (typeId=1) in this node and its children."""
        count = 0 
        type_id_to_check = []
 
        if node_type is None or node_type.lower() == 'all':
            type_id_to_check = [self.typeId]
        elif node_type.lower() == "point":
            swapped_mapping = {value.lower(): key for key, value in nodetype_mapping.items()}
            for p in nodetype_mapping:
                if(p > 100): type_id_to_check.append(p)
        else:
            type_id_lower = node_type.lower() 
            swapped_mapping = {value.lower(): key for key, value in nodetype_mapping.items()}
            type_id_to_check = [swapped_mapping.get(type_id_lower)]
        
        # Check if the current node matches the desired type and status
        if self.typeId in type_id_to_check:
            if is_active is None:
                count += 1
            elif is_active == True and self.active:
                count += 1
            elif is_active == False and not self.active:
                count += 1

        # Corrected recursive call: pass both arguments
        for child in self.children:
            count += child.count_nodes(node_type, is_active) 
        return count
 
    def get_child_by_id(self, child_id: int) -> Optional['Node']:
        """
        Searches for a child node with the given ID.
        This method is recursive.
        """
        # Check current node's children
        for child in self.children:
            if child.id == child_id:
                return child
            
            # Recursively search the child's children
            found_node = child.get_child_by_id(child_id)
            if found_node:
                return found_node
        
        return None  # Return None if no child is found
    
    

class NodeContainer:
    """A container for a list of Node objects."""
    def __init__(self, data_list: List[Dict[str, Any]]):
        self.nodes: List[Node] = []
        for item in data_list:
            if isinstance(item, dict):
                self.nodes.append(Node(item))

    @property
    def describe_counts(self) -> List[Dict]:
        """Returns the sum of the counts per every available type in the hierarchy."""
        arrDiscription = []
        for i in nodetype_mapping:
          crntType = nodetype_mapping[i]
          theCount = self.count_nodes(crntType)
          if(theCount !=0):
              arrDiscription.append({"nodetype":crntType,"count":theCount}) 
        return arrDiscription
    
    @property
    def hierarchy_root(self) -> List[Dict]:
        """Returns the root name and its ID for the main hierarchy."""
        if self.nodes:
            for i in self.nodes:
                if(i.parent ==0):
                  return [{"root name": i.name, "root id": i.id, "root parent": i.parent}]
        return []

    @property
    def hierarchy_name(self) -> List[str]:
        """Returns a list of all node names in the container."""
        return [[node.id, node.name] for node in self.nodes]
    
    @property
    def nodetypes(self) -> str:
        """Returns a string listing all available node types."""  
        return nodetype_mapping
    
    def __repr__(self) -> str:
        return f"{self.to_list()})"

    def __iter__(self):
        """Allows the container to be iterated over."""
        return iter(self.nodes)
    
    
    def get_node_by_id(self, node_id: int) -> Optional['Node']:
        """
        Searches the entire hierarchy for a node with the given ID.
        """
        for node in self.nodes:
            # Check the top-level node first
            if node.id == node_id:
                return node
            
            # Then, search its children recursively
            found_node = node.get_child_by_id(node_id)
            if found_node: 
                return found_node 
        return None # Return None if the node is not found
     
    
    def to_dict(self,node_id: Optional[int] = None) -> List[Any]:
        """
        Exports a specific node (and its children) or the entire hierarchy to a list of dictionaries.

        Args:
            node_id: The ID of the node to export. If None, the entire hierarchy is exported.

        Returns:
            A list of dictionaries representing the exported nodes.
        """
        if node_id is not None:
            # Find the specific node
            target_node = self.get_node_by_id(node_id)
            if target_node:
                # If found, return a list containing only that node's dictionary
                return target_node.to_dict()
            else:
                # If not found, return an empty list
                return {}
        else:
            # If no ID is provided, export the entire hierarchy
            return [node.to_dict() for node in self.nodes]
    

    def to_list(self,node_id: Optional[int] = None) -> List[Any]:
        """
        Exports a specific node (and its children) or the entire hierarchy to a list of dictionaries.

        Args:
            node_id: The ID of the node to export. If None, the entire hierarchy is exported.

        Returns:
            A list of dictionaries representing the exported nodes.
        """
        if node_id is not None:
            # Find the specific node
            target_node = self.get_node_by_id(node_id)
            if target_node:
                # If found, return a list containing only that node's dictionary
                return [target_node.to_dict()]
            else:
                # If not found, return an empty list
                return [{}]
        else:
            # If no ID is provided, export the entire hierarchy
            return [node.to_dict() for node in self.nodes]
    

    def count_nodes(self,node_type: Optional[str]= None, is_active: Optional[bool] = None) -> int:
        """Calculates the total number of notes across all nodes in the container."""
        return sum(node.count_nodes(node_type,is_active) for node in self.nodes)
    
 
   
    
    
    def get_parent_chain(self,node_id: int) -> List[Dict]:
        found_chain = []
        cntr = 0
        while True:
            cntr = cntr + 1
            specificMachine = self.get_node_by_id(node_id=node_id)   
            found_chain.append({"id":specificMachine.id,"name":specificMachine.name,"active":specificMachine.active,"parent":specificMachine.parent,"description":specificMachine.description,"path":specificMachine.path})
            node_id = specificMachine.parent
            if( node_id == 0 or cntr == 100): 
                return found_chain 

    
    
