from ..utils.benchmarking import record_runtime
from abc import ABC, abstractmethod

class TensorUpdater(ABC):
    """
    Abstract base class for the iPEPS tensor update.
    """
    def __init__(self, ipeps, gate):
        """
        Initializes the TensorUpdater class with an iPEPS instance and a gate operation.

        Parameters:
        -----------
        ipeps : object
            An instance of the iPEPS tensor network, which holds the tensor data to be updated.

        gate : object
            The gate operation or transformation that will be applied during the tensor update.
        """
        self.ipeps = ipeps
        self.dims = ipeps.dims
        self.gate = gate

    @abstractmethod
    def tensor_update(self):
        """
        Abstract method that should be implemented by subclasses to define the specific logic 
        for updating the tensors in the iPEPS network.

        This method must be overridden by a subclass to provide the specific update operation 
        for the tensors based on the network's requirements.

        Returns:
        --------
        None
        """
        pass

    @record_runtime
    def update(self, bond):
        """
        Updates the tensors associated with a given bond in the iPEPS network by applying the
        tensor update operation and permuting the tensors.

        This method retrieves the tensors for the specified bond, applies the `tensor_update` 
        operation, and then permutes the tensors back to their original configuration.

        Parameters:
        -----------
        bond : tuple
            A tuple representing the bond to be updated. It contains two site indices and a bond index (s1, s2, k).
        
        Returns:
        --------
        tuple
            A tuple containing the updated tensors for the two sites in the bond (a1, a2).
        """
        s1,s2,k = bond
        a1 = self.ipeps[s1]['A']
        a2 = self.ipeps[s2]['A']
        a1,a2 = self.permute_bond_tensors(a1, a2, k)
        a1,a2 = self.tensor_update(a1, a2, bond)
        a1,a2 = self.permute_bond_tensors(a1, a2, 4-k)
        return a1,a2

    def permute_bond_tensors(self, a1, a2, k):
        """
        Permutes the input tensors `a1` and `a2` based on the bond index `k`.

        This method rearranges the dimensions of the tensors according to a permutation pattern
        determined by the bond direction `k`, which is typically used in the iPEPS update procedure.

        Parameters:
        -----------
        a1 : Tensor
            The first input tensor to be permuted.
        
        a2 : Tensor
            The second input tensor to be permuted.
        
        k : int
            The bond index used to determine the permutation pattern.

        Returns:
        --------
        tuple
            A tuple containing the permuted tensors (a1, a2).
        """
        a1 = a1.permute(self.bond_permutation(k))
        a2 = a2.permute(self.bond_permutation(k))
        return a1,a2

    @staticmethod
    def bond_permutation(k):
        """
        Generates a permutation pattern for tensor indices based on the bond direction `k`.

        The permutation is calculated by shifting the tensor indices in a circular fashion,
        and it determines how the tensor's dimensions will be permuted during the update process.

        Parameters:
        -----------
        k : int
            The bond index used to generate the permutation pattern.

        Returns:
        --------
        list
            A list representing the permutation pattern of the tensor indices.
        """
        return [(i+k)%4 for i in range(4)] + [4,]
