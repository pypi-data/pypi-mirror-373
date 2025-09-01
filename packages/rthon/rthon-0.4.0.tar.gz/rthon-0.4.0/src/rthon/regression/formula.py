"""
R-style formula parser for linear models.
Handles expressions like "y ~ x1 + x2 + I(x1^2) + x1:x2"
"""

from __future__ import annotations
import re
from typing import List, Dict, Any, Tuple, Set, Union, Optional
from .linear_algebra import Matrix, Vector

class Term:
    """Represents a term in a formula (like x1, I(x1^2), x1:x2)."""
    
    def __init__(self, expression: str, variables: List[str], 
                 interaction_order: int = 1, transform: Optional[str] = None):
        self.expression = expression.strip()
        self.variables = variables
        self.interaction_order = interaction_order
        self.transform = transform  # e.g., "^2" for I(x^2)
    
    def __str__(self) -> str:
        return self.expression
    
    def __repr__(self) -> str:
        return f"Term('{self.expression}', {self.variables})"

class Formula:
    """Represents a parsed R-style formula."""
    
    def __init__(self, formula_str: str):
        self.formula_str = formula_str.strip()
        self.response: Optional[str] = None
        self.terms: List[Term] = []
        self.has_intercept = True
        self._parse()
    
    def _parse(self) -> None:
        """Parse the formula string."""
        # Split on ~
        if '~' not in self.formula_str:
            raise ValueError("Formula must contain '~' to separate response and predictors")
        
        response_part, predictor_part = self.formula_str.split('~', 1)
        
        # Parse response
        self.response = response_part.strip()
        if not self.response:
            raise ValueError("Response variable cannot be empty")
        
        # Parse predictors
        self._parse_predictors(predictor_part.strip())
    
    def _parse_predictors(self, predictor_str: str) -> None:
        """Parse the predictor part of the formula."""
        if not predictor_str:
            return
        
        # Handle intercept removal
        if predictor_str.startswith('-1') or predictor_str.startswith('0'):
            self.has_intercept = False
            predictor_str = re.sub(r'^(-1|0)\s*\+?\s*', '', predictor_str)
        elif '+0' in predictor_str or '-1' in predictor_str:
            self.has_intercept = False
            predictor_str = re.sub(r'[+\-]\s*(1|0)', '', predictor_str)
        
        if not predictor_str:
            return
        
        # Split terms by + and -
        # This is a simplified parser - a full parser would be more complex
        term_parts = self._split_terms(predictor_str)
        
        for part in term_parts:
            term = self._parse_term(part.strip())
            if term:
                self.terms.append(term)
    
    def _split_terms(self, s: str) -> List[str]:
        """Split terms by + and - operators, keeping track of parentheses."""
        terms = []
        current_term = ""
        paren_depth = 0
        i = 0
        
        while i < len(s):
            char = s[i]
            
            if char == '(':
                paren_depth += 1
                current_term += char
            elif char == ')':
                paren_depth -= 1
                current_term += char
            elif char in ['+', '-'] and paren_depth == 0:
                if current_term.strip():
                    terms.append(current_term.strip())
                current_term = ""
                # Skip the operator
                i += 1
                continue
            else:
                current_term += char
            
            i += 1
        
        if current_term.strip():
            terms.append(current_term.strip())
        
        return terms
    
    def _parse_term(self, term_str: str) -> Optional[Term]:
        """Parse a single term."""
        if not term_str:
            return None
        
        # Handle I() transformations
        i_pattern = r'I\s*\(\s*([^)]+)\s*\)'
        i_match = re.match(i_pattern, term_str)
        
        if i_match:
            # Extract the expression inside I()
            inner_expr = i_match.group(1)
            variables = self._extract_variables(inner_expr)
            return Term(term_str, variables, 1, inner_expr)
        
        # Handle interactions (x1:x2)
        if ':' in term_str:
            interaction_vars = [v.strip() for v in term_str.split(':')]
            interaction_vars = [v for v in interaction_vars if v]  # Remove empty
            if interaction_vars:
                return Term(term_str, interaction_vars, len(interaction_vars))
        
        # Simple variable
        variables = self._extract_variables(term_str)
        if variables:
            return Term(term_str, variables, 1)
        
        return None
    
    def _extract_variables(self, expr: str) -> List[str]:
        """Extract variable names from an expression."""
        # Simple regex to find variable names (letters, numbers, underscores, dots)
        pattern = r'[a-zA-Z_][a-zA-Z0-9_\.]*'
        variables = re.findall(pattern, expr)
        
        # Filter out known functions/operators
        excluded = {'I', 'log', 'exp', 'sin', 'cos', 'sqrt'}
        variables = [v for v in variables if v not in excluded]
        
        return list(dict.fromkeys(variables))  # Remove duplicates, preserve order
    
    def get_all_variables(self) -> List[str]:
        """Get all unique variables used in the formula."""
        all_vars = set()
        
        if self.response:
            all_vars.add(self.response)
        
        for term in self.terms:
            all_vars.update(term.variables)
        
        return sorted(list(all_vars))
    
    def __str__(self) -> str:
        return self.formula_str
    
    def __repr__(self) -> str:
        return f"Formula('{self.formula_str}')"

def design_matrix_from_formula(formula: Formula, data: Dict[str, Vector]) -> Tuple[Matrix, Vector, List[str]]:
    """
    Create design matrix from formula and data.
    
    Returns:
        X: Design matrix
        y: Response vector
        column_names: Names of columns in design matrix
    """
    if not formula.response or formula.response not in data:
        raise ValueError(f"Response variable '{formula.response}' not found in data")
    
    y = data[formula.response]
    n = len(y)
    
    # Check that all required variables are in data
    required_vars = set()
    for term in formula.terms:
        required_vars.update(term.variables)
    
    missing_vars = required_vars - set(data.keys())
    if missing_vars:
        raise ValueError(f"Variables not found in data: {missing_vars}")
    
    # Build design matrix columns
    X_columns = []
    column_names = []
    
    # Add intercept if needed
    if formula.has_intercept:
        X_columns.append([1.0] * n)
        column_names.append("(Intercept)")
    
    # Process each term
    for term in formula.terms:
        if term.interaction_order == 1:
            # Simple term or transformation
            if term.transform:
                # Handle I() transformations
                column = _evaluate_transformation(term.transform, data, n)
                X_columns.append(column)
                column_names.append(term.expression)
            else:
                # Simple variable
                var_name = term.variables[0]
                if var_name in data:
                    X_columns.append(data[var_name][:])
                    column_names.append(var_name)
        else:
            # Interaction term
            interaction_col = _compute_interaction(term.variables, data, n)
            X_columns.append(interaction_col)
            column_names.append(term.expression)
    
    # Transpose to get proper matrix format
    X = [[X_columns[j][i] for j in range(len(X_columns))] for i in range(n)]
    
    return X, y, column_names

def _evaluate_transformation(transform_expr: str, data: Dict[str, Vector], n: int) -> Vector:
    """Evaluate transformation expressions like 'x^2' or 'log(x)'."""
    # This is a simplified evaluator - a full implementation would be more robust
    
    # Handle power transformations like x^2, x^3
    power_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_\.]*)\s*\^\s*([0-9]+)', transform_expr)
    if power_match:
        var_name = power_match.group(1)
        power = int(power_match.group(2))
        if var_name in data:
            return [x ** power for x in data[var_name]]
    
    # Handle simple variable (fallback)
    var_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_\.]*)$', transform_expr.strip())
    if var_match:
        var_name = var_match.group(1)
        if var_name in data:
            return data[var_name][:]
    
    # If we can't parse it, return zeros (not ideal, but safe)
    return [0.0] * n

def _compute_interaction(variables: List[str], data: Dict[str, Vector], n: int) -> Vector:
    """Compute interaction term by multiplying variables."""
    if not variables:
        return [1.0] * n
    
    result = [1.0] * n
    for var_name in variables:
        if var_name in data:
            for i in range(n):
                result[i] *= data[var_name][i]
    
    return result

def parse_formula(formula_str: str) -> Formula:
    """Parse a formula string into a Formula object."""
    return Formula(formula_str)

# Example usage functions for testing
def example_formulas():
    """Examples of formula parsing."""
    formulas = [
        "y ~ x",
        "y ~ x1 + x2", 
        "y ~ x1 + x2 + x1:x2",
        "y ~ x1 + I(x1^2)",
        "y ~ x1 + x2 - 1",  # No intercept
        "mpg ~ hp + wt + I(hp^2) + hp:wt"
    ]
    
    for formula_str in formulas:
        try:
            f = parse_formula(formula_str)
            print(f"Formula: {formula_str}")
            print(f"  Response: {f.response}")
            print(f"  Has intercept: {f.has_intercept}")
            print(f"  Terms: {[str(t) for t in f.terms]}")
            print(f"  Variables: {f.get_all_variables()}")
            print()
        except Exception as e:
            print(f"Error parsing '{formula_str}': {e}")
            print()

if __name__ == "__main__":
    example_formulas()