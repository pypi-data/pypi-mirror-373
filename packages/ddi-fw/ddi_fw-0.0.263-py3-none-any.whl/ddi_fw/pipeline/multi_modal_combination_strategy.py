from abc import ABC, abstractmethod
import itertools


class CombinationStrategy(ABC):
    @abstractmethod
    def generate(self) -> list:
        pass


class CustomCombinationStrategy(CombinationStrategy):
    def __init__(self, **kwargs_combination_params):
        # kwargs fonksiyona da alınabilir
        self.group_1 = kwargs_combination_params.get("group_1", None)
        self.group_2 = kwargs_combination_params.get("group_2", None)

    def generate(self):
        # Handle edge cases
        if not self.group_1 or not self.group_2:
            raise ValueError(
                f"Parameters of combination strategy could not be empty.")
            # return []  # Return an empty list if either group is empty
        # combinations = []
        # for j in self.group2:
        #     extended_item_group_1 = self.group_1.copy()
        #     extended_item_group_1.append(j)
        #     for i in range(2, len(extended_item_group_1) + 1):
        #         combinations.extend(list(itertools.combinations(extended_item_group_1, i))) #all
        # combinations = list(set(combinations))

        combinations = set()  # Use a set to avoid duplicates directly
        for j in self.group_2:
            extended_item_group_1 = self.group_1.copy()
            extended_item_group_1.append(j)
            # Generate combinations of all lengths from 2 to len(group_1 + 1)
            for i in range(2, len(extended_item_group_1) + 1):
                combinations.update(itertools.combinations(
                    extended_item_group_1, i))  # Add combinations

        # Convert set back to list (if needed) and return
        return list(combinations)
