import re
from typing import Optional, List, Callable, Union, Any, Dict

def extract_columns(text: str = None) -> List[str]:
        # Extract the columns by looking for text between square brackets
        if text:
            return list(set(re.findall(r'\[(.*?)\]', text)))
        return []

class Metric:
    def __init__(
        self,
        name: Optional[str] = None,
        expression: Optional[str] = None,
        aggregation: Optional[Union[str, Callable[[Any], Any]]] = None,
        metric_filters: Optional[Dict[str, Any]] = None,
        row_condition_expression: Optional[str] = None, 
        context_state_name: str = 'Default',
        ignore_dimensions: Optional[Union[bool, List[str]]] = False,
        fillna: Optional[any] = None, 
    ) -> None:
        self.name = name
        self.expression = expression
        self.row_condition_expression = row_condition_expression
        self.aggregation = aggregation
        self.columns = extract_columns(str(self.expression) + str(self.row_condition_expression))
        self.metric_filters = metric_filters
        self.context_state_name = context_state_name
        self.ignore_dimensions = ignore_dimensions
        self.fillna = fillna

        # Required for query processing. It will be populated during metric definition depending on the columns used and the DAG of the specific hypercube where it is being defined.
        self.keys = {}
        self.columns_indexes = {}
    
    def get_metric_details(self):
        import inspect
        #return a dictionary with metric details
        aggregation_display = self.aggregation
        if callable(self.aggregation):
            try:
                # Get source for lambdas, or name for regular functions
                source = inspect.getsource(self.aggregation).strip()
                aggregation_display = source if source.startswith('lambda') else self.aggregation.__name__
            except (TypeError, OSError):
                # Fallback to name for built-in functions or if source is not available
                aggregation_display = self.aggregation.__name__

        return {
            "expression": self.expression,
            "row_condition_expression": self.row_condition_expression,
            "aggregation": aggregation_display,
            #"columns": self.columns,
            "metric_filters": self.metric_filters,
            "context_state_name": self.context_state_name,
            "ignore_dimensions": self.ignore_dimensions,
            "fillna": self.fillna,
        }

class MetricGroup: # group of metrics based on state and query filters
    def __init__(
            self, 
            metric_group_name: Optional[str], 
            metrics: List[Metric], 
            group_filters: Optional[Dict[str, Any]] = None, 
            context_state_name: str = 'Default'
    ) -> None:
        import copy
        self.metric_group_name = metric_group_name
        self.metrics = copy.deepcopy(metrics)  # Ensure we work with a copy of the metrics
        self.group_filters = group_filters
        self.context_state_name = context_state_name


class ComputedMetric:
    """Represents a post-aggregation computed metric.

    These are evaluated after base metrics are aggregated. They can reference
    any column present in the aggregated result using [Column] syntax.
    """
    def __init__(
        self,
        name: str,
        expression: str,
        fillna: Optional[Any] = None,
    ) -> None:
        self.name = name
        self.expression = expression
        self.fillna = fillna
        self.columns = extract_columns(expression)

    def get_computed_metric_details(self) -> Dict[str, Any]:
        return {
            "expression": self.expression,
            "fillna": self.fillna,
        #    "columns": self.columns,
        }